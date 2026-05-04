"""Simple code compliance checks (AISC-like simplified checks).
This is not a replacement for code-based design; it's a mechanical approximation for pipeline.
"""
from typing import Dict, Any

def axial_capacity(A: float, fy: float, phi: float=0.9) -> float:
    # A in mm^2, fy in MPa -> N
    return phi * A * fy

def bending_capacity(Zx: float, fy: float, phi: float=0.9) -> float:
    # Zx in mm^3, fy in MPa -> N*mm
    return phi * Zx * fy

def check_member_basic(member: Dict[str,Any], material: Dict[str,Any]) -> Dict[str,Any]:
    A = member.get('area') or member.get('geom',{}).get('area')
    Zx = member.get('Zx') or member.get('geom',{}).get('Zx')
    fy = material.get('fy')
    if not A or not fy:
        return {"ok": False, "reason": "missing A or fy"}
    Nx = member.get('axial_force', 0.0)
    Mx = member.get('moment', 0.0)
    Pn = axial_capacity(A, fy)
    Mn = bending_capacity(Zx or 0.0, fy)
    return {"axial_ok": abs(Nx) <= Pn, "moment_ok": abs(Mx) <= Mn, "Pn": Pn, "Mn": Mn}


def lateral_torsional_buckling_capacity(Mp: float, Mn: float, Lb: float, E: float=210000.0) -> Dict[str, Any]:
    """Crude LTB check returning available moment capacity and a pass flag.
    Mp: plastic moment capacity estimate, Mn: nominal moment, Lb: unbraced length (mm)
    """
    # This is a placeholder heuristic: reduce Mn based on Lb
    if Lb <= 0:
        return {'Mn_eff': Mn, 'ok': True}
    # reduce capacity as Lb increases; arbitrary shape for pipeline use
    reduction = 1.0 / (1.0 + (Lb/3000.0))
    Mn_eff = Mn * reduction
    return {'Mn_eff': Mn_eff, 'ok': Mn_eff >= Mp}


def euler_effective_length(K: float, L: float, r: float) -> float:
    """Return KL/r value (dimensionless)"""
    if r <= 0:
        return float('inf')
    return (K * L) / r
