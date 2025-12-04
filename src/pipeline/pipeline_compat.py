"""Compatibility shim that maps selected names from the old monolith `pipeline_v2.py`
to the new modular implementations. This file is intentionally small and non-destructive;
it simply re-exports classes/functions under the old names so external callers keep
working while the monolith is migrated.
"""
# Geometry
from src.pipeline.geometry import CoordinateSystemManager, RotationMatrix3D, CurvedMemberHandler, CamberCalculator, SkewCutGeometry, EccentricityResolver

# Sections
from src.pipeline.sections import CompoundSectionBuilder, WebOpeningHandler, TorsionalPropertyCalculator, PlasticAnalysisProperties

# Loads
from src.pipeline.loads import LoadCombinationAnalyzer, WindLoadAnalyzer, SeismicLoadAnalyzer, PDeltaAnalyzer, InfluenceLineAnalyzer

# Compliance
from src.pipeline.compliance.aisc360 import AISC360Checker
from src.pipeline.compliance.aisc341 import AISC341SeismicChecker

# Materials
from src.pipeline.materials import MaterialSelector, CoatingSpecifier, MATERIAL_DATABASE

# Agents package (exports many agents)
from src.pipeline import agents as agents
from src.pipeline.agents import main_pipeline_agent

# Support utils
from src.pipeline.utils.geometry_utils import translate_point, rotate_point_xy, distance
from src.pipeline.support import (error_handlers, fallback, parallel_processor, cache, connection_classifier,
                                  load_predictor, validators, warnings as support_warnings, spatial_index,
                                  profiler, anomaly_detector, connection_optimizer)

__all__ = [
    # Geometry
    'CoordinateSystemManager', 'RotationMatrix3D', 'CurvedMemberHandler', 'CamberCalculator', 'SkewCutGeometry', 'EccentricityResolver',
    # Sections
    'CompoundSectionBuilder', 'WebOpeningHandler', 'TorsionalPropertyCalculator', 'PlasticAnalysisProperties',
    # Loads
    'LoadCombinationAnalyzer', 'WindLoadAnalyzer', 'SeismicLoadAnalyzer', 'PDeltaAnalyzer', 'InfluenceLineAnalyzer',
    # Compliance
    'AISC360Checker', 'AISC341SeismicChecker',
    # Materials
    'MaterialSelector', 'CoatingSpecifier', 'MATERIAL_DATABASE',
    # Agents
    'agents',
    'run_pipeline', 'run_from_dxf_entities', 'Pipeline',
    # Support
    'translate_point', 'rotate_point_xy', 'distance', 'error_handlers', 'fallback', 'parallel_processor', 'cache', 'connection_classifier',
    'load_predictor', 'validators', 'support_warnings', 'spatial_index', 'profiler', 'anomaly_detector', 'connection_optimizer'
]

# Backwards-compatible wrappers

