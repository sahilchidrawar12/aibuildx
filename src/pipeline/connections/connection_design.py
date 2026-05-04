"""Connection design rules: plate sizing, bolt layouts, weld strength approximations."""
from typing import Dict,Any
import math

def plate_width_from_flange(flange_width: float, cover: float = 40.0) -> float:
    return flange_width + 2*cover

def plate_thickness_from_moment(M: float, width: float, fy: float, gamma: float=0.9) -> float:
    # Simple flexural stress t = 6*M/(b*fy*gamma) approximate (units: M in N*mm, b in mm, fy in MPa)
    if width<=0 or fy<=0:
        return 10.0
    t = abs(6.0*M) / (width * fy * gamma)
    # practical discrete thicknesses using common plate sizes
    t = max(6.0, t)
    # round up to nearest 2 mm
    t_rounded = float(int((t + 1.9999)//2 * 2))
    return t_rounded

def min_edge_distance(thickness_mm: float) -> float:
    return 8.0 * thickness_mm

def min_bolt_spacing(diameter_mm: float) -> float:
    return max(3.0*diameter_mm, 25.0)


def bolt_group_eccentricity_effects(bolts_count: int, spacing_mm: float, ecc_mm: float) -> Dict[str, float]:
    """Estimate basic eccentricity effects on bolt group (very approximate).
    Returns increase factor for moment capacity.
    """
    if bolts_count <= 0:
        return {'factor': 0.0}
    # simple lever effect: moment = N*ecc
    lever = ecc_mm
    # assume group capacity proportional to bolts_count*spacing
    base = bolts_count * spacing_mm
    factor = 1.0 + (lever / max(1.0, base))
    return {'factor': factor, 'lever_mm': lever, 'base': base}


def block_shear_check(t_plate: float, a_nt: float, a_nv: float, fu: float, phi: float=0.75) -> Dict[str, float]:
    """Rudimentary block shear: compares shear and tensile rupture paths.
    a_nt, a_nv are net areas in tension and shear respectively (mm^2).
    Returns capacities and a boolean ok flag.
    """
    Rn_tension = a_nt * fu
    Rn_shear = 0.6 * a_nv * fu
    phiRn = phi * (Rn_tension + Rn_shear)
    return {'Rn_tension': Rn_tension, 'Rn_shear': Rn_shear, 'phiRn': phiRn}

def whitmore_width(gusset_angle_deg: float, plate_width: float) -> float:
    # simplified Whitmore width approximate
    theta = math.radians(gusset_angle_deg)
    return plate_width / math.cos(theta) if math.cos(theta)!=0 else plate_width

def weld_throat_required(Fexx: float, demand: float, fy: float) -> float:
    # throat area = demand/(0.6*fy)
    if fy<=0:
        return 1.0
    area = abs(demand)/(0.6*fy)
    # convert to equivalent throat length assuming unit throat
    return max(1.0, area)


def weld_strength(throat_mm: float, length_mm: float, fw: float) -> float:
    """Return approximate weld strength (force) using throat area * fw (weld material strength).
    throat_mm: throat thickness in mm, length_mm: weld length in mm, fw: weld strength (MPa)
    returns N
    """
    area = throat_mm * length_mm
    return area * fw


def weld_length_required(demand: float, throat_mm: float, fw: float) -> float:
    """Estimate required weld length for a given demand (N)."""
    if throat_mm <= 0 or fw <= 0:
        return 0.0
    length = abs(demand) / (throat_mm * fw)
    return max(0.0, length)


def combined_weld_group_capacity(welds: list, fw: float) -> Dict[str, float]:
    """Given a list of weld segments [{'throat':t,'length':L},...], compute combined capacity."""
    total = 0.0
    for w in welds:
        total += weld_strength(w.get('throat',6.0), w.get('length',100.0), fw)
    return {'capacity_N': total}


def end_plate_moment_connection(M: float, flange_width: float, fy: float, bolt_dia: float, bolt_grade: str='A325') -> Dict[str, Any]:
    """Simple end-plate sizing heuristic: determine plate thickness and bolt rows for moment M (N*mm).
    Returns suggested thickness (mm), plate width (mm), bolt layout dict.
    """
    # plate width from flange
    width = plate_width_from_flange(flange_width, cover=40.0)
    # plate thickness from moment
    t = plate_thickness_from_moment(M, width, fy)
    # suggest bolt pattern: 2 rows for small moments, 3 rows for larger
    rows = 2 if abs(M) < 1e6 else 3
    # bolts per row depending on flange width
    per_row = max(2, int(width // 150))
    bolts = {'rows': rows, 'per_row': per_row, 'diameter_mm': bolt_dia, 'grade': bolt_grade}
    return {'thickness_mm': t, 'width_mm': width, 'bolts': bolts}


def gusset_plate_rules(brace_angle_deg: float, brace_section_depth: float, plate_thickness_hint: float=None) -> Dict[str, Any]:
    """Return a suggested gusset plate geometry based on brace angle and depth."""
    w = whitmore_width(brace_angle_deg, plate_width=brace_section_depth)
    t = plate_thickness_hint if plate_thickness_hint else max(6.0, brace_section_depth/50.0)
    return {'width_mm': w, 'thickness_mm': t}
