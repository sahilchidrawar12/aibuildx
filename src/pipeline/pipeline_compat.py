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
        # Accept a path to a JSON/DXF/IFC file, a list of entities, or a dict
        payload_data = input_data
        if isinstance(input_data, str):
            p = Path(input_data)
            if p.exists() and p.is_file():
                suf = p.suffix.lower()
                if suf == '.json':
                    with p.open('r', encoding='utf-8') as fh:
                        try:
                            payload_data = _json.load(fh)
                        except Exception:
                            # If JSON parse fails, pass the path through
                            payload_data = str(p)
                else:
                    # For .dxf/.ifc and other files pass path through
                    payload_data = str(p)
            else:
                # Not a file on disk: treat as inline identifier or content string
                payload_data = input_data

        payload = {'data': {'dxf_entities': payload_data, 'out_dir': out_dir, 'extra': extra}}
        res = main_pipeline_agent.process(payload)

        # If an output directory was requested and we received a dict result, write selected outputs
        try:
            if out_dir and isinstance(res, dict):
                result = res.get('result') if isinstance(res.get('result'), dict) else (res if isinstance(res, dict) else None)
                if result:
                    os.makedirs(out_dir, exist_ok=True)
                    # Write a full dump
                    with open(os.path.join(out_dir, 'result.json'), 'w', encoding='utf-8') as fh:
                        _json.dump(result, fh, indent=2)
                        # Also write aggregated final report and IFC if present
                        if 'final' in result:
                            try:
                                with open(os.path.join(out_dir, 'final.json'), 'w', encoding='utf-8') as fh2:
                                    _json.dump(result['final'], fh2, indent=2)
                            except Exception:
                                pass
                        if 'ifc' in result:
                            try:
                                with open(os.path.join(out_dir, 'ifc.json'), 'w', encoding='utf-8') as fh3:
                                    _json.dump(result['ifc'], fh3, indent=2)
                            except Exception:
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
