"""Enhanced IFC generator with proper profile definitions, geometry, and spatial hierarchy.
Generates complete IfcBeam/IfcColumn/IfcPlate/IfcFastener entities with:
- Profile definitions (IfcIShapeProfileDef, IfcRectangleProfileDef, etc.)
- Extruded area solid geometry
- Quantities (area, volume)
- Proper IfcLocalPlacement and IfcAxis2Placement3D
- Spatial containment relationships
- Structural connections relationships
"""
from typing import Dict, Any, List, Tuple, Optional
import uuid
import math

# ============ UNIT CONVERSION & NORMALIZATION ============

def _new_guid():
    """Generate a unique IFC GUID (using UUID format; ready for conversion to IFC STEP compressed GUID)."""
    return str(uuid.uuid4())

def _to_metres(val: float) -> Optional[float]:
    """Convert a numeric length from mm to metres consistently.
    
    Assumes input is in mm if >= 100. Otherwise treats as already converted.
    This ensures 3000 mm → 3.0 m, 6000 mm → 6.0 m.
    """
    try:
        if val is None:
            return None
        # Heuristic: model inputs are in mm; values like 3000, 6000 should become 3.0, 6.0 m
        return (val / 1000.0) if abs(val) >= 100 else float(val)
    except Exception:
        return val

def _vec_to_metres(vec: List[float]) -> List[float]:
    """Convert vector from mm to metres."""
    if not vec:
        return vec
    return [_to_metres(v) for v in vec]

def normalize_vector(vec: List[float]) -> List[float]:
    """Normalize a vector to unit length.
    
    Args:
        vec: List of floats [x, y, z]
        
    Returns:
        Normalized vector or [0, 0, 1] if magnitude is zero.
    """
    if not vec or len(vec) < 3:
        return [0.0, 0.0, 1.0]
    
    magnitude = math.sqrt(sum(v**2 for v in vec))
    if magnitude < 1e-10:
        return [0.0, 0.0, 1.0]
    
    return [v / magnitude for v in vec]

# ============ PROFILE DEFINITIONS ============

def generate_i_shape_profile(profile: Dict[str, Any], member_id: str) -> Dict[str, Any]:
    """Generate IfcIShapeProfileDef for I/H-sections.
    
    Args:
        profile: Profile dict with depth, width, web_thickness, flange_thickness, etc.
        member_id: Member ID for naming
        
    Returns:
        IFC profile definition dict
    """
    depth_m = _to_metres(profile.get('depth') or 300.0)
    width_m = _to_metres(profile.get('width') or 150.0)
    web_thick_m = _to_metres(profile.get('web_thickness') or 8.0)
    flange_thick_m = _to_metres(profile.get('flange_thickness') or 12.0)
    fillet_radius_m = _to_metres(profile.get('fillet_radius') or 10.0)
    
    area_m2 = _to_metres(_to_metres(profile.get('area'))) if profile.get('area') else None
    ix_m4 = _to_metres(_to_metres(_to_metres(profile.get('Ix')))) if profile.get('Ix') else None
    
    return {
        "type": "IfcIShapeProfileDef",
        "profile_name": profile.get('name') or f"I-Section-{member_id[:8]}",
        "profile_type": "I",
        "depth": depth_m,
        "width": width_m,
        "web_thickness": web_thick_m,
        "flange_thickness": flange_thick_m,
        "fillet_radius": fillet_radius_m,
        "area": area_m2,
        "Ix": ix_m4,  # Second moment about strong axis
        "Iy": _to_metres(_to_metres(_to_metres(profile.get('Iy')))) if profile.get('Iy') else None,
        "Zx": _to_metres(_to_metres(profile.get('Zx'))) if profile.get('Zx') else None,
        "Zy": _to_metres(_to_metres(profile.get('Zy'))) if profile.get('Zy') else None,
    }

