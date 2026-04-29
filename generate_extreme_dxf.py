#!/usr/bin/env python3
"""
Generate 4 EXTREME difficulty DXF files for pipeline robustness testing.
These DXF files represent real-world nightmare scenarios that break standard modelers.
"""

import ezdxf
import math
import numpy as np

# SCALE FACTOR: Disabled global scale-up. Use native units for all extreme DXFs.
# Only skyscraper (Burj/Twin) generators keep 1000:1 scale.
SCALE = 1.0

def create_offshore_pipe_rack():
    """
    OFFSHORE OIL & GAS PIPE RACK + MODULE SUPPORT
    - Multiple elevation mismatches in same grid
    - Skewed columns (non-orthogonal angles)
    - Pipe racks crossing different structural systems
    - Combined primary steel + secondary steel + bracings
    - No standard repetition
    """
    print("Generating: Offshore Oil & Gas Pipe Rack DXF...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # ========== MAIN GRID LAYOUT ==========
    # Plan view: 120m x 80m platform (scaled to mm for DXF)
    main_frame_nodes = [
        # Port side (primary)
        {"pos": (0*SCALE, 0*SCALE, 0*SCALE), "id": "P1"},
        {"pos": (30*SCALE, 0*SCALE, 0*SCALE), "id": "P2"},
        {"pos": (60*SCALE, 0*SCALE, 0*SCALE), "id": "P3"},
        {"pos": (120*SCALE, 0*SCALE, 0*SCALE), "id": "P4"},
        # Starboard side (primary)
        {"pos": (0*SCALE, 80*SCALE, 0*SCALE), "id": "S1"},
        {"pos": (30*SCALE, 80*SCALE, 0*SCALE), "id": "S2"},
        {"pos": (60*SCALE, 80*SCALE, 0.5*SCALE), "id": "S3"},  # ELEVATION MISMATCH #1
        {"pos": (120*SCALE, 80*SCALE, 0*SCALE), "id": "S4"},
    ]
    
    # ========== SKEWED COLUMNS (non-orthogonal) ==========
    # Columns at base with skew angles (leaning, not vertical)
    columns = []
    for node in main_frame_nodes:
        x, y, z = node["pos"]
        # Random skew: 2-5 degrees from vertical
        skew_angle = np.random.uniform(0.035, 0.087)  # rad = 2-5 deg
        skew_x = np.cos(skew_angle)
        skew_y = np.sin(skew_angle)
        
        # Column height varies: 20-35m
        col_height = 20 + (hash(node["id"]) % 15)
        
        # Top of column with skew offset
        top_x = x + skew_x * col_height * 0.15
        top_y = y + skew_y * col_height * 0.15
        
        columns.append({
            "id": node["id"],
            "base": (x, y, z),
            "top": (top_x, top_y, z + col_height),
            "height": col_height
        })
        
        # Draw skewed column
        msp.add_line((x, y, z), (top_x, top_y, z + col_height))
    
    # ========== ELEVATION-DEPENDENT BEAMS (Primary Steel) ==========
    primary_beams = [
        # Longitudinal (X-direction) with elevation changes
        {"start": main_frame_nodes[0]["pos"], "end": main_frame_nodes[1]["pos"]},
        {"start": main_frame_nodes[1]["pos"], "end": main_frame_nodes[2]["pos"]},
        {"start": main_frame_nodes[2]["pos"], "end": main_frame_nodes[3]["pos"]},
        
        {"start": main_frame_nodes[4]["pos"], "end": main_frame_nodes[5]["pos"]},
        {"start": main_frame_nodes[5]["pos"], "end": main_frame_nodes[6]["pos"]},  # MISMATCH #2
        {"start": main_frame_nodes[6]["pos"], "end": main_frame_nodes[7]["pos"]},
        
        # Transverse (Y-direction)
        {"start": main_frame_nodes[0]["pos"], "end": main_frame_nodes[4]["pos"]},
        {"start": main_frame_nodes[1]["pos"], "end": main_frame_nodes[5]["pos"]},
        {"start": main_frame_nodes[2]["pos"], "end": main_frame_nodes[6]["pos"]},
        {"start": main_frame_nodes[3]["pos"], "end": main_frame_nodes[7]["pos"]},
    ]
    
    for beam in primary_beams:
        msp.add_line(beam["start"], beam["end"])
    
    # ========== PIPE RACK (Secondary Steel at +12m elevation) ==========
    # Parallel pipe rack crossing main structure
    pipe_rack_height = 12 * SCALE
    pipe_rack_nodes = [
        (10*SCALE, 10*SCALE, pipe_rack_height),
        (110*SCALE, 10*SCALE, pipe_rack_height),
        (110*SCALE, 70*SCALE, pipe_rack_height + 0.8*SCALE),  # SLOPE
        (10*SCALE, 70*SCALE, pipe_rack_height),
    ]
    
    # Pipe rack primary beams
    msp.add_line(pipe_rack_nodes[0], pipe_rack_nodes[1])
    msp.add_line(pipe_rack_nodes[1], pipe_rack_nodes[2])
    msp.add_line(pipe_rack_nodes[2], pipe_rack_nodes[3])
    msp.add_line(pipe_rack_nodes[3], pipe_rack_nodes[0])
    
    # Pipe rack secondary grid (35 lines at 5m spacing)
    for i in range(0, 6):
        x_pos = 10 + i * 20
        msp.add_line((x_pos, 10, pipe_rack_height), (x_pos, 70, pipe_rack_height))
    
    for j in range(0, 7):
        y_pos = 10 + j * 10
        msp.add_line((10, y_pos, pipe_rack_height), (110, y_pos, pipe_rack_height + 0.12 * (y_pos - 10)))
    
    # ========== K-BRACING (Primary vertical system) ==========
    # 8 K-braces distributed across platform
    for i in range(1, 4):
        for j in range(1, 2):
            base_x = i * 30
            base_y = j * 40
            height_offset = 15
            
            # K-brace members (4 per K)
            braces = [
                # Left-Up
                ((base_x - 5, base_y - 5, 0), (base_x, base_y, height_offset)),
                # Right-Up
                ((base_x + 5, base_y - 5, 0), (base_x, base_y, height_offset)),
                # Left-Down
                ((base_x - 5, base_y + 5, 0), (base_x, base_y, height_offset)),
                # Right-Down
                ((base_x + 5, base_y + 5, 0), (base_x, base_y, height_offset)),
            ]
            
            for start, end in braces:
                msp.add_line(start, end)
    
    # ========== X-BRACING (Secondary vertical system - offset from K-braces) ==========
    for i in range(0, 4):
        for j in range(0, 2):
            base_x = 15 + i * 30
            base_y = 20 + j * 40
            
            # X-brace diagonals at different angles
            x_braces = [
                ((base_x - 8, base_y - 8, 2), (base_x + 8, base_y + 8, 18)),
                ((base_x + 8, base_y - 8, 2), (base_x - 8, base_y + 8, 18)),
            ]
            
            for start, end in x_braces:
                msp.add_line(start, end)
    
    # ========== COMPOUND ANGLE BEAMS (interconnecting at node) ==========
    # 5 beams converging at single node (nightmare for Tekla)
    junction_x, junction_y, junction_z = 60, 40, 12
    
    junction_endpoints = [
        (60, 40, 0),      # Vertical down
        (70, 45, 18),     # Up-forward-starboard
        (50, 35, 15),     # Up-aft-port
        (65, 55, 10),     # Up-forward at angle
        (55, 50, 14),     # Up-aft at angle
    ]
    
    for endpoint in junction_endpoints:
        msp.add_line((junction_x, junction_y, junction_z), endpoint)
    
    # ========== VARIABLE BEAM SIZES AT SAME ELEVATION ==========
    # 4 beams meeting at node with different cross-sections
    meeting_node = (90, 40, 10)
    
    meeting_beams = [
        ((85, 40, 10), meeting_node),  # 457x191x67 UB (large)
        ((95, 40, 10), meeting_node),  # 305x165x40 UB (medium)
        ((90, 35, 10), meeting_node),  # 254x102x28 UB (small)
        ((90, 45, 10), meeting_node),  # 406x178x54 UB (large)
    ]
    
    for start, end in meeting_beams:
        msp.add_line(start, end)
    
    # ========== EXPANSION JOINTS (marked with circles) ==========
    expansion_joints = [
        (40, 40, 8),
        (80, 40, 8),
        (40, 70, pipe_rack_height),
    ]
    
    for joint in expansion_joints:
        circle = msp.add_circle(center=joint, radius=2)
        circle.dxf.color = 5  # Red
    
    dxf.saveas('test_extreme_1_offshore_pipe_rack.dxf')
    print(f"✅ Created: test_extreme_1_offshore_pipe_rack.dxf ({len(msp)} entities)")


def create_curved_stadium_roof():
    """
    CURVED STEEL STADIUM ROOF / FREE-FORM CANOPY
    - No straight grids
    - Radial + spiral geometry
    - Variable section sizes
    - Changing roof slopes every grid line
    """
    print("Generating: Curved Stadium Roof DXF...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # ========== RADIAL GEOMETRY (Stadium bowl) ==========
    # Center: (0, 0, 0), Radius: 100m, 12 radial ribs (scaled to mm)
    center = (0, 0, 0)
    num_ribs = 12
    
    for rib_idx in range(num_ribs):
        angle = (rib_idx / num_ribs) * 2 * math.pi
        
        # Rib starts at radius 60m, ends at 100m (outer)
        inner_r = 60 * SCALE
        outer_r = 100 * SCALE
        
        # 8 nodes along radial line with increasing height
        rib_nodes = []
        for i in range(8):
            r = inner_r + (outer_r - inner_r) * (i / 7)
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            # Height increases non-linearly (parabolic roof)
            z = center[2] + 35*SCALE * (1 - ((r - inner_r) / (outer_r - inner_r)) ** 2)
            rib_nodes.append((x, y, z))
        
        # Draw rib members
        for i in range(len(rib_nodes) - 1):
            msp.add_line(rib_nodes[i], rib_nodes[i + 1])
    
    # ========== SPIRAL PURLINS (secondary grid) ==========
    # 7 concentric spiral rings with variable spacing
    num_rings = 7
    
    for ring_idx in range(num_rings):
        ring_radius = (60 + (100 - 60) * (ring_idx / (num_rings - 1))) * SCALE
        
        # Spiral: 6-12 points per ring (variable spacing = non-uniform)
        num_points = 6 + ring_idx  # More points as radius increases
        
        for point_idx in range(num_points):
            angle1 = (point_idx / num_points) * 2 * math.pi
            angle2 = ((point_idx + 1) % num_points) / num_points * 2 * math.pi
            
            # Height varies with radius AND spiral progression
            z1 = 35 * (1 - ((ring_radius - 60) / 40) ** 2) + ring_idx * 0.5
            z2 = 35 * (1 - ((ring_radius - 60) / 40) ** 2) + ring_idx * 0.5
            
            p1 = (center[0] + ring_radius * math.cos(angle1), 
                  center[1] + ring_radius * math.sin(angle1), z1)
            p2 = (center[0] + ring_radius * math.cos(angle2), 
                  center[1] + ring_radius * math.sin(angle2), z2)
            
            msp.add_line(p1, p2)
    
    # ========== TANGENT BEAMS (connect radial and spiral) ==========
    # Curved members connecting adjacent ribs
    for rib_idx in range(num_ribs):
        rib_next = (rib_idx + 1) % num_ribs
        angle1 = (rib_idx / num_ribs) * 2 * math.pi
        angle2 = (rib_next / num_ribs) * 2 * math.pi
        
        # Connect at 3 intermediate radii
        for r in [70, 80, 90]:
            x1 = center[0] + r * math.cos(angle1)
            y1 = center[1] + r * math.sin(angle1)
            z1 = 35 * (1 - ((r - 60) / 40) ** 2)
            
            x2 = center[0] + r * math.cos(angle2)
            y2 = center[1] + r * math.sin(angle2)
            z2 = 35 * (1 - ((r - 60) / 40) ** 2)
            
            msp.add_line((x1, y1, z1), (x2, y2, z2))
    
    # ========== VARIABLE SECTION SIZES ==========
    # Outer ring uses 457x191x67; middle uses 305x165x40; inner uses 254x102x28
    # Mark with colored points
    for radius, color in [(70, 3), (80, 4), (90, 5)]:
        for rib_idx in range(12):
            angle = (rib_idx / 12) * 2 * math.pi
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = 35 * (1 - ((radius - 60) / 40) ** 2)
            point = msp.add_point((x, y, z))
            point.dxf.color = color
    
    # ========== SUPPORT COLUMNS (at key radii) ==========
    # 4 towers supporting roof
    support_angles = [0, math.pi/2, math.pi, 3*math.pi/2]
    
    for angle in support_angles:
        x = center[0] + 65 * math.cos(angle)
        y = center[1] + 65 * math.sin(angle)
        z_base = 0
        z_top = 32
        
        msp.add_line((x, y, z_base), (x, y, z_top))
    
    dxf.saveas('test_extreme_2_curved_stadium_roof.dxf')
    print(f"✅ Created: test_extreme_2_curved_stadium_roof.dxf ({len(msp)} entities)")


def create_multi_level_industrial_plant():
    """
    MULTI-LEVEL INDUSTRIAL PLANT WITH SKEWED GRIDS
    - Grids rotated 5-15 degrees
    - Floors at irregular elevations
    - Beams framing into beams (no columns)
    - Platforms cutting through main steel
    """
    print("Generating: Multi-Level Industrial Plant DXF...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # ========== FLOOR LEVELS (irregular elevations) ==========
    floor_levels = [
        {"name": "Ground", "z": 0*SCALE, "size": (120*SCALE, 100*SCALE), "angle": 0},
        {"name": "Level 1", "z": 8.5*SCALE, "size": (120*SCALE, 100*SCALE), "angle": 5.2},      # 5.2 degrees
        {"name": "Level 2", "z": 17*SCALE, "size": (110*SCALE, 95*SCALE), "angle": -3.8},       # -3.8 degrees
        {"name": "Level 3", "z": 26.3*SCALE, "size": (100*SCALE, 90*SCALE), "angle": 7.5},      # 7.5 degrees
        {"name": "Level 4", "z": 35.8*SCALE, "size": (90*SCALE, 80*SCALE), "angle": -2.3},      # -2.3 degrees
        {"name": "Level 5", "z": 45*SCALE, "size": (80*SCALE, 70*SCALE), "angle": 12.0},        # 12.0 degrees
        {"name": "Level 6", "z": 54.5*SCALE, "size": (70*SCALE, 60*SCALE), "angle": -5.5},      # -5.5 degrees
    ]
    
    # ========== SKEWED GRIDS PER LEVEL ==========
    for level_idx, level in enumerate(floor_levels):
        z = level["z"]
        width, depth = level["size"]
        angle_rad = math.radians(level["angle"])
        
        # Rotation matrix
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Grid points (rotated)
        grid_points = []
        for i in range(5):  # 5x5 grid
            for j in range(5):
                x_local = (i - 2) * width / 4
                y_local = (j - 2) * depth / 4
                
                # Apply rotation
                x = x_local * cos_a - y_local * sin_a
                y = x_local * sin_a + y_local * cos_a
                
                grid_points.append((x, y, z))
        
        # Draw skewed grid beams (X-direction)
        for i in range(5):
            for j in range(4):
                idx1 = i * 5 + j
                idx2 = i * 5 + (j + 1)
                msp.add_line(grid_points[idx1], grid_points[idx2])
        
        # Draw skewed grid beams (Y-direction)
        for i in range(4):
            for j in range(5):
                idx1 = i * 5 + j
                idx2 = (i + 1) * 5 + j
                msp.add_line(grid_points[idx1], grid_points[idx2])
    
    # ========== BEAMS FRAMING INTO BEAMS (no columns) ==========
    # Primary vertical carry beams at each level
    for level_idx in range(len(floor_levels) - 1):
        z1 = floor_levels[level_idx]["z"]
        z2 = floor_levels[level_idx + 1]["z"]
        
        # 4 vertical beams offset from grid corners
        for i in [0, 1, 2, 3]:
            x = -40 + i * 30
            msp.add_line((x, -30, z1), (x, -30, z2))
    
    # ========== CANTILEVERED WALKWAYS ==========
    # Extend from main structure at 45 degrees (Y direction)
    for level_idx in [1, 3, 5]:
        z = floor_levels[level_idx]["z"]
        
        # Cantilever base
        for x_pos in [-30, 0, 30]:
            # Main beam
            msp.add_line((x_pos, 0, z), (x_pos, 15, z))
            
            # Bracing (X members)
            msp.add_line((x_pos - 3, 0, z), (x_pos + 3, 15, z + 2))
            msp.add_line((x_pos + 3, 0, z), (x_pos - 3, 15, z + 2))
    
    # ========== VERTICAL BRACING (not aligned with columns) ==========
    # Distributed X-bracing offset from grid
    for level_idx in range(len(floor_levels) - 1):
        z1 = floor_levels[level_idx]["z"]
        z2 = floor_levels[level_idx + 1]["z"]
        
        # 6 X-braces per level, offset from grid
        for i in range(6):
            x = -50 + i * 20
            y = -40 + (i % 2) * 40
            
            # X-brace diagonals
            msp.add_line((x - 5, y - 5, z1), (x + 5, y + 5, z2))
            msp.add_line((x + 5, y - 5, z1), (x - 5, y + 5, z2))
    
    # ========== PLATFORMS CUTTING THROUGH MAIN STEEL ==========
    # Platform levels that overlap with primary members
    for plat_z in [14, 32, 50]:
        # Platform is 20x30m rectangle
        plat_nodes = [
            (-10, -15, plat_z),
            (10, -15, plat_z),
            (10, 15, plat_z),
            (-10, 15, plat_z),
        ]
        
        # Draw platform perimeter
        for i in range(4):
            msp.add_line(plat_nodes[i], plat_nodes[(i + 1) % 4])
        
        # Interior beams (3x4 grid on platform)
        for i in range(4):
            for j in range(3):
                x = -10 + i * 20 / 3
                msp.add_line((x, -15, plat_z), (x, 15, plat_z))
        
        for j in range(3):
            for i in range(4):
                y = -15 + j * 30 / 2
                msp.add_line((-10, y, plat_z), (10, y, plat_z))
    
    dxf.saveas('test_extreme_3_multi_level_industrial.dxf')
    print(f"✅ Created: test_extreme_3_multi_level_industrial.dxf ({len(msp)} entities)")


def create_long_span_conveyor_bridge():
    """
    LONG-SPAN CONVEYOR BRIDGE WITH VARIABLE SLOPE
    - Length 150-400 meters
    - Continuous slope change
    - Expansion joints
    - Truss depth varies along length
    """
    print("Generating: Long-Span Conveyor Bridge DXF...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # ========== ALIGNMENT CURVE (Horizontal) ==========
    # S-curve: straight -> gentle curve -> straight
    bridge_length = 300  # meters
    
    def alignment_curve(station):
        """Returns (x, y) for given station along bridge (in mm)."""
        if station < 75:
            # Straight section
            return (station*SCALE, 0*SCALE)
        elif station < 225:
            # Curved section: sine wave
            curve_pos = (station - 75) / 150
            curve_radius = 500*SCALE
            angle = curve_pos * math.pi / 2  # quarter circle
            center_y = curve_radius - curve_radius * math.cos(angle)
            x = 75*SCALE + curve_radius * math.sin(angle)
            y = center_y
            return (x, y)
        else:
            # Straight exit
            return ((225 + (station - 225))*SCALE, 500*SCALE)
    
    # ========== ELEVATION PROFILE (Vertical slope change) ==========
    def elevation_profile(station):
        """Returns z elevation for given station (in mm)."""
        if station < 50:
            # Ramp up: 1.5% grade
            return station * 0.015 * SCALE
        elif station < 250:
            # Main span: 0.5% grade
            return (50 * 0.015 + (station - 50) * 0.005) * SCALE
        else:
            # Ramp down: -2% grade
            return (50 * 0.015 + 200 * 0.005 - (station - 250) * 0.02) * SCALE
    
    # ========== MAIN TRUSS (Warren truss with variable depth) ==========
    # Truss nodes along bridge alignment
    num_panels = 30  # 10m panels = 300m bridge
    
    truss_nodes = []
    
    for panel_idx in range(num_panels + 1):
        station = (panel_idx / num_panels) * bridge_length
        x, y = alignment_curve(station)
        z_base = elevation_profile(station)
        
        # Truss depth varies: 3m at ends, 5m in middle (scaled to mm)
        truss_depth = (3 + 2 * math.sin(panel_idx / num_panels * math.pi) ** 2) * SCALE
        
        # Bottom chord
        truss_nodes.append({
            "station": station,
            "panel": panel_idx,
            "chord": "bottom",
            "x": x,
            "y": y,
            "z": z_base,
        })
        
        # Top chord (offset by truss depth)
        # Slight offset perpendicular to alignment (0.5m scaled to mm)
        truss_nodes.append({
            "station": station,
            "panel": panel_idx,
            "chord": "top",
            "x": x + 0.5*SCALE,
            "y": y + 0.5*SCALE,
            "z": z_base + truss_depth,
        })
    
    # Draw bottom chord
    for i in range(0, len(truss_nodes) - 2, 2):
        msp.add_line(
            (truss_nodes[i]["x"], truss_nodes[i]["y"], truss_nodes[i]["z"]),
            (truss_nodes[i + 2]["x"], truss_nodes[i + 2]["y"], truss_nodes[i + 2]["z"])
        )
    
    # Draw top chord
    for i in range(1, len(truss_nodes) - 2, 2):
        msp.add_line(
            (truss_nodes[i]["x"], truss_nodes[i]["y"], truss_nodes[i]["z"]),
            (truss_nodes[i + 2]["x"], truss_nodes[i + 2]["y"], truss_nodes[i + 2]["z"])
        )
    
    # Draw web members (verticals and diagonals)
    for i in range(0, len(truss_nodes) - 2, 2):
        # Vertical
        msp.add_line(
            (truss_nodes[i]["x"], truss_nodes[i]["y"], truss_nodes[i]["z"]),
            (truss_nodes[i + 1]["x"], truss_nodes[i + 1]["y"], truss_nodes[i + 1]["z"])
        )
        
        # Diagonal 1
        msp.add_line(
            (truss_nodes[i]["x"], truss_nodes[i]["y"], truss_nodes[i]["z"]),
            (truss_nodes[i + 3]["x"], truss_nodes[i + 3]["y"], truss_nodes[i + 3]["z"])
        )
        
        # Diagonal 2
        msp.add_line(
            (truss_nodes[i + 1]["x"], truss_nodes[i + 1]["y"], truss_nodes[i + 1]["z"]),
            (truss_nodes[i + 2]["x"], truss_nodes[i + 2]["y"], truss_nodes[i + 2]["z"])
        )
    
    # ========== SIDE BRACING (Lateral stability) ==========
    # K-braces every 20m along length
    for k in range(0, num_panels, 2):
        station = (k / num_panels) * bridge_length
        x, y = alignment_curve(station)
        z_base = elevation_profile(station)
        
        # K-brace height
        truss_depth = 3 + 2 * math.sin(k / num_panels * math.pi) ** 2
        
        # Left side K-braces
        msp.add_line((x - 2, y - 2, z_base), (x - 1, y - 1, z_base + truss_depth / 2))
        msp.add_line((x - 2, y - 2, z_base + truss_depth), (x - 1, y - 1, z_base + truss_depth / 2))
        
        # Right side K-braces
        msp.add_line((x + 2, y + 2, z_base), (x + 1, y + 1, z_base + truss_depth / 2))
        msp.add_line((x + 2, y + 2, z_base + truss_depth), (x + 1, y + 1, z_base + truss_depth / 2))
    
    # ========== EXPANSION JOINTS (every 50m) ==========
    for k in range(0, num_panels, 5):
        station = (k / num_panels) * bridge_length
        x, y = alignment_curve(station)
        z_base = elevation_profile(station)
        
        # Mark with circle (red = expansion joint)
        circle = msp.add_circle(center=(x, y, z_base), radius=1.5)
        circle.dxf.color = 1  # Red
    
    # ========== SUPPORT BEARINGS (at regular intervals) ==========
    # Bearings every 30m (every 3 panels)
    for k in range(0, num_panels, 3):
        station = (k / num_panels) * bridge_length
        x, y = alignment_curve(station)
        z_base = elevation_profile(station)
        
        # Draw bearing support (small square)
        bearing_size = 2
        bearing = msp.add_lwpolyline([
            (x - bearing_size, y - bearing_size, z_base),
            (x + bearing_size, y - bearing_size, z_base),
            (x + bearing_size, y + bearing_size, z_base),
            (x - bearing_size, y + bearing_size, z_base),
        ])
        bearing.close()
        bearing.dxf.color = 3  # Green
    
    # ========== CABLE SUPPORT TOWERS (for longer spans) ==========
    # 2 towers at stations 100m and 200m
    for tower_station in [100, 200]:
        x, y = alignment_curve(tower_station)
        z_base = elevation_profile(tower_station)
        
        # Tower height: 30m
        tower_top_z = z_base + 30
        
        # Main tower legs (4 corner columns)
        tower_offset = 5
        for dx in [-tower_offset, tower_offset]:
            for dy in [-tower_offset, tower_offset]:
                msp.add_line(
                    (x + dx, y + dy, z_base),
                    (x + dx, y + dy, tower_top_z)
                )
        
        # Tower bracing (X members)
        msp.add_line(
            (x - tower_offset, y - tower_offset, z_base),
            (x + tower_offset, y + tower_offset, tower_top_z)
        )
        msp.add_line(
            (x + tower_offset, y - tower_offset, z_base),
            (x - tower_offset, y + tower_offset, tower_top_z)
        )
    
    dxf.saveas('test_extreme_4_long_span_conveyor_bridge.dxf')
    print(f"✅ Created: test_extreme_4_long_span_conveyor_bridge.dxf ({len(msp)} entities)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("GENERATING 4 EXTREME DIFFICULTY DXF FILES")
    print("="*70 + "\n")
    
    create_offshore_pipe_rack()
    create_curved_stadium_roof()
    create_multi_level_industrial_plant()
    create_long_span_conveyor_bridge()
    
    print("\n" + "="*70)
    print("✅ ALL 4 EXTREME DXF FILES CREATED SUCCESSFULLY")
    print("="*70 + "\n")
