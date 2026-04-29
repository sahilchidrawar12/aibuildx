"""
Comprehensive test suite for Tekla object creation and IFC generation validation.
Tests structural integrity, unit conversions, and compliance with standards.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline.ifc_generator import (
    generate_i_shape_profile,
    generate_rectangular_profile,
    generate_ifc_beam,
    generate_ifc_column,
    _to_metres,
    _vec_to_metres
)
from scripts.api_server import TeklaBeam, TeklaColumn, TeklaPlate

# Test data
SAMPLE_PIPELINE_RESULT = {
    "miner": {
        "members": [
            {
                "id": "beam-001",
                "start": [0.0, 0.0, 0.0],
                "end": [3000.0, 0.0, 0.0],
                "length": 3000.0,
                "layer": "BEAMS",
                "role": "beam",
                "profile": {
                    "name": "HEA200",
                    "depth": 190.0,
                    "width": 200.0,
                    "web_thickness": 6.5,
                    "flange_thickness": 10.0,
                    "fillet_radius": 18.0,
                    "area": 5380.0,  # mm²
                    "Ix": 36920000.0,  # mm⁴
                    "Iy": 13380000.0,  # mm⁴
                    "Zx": 388000.0,   # mm³
                    "Zy": 133800.0,   # mm³
                },
                "material": "S355"
            },
            {
                "id": "column-001",
                "start": [0.0, 0.0, 0.0],
                "end": [0.0, 0.0, 4000.0],
                "length": 4000.0,
                "layer": "COLUMNS",
                "role": "column",
                "profile": {
                    "name": "HEB300",
                    "depth": 300.0,
                    "width": 300.0,
                    "web_thickness": 11.0,
                    "flange_thickness": 19.0,
                    "area": 14900.0,
                    "Ix": 251700000.0,
                    "Iy": 85690000.0,
                    "Zx": 1678000.0,
                    "Zy": 571000.0,
                },
                "material": "S235"
            }
        ]
    }
}

class TestTeklaObjectValidation:
    """Test Tekla object structure validation"""

    def test_tekla_beam_structure(self):
        """Test TeklaBeam model structure compliance"""
        beam_data = {
            "id": "beam-001",
            "type": "beam",
            "name": "Test Beam",
            "start_point": [0.0, 0.0, 0.0],
            "end_point": [3000.0, 0.0, 0.0],
            "profile": "HEA200",
            "material": "S355",
            "rotation_angle": 0.0
        }

        # Validate with Pydantic model
        beam = TeklaBeam(**beam_data)
        assert beam.id == "beam-001"
        assert beam.type == "beam"
        assert beam.start_point == [0.0, 0.0, 0.0]
        assert beam.end_point == [3000.0, 0.0, 0.0]
        assert beam.profile == "HEA200"
        assert beam.material == "S355"

    def test_tekla_column_structure(self):
        """Test TeklaColumn model structure compliance"""
        column_data = {
            "id": "column-001",
            "type": "column",
            "name": "Test Column",
            "start_point": [0.0, 0.0, 0.0],
            "end_point": [0.0, 0.0, 4000.0],
            "profile": "HEB300",
            "material": "S235"
        }

        column = TeklaColumn(**column_data)
        assert column.type == "column"
        assert column.start_point == [0.0, 0.0, 0.0]
        assert column.end_point == [0.0, 0.0, 4000.0]

    def test_conversion_function_output(self):
        """Test convert_pipeline_result_to_tekla_objects output"""
        from app import convert_pipeline_result_to_tekla_objects

        objects, warnings = convert_pipeline_result_to_tekla_objects(SAMPLE_PIPELINE_RESULT)

        assert len(objects) == 2
        assert len(warnings) == 0

        # Check beam
        beam = objects[0]
        assert beam['type'] == 'beam'
        assert beam['id'] == 'beam-001'
        assert beam['start_point'] == [0.0, 0.0, 0.0]
        assert beam['end_point'] == [3000.0, 0.0, 0.0]
        assert beam['profile'] == 'HEA200'
        assert beam['material'] == 'S355'

        # Check column
        column = objects[1]
        assert column['type'] == 'column'
        assert column['profile'] == 'HEB300'

class TestIFCUnitConversions:
    """Test IFC unit conversion correctness"""

    def test_mm_to_metres_conversion(self):
        """Test basic mm to metres conversion"""
        assert _to_metres(1000.0) == 1.0
        assert _to_metres(3000.0) == 3.0
        assert _to_metres(0.0) == 0.0
        assert _to_metres(None) is None

    def test_vector_mm_to_metres(self):
        """Test vector coordinate conversion"""
        vec_mm = [3000.0, 2000.0, 1000.0]
        vec_m = _vec_to_metres(vec_mm)
        assert vec_m == [3.0, 2.0, 1.0]

    def test_i_shape_profile_units(self):
        """Test I-shape profile unit conversions"""
        profile_input = {
            "name": "HEA200",
            "depth": 190.0,      # mm
            "width": 200.0,      # mm
            "web_thickness": 6.5, # mm
            "flange_thickness": 10.0, # mm
            "fillet_radius": 18.0, # mm
            "area": 5380.0,      # mm²
            "Ix": 36920000.0,    # mm⁴
            "Iy": 13380000.0,    # mm⁴
            "Zx": 388000.0,      # mm³
            "Zy": 133800.0,      # mm³
        }

        profile_def = generate_i_shape_profile(profile_input, "test-beam")

        # Check dimensions converted to metres
        assert profile_def['depth'] == 0.19
        assert profile_def['width'] == 0.20
        assert profile_def['web_thickness'] == 0.0065
        assert profile_def['flange_thickness'] == 0.010
        assert profile_def['fillet_radius'] == 0.018

        # Check area: mm² → m²
        assert profile_def['area'] == 0.00538  # 5380 / 1e6

        # Check moments: mm⁴ → m⁴
        assert profile_def['Ix'] == 0.00003692  # 36920000 / 1e12
        assert profile_def['Iy'] == 0.00001338  # 13380000 / 1e12

        # Check section moduli: mm³ → m³
        assert profile_def['Zx'] == 0.000388   # 388000 / 1e9
        assert profile_def['Zy'] == 0.0001338  # 133800 / 1e9

    def test_rectangular_profile_units(self):
        """Test rectangular profile unit conversions"""
        profile_input = {
            "name": "RHS200x100x8",
            "depth": 200.0,      # mm
            "width": 100.0,     # mm
            "wall_thickness": 8.0, # mm
            "area": 4800.0,     # mm²
            "Ix": 3200000.0,    # mm⁴
            "Iy": 12800000.0,   # mm⁴
        }

        profile_def = generate_rectangular_profile(profile_input, "test-column")

        # Check dimensions
        assert profile_def['x_dim'] == 0.1   # width
        assert profile_def['y_dim'] == 0.2   # depth
        assert profile_def['wall_thickness'] == 0.008

        # Check area: mm² → m²
        assert profile_def['area'] == 0.0048  # 4800 / 1e6

        # Check moments: mm⁴ → m⁴
        assert profile_def['Ix'] == 0.0000032   # 3200000 / 1e12
        assert profile_def['Iy'] == 0.0000128   # 12800000 / 1e12

class TestIFCStructureValidation:
    """Test IFC structure correctness"""

    def test_ifc_beam_structure(self):
        """Test complete IFC beam structure"""
        member = SAMPLE_PIPELINE_RESULT['miner']['members'][0]

        beam = generate_ifc_beam(member)

        # Check basic structure
        assert beam['type'] == 'IfcBeam'
        assert beam['id'] == 'beam-001'
        assert beam['name'] == 'Beam-beam-001'

        # Check coordinates converted to metres
        assert beam['start'] == [0.0, 0.0, 0.0]
        assert beam['end'] == [3.0, 0.0, 0.0]
        assert beam['length'] == 3.0

        # Check profile structure
        profile = beam['profile']
        assert profile['type'] == 'IfcIShapeProfileDef'
        assert profile['profile_name'] == 'HEA200'

        # Check placement
        placement = beam['placement']
        assert 'location' in placement
        assert 'axis' in placement
        assert 'ref_direction' in placement

        # Check representation
        rep = beam['representation']
        assert 'swept_area' in rep
        assert rep['swept_area']['type'] == 'IfcExtrudedAreaSolid'

        # Check quantities
        quantities = beam['quantities']
        assert 'Length' in quantities
        assert 'CrossSectionArea' in quantities
        assert 'GrossVolume' in quantities

    def test_ifc_column_structure(self):
        """Test complete IFC column structure"""
        member = SAMPLE_PIPELINE_RESULT['miner']['members'][1]

        column = generate_ifc_column(member)

        assert column['type'] == 'IfcColumn'
        assert column['id'] == 'column-001'
        assert column['start'] == [0.0, 0.0, 0.0]
        assert column['end'] == [0.0, 0.0, 4.0]
        assert column['length'] == 4.0

        # Check profile
        profile = column['profile']
        assert profile['type'] == 'IfcIShapeProfileDef'

class TestIntegrationValidation:
    """Test end-to-end integration"""

    def test_pipeline_to_tekla_conversion(self):
        """Test full pipeline result to Tekla objects conversion"""
        from app import convert_pipeline_result_to_tekla_objects

        objects, warnings = convert_pipeline_result_to_tekla_objects(SAMPLE_PIPELINE_RESULT)

        # Should create valid Tekla objects
        for obj in objects:
            if obj['type'] == 'beam':
                TeklaBeam(**obj)
            elif obj['type'] == 'column':
                TeklaColumn(**obj)

        assert len(objects) == 2
        assert len(warnings) == 0

    def test_pipeline_to_ifc_conversion(self):
        """Test full pipeline result to IFC conversion"""
        from src.pipeline.ifc_generator import generate_ifc_model

        # This would need the full IFC generation function
        # For now, test individual components
        for member in SAMPLE_PIPELINE_RESULT['miner']['members']:
            if member['role'] == 'beam':
                beam = generate_ifc_beam(member)
                assert beam['type'] == 'IfcBeam'
            elif member['role'] == 'column':
                column = generate_ifc_column(member)
                assert column['type'] == 'IfcColumn'

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_member_geometry(self):
        """Test handling of invalid member geometry"""
        invalid_result = {
            "miner": {
                "members": [
                    {
                        "id": "invalid-001",
                        "start": [0, 0, 0],
                        "end": [0, 0, 0],  # Same point - zero length
                        "profile": {"name": "HEA200"},
                        "material": "S355"
                    }
                ]
            }
        }

        from app import convert_pipeline_result_to_tekla_objects
        objects, warnings = convert_pipeline_result_to_tekla_objects(invalid_result)

        assert len(objects) == 0
        assert len(warnings) == 1
        assert "zero-length" in warnings[0]

    def test_missing_profile_data(self):
        """Test handling of missing profile data"""
        incomplete_result = {
            "miner": {
                "members": [
                    {
                        "id": "incomplete-001",
                        "start": [0, 0, 0],
                        "end": [3000, 0, 0],
                        "profile": {},  # Empty profile
                        "material": "S355"
                    }
                ]
            }
        }

        from app import convert_pipeline_result_to_tekla_objects
        objects, warnings = convert_pipeline_result_to_tekla_objects(incomplete_result)

        assert len(objects) == 1
        obj = objects[0]
        assert obj['profile'] == 'HEA200'  # Should default

"""
Comprehensive test suite for Tekla object creation and IFC generation validation.
Tests structural integrity, unit conversions, and compliance with standards.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pipeline.ifc_generator import (
    generate_i_shape_profile,
    generate_rectangular_profile,
    generate_ifc_beam,
    generate_ifc_column,
    _to_metres,
    _vec_to_metres
)

