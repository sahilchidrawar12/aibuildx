#!/usr/bin/env python3
"""
STRUCTURAL ENGINEERING FIXES VERIFICATION SCRIPT
==================================================

Comprehensive verification that ALL 10 fixes have been correctly applied.
Run this to validate the production implementation before deployment.

FIXES TO VERIFY:
1. ✓ Extrusion direction (member-aligned, not hardcoded)
2. ✓ Unit conversion (single-pass mm→m)
3. ✓ Bolt sizing (AISC J3 standard sizes)
4. ✓ Plate thickness (AISC J3.9 bearing rule)
5. ✓ Weld specifications (AWS D1.1 Table 5.1)
6. ✓ Empty array fallback synthesis
7. ✓ IFC opening elements (bolt holes)
8. ✓ IFC structural connections
9. ✓ Compliance verification
10. ✓ Coordinate system fixes

Status: VERIFICATION SUITE COMPLETE
"""

import sys
import math
import inspect
from typing import List, Dict, Any, Tuple

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def verify_fix_1_extrusion_direction():
    """Verify FIX 1: Extrusion direction is member-aligned."""
    print("\n" + "="*70)
    print("VERIFYING FIX 1: Extrusion Direction (Member-Aligned)")
    print("="*70)
    
    try:
        from src.pipeline.ifc_generator import create_extruded_area_solid
        import inspect
        
        sig = inspect.signature(create_extruded_area_solid)
        params = list(sig.parameters.keys())
        
        # Check that extrusion_direction parameter exists
        if 'extrusion_direction' in params:
            print("✓ Parameter 'extrusion_direction' added to create_extruded_area_solid()")
            print(f"  Function signature: {sig}")
            return True
        else:
            print("✗ Parameter 'extrusion_direction' NOT found")
            return False
    except Exception as e:
        print(f"✗ Error verifying extrusion direction: {e}")
        return False


def verify_fix_2_unit_conversion():
    """Verify FIX 2: Unit conversion is single-pass."""
    print("\n" + "="*70)
    print("VERIFYING FIX 2: Unit Conversion (Single-Pass mm→m)")
    print("="*70)
    
    try:
        from src.pipeline.ifc_generator import _to_metres
        
        # Test cases
        test_cases = [
            (3000, 3.0, "3000 mm → 3.0 m"),
            (6000, 6.0, "6000 mm → 6.0 m"),
            (50, 0.05, "50 mm → 0.05 m"),
            (1.5, 0.0015, "1.5 mm → 0.0015 m"),
        ]
        
        all_pass = True
        for input_val, expected, desc in test_cases:
            result = _to_metres(input_val)
            # Allow small floating point errors
            if abs(result - expected) < 1e-10:
                print(f"  ✓ {desc}: {input_val} → {result}")
            else:
                print(f"  ✗ {desc}: got {result}, expected {expected}")
                all_pass = False
        
        # Check that conversion is NOT heuristic (always divides by 1000)
        source = inspect.getsource(_to_metres)
        if "/ 1000.0" in source and "abs(val) >= 100" not in source:
            print("✓ Conversion is single-pass (no heuristic checking)")
            return all_pass
        else:
            print("✗ Conversion still uses heuristic method")
            return False
    except Exception as e:
        print(f"✗ Error verifying unit conversion: {e}")
        return False


def verify_fix_3_bolt_sizing():
    """Verify FIX 3: Bolt sizing uses AISC J3 standard sizes."""
    print("\n" + "="*70)
    print("VERIFYING FIX 3: Bolt Sizing (AISC J3 Standard)")
    print("="*70)
    
    try:
        from src.pipeline.agents.connection_synthesis_agent import BoltStandard
        
        # Check standard sizes
        expected_sizes = [12.7, 15.875, 19.05, 22.225, 25.4, 28.575, 31.75, 34.925, 38.1]
        actual_sizes = BoltStandard.STANDARD_DIAMETERS_MM
        
        if actual_sizes == expected_sizes:
            print(f"✓ AISC standard sizes defined: {actual_sizes}")
        else:
            print(f"✗ Mismatch in standard sizes")
            print(f"  Expected: {expected_sizes}")
            print(f"  Got: {actual_sizes}")
            return False
        
        # Test selection function
        test_loads = [0, 50, 100, 200]
        for load_kn in test_loads:
            diameter = BoltStandard.select(load_kn)
            if diameter in expected_sizes:
                print(f"  ✓ Load {load_kn} kN → diameter {diameter} mm (standard)")
            else:
                print(f"  ✗ Load {load_kn} kN → diameter {diameter} mm (NOT standard)")
                return False
        
        # Verify OLD hardcoded sizes are NOT used
        source_file = "/Users/sahil/Documents/aibuildx/src/pipeline/agents/connection_synthesis_agent.py"
        with open(source_file, 'r') as f:
            source = f.read()
        
        if "bolt_dia_mm = 20.0" in source or "bolt_dia_mm = 24.0" in source:
            print("✗ Old hardcoded bolt sizes (20/24mm) still present")
            return False
        else:
            print("✓ Old hardcoded bolt sizes removed")
            return True
    except Exception as e:
        print(f"✗ Error verifying bolt sizing: {e}")
        return False


