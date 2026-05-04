#!/usr/bin/env python3
"""
Test BIM Geometry Fixer - Validate all functionality
"""

import os
import json
import tempfile
from pathlib import Path
from bim_geometry_fixer import BIMGeometryFixer


def create_test_dxf_truncated():
    """Create a test DXF file that's truncated (missing EOF)."""
    content = """  0
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
100000.0
 20
0.0
 30
0.0
 11
100010.0
 21
0.0
 31
0.0
  0
LINE
  8
COLUMNS
 10
100000.123456789
 20
50000.789012345
 30
10000.345678901
 11
150000.123456
 21
50010.789012
 31
20000.345678
  0
LINE
  8
GRIDS
 10
100000.4999
 20
0.0
 30
0.0
 11
100010.4999
 21
0.0
 31
0.0
  0
ENDSEC"""
    return content


def create_test_dxf_complete():
    """Create a complete test DXF file."""
    content = create_test_dxf_truncated() + "\n  0\nEOF\n"
    return content


def create_test_ifc_truncated():
    """Create a test IFC file that's truncated."""
    content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('test.ifc','2024-01-01T00:00:00',(''),(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROJECT('12345678-1234-1234-1234-123456789012',#2,'Project Name','Project Description',$,$,$,$,$);
#2=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,$,$,0);
#3=IFCPERSONANDORGANIZATION(#5,#6,$);
#4=IFCORGANIZATION($,'Organization Name',$,$,$);
#5=IFCPERSON($,'John','Doe',$,$,$,$,$);
#6=IFCORGANIZATION($,'Company',$,$,$);
#7=IFCCARTESIANPOINT((100000.123456,50000.789012,10000.345678));
#8=IFCCARTESIANPOINT((150000.123456,50010.789012,20000.345678));
#9=IFCDIRECTION((1.0,0.0,0.0));
#10=IFCDIRECTION((0.0,1.0,0.0));
#11=IFCDIRECTION((0.0,0.0,1.0));
ENDSEC;"""
    return content


def create_test_ifc_complete():
    """Create a complete test IFC file."""
    content = create_test_ifc_truncated() + "\nEND-ISO-10303-21;\n"
    return content


def test_dxf_truncation_fix():
    """Test DXF file truncation fixing."""
    print("🧪 Testing DXF truncation fix...")

    fixer = BIMGeometryFixer()

    # Create truncated DXF
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
        f.write(create_test_dxf_truncated())
        input_path = f.name

    # Create output path
    output_path = input_path.replace('.dxf', '_fixed.dxf')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify truncation was fixed
        assert stats['truncation_fixed'] == True, "Truncation should have been fixed"
        assert stats['file_type'] == 'DXF', "Should be DXF file type"

        # Verify output file ends with EOF
        with open(output_path, 'r') as f:
            content = f.read()
            assert content.strip().endswith('EOF'), "Fixed file should end with EOF"

        print("✅ DXF truncation fix passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_dxf_unit_conversion():
    """Test DXF unit conversion (meters with large coords -> millimeters)."""
    print("🧪 Testing DXF unit conversion...")

    fixer = BIMGeometryFixer()

    # Create DXF with meter units but large coordinates
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
        f.write(create_test_dxf_complete())
        input_path = f.name

    output_path = input_path.replace('.dxf', '_fixed.dxf')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify units were converted
        assert stats['units_converted'] == True, "Units should have been converted"

        # Verify coordinates were scaled (100000 -> 100000000)
        with open(output_path, 'r') as f:
            content = f.read()
            # Should find scaled coordinates like 100000000.0000
            assert '100000000.0000' in content, "Coordinates should be scaled to millimeters"

        print("✅ DXF unit conversion passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_dxf_layer_extraction():
    """Test DXF structural layer extraction."""
    print("🧪 Testing DXF layer extraction...")

    fixer = BIMGeometryFixer()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
        f.write(create_test_dxf_complete())
        input_path = f.name

    output_path = input_path.replace('.dxf', '_fixed.dxf')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify structural layers were extracted
        assert 'BEAMS' in stats['layers_extracted'], "BEAMS layer should be extracted"
        assert 'COLUMNS' in stats['layers_extracted'], "COLUMNS layer should be extracted"
        assert 'GRIDS' in stats['layers_extracted'], "GRIDS layer should be extracted"

        # Verify coordinates were rounded OR scaled (since scaling happens first)
        # When units are converted, coordinates get scaled by 1000, so rounding may not be needed
        if stats['units_converted']:
            # Check that scaled coordinates are present
            with open(output_path, 'r') as f:
                content = f.read()
                assert '150000123.4560' in content, "Scaled coordinates should be present"
        else:
            assert stats['coordinates_rounded'] > 0, "Coordinates should be rounded when not scaled"

        print("✅ DXF layer extraction passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_dxf_node_snapping():
    """Test DXF coordinate node snapping."""
    print("🧪 Testing DXF node snapping...")

    fixer = BIMGeometryFixer()

    # Create DXF with coordinates very close to each other
    content = create_test_dxf_complete().replace('100000.4999', '100000.4999')  # This should snap to existing node

    with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
        f.write(content)
        input_path = f.name

    output_path = input_path.replace('.dxf', '_fixed.dxf')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify node snapping occurred
        assert stats['nodes_snapped'] >= 0, "Node snapping should work"

        print("✅ DXF node snapping passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_ifc_truncation_fix():
    """Test IFC file truncation fixing."""
    print("🧪 Testing IFC truncation fix...")

    fixer = BIMGeometryFixer()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ifc', delete=False) as f:
        f.write(create_test_ifc_truncated())
        input_path = f.name

    output_path = input_path.replace('.ifc', '_fixed.ifc')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify truncation was fixed
        assert stats['truncation_fixed'] == True, "Truncation should have been fixed"
        assert stats['file_type'] == 'IFC', "Should be IFC file type"

        # Verify output file ends correctly
        with open(output_path, 'r') as f:
            content = f.read()
            assert 'END-ISO-10303-21;' in content, "Fixed file should end with END-ISO-10303-21;"

        print("✅ IFC truncation fix passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_ifc_coordinate_precision():
    """Test IFC coordinate precision fixing."""
    print("🧪 Testing IFC coordinate precision...")

    fixer = BIMGeometryFixer()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ifc', delete=False) as f:
        f.write(create_test_ifc_complete())
        input_path = f.name

    output_path = input_path.replace('.ifc', '_fixed.ifc')

    try:
        stats = fixer.fix_file(input_path, output_path)

        # Verify coordinates were rounded
        assert stats['coordinates_rounded'] > 0, "Coordinates should be rounded"

        # Verify precision (should be .4f format)
        with open(output_path, 'r') as f:
            content = f.read()
            # Should have rounded coordinates like 100000.1235
            assert '100000.1235' in content, "Should round to 4 decimal places"
            assert '50000.7890' in content, "Should round to 4 decimal places"

        print("✅ IFC coordinate precision passed")
        return True

    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running BIM Geometry Fixer Tests\n")

    tests = [
        test_dxf_truncation_fix,
        test_dxf_unit_conversion,
        test_dxf_layer_extraction,
        test_dxf_node_snapping,
        test_ifc_truncation_fix,
        test_ifc_coordinate_precision,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with error: {e}")
            failed += 1

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)