# Import Tekla models
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from api_server import TeklaBeam, TeklaColumn

# Test data
SAMPLE_PIPELINE_RESULT = {
    "miner": {
        "members": [
            {
                "id": "beam-001",
                "start": [0.0, 0.0, 0.0],
                "end": [3000.0, 0.0, 0.0],
                "length": 3000.0,
                "layer": "BEAMS",
                "role": "beam",
                "profile": {
                    "name": "HEA200",
                    "depth": 190.0,
                    "width": 200.0,
                    "web_thickness": 6.5,
                    "flange_thickness": 10.0,
                    "fillet_radius": 18.0,
                    "area": 5380.0,  # mm²
                    "Ix": 36920000.0,  # mm⁴
                    "Iy": 13380000.0,  # mm⁴
                    "Zx": 388000.0,   # mm³
                    "Zy": 133800.0,   # mm³
                },
                "material": "S355"
            },
            {
                "id": "column-001",
                "start": [0.0, 0.0, 0.0],
                "end": [0.0, 0.0, 4000.0],
                "length": 4000.0,
                "layer": "COLUMNS",
                "role": "column",
                "profile": {
                    "name": "HEB300",
                    "depth": 300.0,
                    "width": 300.0,
                    "web_thickness": 11.0,
                    "flange_thickness": 19.0,
                    "area": 14900.0,
                    "Ix": 251700000.0,
                    "Iy": 85690000.0,
                    "Zx": 1678000.0,
                    "Zy": 571000.0,
                },
                "material": "S235"
            }
        ]
    }
}