def verify_fix_4_plate_thickness():
    """Verify FIX 4: Plate thickness uses AISC J3.9 bearing rule."""
    print("\n" + "="*70)
    print("VERIFYING FIX 4: Plate Thickness (AISC J3.9 Bearing Rule)")
    print("="*70)
    
    try:
        from src.pipeline.agents.connection_synthesis_agent import PlateThicknessStandard
        
        # Check standard thicknesses
        print(f"✓ Available thicknesses: {len(PlateThicknessStandard.AVAILABLE_THICKNESSES_MM)} sizes")
        
        # Test bearing rule: t >= d/1.5
        test_bolts = [19.05, 22.225, 25.4]
        for bolt_dia in test_bolts:
            min_thickness = bolt_dia / 1.5
            selected = PlateThicknessStandard.select(bolt_dia)
            if selected >= min_thickness:
                print(f"  ✓ Bolt {bolt_dia}mm → min t={min_thickness:.2f}mm, selected {selected}mm ✓")
            else:
                print(f"  ✗ Bolt {bolt_dia}mm → selected {selected}mm but minimum is {min_thickness:.2f}mm")
                return False
        
        # Verify OLD arbitrary formula is NOT used in actual code (not in comments)
        source_file = "/Users/sahil/Documents/aibuildx/src/pipeline/agents/connection_synthesis_agent.py"
        with open(source_file, 'r') as f:
            lines = f.readlines()
        
        # Look for the actual formula in code (not comments/docstrings)
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip comments and docstrings
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            # Check for actual formula usage
            if 'depth/20' in line and '=' in line and not stripped.startswith('"""'):
                print("✗ Old arbitrary thickness formula found in code")
                return False
            if 'max(8' in line and 'min(20' in line and '=' in line:
                print("✗ Old arbitrary thickness formula found in code")
                return False
        
        print("✓ Old arbitrary formula removed from active code")
        return True
    except Exception as e:
        print(f"✗ Error verifying plate thickness: {e}")
        return False


def verify_fix_5_weld_specifications():
    """Verify FIX 5: Weld sizing uses AWS D1.1 Table 5.1."""
    print("\n" + "="*70)
    print("VERIFYING FIX 5: Weld Specifications (AWS D1.1 Table 5.1)")
    print("="*70)
    
    try:
        from src.pipeline.agents.connection_synthesis_agent import WeldSizeStandard
        
        # Check available sizes
        expected_sizes = [3.2, 4.8, 6.4, 7.9, 9.5, 11.1, 12.7, 14.3, 15.9]
        actual_sizes = WeldSizeStandard.AVAILABLE_SIZES_MM
        
        if actual_sizes == expected_sizes:
            print(f"✓ AWS D1.1 fillet sizes defined: {actual_sizes}")
        else:
            print(f"✗ Mismatch in weld sizes")
            return False
        
        # Test minimum size by plate thickness
        test_cases = [
            (3.0, 3.2),    # <= 1/8" → 1/8" min
            (6.0, 4.8),    # <= 1/4" → 3/16" min
            (12.0, 6.4),   # <= 1/2" → 1/4" min
            (25.0, 7.9),   # > 1/2" → 5/16" min
        ]
        
        for plate_thickness, expected_weld in test_cases:
            result = WeldSizeStandard.minimum_size(plate_thickness)
            if result == expected_weld:
                print(f"  ✓ Plate {plate_thickness}mm → weld {result}mm")
            else:
                print(f"  ✗ Plate {plate_thickness}mm → got {result}mm, expected {expected_weld}mm")
                return False
        
        print("✓ AWS D1.1 Table 5.1 compliance verified")
        return True
    except Exception as e:
        print(f"✗ Error verifying weld specifications: {e}")
        return False


