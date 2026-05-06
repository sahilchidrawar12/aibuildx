"""
Flask web application for DWG→Tekla conversion pipeline.
Allows users to upload DWG files, run the full pipeline, and export to Tekla Structures.
"""
import os
import json
import uuid
import sqlite3
import urllib.request
import urllib.error
import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file
from .pipeline.utils.pipeline_compat import run_pipeline
from .pipeline.agents.llm_validation_agent import (
    LLMValidationAgent,
    load_job_result,
    save_job_result,
    save_ai_audit,
    record_ai_feedback,
    aggregate_feedback_trends,
)

# Configuration - use project root paths
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(PROJECT_ROOT / 'uploads'))
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', str(PROJECT_ROOT / 'outputs'))
ALLOWED_EXTENSIONS = {'dwg', 'dxf', 'json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
DB_PATH = os.getenv('JOB_DB_PATH', str(PROJECT_ROOT / 'jobs.db'))
TEKLA_API_URL = os.getenv('TEKLA_API_URL', 'http://localhost:8000')
TEKLA_BRIDGE_MAP_PATH = os.getenv('TEKLA_BRIDGE_MAP_PATH', str(PROJECT_ROOT / 'config' / 'tekla_bridge_map.json'))

# Ensure Tekla bridge config path exists and has a default mapping
os.makedirs(os.path.dirname(TEKLA_BRIDGE_MAP_PATH), exist_ok=True)
if not os.path.exists(TEKLA_BRIDGE_MAP_PATH):
    with open(TEKLA_BRIDGE_MAP_PATH, 'w') as fh:
        json.dump({'default': TEKLA_API_URL}, fh, indent=2)


def load_company_tekla_bridge_map():
    if not os.path.exists(TEKLA_BRIDGE_MAP_PATH):
        return {}
    try:
        with open(TEKLA_BRIDGE_MAP_PATH, 'r') as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def resolve_tekla_api_url(company_id=None):
    bridge_map = load_company_tekla_bridge_map()
    if company_id and bridge_map.get(company_id):
        return bridge_map[company_id], 'company_mapping'
    if bridge_map.get('default'):
        return bridge_map['default'], 'default_mapping'
    return TEKLA_API_URL, 'env_default'


MOCK_USERS = [
    {
      'id': '1',
      'email': 'superadmin@aibuildx.com',
      'name': 'Super Admin',
      'role': 'super_admin',
      'companyId': None,
      'lastLogin': datetime.datetime.utcnow().isoformat()
    },
    {
      'id': '2',
      'email': 'admin@company.com',
      'name': 'Company Admin',
      'role': 'company_admin',
      'companyId': 'company-1',
      'lastLogin': datetime.datetime.utcnow().isoformat()
    },
    {
      'id': '3',
      'email': 'employee@company.com',
      'name': 'John Employee',
      'role': 'employee',
      'companyId': 'company-1',
      'lastLogin': datetime.datetime.utcnow().isoformat()
    },
    {
      'id': '4',
      'email': 'sarah.engineer@company.com',
      'name': 'Sarah Engineer',
      'role': 'employee',
      'companyId': 'company-1',
      'lastLogin': datetime.datetime.utcnow().isoformat()
    },
    {
      'id': '5',
      'email': 'mike.architect@company.com',
      'name': 'Mike Architect',
      'role': 'employee',
      'companyId': 'company-1',
      'lastLogin': datetime.datetime.utcnow().isoformat()
    }
]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            source_file TEXT,
            company_id TEXT,
            user_id TEXT,
            status TEXT,
            created_at TEXT,
            output_dir TEXT
        )
        '''
    )
    conn.commit()
    conn.close()


def save_job_record(job_id, source_file, company_id=None, user_id=None, status='complete', output_dir=''):
    conn = get_db_connection()
    conn.execute(
        '''
        INSERT OR REPLACE INTO jobs (id, source_file, company_id, user_id, status, created_at, output_dir)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (job_id, source_file, company_id, user_id, status, datetime.datetime.utcnow().isoformat(), output_dir)
    )
    conn.commit()
    conn.close()


