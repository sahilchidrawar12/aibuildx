"""
Modern DXF parser for the modular pipeline.
Extracts geometric entities from DXF files and converts them to the pipeline format.
"""
import os
import uuid
import math
from typing import List, Dict, Any
from math import cos, sin, pi


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
    circles = []
    
    # Extract LINE entities and CIRCLE entities
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
                # Handle classic POLYLINE with vertices iterator
                pts = []
                try:
                    # ezdxf < 1.0 may expose .points(); prefer vertices for robustness
                    pts = list(entity.points())
                except Exception:
                    try:
                        pts = [[v.dxf.location.x, v.dxf.location.y, getattr(v.dxf.location, 'z', 0.0)] for v in entity.vertices()]
                    except Exception:
                        pts = []

                if len(pts) >= 2:
                    for i in range(len(pts) - 1):
                        p1, p2 = pts[i], pts[i+1]
                        entities.append({
                            'type': 'LINE',
                            'start': [p1[0], p1[1], p1[2] if len(p1) > 2 else 0.0],
                            'end': [p2[0], p2[1], p2[2] if len(p2) > 2 else 0.0],
                            'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                        })
                    # If closed polyline, connect last to first
                    try:
                        is_closed = bool(entity.dxf.flags & 1) if hasattr(entity.dxf, 'flags') else False
                    except Exception:
                        is_closed = False
                    if is_closed:
                        p1, p2 = pts[-1], pts[0]
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
                # Support both xy and xyz retrieval; default z=0
                try:
                    points = list(entity.get_points('xy'))
                except Exception:
                    points = [(p[0], p[1]) for p in getattr(entity, 'points', [])]

                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        p1, p2 = points[i], points[i+1]
                        entities.append({
                            'type': 'LINE',
                            'start': [p1[0], p1[1], 0.0],
                            'end': [p2[0], p2[1], 0.0],
                            'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                        })
                    # If closed, connect last to first
                    try:
                        is_closed = bool(entity.dxf.flags & 1) if hasattr(entity.dxf, 'flags') else False
                    except Exception:
                        is_closed = False
                    if is_closed:
                        p1, p2 = points[-1], points[0]
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
        
        # Extract CIRCLE entities (connection points)
        elif entity.dxftype() == 'CIRCLE':
            try:
                center = entity.dxf.center
                radius = entity.dxf.radius
                circles.append({
                    'type': 'CIRCLE',
                    'center': [center.x, center.y, center.z if hasattr(center, 'z') else 0.0],
                    'radius': radius,
                    'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                })
            except Exception:
                pass

        # Extract ARC entities (approximate with segments)
        elif entity.dxftype() == 'ARC':
            try:
                center = entity.dxf.center
                radius = float(entity.dxf.radius)
                start_angle = float(entity.dxf.start_angle) * pi / 180.0
                end_angle = float(entity.dxf.end_angle) * pi / 180.0
                z = center.z if hasattr(center, 'z') else 0.0
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                # Choose segments based on sweep
                sweep = abs(end_angle - start_angle)
                segments = max(8, int(sweep / (pi / 12)))  # ~15° per segment
                pts = []
                for i in range(segments + 1):
                    t = start_angle + (sweep * i / segments) * (1 if end_angle >= start_angle else -1)
                    x = center.x + radius * cos(t)
                    y = center.y + radius * sin(t)
                    pts.append([x, y, z])
                for i in range(len(pts) - 1):
                    entities.append({'type': 'LINE', 'start': pts[i], 'end': pts[i+1], 'layer': layer})
            except Exception:
                pass

        # Extract ELLIPSE entities (approximate with segments)
        elif entity.dxftype() == 'ELLIPSE':
            try:
                center = entity.dxf.center
                ratio = float(entity.dxf.ratio)
                major = entity.dxf.major_axis
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                z = center.z if hasattr(center, 'z') else 0.0
                # Build orthonormal basis
                ux, uy = major.x, major.y
                # Normalize major axis
                norm = (ux**2 + uy**2) ** 0.5 or 1.0
                ux, uy = ux / norm, uy / norm
                vx, vy = -uy, ux
                segments = 64
                pts = []
                for i in range(segments + 1):
                    t = 2 * pi * i / segments
                    x = center.x + norm * (ux * cos(t) + vx * ratio * sin(t))
                    y = center.y + norm * (uy * cos(t) + vy * ratio * sin(t))
                    pts.append([x, y, z])
                for i in range(len(pts) - 1):
                    entities.append({'type': 'LINE', 'start': pts[i], 'end': pts[i+1], 'layer': layer})
            except Exception:
                pass

        # Extract SPLINE entities (approximate by sampling)
        elif entity.dxftype() == 'SPLINE':
            try:
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'
                # Use ezdxf adaptive sampling if available
                pts = []
                try:
                    # fit points usually exist
                    pts = [[p.x, p.y, getattr(p, 'z', 0.0)] for p in entity.fit_points]
                except Exception:
                    pass
                if not pts:
                    try:
                        # control points fall back
                        pts = [[p.x, p.y, getattr(p, 'z', 0.0)] for p in entity.control_points]
                    except Exception:
                        pts = []
                # If still empty, try to flatten to polyline using virtual entities
                if not pts:
                    try:
                        for v in entity.virtual_entities():
                            if v.dxftype() == 'LINE':
                                s, e = v.dxf.start, v.dxf.end
                                entities.append({'type': 'LINE', 'start': [s.x, s.y, getattr(s, 'z', 0.0)], 'end': [e.x, e.y, getattr(e, 'z', 0.0)], 'layer': layer})
                    except Exception:
                        pass
                else:
                    for i in range(len(pts) - 1):
                        entities.append({'type': 'LINE', 'start': pts[i], 'end': pts[i+1], 'layer': layer})
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
    
    return {'members': members, 'circles': circles}


def _calculate_length(p0: List[float], p1: List[float]) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(
        (p1[0] - p0[0])**2 + 
        (p1[1] - p0[1])**2 + 
        (p1[2] - p0[2])**2
    )
