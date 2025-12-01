"""Weld type catalogs and specifications.

Defines standard weld types, materials, and performance characteristics
for structural steel connections including fillet, butt, plug, and slot welds.

Data:
    WELD_TYPES: Comprehensive weld type catalog
    ELECTRODE_SPECS: Electrode classification and properties
    WELD_QUALITY_STANDARDS: Quality requirements by application
"""

# Weld type definitions
WELD_TYPES = {
    'FILLET': {
        'fillet_general': {
            'description': 'General fillet weld for shear transfer',
            'geometry': 'triangular cross-section',
            'size_range': [3/16, 1/4, 5/16, 3/8, 7/16, 1/2, 9/16, 5/8],
            'typical_applications': ['lap joints', 'T-connections', 'lap connections'],
            'strength_per_size': {  # kips per inch of weld (for E70XX)
                0.1875: 2.8,
                0.25: 3.7,
                0.3125: 4.6,
                0.375: 5.6,
                0.4375: 6.5,
                0.5: 7.4,
            },
            'position': ['flat', 'horizontal', 'vertical', 'overhead'],
            'penetration': 'approximately 70% for groove welds',
        },
        'fillet_load_carrying': {
            'description': 'Load-carrying fillet weld (high strength)',
            'geometry': 'triangular, deeper penetration',
            'size_range': [1/4, 5/16, 3/8, 7/16, 1/2, 9/16, 5/8],
            'typical_applications': ['primary connections', 'moment connections', 'critical'],
            'electrode_types': ['E70XX', 'E80XX', 'E90XX'],
            'inspection': ['visual', 'UT selective', 'MT optional'],
            'prequalification': 'recommended',
        },
        'fillet_intermittent': {
            'description': 'Intermittent fillet weld (discontinuous)',
            'geometry': 'short segments with gaps',
            'length_min_in': 1.5,
            'length_typical_in': 3.0,
            'gap_typical_in': 6.0,
            'typical_applications': ['secondary connections', 'reduced cost'],
            'strength_reduction': 0.85,  # Empirical reduction for fatigue
            'restrictions': 'not allowed in high-stress or seismic',
        },
    },
    'BUTT': {
        'complete_joint_penetration': {
            'description': 'Complete joint penetration (CJP) butt weld',
            'joint_type': 'groove',
            'geometry': 'full thickness fusion',
            'typical_applications': ['moment connections', 'primary stress paths', 'seismic'],
            'groove_angle': 60,  # degrees
            'electrode_types': ['E70XX', 'E80XX', 'E90XX', 'E100XX', 'E120XX'],
            'passes_typical': 3,  # For 1/2" thickness
            'penetration': 'complete through thickness',
            'inspection': ['visual', '100% UT or RT', 'MT/PT optional'],
            'pwht': 'required for thick sections and HY50',
        },
        'partial_joint_penetration': {
            'description': 'Partial joint penetration (PJP) butt weld',
            'joint_type': 'groove',
            'geometry': 'partial thickness fusion',
            'penetration_ratio': [0.5, 0.67, 0.75],  # Fraction of thickness
            'typical_applications': ['secondary connections', 'reduced cost', 'adequate capacity'],
            'electrode_types': ['E60XX', 'E70XX', 'E80XX'],
            'root_opening_in': 0.125,
            'bevel_angle': 45,
            'effective_throat': 'per penetration requirement',
            'inspection': ['visual', 'UT selective'],
        },
        'square_groove': {
            'description': 'Square groove butt weld (minimal prep)',
            'joint_type': 'groove',
            'geometry': 'square edges, minimal bevel',
            'typical_applications': ['thin sections', 'shop work', 'reduced cost'],
            'thickness_range': [3/8, 0.5, 5/8, 0.75],  # Practical limits
            'electrode_types': ['E60XX', 'E70XX'],
            'inspection': ['visual only'],
        },
    },
    'PLUG_SLOT': {
        'plug_weld': {
            'description': 'Plug weld through one member',
            'joint_type': 'hole',
            'hole_diameter': [0.75, 1.0, 1.25, 1.5, 2.0],
            'hole_spacing_min': 2.0,  # Diameters
            'depth_min': 1.0,  # Times hole diameter
            'typical_applications': ['lap connections', 'splice plates', 'shear transfer'],
            'strength_per_size': {  # kips per plug (E70XX)
                0.75: 3.5,
                1.0: 6.0,
                1.25: 9.0,
                1.5: 12.0,
            },
            'electrode_types': ['E60XX', 'E70XX', 'E80XX'],
            'inspection': ['visual'],
        },
        'slot_weld': {
            'description': 'Slot weld through one member',
            'joint_type': 'slot',
            'slot_width': [0.625, 0.75, 1.0],
            'slot_length': [1.5, 2.0, 2.5, 3.0],  # Typical
            'typical_applications': ['lap connections', 'edge connections'],
            'strength_calculation': 'similar to plug, based on area',
            'electrode_types': ['E60XX', 'E70XX'],
            'inspection': ['visual'],
        },
    },
    'SPECIAL': {
        'back_weld': {
            'description': 'Back weld (backing weld)',
            'purpose': 'ensures root fusion, two-sided',
            'typical_applications': ['critical CJP butt welds'],
            'size_typical': 0.25,
            'backing_type': ['steel backing', 'copper backing', 'ceramic backing'],
        },
        'cosmetic_finish': {
            'description': 'Finished/ground weld surface',
            'purpose': 'aesthetic or stress concentration reduction',
            'typical_applications': ['architectural', 'fatigue-critical'],
            'finish_depth': 'flush with base metal',
            'cost_multiplier': 1.5,  # Relative to standard weld
        },
        'seal_weld': {
            'description': 'Seal weld (corrosion protection)',
            'purpose': 'prevent corrosion path penetration',
            'typical_applications': ['splash zone', 'corrosive environment'],
            'material': 'low hydrogen electrode recommended',
            'pwht': 'may be required',
        },
    },
}