def run_test(test_func):
    """Run a test function and report result"""
    try:
        test_func()
        print(f"✓ {test_func.__name__}")
        return True
    except Exception as e:
        print(f"✗ {test_func.__name__}: {e}")
        return False

class TestTeklaObjectValidation:
    """Test Tekla object structure validation"""

    def test_tekla_beam_structure(self):
        """Test TeklaBeam model structure compliance"""
        beam_data = {
            "id": "beam-001",
            "type": "beam",
            "name": "Test Beam",
            "start_point": [0.0, 0.0, 0.0],
            "end_point": [3000.0, 0.0, 0.0],
            "profile": "HEA200",
            "material": "S355",
            "rotation_angle": 0.0
        }

        # Validate with Pydantic model
        beam = TeklaBeam(**beam_data)
        assert beam.id == "beam-001"
        assert beam.type == "beam"
        assert beam.start_point == [0.0, 0.0, 0.0]
        assert beam.end_point == [3000.0, 0.0, 0.0]
        assert beam.profile == "HEA200"
        assert beam.material == "S355"

    def test_tekla_column_structure(self):
        """Test TeklaColumn model structure compliance"""
        column_data = {
            "id": "column-001",
            "type": "column",
            "name": "Test Column",
            "start_point": [0.0, 0.0, 0.0],
            "end_point": [0.0, 0.0, 4000.0],
            "profile": "HEB300",
            "material": "S235"
        }

        column = TeklaColumn(**column_data)
        assert column.type == "column"
        assert column.start_point == [0.0, 0.0, 0.0]
        assert column.end_point == [0.0, 0.0, 4000.0]

    def test_conversion_function_output(self):
        """Test convert_pipeline_result_to_tekla_objects output"""
        sys.path.insert(0, str(Path(__file__).parent))
        from app import convert_pipeline_result_to_tekla_objects

        objects, warnings = convert_pipeline_result_to_tekla_objects(SAMPLE_PIPELINE_RESULT)

        assert len(objects) == 2
        assert len(warnings) == 0

        # Check beam
        beam = objects[0]
        assert beam['type'] == 'beam'
        assert beam['id'] == 'beam-001'
        assert beam['start_point'] == [0.0, 0.0, 0.0]
        assert beam['end_point'] == [3000.0, 0.0, 0.0]
        assert beam['profile'] == 'HEA200'
        assert beam['material'] == 'S355'

        # Check column
        column = objects[1]
        assert column['type'] == 'column'
        assert column['profile'] == 'HEB300'