def generate_rectangular_profile(profile: Dict[str, Any], member_id: str) -> Dict[str, Any]:
    """Generate IfcRectangleProfileDef for rectangular/tube sections.
    
    Args:
        profile: Profile dict with depth, width, wall_thickness, etc.
        member_id: Member ID for naming
        
    Returns:
        IFC profile definition dict
    """
    depth_m = _to_metres(profile.get('depth') or 300.0)
    width_m = _to_metres(profile.get('width') or 150.0)
    thickness_m = _to_metres(profile.get('wall_thickness') or profile.get('thickness') or 8.0)
    
    return {
        "type": "IfcRectangleProfileDef",
        "profile_name": profile.get('name') or f"RHS-{member_id[:8]}",
        "profile_type": "RECTANGLE",
        "x_dim": width_m,
        "y_dim": depth_m,
        "wall_thickness": thickness_m,
        "area": _to_metres(_to_metres(profile.get('area'))) if profile.get('area') else None,
        "Ix": _to_metres(_to_metres(_to_metres(profile.get('Ix')))) if profile.get('Ix') else None,
        "Iy": _to_metres(_to_metres(_to_metres(profile.get('Iy')))) if profile.get('Iy') else None,
    }

def generate_profile_def(profile: Dict[str, Any], member_id: str) -> Dict[str, Any]:
    """Determine profile type and generate appropriate IFC profile definition.
    
    Args:
        profile: Profile dict from member
        member_id: Member ID for naming
        
    Returns:
        IFC profile definition dict (I-shape, rectangle, or circle)
    """
    profile_type = (profile.get('type') or '').upper()
    
    if not profile:
        # Fallback: default I-shape
        return generate_i_shape_profile({}, member_id)
    
    if 'I' in profile_type or 'H' in profile_type or 'W' in profile_type:
        return generate_i_shape_profile(profile, member_id)
    elif 'RHS' in profile_type or 'RECT' in profile_type or 'BOX' in profile_type:
        return generate_rectangular_profile(profile, member_id)
    else:
        # Default: treat as I-shape
        return generate_i_shape_profile(profile, member_id)

def create_extruded_area_solid(profile_def: Dict[str, Any], length_m: float, member_id: str) -> Dict[str, Any]:
    """Create IfcExtrudedAreaSolid geometry for a member.
    
    Args:
        profile_def: Profile definition dict
        length_m: Extrusion length in metres
        member_id: Member ID for naming
        
    Returns:
        Extruded area solid representation dict
    """
    return {
        "type": "IfcExtrudedAreaSolid",
        "profile_type": profile_def.get('type'),
        "profile_name": profile_def.get('profile_name'),
        "extrusion_direction": [1.0, 0.0, 0.0],  # Along member X-axis
        "extrusion_length": length_m,
        "area": profile_def.get('area'),
        "volume": profile_def.get('area') * length_m if profile_def.get('area') else None,
    }

# ============ LOCAL PLACEMENT CREATION ============

def create_local_placement(location_m: List[float], axis_z: List[float], 
                          ref_direction_x: List[float]) -> Dict[str, Any]:
    """Create proper IfcLocalPlacement with IfcAxis2Placement3D.
    
    Args:
        location_m: Origin in metres [x, y, z]
        axis_z: Z-axis direction (normalized)
        ref_direction_x: X-axis reference direction (normalized)
        
    Returns:
        Placement dict with proper structure
    """
    axis_z_norm = normalize_vector(axis_z or [0, 0, 1])
    ref_x_norm = normalize_vector(ref_direction_x or [1, 0, 0])
    
    return {
        "location": location_m or [0.0, 0.0, 0.0],
        "axis": axis_z_norm,
        "ref_direction": ref_x_norm,
        "Axis2Placement3D": {
            "location": location_m or [0.0, 0.0, 0.0],
            "axis": axis_z_norm,
            "ref_direction": ref_x_norm,
        }
    }

# ============ QUANTITY CALCULATION ============