# Electrode specifications
ELECTRODE_SPECS = {
    'E60XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 60,
        'yield_strength_ksi': 50,
        'elongation_percent': 22,
        'typical_applications': ['general purpose', 'low stress'],
        'cost_per_lb': 0.8,
        'deposition_rate': 'standard',
    },
    'E70XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 70,
        'yield_strength_ksi': 58,
        'elongation_percent': 20,
        'typical_applications': ['general structural', 'most common'],
        'cost_per_lb': 0.9,
        'deposition_rate': 'standard',
    },
    'E80XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 80,
        'yield_strength_ksi': 67,
        'elongation_percent': 18,
        'typical_applications': ['higher strength steel', 'HY50', 'HY80'],
        'cost_per_lb': 1.1,
        'deposition_rate': 'reduced',
        'preheat': 'typically required',
    },
    'E90XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 90,
        'yield_strength_ksi': 77,
        'elongation_percent': 16,
        'typical_applications': ['very high strength', 'HY100', 'specialty'],
        'cost_per_lb': 1.3,
        'deposition_rate': 'reduced',
        'preheat': 'required',
        'pwht': 'required',
    },
    'E100XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 100,
        'yield_strength_ksi': 88,
        'typical_applications': ['extreme strength applications'],
        'cost_per_lb': 1.5,
        'deposition_rate': 'very low',
        'preheat': 'required',
        'pwht': 'required',
        'availability': 'special order only',
    },
    'E120XX': {
        'classification': 'AWS A5.1',
        'tensile_strength_ksi': 120,
        'yield_strength_ksi': 105,
        'typical_applications': ['specialty/research'],
        'cost_per_lb': 2.0,
        'deposition_rate': 'very low',
        'preheat': 'critical',
        'pwht': 'mandatory',
        'availability': 'very limited',
    },
}

