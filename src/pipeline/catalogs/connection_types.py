"""Connection type catalogs and specifications.

Defines standard connection types, configurations, and design parameters
for structural steel connections including bolted, welded, and hybrid types.

Data:
    CONNECTION_TYPES: Comprehensive connection type catalog
    CONNECTION_CRITERIA: Design requirements by connection type
"""

# Connection type definitions
CONNECTION_TYPES = {
    'BOLTED': {
        'simple_shear': {
            'description': 'Single or double shear bolted connection',
            'load_type': 'shear',
            'fastener': 'bolt',
            'typical_applications': ['beam-to-column', 'splice plates', 'angle connections'],
            'strength_equations': 'AISC 360 J3.6',
            'friction_type': 'standard',
            'bolt_grades': ['A325', 'A490'],
            'typical_dia': [0.5, 0.625, 0.75, 0.875, 1.0],
        },
        'tension': {
            'description': 'Bolted tension connection',
            'load_type': 'tension',
            'fastener': 'bolt',
            'typical_applications': ['tension splices', 'hanger connections', 'tie rods'],
            'strength_equations': 'AISC 360 J3.7',
            'friction_type': 'none',
            'bolt_grades': ['A325', 'A490'],
            'typical_dia': [0.625, 0.75, 0.875, 1.0, 1.125],
        },
        'combined': {
            'description': 'Combined shear and tension',
            'load_type': 'combined',
            'fastener': 'bolt',
            'typical_applications': ['bracket connections', 'moment connections'],
            'strength_equations': 'AISC 360 J3.7-1',
            'friction_type': 'slip-critical',
            'bolt_grades': ['A325', 'A490'],
            'typical_dia': [0.75, 0.875, 1.0],
        },
        'bearing': {
            'description': 'Bearing-type bolted connection',
            'load_type': 'shear',
            'fastener': 'bolt',
            'typical_applications': ['standard shear connections'],
            'strength_equations': 'AISC 360 J3.6',
            'friction_type': 'bearing',
            'bolt_grades': ['A307', 'A325', 'A490'],
            'typical_dia': [0.5, 0.625, 0.75, 1.0],
        },
        'slip_critical': {
            'description': 'Slip-critical (friction) connection',
            'load_type': 'shear',
            'fastener': 'bolt',
            'typical_applications': ['seismic connections', 'vibration-sensitive'],
            'strength_equations': 'AISC 360 J3.8',
            'friction_type': 'slip-critical',
            'bolt_grades': ['A325', 'A490'],
            'typical_dia': [0.75, 0.875, 1.0, 1.125],
            'surface_prep': ['Class A', 'Class B', 'Class C'],
        },
    },
    'WELDED': {
        'fillet_shear': {
            'description': 'Fillet weld in shear',
            'load_type': 'shear',
            'fastener': 'weld',
            'typical_applications': ['beam-to-column', 'plate connections', 'splices'],
            'strength_equations': 'AISC 360 J2.4',
            'weld_type': 'fillet',
            'electrode_types': ['E60XX', 'E70XX', 'E80XX', 'E90XX'],
            'typical_sizes': [3/16, 1/4, 5/16, 3/8, 7/16, 1/2],
            'position': ['flat', 'horizontal', 'vertical', 'overhead'],
        },
        'fillet_tension': {
            'description': 'Fillet weld in tension',
            'load_type': 'tension',
            'fastener': 'weld',
            'typical_applications': ['tension splices', 'T-connections'],
            'strength_equations': 'AISC 360 J2.4',
            'weld_type': 'fillet',
            'electrode_types': ['E60XX', 'E70XX', 'E80XX'],
            'typical_sizes': [1/4, 5/16, 3/8, 7/16, 1/2],
            'position': ['flat', 'horizontal'],
        },
        'complete_joint_pen': {
            'description': 'Complete joint penetration (CJP) butt weld',
            'load_type': 'combined',
            'fastener': 'weld',
            'typical_applications': ['moment connections', 'primary members', 'high stress'],
            'strength_equations': 'AISC 360 J2.5',
            'weld_type': 'butt',
            'electrode_types': ['E70XX', 'E80XX', 'E90XX', 'E100XX', 'E120XX'],
            'typical_sizes': ['full penetration'],
            'position': ['flat', 'horizontal', 'vertical', 'overhead'],
            'inspection': ['UT', 'RT', 'MT', 'PT'],
        },
        'partial_joint_pen': {
            'description': 'Partial joint penetration (PJP) butt weld',
            'load_type': 'combined',
            'fastener': 'weld',
            'typical_applications': ['secondary connections', 'transfers loads'],
            'strength_equations': 'AISC 360 J2.5',
            'weld_type': 'butt',
            'electrode_types': ['E60XX', 'E70XX', 'E80XX'],
            'typical_sizes': [1/4, 3/8, 1/2, 5/8, 3/4],
            'inspection': ['visual', 'UT selective'],
        },
        'plug': {
            'description': 'Plug or slot weld',
            'load_type': 'shear',
            'fastener': 'weld',
            'typical_applications': ['lap connections', 'splice plates'],
            'strength_equations': 'AISC 360 J2.3',
            'weld_type': 'plug',
            'electrode_types': ['E60XX', 'E70XX', 'E80XX'],
            'hole_dia': [0.75, 1.0, 1.25, 1.5],
            'min_depth': ['1.0 × dia', '1.0 × dia'],
        },
    },
    'HYBRID': {
        'bolted_welded': {
            'description': 'Combination of bolts and welds',
            'load_type': 'combined',
            'fastener': 'bolt + weld',
            'typical_applications': ['moment connections', 'complex transfers'],
            'strength_equations': 'AISC 360 J2/J3',
            'bolt_grades': ['A325', 'A490'],
            'electrode_types': ['E70XX', 'E80XX'],
            'configuration': 'bolts for shear, welds for tension or moment',
        },
        'high_strength_bolts_washers': {
            'description': 'HSBs with hardened washers',
            'load_type': 'shear',
            'fastener': 'bolt + washer',
            'typical_applications': ['high-load shear', 'tension controls'],
            'bolt_grades': ['A325', 'A490'],
            'washer_type': ['hardened', 'ASTM F436', 'ASTM F844'],
        },
    },
    'SPECIAL': {
        'moment_connection': {
            'description': 'Moment-resisting connection (rigid)',
            'load_type': 'moment',
            'fastener': 'weld + bolt',
            'typical_applications': ['rigid frames', 'SMRFs', 'seismic'],
            'strength_equations': 'AISC 341',
            'joint_types': ['CJP butt weld', 'reduced beam section', 'bolted flange plate'],
            'panel_zone_required': True,
        },
        'eccentric_connection': {
            'description': 'Eccentric load on fasteners',
            'load_type': 'combined',
            'fastener': 'bolt',
            'typical_applications': ['bracket loads', 'corner connections'],
            'strength_equations': 'AISC 360 J3.6',
            'analysis_method': 'IC method or vector analysis',
        },
        'cantilever': {
            'description': 'Cantilever or overhang connection',
            'load_type': 'combined',
            'fastener': 'bolt + weld',
            'typical_applications': ['balconies', 'exterior elements'],
            'design_note': 'Account for tension pry-out and overhang moment',
        },
    },
}

