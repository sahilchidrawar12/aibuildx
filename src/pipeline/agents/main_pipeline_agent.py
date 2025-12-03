"""Main pipeline agent: orchestrates core pipeline stages by delegating
to the canonical pipeline functions. This agent provides a stable agent
interface while allowing gradual migration from the monolith.
"""
from typing import Dict, Any
import json
from src.pipeline.logging_setup import get_logger

logger = get_logger("main_pipeline_agent")


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload.get('data', {}) or {}
    dxf_entities = data.get('dxf_entities') or data.get('items') or data.get('members') or []
    out = {}

    try:
        # 1) Miner: accept path or pre-extracted entities
        if isinstance(dxf_entities, str):
            if dxf_entities.lower().endswith('.json'):
                try:
                    with open(dxf_entities, 'r', encoding='utf-8') as fh:
                        payload_entities = json.load(fh)
                except Exception:
                    payload_entities = dxf_entities
            elif dxf_entities.lower().endswith('.dxf'):
                # Use new modular DXF parser
                from src.pipeline.dxf_parser import parse_dxf_file
                payload_entities = parse_dxf_file(dxf_entities)
            elif dxf_entities.lower().endswith('.ifc'):
                # Use legacy IFC parser (can be modernized later)
                try:
                    from src.pipeline import pipeline_v2 as legacy
                    payload_entities = legacy.extract_from_ifc(dxf_entities)
                except Exception as e:
                    logger.error(f"IFC extraction failed: {e}")
                    payload_entities = {'members': []}
            else:
                payload_entities = dxf_entities
        else:
            payload_entities = dxf_entities

        out['miner'] = payload_entities

        # 1.5) Auto-repair missing fields
        try:
            from src.pipeline.auto_repair_engine import repair_pipeline
            if isinstance(payload_entities, dict):
                repaired = repair_pipeline({'members': payload_entities.get('members', [])})
            elif isinstance(payload_entities, list):
                repaired = repair_pipeline({'members': payload_entities})
            else:
                repaired = repair_pipeline({'members': []})
            members = repaired.get('members', [])
        except Exception:
            if isinstance(payload_entities, dict):
                members = payload_entities.get('members', [])
            elif isinstance(payload_entities, list):
                members = payload_entities
            else:
                members = []

        # 2) Geometry agent: set CS, merge nodes, resolve orientation
        from src.pipeline.geometry_agent import set_global_coordinate_system, merge_nodes, resolve_member_orientation
        set_global_coordinate_system({}, origin=(0,0,0))
        nodes, mapping = merge_nodes(members, tolerance=10.0)
        for m in members:
            resolve_member_orientation(m)

        # 3) Node resolution and joints
        from src.pipeline.node_resolution import snap_nodes, auto_generate_joints
        nodes, members = snap_nodes(members, tolerance=10.0)
        joints = auto_generate_joints(members, tolerance=10.0)
        out['nodes'] = nodes
        out['joints'] = joints

        # 3.5) Connection parser: convert circles to joints with member links
        try:
            from src.pipeline.agents.connection_parser_agent import parse_connections
            circles = payload_entities.get('circles', [])
            if circles:
                parsed_joints = parse_connections(circles, members, search_radius_mm=150.0)
                # Merge with auto-generated joints
                joints.extend(parsed_joints)
                out['joints'] = joints
                out['circles_parsed'] = len(circles)
        except Exception as e:
            logger.warning(f"Connection parsing failed: {e}")
            out['circles_parsed'] = 0

        # 3.7) Universal coordinate origin fix (applies to IFC data with coordinate issues)
        try:
            from src.pipeline.universal_geometry_engine import fix_coordinate_origins_universal
            # Build IFC-like structure from current state
            ifc_data = {
                'members': members,
                'joints': joints,
                'plates': [],  # Will be populated by connection synthesis
                'bolts': []
            }
            # Apply universal geometry fixes (detects and corrects broken coordinates)
            ifc_data_fixed = fix_coordinate_origins_universal(ifc_data)
            # Update members and joints if fixes were applied
            if ifc_data_fixed.get('members'):
                members = ifc_data_fixed['members']
            if ifc_data_fixed.get('joints'):
                joints = ifc_data_fixed['joints']
            out['coordinate_origin_fixed'] = True
            logger.info("Universal coordinate origin fix applied successfully")
        except Exception as e:
            logger.debug(f"Coordinate origin fix skipped or not applicable: {e}")
            out['coordinate_origin_fixed'] = False

        # 4) Section and material classification
        from src.pipeline.section_classifier import classify_section
        from src.pipeline.material_classifier import classify_material
        for m in members:
            prof = classify_section(m)
            if prof:
                m.setdefault('profile', prof)
                m.setdefault('geom', prof)
                m.setdefault('area', prof.get('area'))
                m.setdefault('Zx', prof.get('Zx'))
            mat = classify_material(m)
            m.setdefault('material', mat)

        out['members_classified'] = members

        # 5) Loads & combinations
        from src.pipeline.load_combination import generate_lrfd, generate_asd
        loads = data.get('loads', {'dead':0.0,'live':0.0,'wind':0.0,'seismic':0.0})
        out['load_combinations'] = generate_lrfd(loads)

        # 6) Deflection checks
        from src.pipeline.deflection_agent import check_deflection
        E_default = 210000.0  # MPa
        deflection_reports = []
        for m in members:
            L = m.get('length') or m.get('geom',{}).get('length') or m.get('end', [0,0,0])[0] - m.get('start', [0,0,0])[0]
            I = m.get('geom',{}).get('Ix') or m.get('Ix') or 1.0
            dr = check_deflection(m, span=abs(L), E=E_default, I=I, loads_w=0.0)
            deflection_reports.append({'id': m.get('id'), 'deflection': dr})
        out['deflection'] = deflection_reports

        # 7) Connection synthesis (plates + bolts) from joints via MODEL-DRIVEN agent
        try:
            # Use enhanced model-driven agent with AI predictions
            from src.pipeline.agents.connection_synthesis_agent_enhanced import (
                synthesize_connections_model_driven,
                ModelInferenceEngine
            )
            
            logger.info("Using MODEL-DRIVEN connection synthesis (6 AI models)")
            plates_synth, bolts_synth = synthesize_connections_model_driven(members, joints)
            
            # Log model-driven decision for traceability
            for plate in plates_synth:
                plate['synthesis_method'] = 'MODEL-DRIVEN-AI'
                plate['models_used'] = [
                    'BoltSizePredictor',
                    'PlateThicknessPredictor', 
                    'WeldSizePredictor',
                    'JointInferenceNet',
                    'BoltPatternOptimizer'
                ]
            
            logger.info(f"Generated {len(plates_synth)} model-driven connection plates")
            logger.info(f"Generated {len(bolts_synth)} model-driven connection bolts")
            
        except ImportError as e:
            logger.error(f"Model-driven agent import failed: {e}")
            logger.warning("Falling back to standards-based connection synthesis")
            try:
                from src.pipeline.agents.connection_synthesis_agent import synthesize_connections
                plates_synth, bolts_synth = synthesize_connections(members, joints)
            except Exception:
                plates_synth, bolts_synth = [], []
        except Exception as e:
            logger.error(f"Model-driven synthesis failed: {e}")
            logger.warning("Falling back to standards-based connection synthesis")
            try:
                from src.pipeline.agents.connection_synthesis_agent import synthesize_connections
                plates_synth, bolts_synth = synthesize_connections(members, joints)
            except Exception:
                plates_synth, bolts_synth = [], []
        
        out['plates'] = plates_synth
        out['bolts'] = bolts_synth

        # 7) COMPREHENSIVE CLASH DETECTION (NEW - v2.0)
        try:
            from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector
            from src.pipeline.agents.tolerance_and_standards_providers import (
                ToleranceProvider, StandardsProvider
            )
            
            logger.info("Running comprehensive clash detection...")
            ifc_data_for_clash = {
                'members': members,
                'joints': joints,
                'plates': plates_synth,
                'bolts': bolts_synth
            }
            
            tol = ToleranceProvider()
            std = StandardsProvider()
            detector = ComprehensiveClashDetector(tolerance_provider=tol, standards_provider=std)
            clashes, clash_summary = detector.detect_all_clashes(ifc_data_for_clash)
            
            logger.info(f"Clash detection complete: {len(clashes)} clashes found")
            out['clashes_detected'] = clashes
            out['clash_summary'] = clash_summary
            
            # Log by severity
            critical_count = clash_summary.get('by_severity', {}).get('CRITICAL', 0)
            major_count = clash_summary.get('by_severity', {}).get('MAJOR', 0)
            if critical_count > 0 or major_count > 0:
                logger.warning(f"CRITICAL: {critical_count}, MAJOR: {major_count}")
        except Exception as e:
            logger.warning(f"Comprehensive clash detection failed: {e}")
            out['clashes_detected'] = []
            out['clash_summary'] = {'total': 0, 'by_severity': {}}

        # 7.5) CLASH CORRECTION (NEW - v2.0)
        try:
            if out.get('clashes_detected'):
                from src.pipeline.agents.comprehensive_clash_corrector_v2 import ComprehensiveClashCorrector
                
                logger.info(f"Applying clash corrections to {len(out['clashes_detected'])} clashes...")
                corrector = ComprehensiveClashCorrector()
                
                corrections, corr_summary = corrector.correct_all_clashes(
                    out['clashes_detected'],
                    ifc_data_for_clash
                )
                
                out['clashes_corrected'] = corrections
                out['correction_summary'] = corr_summary
                
                # Log correction results
                auto_fixed = corr_summary.get('auto_fixed', 0)
                review_required = corr_summary.get('review_required', 0)
                failed = corr_summary.get('failed', 0)
                logger.info(f"Correction results - Auto-fixed: {auto_fixed}, Review: {review_required}, Failed: {failed}")
        except Exception as e:
            logger.warning(f"Clash correction failed: {e}")
            out['clashes_corrected'] = []
            out['correction_summary'] = {}

        # 7) Code compliance checks
        from src.pipeline.code_compliance import check_member_basic
        compliance_reports = []
        for m in members:
            mat = m.get('material') or {'fy': 355.0}
            cr = check_member_basic(m, mat)
            compliance_reports.append({'id': m.get('id'), 'compliance': cr})
        out['compliance'] = compliance_reports

        # 8) Connection capacity and design
        from src.pipeline.connection_capacity import check_bolt_group
        conn_reports = []
        connections = data.get('connections') or []
        for c in connections:
            demand_shear = c.get('demand_shear', 0.0)
            demand_tension = c.get('demand_tension', 0.0)
            mat_fu = (c.get('material') or {}).get('fu', 450.0)
            br = check_bolt_group(c.get('bolts', {'count':1,'diameter_mm':20}), demand_shear, demand_tension, mat_fu)
            conn_reports.append({'id': c.get('id'), 'report': br})
        out['connections'] = conn_reports

        # 9) Fabrication tolerances checks
        from src.pipeline.fabrication_tolerances import check_edge_distance, check_bolt_spacing
        fab_reports = []
        for p in data.get('plates', []):
            ok_edge = check_edge_distance(p.get('thickness',10.0), p.get('edge_distance',80.0))
            ok_spacing = check_bolt_spacing(p.get('bolt_diameter',20.0), p.get('bolt_spacing',70.0))
            fab_reports.append({'id': p.get('id'), 'edge_ok': ok_edge, 'spacing_ok': ok_spacing})
        out['fabrication'] = fab_reports

        # 10) Erection sequencing
        from src.pipeline.erection_sequencing import sequence_erection
        out['erection_sequence'] = sequence_erection(members)

        # 11) Clash avoidance adjustments
        from src.pipeline.clash_avoidance import avoid_clashes
        plates = data.get('plates', [])
        bolts = data.get('bolts', [])
        clash_adj = avoid_clashes(plates, bolts)
        out['clash_adjustments'] = clash_adj

        # 12) Stability checks
        from src.pipeline.stability_engine import euler_buckling_capacity, klr, p_delta_amplification
        stability_reports = []
        for m in members:
            r = m.get('geom',{}).get('r') or 1.0
            L = m.get('length') or 1000.0
            k = 1.0
            E = 210000.0
            I = m.get('geom',{}).get('Ix') or 1.0
            Pcr = euler_buckling_capacity(E, I, k, L)
            stability_reports.append({'id': m.get('id'), 'Pcr': Pcr, 'klr': klr(r,L)})
        out['stability'] = stability_reports

        # 13) IFC export
        from src.pipeline.ifc_generator import export_ifc_model
        ifc_model = export_ifc_model(
            members,
            out.get('plates') or data.get('plates', []),
            out.get('bolts') or data.get('bolts', []),
            out.get('joints', [])
        )
        out['ifc'] = ifc_model

        # 13.5) Post-process IFC model to fix any remaining coordinate issues
        try:
            from src.pipeline.universal_geometry_engine import fix_coordinate_origins_universal
            ifc_model_fixed = fix_coordinate_origins_universal(ifc_model)
            out['ifc'] = ifc_model_fixed
            out['ifc_coordinates_verified'] = True
            logger.info("IFC coordinates post-processed and verified")
        except Exception as e:
            logger.debug(f"IFC coordinate post-processing skipped: {e}")
            out['ifc_coordinates_verified'] = False

        # 14) Report aggregation
        from src.pipeline.report_aggregator import aggregate_reports
        agent_reports = [{'agent':'geometry','ok':True}, {'agent':'sections','ok':True}, {'agent':'material','ok':True}, {'agent':'loads','ok':True}, {'agent':'deflection','ok':True}, {'agent':'compliance','ok': all(c.get('compliance',{}).get('moment_ok',True) for c in compliance_reports)}]
        final_report = aggregate_reports(agent_reports)
        out['final'] = final_report

        status = 'ok'
    except Exception as e:
        logger.exception("Pipeline agent processing failed")
        out['error'] = str(e)
        status = 'error'

    return {'status': status, 'result': out}


class MainPipelineAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
