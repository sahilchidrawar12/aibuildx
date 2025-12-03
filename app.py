"""
Flask web application for DWG→Tekla conversion pipeline.
Allows users to upload DWG files, run the full pipeline, and export to Tekla Structures.
"""
import os
import json
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file
from src.pipeline.pipeline_compat import run_pipeline

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'dwg', 'dxf', 'json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

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
        
        # Run pipeline
        job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        
        result = run_pipeline(filepath, out_dir=job_output_dir)
        
        if isinstance(result, dict) and result.get('status') == 'error':
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
            }
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
    
    files = [f for f in os.listdir(job_output_dir) if f.endswith(('.json', '.csv'))]
    return jsonify({
        'status': 'complete',
        'job_id': job_id,
        'files': files,
        'download_url': f'/api/download/{job_id}/'
    }), 200

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
        
        # Check for IFC
        ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
        ifc_exists = os.path.exists(ifc_path)
        
        return jsonify({
            'status': 'ok',
            'job_id': job_id,
            'ifc_available': ifc_exists,
            'ifc_path': f'/api/download/{job_id}/model.ifc' if ifc_exists else None,
            'members_count': len(result.get('miner', {}).get('members', [])) if isinstance(result, dict) else 0,
            'message': 'Ready for Tekla import'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Pipeline service running'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
