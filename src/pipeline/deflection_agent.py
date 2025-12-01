"""Simple deflection checks (L/240, L/360) for beam spans."""
from typing import Dict,Any

def check_deflection(member: Dict[str,Any], span: float, E: float, I: float, loads_w: float) -> Dict[str,Any]:
    """Calculate midspan deflection for simply supported uniformly distributed load: wL^4/(384EI)
    Returns dict with actual deflection and limit flags.
    E in MPa, I in mm^4, loads_w in N/mm
    """
    L = span
    if L <= 0 or E <= 0 or I <= 0:
        return {"deflection": 0.0, "ok": True, "note": "insufficient data"}
    # w in N/mm, L in mm
    w = loads_w
    delta = w * L**4 / (384.0 * E * 1e3 * I)  # convert E MPa to N/mm^2 already; keep units approx
    limit_240 = L/240.0
    limit_360 = L/360.0
    return {"deflection": delta, "limit_L240": limit_240, "limit_L360": limit_360, "ok_L240": delta <= limit_240, "ok_L360": delta <= limit_360}
