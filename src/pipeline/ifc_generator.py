"""Lightweight IFC generator that emits simple JSON-like IFC structures.
This is a helper for producing IfcBeam/IfcColumn/IfcPlate/IfcFastener entries.
"""
from typing import Dict, Any, List
import uuid

def _new_guid():
    return str(uuid.uuid4())

def _to_metres(val: float) -> float:
    """Convert a numeric length from mm to metres if it looks like mm (>= 100)."""
    try:
        if val is None:
            return None
        # Heuristic: model inputs are in mm; values like 3000, 6000 should become 3.0, 6.0 m
        return (val / 1000.0) if abs(val) >= 100 else float(val)
    except Exception:
        return val

def _vec_to_metres(vec: List[float]) -> List[float]:
    if not vec:
        return vec
    return [_to_metres(v) for v in vec]

def generate_ifc_beam(member: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC beam with all required properties."""
    # Unit normalization: assume input coordinates are mm → convert to metres
    start_m = _vec_to_metres(member.get('start'))
    end_m = _vec_to_metres(member.get('end'))
    length_m = _to_metres(member.get('length'))

    profile = member.get('profile') or member.get('geom') or {}
    material = member.get('material') or {}
    # Enrich material with typical steel properties when missing
    material.setdefault('name', 'S235')
    material.setdefault('E', 210000.0)  # MPa
    material.setdefault('density', 7850.0)  # kg/m3

    area = (profile or {}).get('area')
    # If area is likely in mm2, convert to m2
    area_m2 = None
    if isinstance(area, (int, float)):
        area_m2 = (area / 1_000_000.0) if area > 1000 else area

    volume_m3 = None
    if area_m2 is not None and length_m is not None:
        try:
            volume_m3 = area_m2 * length_m
        except Exception:
            volume_m3 = None

    return {
        "type": "IfcBeam",
        "id": member.get('id') or _new_guid(),
        "name": f"Beam-{member.get('id', 'Unknown')[:8]}",
        "length": length_m,
        "profile": profile,
        "start": start_m,
        "end": end_m,
        "material": material,
        "placement": {
            "location": start_m,
            "axis": member.get('dir'),
            "ref_direction": [1.0, 0.0, 0.0]
        },
        "representation": {
            "profile_name": (profile or {}).get('name'),
            "profile_type": (profile or {}).get('type'),
            "swept_area": area_m2
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
        "quantities": {
            "Length": length_m,
            "CrossSectionArea": area_m2,
            "GrossVolume": volume_m3,
            "NetVolume": volume_m3
        }
    }

def generate_ifc_column(member: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC column with all required properties."""
    start_m = _vec_to_metres(member.get('start'))
    end_m = _vec_to_metres(member.get('end'))
    length_m = _to_metres(member.get('length'))

    profile = member.get('profile') or member.get('geom') or {}
    material = member.get('material') or {}
    material.setdefault('name', 'S235')
    material.setdefault('E', 210000.0)
    material.setdefault('density', 7850.0)

    area = (profile or {}).get('area')
    area_m2 = None
    if isinstance(area, (int, float)):
        area_m2 = (area / 1_000_000.0) if area > 1000 else area

    volume_m3 = None
    if area_m2 is not None and length_m is not None:
        try:
            volume_m3 = area_m2 * length_m
        except Exception:
            volume_m3 = None

    return {
        "type": "IfcColumn",
        "id": member.get('id') or _new_guid(),
        "name": f"Column-{member.get('id', 'Unknown')[:8]}",
        "length": length_m,
        "profile": profile,
        "start": start_m,
        "end": end_m,
        "material": material,
        "placement": {
            "location": start_m,
            "axis": member.get('dir'),
            "ref_direction": [1.0, 0.0, 0.0]
        },
        "representation": {
            "profile_name": (profile or {}).get('name'),
            "profile_type": (profile or {}).get('type'),
            "swept_area": area_m2
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
        "quantities": {
            "Length": length_m,
            "CrossSectionArea": area_m2,
            "GrossVolume": volume_m3,
            "NetVolume": volume_m3
        }
    }

def generate_ifc_plate(plate: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC plate with all required properties."""
    return {
        "type": "IfcPlate",
        "id": plate.get('id') or _new_guid(),
        "name": f"Plate-{plate.get('id', 'Unknown')[:8]}",
        "outline": plate.get('outline'),
        "thickness": plate.get('thickness'),
        "material": plate.get('material'),
        "placement": {
            "location": plate.get('position') or [0, 0, 0],
            "axis": [0, 0, 1],
            "ref_direction": [1, 0, 0]
        },
        "property_sets": {
            "Pset_PlateCommon": {
                "Reference": plate.get('id'),
                "LoadBearing": True
            }
        }
    }

def generate_ifc_fastener(bolt: Dict[str,Any]) -> Dict[str,Any]:
    """Generate complete IFC fastener with all required properties."""
    return {
        "type": "IfcFastener",
        "id": bolt.get('id') or _new_guid(),
        "name": f"Bolt-{bolt.get('id', 'Unknown')[:8]}",
        "diameter": bolt.get('diameter'),
        "position": bolt.get('pos') or bolt.get('position'),
        "grade": bolt.get('grade', 'A325'),
        "property_sets": {
            "Pset_FastenerCommon": {
                "NominalDiameter": bolt.get('diameter'),
                "Grade": bolt.get('grade', 'A325')
            }
        }
    }

def export_ifc_model(members: List[Dict[str,Any]], plates: List[Dict[str,Any]], bolts: List[Dict[str,Any]]) -> Dict[str,Any]:
    """
    Export IFC model with complete spatial structure and metadata.
    
    FIXED: Now correctly classifies members using 'layer' field instead of non-existent 'role' field.
    - Members with layer='COLUMNS' → IfcColumn
    - Members with layer='BEAMS' → IfcBeam
    - Vertical members (dir[2] > 0.9) → IfcColumn (fallback)
    """
    # Initialize model with complete structure
    model = {
        "schema": "IFC4",
        "project": {
            "id": _new_guid(),
            "name": "Steel Structure Project",
            "description": "Automated DXF to IFC conversion"
        },
        "site": {
            "id": _new_guid(),
            "name": "Construction Site",
            "elevation": 0.0
        },
        "building": {
            "id": _new_guid(),
            "name": "Building",
            "elevation_of_ref_height": 0.0,
            "elevation_of_terrain": 0.0
        },
        "storey": {
            "id": _new_guid(),
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
            "version": "2.0.0"
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
    
    # Classify members correctly using 'layer' field
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
            # Add spatial containment relationship
            model['relationships']['spatial_containment'].append({
                "element_id": ifc_element['id'],
                "element_type": "IfcColumn",
                "contained_in": model['storey']['id'],
                "container_type": "IfcBuildingStorey"
            })
        else:
            ifc_element = generate_ifc_beam(m)
            model['beams'].append(ifc_element)
            # Add spatial containment relationship
            model['relationships']['spatial_containment'].append({
                "element_id": ifc_element['id'],
                "element_type": "IfcBeam",
                "contained_in": model['storey']['id'],
                "container_type": "IfcBuildingStorey"
            })
    
    # Process plates
    for p in plates:
        ifc_plate = generate_ifc_plate(p)
        model['plates'].append(ifc_plate)
        model['relationships']['spatial_containment'].append({
            "element_id": ifc_plate['id'],
            "element_type": "IfcPlate",
            "contained_in": model['storey']['id'],
            "container_type": "IfcBuildingStorey"
        })
    
    # Process fasteners
    for b in bolts:
        ifc_fastener = generate_ifc_fastener(b)
        model['fasteners'].append(ifc_fastener)
    
    # Add summary statistics
    model['summary'] = {
        "total_columns": len(model['columns']),
        "total_beams": len(model['beams']),
        "total_plates": len(model['plates']),
        "total_fasteners": len(model['fasteners']),
        "total_elements": len(model['columns']) + len(model['beams']) + len(model['plates']) + len(model['fasteners'])
    }
    
    return model