class TestIFCUnitConversions:
    """Test IFC unit conversion correctness"""

    def test_mm_to_metres_conversion(self):
        """Test basic mm to metres conversion"""
        assert _to_metres(1000.0) == 1.0
        assert _to_metres(3000.0) == 3.0
        assert _to_metres(0.0) == 0.0
        assert _to_metres(None) is None

    def test_vector_mm_to_metres(self):
        """Test vector coordinate conversion"""
        vec_mm = [3000.0, 2000.0, 1000.0]
        vec_m = _vec_to_metres(vec_mm)
        assert vec_m == [3.0, 2.0, 1.0]

    def test_i_shape_profile_units(self):
        """Test I-shape profile unit conversions"""
        profile_input = {
            "name": "HEA200",
            "depth": 190.0,      # mm
            "width": 200.0,      # mm
            "web_thickness": 6.5, # mm
            "flange_thickness": 10.0, # mm
            "fillet_radius": 18.0, # mm
            "area": 5380.0,      # mm²
            "Ix": 36920000.0,    # mm⁴
            "Iy": 13380000.0,    # mm⁴
            "Zx": 388000.0,      # mm³
            "Zy": 133800.0,      # mm³
        }

        profile_def = generate_i_shape_profile(profile_input, "test-beam")

        # Check dimensions converted to metres
        assert profile_def['depth'] == 0.19
        assert profile_def['width'] == 0.20
        assert profile_def['web_thickness'] == 0.0065
        assert profile_def['flange_thickness'] == 0.010
        assert profile_def['fillet_radius'] == 0.018

        # Check area: mm² → m²
        assert profile_def['area'] == 0.00538  # 5380 / 1e6

        # Check moments: mm⁴ → m⁴
        assert profile_def['Ix'] == 0.00003692  # 36920000 / 1e12
        assert profile_def['Iy'] == 0.00001338  # 13380000 / 1e12

        # Check section moduli: mm³ → m³
        assert profile_def['Zx'] == 0.000388   # 388000 / 1e9
        assert profile_def['Zy'] == 0.0001338  # 133800 / 1e9

    def test_rectangular_profile_units(self):
        """Test rectangular profile unit conversions"""
        profile_input = {
            "name": "RHS200x100x8",
            "depth": 200.0,      # mm
            "width": 100.0,     # mm
            "wall_thickness": 8.0, # mm
            "area": 4800.0,     # mm²
            "Ix": 3200000.0,    # mm⁴
            "Iy": 12800000.0,   # mm⁴
        }

        profile_def = generate_rectangular_profile(profile_input, "test-column")

        # Check dimensions
        assert profile_def['x_dim'] == 0.1   # width
        assert profile_def['y_dim'] == 0.2   # depth
        assert profile_def['wall_thickness'] == 0.008

        # Check area: mm² → m²
        assert profile_def['area'] == 0.0048  # 4800 / 1e6

        # Check moments: mm⁴ → m⁴
        assert profile_def['Ix'] == 0.0000032   # 3200000 / 1e12
        assert profile_def['Iy'] == 0.0000128   # 12800000 / 1e12

