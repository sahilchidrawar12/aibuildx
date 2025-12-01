import json
import os
from src.pipeline.pipeline_v2 import Pipeline


def test_pipeline_runs_on_sample():
    sample_path = os.path.join('examples', 'sample_input.json')
    with open(sample_path, 'r') as f:
        entities = json.load(f)
    p = Pipeline()
    out = p.run_from_dxf_entities(entities, out_dir='outputs')
    # basic assertions
    assert 'final' in out
    assert isinstance(out['miner']['members'], list)
    assert len(out['miner']['members']) >= 1
    # no exceptions and final contains members
    assert 'members' in out['final']
