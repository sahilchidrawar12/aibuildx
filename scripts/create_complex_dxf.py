#!/usr/bin/env python3
"""
Create a complex multi-story steel building DXF file for testing.
Simulates a 3-story office building with:
- 4x4 column grid (16 columns total)
- Moment-resisting connections on perimeter
- Bracing on end bays
- Composite floor system
- Complex geometry suitable for deep pipeline analysis
"""

import os
import json
from typing import List, Tuple, Dict, Any

# Try to import ezdxf, if not available create manual DXF
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False
    print("⚠️  ezdxf not available, creating manual DXF format")

def create_complex_structure_dxf() -> Dict[str, Any]:
    """
    Create a 3-story steel building with:
    - 4 bays x 4 bays (5m spacing each)
    - 3 stories (4m floor height)
    - Grid dimensions: 20m x 20m x 12m
    - 16 columns, 48 beams, 8 braces, 64 connections
    """
    
    # Grid and geometry parameters
    BAY_SIZE = 5.0  # 5m bays
    FLOOR_HEIGHT = 4.0  # 4m stories
    NUM_BAYS_X = 4
    NUM_BAYS_Y = 4
    NUM_STORIES = 3
    
    # Building dimensions
    BUILDING_WIDTH = BAY_SIZE * NUM_BAYS_X  # 20m
    BUILDING_LENGTH = BAY_SIZE * NUM_BAYS_Y  # 20m
    BUILDING_HEIGHT = FLOOR_HEIGHT * NUM_STORIES  # 12m
    
    # Column and beam sizes (placeholder - will be standardized)
    COL_SIZE = "W14x90"  # 14" x 10.5" x 90 lb/ft
    BEAM_SIZE = "W24x55"  # 24" x 7" x 55 lb/ft
    BRACE_SIZE = "HSS6x6x1/2"  # 6"x6"x1/2" hollow square
    
    # Data structures
    columns = []
    beams = []
    braces = []
    connections = []
    plates = []
    
    # ===== COLUMNS =====
    # 4x4 grid of columns at each story level
    col_id = 0
    for floor in range(NUM_STORIES + 1):  # 0, 1, 2, 3 (foundation to roof)
        z = floor * FLOOR_HEIGHT
        for j in range(NUM_BAYS_Y + 1):
            for i in range(NUM_BAYS_X + 1):
                x = i * BAY_SIZE
                y = j * BAY_SIZE
                
                # Only create columns for 3 stories (not roof)
                if floor < NUM_STORIES:
                    col_id += 1
                    col_height = FLOOR_HEIGHT
                    
                    # Corner and perimeter columns are larger
                    is_corner = (i == 0 or i == NUM_BAYS_X) and (j == 0 or j == NUM_BAYS_Y)
                    is_edge = (i == 0 or i == NUM_BAYS_X) or (j == 0 or j == NUM_BAYS_Y)
                    
                    col_profile = "W14x99" if is_corner else ("W14x90" if is_edge else "W14x82")
                    
                    columns.append({
                        "id": f"COL_{col_id:03d}",
                        "type": "COLUMN",
                        "profile": col_profile,
                        "start_x": x,
                        "start_y": y,
                        "start_z": z,
                        "end_x": x,
                        "end_y": y,
                        "end_z": z + col_height,
                        "length": col_height,
                        "material": "A992",  # ASTM A992 Gr50
                        "yield_strength": 345.0,  # MPa (50 ksi)
                        "rotation": 0.0,
                        "story": floor + 1,
                        "grid_i": i,
                        "grid_j": j
                    })
    
    # ===== BEAMS (Girders in X direction) =====
    # Main floor beams connecting columns
    beam_id = 0
    for floor in range(1, NUM_STORIES + 1):
        z = floor * FLOOR_HEIGHT
        
        for j in range(NUM_BAYS_Y + 1):
            for i in range(NUM_BAYS_X):
                x_start = i * BAY_SIZE
                x_end = (i + 1) * BAY_SIZE
                y = j * BAY_SIZE
                
                beam_id += 1
                beam_length = BAY_SIZE
                
                # Perimeter beams are larger
                is_perimeter = (j == 0 or j == NUM_BAYS_Y)
                beam_profile = "W27x114" if is_perimeter else "W24x55"
                
                beams.append({
                    "id": f"BM_X_{beam_id:03d}",
                    "type": "BEAM",
                    "profile": beam_profile,
                    "start_x": x_start,
                    "start_y": y,
                    "start_z": z,
                    "end_x": x_end,
                    "end_y": y,
                    "end_z": z,
                    "length": beam_length,
                    "material": "A992",
                    "yield_strength": 345.0,
                    "rotation": 0.0,
                    "direction": "X",
                    "story": floor,
                    "grid_i": i,
                    "grid_j": j
                })
    
    # ===== BEAMS (Girders in Y direction) =====
    for floor in range(1, NUM_STORIES + 1):
        z = floor * FLOOR_HEIGHT
        
        for i in range(NUM_BAYS_X + 1):
            for j in range(NUM_BAYS_Y):
                x = i * BAY_SIZE
                y_start = j * BAY_SIZE
                y_end = (j + 1) * BAY_SIZE
                
                beam_id += 1
                beam_length = BAY_SIZE
                
                # Perimeter beams are larger
                is_perimeter = (i == 0 or i == NUM_BAYS_X)
                beam_profile = "W27x114" if is_perimeter else "W24x55"
                
                beams.append({
                    "id": f"BM_Y_{beam_id:03d}",
                    "type": "BEAM",
                    "profile": beam_profile,
                    "start_x": x,
                    "start_y": y_start,
                    "start_z": z,
                    "end_x": x,
                    "end_y": y_end,
                    "end_z": z,
                    "length": beam_length,
                    "material": "A992",
                    "yield_strength": 345.0,
                    "rotation": 90.0,  # 90 degrees (Y-direction)
                    "direction": "Y",
                    "story": floor,
                    "grid_i": i,
                    "grid_j": j
                })
    
    # ===== BRACING (X-diaphragm) =====
    # Chevron bracing on end bays
    brace_id = 0
    for floor in range(1, NUM_STORIES + 1):
        z = floor * FLOOR_HEIGHT
        
        # End bay X-bracing (j=0 and j=NUM_BAYS_Y)
        for j in [0, NUM_BAYS_Y]:
            for i in range(NUM_BAYS_X):
                x_left = i * BAY_SIZE
                x_right = (i + 1) * BAY_SIZE
                y = j * BAY_SIZE
                
                # V-brace configuration (two diagonals meeting at mid-height)
                mid_x = (x_left + x_right) / 2
                mid_y = y
                mid_z = z + FLOOR_HEIGHT / 2
                
                # Upper diagonal
                brace_id += 1
                braces.append({
                    "id": f"BR_{brace_id:03d}",
                    "type": "BRACE",
                    "profile": BRACE_SIZE,
                    "start_x": x_left,
                    "start_y": y,
                    "start_z": z,
                    "end_x": mid_x,
                    "end_y": mid_y,
                    "end_z": mid_z + 0.3,  # Slight offset
                    "length": ((mid_x - x_left)**2 + (mid_y - y)**2 + (mid_z - z)**2)**0.5,
                    "material": "A500",  # ASTM A500 (HSS)
                    "yield_strength": 290.0,
                    "rotation": 0.0,
                    "connection_type": "GUSSET",
                    "story": floor,
                    "direction": "DIAGONAL"
                })
                
                # Lower diagonal
                brace_id += 1
                braces.append({
                    "id": f"BR_{brace_id:03d}",
                    "type": "BRACE",
                    "profile": BRACE_SIZE,
                    "start_x": x_right,
                    "start_y": y,
                    "start_z": z,
                    "end_x": mid_x,
                    "end_y": mid_y,
                    "end_z": mid_z - 0.3,  # Slight offset
                    "length": ((mid_x - x_right)**2 + (mid_y - y)**2 + (mid_z - z)**2)**0.5,
                    "material": "A500",
                    "yield_strength": 290.0,
                    "rotation": 0.0,
                    "connection_type": "GUSSET",
                    "story": floor,
                    "direction": "DIAGONAL"
                })
    
    # ===== CONNECTIONS =====
    # Moment connections at perimeter columns
    conn_id = 0
    for col in columns:
        if col["story"] < NUM_STORIES:  # Not roof level
            # Find connected beams
            col_x = col["start_x"]
            col_y = col["start_y"]
            col_z = col["start_z"]
            
            # Check for X-direction beams
            for beam in beams:
                if beam["direction"] == "X":
                    if ((abs(beam["start_y"] - col_y) < 0.1 and
                         abs(beam["start_z"] - col_z) < 0.1 and
                         (beam["start_x"] <= col_x <= beam["end_x"] or
                          beam["end_x"] <= col_x <= beam["start_x"]))):
                        
                        conn_id += 1
                        connections.append({
                            "id": f"CONN_{conn_id:03d}",
                            "type": "MOMENT",
                            "member1_id": col["id"],
                            "member2_id": beam["id"],
                            "member1_type": "COLUMN",
                            "member2_type": "BEAM",
                            "connection_x": col_x,
                            "connection_y": col_y,
                            "connection_z": col_z,
                            "weld_type": "FILLET",
                            "weld_size": 0.375,  # 3/8"
                            "bolt_config": {
                                "standard": "ASTM A325",
                                "diameter": 0.75,  # 3/4"
                                "rows": 2,
                                "cols": 3,
                                "spacing": 3.0
                            },
                            "flange_plate": True,
                            "web_cleat": False,
                            "capacity_ratio": 0.65
                        })
            
            # Check for Y-direction beams
            for beam in beams:
                if beam["direction"] == "Y":
                    if ((abs(beam["start_x"] - col_x) < 0.1 and
                         abs(beam["start_z"] - col_z) < 0.1 and
                         (beam["start_y"] <= col_y <= beam["end_y"] or
                          beam["end_y"] <= col_y <= beam["start_y"]))):
                        
                        conn_id += 1
                        connections.append({
                            "id": f"CONN_{conn_id:03d}",
                            "type": "MOMENT",
                            "member1_id": col["id"],
                            "member2_id": beam["id"],
                            "member1_type": "COLUMN",
                            "member2_type": "BEAM",
                            "connection_x": col_x,
                            "connection_y": col_y,
                            "connection_z": col_z,
                            "weld_type": "FILLET",
                            "weld_size": 0.375,
                            "bolt_config": {
                                "standard": "ASTM A325",
                                "diameter": 0.75,
                                "rows": 2,
                                "cols": 3,
                                "spacing": 3.0
                            },
                            "flange_plate": True,
                            "web_cleat": False,
                            "capacity_ratio": 0.65
                        })
    
    # ===== GUSSET PLATES (for bracing) =====
    plate_id = 0
    for brace in braces:
        plate_id += 1
        plates.append({
            "id": f"PL_{plate_id:03d}",
            "type": "GUSSET",
            "associated_brace": brace["id"],
            "thickness": 0.5,  # 1/2"
            "material": "A36",
            "length": 0.8,  # 32"
            "width": 0.8,  # 32"
            "connection_x": (brace["start_x"] + brace["end_x"]) / 2,
            "connection_y": (brace["start_y"] + brace["end_y"]) / 2,
            "connection_z": (brace["start_z"] + brace["end_z"]) / 2,
            "bolt_holes": 12,
            "bolt_size": 0.75
        })
    
    # ===== FLOOR DECK =====
    # Composite deck covering each floor
    deck_plates = []
    for floor in range(1, NUM_STORIES + 1):
        z = floor * FLOOR_HEIGHT
        deck_plates.append({
            "id": f"DECK_{floor}",
            "type": "DECK",
            "floor": floor,
            "material": "A1018",  # Deck steel
            "cover_x_start": 0.0,
            "cover_x_end": BUILDING_WIDTH,
            "cover_y_start": 0.0,
            "cover_y_end": BUILDING_LENGTH,
            "cover_z": z,
            "thickness": 0.05,  # 2" total with concrete
            "concrete_thickness": 0.10,
            "ribs_direction": "X"  # Ribs running in X direction
        })
    
    structure = {
        "building": {
            "name": "Complex Multi-Story Steel Frame",
            "description": "3-story office building with 4x4 column grid",
            "width": BUILDING_WIDTH,
            "length": BUILDING_LENGTH,
            "height": BUILDING_HEIGHT,
            "stories": NUM_STORIES,
            "bay_size": BAY_SIZE,
            "floor_height": FLOOR_HEIGHT,
            "occupancy": "Office",
            "location": "Chicago, IL",
            "code": "IBC 2021",
            "design_standard": "AISC 360-16"
        },
        "columns": columns,
        "beams": beams,
        "braces": braces,
        "connections": connections,
        "plates": plates,
        "deck": deck_plates,
        "summary": {
            "total_columns": len(columns),
            "total_beams": len(beams),
            "total_braces": len(braces),
            "total_connections": len(connections),
            "total_plates": len(plates),
            "total_members": len(columns) + len(beams) + len(braces)
        }
    }
    
    return structure


