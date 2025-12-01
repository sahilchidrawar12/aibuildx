"""Connection capacity approximations for bolts, bearing, and tear-out checks."""
from typing import Dict, Any
import math

def bolt_shear_capacity(diameter_mm: float, grade_fu: float, gamma: float = 0.9) -> float:
    # Very simplified: shear capacity ~ 0.6*As*fu*gamma
    # diameter in mm -> As in mm^2
    As = math.pi*(diameter_mm/2.0)**2
    return 0.6 * As * grade_fu * gamma

def bolt_tension_capacity(diameter_mm: float, grade_fu: float, gamma: float = 0.75) -> float:
    As = math.pi*(diameter_mm/2.0)**2
    return As * grade_fu * gamma


def aisc_bolt_shear_design(diameter_mm: float, grade: str = 'A325') -> float:
    """Approximate nominal shear capacity per AISC-like rules (simplified).
    This is an approximation for pipeline use; diameter in mm.
    Returns N (Newton) capacity.
    """
    # map grade to nominal fu (MPa)
    grade_map = {'A325': 400.0, 'A490': 500.0}
    fu = grade_map.get(grade, 400.0)
    return bolt_shear_capacity(diameter_mm, fu, gamma=0.75)


def aisc_bolt_tension_design(diameter_mm: float, grade: str = 'A325') -> float:
    grade_map = {'A325': 400.0, 'A490': 500.0}
    fu = grade_map.get(grade, 400.0)
    return bolt_tension_capacity(diameter_mm, fu, gamma=0.6)


def bolt_nominal_shear(diameter_mm: float, fu: float) -> float:
    """Nominal shear per bolt (approx). Vn = 0.6*Fu*As (As=area of bolt shank)
    diameter_mm in mm, fu in MPa; returns N
    """
    As = math.pi * (diameter_mm / 2.0) ** 2
    Vn = 0.6 * fu * As
    return Vn


def bolt_design_shear(diameter_mm: float, fu: float, phi: float = 0.75) -> float:
    """Design shear capacity = phi * Vn"""
    return phi * bolt_nominal_shear(diameter_mm, fu)


def bolt_nominal_tension(diameter_mm: float, fu: float) -> float:
    """Nominal tension per bolt (approx). Pn = As*Fu"""
    As = math.pi * (diameter_mm / 2.0) ** 2
    return As * fu


def bolt_design_tension(diameter_mm: float, fu: float, phi: float = 0.75) -> float:
    return phi * bolt_nominal_tension(diameter_mm, fu)


def bolt_group_design_check(boltspec: Dict[str, Any], demand_shear: float, demand_tension: float, fu: float) -> Dict[str, Any]:
    """Check bolt group per simple LRFD interaction: V/Vn + N/Pn <= 1.0
    boltspec: {'count': int, 'diameter_mm': float}
    fu: material tensile strength (MPa)
    Returns capacities and pass/fail.
    """
    cnt = int(boltspec.get('count', 1))
    d = float(boltspec.get('diameter_mm', 20.0))
    phi_s = 0.75
    phi_t = 0.75
    Vn_single = bolt_nominal_shear(d, fu)
    Pn_single = bolt_nominal_tension(d, fu)
    Vn = Vn_single * cnt
    Pn = Pn_single * cnt
    Vd = abs(float(demand_shear))
    Nd = abs(float(demand_tension))
    # interaction ratio using design (phi*Rn)
    ratio = (Vd / (phi_s * Vn)) + (Nd / (phi_t * Pn))
    ok = ratio <= 1.0
    return {
        'Vn': Vn, 'Pn': Pn, 'Vn_design': phi_s * Vn, 'Pn_design': phi_t * Pn,
        'interaction_ratio': ratio, 'ok': ok
    }


def end_plate_moment_connection(M_nm: float, lever_arm_mm: float, boltspec: Dict[str, Any], fu: float) -> Dict[str, Any]:
    """Very simplified end-plate design: compute required tensile force = M / e
    and check against bolt group capacity. M in N*mm, lever_arm_mm is distance from bolt group centroid to compression face.
    """
    if lever_arm_mm <= 0:
        lever_arm_mm = 50.0
    required_tension = abs(M_nm) / lever_arm_mm
    check = bolt_group_design_check(boltspec, demand_shear=0.0, demand_tension=required_tension, fu=fu)
    check.update({'required_tension_per_group_N': required_tension})
    return check


