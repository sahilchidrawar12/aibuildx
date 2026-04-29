"""
Simple test for IFC unit conversions
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pipeline.ifc_generator import (
    generate_i_shape_profile,
    generate_rectangular_profile,
    _to_metres,
    _vec_to_metres
)

def test_mm_to_metres_conversion():
    """Test basic mm to metres conversion"""
    assert _to_metres(1000.0) == 1.0
    assert _to_metres(3000.0) == 3.0
    assert _to_metres(0.0) == 0.0
    assert _to_metres(None) is None
    print("✓ test_mm_to_metres_conversion")

def test_i_shape_profile_units():
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

    print(f"Profile def: {profile_def}")

    # Check dimensions converted to metres
    assert profile_def['depth'] == 0.19
    assert profile_def['width'] == 0.20
    assert profile_def['web_thickness'] == 0.0065
    assert profile_def['flange_thickness'] == 0.010
    assert profile_def['fillet_radius'] == 0.018

    # Check area: mm² → m²
    expected_area = 5380.0 / 1e6
    print(f"Expected area: {expected_area}, Got: {profile_def['area']}")
    assert abs(profile_def['area'] - expected_area) < 1e-6

    # Check moments: mm⁴ → m⁴
    expected_Ix = 36920000.0 / 1e12
    print(f"Expected Ix: {expected_Ix}, Got: {profile_def['Ix']}")
    assert abs(profile_def['Ix'] - expected_Ix) < 1e-10

    expected_Iy = 13380000.0 / 1e12
    print(f"Expected Iy: {expected_Iy}, Got: {profile_def['Iy']}")
    assert abs(profile_def['Iy'] - expected_Iy) < 1e-10

    # Check section moduli: mm³ → m³
    expected_Zx = 388000.0 / 1e9
    print(f"Expected Zx: {expected_Zx}, Got: {profile_def['Zx']}")
    assert abs(profile_def['Zx'] - expected_Zx) < 1e-7

    expected_Zy = 133800.0 / 1e9
    print(f"Expected Zy: {expected_Zy}, Got: {profile_def['Zy']}")
    assert abs(profile_def['Zy'] - expected_Zy) < 1e-7

    print("✓ test_i_shape_profile_units")

if __name__ == "__main__":
    test_mm_to_metres_conversion()
    test_i_shape_profile_units()
    print("All tests passed!")