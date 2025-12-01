import os
import json
import uuid
import pytest

from src.pipeline import pipeline_v2 as pv2


def make_sample_members():
    return {
        'members': [
            {'id': str(uuid.uuid4()), 'start': [0.0, 0.0, 0.0], 'end': [6.0, 0.0, 0.0], 'length': 6.0, 'type': 'beam', 'selection': {'section_name': 'W8x10'}},
            {'id': str(uuid.uuid4()), 'start': [6.0, 0.0, 0.0], 'end': [6.0, 0.0, 4.0], 'length': 4.0, 'type': 'column', 'selection': {'section_name': 'HSS100x100x6'}},
        ]
    }


def test_builder_ifc_creates_extruded_solids(tmp_path):
    try:
        import ifcopenshell  # try optional dependency
    except Exception:
        pytest.skip("ifcopenshell not available; skipping IFC extrusion test")

    sample = make_sample_members()
    out_file = os.path.join(str(tmp_path), 'test_model.ifc')
    res = pv2.builder_ifc(sample, out_path=out_file)
    assert res is not None
    assert res.get('ifc') is not None
    # open with ifcopenshell and check for extruded solids
    model = ifcopenshell.open(res.get('ifc'))
    solids = model.by_type('IfcExtrudedAreaSolid')
    assert len(solids) >= 1, "Expected at least one IfcExtrudedAreaSolid in the IFC model"