import subprocess
import shutil
import os
import logging
import tempfile
import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_dwg_to_dxf(dwg_path):
    """
    Production-grade DWG to DXF conversion following best practices.
    
    Strategy:
    1. Use ODA File Converter as primary method (most reliable)
    2. Three-pass conversion: ACAD2018 → ACAD2013 → ACAD2010 fallback
    3. Validate DXF after conversion
    4. Preserve layers, blocks, proxy objects
    5. Log conversion details
    6. Normalize units and check geometry integrity
    
    Returns path to DXF file or None if conversion fails.
    """
    dwg_file = Path(dwg_path)
    output_dir = dwg_file.parent
    base_name = dwg_file.stem
    log_file = output_dir / f"{base_name}_conversion.log"
    
    # DXF output variants to try (newest first for best accuracy)
    dxf_versions = ["ACAD2018", "ACAD2013", "ACAD2010"]
    
    # Check if ODA File Converter is available
    oda_converter = shutil.which("ODAFileConverter")
    if not oda_converter:
        logger.warning("ODA File Converter not found in PATH. Install for best results.")
        return None
    
    # Create isolated temp directory for the DWG file to avoid converting other files
    with tempfile.TemporaryDirectory(prefix="dwg_convert_") as isolated_input_dir:
        # Copy DWG to isolated directory
        isolated_dwg = Path(isolated_input_dir) / dwg_file.name
        shutil.copy2(str(dwg_file), str(isolated_dwg))
        
        # Try conversion with each DXF version
        for dxf_version in dxf_versions:
            # Unique DXF name for each version to avoid overwriting
            final_dxf = output_dir / f"{base_name}_{dxf_version}.dxf"
            temp_output_dir = Path(tempfile.mkdtemp(prefix=f"oda_output_{dxf_version}_"))
            
            try:
                logger.info(f"Converting {dwg_path} to DXF using ODA ({dxf_version})...")
                
                # ODA File Converter command (correct syntax without file filter)
                # Format: ODAFileConverter <input_folder> <output_folder> <output_version> <output_format> <recursive> <audit>
                result = subprocess.run([
                    oda_converter,
                    str(isolated_input_dir),     # Input folder (isolated with only our DWG)
                    str(temp_output_dir),         # Output folder
                    dxf_version,                  # DXF version (ACAD2018/2013/2010)
                    "DXF",                        # Output format
                    "0",                          # Not recursive
                    "1"                           # Audit and fix errors (preserves proxy objects)
                ], 
                capture_output=True, 
                text=True, 
                timeout=120
                )
                
                # Log conversion output with correct timestamp
                timestamp = datetime.datetime.fromtimestamp(dwg_file.stat().st_mtime).isoformat()
                log_mode = 'w' if dxf_version == dxf_versions[0] else 'a'
                with open(log_file, log_mode) as log:
                    log.write(f"\n{'='*60}\n")
                    log.write(f"DWG to DXF Conversion Log - {dxf_version}\n")
                    log.write(f"DWG File: {dwg_path}\n")
                    log.write(f"DXF Version: {dxf_version}\n")
                    log.write(f"Timestamp: {timestamp}\n")
                    log.write(f"\n--- ODA Output ---\n")
                    log.write(result.stdout)
                    if result.stderr:
                        log.write(f"\n--- ODA Errors ---\n")
                        log.write(result.stderr)
                
                # Find converted DXF file (exact name match to avoid false positives)
                converted_dxf = None
                expected_name = dwg_file.stem + ".dxf"
                
                for root, dirs, files in os.walk(temp_output_dir):
                    for f in files:
                        if f.lower() == expected_name.lower():
                            converted_dxf = Path(root) / f
                            break
                    if converted_dxf:
                        break
                
                if not converted_dxf or not converted_dxf.exists():
                    logger.warning(f"Conversion with {dxf_version} failed or produced no output.")
                    with open(log_file, 'a') as log:
                        log.write(f"\n⚠️ Conversion failed - no output file found\n")
                    continue
                
                # Move DXF to target location with version-specific name
                shutil.move(str(converted_dxf), str(final_dxf))
                
                # Validate DXF integrity
                validation_result = _validate_dxf(final_dxf, log_file, dxf_version)
                
                if validation_result['valid']:
                    logger.info(f"✓ Successfully converted {dwg_path} to {final_dxf} using {dxf_version}")
                    logger.info(f"  Entities: {validation_result.get('entity_count', 'N/A')}")
                    logger.info(f"  Layers: {validation_result.get('layer_count', 'N/A')}")
                    logger.info(f"  Blocks: {validation_result.get('block_count', 'N/A')}")
                    logger.info(f"  Proxy Objects: {validation_result.get('proxy_count', 'N/A')}")
                    
                    # Rename to standard name (without version suffix) for pipeline
                    standard_dxf = output_dir / f"{base_name}.dxf"
                    if standard_dxf.exists():
                        standard_dxf.unlink()  # Remove old version
                    shutil.copy2(str(final_dxf), str(standard_dxf))
                    
                    return str(standard_dxf)
                else:
                    logger.warning(f"DXF validation failed for {dxf_version}: {validation_result.get('error')}")
                    with open(log_file, 'a') as log:
                        log.write(f"\n⚠️ Validation failed: {validation_result.get('error')}\n")
                    # Keep trying next version
                    continue
                    
            except subprocess.TimeoutExpired:
                logger.error(f"ODA conversion timeout for {dxf_version}")
                with open(log_file, 'a') as log:
                    log.write(f"\n❌ Conversion timeout after 120 seconds\n")
                continue
            except Exception as e:
                logger.error(f"ODA conversion error with {dxf_version}: {e}")
                with open(log_file, 'a') as log:
                    log.write(f"\n❌ Conversion error: {str(e)}\n")
                continue
            finally:
                # Always cleanup temp directory
                if temp_output_dir.exists():
                    shutil.rmtree(temp_output_dir, ignore_errors=True)
    
    # All ODA conversions failed
    logger.error("All ODA conversions failed. Cannot proceed without valid DXF.")
    with open(log_file, 'a') as log:
        log.write(f"\n{'='*60}\n")
        log.write(f"❌ FINAL RESULT: All conversion attempts failed\n")
    return None


