"""
Catalog of Section Profiles - AISC, Eurocode sections with standard properties.
Includes I-beams, hollow sections, and other common structural profiles.
"""

# ============================================================================
# SECTION CATALOG - AISC Standard Sections
# ============================================================================

SECTION_CATALOG = [
    {"name": "W8x10", "area": 0.013, "Ixx": 8e-5, "weight_kg_per_m": 12.0, "price_per_kg": 1.2},
    {"name": "W8x13", "area": 0.015, "Ixx": 1.0e-4, "weight_kg_per_m": 14.5, "price_per_kg": 1.2},
    {"name": "W10x12", "area": 0.020, "Ixx": 2.0e-4, "weight_kg_per_m": 17.0, "price_per_kg": 1.15},
    {"name": "W10x15", "area": 0.023, "Ixx": 2.5e-4, "weight_kg_per_m": 19.5, "price_per_kg": 1.15},
    {"name": "W12x14", "area": 0.026, "Ixx": 3.5e-4, "weight_kg_per_m": 22.0, "price_per_kg": 1.15},
    {"name": "W12x19", "area": 0.033, "Ixx": 4.8e-4, "weight_kg_per_m": 28.5, "price_per_kg": 1.12},
    {"name": "W14x22", "area": 0.040, "Ixx": 6.2e-4, "weight_kg_per_m": 33.0, "price_per_kg": 1.12},
    {"name": "W14x30", "area": 0.054, "Ixx": 8.5e-4, "weight_kg_per_m": 44.5, "price_per_kg": 1.10},
    {"name": "W16x31", "area": 0.058, "Ixx": 1.1e-3, "weight_kg_per_m": 46.5, "price_per_kg": 1.10},
    {"name": "W16x40", "area": 0.074, "Ixx": 1.4e-3, "weight_kg_per_m": 59.5, "price_per_kg": 1.08},
    {"name": "W18x35", "area": 0.065, "Ixx": 1.3e-3, "weight_kg_per_m": 52.0, "price_per_kg": 1.10},
    {"name": "W18x46", "area": 0.085, "Ixx": 1.7e-3, "weight_kg_per_m": 68.5, "price_per_kg": 1.08},
    {"name": "W20x49", "area": 0.091, "Ixx": 2.2e-3, "weight_kg_per_m": 72.5, "price_per_kg": 1.08},
    {"name": "W24x55", "area": 0.103, "Ixx": 2.7e-3, "weight_kg_per_m": 82.0, "price_per_kg": 1.06},
    {"name": "W27x84", "area": 0.155, "Ixx": 4.3e-3, "weight_kg_per_m": 125.0, "price_per_kg": 1.04},
    {"name": "HSS100x100x6", "area": 0.018, "Ixx": 1.6e-4, "weight_kg_per_m": 15.5, "price_per_kg": 1.25},
    {"name": "HSS125x125x6", "area": 0.028, "Ixx": 3.2e-4, "weight_kg_per_m": 24.0, "price_per_kg": 1.23},
    {"name": "HSS150x150x8", "area": 0.044, "Ixx": 5.8e-4, "weight_kg_per_m": 37.5, "price_per_kg": 1.20},
    {"name": "HSS200x200x8", "area": 0.062, "Ixx": 1.2e-3, "weight_kg_per_m": 52.5, "price_per_kg": 1.18},
]

# ============================================================================
# SECTION GEOMETRY (for IFC/CAD export)
# ============================================================================

