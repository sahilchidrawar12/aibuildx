import uuid
import pytest
from src.pipeline import pipeline_v2 as pv2
from src.pipeline.agents import engineer_agent, optimizer_agent, fabrication_agent


@pytest.fixture
def sample_members():
    return [
        {'id': str(uuid.uuid4()), 'start': [0.0, 0.0, 0.0], 'end': [6.0, 0.0, 0.0], 'length': 6.0, 'layer': 'BEAMS'},
        {'id': str(uuid.uuid4()), 'start': [6.0, 0.0, 0.0], 'end': [6.0, 0.0, 4.0], 'length': 4.0, 'layer': 'COLUMNS'},
    ]


def test_engineer_agent_standardizes(sample_members):
    res = engineer_agent.process({'members': sample_members})
    assert res['status'] == 'ok'
    assert 'members' in res
    assert all('orientation' in m for m in res['members'])


def test_optimizer_agent_chain(sample_members):
    res = optimizer_agent.process({'members': sample_members})
    assert res['status'] == 'ok'
    assert 'result' in res or 'best' in res


def test_fabrication_agent_model_flow(sample_members):
    # Prepare a minimal pipeline flow to produce connections
    miner = pv2.miner_from_dxf(sample_members)
    eng = pv2.engineer_standardize(miner)
    loads = pv2.load_path_resolver(eng)
    stab = pv2.stability_agent(loads)
    opt = pv2.optimizer_agent(stab)
    conn = pv2.connection_designer(opt)
    fab = fabrication_agent.process({'members': conn['members']})
    assert fab['status'] == 'ok'
    assert 'fabrication' in fab or 'fabrication_steps' in fab