def query_job_record(job_id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    return row


init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the upload page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and pipeline execution."""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'File type not allowed. Use DWG, DXF, or JSON'}), 400
        
        # Generate unique job ID and save file
        job_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}_{filename}')
        file.save(filepath)
        
        company_id = request.form.get('company_id') or None
        user_id = request.form.get('user_id') or None
        
        # Record the job before running the pipeline
        job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        save_job_record(job_id, filename, company_id=company_id, user_id=user_id, status='processing', output_dir=job_output_dir)
        
        # Run pipeline
        result = run_pipeline(filepath, out_dir=job_output_dir)
        
        if isinstance(result, dict) and result.get('status') == 'error':
            save_job_record(job_id, filename, company_id=company_id, user_id=user_id, status='error', output_dir=job_output_dir)
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Pipeline execution failed'),
                'job_id': job_id
            }), 500
        
        # Collect output files
        output_files = []
        file_details = []
        if os.path.exists(job_output_dir):
            for fname in os.listdir(job_output_dir):
                if fname.endswith('.json') or fname.endswith('.csv') or fname.endswith('.ifc'):
                    output_files.append(fname)
                    file_path = os.path.join(job_output_dir, fname)
                    file_size = os.path.getsize(file_path)
                    file_details.append({
                        'name': fname,
                        'size': file_size,
                        'type': fname.split('.')[-1].upper()
                    })
        
        # Get absolute output path
        output_path = os.path.abspath(job_output_dir)
        
        # Debug log
        print(f"DEBUG: Returning output_path: {output_path}")
        print(f"DEBUG: File details: {file_details}")
        
        # Optionally read IFC summary counts if available
        ifc_summary = {}
        if os.path.exists(os.path.join(job_output_dir, 'ifc.json')):
            try:
                with open(os.path.join(job_output_dir, 'ifc.json'), 'r') as fh:
                    ifc_data = json.load(fh)
                    ifc_summary = ifc_data.get('summary', {})
            except Exception:
                ifc_summary = {}

        # Build viewer URL if IFC exists
        viewer_url = None
        if os.path.exists(os.path.join(job_output_dir, 'model.ifc')):
            viewer_url = f"/viewer/{job_id}"

        save_job_record(job_id, filename, company_id=company_id, user_id=user_id, status='complete', output_dir=job_output_dir)
        return jsonify({
            'status': 'ok',
            'job_id': job_id,
            'message': f'Pipeline completed successfully. {len(result.keys())} outputs generated.',
            'output_path': output_path,
            'outputs': {
                'keys': list(result.keys()) if isinstance(result, dict) else [],
                'files': output_files,
                'file_details': file_details,
                'summary': {
                    'members': len(result.get('miner', {}).get('members', [])) if isinstance(result, dict) else 0,
                    'errors': len(result.get('validator', {}).get('errors', [])) if isinstance(result, dict) else 0,
                    'clashes': len(result.get('clashes', {}).get('clashes', [])) if isinstance(result, dict) else 0,
                    'entities': len(result.get('entities', [])) if isinstance(result, dict) else 0,
                    'format': filename.split('.')[-1].upper(),
                    'time': 'N/A',
                    'columns': ifc_summary.get('total_columns'),
                    'beams': ifc_summary.get('total_beams'),
                    'plates': ifc_summary.get('total_plates'),
                    'fasteners': ifc_summary.get('total_fasteners')
                }
            },
            'viewer_url': viewer_url
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/download/<job_id>/<filename>')
def download_file(job_id, filename):
    """Download a generated output file."""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, job_id, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Check job status and output availability."""
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.exists(job_output_dir):
        return jsonify({'status': 'not_found'}), 404
    
    files = [f for f in os.listdir(job_output_dir) if f.endswith(('.json', '.csv', '.ifc'))]
    record = query_job_record(job_id)
    return jsonify({
        'status': 'complete',
        'job_id': job_id,
        'files': files,
        'source_file': record['source_file'] if record else None,
        'company_id': record['company_id'] if record else None,
        'user_id': record['user_id'] if record else None,
        'download_url': f'/api/download/{job_id}/'
    }), 200


@app.route('/api/users')
def list_users():
    clean_users = [
        {
            'id': u['id'],
            'email': u['email'],
            'name': u['name'],
            'role': u['role'],
            'companyId': u['companyId'],
            'lastLogin': u['lastLogin']
        }
        for u in MOCK_USERS
    ]
    return jsonify({'status': 'ok', 'users': clean_users}), 200


@app.route('/api/companies')
def list_companies():
    companies = sorted({u['companyId'] for u in MOCK_USERS if u['companyId']})
    return jsonify({'status': 'ok', 'companies': [{'id': cid, 'name': cid} for cid in companies]}), 200


@app.route('/api/jobs')
def list_jobs():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM jobs ORDER BY created_at DESC').fetchall()
    conn.close()

    jobs = []
    for row in rows:
        output_dir = row['output_dir']
        file_details = []
        if output_dir and os.path.exists(output_dir):
            for fname in sorted(os.listdir(output_dir)):
                if os.path.isfile(os.path.join(output_dir, fname)):
                    file_details.append({
                        'name': fname,
                        'type': fname.rsplit('.', 1)[-1].upper(),
                        'size': os.path.getsize(os.path.join(output_dir, fname))
                    })
        jobs.append({
            'id': row['id'],
            'source_file': row['source_file'],
            'company_id': row['company_id'],
            'user_id': row['user_id'],
            'status': row['status'],
            'created_at': row['created_at'],
            'output_dir': output_dir,
            'outputs': {
                'files': file_details,
                'ifc_available': os.path.exists(os.path.join(output_dir, 'model.ifc')) if output_dir else False
            }
        })

    return jsonify({'status': 'ok', 'jobs': jobs}), 200


@app.route('/api/jobs/<job_id>')
def get_job(job_id):
    row = query_job_record(job_id)
    if not row:
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404

    output_dir = row['output_dir']
    file_details = []
    if output_dir and os.path.exists(output_dir):
        for fname in sorted(os.listdir(output_dir)):
            if os.path.isfile(os.path.join(output_dir, fname)):
                file_details.append({
                    'name': fname,
                    'type': fname.rsplit('.', 1)[-1].upper(),
                    'size': os.path.getsize(os.path.join(output_dir, fname))
                })

    return jsonify({
        'status': 'ok',
        'job': {
            'id': row['id'],
            'source_file': row['source_file'],
            'company_id': row['company_id'],
            'user_id': row['user_id'],
            'status': row['status'],
            'created_at': row['created_at'],
            'output_dir': output_dir,
            'outputs': {
                'files': file_details,
                'ifc_available': os.path.exists(os.path.join(output_dir, 'model.ifc')) if output_dir else False
            }
        }
    }), 200


@app.route('/api/ai-validate/<job_id>')
def ai_validate(job_id):
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.exists(job_output_dir):
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404

    result = load_job_result(job_output_dir)
    if not result:
        return jsonify({'status': 'error', 'message': 'No valid pipeline result to audit'}), 404

    try:
        agent = LLMValidationAgent()
        audit_report = agent.audit(result)
        save_ai_audit(job_output_dir, audit_report)
        response_payload = {
            'status': 'ok',
            'job_id': job_id,
            'audit': audit_report,
            'needs_user_confirmation': audit_report.get('scale_correction_needed', False) or audit_report.get('disconnected_node_count', 0) > 0 or audit_report.get('semantic_mismatch_count', 0) > 0
        }
        return jsonify(response_payload), 200
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@app.route('/api/ai-act/<job_id>', methods=['POST'])
def ai_act(job_id):
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.exists(job_output_dir):
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404

    payload = request.get_json(silent=True) or {}
    action = payload.get('action', 'accept_as_is')
    user_decision = payload.get('decision', 'no')

    result = load_job_result(job_output_dir)
    if not result:
        return jsonify({'status': 'error', 'message': 'No valid pipeline result to modify'}), 404

    try:
        agent = LLMValidationAgent()
        audit_report = agent.audit(result)
        apply_scale = action in ('apply_all', 'rescale') and audit_report.get('scale_correction_needed', False)
        snap_nodes = action in ('apply_all', 'snap_nodes') or (action == 'apply_all' and audit_report.get('disconnected_node_count', 0) > 0)
        repair_plan = audit_report.get('llm_repair_plan') if isinstance(audit_report, dict) else None

        if action in ('apply_all', 'rescale', 'snap_nodes'):
            corrected = agent.apply_repair(result, apply_scale=apply_scale, snap_nodes=snap_nodes, repair_plan=repair_plan)
            saved = save_job_result(job_output_dir, corrected)
            if not saved:
                return jsonify({'status': 'error', 'message': 'Failed to persist repaired model'}), 500
        else:
            corrected = result

        feedback = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'job_id': job_id,
            'action': action,
            'decision': user_decision,
            'accepted': user_decision.lower() in ('yes', 'y', 'accept', 'apply'),
            'confidence_score': audit_report.get('confidence_score', 0.0),
            'scale_correction_needed': audit_report.get('scale_correction_needed', False),
            'disconnected_node_count': audit_report.get('disconnected_node_count', 0),
            'semantic_mismatch_count': audit_report.get('semantic_mismatch_count', 0),
            'suggestions': audit_report.get('suggestions', []),
        }
        record_ai_feedback(job_output_dir, feedback, audit_report=audit_report)
        save_ai_audit(job_output_dir, audit_report)

        return jsonify({
            'status': 'ok',
            'job_id': job_id,
            'action': action,
            'audit': audit_report,
            'repaired': action in ('apply_all', 'rescale', 'snap_nodes')
        }), 200
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@app.route('/api/ai-feedback-trend')
def ai_feedback_trend():
    try:
        trend = aggregate_feedback_trends(OUTPUT_FOLDER)
        return jsonify({'status': 'ok', 'trend': trend}), 200
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