class TestIFCStructureValidation:
    """Test IFC structure correctness"""

    def test_ifc_beam_structure(self):
        """Test complete IFC beam structure"""
        member = SAMPLE_PIPELINE_RESULT['miner']['members'][0]

        beam = generate_ifc_beam(member)

        # Check basic structure
        assert beam['type'] == 'IfcBeam'
        assert beam['id'] == 'beam-001'
        assert beam['name'] == 'Beam-beam-001'

        # Check coordinates converted to metres
        assert beam['start'] == [0.0, 0.0, 0.0]
        assert beam['end'] == [3.0, 0.0, 0.0]
        assert beam['length'] == 3.0

        # Check profile structure
        profile = beam['profile']
        assert profile['type'] == 'IfcIShapeProfileDef'
        assert profile['profile_name'] == 'HEA200'

        # Check placement
        placement = beam['placement']
        assert 'location' in placement
        assert 'axis' in placement
        assert 'ref_direction' in placement

        # Check representation
        rep = beam['representation']
        assert 'swept_area' in rep
        assert rep['swept_area']['type'] == 'IfcExtrudedAreaSolid'

        # Check quantities
        quantities = beam['quantities']
        assert 'Length' in quantities
        assert 'CrossSectionArea' in quantities
        assert 'GrossVolume' in quantities

    def test_ifc_column_structure(self):
        """Test complete IFC column structure"""
        member = SAMPLE_PIPELINE_RESULT['miner']['members'][1]

        column = generate_ifc_column(member)

        assert column['type'] == 'IfcColumn'
        assert column['id'] == 'column-001'
        assert column['start'] == [0.0, 0.0, 0.0]
        assert column['end'] == [0.0, 0.0, 4.0]
        assert column['length'] == 4.0

        # Check profile
        profile = column['profile']
        assert profile['type'] == 'IfcIShapeProfileDef'

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_member_geometry(self):
        """Test handling of invalid member geometry"""
        invalid_result = {
            "miner": {
                "members": [
                    {
                        "id": "invalid-001",
                        "start": [0, 0, 0],
                        "end": [0, 0, 0],  # Same point - zero length
                        "profile": {"name": "HEA200"},
                        "material": "S355"
                    }
                ]
            }
        }

        sys.path.insert(0, str(Path(__file__).parent))
        from app import convert_pipeline_result_to_tekla_objects
        objects, warnings = convert_pipeline_result_to_tekla_objects(invalid_result)

        assert len(objects) == 0
        assert len(warnings) == 1
        assert "zero-length" in warnings[0]

    def test_missing_profile_data(self):
        """Test handling of missing profile data"""
        incomplete_result = {
            "miner": {
                "members": [
                    {
                        "id": "incomplete-001",
                        "start": [0, 0, 0],
                        "end": [3000, 0, 0],
                        "profile": {},  # Empty profile
                        "material": "S355"
                    }
                ]
            }
        }

        sys.path.insert(0, str(Path(__file__).parent))
        from app import convert_pipeline_result_to_tekla_objects
        objects, warnings = convert_pipeline_result_to_tekla_objects(incomplete_result)

        assert len(objects) == 1
        obj = objects[0]
        assert obj['profile'] == 'HEA200'  # Should default

def main():
    """Run all tests and report results"""
    print("Running Tekla and IFC Validation Tests")
    print("=" * 50)

    test_classes = [
        TestTeklaObjectValidation(),
        TestIFCUnitConversions(),
        TestIFCStructureValidation(),
        TestErrorHandling()
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\nRunning {test_class.__class__.__name__}:")

        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total_tests += 1
                if run_test(getattr(test_class, method_name)):
                    passed_tests += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed_tests}/{total_tests} passed")

    if passed_tests < total_tests:
        print(f"❌ {total_tests - passed_tests} tests failed")
        return 1
    else:
        print("✅ All tests passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())</content>
<parameter name="filePath">/Users/sahil/Documents/aibuildx/test_tekla_ifc_validation.py