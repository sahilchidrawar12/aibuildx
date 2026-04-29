#!/usr/bin/env python3
"""
Generate 2 pipeline-compatible DXF structures:
1) 20-Floor Square Tower (clean core/perimeter columns, floor beams, face bracing)
2) Pyramid-like Space Frame (tiered ring beams, sloped edges to apex)

Conventions:
- Units: millimeters (SCALE=1000)
- Geometry: 3D LINE entities (no solids), CIRCLE markers aid joint detection
- Layers: COLUMNS, BEAMS, BRACING, GRIDS, MARKERS
"""

import math
from math import sin, cos, pi
import ezdxf

SCALE = 1000.0  # meters to mm


def _add_line(msp, a, b, layer):
    msp.add_line(a, b, dxfattribs={"layer": layer})


def _add_circle(msp, center, radius, layer, color=None):
    ent = msp.add_circle(center=center, radius=radius, dxfattribs={"layer": layer})
    if color is not None:
        ent.dxf.color = color


def generate_20_floor_tower(filename="test_20_floor_tower.dxf"):
    dxf = ezdxf.new(dxfversion="R2000")
    msp = dxf.modelspace()

    # Layers
    for layer in ["COLUMNS", "BEAMS", "BRACING", "GRIDS", "MARKERS"]:
        if layer not in dxf.layers:
            dxf.layers.add(name=layer)

    # Tower parameters
    floors = 20
    floor_h = 3.6 * SCALE  # 3.6 m per floor
    h_total = floors * floor_h  # ~72 m

    core_w = 14 * SCALE  # 14 m square core
    perim_w = 40 * SCALE  # 40 m square perimeter
    core_half = core_w / 2
    perim_half = perim_w / 2

    # Core columns (4 corners)
    core_corners = [
        ( core_half,  core_half),
        (-core_half,  core_half),
        (-core_half, -core_half),
        ( core_half, -core_half),
    ]
    for (x, y) in core_corners:
        _add_line(msp, (x, y, 0), (x, y, h_total), layer="COLUMNS")

    # Perimeter columns (at 8 corners of a rotated octagon-like ring)
    perim_pts = []
    for i in range(8):
        ang = 2 * pi * i / 8
        perim_pts.append((perim_half * cos(ang), perim_half * sin(ang)))
    for (x, y) in perim_pts:
        _add_line(msp, (x, y, 0), (x, y, h_total), layer="COLUMNS")

    # Floor edge beams (every floor) forming squares
    for f in range(floors + 1):
        z = f * floor_h
        s = perim_half
        corners = [( s,  s), (-s,  s), (-s, -s), ( s, -s)]
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            _add_line(msp, (x1, y1, z), (x2, y2, z), layer="BEAMS")

    # Core-to-perimeter tie beams (every 2 floors)
    for f in range(0, floors + 1, 2):
        z = f * floor_h
        s = perim_half
        # Connect core midpoints to perimeter midpoints (4 directions)
        _add_line(msp, ( core_half, 0, z), ( s, 0, z), layer="BEAMS")
        _add_line(msp, (-core_half, 0, z), (-s, 0, z), layer="BEAMS")
        _add_line(msp, (0,  core_half, z), (0,  s, z), layer="BEAMS")
        _add_line(msp, (0, -core_half, z), (0, -s, z), layer="BEAMS")

    # Face X-bracing (two opposite faces) every 4 floors
    for f in range(0, floors - 3, 4):
        z1 = f * floor_h
        z2 = (f + 4) * floor_h
        p = perim_half
        # +Y face
        _add_line(msp, (-p, p, z1), ( p, p, z2), layer="BRACING")
        _add_line(msp, ( p, p, z1), (-p, p, z2), layer="BRACING")
        # -Y face
        _add_line(msp, (-p,-p, z1), ( p,-p, z2), layer="BRACING")
        _add_line(msp, ( p,-p, z1), (-p,-p, z2), layer="BRACING")

    # Ground reference (sparse grid)
    g = int(100 * SCALE)
    step = int(20 * SCALE)
    for x in range(-g, g + 1, step):
        _add_line(msp, (x, -g, 0), (x, g, 0), layer="GRIDS")
    for y in range(-g, g + 1, step):
        _add_line(msp, (-g, y, 0), (g, y, 0), layer="GRIDS")

    # Markers at base/top perimeter corners and roof center
    for (x, y) in [( perim_half,  perim_half), (-perim_half,  perim_half), (-perim_half, -perim_half), ( perim_half, -perim_half)]:
        for z in (0, h_total):
            _add_circle(msp, (x, y, z), radius=500, layer="MARKERS", color=2)
    _add_circle(msp, (0, 0, h_total), radius=600, layer="MARKERS", color=3)

    dxf.saveas(filename)
    print(f"✅ Created: {filename} (20-Floor Tower)")
    return filename


