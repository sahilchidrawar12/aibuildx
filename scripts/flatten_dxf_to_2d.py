#!/usr/bin/env python3
"""Flatten a 3D DXF into a 2D DXF plan view.

This script preserves the input DXF geometry and layer names, projects all 3D coordinates to XY,
and writes a clean 2D DXF that matches the original 3D geometry in plan.
"""

import argparse
import math
from pathlib import Path
from typing import Iterable, Tuple


def _project_point(point) -> Tuple[float, float, float]:
    if point is None:
        return 0.0, 0.0, 0.0
    if hasattr(point, 'x') and hasattr(point, 'y'):
        return float(point.x), float(point.y), 0.0
    if isinstance(point, (list, tuple)) and len(point) >= 2:
        return float(point[0]), float(point[1]), 0.0
    return 0.0, 0.0, 0.0


def _project_points(points):
    return [_project_point(p) for p in points]


def _copy_layer(doc, out_doc, layer_name):
    if layer_name in out_doc.layers:
        return
    source_layer = doc.layers.get(layer_name)
    if source_layer is None:
        out_doc.layers.new(name=layer_name)
        return
    attribs = {
        'color': source_layer.dxf.color,
        'linetype': source_layer.dxf.linetype,
    }
    out_doc.layers.new(name=layer_name, dxfattribs={k: v for k, v in attribs.items() if v is not None})


def _copy_style(doc, out_doc, style_name):
    if style_name in out_doc.styles or style_name in ('Standard', None):
        return
    source_style = doc.styles.get(style_name)
    if source_style is None:
        return
    out_doc.styles.new(style_name)


def _copy_linetype(doc, out_doc, linetype_name):
    if linetype_name in out_doc.linetypes or linetype_name in ('BYLAYER', 'BYBLOCK', None):
        return
    try:
        out_doc.linetypes.new(linetype_name)
    except Exception:
        pass


def _explode_insert(entity, doc):
    block_name = entity.dxf.name
    try:
        block = doc.blocks.get(block_name)
    except Exception:
        return []

    if block is None:
        return []

    insert = _project_point(entity.dxf.insert)
    rotation = float(getattr(entity.dxf, 'rotation', 0.0) or 0.0)
    scale = (
        float(getattr(entity.dxf, 'xscale', 1.0) or 1.0),
        float(getattr(entity.dxf, 'yscale', 1.0) or 1.0),
        float(getattr(entity.dxf, 'zscale', 1.0) or 1.0)
    )

    exploded = []
    for sub in block:
        if sub.dxftype() == 'INSERT':
            exploded.extend(_explode_insert(sub, doc))
            continue
        exploded.append((sub, insert, rotation, scale))
    return exploded


def _transform_point(pt, insert, rotation, scale):
    x = pt[0] * scale[0]
    y = pt[1] * scale[1]
    theta = rotation * 3.141592653589793 / 180.0
    x_rot = x * math.cos(theta) - y * math.sin(theta)
    y_rot = x * math.sin(theta) + y * math.cos(theta)
    return x_rot + insert[0], y_rot + insert[1], 0.0


def _add_text(out_msp, entity, layer):
    insert = _project_point(entity.dxf.insert if hasattr(entity.dxf, 'insert') else entity.insert)
    text_value = entity.dxf.text if entity.dxftype() == 'TEXT' else entity.text
    height = float(getattr(entity.dxf, 'height', 250.0) or 250.0)
    out_msp.add_text(str(text_value), dxfattribs={
        'layer': layer,
        'height': height,
        'style': getattr(entity.dxf, 'style', 'Standard'),
        'rotation': float(getattr(entity.dxf, 'rotation', 0.0) or 0.0)
    }).set_pos(insert, align='LEFT')