# Design criteria by connection type
CONNECTION_CRITERIA = {
    'simple_shear': {
        'serviceability': {'slip_check': True, 'fatigue_check': False},
        'ultimate': {'bolt_bearing': True, 'net_section': True, 'pry_out': False},
        'min_bolts': 2,
        'edge_distance_min': 1.5,  # Bolt diameters from edge
        'pitch_min': 3.0,  # Bolt diameters
        'pitch_max': 6.0,  # Bolt diameters
    },
    'tension': {
        'serviceability': {'slip_check': False, 'fatigue_check': False},
        'ultimate': {'bolt_tension': True, 'pry_out': True, 'net_section': True},
        'min_bolts': 1,
        'edge_distance_min': 1.25,
        'pitch_min': 3.0,
        'pry_out_lever_arm': 'a dimension',  # See AISC J3.7-1
    },
    'combined': {
        'serviceability': {'slip_check': True, 'fatigue_check': False},
        'ultimate': {'interaction': True, 'bolt_tension': True, 'pry_out': True},
        'min_bolts': 4,
        'tension_reduction': 0.9,  # Typical reduction factor
    },
    'fillet_weld': {
        'serviceability': {'stress_check': True},
        'ultimate': {'capacity': True, 'intermittent': 'allowed'},
        'min_size_in': 3/16,  # For plate thickness > 1/4"
        'max_size_in': 'plate_thickness',
        'leg_size': [3/16, 1/4, 5/16, 3/8, 7/16, 1/2],
    },
    'moment_connection': {
        'serviceability': {'rotation': True, 'elastic_deformation': True},
        'ultimate': {'moment_capacity': True, 'shear': True, 'panel_zone': True},
        'panel_zone_check': True,
        'strong_column_weak_beam': 1.2,  # AISC 341 requirement
        'ductility_required': True,
    },
}

# Helper functions
def get_connection_by_name(conn_type: str, conn_subtype: str = None) -> dict:
    """Get connection specification by type and subtype.
    
    Args:
        conn_type (str): 'BOLTED', 'WELDED', 'HYBRID', 'SPECIAL'
        conn_subtype (str): Specific connection subtype
    
    Returns:
        dict: Connection specification
    
    Example:
        >>> conn = get_connection_by_name('BOLTED', 'simple_shear')
        >>> conn['load_type']
        'shear'
    """
    if conn_type not in CONNECTION_TYPES:
        return {}
    
    if conn_subtype is None:
        return CONNECTION_TYPES[conn_type]
    
    return CONNECTION_TYPES.get(conn_type, {}).get(conn_subtype, {})


def list_connection_types(conn_category: str = None) -> list:
    """List available connection types.
    
    Args:
        conn_category (str): Optional category filter
    
    Returns:
        list: Available connection types
    """
    if conn_category and conn_category in CONNECTION_TYPES:
        return list(CONNECTION_TYPES[conn_category].keys())
    
    all_types = []
    for category, types_dict in CONNECTION_TYPES.items():
        all_types.extend(types_dict.keys())
    
    return all_types


def connection_load_type(conn_type: str, conn_subtype: str) -> str:
    """Get load type for connection.
    
    Args:
        conn_type (str): Category
        conn_subtype (str): Specific type
    
    Returns:
        str: Load type ('shear', 'tension', 'combined', 'moment')
    """
    conn_spec = get_connection_by_name(conn_type, conn_subtype)
    return conn_spec.get('load_type', 'unknown')


def get_connection_materials(conn_type: str, conn_subtype: str) -> dict:
    """Get material requirements for connection.
    
    Args:
        conn_type (str): Category
        conn_subtype (str): Specific type
    
    Returns:
        dict: Material specifications (bolts, welds, etc)
    """
    conn_spec = get_connection_by_name(conn_type, conn_subtype)
    materials = {}
    
    if 'bolt_grades' in conn_spec:
        materials['bolt_grades'] = conn_spec['bolt_grades']
    
    if 'electrode_types' in conn_spec:
        materials['electrode_types'] = conn_spec['electrode_types']
    
    if 'typical_dia' in conn_spec:
        materials['bolt_diameters'] = conn_spec['typical_dia']
    
    return materials
