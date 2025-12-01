import pytest

from src.pipeline.pipeline_v2 import mesh_clasher_agent, precise_mesh_clasher


def test_mesh_clasher_fallback():
    # simple orthogonal members should not clash
    sample = {'members': [
        {'id': 'm1', 'start': [0,0,0], 'end': [6,0,0], 'length': 6.0, 'selection': {'section_name': 'W8x10'}},
        {'id': 'm2', 'start': [6,0,0], 'end': [6,0,4], 'length': 4.0, 'selection': {'section_name': 'W8x10'}}
    ]}
    res = mesh_clasher_agent(sample)
    assert isinstance(res, dict)
    assert 'clashes' in res


def test_precise_mesh_clasher_optional():
    try:
        import trimesh  # type: ignore
    except Exception:
        pytest.skip('trimesh not installed; skipping precise mesh test')
    sample = {'members': [
        {'id': 'm1', 'start': [0,0,0], 'end': [2,0,0], 'length': 2.0, 'selection': {'section_name': 'W8x10'}},
        {'id': 'm2', 'start': [0.5,0,0], 'end': [2.5,0,0], 'length': 2.0, 'selection': {'section_name': 'W8x10'}}
    ]}
    res = precise_mesh_clasher(sample)
    assert isinstance(res, dict)
    assert 'clashes' in res