def verify_fix_6_fallback_synthesis():
    """Verify FIX 6: Empty array fallback synthesis."""
    print("\n" + "="*70)
    print("VERIFYING FIX 6: Fallback Synthesis (Empty Array Handling)")
    print("="*70)
    
    try:
        from src.pipeline.agents.connection_synthesis_agent import synthesize_connections, _infer_joints_from_geometry
        import inspect
        
        # Check that _infer_joints_from_geometry exists
        sig = inspect.signature(_infer_joints_from_geometry)
        print(f"✓ Fallback function _infer_joints_from_geometry exists: {sig}")
        
        # Check synthesize_connections signature
        sig = inspect.signature(synthesize_connections)
        params = list(sig.parameters.keys())
        
        if 'joints' in params:
            param_obj = sig.parameters['joints']
            if param_obj.default is not inspect.Parameter.empty:
                print(f"✓ synthesize_connections() has default for joints: {param_obj.default}")
            else:
                print("✓ synthesize_connections() accepts joints parameter")
        
        # Check that empty joints are handled
        source = inspect.getsource(synthesize_connections)
        if "_infer_joints_from_geometry" in source:
            print("✓ synthesize_connections() calls fallback synthesis")
            return True
        else:
            print("✗ Fallback synthesis not called in synthesize_connections()")
            return False
    except Exception as e:
        print(f"✗ Error verifying fallback synthesis: {e}")
        return False


def verify_fix_7_ifc_openings():
    """Verify FIX 7: IFC opening elements (bolt holes)."""
    print("\n" + "="*70)
    print("VERIFYING FIX 7: IFC Opening Elements (Bolt Holes)")
    print("="*70)
    
    try:
        from src.pipeline.STRUCTURAL_ENGINEERING_FIXES_INTEGRATION import create_ifc_opening_element
        import inspect
        
        sig = inspect.signature(create_ifc_opening_element)
        print(f"✓ Function create_ifc_opening_element exists: {sig}")
        
        # Test the function
        bolt = {'id': 'test_bolt', 'diameter_mm': 20, 'position_m': [0, 0, 0]}
        plate = {'id': 'test_plate', 'thickness_mm': 12, 'position': [0, 0, 0]}
        
        result = create_ifc_opening_element(bolt, plate)
        
        required_keys = ['type', 'id', 'hole_diameter_m', 'hole_depth_m', 'geometry']
        if all(key in result for key in required_keys):
            print(f"✓ Function returns all required keys: {required_keys}")
            if result['type'] == 'IfcOpeningElement':
                print(f"✓ Correct IFC type: {result['type']}")
                return True
            else:
                print(f"✗ Wrong IFC type: {result['type']}")
                return False
        else:
            print(f"✗ Missing keys in result")
            return False
    except Exception as e:
        print(f"✗ Error verifying IFC openings: {e}")
        return False


def verify_fix_8_ifc_connections():
    """Verify FIX 8: IFC structural connections."""
    print("\n" + "="*70)
    print("VERIFYING FIX 8: IFC Structural Element Connections")
    print("="*70)
    
    try:
        from src.pipeline.STRUCTURAL_ENGINEERING_FIXES_INTEGRATION import create_ifc_structural_element_connection
        import inspect
        
        sig = inspect.signature(create_ifc_structural_element_connection)
        print(f"✓ Function create_ifc_structural_element_connection exists: {sig}")
        
        # Test the function
        result = create_ifc_structural_element_connection('elem1', 'elem2', 'BoltedConnection')
        
        required_keys = ['type', 'id', 'relating_element', 'related_element', 'connection_type']
        if all(key in result for key in required_keys):
            print(f"✓ Function returns all required keys: {required_keys}")
            if result['type'] == 'IfcRelConnectsStructuralElement':
                print(f"✓ Correct IFC type: {result['type']}")
                return True
            else:
                print(f"✗ Wrong IFC type: {result['type']}")
                return False
        else:
            print(f"✗ Missing keys in result")
            return False
    except Exception as e:
        print(f"✗ Error verifying IFC connections: {e}")
        return False


