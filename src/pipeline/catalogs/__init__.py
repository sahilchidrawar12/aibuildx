"""Catalogs module for structural components and specifications.

Provides comprehensive catalogs for structural sections, connections, and welds,
including AISC, Eurocode, and proprietary specifications.

Data:
    SECTION_CATALOG: AISC wide-flange and hollow section profiles
    EUROCODE_CATALOG: Eurocode IPE and HE section profiles
    CONNECTION_TYPES: Standard connection type definitions
    WELD_TYPES: Standard weld type definitions
    
Functions:
    get_section_by_name: Retrieve section properties by name
    get_connection_by_name: Retrieve connection spec by type
    get_weld_by_name: Retrieve weld spec by type

Import Examples:
    from src.pipeline.catalogs import SECTION_CATALOG
    from src.pipeline.catalogs import CONNECTION_TYPES
    from src.pipeline.catalogs import WELD_TYPES
    from src.pipeline.catalogs import get_section_by_name
    from src.pipeline.catalogs import get_connection_by_name
    
    # Get section properties
    w_section = get_section_by_name('W12x19')
    print(w_section['Ix'])  # Moment of inertia
    
    # Get connection type
    bolted = get_connection_by_name('BOLTED', 'simple_shear')
    print(bolted['load_type'])  # 'shear'
    
    # Get weld type
    fillet = get_weld_by_name('FILLET', 'fillet_general')
"""

from .section_catalog import (
    SECTION_CATALOG,
    EUROCODE_CATALOG,
    SECTION_GEOM,
    get_section_by_name,
    find_lightest_section,
    find_strongest_section,
)

from .connection_types import (
    CONNECTION_TYPES,
    CONNECTION_CRITERIA,
    get_connection_by_name,
    list_connection_types,
    get_connection_materials,
)

from .weld_types import (
    WELD_TYPES,
    ELECTRODE_SPECS,
    WELD_QUALITY_STANDARDS,
    get_weld_by_name,
    list_weld_types,
    weld_strength_per_length,
)

__all__ = [
    # Section catalogs
    'SECTION_CATALOG',
    'EUROCODE_CATALOG',
    'SECTION_GEOM',
    'get_section_by_name',
    'find_lightest_section',
    'find_strongest_section',
    
    # Connection catalogs
    'CONNECTION_TYPES',
    'CONNECTION_CRITERIA',
    'get_connection_by_name',
    'list_connection_types',
    'get_connection_materials',
    
    # Weld catalogs
    'WELD_TYPES',
    'ELECTRODE_SPECS',
    'WELD_QUALITY_STANDARDS',
    'get_weld_by_name',
    'list_weld_types',
    'weld_strength_per_length',
]