def generate_pyramid_spaceframe(filename="test_pyramid_spaceframe.dxf"):
    dxf = ezdxf.new(dxfversion="R2000")
    msp = dxf.modelspace()

    for layer in ["COLUMNS", "BEAMS", "BRACING", "GRIDS", "MARKERS"]:
        if layer not in dxf.layers:
            dxf.layers.add(name=layer)

    # Pyramid parameters
    base_size = 120 * SCALE  # 120 m square base
    half = base_size / 2
    levels = 12
    level_h = 6 * SCALE  # 6 m per tier
    apex_z = levels * level_h

    # Sloping edge "columns" from base corners to apex
    corners = [( half,  half), (-half,  half), (-half, -half), ( half, -half)]
    for (x, y) in corners:
        _add_line(msp, (x, y, 0), (0, 0, apex_z), layer="COLUMNS")

    # Tiered ring beams shrinking each level towards apex
    for lvl in range(levels + 1):
        z = lvl * level_h
        s = half * (1 - (lvl / levels))  # linear taper
        sq = [( s,  s), (-s,  s), (-s, -s), ( s, -s)]
        for i in range(4):
            x1, y1 = sq[i]
            x2, y2 = sq[(i + 1) % 4]
            _add_line(msp, (x1, y1, z), (x2, y2, z), layer="BEAMS")
        # cross-ties on alternate levels
        if lvl % 2 == 0:
            _add_line(msp, ( s,  s, z), (-s, -s, z), layer="BRACING")
            _add_line(msp, (-s,  s, z), ( s, -s, z), layer="BRACING")

    # Diagonals up faces connecting tiers (space frame effect)
    for lvl in range(levels - 1):
        z1 = lvl * level_h
        z2 = (lvl + 1) * level_h
        s1 = half * (1 - (lvl / levels))
        s2 = half * (1 - ((lvl + 1) / levels))
        face_edges_1 = [( s1,  s1), (-s1,  s1), (-s1, -s1), ( s1, -s1)]
        face_edges_2 = [( s2,  s2), (-s2,  s2), (-s2, -s2), ( s2, -s2)]
        for i in range(4):
            _add_line(msp, (face_edges_1[i][0], face_edges_1[i][1], z1), (face_edges_2[i][0], face_edges_2[i][1], z2), layer="BRACING")

    # Sparse ground grid
    g = int(160 * SCALE)
    step = int(20 * SCALE)
    for x in range(-g, g + 1, step):
        _add_line(msp, (x, -g, 0), (x, g, 0), layer="GRIDS")
    for y in range(-g, g + 1, step):
        _add_line(msp, (-g, y, 0), (g, y, 0), layer="GRIDS")

    # Markers at base corners, mid-tier corners, and apex
    for (x, y) in corners:
        _add_circle(msp, (x, y, 0), radius=800, layer="MARKERS", color=2)
    mid_lvl = levels // 2
    z_mid = mid_lvl * level_h
    s_mid = half * (1 - (mid_lvl / levels))
    for (x, y) in [( s_mid,  s_mid), (-s_mid,  s_mid), (-s_mid, -s_mid), ( s_mid, -s_mid)]:
        _add_circle(msp, (x, y, z_mid), radius=700, layer="MARKERS", color=3)
    _add_circle(msp, (0, 0, apex_z), radius=900, layer="MARKERS", color=4)

    dxf.saveas(filename)
    print(f"✅ Created: {filename} (Pyramid Space Frame)")
    return filename


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GENERATING 20-FLOOR TOWER AND PYRAMID DXFs")
    print("=" * 70 + "\n")
    f1 = generate_20_floor_tower()
    f2 = generate_pyramid_spaceframe()
    print("\n" + "=" * 70)
    print("✅ GENERATION COMPLETE")
    print("=" * 70)