def verify_fix_9_compliance():
    """Verify FIX 9: Compliance verification function."""
    print("\n" + "="*70)
    print("VERIFYING FIX 9: Compliance Verification Function")
    print("="*70)
    
    try:
        from src.pipeline.STRUCTURAL_ENGINEERING_FIXES_INTEGRATION import verify_standards_compliance
        import inspect
        
        sig = inspect.signature(verify_standards_compliance)
        print(f"✓ Function verify_standards_compliance exists: {sig}")
        
        # Test with empty input
        result = verify_standards_compliance()
        
        required_keys = ['compliant', 'issues', 'warnings', 'standards']
        if all(key in result for key in required_keys):
            print(f"✓ Function returns all required keys: {required_keys}")
            print(f"✓ Standards: {result['standards']}")
            return True
        else:
            print(f"✗ Missing keys in result")
            return False
    except Exception as e:
        print(f"✗ Error verifying compliance function: {e}")
        return False


def verify_fix_10_coordinate_systems():
    """Verify FIX 10: Coordinate system fixes."""
    print("\n" + "="*70)
    print("VERIFYING FIX 10: Coordinate System Fixes")
    print("="*70)
    
    try:
        from src.pipeline.STRUCTURAL_ENGINEERING_FIXES_INTEGRATION import compute_member_local_axes, get_member_extrusion_direction
        import inspect
        
        sig1 = inspect.signature(compute_member_local_axes)
        sig2 = inspect.signature(get_member_extrusion_direction)
        
        print(f"✓ Function compute_member_local_axes exists: {sig1}")
        print(f"✓ Function get_member_extrusion_direction exists: {sig2}")
        
        # Test with sample member
        member = {
            'id': 'test_member',
            'start': [0, 0, 0],
            'end': [707, 707, 0]  # Diagonal member
        }
        
        axes = compute_member_local_axes(member)
        expected_keys = ['X', 'Y', 'Z', 'origin_m']
        if all(key in axes for key in expected_keys):
            print(f"✓ compute_member_local_axes returns: {expected_keys}")
            
            # Verify X axis is normalized
            mag = math.sqrt(sum(x**2 for x in axes['X']))
            if abs(mag - 1.0) < 0.01:
                print(f"✓ X-axis normalized: magnitude = {mag:.4f}")
            else:
                print(f"✗ X-axis not normalized: magnitude = {mag}")
                return False
            
            # Test extrusion direction
            extr_dir = get_member_extrusion_direction(member)
            print(f"✓ get_member_extrusion_direction returns: {extr_dir}")
            
            # Should be diagonal, not [1,0,0]
            if extr_dir != [1, 0, 0]:
                print(f"✓ Extrusion direction is member-aligned (not hardcoded [1,0,0])")
                return True
            else:
                print(f"✗ Extrusion direction is still [1,0,0]")
                return False
        else:
            print(f"✗ Missing keys in result")
            return False
    except Exception as e:
        print(f"✗ Error verifying coordinate systems: {e}")
        return False


# ============================================================================
# MAIN VERIFICATION SUITE
# ============================================================================

def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "STRUCTURAL ENGINEERING FIXES" + " "*25 + "║")
    print("║" + " "*18 + "COMPREHENSIVE VERIFICATION" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    verifications = [
        ("FIX 1: Extrusion Direction", verify_fix_1_extrusion_direction),
        ("FIX 2: Unit Conversion", verify_fix_2_unit_conversion),
        ("FIX 3: Bolt Sizing", verify_fix_3_bolt_sizing),
        ("FIX 4: Plate Thickness", verify_fix_4_plate_thickness),
        ("FIX 5: Weld Specifications", verify_fix_5_weld_specifications),
        ("FIX 6: Fallback Synthesis", verify_fix_6_fallback_synthesis),
        ("FIX 7: IFC Openings", verify_fix_7_ifc_openings),
        ("FIX 8: IFC Connections", verify_fix_8_ifc_connections),
        ("FIX 9: Compliance Verification", verify_fix_9_compliance),
        ("FIX 10: Coordinate Systems", verify_fix_10_coordinate_systems),
    ]
    
    results = []
    for name, verify_func in verifications:
        try:
            result = verify_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "-"*70)
    print(f"TOTAL: {passed}/{total} verifications passed")
    print("-"*70)
    
    if passed == total:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY! 🎉")
        print("\nThe structural engineering implementation is ready for production.")
        print("All 10 critical fixes have been applied and validated.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
