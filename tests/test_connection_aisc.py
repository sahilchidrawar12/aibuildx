import math
from src.pipeline import connection_capacity as cc


def test_bolt_nominal_and_design():
    d = 20.0
    fu = 400.0
    Vn = cc.bolt_nominal_shear(d, fu)
    Vd = cc.bolt_design_shear(d, fu)
    assert Vn > 0
    assert Vd == cc.bolt_design_shear(d, fu)
    assert Vd < Vn * 1.0  # design less than nominal when phi < 1


def test_bolt_group_design_check_simple():
    bolts = {'count': 4, 'diameter_mm': 20.0}
    # small demand
    res = cc.bolt_group_design_check(bolts, demand_shear=10000.0, demand_tension=5000.0, fu=400.0)
    assert 'ok' in res
    assert isinstance(res['ok'], bool)


def test_block_shear_from_pattern():
    res = cc.block_shear_from_bolt_pattern(bolts_count=6, bolt_dia_mm=20.0, edge_dist_mm=60.0, t_plate_mm=10.0, fu=350.0)
    assert res['phiRn'] > 0


def test_end_plate_moment_connection():
    # M = 100 kN*m = 100e3 N*m = 100e6 N*mm
    M = 100e6
    bolts = {'count': 8, 'diameter_mm': 22.0}
    res = cc.end_plate_moment_connection(M, lever_arm_mm=200.0, boltspec=bolts, fu=350.0)
    assert 'required_tension_per_group_N' in res
    assert res['required_tension_per_group_N'] > 0
