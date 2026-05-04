#!/usr/bin/env python3
"""
Generate 2 NEW HARD DXF structures (no reference to previous examples).
Both are Tekla/pipeline-friendly using 3D LINE geometry and clean layers.
- Units: millimeters (SCALE=1000)
- Layers: COLUMNS, BEAMS, BRACING, RIBS, ARCHES, GRIDS, MARKERS
- Connection markers: CIRCLEs at key nodes to help pipeline joint detection

Structures:
1) Twisted Atrium Tower + Podium (200m tower, 35 floors, twisted facade ribs, podium with ramps)
2) Tri-Span Stadium Hall (3 long-span arches, radial roof ribs, perimeter ring, truss ties)
"""

import math
import ezdxf
from math import sin, cos, pi

SCALE = 1000.0  # meters to millimeters


def _add_line(msp, a, b, layer):
    msp.add_line(a, b, dxfattribs={"layer": layer})


def _add_circle(msp, center, radius, layer, color=None):
    ent = msp.add_circle(center=center, radius=radius, dxfattribs={"layer": layer})
    if color is not None:
        ent.dxf.color = color


def generate_twisted_atrium_tower(filename="test_hard_1_twisted_atrium_tower.dxf"):
    dxf = ezdxf.new(dxfversion="R2000")
    msp = dxf.modelspace()

    # Define layers
    for layer in ["COLUMNS", "BEAMS", "BRACING", "RIBS", "GRIDS", "MARKERS"]:
        if layer not in dxf.layers:
            dxf.layers.add(name=layer)

    # Deduplicate markers to avoid excessive joints at the same location
    marker_seen = set()
    def add_marker(center, radius=600, layer="MARKERS", color=2, q=50.0):
        key = (round(center[0] / q) * q, round(center[1] / q) * q, round(center[2] / q) * q)
        if key in marker_seen:
            return
        marker_seen.add(key)
        _add_circle(msp, center, radius=radius, layer=layer, color=color)

    # Tower parameters (moderate to keep voxel grids reasonable)
    floors = 35
    floor_h = 5.5 * SCALE  # 5.5 m
    tower_h = floors * floor_h  # ~192.5 m

    core_w = 24 * SCALE  # 24 m square core
    perim_w = 48 * SCALE  # 48 m square perimeter

    # Core columns (4 corners)
    core_half = core_w / 2
    core_corners = [
        (core_half, core_half), (-core_half, core_half), (-core_half, -core_half), (core_half, -core_half)
    ]
    for (cx, cy) in core_corners:
        _add_line(msp, (cx, cy, 0), (cx, cy, tower_h), layer="COLUMNS")

    # Perimeter columns (8 corners of octagon-like perimeter)
    perim_half = perim_w / 2
    perim_pts = []
    for i in range(8):
        ang = 2 * pi * i / 8
        perim_pts.append((perim_half * cos(ang), perim_half * sin(ang)))
    for (px, py) in perim_pts:
        _add_line(msp, (px, py, 0), (px, py, tower_h), layer="COLUMNS")

    # Twisted facade ribs: each floor rotates a small angle around Z
    twist_per_floor = pi / 90  # 2 degrees per floor
    ribs_per_level = 12
    for f in range(0, floors, 2):
        z = f * floor_h
        z2 = min(tower_h, (f + 2) * floor_h)
        for i in range(ribs_per_level):
            base_ang = 2 * pi * i / ribs_per_level
            # radius transitions slightly with height for subtle taper
            r1 = perim_half * (0.95 + 0.05 * sin(f / 7))
            r2 = perim_half * (0.95 + 0.05 * sin((f + 2) / 7))
            ang1 = base_ang + f * twist_per_floor
            ang2 = base_ang + (f + 2) * twist_per_floor
            x1, y1 = r1 * cos(ang1), r1 * sin(ang1)
            x2, y2 = r2 * cos(ang2), r2 * sin(ang2)
            _add_line(msp, (x1, y1, z), (x2, y2, z2), layer="RIBS")

    # Floor edge beams (every 5 floors) forming rotated squares
    for f in range(0, floors, 5):
        z = f * floor_h
        ang = f * twist_per_floor
        s = perim_half
        # square corners rotated by ang
        sq = [
            ( s * cos(ang) - s * sin(ang),  s * sin(ang) + s * cos(ang)),
            (-s * cos(ang) - s * sin(ang), -s * sin(ang) + s * cos(ang)),
            (-s * cos(ang) + s * sin(ang), -s * sin(ang) - s * cos(ang)),
            ( s * cos(ang) + s * sin(ang),  s * sin(ang) - s * cos(ang)),
        ]
        for i in range(4):
            x1, y1 = sq[i]
            x2, y2 = sq[(i + 1) % 4]
            _add_line(msp, (x1, y1, z), (x2, y2, z), layer="BEAMS")

    # Roof ring beams at the top elevation for proper closure
    z_top = tower_h
    ang_top = floors * twist_per_floor
    s = perim_half
    sq_top = [
        ( s * cos(ang_top) - s * sin(ang_top),  s * sin(ang_top) + s * cos(ang_top)),
        (-s * cos(ang_top) - s * sin(ang_top), -s * sin(ang_top) + s * cos(ang_top)),
        (-s * cos(ang_top) + s * sin(ang_top), -s * sin(ang_top) - s * cos(ang_top)),
        ( s * cos(ang_top) + s * sin(ang_top),  s * sin(ang_top) - s * cos(ang_top)),
    ]
    for i in range(4):
        x1, y1 = sq_top[i]
        x2, y2 = sq_top[(i + 1) % 4]
        _add_line(msp, (x1, y1, z_top), (x2, y2, z_top), layer="BEAMS")
    # Roof cross ties for diaphragm action
    for a, b in [(0, 2), (1, 3)]:
        x1, y1 = sq_top[a]
        x2, y2 = sq_top[b]
        _add_line(msp, (x1, y1, z_top), (x2, y2, z_top), layer="BEAMS")

    # Atrium: two opposite sides have vertical braces forming X
    for f in range(0, floors - 5, 5):
        z1 = f * floor_h
        z2 = (f + 5) * floor_h
        # front face center (~+Y)
        p = perim_half * 0.98
        _add_line(msp, (-p, p, z1), (p, p, z2), layer="BRACING")
        _add_line(msp, (p, p, z1), (-p, p, z2), layer="BRACING")
        # back face (-Y)
        _add_line(msp, (-p, -p, z1), (p, -p, z2), layer="BRACING")
        _add_line(msp, (p, -p, z1), (-p, -p, z2), layer="BRACING")

    # Podium: 3 levels with ramps (helical quarter turns)
    podium_levels = [0, 8 * SCALE, 16 * SCALE]
    rad = 35 * SCALE
    for idx in range(2):
        z1 = podium_levels[idx]
        z2 = podium_levels[idx + 1]
        turns = 0.5
        steps = 36
        for i in range(steps):
            t1 = 2 * pi * (i / steps) * turns
            t2 = 2 * pi * ((i + 1) / steps) * turns
            x1, y1 = rad * cos(t1), rad * sin(t1)
            x2, y2 = rad * cos(t2), rad * sin(t2)
            zz1 = z1 + (z2 - z1) * (i / steps)
            zz2 = z1 + (z2 - z1) * ((i + 1) / steps)
            _add_line(msp, (x1, y1, zz1), (x2, y2, zz2), layer="BEAMS")

    # Ground reference grid removed to prevent unnecessary members/joints in pipeline
    # (Viewer provides its own grid; keeping model geometry clean.)

    # Markers only at ring-beam vertices (base and top) to avoid unnecessary joints
    def square_corners(angle):
        s = perim_half
        return [
            ( s * cos(angle) - s * sin(angle),  s * sin(angle) + s * cos(angle)),
            (-s * cos(angle) - s * sin(angle), -s * sin(angle) + s * cos(angle)),
            (-s * cos(angle) + s * sin(angle), -s * sin(angle) - s * cos(angle)),
            ( s * cos(angle) + s * sin(angle),  s * sin(angle) - s * cos(angle)),
        ]
    for corners, z_lev in [(square_corners(0.0), 0), (square_corners(ang_top), tower_h)]:
        for (px, py) in corners:
            add_marker((px, py, z_lev), radius=600, layer="MARKERS", color=2)

    dxf.saveas(filename)
    print(f"✅ Created: {filename} (Twisted Atrium Tower)")
    return filename