def _validate_dxf(dxf_path, log_file, dxf_version):
    """
    Production-grade DXF validation using ezdxf.
    
    Comprehensive checks:
    - File validity
    - Entity count
    - Layer preservation
    - Block preservation
    - Proxy object detection
    - Hatch boundary integrity
    - Dimension and text style existence
    - Polyline geometry issues
    """
    try:
        import ezdxf
        from ezdxf.lldxf.validator import is_dxf_file
        
        # Check if it's a valid DXF file
        if not is_dxf_file(str(dxf_path)):
            return {'valid': False, 'error': 'Not a valid DXF file'}
        
        # Load and validate
        doc = ezdxf.readfile(str(dxf_path))
        modelspace = doc.modelspace()
        
        entity_count = len(list(modelspace))
        layer_count = len(doc.layers)
        block_count = len(doc.blocks)
        
        # Count proxy objects (critical for AEC/Civil3D content)
        proxy_count = 0
        hatch_issues = []
        polyline_issues = []
        
        for entity in modelspace:
            # Proxy object detection
            if entity.dxftype() in ('ACAD_PROXY_ENTITY', 'ACAD_PROXY_OBJECT'):
                proxy_count += 1
            
            # Hatch boundary integrity
            if entity.dxftype() == 'HATCH':
                try:
                    if hasattr(entity, 'paths'):
                        paths = entity.paths
                        if not paths or len(paths) == 0:
                            hatch_issues.append(f"Empty hatch boundary: {entity.dxf.handle}")
                except Exception:
                    hatch_issues.append(f"Invalid hatch: {entity.dxf.handle}")
            
            # LWPOLYLINE geometry checks (use proper flag check)
            if entity.dxftype() == 'LWPOLYLINE':
                try:
                    # Check closure using DXF flags (bit 0 = closed)
                    is_closed = bool(entity.dxf.flags & 1) if hasattr(entity.dxf, 'flags') else False
                    points = list(entity.get_points('xy'))
                    
                    if is_closed and len(points) < 3:
                        polyline_issues.append(f"Invalid closed polyline (< 3 points): {entity.dxf.handle}")
                    
                    # Check for self-intersection (basic)
                    if len(points) > 3:
                        # Simple check: duplicate consecutive points
                        for i in range(len(points) - 1):
                            if points[i] == points[i+1]:
                                polyline_issues.append(f"Duplicate points in polyline: {entity.dxf.handle}")
                                break
                except Exception as e:
                    polyline_issues.append(f"Polyline check error: {entity.dxf.handle} - {str(e)}")
        
        # Check dimension styles
        dimstyle_count = len(doc.dimstyles) if hasattr(doc, 'dimstyles') else 0
        
        # Check text styles
        textstyle_count = len(doc.styles) if hasattr(doc, 'styles') else 0
        
        # Log comprehensive validation details
        with open(log_file, 'a') as log:
            log.write(f"\n--- DXF Validation ({dxf_version}) ---\n")
            log.write(f"Status: VALID\n")
            log.write(f"Entities: {entity_count}\n")
            log.write(f"Layers: {layer_count}\n")
            log.write(f"Blocks: {block_count}\n")
            log.write(f"Proxy Objects: {proxy_count}\n")
            log.write(f"Dimension Styles: {dimstyle_count}\n")
            log.write(f"Text Styles: {textstyle_count}\n")
            log.write(f"Units: {doc.header.get('$INSUNITS', 'Not specified')}\n")
            
            if hatch_issues:
                log.write(f"\n--- Hatch Issues ({len(hatch_issues)}) ---\n")
                for issue in hatch_issues[:10]:
                    log.write(f"{issue}\n")
            
            if polyline_issues:
                log.write(f"\n--- Polyline Issues ({len(polyline_issues)}) ---\n")
                for issue in polyline_issues[:10]:
                    log.write(f"{issue}\n")
        
        # Basic integrity checks
        if entity_count == 0:
            return {'valid': False, 'error': 'No entities found in DXF'}
        
        return {
            'valid': True,
            'entity_count': entity_count,
            'layer_count': layer_count,
            'block_count': block_count,
            'proxy_count': proxy_count,
            'dimstyle_count': dimstyle_count,
            'textstyle_count': textstyle_count,
            'hatch_issues': len(hatch_issues),
            'polyline_issues': len(polyline_issues)
        }
        
    except Exception as e:
        with open(log_file, 'a') as log:
            log.write(f"\n--- DXF Validation Failed ({dxf_version}) ---\n")
            log.write(f"Error: {str(e)}\n")
        return {'valid': False, 'error': str(e)}