def query_local_tekla_api(path, method='GET', payload=None, timeout=5, company_id=None):
    tekla_url, tekla_source = resolve_tekla_api_url(company_id)
    url = f'{tekla_url.rstrip('/')}{path}'
    headers = {'Content-Type': 'application/json'}
    data = None

    if payload is not None:
        data = json.dumps(payload).encode('utf-8')

    request_obj = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            return {'error': error_body, 'status': e.code}
        except Exception:
            return {'error': str(e), 'status': e.code}
    except Exception as e:
        return {'error': str(e)}


def _normalize_profile_value(profile):
    if profile is None:
        return 'HEA200'
    if isinstance(profile, str):
        return profile
    if isinstance(profile, dict):
        return profile.get('profile') or profile.get('name') or profile.get('profile_name') or 'HEA200'
    return str(profile)


def convert_pipeline_result_to_tekla_objects(result):
    objects = []
    warnings = []

    if not isinstance(result, dict):
        return objects, ['Pipeline result is not a JSON object']

    members = result.get('miner', {}).get('members', [])
    if not isinstance(members, list):
        members = []

    for member in members:
        if not isinstance(member, dict):
            continue

        start = member.get('start') or member.get('start_point') or []
        end = member.get('end') or member.get('end_point') or []

        if not (isinstance(start, list) and isinstance(end, list) and len(start) == 3 and len(end) == 3):
            warnings.append(f"Skipping member {member.get('id', 'unknown')}: invalid geometry")
            continue

        if start == end:
            warnings.append(f"Skipping member {member.get('id', 'unknown')}: zero-length geometry")
            continue

        member_type = str(member.get('type', 'beam')).lower()
        if member_type not in {'beam', 'column'}:
            member_type = 'beam'

        profile = _normalize_profile_value(member.get('profile') or member.get('section'))
        material = member.get('material') or 'S355'
        object_id = member.get('id') or str(uuid.uuid4())

        tekla_obj = {
            'id': object_id,
            'type': member_type,
            'name': member.get('name') or object_id,
            'start_point': start,
            'end_point': end,
            'profile': profile,
            'material': material
        }

        # Add rotation_angle for beams
        if member_type == 'beam':
            tekla_obj['rotation_angle'] = float(member.get('rotation', 0.0))

        objects.append(tekla_obj)

    return objects, warnings