def generate_tri_span_stadium(filename="test_hard_2_tri_span_stadium.dxf"):
    dxf = ezdxf.new(dxfversion="R2000")
    msp = dxf.modelspace()

    # Define layers
    for layer in ["COLUMNS", "BEAMS", "BRACING", "RIBS", "ARCHES", "GRIDS", "MARKERS"]:
        if layer not in dxf.layers:
            dxf.layers.add(name=layer)

    # Hall footprint
    length = 220 * SCALE
    width = 140 * SCALE
    span_centers = [-70 * SCALE, 0, 70 * SCALE]  # three spans across width

    # Arches along length for each span (parabolic)
    arch_height = 48 * SCALE
    arch_steps = 40

    for cy in span_centers:
        # columns at ends
        for side in [-1, 1]:
            x = side * (length / 2)
            _add_line(msp, (x, cy, 0), (x, cy, arch_height * 0.2), layer="COLUMNS")
        # generate arch curve from -L/2 to +L/2
        pts = []
        for i in range(arch_steps + 1):
            t = -0.5 + i / arch_steps
            x = t * length
            z = arch_height * (1 - (2 * t) ** 2)  # parabola
            pts.append((x, cy, z))
        for i in range(len(pts) - 1):
            _add_line(msp, pts[i], pts[i + 1], layer="ARCHES")

    # Longitudinal roof ribs connecting arches along length
    rib_rows = 12
    for r in range(rib_rows):
        y = -width / 2 + (r + 0.5) * (width / rib_rows)
        # sample height at x for center span for gentle undulation
        for i in range(arch_steps):
            t1 = -0.5 + i / arch_steps
            t2 = -0.5 + (i + 1) / arch_steps
            x1 = t1 * length
            x2 = t2 * length
            z1 = arch_height * (1 - (2 * t1) ** 2) * (0.9 + 0.1 * sin(r * 0.5))
            z2 = arch_height * (1 - (2 * t2) ** 2) * (0.9 + 0.1 * sin(r * 0.5))
            _add_line(msp, (x1, y, z1), (x2, y, z2), layer="RIBS")

    # Perimeter ring beam
    halfL = length / 2
    halfW = width / 2
    corners = [(-halfL, -halfW), (halfL, -halfW), (halfL, halfW), (-halfL, halfW)]
    ring_z = 8 * SCALE
    for i in range(4):
        x1, y1 = corners[i]
        x2, y2 = corners[(i + 1) % 4]
        _add_line(msp, (x1, y1, ring_z), (x2, y2, ring_z), layer="BEAMS")

    # Cross-ties (bracing) between span arches at quarter points
    for cy in span_centers[:-1]:
        cy2 = cy + 70 * SCALE
        for frac in [0.25, 0.5, 0.75]:
            x = (-0.5 + frac) * length
            z = arch_height * (1 - (2 * (-0.5 + frac)) ** 2)
            _add_line(msp, (x, cy, z), (x, cy2, z * 0.98), layer="BRACING")

    # Short columns under ring beam (around perimeter every 20m)
    step = 20 * SCALE
    for x in range(-int(halfL), int(halfL) + 1, int(step)):
        _add_line(msp, (x, -halfW, 0), (x, -halfW, ring_z), layer="COLUMNS")
        _add_line(msp, (x, halfW, 0), (x, halfW, ring_z), layer="COLUMNS")
    for y in range(-int(halfW), int(halfW) + 1, int(step)):
        _add_line(msp, (-halfL, y, 0), (-halfL, y, ring_z), layer="COLUMNS")
        _add_line(msp, (halfL, y, 0), (halfL, y, ring_z), layer="COLUMNS")

    # Ground grids
    g = int(260 * SCALE)
    s = int(20 * SCALE)
    for x in range(-g, g + 1, s):
        _add_line(msp, (x, -g, 0), (x, g, 0), layer="GRIDS")
    for y in range(-g, g + 1, s):
        _add_line(msp, (-g, y, 0), (g, y, 0), layer="GRIDS")

    # Markers at arch crowns and quarter points
    for cy in span_centers:
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            t = -0.5 + frac
            x = t * length
            z = arch_height * (1 - (2 * t) ** 2)
            _add_circle(msp, (x, cy, z), radius=800, layer="MARKERS", color=3)

    dxf.saveas(filename)
    print(f"✅ Created: {filename} (Tri-Span Stadium Hall)")
    return filename


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GENERATING 2 NEW HARD DXF STRUCTURES")
    print("=" * 70 + "\n")
    f1 = generate_twisted_atrium_tower()
    f2 = generate_tri_span_stadium()
    print("\n" + "=" * 70)
    print("✅ NEW HARD DXF GENERATION COMPLETE")
    print("=" * 70)