def flatten_dxf(input_path: Path, output_path: Path) -> None:
    try:
        import ezdxf
    except ImportError as exc:
        raise ImportError("ezdxf is required to run this script. Install with: pip install ezdxf") from exc

    doc = ezdxf.readfile(str(input_path))
    out_doc = ezdxf.new('R2010')
    if 'Standard' not in out_doc.styles:
        out_doc.styles.new('Standard')

    for layer in doc.layers:
        if layer.dxf.name not in out_doc.layers:
            _copy_layer(doc, out_doc, layer.dxf.name)

    modelspace = doc.modelspace()
    out_msp = out_doc.modelspace()

    def add_line(start, end, layer):
        out_msp.add_line(start[:2], end[:2], dxfattribs={'layer': layer})

    def add_circle(center, radius, layer):
        out_msp.add_circle(center[:2], radius, dxfattribs={'layer': layer})

    import math

    for entity in modelspace:
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0'
        etype = entity.dxftype()

        if etype == 'LINE':
            start = _project_point(entity.dxf.start)
            end = _project_point(entity.dxf.end)
            add_line(start, end, layer)

        elif etype in ('LWPOLYLINE', 'POLYLINE'):
            pts = []
            if hasattr(entity, 'get_points'):
                pts = [p for p in entity.get_points('xy')]
            elif hasattr(entity, 'vertices'):
                pts = [p for p in entity.vertices()]
            pts2d = [_project_point(p) for p in pts]
            if len(pts2d) >= 2:
                for i in range(len(pts2d) - 1):
                    add_line(pts2d[i], pts2d[i + 1], layer)
                closed = False
                try:
                    closed = bool(entity.closed)
                except Exception:
                    try:
                        closed = bool(int(entity.dxf.flags) & 1)
                    except Exception:
                        closed = False
                if closed:
                    add_line(pts2d[-1], pts2d[0], layer)

        elif etype == 'CIRCLE':
            center = _project_point(entity.dxf.center)
            add_circle(center, float(entity.dxf.radius), layer)

        elif etype == 'ARC':
            center = _project_point(entity.dxf.center)
            radius = float(entity.dxf.radius)
            start_angle = float(entity.dxf.start_angle)
            end_angle = float(entity.dxf.end_angle)
            if end_angle <= start_angle:
                end_angle += 360
            segments = max(8, int(abs(end_angle - start_angle) / 10))
            points = []
            for step in range(segments + 1):
                angle = math.radians(start_angle + (end_angle - start_angle) * step / segments)
                points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle), 0.0))
            for i in range(len(points) - 1):
                add_line(points[i], points[i + 1], layer)

        elif etype == 'ELLIPSE':
            center = _project_point(entity.dxf.center)
            major = _project_point(entity.dxf.major_axis)
            ratio = float(entity.dxf.ratio)
            u = math.hypot(major[0], major[1])
            if u == 0:
                continue
            ux, uy = major[0] / u, major[1] / u
            vx, vy = -uy, ux
            segments = 64
            pts = []
            for i in range(segments + 1):
                t = 2 * math.pi * i / segments
                pts.append((center[0] + u * (ux * math.cos(t) + vx * ratio * math.sin(t)),
                            center[1] + u * (uy * math.cos(t) + vy * ratio * math.sin(t)),
                            0.0))
            for i in range(len(pts) - 1):
                add_line(pts[i], pts[i + 1], layer)

        elif etype in ('POINT',):
            point = _project_point(entity.dxf.location if hasattr(entity.dxf, 'location') else entity.dxf.position)
            out_msp.add_point(point[:2], dxfattribs={'layer': layer})

        elif etype in ('TEXT', 'MTEXT'):
            _add_text(out_msp, entity, layer)

        elif etype == '3DFACE':
            pts = [_project_point(entity.dxf.vtx0), _project_point(entity.dxf.vtx1), _project_point(entity.dxf.vtx2)]
            if hasattr(entity.dxf, 'vtx3'):
                pts.append(_project_point(entity.dxf.vtx3))
            for i in range(len(pts)):
                add_line(pts[i], pts[(i + 1) % len(pts)], layer)

        elif etype == 'SOLID':
            pts = [_project_point(entity.dxf.vtx0), _project_point(entity.dxf.vtx1), _project_point(entity.dxf.vtx2), _project_point(entity.dxf.vtx3)]
            for i in range(len(pts)):
                add_line(pts[i], pts[(i + 1) % len(pts)], layer)

        elif etype == 'INSERT':
            for sub_entity, insert_point, rotation, scale in _explode_insert(entity, doc):
                sub_layer = sub_entity.dxf.layer if hasattr(sub_entity.dxf, 'layer') else layer
                if sub_entity.dxftype() == 'LINE':
                    start = _transform_point(_project_point(sub_entity.dxf.start), insert_point, rotation, scale)
                    end = _transform_point(_project_point(sub_entity.dxf.end), insert_point, rotation, scale)
                    add_line(start, end, sub_layer)
                elif sub_entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                    points = [p for p in sub_entity.get_points('xy')] if hasattr(sub_entity, 'get_points') else [v for v in sub_entity.vertices()]
                    pts2d = [_transform_point(_project_point(p), insert_point, rotation, scale) for p in points]
                    for i in range(len(pts2d) - 1):
                        add_line(pts2d[i], pts2d[i + 1], sub_layer)
                    closed = False
                    try:
                        closed = bool(sub_entity.closed)
                    except Exception:
                        try:
                            closed = bool(int(sub_entity.dxf.flags) & 1)
                        except Exception:
                            closed = False
                    if closed and len(pts2d) >= 2:
                        add_line(pts2d[-1], pts2d[0], sub_layer)

        else:
            # Preserve unknown entity types by projecting key geometry when possible
            try:
                if hasattr(entity, 'vertices'):
                    pts = [p for p in entity.vertices()]
                    pts2d = [_project_point(p) for p in pts]
                    for i in range(len(pts2d) - 1):
                        add_line(pts2d[i], pts2d[i + 1], layer)
            except Exception:
                continue

    out_doc.saveas(str(output_path))


def main():
    parser = argparse.ArgumentParser(description='Flatten 3D DXF to 2D plan DXF.')
    parser.add_argument('input', help='Input 3D DXF file')
    parser.add_argument('output', help='Output flattened 2D DXF file')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input DXF not found: {input_path}")

    flatten_dxf(input_path, output_path)
    print(f"✅ Flattened 2D DXF created: {output_path}")


if __name__ == '__main__':
    main()