def create_quantities(profile_def: Dict[str, Any], length_m: float) -> Dict[str, Any]:
    """Calculate and create quantities for a member.
    
    Args:
        profile_def: Profile definition dict
        length_m: Member length in metres
        
    Returns:
        Quantities dict with area, volume, mass, etc.
    """
    area_m2 = profile_def.get('area')
    volume_m3 = None
    mass_kg = None
    
    if area_m2 and length_m:
        volume_m3 = area_m2 * length_m
        # Steel density: 7850 kg/m³
        mass_kg = volume_m3 * 7850.0
    
    return {
        "Length": length_m,
        "CrossSectionArea": area_m2,
        "GrossVolume": volume_m3,
        "NetVolume": volume_m3,
        "Mass": mass_kg,
        "MassPerUnitLength": mass_kg / length_m if (mass_kg and length_m) else None,
    }

# ============ MEMBER GENERATION ============

def generate_ifc_beam(member: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC beam with profile definitions, geometry, and quantities."""
    # Unit normalization: assume input coordinates are mm → convert to metres
    start_m = _vec_to_metres(member.get('start'))
    end_m = _vec_to_metres(member.get('end'))
    length_m = _to_metres(member.get('length'))
    
    # Compute direction vector (normalized)
    if start_m and end_m and length_m and length_m > 1e-6:
        direction = [(end_m[i] - start_m[i]) / length_m for i in range(3)]
    else:
        direction = member.get('dir') or [1.0, 0.0, 0.0]
    
    direction_norm = normalize_vector(direction)

    profile = member.get('profile') or member.get('geom') or {}
    material = member.get('material') or {}
    # Enrich material with typical steel properties when missing
    material.setdefault('name', 'S235')
    material.setdefault('E', 210000.0)  # MPa
    material.setdefault('fy', 235.0)  # MPa
    material.setdefault('density', 7850.0)  # kg/m3

    # Generate profile definition
    profile_def = generate_profile_def(profile, member.get('id', 'beam'))
    
    # Create extruded area solid
    swept_area = create_extruded_area_solid(profile_def, length_m or 0.0, member.get('id', 'beam'))
    
    # Create quantities
    quantities = create_quantities(profile_def, length_m or 0.0)
    
    # Create placement
    placement = create_local_placement(
        location_m=start_m,
        axis_z=member.get('weak_axis') or [0, 0, 1],
        ref_direction_x=direction_norm
    )

    return {
        "type": "IfcBeam",
        "id": member.get('id') or _new_guid(),
        "name": f"Beam-{member.get('id', 'Unknown')[:8]}",
        "length": length_m,
        "profile": profile_def,
        "start": start_m,
        "end": end_m,
        "direction": direction_norm,
        "material": material,
        "placement": placement,
        "representation": {
            "profile_name": profile_def.get('profile_name'),
            "profile_type": profile_def.get('type'),
            "swept_area": swept_area,
        },
        "property_sets": {
            "Pset_BeamCommon": {
                "Reference": member.get('id'),
                "LoadBearing": True,
                "IsExternal": False
            },
            "Structural_Properties": {
                "Length": length_m,
                "Layer": member.get('layer'),
                "Rotation": member.get('rotation', 0.0),
                "ErectionSequence": member.get('erection_seq')
            }
        },
        "quantities": quantities
    }

def generate_ifc_column(member: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC column with profile definitions, geometry, and quantities."""
    # Unit normalization: assume input coordinates are mm → convert to metres
    start_m = _vec_to_metres(member.get('start'))
    end_m = _vec_to_metres(member.get('end'))
    length_m = _to_metres(member.get('length'))
    
    # Compute direction vector (normalized)
    if start_m and end_m and length_m and length_m > 1e-6:
        direction = [(end_m[i] - start_m[i]) / length_m for i in range(3)]
    else:
        direction = member.get('dir') or [0.0, 0.0, 1.0]
    
    direction_norm = normalize_vector(direction)

    profile = member.get('profile') or member.get('geom') or {}
    material = member.get('material') or {}
    material.setdefault('name', 'S235')
    material.setdefault('E', 210000.0)
    material.setdefault('fy', 235.0)
    material.setdefault('density', 7850.0)

    # Generate profile definition
    profile_def = generate_profile_def(profile, member.get('id', 'column'))
    
    # Create extruded area solid
    swept_area = create_extruded_area_solid(profile_def, length_m or 0.0, member.get('id', 'column'))
    
    # Create quantities
    quantities = create_quantities(profile_def, length_m or 0.0)
    
    # Create placement
    placement = create_local_placement(
        location_m=start_m,
        axis_z=direction_norm,
        ref_direction_x=member.get('strong_axis') or [1, 0, 0]
    )

    return {
        "type": "IfcColumn",
        "id": member.get('id') or _new_guid(),
        "name": f"Column-{member.get('id', 'Unknown')[:8]}",
        "length": length_m,
        "profile": profile_def,
        "start": start_m,
        "end": end_m,
        "direction": direction_norm,
        "material": material,
        "placement": placement,
        "representation": {
            "profile_name": profile_def.get('profile_name'),
            "profile_type": profile_def.get('type'),
            "swept_area": swept_area,
        },
        "property_sets": {
            "Pset_ColumnCommon": {
                "Reference": member.get('id'),
                "LoadBearing": True,
                "IsExternal": False
            },
            "Structural_Properties": {
                "Length": length_m,
                "Layer": member.get('layer'),
                "Rotation": member.get('rotation', 0.0),
                "ErectionSequence": member.get('erection_seq')
            }
        },
        "quantities": quantities
    }

def generate_ifc_plate(plate: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC plate with proper orientation and units.
    
    Plates have outline dimensions and thickness. Position is global coordinates.
    Orientation includes Axis2Placement3D for proper spatial reference.
    """
    # Convert plate dimensions from mm to metres if needed
    plate_id = plate.get('id') or _new_guid()
    
    # Position: convert from mm to m if it looks like mm
    position_m = _vec_to_metres(plate.get('position') or plate.get('pos') or [0, 0, 0])
    
    # Outline dimensions: convert from mm to m
    outline = plate.get('outline') or {}
    width_mm = outline.get('width_mm') or outline.get('width') or 100.0
    height_mm = outline.get('height_mm') or outline.get('height') or 100.0
    thickness_mm = plate.get('thickness') or 10.0
    
    width_m = _to_metres(width_mm)
    height_m = _to_metres(height_mm)
    thickness_m = _to_metres(thickness_mm)
    
    # Get orientation or use defaults
    orientation = plate.get('orientation') or {}
    axis_placement = orientation.get('Axis2Placement3D') or {}
    
    # Normalize axis and reference direction
    axis_z = normalize_vector(axis_placement.get('axis') or [0, 0, 1])
    ref_dir_x = normalize_vector(axis_placement.get('refDirection') or [1, 0, 0])
    
    # Calculate area and volume
    area_m2 = (width_m or 0.0) * (height_m or 0.0)
    volume_m3 = area_m2 * (thickness_m or 0.0)
    
    return {
        "type": "IfcPlate",
        "id": plate_id,
        "name": f"Plate-{plate_id[:8]}",
        "outline": {
            "width": width_m,
            "height": height_m,
        },
        "thickness": thickness_m,
        "material": plate.get('material') or {'name': 'S235'},
        "placement": create_local_placement(position_m, axis_z, ref_dir_x),
        "representation": {
            "area": area_m2,
            "volume": volume_m3,
            "thickness": thickness_m,
        },
        "property_sets": {
            "Pset_PlateCommon": {
                "Reference": plate.get('id'),
                "LoadBearing": True
            }
        },
        "quantities": {
            "Area": area_m2,
            "Volume": volume_m3,
            "Thickness": thickness_m,
        }
    }

def generate_ifc_fastener(bolt: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC fastener (bolt) with proper global placement.
    
    Fasteners have global position (in metres) and diameter (in mm → m).
    Orientation is vertical by default.
    """
    bolt_id = bolt.get('id') or _new_guid()
    
    # Convert position from mm to m
    position_m = _vec_to_metres(bolt.get('position') or bolt.get('pos') or [0, 0, 0])
    
    # Bolt diameter: convert from mm to m
    diameter_mm = bolt.get('diameter') or 20.0
    diameter_m = _to_metres(diameter_mm)
    
    # Get orientation or use defaults (vertical)
    orientation = bolt.get('orientation') or {}
    axis_placement = orientation.get('Axis2Placement3D') or {}
    
    axis_z = normalize_vector(axis_placement.get('axis') or [0, 0, 1])
    ref_dir_x = normalize_vector(axis_placement.get('refDirection') or [1, 0, 0])
    
    return {
        "type": "IfcFastener",
        "id": bolt_id,
        "name": f"Bolt-{bolt_id[:8]}",
        "diameter": diameter_m,
        "position": position_m,
        "diameter_mm": diameter_mm,  # Keep original for reference
        "grade": bolt.get('grade', 'A325'),
        "placement": create_local_placement(position_m, axis_z, ref_dir_x),
        "property_sets": {
            "Pset_FastenerCommon": {
                "NominalDiameter": diameter_m,
                "DiameterMillimetres": diameter_mm,
                "Grade": bolt.get('grade', 'A325')
            }
        }
    }

def export_ifc_model(members: List[Dict[str,Any]], plates: List[Dict[str,Any]], bolts: List[Dict[str,Any]]) -> Dict[str,Any]:
    """
    Export complete IFC model with spatial hierarchy, relationships, and all structural connections.
    
    Features:
    - Proper classification of members using 'layer' field and direction vectors
    - Profile definitions for all members (IfcIShapeProfileDef, IfcRectangleProfileDef)
    - IfcExtrudedAreaSolid geometry for members
    - Complete quantities (area, volume, mass)
    - Proper IfcLocalPlacement and IfcAxis2Placement3D for all elements
    - Spatial containment: project → site → building → storey → elements
    - Structural connections: IfcRelConnectsElements linking members, plates, bolts
    """
    # Initialize model with complete spatial structure
    project_id = _new_guid()
    site_id = _new_guid()
    building_id = _new_guid()
    storey_id = _new_guid()
    
    model = {
        "schema": "IFC4",
        "project": {
            "id": project_id,
            "name": "Steel Structure Project",
            "description": "Automated DXF to IFC conversion with connection synthesis"
        },
        "site": {
            "id": site_id,
            "name": "Construction Site",
            "elevation": 0.0
        },
        "building": {
            "id": building_id,
            "name": "Building",
            "elevation_of_ref_height": 0.0,
            "elevation_of_terrain": 0.0
        },
        "storey": {
            "id": storey_id,
            "name": "Ground Floor",
            "elevation": 0.0
        },
        "units": {
            "length": "METRE",
            "area": "SQUARE_METRE",
            "volume": "CUBIC_METRE",
            "force": "NEWTON",
            "stress": "MEGAPASCAL"
        },
        "owner_history": {
            "creation_date": "2025-12-03",
            "application": "AIBuildX",
            "version": "3.0.0"
        },
        "beams": [],
        "columns": [],
        "plates": [],
        "fasteners": [],
        "relationships": {
            "spatial_containment": [],
            "structural_connections": []
        }
    }
    
    # Build map of member IDs for connection tracking
    member_map = {}
    
    # Classify and process members
    for m in members:
        # Primary classification: use 'layer' field from DXF
        layer = (m.get('layer') or '').upper()
        
        # Secondary classification: check direction vector for vertical members
        direction = m.get('dir') or [0, 0, 0]
        is_vertical = abs(direction[2]) > 0.9  # Z-direction dominates
        
        # Tertiary classification: check for 'role' field (legacy support)
        role = (m.get('role') or '').lower()
        
        # Decision logic
        is_column = False
        if 'COLUMN' in layer:
            is_column = True
        elif is_vertical and layer != 'BEAMS':
            is_column = True  # Vertical member likely a column
        elif 'column' in role:
            is_column = True
        
        if is_column:
            ifc_element = generate_ifc_column(m)
            model['columns'].append(ifc_element)
            member_map[m.get('id')] = {
                'type': 'IfcColumn',
                'element_id': ifc_element['id'],
                'obj': ifc_element
            }
            # Add spatial containment relationship
            model['relationships']['spatial_containment'].append({
                "type": "IfcRelContainedInSpatialStructure",
                "relationship_id": _new_guid(),
                "element_id": ifc_element['id'],
                "element_type": "IfcColumn",
                "contained_in": storey_id,
                "container_type": "IfcBuildingStorey"
            })
        else:
            ifc_element = generate_ifc_beam(m)
            model['beams'].append(ifc_element)
            member_map[m.get('id')] = {
                'type': 'IfcBeam',
                'element_id': ifc_element['id'],
                'obj': ifc_element
            }
            # Add spatial containment relationship
            model['relationships']['spatial_containment'].append({
                "type": "IfcRelContainedInSpatialStructure",
                "relationship_id": _new_guid(),
                "element_id": ifc_element['id'],
                "element_type": "IfcBeam",
                "contained_in": storey_id,
                "container_type": "IfcBuildingStorey"
            })
    
    # Process plates and create connections
    plate_map = {}
    for p in plates:
        ifc_plate = generate_ifc_plate(p)
        model['plates'].append(ifc_plate)
        plate_map[p.get('id')] = ifc_plate['id']
        
        # Add plate to spatial containment
        model['relationships']['spatial_containment'].append({
            "type": "IfcRelContainedInSpatialStructure",
            "relationship_id": _new_guid(),
            "element_id": ifc_plate['id'],
            "element_type": "IfcPlate",
            "contained_in": storey_id,
            "container_type": "IfcBuildingStorey"
        })
        
        # Create connections between plate and connected members
        # Extract member references from plate (if available)
        members_on_plate = p.get('members') or []
        for member_id in members_on_plate:
            if member_id in member_map:
                member_info = member_map[member_id]
                # Add structural connection relationship
                model['relationships']['structural_connections'].append({
                    "type": "IfcRelConnectsElements",
                    "connection_id": _new_guid(),
                    "relating_element": member_info['element_id'],
                    "related_element": ifc_plate['id'],
                    "connection_type": "PlateConnection",
                    "element_types": [member_info['type'], "IfcPlate"]
                })
    
    # Process fasteners and create connections
    for b in bolts:
        ifc_fastener = generate_ifc_fastener(b)
        model['fasteners'].append(ifc_fastener)
        
        # Create connections between fastener and plate/members
        # Fasteners connect plates to members
        plate_id = b.get('plate_id')
        if plate_id and plate_id in plate_map:
            model['relationships']['structural_connections'].append({
                "type": "IfcRelConnectsWithRealizingElements",
                "connection_id": _new_guid(),
                "relating_element": plate_id,
                "related_element": plate_map.get(plate_id),
                "realizing_element": ifc_fastener['id'],
                "connection_type": "BoltConnection",
                "element_types": ["IfcPlate", "IfcFastener"]
            })
    
    # Add project-level spatial hierarchy relationships
    # project → site → building → storey
    model['relationships']['spatial_containment'].extend([
        {
            "type": "IfcRelAggregates",
            "relationship_id": _new_guid(),
            "relating_element": project_id,
            "related_elements": [site_id],
            "relation": "Project contains Site"
        },
        {
            "type": "IfcRelAggregates",
            "relationship_id": _new_guid(),
            "relating_element": site_id,
            "related_elements": [building_id],
            "relation": "Site contains Building"
        },
        {
            "type": "IfcRelAggregates",
            "relationship_id": _new_guid(),
            "relating_element": building_id,
            "related_elements": [storey_id],
            "relation": "Building contains Storey"
        }
    ])
    
    # Add summary statistics
    model['summary'] = {
        "total_columns": len(model['columns']),
        "total_beams": len(model['beams']),
        "total_plates": len(model['plates']),
        "total_fasteners": len(model['fasteners']),
        "total_elements": len(model['columns']) + len(model['beams']) + len(model['plates']) + len(model['fasteners']),
        "total_relationships": len(model['relationships']['spatial_containment']) + len(model['relationships']['structural_connections'])
    }
    
    return model
