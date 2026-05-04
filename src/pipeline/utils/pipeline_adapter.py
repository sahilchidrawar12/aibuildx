"""Adapter + smoke test to exercise modularized pipeline components.
This file performs safe imports and runs small example calls to verify integration.
"""
from typing import Dict, Any
import json


def _safe_import(module_name: str, attr: str = None):
    try:
        mod = __import__(module_name, fromlist=['*'])
        if attr:
            return getattr(mod, attr)
        return mod
    except Exception as e:
        return e


def run_smoke_test() -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    # Materials
    ms_cls = _safe_import('src.pipeline.materials.material_selector', 'MaterialSelector')
    cs_cls = _safe_import('src.pipeline.materials.coating', 'CoatingSpecifier')
    if isinstance(ms_cls, Exception):
        results['material_selector'] = {'error': str(ms_cls)}
    else:
        try:
            ms = ms_cls()
            results['material_selector'] = {'ok': True, 'sample': ms.recommend_material_for_section({'area_mm2': 1000}) if hasattr(ms, 'recommend_material_for_section') else 'instantiated'}
        except Exception as e:
            results['material_selector'] = {'error': str(e)}
    if isinstance(cs_cls, Exception):
        results['coating_specifier'] = {'error': str(cs_cls)}
    else:
        try:
            cs = cs_cls()
            results['coating_specifier'] = {'ok': True, 'options': cs.list_options() if hasattr(cs, 'list_options') else 'instantiated'}
        except Exception as e:
            results['coating_specifier'] = {'error': str(e)}

    # Loads
    lc_cls = _safe_import('src.pipeline.loads.load_combinations', 'LoadCombinationAnalyzer')
    if isinstance(lc_cls, Exception):
        results['load_combinations'] = {'error': str(lc_cls)}
    else:
        try:
            lca = lc_cls()
            # Add sample load cases then calculate combinations
            if hasattr(lca, 'add_load_case'):
                lca.add_load_case('D', {'shear': 10.0, 'moment': 50.0})
                lca.add_load_case('L', {'shear': 15.0, 'moment': 75.0})
            combos = None
            if hasattr(lca, 'calculate_combinations'):
                combos = lca.calculate_combinations()
            results['load_combinations'] = {'ok': True, 'sample': combos}
        except Exception as e:
            results['load_combinations'] = {'error': str(e)}

    # Compliance
    aisc_cls = _safe_import('src.pipeline.compliance.aisc360', 'AISC360Checker')
    if isinstance(aisc_cls, Exception):
        results['aisc360'] = {'error': str(aisc_cls)}
    else:
        try:
            # instantiate with typical structural steel strengths (ksi)
            checker = aisc_cls(50.0, 65.0)
            res = None
            if hasattr(checker, 'tensile_capacity'):
                res = checker.tensile_capacity(10.0)
            results['aisc360'] = {'ok': True, 'sample': res}
        except Exception as e:
            results['aisc360'] = {'error': str(e)}

    # Agents (main pipeline)
    main_proc = _safe_import('src.pipeline.agents.main_pipeline_agent', 'process')
    if isinstance(main_proc, Exception):
        results['main_pipeline_agent'] = {'error': str(main_proc)}
    else:
        try:
            out = main_proc({'data': {'hazard': 0.1, 'exposure': 0.2, 'items': [{'x': 1}, {'x': 2}]}})
            results['main_pipeline_agent'] = {'ok': True, 'output': out}
        except Exception as e:
            results['main_pipeline_agent'] = {'error': str(e)}

    return results


if __name__ == '__main__':
    r = run_smoke_test()
    print(json.dumps(r, indent=2))
