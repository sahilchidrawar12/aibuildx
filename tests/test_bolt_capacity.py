from src.pipeline.connection_capacity import aisc_bolt_shear_design, aisc_bolt_tension_design, interaction_tension_shear

def test_aisc_bolt_shear_and_tension():
    v = aisc_bolt_shear_design(20.0, 'A325')
    t = aisc_bolt_tension_design(20.0, 'A325')
    assert v > 0
    assert t > 0

def test_interaction_ok():
    bolts = {'count':4,'diameter_mm':20,'grade':'A325'}
    res = interaction_tension_shear(50000.0, 20000.0, bolts)
    assert 'ok' in res
