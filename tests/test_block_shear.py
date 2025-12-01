from src.pipeline.connection_capacity import block_shear_capacity, block_shear_from_bolt_pattern

def test_block_shear_basic():
    res = block_shear_capacity(1000.0, 200.0, 450.0)
    assert 'phiRn' in res and res['phiRn'] > 0

def test_block_shear_pattern():
    res = block_shear_from_bolt_pattern(8, 20.0, 80.0, 10.0, 450.0)
    assert 'phiRn' in res
    assert res['phiRn'] >= 0