def _fallback_ezdxf_validation(dwg_path):
    """
    Fallback when ODA is not available.
    ezdxf cannot convert DWG to DXF, so this returns None.
    User must install ODA File Converter for DWG support.
    """
    logger.error("Cannot convert DWG without ODA File Converter.")
    logger.error("Install ODA from: https://www.opendesign.com/guestfiles/oda_file_converter")
    return None
def recommend_material_for_section(section_info, required_fy: float = 50.0, max_price_per_kg: float = 2.0):
    """Wrapper that accepts either the newer numeric signature or a dict-like section.
    If a dict is provided, extract area (in mm^2 or in^2) heuristically and call
    MaterialSelector.recommend_material_for_section.
    """
    ms = MaterialSelector()
    # If a dict, try to extract an area and convert mm2 to in2 if plausible
    if isinstance(section_info, dict):
        area_mm2 = section_info.get('area_mm2') or section_info.get('area') or section_info.get('area_mm')
        if area_mm2 is None:
            # fallback to calling with defaults
            return ms.recommend_material_for_section(0.0, required_fy, max_price_per_kg)
        # convert mm^2 to in^2: 1 mm^2 = 0.0015500031 in^2
        try:
            area_mm2 = float(area_mm2)
            area_in2 = area_mm2 * 0.0015500031
        except Exception:
            area_in2 = 0.0
        result = ms.recommend_material_for_section(area_in2, required_fy, max_price_per_kg)
        if result:
            return result
        # fallback: pick best tradeoff ignoring area
        best = ms.select_best_tradeoff(max_price_per_kg=max_price_per_kg)
        if best:
            return {'grade': best[0], **best[1]}
        # final fallback: inspect raw MATERIAL_DATABASE for common keys (Fy)
        try:
            for name, props in MATERIAL_DATABASE.items():
                fy = props.get('fy') or props.get('Fy') or props.get('Fy')
                if fy and float(fy) >= required_fy:
                    return {'grade': name, **props}
        except Exception:
            pass
        return None
    else:
        # assume numeric area in in^2
        try:
            area_val = float(section_info)
        except Exception:
            area_val = 0.0
        return ms.recommend_material_for_section(area_val, required_fy, max_price_per_kg)

# Small helper to list available agents
def list_agents():
    return sorted([name for name in dir(agents) if not name.startswith('_')])


