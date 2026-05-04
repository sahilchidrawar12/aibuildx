#!/usr/bin/env python3
"""
Generate Tekla-Compatible 3D Skyscraper DXF Files
Corrected for proper import into Tekla Structures
"""

import ezdxf
import math

def create_burj_khalifa_tower():
    """
    BURJ KHALIFA STYLE - 120 STORY TOWER
    Tekla-compatible with proper layers and 3D entities
    """
    print("Generating: Burj Khalifa Style 120-Story Tower DXF (Tekla-Compatible)...")
    
    # Use R2010 or later for better 3D support
    dxf = ezdxf.new(dxfversion='R2010')
    msp = dxf.modelspace()
    
    # Create layers for organization
    dxf.layers.new(name='COLUMNS', dxfattribs={'color': 5})
    dxf.layers.new(name='BEAMS', dxfattribs={'color': 1})
    dxf.layers.new(name='BRACING', dxfattribs={'color': 6})
    dxf.layers.new(name='SPIRE', dxfattribs={'color': 4})
    
    # Units in millimeters (Tekla default)
    SCALE = 1000
    
    tower_height = 828 * SCALE  # 828m total height
    num_floors = 120
    floor_height = tower_height / num_floors  # 6.9m per floor
    
    base_size = 150 * SCALE  # 150m base width
    
    # ========== CORE COLUMNS (Tapered) ==========
    num_core_cols = 8  # Octagonal core
    
    for floor in range(0, num_floors, 2):  # Every 2 floors
        z = floor * floor_height
        
        # Taper factor
        taper = 1.0 - (floor / num_floors) * 0.6
        radius = (base_size / 2) * taper
        
        for i in range(num_core_cols):
            angle = (2 * math.pi * i) / num_core_cols
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            
            if floor < num_floors - 2:
                next_z = (floor + 2) * floor_height
                next_taper = 1.0 - ((floor + 2) / num_floors) * 0.6
                next_radius = (base_size / 2) * next_taper
                next_x = math.cos(angle) * next_radius
                next_y = math.sin(angle) * next_radius
                
                # Use 3DLINE (LINE in 3D space)
                msp.add_line(
                    (x, y, z), 
                    (next_x, next_y, next_z),
                    dxfattribs={'layer': 'COLUMNS'}
                )
    
    # ========== PERIMETER COLUMNS (Setbacks) ==========
    setback_levels = [25, 50, 75, 100]
    setback_sizes = [
        base_size,
        base_size * 0.85,
        base_size * 0.70,
        base_size * 0.55,
        base_size * 0.40
    ]
    
    for level_idx, size in enumerate(setback_sizes):
        start_floor = 0 if level_idx == 0 else setback_levels[level_idx - 1]
        end_floor = setback_levels[level_idx] if level_idx < len(setback_levels) else num_floors
        
        half_size = size / 2
        
        # 8 perimeter positions
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
        
        for floor in range(start_floor, end_floor, 3):
            z = floor * floor_height
            
            for x, y in positions:
                if floor < end_floor - 3:
                    next_z = z + 3 * floor_height
                    msp.add_line(
                        (x, y, z),
                        (x, y, next_z),
                        dxfattribs={'layer': 'COLUMNS'}
                    )
    
    # ========== FLOOR BEAMS (Radial pattern) ==========
    for floor in range(5, num_floors, 5):
        z = floor * floor_height
        
        taper = 1.0 - (floor / num_floors) * 0.6
        core_radius = (base_size / 4) * taper
        perim_radius = (base_size / 2) * taper
        
        # 12 radial beams
        for i in range(12):
            angle = (2 * math.pi * i) / 12
            
            x1 = math.cos(angle) * core_radius
            y1 = math.sin(angle) * core_radius
            x2 = math.cos(angle) * perim_radius
            y2 = math.sin(angle) * perim_radius
            
            msp.add_line(
                (x1, y1, z),
                (x2, y2, z),
                dxfattribs={'layer': 'BEAMS'}
            )
        
        # Circular ring beam at perimeter
        for i in range(24):
            angle1 = (2 * math.pi * i) / 24
            angle2 = (2 * math.pi * (i + 1)) / 24
            
            x1 = math.cos(angle1) * perim_radius
            y1 = math.sin(angle1) * perim_radius
            x2 = math.cos(angle2) * perim_radius
            y2 = math.sin(angle2) * perim_radius
            
            msp.add_line(
                (x1, y1, z),
                (x2, y2, z),
                dxfattribs={'layer': 'BEAMS'}
            )
    
    # ========== DIAGONAL BRACING ==========
    for floor in range(10, num_floors, 10):
        z = floor * floor_height
        z_next = min((floor + 5) * floor_height, tower_height)
        
        taper = 1.0 - (floor / num_floors) * 0.6
        next_floor = min(floor + 5, num_floors - 1)
        taper_next = 1.0 - (next_floor / num_floors) * 0.6
        
        core_r = (base_size / 4) * taper
        perim_r = (base_size / 2) * taper
        core_r_next = (base_size / 4) * taper_next
        perim_r_next = (base_size / 2) * taper_next
        
        # X-bracing at 4 faces
        for i in range(4):
            angle = (math.pi * i) / 2
            
            x1 = math.cos(angle) * core_r
            y1 = math.sin(angle) * core_r
            x2 = math.cos(angle) * perim_r_next
            y2 = math.sin(angle) * perim_r_next
            x3 = math.cos(angle) * core_r_next
            y3 = math.sin(angle) * core_r_next
            x4 = math.cos(angle) * perim_r
            y4 = math.sin(angle) * perim_r
            
            # Diagonal 1: core bottom to perimeter top
            msp.add_line(
                (x1, y1, z),
                (x2, y2, z_next),
                dxfattribs={'layer': 'BRACING'}
            )
            
            # Diagonal 2: core top to perimeter bottom
            msp.add_line(
                (x3, y3, z_next),
                (x4, y4, z),
                dxfattribs={'layer': 'BRACING'}
            )
    
    # ========== SPIRE ==========
    spire_start = tower_height
    spire_height = 80 * SCALE
    spire_levels = 20
    
    for i in range(spire_levels):
        t = i / spire_levels
        z1 = spire_start + i * (spire_height / spire_levels)
        z2 = z1 + (spire_height / spire_levels)
        
        radius1 = 10 * SCALE * (1 - t)
        radius2 = 10 * SCALE * (1 - (t + 1/spire_levels))
        
        # 4 corner struts
        for j in range(4):
            angle = (math.pi * j) / 2
            x1 = math.cos(angle) * radius1
            y1 = math.sin(angle) * radius1
            x2 = math.cos(angle) * radius2
            y2 = math.sin(angle) * radius2
            
            msp.add_line(
                (x1, y1, z1),
                (x2, y2, z2),
                dxfattribs={'layer': 'SPIRE'}
            )
        
        # Cross bracing in spire
        if i % 2 == 0:
            for j in range(4):
                angle1 = (math.pi * j) / 2
                angle2 = (math.pi * (j + 1)) / 2
                
                x1 = math.cos(angle1) * radius1
                y1 = math.sin(angle1) * radius1
                x2 = math.cos(angle2) * radius2
                y2 = math.sin(angle2) * radius2
                
                msp.add_line(
                    (x1, y1, z1),
                    (x2, y2, z2),
                    dxfattribs={'layer': 'SPIRE'}
                )
    
    # ========== SAVE DXF ==========
    filename = 'tekla_burj_khalifa_tower.dxf'
    dxf.saveas(filename)
    print(f"✅ Created: {filename}")
    print(f"   - 120 floors, 828m height")
    print(f"   - Layers: COLUMNS, BEAMS, BRACING, SPIRE")
    print(f"   - Units: millimeters\n")
    
    return filename