def create_manual_dxf(structure: Dict[str, Any]) -> str:
    """
    Create a manual DXF file (text format) for the structure.
    Returns the DXF content as a string.
    """
    
    dxf_content = [
        "999",
        "Complex Steel Building - Multi-Story Frame",
        "  0",
        "SECTION",
        "  2",
        "HEADER",
        "  9",
        "$ACADVER",
        "  1",
        "AC1021",
        "  9",
        "$UNITS",
        " 70",
        "1",
        "  0",
        "ENDSEC",
        "  0",
        "SECTION",
        "  2",
        "TABLES",
        "  0",
        "TABLE",
        "  2",
        "LAYER",
        " 70",
        "7",
        # Layers
        "  0",
        "LAYER",
        "  2",
        "COLUMNS",
        " 70",
        "0",
        " 62",
        "1",
        "  6",
        "CONTINUOUS",
        "  0",
        "LAYER",
        "  2",
        "BEAMS_X",
        " 70",
        "0",
        " 62",
        "2",
        "  6",
        "CONTINUOUS",
        "  0",
        "LAYER",
        "  2",
        "BEAMS_Y",
        " 70",
        "0",
        " 62",
        "3",
        "  6",
        "CONTINUOUS",
        "  0",
        "LAYER",
        "  2",
        "BRACES",
        " 70",
        "0",
        " 62",
        "5",
        "  6",
        "CONTINUOUS",
        "  0",
        "LAYER",
        "  2",
        "CONNECTIONS",
        " 70",
        "0",
        " 62",
        "4",
        "  6",
        "CONTINUOUS",
        "  0",
        "ENDTAB",
        "  0",
        "ENDSEC",
        "  0",
        "SECTION",
        "  2",
        "BLOCKS",
        "  0",
        "ENDSEC",
        "  0",
        "SECTION",
        "  2",
        "ENTITIES",
    ]
    
    # Add columns as vertical lines
    for col in structure["columns"]:
        dxf_content.extend([
            "  0",
            "LINE",
            "  8",
            "COLUMNS",
            " 10",
            f"{col['start_x']:.2f}",
            " 20",
            f"{col['start_y']:.2f}",
            " 30",
            f"{col['start_z']:.2f}",
            " 11",
            f"{col['end_x']:.2f}",
            " 21",
            f"{col['end_y']:.2f}",
            " 31",
            f"{col['end_z']:.2f}",
        ])
        # Add text label
        dxf_content.extend([
            "  0",
            "TEXT",
            "  8",
            "COLUMNS",
            " 10",
            f"{col['start_x']:.2f}",
            " 20",
            f"{col['start_y']:.2f}",
            " 30",
            f"{col['start_z']:.2f}",
            " 40",
            "0.3",
            "  1",
            col["id"]
        ])
    
    # Add beams as lines
    for beam in structure["beams"]:
        layer = "BEAMS_X" if beam["direction"] == "X" else "BEAMS_Y"
        dxf_content.extend([
            "  0",
            "LINE",
            "  8",
            layer,
            " 10",
            f"{beam['start_x']:.2f}",
            " 20",
            f"{beam['start_y']:.2f}",
            " 30",
            f"{beam['start_z']:.2f}",
            " 11",
            f"{beam['end_x']:.2f}",
            " 21",
            f"{beam['end_y']:.2f}",
            " 31",
            f"{beam['end_z']:.2f}",
        ])
    
    # Add braces as lines
    for brace in structure["braces"]:
        dxf_content.extend([
            "  0",
            "LINE",
            "  8",
            "BRACES",
            " 10",
            f"{brace['start_x']:.2f}",
            " 20",
            f"{brace['start_y']:.2f}",
            " 30",
            f"{brace['start_z']:.2f}",
            " 11",
            f"{brace['end_x']:.2f}",
            " 21",
            f"{brace['end_y']:.2f}",
            " 31",
            f"{brace['end_z']:.2f}",
        ])
    
    # Add connection points as circles
    for conn in structure["connections"]:
        dxf_content.extend([
            "  0",
            "CIRCLE",
            "  8",
            "CONNECTIONS",
            " 10",
            f"{conn['connection_x']:.2f}",
            " 20",
            f"{conn['connection_y']:.2f}",
            " 30",
            f"{conn['connection_z']:.2f}",
            " 40",
            "0.2"
        ])
    
    dxf_content.extend([
        "  0",
        "ENDSEC",
        "  0",
        "EOF"
    ])
    
    return "\n".join(dxf_content)


