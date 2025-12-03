"""
Modern DXF parser for the modular pipeline.
Extracts geometric entities from DXF files and converts them to the pipeline format.
"""
import os
import uuid
import math
from typing import List, Dict, Any


def parse_dxf_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a DXF file and extract structural members.
    
    Args:
        file_path: Path to the DXF file
        
    Returns:
        Dictionary with 'members' list containing extracted entities
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DXF file not found: {file_path}")
    
    try:
        import ezdxf
    except ImportError:
        raise RuntimeError("ezdxf is required for DXF parsing. Install with: pip install ezdxf")
    
    # Read DXF file
    try:
        doc = ezdxf.readfile(file_path)
    except Exception as e:
        error_msg = str(e)
        if "Invalid group code" in error_msg or "DXFStructureError" in error_msg:
            raise RuntimeError(
                f"Invalid DXF file format. The file appears to be corrupted or contains non-DXF content. "
                f"Please ensure the file is a valid DXF file exported from CAD software. Error: {error_msg}"
            )
        else:
            raise RuntimeError(f"Failed to read DXF file: {error_msg}")
    
    modelspace = doc.modelspace()
    
    entities = []
    
    # Extract LINE entities
    for entity in modelspace:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            entities.append({
                'type': 'LINE',
                'start': [start.x, start.y, start.z],
                'end': [end.x, end.y, end.z],
                'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
            })
        
        # Extract POLYLINE entities
        elif entity.dxftype() == 'POLYLINE':
            try:
                points = list(entity.points())
                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        p1, p2 = points[i], points[i+1]
                        entities.append({
                            'type': 'LINE',
                            'start': [p1[0], p1[1], p1[2] if len(p1) > 2 else 0.0],
                            'end': [p2[0], p2[1], p2[2] if len(p2) > 2 else 0.0],
                            'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                        })
            except Exception:
                pass
        
        # Extract LWPOLYLINE entities
        elif entity.dxftype() == 'LWPOLYLINE':
            try:
                points = list(entity.get_points('xy'))
                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        p1, p2 = points[i], points[i+1]
                        entities.append({
                            'type': 'LINE',
                            'start': [p1[0], p1[1], 0.0],
                            'end': [p2[0], p2[1], 0.0],
                            'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                        })
            except Exception:
                pass
        
        # Extract 3DFACE entities (common in structural models)
        elif entity.dxftype() == '3DFACE':
            try:
                # Extract edges of the 3D face as lines
                vtx = entity.dxf
                points = [
                    [vtx.vtx0.x, vtx.vtx0.y, vtx.vtx0.z],
                    [vtx.vtx1.x, vtx.vtx1.y, vtx.vtx1.z],
                    [vtx.vtx2.x, vtx.vtx2.y, vtx.vtx2.z]
                ]
                if hasattr(vtx, 'vtx3'):
                    points.append([vtx.vtx3.x, vtx.vtx3.y, vtx.vtx3.z])
                
                # Create lines from face edges
                for i in range(len(points)):
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    entities.append({
                        'type': 'LINE',
                        'start': p1,
                        'end': p2,
                        'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                    })
            except Exception:
                pass
    
    # Convert entities to members format
    members = []
    for ent in entities:
        members.append({
            'id': str(uuid.uuid4()),
            'start': ent['start'],
            'end': ent['end'],
            'length': _calculate_length(ent['start'], ent['end']),
            'layer': ent.get('layer', 'default')
        })
    
    return {'members': members}


def _calculate_length(p0: List[float], p1: List[float]) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(
        (p1[0] - p0[0])**2 + 
        (p1[1] - p0[1])**2 + 
        (p1[2] - p0[2])**2
    )
