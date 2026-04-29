#!/usr/bin/env python3
"""
Generate Bird's Nest Stadium DXF (Beijing National Stadium)
Pipeline-compatible with iconic interwoven steel lattice structure.

Features:
- Elliptical outer ring and inner compression ring
- Interwoven diagonal lattice members creating the "nest" effect
- Radial supports connecting inner and outer rings
- Multiple elevation levels with proper 3D geometry
- Clean layers, mm units, strategic markers for joint detection
"""

import math
from math import sin, cos, pi, sqrt
import ezdxf

SCALE = 1000.0  # meters to mm


def _add_line(msp, a, b, layer):
    """Add a 3D line to the modelspace."""
    msp.add_line(a, b, dxfattribs={"layer": layer})


def _add_circle(msp, center, radius, layer, color=None):
    """Add a marker circle for joint detection."""
    ent = msp.add_circle(center=center, radius=radius, dxfattribs={"layer": layer})
    if color is not None:
        ent.dxf.color = color


def generate_birds_nest_stadium(filename="test_birds_nest_stadium.dxf"):
    """
    Generate the Bird's Nest Stadium structure.
    
    Geometry:
    - Outer elliptical ring: ~330m x 220m (major x minor axis)
    - Inner compression ring: ~200m x 130m
    - Height variation: 0m to 70m
    - Interwoven lattice with varying angles and elevations
    """
    dxf = ezdxf.new(dxfversion="R2000")
    msp = dxf.modelspace()

    # Create layers
    for layer in ["COLUMNS", "BEAMS", "BRACING", "LATTICE", "GRIDS", "MARKERS"]:
        if layer not in dxf.layers:
            dxf.layers.add(name=layer)

    # Stadium parameters (scaled to mm)
    outer_major = 165 * SCALE  # 165m half major axis
    outer_minor = 110 * SCALE  # 110m half minor axis
    inner_major = 100 * SCALE  # 100m half major axis
    inner_minor = 65 * SCALE   # 65m half minor axis
    
    base_height = 0.0
    max_height = 70 * SCALE  # 70m max height
    mid_height = 35 * SCALE  # 35m mid height
    
    # Number of segments around the ellipse
    n_segments = 32  # Sufficient resolution for the lattice
    
    # Generate outer ring nodes at varying heights (wave pattern)
    outer_nodes_base = []
    outer_nodes_top = []
    for i in range(n_segments):
        angle = 2 * pi * i / n_segments
        x_outer = outer_major * cos(angle)
        y_outer = outer_minor * sin(angle)
        
        # Height varies sinusoidally to create wave effect
        h_base = base_height
        h_top = mid_height + (max_height - mid_height) * (0.5 + 0.5 * sin(4 * angle))
        
        outer_nodes_base.append((x_outer, y_outer, h_base))
        outer_nodes_top.append((x_outer, y_outer, h_top))
    
    # Generate inner compression ring nodes
    inner_nodes_base = []
    inner_nodes_mid = []
    for i in range(n_segments):
        angle = 2 * pi * i / n_segments
        x_inner = inner_major * cos(angle)
        y_inner = inner_minor * sin(angle)
        
        h_base = base_height + 5 * SCALE  # Slightly elevated
        h_mid = mid_height - 5 * SCALE    # Below mid-height
        
        inner_nodes_base.append((x_inner, y_inner, h_base))
        inner_nodes_mid.append((x_inner, y_inner, h_mid))
    
    # 1. Ground-level outer ring (base structure)
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        _add_line(msp, outer_nodes_base[i], outer_nodes_base[i_next], layer="BEAMS")
    
    # 2. Top-level outer ring
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        _add_line(msp, outer_nodes_top[i], outer_nodes_top[i_next], layer="BEAMS")
    
    # 3. Vertical/near-vertical outer columns
    for i in range(n_segments):
        _add_line(msp, outer_nodes_base[i], outer_nodes_top[i], layer="COLUMNS")
    
    # 4. Inner compression ring at base and mid-level
    for i in range(n_segments):
        i_next = (i + 1) % n_segments
        _add_line(msp, inner_nodes_base[i], inner_nodes_base[i_next], layer="BEAMS")
        _add_line(msp, inner_nodes_mid[i], inner_nodes_mid[i_next], layer="BEAMS")
    
    # 5. Inner ring vertical supports
    for i in range(0, n_segments, 2):  # Every other node
        _add_line(msp, inner_nodes_base[i], inner_nodes_mid[i], layer="COLUMNS")
    
    # 6. Radial supports connecting inner to outer (like spokes)
    for i in range(0, n_segments, 4):  # Every 4th segment
        # Base level
        _add_line(msp, inner_nodes_base[i], outer_nodes_base[i], layer="BEAMS")
        # Mid-level to top
        _add_line(msp, inner_nodes_mid[i], outer_nodes_top[i], layer="BRACING")
    
    # 7. INTERWOVEN LATTICE - the iconic "nest" structure
    # Create criss-crossing diagonal members with varying angles and overlaps
    
    # Lattice pattern 1: Ascending spirals
    for i in range(n_segments):
        i_next_2 = (i + 2) % n_segments
        i_next_3 = (i + 3) % n_segments
        i_next_5 = (i + 5) % n_segments
        
        # Outer lattice: base to top with spiral offset
        _add_line(msp, outer_nodes_base[i], outer_nodes_top[i_next_3], layer="LATTICE")
        
        # Reverse spiral
        _add_line(msp, outer_nodes_base[i_next_2], outer_nodes_top[i], layer="LATTICE")
    
    # Lattice pattern 2: Diagonal cross-bracing at mid-height
    for i in range(0, n_segments, 2):
        i_next_4 = (i + 4) % n_segments
        i_next_6 = (i + 6) % n_segments
        
        # Mid-height point on outer ring
        mid_pt_i = (
            outer_nodes_base[i][0],
            outer_nodes_base[i][1],
            (outer_nodes_base[i][2] + outer_nodes_top[i][2]) / 2
        )
        mid_pt_next = (
            outer_nodes_base[i_next_4][0],
            outer_nodes_base[i_next_4][1],
            (outer_nodes_base[i_next_4][2] + outer_nodes_top[i_next_4][2]) / 2
        )
        
        # Cross diagonals creating weave effect
        _add_line(msp, mid_pt_i, outer_nodes_top[i_next_6], layer="LATTICE")
        _add_line(msp, mid_pt_i, outer_nodes_base[i_next_6], layer="LATTICE")
    
    # Lattice pattern 3: Inner-to-outer diagonal ties
    for i in range(0, n_segments, 3):
        i_offset = (i + 7) % n_segments
        
        # Connect inner mid-level to outer top at offset angles
        _add_line(msp, inner_nodes_mid[i], outer_nodes_top[i_offset], layer="LATTICE")
        
        # Reverse direction weave
        i_rev = (i + 11) % n_segments
        _add_line(msp, inner_nodes_base[i], outer_nodes_top[i_rev], layer="LATTICE")
    
    # Lattice pattern 4: Additional criss-cross for density
    for i in range(1, n_segments, 4):
        i_next_8 = (i + 8) % n_segments
        
        # Lower lattice
        _add_line(msp, outer_nodes_base[i], outer_nodes_top[i_next_8], layer="LATTICE")
        
        # Upper reverse lattice
        i_prev_5 = (i - 5) % n_segments
        _add_line(msp, outer_nodes_top[i], outer_nodes_base[i_prev_5], layer="LATTICE")
    
    # 8. Ground reference grid (sparse)
    grid_range = int(200 * SCALE)
    grid_step = int(40 * SCALE)
    for x in range(-grid_range, grid_range + 1, grid_step):
        _add_line(msp, (x, -grid_range, 0), (x, grid_range, 0), layer="GRIDS")
    for y in range(-grid_range, grid_range + 1, grid_step):
        _add_line(msp, (-grid_range, y, 0), (grid_range, y, 0), layer="GRIDS")
    
    # 9. Strategic markers for joint detection
    # Outer ring key points (every 8th node at base and top)
    for i in range(0, n_segments, 8):
        _add_circle(msp, outer_nodes_base[i], radius=800, layer="MARKERS", color=2)
        _add_circle(msp, outer_nodes_top[i], radius=800, layer="MARKERS", color=3)
    
    # Inner ring key points
    for i in range(0, n_segments, 8):
        _add_circle(msp, inner_nodes_base[i], radius=700, layer="MARKERS", color=4)
        _add_circle(msp, inner_nodes_mid[i], radius=700, layer="MARKERS", color=5)
    
    # Center axis marker
    _add_circle(msp, (0, 0, 0), radius=1000, layer="MARKERS", color=1)
    _add_circle(msp, (0, 0, max_height), radius=1000, layer="MARKERS", color=6)
    
    dxf.saveas(filename)
    print(f"✅ Created: {filename}")
    print(f"   Structure: Bird's Nest Stadium (Beijing National Stadium)")
    print(f"   Outer ring: {outer_major*2/SCALE:.0f}m x {outer_minor*2/SCALE:.0f}m ellipse")
    print(f"   Inner ring: {inner_major*2/SCALE:.0f}m x {inner_minor*2/SCALE:.0f}m ellipse")
    print(f"   Height: 0-{max_height/SCALE:.0f}m (wave pattern)")
    print(f"   Segments: {n_segments} around perimeter")
    print(f"   Layers: COLUMNS, BEAMS, BRACING, LATTICE, GRIDS, MARKERS")
    print(f"   Units: millimeters")
    return filename


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GENERATING BIRD'S NEST STADIUM DXF")
    print("=" * 80 + "\n")
    
    filename = generate_birds_nest_stadium()
    
    print("\n" + "=" * 80)
    print("✅ GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nOutput: {filename}")
    print("Ready for pipeline conversion.")
