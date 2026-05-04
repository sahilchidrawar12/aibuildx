"""
Modern DXF parser for the modular pipeline.
Extracts geometric entities from DXF files and converts them to the pipeline format.
"""
import os
import uuid
import math
from typing import List, Dict, Any, Optional
from math import cos, sin, pi


def _to_xyz(point: Any) -> List[float]:
    if point is None:
        return [0.0, 0.0, 0.0]
    if hasattr(point, 'x') and hasattr(point, 'y'):
        z = getattr(point, 'z', 0.0)
        return [float(point.x), float(point.y), float(z)]
    if isinstance(point, (list, tuple)) and len(point) >= 2:
        z = float(point[2]) if len(point) > 2 else 0.0
        return [float(point[0]), float(point[1]), z]
    return [0.0, 0.0, 0.0]


def _transform_point(point: List[float], insert: List[float], rotation: float, scale: List[float]) -> List[float]:
    x = point[0] * scale[0]
    y = point[1] * scale[1]
    z = point[2] * scale[2]
    theta = math.radians(rotation or 0.0)
    x_rot = x * cos(theta) - y * sin(theta)
    y_rot = x * sin(theta) + y * cos(theta)
    return [x_rot + insert[0], y_rot + insert[1], z + insert[2]]


def _line_distance(point: List[float], p0: List[float], p1: List[float]) -> float:
    vx = [p1[i] - p0[i] for i in range(3)]
    wx = [point[i] - p0[i] for i in range(3)]
    lensq = sum(v * v for v in vx)
    if lensq == 0:
        return math.dist(point, p0)
    t = max(0.0, min(1.0, sum(wx[i] * vx[i] for i in range(3)) / lensq))
    closest = [p0[i] + t * vx[i] for i in range(3)]
    return math.dist(point, closest)


