import os
import json
import pytest


def test_ifc_export_writable_and_readable(tmp_path):
    # skip the test if ifcopenshell is not available in the environment
    ifcopenshell = pytest.importorskip('ifcopenshell')
    sample_path = os.path.join('examples', 'sample_input.json')
    with open(sample_path, 'r') as f:
        entities = json.load(f)
    from src.pipeline.pipeline_v2 import Pipeline
    p = Pipeline()
    out_dir = str(tmp_path)
    result = p.run_from_dxf_entities(entities, out_dir=out_dir)
    # the pipeline returns an 'ifc' entry with path when written
    ifc_info = result.get('ifc') or {}
    ifc_path = ifc_info.get('ifc') or os.path.join(out_dir, 'model.ifc')
    assert os.path.exists(ifc_path), f'IFC file not found at {ifc_path}'
    # try opening with ifcopenshell
    model = ifcopenshell.open(ifc_path)
    # assert that there is at least one beam or column or building element proxy
    beams = model.by_type('IfcBeam')
    columns = model.by_type('IfcColumn')
    proxies = model.by_type('IfcBuildingElementProxy')
    assert (len(beams) + len(columns) + len(proxies)) > 0
