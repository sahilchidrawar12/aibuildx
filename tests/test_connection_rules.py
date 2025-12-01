from src.pipeline.connection_capacity import bearing_capacity_aisc, tearout_capacity, bearing_and_tearout_check, interaction_tension_shear

def test_bearing_and_tearout():
    b = bearing_capacity_aisc(10.0, 20.0, 450.0)
    t = tearout_capacity(80.0, 20.0, 450.0, 10.0)
    assert b > 0
    assert t >= 0

def test_bearing_and_tearout_check():
    bolts = {'count':4,'diameter_mm':20}
    plate = {'thickness':10.0,'edge_distance':80.0}
    res = bearing_and_tearout_check(bolts, plate, 450.0)
    assert 'bearing_per_bolt' in res
    assert 'tear_per_bolt' in res

def test_interaction_ratio():
    bolts = {'count':4,'diameter_mm':20,'grade':'A325'}
    res = interaction_tension_shear(50000.0, 20000.0, bolts)
    assert 'interaction_ratio' in res