def create_twin_towers():
    """
    TWIN TOWERS (WTC style) - 2×110 STORY
    Tekla-compatible with proper organization
    """
    print("Generating: Twin Towers (110-Story Each) DXF (Tekla-Compatible)...")
    
    dxf = ezdxf.new(dxfversion='R2010')
    msp = dxf.modelspace()
    
    # Create layers
    dxf.layers.new(name='COLUMNS_T1', dxfattribs={'color': 5})
    dxf.layers.new(name='COLUMNS_T2', dxfattribs={'color': 5})
    dxf.layers.new(name='BEAMS_T1', dxfattribs={'color': 1})
    dxf.layers.new(name='BEAMS_T2', dxfattribs={'color': 1})
    dxf.layers.new(name='BRACING', dxfattribs={'color': 6})
    dxf.layers.new(name='SKYBRIDGE', dxfattribs={'color': 3})
    
    SCALE = 1000
    
    tower_height = 417 * SCALE
    num_floors = 110
    floor_height = tower_height / num_floors  # 3.79m per floor
    tower_separation = 60 * SCALE
    
    # ========== TOWER 1 ==========
    tower1_x_offset = -tower_separation / 2
    _create_single_tower(
        msp, dxf, tower1_x_offset, 0, num_floors, 
        floor_height, SCALE, tower_id=1
    )
    
    # ========== TOWER 2 ==========
    tower2_x_offset = tower_separation / 2
    _create_single_tower(
        msp, dxf, tower2_x_offset, 0, num_floors, 
        floor_height, SCALE, tower_id=2
    )
    
    # ========== SKY BRIDGE (Level 44) ==========
    bridge_level = 44
    bridge_z = bridge_level * floor_height
    bridge_width = 20 * SCALE
    bridge_height = 4 * SCALE
    
    t1_x = tower1_x_offset
    t2_x = tower2_x_offset
    
    # Top chords
    msp.add_line(
        (t1_x, bridge_width/2, bridge_z + bridge_height),
        (t2_x, bridge_width/2, bridge_z + bridge_height),
        dxfattribs={'layer': 'SKYBRIDGE'}
    )
    msp.add_line(
        (t1_x, -bridge_width/2, bridge_z + bridge_height),
        (t2_x, -bridge_width/2, bridge_z + bridge_height),
        dxfattribs={'layer': 'SKYBRIDGE'}
    )
    
    # Bottom chords
    msp.add_line(
        (t1_x, bridge_width/2, bridge_z),
        (t2_x, bridge_width/2, bridge_z),
        dxfattribs={'layer': 'SKYBRIDGE'}
    )
    msp.add_line(
        (t1_x, -bridge_width/2, bridge_z),
        (t2_x, -bridge_width/2, bridge_z),
        dxfattribs={'layer': 'SKYBRIDGE'}
    )
    
    # Vertical posts (every 5m along bridge)
    num_posts = int(abs(t2_x - t1_x) / (5 * SCALE))
    for i in range(num_posts + 1):
        x = t1_x + i * (t2_x - t1_x) / num_posts
        
        msp.add_line(
            (x, bridge_width/2, bridge_z),
            (x, bridge_width/2, bridge_z + bridge_height),
            dxfattribs={'layer': 'SKYBRIDGE'}
        )
        msp.add_line(
            (x, -bridge_width/2, bridge_z),
            (x, -bridge_width/2, bridge_z + bridge_height),
            dxfattribs={'layer': 'SKYBRIDGE'}
        )
        
        # Cross beam
        msp.add_line(
            (x, -bridge_width/2, bridge_z + bridge_height/2),
            (x, bridge_width/2, bridge_z + bridge_height/2),
            dxfattribs={'layer': 'SKYBRIDGE'}
        )
    
    # Diagonal truss members
    for i in range(num_posts):
        x1 = t1_x + i * (t2_x - t1_x) / num_posts
        x2 = t1_x + (i + 1) * (t2_x - t1_x) / num_posts
        
        # X-bracing
        msp.add_line(
            (x1, bridge_width/2, bridge_z),
            (x2, bridge_width/2, bridge_z + bridge_height),
            dxfattribs={'layer': 'SKYBRIDGE'}
        )
        msp.add_line(
            (x1, bridge_width/2, bridge_z + bridge_height),
            (x2, bridge_width/2, bridge_z),
            dxfattribs={'layer': 'SKYBRIDGE'}
        )
    
    # ========== SAVE DXF ==========
    filename = 'tekla_twin_towers.dxf'
    dxf.saveas(filename)
    print(f"✅ Created: {filename}")
    print(f"   - 2×110 floors, 417m height each")
    print(f"   - Sky bridge at level 44")
    print(f"   - Layers: COLUMNS_T1/T2, BEAMS_T1/T2, BRACING, SKYBRIDGE")
    print(f"   - Units: millimeters\n")
    
    return filename