SECTION_GEOM = {
    'W8x10': {'type': 'I', 'width': 0.203, 'depth': 0.203, 'web_thk': 0.005, 'flange_thk': 0.006},
    'W8x13': {'type': 'I', 'width': 0.203, 'depth': 0.206, 'web_thk': 0.005, 'flange_thk': 0.007},
    'W10x12': {'type': 'I', 'width': 0.254, 'depth': 0.254, 'web_thk': 0.006, 'flange_thk': 0.007},
    'W10x15': {'type': 'I', 'width': 0.254, 'depth': 0.257, 'web_thk': 0.006, 'flange_thk': 0.008},
    'W12x14': {'type': 'I', 'width': 0.305, 'depth': 0.305, 'web_thk': 0.006, 'flange_thk': 0.007},
    'W12x19': {'type': 'I', 'width': 0.305, 'depth': 0.318, 'web_thk': 0.007, 'flange_thk': 0.009},
    'W14x22': {'type': 'I', 'width': 0.356, 'depth': 0.356, 'web_thk': 0.007, 'flange_thk': 0.008},
    'W14x30': {'type': 'I', 'width': 0.356, 'depth': 0.368, 'web_thk': 0.008, 'flange_thk': 0.010},
    'W16x31': {'type': 'I', 'width': 0.382, 'depth': 0.406, 'web_thk': 0.008, 'flange_thk': 0.009},
    'W16x40': {'type': 'I', 'width': 0.382, 'depth': 0.414, 'web_thk': 0.009, 'flange_thk': 0.011},
    'W18x35': {'type': 'I', 'width': 0.406, 'depth': 0.432, 'web_thk': 0.008, 'flange_thk': 0.009},
    'W18x46': {'type': 'I', 'width': 0.406, 'depth': 0.445, 'web_thk': 0.009, 'flange_thk': 0.011},
    'W20x49': {'type': 'I', 'width': 0.420, 'depth': 0.505, 'web_thk': 0.010, 'flange_thk': 0.010},
    'W24x55': {'type': 'I', 'width': 0.505, 'depth': 0.594, 'web_thk': 0.011, 'flange_thk': 0.010},
    'W27x84': {'type': 'I', 'width': 0.535, 'depth': 0.686, 'web_thk': 0.014, 'flange_thk': 0.015},
    'HSS100x100x6': {'type': 'HollowRect', 'outer_w': 0.100, 'outer_h': 0.100, 'thickness': 0.006},
    'HSS125x125x6': {'type': 'HollowRect', 'outer_w': 0.125, 'outer_h': 0.125, 'thickness': 0.006},
    'HSS150x150x8': {'type': 'HollowRect', 'outer_w': 0.150, 'outer_h': 0.150, 'thickness': 0.008},
    'HSS200x200x8': {'type': 'HollowRect', 'outer_w': 0.200, 'outer_h': 0.200, 'thickness': 0.008},
    'REC200x50': {'type': 'Rect', 'width': 0.200, 'depth': 0.050, 'thickness': 0.005},
}

# ============================================================================
# EUROCODE SECTIONS (S355, IPE, HE profiles)
# ============================================================================

EUROCODE_CATALOG = [
    {"name": "IPE100", "area": 0.010, "Ixx": 1.7e-5, "weight_kg_per_m": 8.1, "fy_mpa": 355},
    {"name": "IPE120", "area": 0.013, "Ixx": 3.2e-5, "weight_kg_per_m": 10.4, "fy_mpa": 355},
    {"name": "IPE140", "area": 0.016, "Ixx": 5.4e-5, "weight_kg_per_m": 12.9, "fy_mpa": 355},
    {"name": "IPE160", "area": 0.020, "Ixx": 8.7e-5, "weight_kg_per_m": 15.8, "fy_mpa": 355},
    {"name": "IPE180", "area": 0.024, "Ixx": 1.3e-4, "weight_kg_per_m": 18.8, "fy_mpa": 355},
    {"name": "IPE200", "area": 0.029, "Ixx": 1.9e-4, "weight_kg_per_m": 22.4, "fy_mpa": 355},
    {"name": "HE100A", "area": 0.021, "Ixx": 3.9e-5, "weight_kg_per_m": 16.7, "fy_mpa": 355},
    {"name": "HE100B", "area": 0.026, "Ixx": 4.5e-5, "weight_kg_per_m": 20.4, "fy_mpa": 355},
    {"name": "HE140A", "area": 0.031, "Ixx": 8.6e-5, "weight_kg_per_m": 24.7, "fy_mpa": 355},
    {"name": "HE140B", "area": 0.043, "Ixx": 1.1e-4, "weight_kg_per_m": 33.7, "fy_mpa": 355},
]

def get_section_by_name(name):
    """Retrieve section from catalog by name"""
    for section in SECTION_CATALOG + EUROCODE_CATALOG:
        if section.get('name') == name:
            return section
    return None

def get_section_geometry(name):
    """Get detailed geometry for IFC/CAD export"""
    return SECTION_GEOM.get(name, {})

def find_lightest_section(min_ixx, max_weight_per_m=1000):
    """Find lightest section meeting minimum inertia requirement"""
    candidates = [s for s in SECTION_CATALOG if s['Ixx'] >= min_ixx and s['weight_kg_per_m'] <= max_weight_per_m]
    if candidates:
        candidates.sort(key=lambda x: x['weight_kg_per_m'])
        return candidates[0]
    return None

def find_strongest_section(span_m, min_deflection_ratio=240):
    """Find section adequate for given span and deflection limit"""
    # Deflection ratio = L / (5*I/W)  where W is section modulus
    # Rearranging: I needed = L * 5 * W / (deflection_ratio * weight_per_m)
    min_ixx_needed = (span_m / min_deflection_ratio) * 1e-3  # Rough estimate
    return find_lightest_section(min_ixx_needed)
