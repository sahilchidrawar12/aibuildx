"""
Materials Database - comprehensive steel material grades and specifications.
Includes ASTM, Eurocode, and proprietary steel grades with mechanical and environmental properties.
"""

# ============================================================================
# MATERIAL DATABASE: Steel Grades and Properties
# ============================================================================

MATERIAL_DATABASE = {
    'A36': {
        'Fy': 250, 'Fu': 400, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'general', 'cost_premium': 1.0, 'availability': 'excellent',
        'fracture_toughness_cvn': 20, 'weldability': 'excellent', 'formability': 'excellent'
    },
    'A572_Gr50': {
        'Fy': 345, 'Fu': 450, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'high_strength', 'cost_premium': 1.15, 'availability': 'good',
        'fracture_toughness_cvn': 25, 'weldability': 'good', 'formability': 'good'
    },
    'A572_Gr65': {
        'Fy': 450, 'Fu': 550, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'very_high_strength', 'cost_premium': 1.35, 'availability': 'moderate',
        'fracture_toughness_cvn': 20, 'weldability': 'fair', 'formability': 'fair'
    },
    'A992': {
        'Fy': 345, 'Fu': 450, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'general_high_strength', 'cost_premium': 1.12, 'availability': 'excellent',
        'fracture_toughness_cvn': 27, 'weldability': 'excellent', 'formability': 'good'
    },
    'A500_Gr_B_Round': {
        'Fy': 317, 'Fu': 413, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'hss', 'cost_premium': 1.25, 'availability': 'good',
        'fracture_toughness_cvn': 22, 'weldability': 'good', 'formability': 'good'
    },
    'A588': {
        'Fy': 345, 'Fu': 485, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'weathering_steel', 'cost_premium': 1.4, 'availability': 'moderate',
        'fracture_toughness_cvn': 25, 'weldability': 'fair', 'formability': 'good'
    },
    'A913': {
        'Fy': 450, 'Fu': 620, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'high_strength_railroad', 'cost_premium': 1.5, 'availability': 'limited',
        'fracture_toughness_cvn': 27, 'weldability': 'fair', 'formability': 'fair'
    },
    'A514': {
        'Fy': 690, 'Fu': 760, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850,
        'use': 'quenched_tempered', 'cost_premium': 1.8, 'availability': 'limited',
        'fracture_toughness_cvn': 30, 'weldability': 'poor', 'formability': 'poor'
    },
    'S355': {
        'Fy': 355, 'Fu': 510, 'E': 210000, 'G': 81000, 'density_kg_m3': 7850,
        'use': 'european', 'cost_premium': 1.2, 'availability': 'good',
        'fracture_toughness_cvn': 27, 'weldability': 'good', 'formability': 'good'
    },
}

# ============================================================================
# BOLT SPECIFICATIONS (ISO/ASTM)
# ============================================================================

BOLT_SPECIFICATIONS = {
    'M12': {'dia_mm': 12, 'tensile_area_mm2': 84.3, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M16': {'dia_mm': 16, 'tensile_area_mm2': 156.7, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M20': {'dia_mm': 20, 'tensile_area_mm2': 244.8, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M24': {'dia_mm': 24, 'tensile_area_mm2': 352.5, 'grades': ['5.8', '8.8', '10.9']},
    'M32': {'dia_mm': 32, 'tensile_area_mm2': 561, 'grades': ['5.8', '8.8', '10.9']},
    'M39': {'dia_mm': 39, 'tensile_area_mm2': 817, 'grades': ['8.8', '10.9']},
}

# ============================================================================
# BOLT STRENGTH GRADES (ISO 898-1)
# ============================================================================

BOLT_STRENGTH = {
    '4.6': {'ultimate_mpa': 400, 'yield_mpa': 240, 'preload_factor': 0.7},
    '5.8': {'ultimate_mpa': 500, 'yield_mpa': 400, 'preload_factor': 0.7},
    '8.8': {'ultimate_mpa': 800, 'yield_mpa': 640, 'preload_factor': 0.7},
    '10.9': {'ultimate_mpa': 1000, 'yield_mpa': 900, 'preload_factor': 0.7},
}

# ============================================================================
# FASTENER AND ANCHOR SPECIFICATIONS
# ============================================================================

ANCHOR_BOLT_SPECS = {
    'A307': {'grade': 'A307', 'fu_mpa': 414, 'fy_mpa': 207, 'use': 'general', 'cost': 1.0},
    'A325': {'grade': 'A325', 'fu_mpa': 825, 'fy_mpa': 660, 'use': 'structural', 'cost': 1.2},
    'A490': {'grade': 'A490', 'fu_mpa': 1035, 'fy_mpa': 825, 'use': 'high_strength', 'cost': 1.5},
}

WELD_ELECTRODE_SPECS = {
    'E6010': {'tensile_mpa': 415, 'yield_mpa': 345, 'impact_temp': 0, 'process': 'SMAW', 'cost': 1.0},
    'E6012': {'tensile_mpa': 415, 'yield_mpa': 345, 'impact_temp': -20, 'process': 'SMAW', 'cost': 0.9},
    'E7010': {'tensile_mpa': 480, 'yield_mpa': 415, 'impact_temp': -45, 'process': 'SMAW', 'cost': 1.1},
    'E70S-2': {'tensile_mpa': 485, 'yield_mpa': 415, 'impact_temp': -30, 'process': 'GMAW', 'cost': 0.95},
    'E70S-6': {'tensile_mpa': 490, 'yield_mpa': 420, 'impact_temp': -20, 'process': 'GMAW', 'cost': 1.0},
    'E8010-G': {'tensile_mpa': 550, 'yield_mpa': 480, 'impact_temp': -45, 'process': 'GMAW', 'cost': 1.2},
}