def _explode_block_reference(entity: Any, doc: Any, transform: Optional[Dict[str, Any]] = None, depth: int = 0) -> List[Any]:
    if depth >= 4 or transform is None:
        return []
    try:
        block_name = entity.dxf.name
        block = doc.blocks.get(block_name)
    except Exception:
        return []
    if block is None:
        return []

    insert = _to_xyz(entity.dxf.insert)
    rotation = float(getattr(entity.dxf, 'rotation', 0.0) or 0.0)
    scale = [
        float(getattr(entity.dxf, 'xscale', 1.0) or 1.0),
        float(getattr(entity.dxf, 'yscale', 1.0) or 1.0),
        float(getattr(entity.dxf, 'zscale', 1.0) or 1.0)
    ]

    exploded = []
    for sub in block:
        try:
            if sub.dxftype() == 'INSERT':
                exploded.extend(_explode_block_reference(sub, doc, transform, depth + 1))
                continue
        except Exception:
            pass
        exploded.append((sub, insert, rotation, scale))
    return exploded


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
    annotations = []

    def emit_line_segment(p1: List[float], p2: List[float], layer: str) -> None:
        entities.append({
            'type': 'LINE',
            'start': _to_xyz(p1),
            'end': _to_xyz(p2),
            'layer': layer
        })

    def extract_points(entity: Any, mode: str = 'xyz') -> List[List[float]]:
        pts = []
        try:
            pts = [list(_to_xyz(p)) for p in entity.get_points(mode)]
        except Exception:
            try:
                pts = [list(_to_xyz(v.dxf.location if hasattr(v, 'dxf') else v)) for v in entity.vertices()]
            except Exception:
                pts = []
        return pts

    for entity in modelspace:
        entity_type = entity.dxftype()
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'default'

        if entity_type == 'LINE':
            emit_line_segment(entity.dxf.start, entity.dxf.end, layer)

        elif entity_type == 'POLYLINE':
            pts = extract_points(entity, 'xyz')
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    emit_line_segment(pts[i], pts[i+1], layer)
                is_closed = False
                try:
                    is_closed = bool(entity.closed)
                except Exception:
                    try:
                        is_closed = bool(entity.dxf.flags & 1)
                    except Exception:
                        is_closed = False
                if is_closed:
                    emit_line_segment(pts[-1], pts[0], layer)

        elif entity_type == 'LWPOLYLINE':
            pts = extract_points(entity, 'xyz')
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    emit_line_segment(pts[i], pts[i+1], layer)
                is_closed = False
                try:
                    is_closed = bool(entity.closed)
                except Exception:
                    try:
                        is_closed = bool(entity.dxf.flags & 1)
                    except Exception:
                        is_closed = False
                if is_closed:
                    emit_line_segment(pts[-1], pts[0], layer)

        elif entity_type == 'POINT':
            try:
                center = _to_xyz(entity.dxf.location)
                circles.append({'type': 'CIRCLE', 'center': center, 'radius': 0.0, 'layer': layer})
            except Exception:
                pass

        elif entity_type == '3DFACE':
            try:
                vtx = entity.dxf
                pts = [_to_xyz(vtx.vtx0), _to_xyz(vtx.vtx1), _to_xyz(vtx.vtx2)]
                if hasattr(vtx, 'vtx3'):
                    pts.append(_to_xyz(vtx.vtx3))
                for i in range(len(pts)):
                    emit_line_segment(pts[i], pts[(i + 1) % len(pts)], layer)
            except Exception:
                pass

        elif entity_type == 'CIRCLE':
            try:
                center = _to_xyz(entity.dxf.center)
                circles.append({
                    'type': 'CIRCLE',
                    'center': center,
                    'radius': float(entity.dxf.radius),
                    'layer': layer
                })
            except Exception:
                pass

        elif entity_type == 'ARC':
            try:
                center = _to_xyz(entity.dxf.center)
                radius = float(entity.dxf.radius)
                start_angle = float(entity.dxf.start_angle) * pi / 180.0
                end_angle = float(entity.dxf.end_angle) * pi / 180.0
                if end_angle <= start_angle:
                    end_angle += 2 * pi
                sweep = end_angle - start_angle
                segments = max(8, int(abs(sweep) / (pi / 12)))
                pts = []
                for i in range(segments + 1):
                    t = start_angle + sweep * i / segments
                    pts.append([
                        center[0] + radius * cos(t),
                        center[1] + radius * sin(t),
                        center[2]
                    ])
                for i in range(len(pts) - 1):
                    emit_line_segment(pts[i], pts[i+1], layer)
            except Exception:
                pass

        elif entity_type == 'ELLIPSE':
            try:
                center = _to_xyz(entity.dxf.center)
                major = _to_xyz(entity.dxf.major_axis)
                ratio = float(entity.dxf.ratio)
                ux, uy = major[0], major[1]
                norm = math.hypot(ux, uy) or 1.0
                ux, uy = ux / norm, uy / norm
                vx, vy = -uy, ux
                segments = 64
                pts = []
                for i in range(segments + 1):
                    t = 2 * pi * i / segments
                    pts.append([
                        center[0] + norm * (ux * cos(t) + vx * ratio * sin(t)),
                        center[1] + norm * (uy * cos(t) + vy * ratio * sin(t)),
                        center[2]
                    ])
                for i in range(len(pts) - 1):
                    emit_line_segment(pts[i], pts[i+1], layer)
            except Exception:
                pass

        elif entity_type == 'SPLINE':
            try:
                pts = []
                try:
                    pts = [list(_to_xyz(p)) for p in entity.fit_points]
                except Exception:
                    pass
                if not pts:
                    try:
                        pts = [list(_to_xyz(p)) for p in entity.control_points]
                    except Exception:
                        pts = []
                if not pts:
                    try:
                        for v in entity.virtual_entities():
                            if v.dxftype() == 'LINE':
                                emit_line_segment(v.dxf.start, v.dxf.end, layer)
                    except Exception:
                        pass
                else:
                    for i in range(len(pts) - 1):
                        emit_line_segment(pts[i], pts[i+1], layer)
            except Exception:
                pass

        elif entity_type in ('TEXT', 'MTEXT'):
            try:
                text_value = entity.dxf.text if entity_type == 'TEXT' else entity.text
                insert = _to_xyz(entity.dxf.insert if hasattr(entity.dxf, 'insert') else entity.insert)
                annotations.append({'text': str(text_value), 'position': insert, 'layer': layer})
            except Exception:
                pass

        elif entity_type == 'INSERT':
            try:
                for sub, insert, rotation, scale in _explode_block_reference(entity, doc, transform={'active': True}):
                    sub_layer = sub.dxf.layer if hasattr(sub.dxf, 'layer') else layer
                    sub_type = sub.dxftype()
                    if sub_type == 'LINE':
                        start = _transform_point(_to_xyz(sub.dxf.start), insert, rotation, scale)
                        end = _transform_point(_to_xyz(sub.dxf.end), insert, rotation, scale)
                        emit_line_segment(start, end, sub_layer)
                    elif sub_type in ('POLYLINE', 'LWPOLYLINE'):
                        try:
                            pts = [
                                _transform_point(_to_xyz(p), insert, rotation, scale)
                                for p in sub.get_points('xyz')
                            ]
                        except Exception:
                            pts = []
                        for i in range(len(pts) - 1):
                            emit_line_segment(pts[i], pts[i+1], sub_layer)
                        is_closed = False
                        try:
                            is_closed = bool(sub.closed)
                        except Exception:
                            try:
                                is_closed = bool(sub.dxf.flags & 1)
                            except Exception:
                                is_closed = False
                        if is_closed and len(pts) >= 2:
                            emit_line_segment(pts[-1], pts[0], sub_layer)
                    elif sub_type == 'CIRCLE':
                        center = _transform_point(_to_xyz(sub.dxf.center), insert, rotation, scale)
                        circles.append({'type': 'CIRCLE', 'center': center, 'radius': float(sub.dxf.radius), 'layer': sub_layer})
            except Exception:
                pass

    # Assign annotations to nearest members if text is close enough
    if annotations and entities:
        for ann in annotations:
            best_member = None
            best_distance = float('inf')
            for ent in entities:
                dist = _line_distance(ann['position'], ent['start'], ent['end'])
                if dist < best_distance:
                    best_distance = dist
                    best_member = ent
            if best_member is not None and best_distance <= 100.0:
                existing = best_member.get('annotation', '')
                annex = ann['text'].strip()
                if existing:
                    best_member['annotation'] = f"{existing}; {annex}"
                else:
                    best_member['annotation'] = annex

    members = []
    for ent in entities:
        member = {
            'id': str(uuid.uuid4()),
            'start': ent['start'],
            'end': ent['end'],
            'length': _calculate_length(ent['start'], ent['end']),
            'layer': ent.get('layer', 'default')
        }
        if 'annotation' in ent:
            member['annotation'] = ent['annotation']
        members.append(member)
    
    result = {'members': members, 'circles': circles}
    if annotations:
        result['annotations'] = annotations
    return result


def _calculate_length(p0: List[float], p1: List[float]) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(
        (p1[0] - p0[0])**2 + 
        (p1[1] - p0[1])**2 + 
        (p1[2] - p0[2])**2
    )