# Weld quality standards
WELD_QUALITY_STANDARDS = {
    'visual': {
        'standard': 'AWS D1.1 / AWS D1.2',
        'inspection_method': 'visual examination only',
        'defects_allowed': 'per AWS D1.1 acceptance criteria',
        'typical_applications': ['general structural', 'secondary connections'],
        'cost': 1.0,
    },
    'partial_ul': {
        'standard': 'AWS D1.1 Section 12.2',
        'inspection_method': '10% UT sample',
        'defects_allowed': 'very limited per AISC',
        'typical_applications': ['primary connections', 'tier 2'],
        'cost': 1.3,
    },
    'full_ut': {
        'standard': '100% Ultrasonic Testing',
        'inspection_method': 'Full UT coverage',
        'defects_allowed': 'minimal - accept/reject per ASME Section VIII',
        'typical_applications': ['critical welds', 'moment connections', 'seismic'],
        'cost': 1.8,
        'qualification': 'UT level II/III required',
    },
    'magnetic_particle': {
        'standard': 'AWS D1.1',
        'inspection_method': 'Magnetic particle testing',
        'defects_allowed': 'per AWS D1.1 MT criteria',
        'typical_applications': ['fatigue-critical', 'high cycle'],
        'cost': 1.5,
        'material_restriction': 'ferrous only',
    },
    'radiographic': {
        'standard': 'AWS D1.1',
        'inspection_method': 'X-ray or gamma-ray',
        'defects_allowed': 'per AWS D1.1 RT criteria',
        'typical_applications': ['pressure vessels', 'critical structures'],
        'cost': 2.0,
        'turnaround': 'slow (film processing)',
    },
    'phased_array_ut': {
        'standard': 'ASME PCC-2',
        'inspection_method': 'Advanced UT (phased array)',
        'defects_allowed': 'minimal',
        'typical_applications': ['modern seismic', 'bridge work'],
        'cost': 1.9,
        'speed': 'faster than radiography',
    },
}

# Helper functions
def get_electrode_by_grade(grade: str) -> dict:
    """Get electrode properties by AWS grade.
    
    Args:
        grade (str): Electrode grade (e.g., 'E70XX', 'E80XX')
    
    Returns:
        dict: Electrode specifications
    
    Example:
        >>> elec = get_electrode_by_grade('E70XX')
        >>> elec['tensile_strength_ksi']
        70
    """
    return ELECTRODE_SPECS.get(grade, {})


def weld_strength_per_length(weld_size: float, electrode_grade: str = 'E70XX') -> float:
    """Calculate weld capacity per unit length.
    
    Args:
        weld_size (float): Weld size (in)
        electrode_grade (str): AWS grade
    
    Returns:
        float: Capacity (kips per inch of weld)
    """
    electrode = get_electrode_by_grade(electrode_grade)
    strength = electrode.get('tensile_strength_ksi', 70)
    
    # Simplified formula: 0.6 * F_EXX * weld_area
    # Throat area = weld_size * sin(45°) * length = 0.707 * size * length
    # Strength per length = 0.6 * 0.707 * size * strength / 1000
    
    return 0.6 * 0.707 * weld_size * strength / 1000


def get_weld_by_name(weld_type: str, weld_subtype: str = None) -> dict:
    """Get weld specification by type.
    
    Args:
        weld_type (str): Category ('FILLET', 'BUTT', etc)
        weld_subtype (str): Specific type
    
    Returns:
        dict: Weld specification
    """
    if weld_type not in WELD_TYPES:
        return {}
    
    if weld_subtype is None:
        return WELD_TYPES[weld_type]
    
    return WELD_TYPES.get(weld_type, {}).get(weld_subtype, {})


def list_weld_types(category: str = None) -> list:
    """List available weld types.
    
    Args:
        category (str): Optional category filter
    
    Returns:
        list: Available weld types
    """
    if category and category in WELD_TYPES:
        return list(WELD_TYPES[category].keys())
    
    all_types = []
    for cat, types_dict in WELD_TYPES.items():
        all_types.extend(types_dict.keys())
    
    return all_types


def inspection_cost_factor(inspection_type: str) -> float:
    """Get cost multiplier for inspection type.
    
    Args:
        inspection_type (str): Inspection standard name
    
    Returns:
        float: Cost multiplier
    """
    return WELD_QUALITY_STANDARDS.get(inspection_type, {}).get('cost', 1.0)