def interaction_tension_shear(Vd: float, Nd: float, boltspec: Dict[str, Any]) -> Dict[str, Any]:
    """Simple interaction check using linear interaction: V/Vn + N/Pn <= 1.0"""
    cnt = boltspec.get('count', 1)
    dia = boltspec.get('diameter_mm', 20.0)
    grade = boltspec.get('grade', 'A325')
    Vn = aisc_bolt_shear_design(dia, grade) * cnt
    Pn = aisc_bolt_tension_design(dia, grade) * cnt
    ok = (abs(Vd)/Vn + abs(Nd)/Pn) <= 1.0
    return {'Vn': Vn, 'Pn': Pn, 'interaction_ratio': (abs(Vd)/Vn + abs(Nd)/Pn), 'ok': ok}


def bearing_capacity_aisc(plate_thickness_mm: float, bolt_diameter_mm: float, fu: float, kb: float=2.4) -> float:
    """Approximate AISC bearing capacity: kb * t * d * fu (k_b simplified).
    Returns N per bolt.
    """
    return kb * plate_thickness_mm * bolt_diameter_mm * fu


def tearout_capacity(net_edge_dist_mm: float, bolt_dia_mm: float, fu: float, t_plate: float) -> float:
    """Simple tear-out estimate using edge distance and plate thickness.
    Returns N capacity approximation.
    """
    # Use a simple formula proportional to (edge_dist - 1.5*diameter) * t * fu
    eff = max(0.0, net_edge_dist_mm - 1.5*bolt_dia_mm)
    return eff * t_plate * fu * 0.5


def bearing_and_tearout_check(boltspec: Dict[str, Any], plate: Dict[str, Any], fu: float) -> Dict[str, Any]:
    d = boltspec.get('diameter_mm', 20.0)
    t = plate.get('thickness', plate.get('thickness_mm', 10.0))
    edge = plate.get('edge_distance', 8.0 * t)
    kb = 2.4
    bearing_per_bolt = bearing_capacity_aisc(t, d, fu, kb)
    tear_per_bolt = tearout_capacity(edge, d, fu, t)
    return {'bearing_per_bolt': bearing_per_bolt, 'tear_per_bolt': tear_per_bolt}


def block_shear_capacity(Anv: float, Ant: float, fu: float, phi: float = 0.75) -> Dict[str, Any]:
    """Compute AISC-like block shear limit state.
    Rn = 0.6*Fu*Anv + Fu*Ant ; design = phi * Rn
    Anv: net shear area (mm^2)
    Ant: net tension area (mm^2)
    fu: tensile strength (MPa)
    """
    Rn = 0.6 * fu * Anv + fu * Ant
    phiRn = phi * Rn
    return {'Rn': Rn, 'phiRn': phiRn}


def block_shear_from_bolt_pattern(bolts_count: int, bolt_dia_mm: float, edge_dist_mm: float, t_plate_mm: float, fu: float, phi: float=0.75) -> Dict[str, Any]:
    """Estimate block shear from bolt pattern by approximating net areas.
    This helper is approximate: Anv ~= t * (spacing*(rows-1)) and Ant ~= t*(edge_dist - hole_diameter)
    bolts_count: total bolts in group
    """
    if bolts_count <= 0:
        return {'Rn': 0.0, 'phiRn': 0.0}
    # assume 2 rows by n columns roughly
    rows = 2 if bolts_count < 6 else 3
    cols = max(1, bolts_count // rows)
    spacing = max(75.0, 1.5 * bolt_dia_mm)
    Anv = t_plate_mm * spacing * max(0, (rows - 1)) * cols
    Ant = t_plate_mm * max(0.0, (edge_dist_mm - 1.1 * bolt_dia_mm)) * cols
    return block_shear_capacity(Anv, Ant, fu, phi)

def bearing_capacity(plate_t: float, bolt_d: float, fu: float, k1: float=2.4) -> float:
    # simplified bearing: kb * t * d * fu
    return k1 * plate_t * bolt_d * fu

def check_bolt_group(bolts: Dict[str,Any], demand_shear: float, demand_tension: float, material_fu: float) -> Dict[str,Any]:
    count = bolts.get('count', 1)
    d = bolts.get('diameter_mm', 20.0)
    vsingle = bolt_shear_capacity(d, material_fu)
    tsingle = bolt_tension_capacity(d, material_fu)
    total_shear = vsingle * count
    total_tension = tsingle * count
    return {"v_capacity": total_shear, "t_capacity": total_tension, "shear_ok": total_shear>=abs(demand_shear), "tension_ok": total_tension>=abs(demand_tension)}
