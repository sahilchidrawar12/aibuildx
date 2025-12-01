from src.pipeline.connection_design import weld_throat_required, weld_length_required, end_plate_moment_connection, combined_weld_group_capacity

def test_weld_throat_and_length():
    throat = weld_throat_required(400.0, 10000.0, 355.0)
    assert throat >= 1.0
    length = weld_length_required(10000.0, throat, 355.0)
    assert length > 0

def test_end_plate_heuristic():
    res = end_plate_moment_connection(2e6, flange_width=300.0, fy=355.0, bolt_dia=20.0)
    assert res['thickness_mm'] >= 6.0
    assert 'bolts' in res

def test_combined_weld_capacity():
    welds = [{'throat':6.0,'length':100.0},{'throat':6.0,'length':80.0}]
    cap = combined_weld_group_capacity(welds, fw=355.0)
    assert cap['capacity_N'] > 0
