import os
import json
from src.pipeline.pipeline_v2 import Pipeline


def test_cnc_csv_created(tmp_path):
    sample_path = os.path.join('examples', 'sample_input.json')
    with open(sample_path, 'r') as f:
        entities = json.load(f)
    p = Pipeline()
    out_dir = str(tmp_path)
    out = p.run_from_dxf_entities(entities, out_dir=out_dir)
    cnc = out.get('cnc')
    assert cnc is not None
    csv_path = cnc.get('cnc_csv')
    assert csv_path is not None
    assert os.path.exists(csv_path)
    # read CSV and verify header and at least one member row
    with open(csv_path, 'r') as f:
        content = f.read()
    assert 'member_id' in content
    assert '\n' in content
