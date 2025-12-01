import os
import uuid
from src.pipeline.agents import stability_agent, validator_agent, cnc_exporter_agent


def test_stability_agent_computes_slenderness_and_factor():
    member = {'id': str(uuid.uuid4()), 'length': 4000.0, 'r_g': 20.0}
    res = stability_agent.process({'member': member})
    assert res['status'] == 'ok'
    assert 'slenderness' in res
    assert res['slenderness'] == 4000.0 / 20.0
    assert res['stability_factor'] in (1.0, 1.5, 2.0)


def test_validator_detects_bending_capacity_exceedance():
    mid = str(uuid.uuid4())
    members = [
        {'id': mid, 'length': 6.0, 'loads': {'moment_kNm': 30.0}, 'selection': {'bending_capacity_Nm': 20000.0}},
    ]
    res = validator_agent.process({'data': {'members': members}})
    # 30 kNm = 30000 Nm, capacity 20000 -> error
    assert res['status'] == 'error'
    assert any(e.get('err') == 'bending_capacity_exceeded' for e in res['errors'])


def test_cnc_exporter_writes_files(tmp_path):
    members = [{'id': str(uuid.uuid4()), 'length': 6.0, 'selection': {'section_name': 'W8x10'}}]
    out_dir = str(tmp_path / 'cnc')
    res = cnc_exporter_agent.process({'members': members, 'out_dir': out_dir})
    assert res['status'] == 'ok'
    assert len(res['exported_files']) == 1
    assert os.path.exists(res['exported_files'][0])
