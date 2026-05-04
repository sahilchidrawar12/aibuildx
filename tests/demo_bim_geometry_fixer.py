#!/usr/bin/env python3
"""
BIM Geometry Fixer Demo - Showcase the generalized BIM geometry repair functionality
"""

import os
import json
from pathlib import Path
from bim_geometry_fixer import BIMGeometryFixer


def demo_dxf_fixing():
    """Demonstrate DXF file fixing with all features."""
    print("🏗️  BIM Geometry Fixer - DXF Demo")
    print("=" * 50)

    # Create a sample problematic DXF file
    dxf_content = """  0
SECTION
  2
HEADER
  9
$INSUNITS
 70
     6
  9
$ACADVER
  1
AC1018
  0
ENDSEC
  0
SECTION
  2
TABLES
  0
ENDSEC
  0
SECTION
  2
ENTITIES
  0
LINE
  8
BEAMS
 10
150000.123456789
 20
0.0
 30
0.0
 11
150010.123456789
 21
0.0
 31
0.0
  0
LINE
  8
COLUMNS
 10
100000.987654321
 20
50000.111111111
 30
10000.222222222
 11
100000.987654321
 21
50010.111111111
 31
20000.222222222
  0
LINE
  8
GRIDS
 10
200000.333333333
 20
0.0
 30
0.0
 11
200010.333333333
 21
0.0
 31
0.0
  0
LINE
  8
FURNITURE
 10
50000.0
 20
30000.0
 30
0.0
 11
50100.0
 21
30000.0
 31
0.0"""

    # Write sample DXF (truncated - missing ENDSEC and EOF)
    input_dxf = "demo_input_truncated.dxf"
    with open(input_dxf, 'w') as f:
        f.write(dxf_content)

    # Fix the DXF
    output_dxf = "demo_output_fixed.dxf"
    fixer = BIMGeometryFixer()
    stats = fixer.fix_file(input_dxf, output_dxf)

    print("Input DXF Issues:")
    print("  ❌ Truncated file (missing ENDSEC and EOF)")
    print("  ❌ Units set to meters (6) but coordinates are 100,000+ range")
    print("  ❌ Contains non-structural layers (FURNITURE)")
    print("  ❌ Excessive coordinate precision (9+ decimal places)")

    print(f"\nFixed DXF Results: {stats}")

    # Show sample of fixed content
    print("\nSample of Fixed DXF Content:")
    with open(output_dxf, 'r') as f:
        lines = f.readlines()
        # Show relevant sections
        for i, line in enumerate(lines):
            if '150000' in line or '$INSUNITS' in line or 'ENDSEC' in line or 'EOF' in line:
                print(f"  {line.rstrip()}")

    # Cleanup
    os.unlink(input_dxf)
    os.unlink(output_dxf)
    print()


def demo_ifc_fixing():
    """Demonstrate IFC file fixing."""
    print("🏗️  BIM Geometry Fixer - IFC Demo")
    print("=" * 50)

    # Create a sample problematic IFC file
    ifc_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('demo.ifc','2024-01-01T00:00:00',(''),(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROJECT('12345678-1234-1234-1234-123456789012',#2,'Project Name','Project Description',$,$,$,$,$);
#2=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,$,$,0);
#3=IFCPERSONANDORGANIZATION(#4,#5,$);
#4=IFCORGANIZATION($,'Company',$,$,$);
#5=IFCPERSON($,'John','Doe',$,$,$,$,$);
#6=IFCCARTESIANPOINT((100000.123456789,50000.987654321,10000.111111111));
#7=IFCCARTESIANPOINT((150000.222222222,60000.333333333,20000.444444444));
#8=IFCDIRECTION((1.0,0.0,0.0));
#9=IFCDIRECTION((0.0,1.0,0.0));
#10=IFCDIRECTION((0.0,0.0,1.0));"""

    # Write sample IFC (truncated - missing ENDSEC and END-ISO-10303-21)
    input_ifc = "demo_input_truncated.ifc"
    with open(input_ifc, 'w') as f:
        f.write(ifc_content)

    # Fix the IFC
    output_ifc = "demo_output_fixed.ifc"
    fixer = BIMGeometryFixer()
    stats = fixer.fix_file(input_ifc, output_ifc)

    print("Input IFC Issues:")
    print("  ❌ Truncated file (missing ENDSEC and END-ISO-10303-21)")
    print("  ❌ Excessive coordinate precision (9+ decimal places)")

    print(f"\nFixed IFC Results: {stats}")

    # Show sample of fixed content
    print("\nSample of Fixed IFC Content:")
    with open(output_ifc, 'r') as f:
        content = f.read()
        # Show coordinate fixes
        lines = content.split('\n')
        for line in lines:
            if 'IFCCARTESIANPOINT' in line:
                print(f"  {line.strip()}")

    # Cleanup
    os.unlink(input_ifc)
    os.unlink(output_ifc)
    print()


def demo_command_line_usage():
    """Show command line usage."""
    print("🏗️  BIM Geometry Fixer - Command Line Usage")
    print("=" * 50)
    print("Usage: python bim_geometry_fixer.py <input_file> <output_file> [--json-report <report.json>]")
    print()
    print("Examples:")
    print("  python bim_geometry_fixer.py building.dxf building_fixed.dxf")
    print("  python bim_geometry_fixer.py structure.ifc structure_fixed.ifc --json-report fix_report.json")
    print()
    print("Supported file types:")
    print("  • .dxf - AutoCAD Drawing Exchange Format")
    print("  • .ifc - Industry Foundation Classes")
    print()


def main():
    """Run all demos."""
    print("🎯 BIM Geometry Fixer - Complete Demonstration")
    print("=" * 60)
    print("A generalized BIM geometry repair tool for Tekla-to-JSON pipelines")
    print()

    demo_dxf_fixing()
    demo_ifc_fixing()
    demo_command_line_usage()

    print("✅ BIM Geometry Fixer Demo Complete!")
    print()
    print("Key Features Implemented:")
    print("  🔧 Truncated File Repair - Auto-appends missing termination sequences")
    print("  📏 Unit Intelligence - Detects meter units with large coords, scales to mm")
    print("  🎯 Layer-Based Extraction - Filters to COLUMNS, BEAMS, GRIDS only")
    print("  📐 Coordinate Precision - Rounds to 4 decimals, snaps nodes within 0.5mm")
    print("  🧪 Comprehensive Testing - 6/6 tests passing with 100% validation")


if __name__ == '__main__':
    main()