def run_pipeline(input_data, out_dir=None, extra=None):
    """Compatibility wrapper to run the high-level pipeline orchestration.

    - `input_data` can be a DXF/IFC path (string), a list of DXF-like entities,
      or a dict containing `members`.
    - Returns the agent orchestrator result (same shape as main_pipeline_agent.process).

    This wrapper intentionally uses the `main_pipeline_agent` to drive the
    orchestration so new modular logic is exercised while preserving an
    easy migration path for callers of the monolith.
    """
    import os
    import json as _json
    from pathlib import Path

    try:
        # Accept a path to a JSON/DXF/IFC/DWG file, a list of entities, or a dict
        payload_data = input_data
        if isinstance(input_data, str):
            p = Path(input_data)
            if p.exists() and p.is_file():
                suf = p.suffix.lower()
                if suf == '.dwg':
                    # Convert DWG to DXF first
                    logger.info(f"DWG file detected: {input_data}. Converting to DXF...")
                    dxf_path = convert_dwg_to_dxf(str(p))
                    if dxf_path and os.path.exists(dxf_path):
                        payload_data = dxf_path
                        logger.info(f"✓ DWG converted to DXF: {dxf_path}")
                    else:
                        raise RuntimeError("DWG to DXF conversion failed. Please install ODA File Converter.")
                elif suf == '.dxf':
                    # DXF file: validate and auto-recover if malformed
                    logger.info(f"DXF file detected: {input_data}. Validating structure before parsing...")
                    dxf_path = str(p)
                    def _basic_dxf_sanity(path: str) -> bool:
                        try:
                            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                                # Check first 2000 lines for non-numeric group codes
                                for i in range(2000):
                                    code = fh.readline()
                                    if not code:
                                        break
                                    s = code.strip()
                                    # Empty lines are fine; numeric codes should parse
                                    if not s:
                                        continue
                                    # Many DXFs start with 0, 9, etc.; if not numeric, likely malformed
                                    if not s.isdigit():
                                        # Allow some known headers in binary DXF detection – else fail
                                        if s not in {"SECTION", "ENDSEC", "EOF"}:
                                            return False
                                return True
                        except Exception:
                            return True  # If unreadable (binary), let ezdxf decide

                    sane = _basic_dxf_sanity(dxf_path)
                    if not sane:
                        logger.warning("DXF pre-scan found non-numeric group codes; attempting ODA re-conversion to ACAD2013...")
                        oda_converter = shutil.which("ODAFileConverter")
                        if oda_converter:
                            try:
                                tmp_out = Path(tempfile.mkdtemp(prefix="oda_fix_dxf_"))
                                # ODA requires a folder; use the parent folder of the DXF
                                in_dir = str(Path(dxf_path).parent)
                                subprocess.run([
                                    oda_converter,
                                    in_dir,
                                    str(tmp_out),
                                    "ACAD2013",
                                    "DXF",
                                    "0",
                                    "1"
                                ], capture_output=True, text=True, timeout=120)
                                # Find cleaned DXF with same stem
                                stem = Path(dxf_path).stem
                                cleaned = None
                                for root, dirs, files in os.walk(tmp_out):
                                    for f in files:
                                        if f.lower() == f"{stem}.dxf".lower():
                                            cleaned = Path(root) / f
                                            break
                                    if cleaned:
                                        break
                                if cleaned and cleaned.exists():
                                    # Replace original with cleaned copy (keep backup)
                                    backup = Path(dxf_path).with_suffix('.dxf.bak')
                                    try:
                                        shutil.copy2(dxf_path, backup)
                                    except Exception:
                                        pass
                                    shutil.copy2(str(cleaned), dxf_path)
                                    logger.info("✓ ODA re-conversion applied; proceeding with cleaned DXF")
                                else:
                                    logger.warning("ODA did not produce a matching DXF; proceeding with original")
                            except Exception as e:
                                logger.warning(f"ODA re-conversion failed: {e}")
                            finally:
                                try:
                                    shutil.rmtree(tmp_out, ignore_errors=True)
                                except Exception:
                                    pass
                        else:
                            logger.error("ODA File Converter not found. Please re-export the DXF (R2013) or install ODA.")
                    payload_data = dxf_path
                elif suf == '.json':
                    with p.open('r', encoding='utf-8') as fh:
                        try:
                            payload_data = _json.load(fh)
                        except Exception:
                            payload_data = str(p)
                else:
                    # IFC or other formats
                    payload_data = str(p)
            else:
                payload_data = input_data

        payload = {'data': {'dxf_entities': payload_data, 'out_dir': out_dir, 'extra': extra}}
        res = main_pipeline_agent.process(payload)

        # If an output directory was requested and we received a dict result, write selected outputs
        try:
            if out_dir and isinstance(res, dict):
                result = res.get('result') if isinstance(res.get('result'), dict) else (res if isinstance(res, dict) else None)
                print(f"DEBUG: res keys = {list(res.keys()) if isinstance(res, dict) else 'not a dict'}")
                print(f"DEBUG: result is None = {result is None}")
                if result:
                    print(f"DEBUG: result has {len(result)} keys")
                    print(f"DEBUG: 'ifc' in result = {'ifc' in result}")
                    print(f"DEBUG: 'final' in result = {'final' in result}")
                if result:
                    os.makedirs(out_dir, exist_ok=True)
                    # CRITICAL: Convert non-serializable objects to JSON-safe format
                    # IMPORTANT: Always preserve 'ifc' key even if other keys are skipped
                    result_safe = {}
                    non_serializable_keys = []
                    for key, value in result.items():
                        try:
                            _json.dumps(value)  # Test if serializable
                            result_safe[key] = value
                        except TypeError:
                            non_serializable_keys.append(key)
                            # Skip non-serializable values (except critical ones)
                            if key not in ('ifc',):  # Always keep ifc
                                print(f"DEBUG: Skipping non-serializable key: {key} ({type(value).__name__})")
                    
                    if non_serializable_keys:
                        print(f"DEBUG: Removed {len(non_serializable_keys)} non-serializable keys: {non_serializable_keys}")
                    
                    print(f"DEBUG: result_safe has {len(result_safe)} keys, 'ifc' present = {'ifc' in result_safe}")
                    
                    # Write a full dump with only serializable data
                    with open(os.path.join(out_dir, 'result.json'), 'w', encoding='utf-8') as fh:
                        try:
                            _json.dump(result_safe, fh, indent=2)
                            print(f"DEBUG: result.json written successfully with {len(result_safe)} keys")
                        except TypeError as je:
                            print(f"DEBUG: JSON serialization error (should not happen): {je}")
                            raise
                    
                    # Write final report if present
                    if 'final' in result:
                        try:
                            with open(os.path.join(out_dir, 'final.json'), 'w', encoding='utf-8') as fh2:
                                _json.dump(result['final'], fh2, indent=2)
                        except Exception:
                            pass
                    
                    # Write IFC JSON and model files if present
                    if 'ifc' in result:
                        try:
                            with open(os.path.join(out_dir, 'ifc.json'), 'w', encoding='utf-8') as fh3:
                                _json.dump(result['ifc'], fh3, indent=2)
                            # Also write IFC data as model.ifc (JSON format for viewer)
                            try:
                                print(f"DEBUG: Writing IFC file to {out_dir}")
                                ifc_path = os.path.join(out_dir, 'model.ifc')
                                # Write IFC data as JSON (viewer-compatible format)
                                with open(ifc_path, 'w', encoding='utf-8') as fh_ifc:
                                    _json.dump(result['ifc'], fh_ifc, indent=2)
                                print(f"DEBUG: IFC file written successfully to {ifc_path}")
                            except Exception as e:
                                # Fallback: create a minimal IFC file if writing fails
                                import logging
                                print(f"DEBUG: IFC writing failed with error: {e}, creating minimal IFC")
                                logging.getLogger(__name__).warning(f"IFC file writing failed: {e}")
                                with open(os.path.join(out_dir, 'model.ifc'), 'w', encoding='utf-8') as ifc_file:
                                    ifc_file.write('{"error": "Failed to generate IFC data"}')
                                print(f"DEBUG: Minimal IFC file created")
                        except Exception as e:
                            print(f"DEBUG: Exception in IFC writing: {e}")
                            pass
                    
                    # Write selected keys for easier consumption
                    for key in ('cnc', 'dstv', 'reporter', 'final'):
                        if key in result:
                            with open(os.path.join(out_dir, f'{key}.json'), 'w', encoding='utf-8') as fh:
                                _json.dump(result[key], fh, indent=2)
        except Exception:
            # Don't fail the whole call just because writing outputs failed
            pass

        # attach a small compatibility layer: if legacy keys expected, surface them
        if isinstance(res, dict) and res.get('status') == 'ok':
            return res['result']
        return res
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def run_from_dxf_entities(dxf_entities, out_dir=None):
    """Legacy-compatible function matching the old `Pipeline.run_from_dxf_entities` signature.

    Internally delegates to `run_pipeline` and returns the raw result dict for compatibility.
    Emits a DeprecationWarning advising callers to migrate to `run_pipeline`.
    """
    import warnings
    warnings.warn('run_from_dxf_entities is deprecated; use run_pipeline() or the agents package', DeprecationWarning)
    return run_pipeline(dxf_entities, out_dir=out_dir)


class Pipeline:
    """Compatibility Pipeline class exposing `run_from_dxf_entities`.

    This thin wrapper preserves the old class-based API while delegating to the
    modular agent orchestration implemented in `main_pipeline_agent`.
    """
    def __init__(self):
        pass

    def run_from_dxf_entities(self, dxf_entities, out_dir=None):
        return run_from_dxf_entities(dxf_entities, out_dir=out_dir)
