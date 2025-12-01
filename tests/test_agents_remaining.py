import os
import json
import uuid
from src.pipeline.agents import miner_agent, connection_designer, engineer_agent
from src.pipeline import pipeline_compat as compat


def test_miner_agent_metadata():
    payload = {'model': {'id': 'm1', 'type': 'frame', 'members': [{}, {}, {}]}}
    res = miner_agent.process(payload)
    assert res['status'] == 'ok'
    assert res['metadata']['id'] == 'm1'
    assert res['metadata']['num_members'] == 3


def test_connection_designer_rules():
    res = connection_designer.process({'shear': 60, 'tension': 10})
    assert res['status'] == 'ok'
    assert 'bearing' in res['suggested_connection'] or 'bolted' in res['suggested_connection']


def test_run_pipeline_writes_outputs(tmp_path):
    # prepare minimal member list
    members = [
        {'id': str(uuid.uuid4()), 'start': [0, 0, 0], 'end': [6, 0, 0], 'length': 6.0, 'layer': 'BEAMS'},
    ]
    out_dir = str(tmp_path / 'smoke_out')
    res = compat.run_pipeline({'members': members}, out_dir=out_dir)
    # compat.run_pipeline should return a dict result
    assert isinstance(res, dict)
    # output files should be present
    assert os.path.exists(os.path.join(out_dir, 'result.json'))
    # reporter.json or final.json may be present depending on pipeline
    assert any(os.path.exists(os.path.join(out_dir, n)) for n in ['final.json', 'reporter.json', 'cnc.json'])