def main():
    """Main entry point."""
    
    print("🏗️  Creating complex 3-story steel building structure...")
    
    # Create structure
    structure = create_complex_structure_dxf()
    
    # Save as JSON
    json_output_path = "/Users/sahil/Documents/aibuildx/examples/complex_structure_input.json"
    with open(json_output_path, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"✅ JSON saved to {json_output_path}")
    
    # Create DXF
    dxf_content = create_manual_dxf(structure)
    dxf_output_path = "/Users/sahil/Documents/aibuildx/examples/complex_structure.dxf"
    with open(dxf_output_path, "w") as f:
        f.write(dxf_content)
    print(f"✅ DXF saved to {dxf_output_path}")
    
    # Print summary
    print("\n📊 Structure Summary:")
    print(f"   Columns: {structure['summary']['total_columns']}")
    print(f"   Beams: {structure['summary']['total_beams']}")
    print(f"   Braces: {structure['summary']['total_braces']}")
    print(f"   Connections: {structure['summary']['total_connections']}")
    print(f"   Gusset Plates: {structure['summary']['total_plates']}")
    print(f"   Total Members: {structure['summary']['total_members']}")
    print(f"\n   Building Dimensions: {structure['building']['width']}m x {structure['building']['length']}m x {structure['building']['height']}m")
    print(f"   Stories: {structure['building']['stories']}")
    print(f"   Grid: {structure['building']['width']/structure['building']['bay_size']:.0f} x {structure['building']['length']/structure['building']['bay_size']:.0f} @ {structure['building']['bay_size']}m bays")
    
    return structure


if __name__ == "__main__":
    main()
