#!/usr/bin/env python3
"""
Generate 2 EXTREME DIFFICULTY SKYSCRAPER DXF FILES (FIXED VERSION)
1. Burj Khalifa style - 120-story tapered tower with spire
2. Twin Towers (like World Trade Center) - 2×110 story connected towers

FIXES:
- Columns are now FULL HEIGHT (not segmented)
- Beams properly horizontal
- Z-axis properly scaled (828m and 417m)
- Coordinates in millimeters for proper scaling
"""

import ezdxf
import math
import numpy as np

def create_burj_khalifa_tower():
    """
    BURJ KHALIFA STYLE - 120 STORY TOWER (FIXED)
    - Height: 828m (828,000mm)
    - Tapered design - wider at base, narrower at top
    - Spire at top (80m additional)
    - Complex geometry with setbacks at multiple levels
    - FULL HEIGHT columns (not segmented)
    """
    print("Generating: Burj Khalifa Style 120-Story Tower DXF (FIXED)...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # SCALE: All coordinates in millimeters
    SCALE = 1000
    
    tower_height = 828 * SCALE  # 828m total height (828,000mm)
    num_floors = 120
    floor_height = tower_height / num_floors  # 6,900mm per floor
    
    # Base dimensions (in mm)
    base_size = 150 * SCALE  # 150m base width
    
    print(f"  Tower height: {tower_height/SCALE:.0f}m ({tower_height:.0f}mm)")
    print(f"  Floor height: {floor_height/SCALE:.2f}m ({floor_height:.0f}mm)")
    
    # ========== CORE COLUMNS (FULL HEIGHT - Tapered) ==========
    # Central core columns - get smaller as you go up
    num_core_cols = 8  # Octagonal core
    
    for i in range(num_core_cols):
        angle = (2 * math.pi * i) / num_core_cols
        
        # Bottom position (floor 0)
        taper_bottom = 1.0 - (0 / num_floors) * 0.6
        radius_bottom = (base_size / 2) * taper_bottom
        x_bottom = math.cos(angle) * radius_bottom
        y_bottom = math.sin(angle) * radius_bottom
        z_bottom = 0
        
        # Top position (floor 120)
        taper_top = 1.0 - (num_floors / num_floors) * 0.6  # = 0.4
        radius_top = (base_size / 2) * taper_top
        x_top = math.cos(angle) * radius_top
        y_top = math.sin(angle) * radius_top
        z_top = tower_height
        
        # Full height column
        msp.add_line((x_bottom, y_bottom, z_bottom), (x_top, y_top, z_top), dxfattribs={'color': 5})
    
    # ========== PERIMETER COLUMNS (FULL HEIGHT with Setbacks) ==========
    # Setbacks at floors 25, 50, 75, 100
    setback_configs = [
        (0, 25, base_size * 1.0),         # 0-25: 100% size
        (25, 50, base_size * 0.85),       # 25-50: 85% size
        (50, 75, base_size * 0.70),       # 50-75: 70% size
        (75, 100, base_size * 0.55),      # 75-100: 55% size
        (100, 120, base_size * 0.40),     # 100-120: 40% size
    ]
    
    for level_idx, (start_floor, end_floor, size) in enumerate(setback_configs):
        half_size = size / 2
        
        # Perimeter columns at 8 positions (corners + sides)
        positions = [
            (half_size, half_size),
            (-half_size, half_size),
            (-half_size, -half_size),
            (half_size, -half_size),
            (half_size, 0),
            (-half_size, 0),
            (0, half_size),
            (0, -half_size),
        ]
        
        z_start = start_floor * floor_height
        z_end = end_floor * floor_height
        
        for x, y in positions:
            msp.add_line((x, y, z_start), (x, y, z_end), dxfattribs={'color': 5})
    
    # ========== FLOOR BEAMS (Radial truss pattern - Horizontal) ==========
    # Each floor has radial beams from core to perimeter
    for floor in range(5, num_floors, 6):
        z = floor * floor_height
        
        taper = 1.0 - (floor / num_floors) * 0.6
        core_radius = (base_size / 4) * taper
        perim_radius = (base_size / 2) * taper
        
        # 12 radial beams per floor (every 30 degrees)
        for i in range(12):
            angle = (2 * math.pi * i) / 12
            
            # From core to perimeter (HORIZONTAL)
            x1 = math.cos(angle) * core_radius
            y1 = math.sin(angle) * core_radius
            x2 = math.cos(angle) * perim_radius
            y2 = math.sin(angle) * perim_radius
            
            msp.add_line((x1, y1, z), (x2, y2, z), dxfattribs={'color': 1})
    
    # ========== DIAGONAL BRACING (Exterior X-braces) ==========
    # Every 10 floors, add diagonal bracing between core and perimeter
    for floor in range(10, num_floors, 10):
        z = floor * floor_height
        z_next = (floor + 5) * floor_height
        
        taper = 1.0 - (floor / num_floors) * 0.6
        taper_next = 1.0 - ((floor + 5) / num_floors) * 0.6
        
        core_r = (base_size / 4) * taper
        perim_r = (base_size / 2) * taper
        core_r_next = (base_size / 4) * taper_next
        perim_r_next = (base_size / 2) * taper_next
        
        # 4 diagonal braces (X-pattern)
        for i in range(4):
            angle = (math.pi * i) / 2
            
            # Diagonal from core bottom to perimeter top
            x1 = math.cos(angle) * core_r
            y1 = math.sin(angle) * core_r
            x2 = math.cos(angle) * perim_r_next
            y2 = math.sin(angle) * perim_r_next
            
            msp.add_line((x1, y1, z), (x2, y2, z_next), dxfattribs={'color': 6})
            
            # Diagonal from core top to perimeter bottom
            x3 = math.cos(angle) * core_r_next
            y3 = math.sin(angle) * core_r_next
            
            msp.add_line((x3, y3, z_next), (x2, y2, z), dxfattribs={'color': 6})
    
    # ========== SPIRE (Top 80m of tower) ==========
    spire_start = tower_height
    spire_height = 80 * SCALE
    spire_levels = 20
    
    for i in range(spire_levels):
        t = i / spire_levels
        z1 = spire_start + i * (spire_height / spire_levels)
        z2 = z1 + (spire_height / spire_levels)
        
        # Tapered spire - cone shape
        radius1 = 10 * SCALE * (1 - t)
        radius2 = 10 * SCALE * (1 - (t + 1/spire_levels))
        
        # 4 corner struts
        for j in range(4):
            angle = (math.pi * j) / 2
            x1 = math.cos(angle) * radius1
            y1 = math.sin(angle) * radius1
            x2 = math.cos(angle) * radius2
            y2 = math.sin(angle) * radius2
            
            msp.add_line((x1, y1, z1), (x2, y2, z2), dxfattribs={'color': 4})
    
    # ========== SAVE DXF FILE ==========
    filename = 'test_extreme_5_burj_khalifa_tower.dxf'
    dxf.saveas(filename)
    print(f"✅ Created: {filename} (120 floors, 828m height, FULL HEIGHT columns)\n")
    
    return filename


def _create_single_tower(msp, x_offset, y_offset, num_floors, floor_height, tower_height, SCALE, tower_id=1):
    """Helper function to create a single tower"""
    
    # Core columns (4 columns forming 40m square)
    core_size = 40 * SCALE
    core_half = core_size / 2
    core_positions = [
        (core_half, core_half),
        (-core_half, core_half),
        (-core_half, -core_half),
        (core_half, -core_half),
    ]
    
    # FULL HEIGHT core columns
    for x, y in core_positions:
        x_pos = x_offset + x
        y_pos = y_offset + y
        msp.add_line((x_pos, y_pos, 0), (x_pos, y_pos, tower_height), dxfattribs={'color': 5})
    
    # Perimeter columns (4 columns forming 60m square)
    perim_size = 60 * SCALE
    perim_half = perim_size / 2
    perim_positions = [
        (perim_half, perim_half),
        (-perim_half, perim_half),
        (-perim_half, -perim_half),
        (perim_half, -perim_half),
    ]
    
    # FULL HEIGHT perimeter columns
    for x, y in perim_positions:
        x_pos = x_offset + x
        y_pos = y_offset + y
        msp.add_line((x_pos, y_pos, 0), (x_pos, y_pos, tower_height), dxfattribs={'color': 5})
    
    # Floor beams (core-to-perimeter, every 5 floors) - HORIZONTAL
    for floor in range(5, num_floors, 5):
        z = floor * floor_height
        
        # 4 beams connecting core to each perimeter column
        core_x = x_offset
        core_y = y_offset
        
        for perim_x, perim_y in perim_positions:
            x_perim = x_offset + perim_x
            y_perim = y_offset + perim_y
            msp.add_line((core_x, core_y, z), (x_perim, y_perim, z), dxfattribs={'color': 1})


def create_twin_towers():
    """
    TWIN TOWERS (World Trade Center style) - 2×110 STORY CONNECTED (FIXED)
    - Height: 417m each tower (417,000mm)
    - 2 identical towers connected by sky bridge at level 44
    - Spacing between towers: 60m
    - FULL HEIGHT columns (not segmented)
    """
    print("Generating: Twin Towers (110-Story Each) DXF (FIXED)...")
    
    dxf = ezdxf.new(dxfversion='R2000')
    msp = dxf.modelspace()
    
    # SCALE: All coordinates in millimeters
    SCALE = 1000
    
    tower_height = 417 * SCALE  # 417m total height (417,000mm)
    num_floors = 110
    floor_height = tower_height / num_floors  # 3,790mm per floor
    tower_separation = 60 * SCALE  # 60m between towers
    
    print(f"  Tower height: {tower_height/SCALE:.0f}m ({tower_height:.0f}mm)")
    print(f"  Floor height: {floor_height/SCALE:.2f}m ({floor_height:.0f}mm)")
    print(f"  Separation: {tower_separation/SCALE:.0f}m")
    
    # ========== TOWER 1 ==========
    tower1_x_offset = -tower_separation / 2
    _create_single_tower(msp, tower1_x_offset, 0, num_floors, floor_height, tower_height, SCALE, tower_id=1)
    
    # ========== TOWER 2 ==========
    tower2_x_offset = tower_separation / 2
    _create_single_tower(msp, tower2_x_offset, 0, num_floors, floor_height, tower_height, SCALE, tower_id=2)
    
    # ========== SKY BRIDGE (Level 44) ==========
    bridge_level = 44
    bridge_z = bridge_level * floor_height
    bridge_width = 50 * SCALE  # 50m wide bridge
    
    # Main truss of bridge (HORIZONTAL)
    t1_x = tower1_x_offset
    t2_x = tower2_x_offset
    
    # Top chord (horizontal)
    msp.add_line((t1_x, bridge_width, bridge_z + 5*SCALE), (t2_x, bridge_width, bridge_z + 5*SCALE), dxfattribs={'color': 3})
    # Bottom chord (horizontal)
    msp.add_line((t1_x, -bridge_width, bridge_z - 5*SCALE), (t2_x, -bridge_width, bridge_z - 5*SCALE), dxfattribs={'color': 3})
    
    # Connection points from towers to bridge - vertical hangers
    for i in range(0, int(bridge_width * 2), int(5*SCALE)):
        y_pos = -bridge_width + i
        # Vertical hangers
        msp.add_line((t1_x, y_pos, bridge_z), (t1_x, y_pos, bridge_z + 5*SCALE), dxfattribs={'color': 7})
        msp.add_line((t2_x, y_pos, bridge_z), (t2_x, y_pos, bridge_z + 5*SCALE), dxfattribs={'color': 7})

    # ========== CONNECTION MARKERS (circles) FOR PIPELINE DETECTION ==========
    def add_markers(centers, z_levels, radius=500):
        for (cx, cy) in centers:
            for z in z_levels:
                msp.add_circle((cx, cy, z), radius=radius, dxfattribs={'color': 2})

    core_size = 40 * SCALE
    perim_size = 60 * SCALE
    core_half = core_size / 2
    perim_half = perim_size / 2

    # Core and perimeter marker positions relative to tower origin
    core_pts = [
        (core_half, core_half), (-core_half, core_half), (-core_half, -core_half), (core_half, -core_half)
    ]
    perim_pts = [
        (perim_half, perim_half), (-perim_half, perim_half), (-perim_half, -perim_half), (perim_half, -perim_half)
    ]

    z_levels = [0, bridge_z, tower_height]
    add_markers([(tower1_x_offset + x, y) for x, y in core_pts + perim_pts], z_levels)
    add_markers([(tower2_x_offset + x, y) for x, y in core_pts + perim_pts], z_levels)

    # Bridge end markers
    add_markers([(t1_x, bridge_width), (t1_x, -bridge_width), (t2_x, bridge_width), (t2_x, -bridge_width)], [bridge_z], radius=400)
    
    # ========== INTER-TOWER BRACING (Diagonal) ==========
    # Diagonal braces connecting towers at multiple levels
    for level in range(20, num_floors, 20):
        z = level * floor_height
        
        # Upper left to lower right (diagonal)
        msp.add_line((tower1_x_offset, 0, z), (tower2_x_offset, 0, z + 10*floor_height), dxfattribs={'color': 6})
        # Upper right to lower left (diagonal)
        msp.add_line((tower2_x_offset, 0, z), (tower1_x_offset, 0, z + 10*floor_height), dxfattribs={'color': 6})
    
    # ========== SAVE DXF FILE ==========
    filename = 'test_extreme_6_twin_towers.dxf'
    dxf.saveas(filename)
    print(f"✅ Created: {filename} (2×110 floors, 417m height each, FULL HEIGHT columns)\n")
    
    return filename


if __name__ == '__main__':
    print("\n" + "="*70)
    print("GENERATING 2 EXTREME SKYSCRAPER DXF FILES (FIXED VERSION)")
    print("="*70 + "\n")
    
    create_burj_khalifa_tower()
    create_twin_towers()
    
    print("="*70)
    print("✅ SKYSCRAPER DXF GENERATION COMPLETE (FIXED)")
    print("="*70 + "\n")