def _create_single_tower(msp, dxf, x_offset, y_offset, num_floors, floor_height, SCALE, tower_id):
    """Helper: Create a single tower with proper layers"""
    
    col_layer = f'COLUMNS_T{tower_id}'
    beam_layer = f'BEAMS_T{tower_id}'
    
    core_size = 40 * SCALE
    perim_size = 63 * SCALE  # 63m x 63m (actual WTC dimensions)
    
    # ========== CORE COLUMNS (3x3 grid) ==========
    core_spacing = core_size / 2
    
    for floor in range(0, num_floors, 2):
        z = floor * floor_height
        
        if floor < num_floors - 2:
            z_next = (floor + 2) * floor_height
            
            # 9 core columns in 3x3 grid
            for ix in [-1, 0, 1]:
                for iy in [-1, 0, 1]:
                    x = x_offset + ix * core_spacing
                    y = y_offset + iy * core_spacing
                    
                    msp.add_line(
                        (x, y, z),
                        (x, y, z_next),
                        dxfattribs={'layer': col_layer}
                    )
    
    # ========== PERIMETER COLUMNS (Close-spaced) ==========
    # WTC had closely spaced perimeter columns (1.016m spacing)
    perim_half = perim_size / 2
    column_spacing = 1.016 * SCALE
    num_cols_per_side = int(perim_size / column_spacing)
    
    for floor in range(0, num_floors, 3):
        z = floor * floor_height
        
        if floor < num_floors - 3:
            z_next = (floor + 3) * floor_height
            
            # 4 sides of perimeter
            for i in range(num_cols_per_side):
                offset = -perim_half + i * column_spacing
                
                # North side
                msp.add_line(
                    (x_offset + offset, y_offset + perim_half, z),
                    (x_offset + offset, y_offset + perim_half, z_next),
                    dxfattribs={'layer': col_layer}
                )
                # South side
                msp.add_line(
                    (x_offset + offset, y_offset - perim_half, z),
                    (x_offset + offset, y_offset - perim_half, z_next),
                    dxfattribs={'layer': col_layer}
                )
                # East side
                msp.add_line(
                    (x_offset + perim_half, y_offset + offset, z),
                    (x_offset + perim_half, y_offset + offset, z_next),
                    dxfattribs={'layer': col_layer}
                )
                # West side
                msp.add_line(
                    (x_offset - perim_half, y_offset + offset, z),
                    (x_offset - perim_half, y_offset + offset, z_next),
                    dxfattribs={'layer': col_layer}
                )
    
    # ========== FLOOR BEAMS ==========
    for floor in range(5, num_floors, 5):
        z = floor * floor_height
        
        core_half = core_size / 2
        perim_half = perim_size / 2
        
        # Radial beams from core to perimeter (8 directions)
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(angle)
            
            # From core edge
            x1 = x_offset + math.cos(rad) * core_half
            y1 = y_offset + math.sin(rad) * core_half
            
            # To perimeter
            x2 = x_offset + math.cos(rad) * perim_half
            y2 = y_offset + math.sin(rad) * perim_half
            
            msp.add_line(
                (x1, y1, z),
                (x2, y2, z),
                dxfattribs={'layer': beam_layer}
            )
        
        # Perimeter ring beams
        num_segments = 32
        for i in range(num_segments):
            angle1 = (2 * math.pi * i) / num_segments
            angle2 = (2 * math.pi * (i + 1)) / num_segments
            
            x1 = x_offset + math.cos(angle1) * perim_half
            y1 = y_offset + math.sin(angle1) * perim_half
            x2 = x_offset + math.cos(angle2) * perim_half
            y2 = y_offset + math.sin(angle2) * perim_half
            
            msp.add_line(
                (x1, y1, z),
                (x2, y2, z),
                dxfattribs={'layer': beam_layer}
            )


if __name__ == '__main__':
    print("\n" + "="*70)
    print("GENERATING TEKLA-COMPATIBLE SKYSCRAPER DXF FILES")
    print("="*70 + "\n")
    
    create_burj_khalifa_tower()
    create_twin_towers()
    
    print("="*70)
    print("✅ GENERATION COMPLETE")
    print("\nIMPORT INSTRUCTIONS FOR TEKLA STRUCTURES:")
    print("1. File → Import → DXF/DWG")
    print("2. Select the DXF file")
    print("3. Units: Millimeters (already set)")
    print("4. Import as: 3D Lines/Reference Model")
    print("5. Layer mapping: Use provided layers")
    print("6. Convert lines to structural members as needed")
    print("="*70)