@app.route('/api/export-tekla/<job_id>')
def export_to_tekla(job_id):
    """Prepare Tekla export (returns IFC + metadata)."""
    try:
        result_path = os.path.join(OUTPUT_FOLDER, job_id, 'result.json')
        final_path = os.path.join(OUTPUT_FOLDER, job_id, 'final.json')
        
        if not os.path.exists(result_path) and not os.path.exists(final_path):
            return jsonify({'status': 'error', 'message': 'No pipeline result found'}), 404
        
        # Load result
        result_file = result_path if os.path.exists(result_path) else final_path
        with open(result_file, 'r') as f:
            result = json.load(f)

        record = query_job_record(job_id)
        company_id = record['company_id'] if record else None
        tekla_api_url, tekla_url_source = resolve_tekla_api_url(company_id)
        
        # Check for IFC
        ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
        ifc_exists = os.path.exists(ifc_path)
        
        viewer_url = f"/viewer/{job_id}" if ifc_exists else None

        return jsonify({
            'status': 'ok',
            'job_id': job_id,
            'company_id': company_id,
            'tekla_api_url': tekla_api_url,
            'tekla_url_source': tekla_url_source,
            'ifc_available': ifc_exists,
            'ifc_path': f'/api/download/{job_id}/model.ifc' if ifc_exists else None,
            'members_count': len(result.get('miner', {}).get('members', [])) if isinstance(result, dict) else 0,
            'message': 'Ready for Tekla import',
            'viewer_url': viewer_url
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/export-tekla-direct/<job_id>')
def export_to_tekla_direct(job_id):
    """Send pipeline model objects directly to a connected Tekla API bridge."""
    result_path = os.path.join(OUTPUT_FOLDER, job_id, 'result.json')
    final_path = os.path.join(OUTPUT_FOLDER, job_id, 'final.json')
    
    if not os.path.exists(result_path) and not os.path.exists(final_path):
        return jsonify({'status': 'error', 'message': 'No pipeline result found'}), 404

    result_file = result_path if os.path.exists(result_path) else final_path
    with open(result_file, 'r') as f:
        result = json.load(f)

    record = query_job_record(job_id)
    company_id = record['company_id'] if record else None
    tekla_status = query_local_tekla_api('/api/v1/tekla/status', company_id=company_id)
    if not isinstance(tekla_status, dict) or not tekla_status.get('connected'):
        msg = tekla_status.get('error', 'Tekla API bridge is not available or not connected')
        return jsonify({'status': 'error', 'message': f'Direct Tekla API unavailable: {msg}'}), 503

    objects, warnings = convert_pipeline_result_to_tekla_objects(result)
    if not objects:
        return jsonify({'status': 'error', 'message': 'No valid Tekla objects could be created from the pipeline output', 'warnings': warnings}), 400

    payload = {'objects': objects, 'transaction_id': f'tx_{job_id}'}
    tekla_response = query_local_tekla_api('/api/v1/tekla/create', method='POST', payload=payload, company_id=company_id)

    if not isinstance(tekla_response, dict) or tekla_response.get('success') is not True:
        return jsonify({'status': 'error', 'message': 'Tekla API create call failed', 'tekla_response': tekla_response, 'warnings': warnings}), 500

    ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
    ifc_exists = os.path.exists(ifc_path)

    tekla_api_url, tekla_url_source = resolve_tekla_api_url(company_id)

    return jsonify({
        'status': 'ok',
        'job_id': job_id,
        'company_id': company_id,
        'tekla_api_url': tekla_api_url,
        'tekla_url_source': tekla_url_source,
        'tekla_sent': True,
        'tekla_response': tekla_response,
        'warnings': warnings,
        'ifc_available': ifc_exists,
        'ifc_path': f'/api/download/{job_id}/model.ifc' if ifc_exists else None
    }), 200


@app.route('/api/tekla/config/<company_id>')
def get_tekla_config(company_id):
    tekla_api_url, tekla_url_source = resolve_tekla_api_url(company_id)
    return jsonify({
        'status': 'ok',
        'company_id': company_id,
        'tekla_api_url': tekla_api_url,
        'resolved_from': tekla_url_source
    }), 200


@app.route('/viewer/<job_id>')
def viewer(job_id):
    """Render a 3D web viewer for the IFC model of a job."""
    # Check IFC availability
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    ifc_path = os.path.join(job_output_dir, 'model.ifc')
    has_ifc = os.path.exists(ifc_path)

    return render_template('viewer.html', job_id=job_id, has_ifc=has_ifc)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Pipeline service running'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
