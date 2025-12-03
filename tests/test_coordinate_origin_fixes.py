#!/usr/bin/env python3
"""
TEST SUITE - Coordinate Origin Problem Fixes Validation

This script validates that the 5 root causes have been fixed:
1. ✅ Joint locations calculated from real intersection points
2. ✅ Plates positioned at calculated joints (not [0,0,0])
3. ✅ Member intersection detection working
4. ✅ Bolt positions using corrected base (no negative coords)
5. ✅ Weld sizes calculated per AWS D1.1 (not 0.0)
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.agents.connection_synthesis_agent import synthesize_connections


def test_1_joint_location_calculation():
    """Test 1: Verify joint locations are calculated from member intersections."""
    print("\n" + "="*80)
    print("TEST 1: Joint Location Calculation")
    print("="*80)
    
    # Create test structure: simple beam-column connection
    members = [
        {
            'id': 'column_0',
            'type': 'Column',
            'start': [0.0, 0.0, 0.0],
            'end': [0.0, 0.0, 3000.0],  # Vertical
            'profile': {'area': 20000.0, 'depth': 300, 'width': 300}
        },
        {
            'id': 'beam_0',
            'type': 'Beam',
            'start': [0.0, 0.0, 3000.0],  # Starts at column end
            'end': [6000.0, 0.0, 3000.0],  # Horizontal
            'profile': {'area': 15000.0, 'depth': 400, 'width': 200}
        }
    ]
    
    # Synthesize connections (no pre-computed joints)
    plates, bolts = synthesize_connections(members, joints=None)
    
    # Verify results
    print(f"\n✓ Generated {len(plates)} plates and {len(bolts)} bolts")
    
    if not plates:
        print("✗ FAILED: No plates generated")
        return False
    
    plate = plates[0]
    plate_pos = plate.get('position', [0, 0, 0])
    
    # Expected: plate at [0, 0, 3000] (beam-column intersection)
    expected_pos = [0.0, 0.0, 3000.0]
    distance = sum((plate_pos[i] - expected_pos[i])**2 for i in range(3)) ** 0.5
    
    print(f"\nPlate position: {plate_pos}")
    print(f"Expected position: {expected_pos}")
    print(f"Distance from expected: {distance:.2f} mm")
    
    if distance < 100:  # Within 100mm tolerance
        print("✓ PASSED: Plate positioned at beam-column intersection")
        return True
    else:
        print(f"✗ FAILED: Plate too far from expected position (distance={distance:.2f}mm)")
        return False


def test_2_no_hardcoded_zero_zero_zero():
    """Test 2: Verify plates are NOT at hardcoded [0,0,0]."""
    print("\n" + "="*80)
    print("TEST 2: No Hardcoded [0,0,0] Positions")
    print("="*80)
    
    # Create test structure
    members = [
        {
            'id': 'column_0',
            'type': 'Column',
            'start': [6000.0, 0.0, 0.0],
            'end': [6000.0, 0.0, 3000.0],
            'profile': {'area': 20000.0}
        },
        {
            'id': 'beam_1',
            'type': 'Beam',
            'start': [6000.0, 0.0, 3000.0],
            'end': [10000.0, 0.0, 3000.0],
            'profile': {'area': 15000.0}
        }
    ]
    
    plates, bolts = synthesize_connections(members)
    
    all_pass = True
    
    for plate in plates:
        pos = plate.get('position', [0, 0, 0])
        print(f"\nPlate {plate.get('id')}: position={pos}")
        
        # Check if at origin
        if pos == [0.0, 0.0, 0.0]:
            print(f"✗ FAILED: Plate at hardcoded [0,0,0]")
            all_pass = False
        elif pos == [0, 0, 0]:  # Same check with int
            print(f"✗ FAILED: Plate at hardcoded [0,0,0]")
            all_pass = False
        else:
            print(f"✓ PASSED: Plate NOT at [0,0,0]")
    
    for bolt in bolts:
        pos = bolt.get('position', [0, 0, 0])
        
        # Check for negative coordinates
        if any(coord < -10 for coord in pos):
            print(f"\n✗ FAILED: Bolt has negative coordinate: {pos}")
            all_pass = False
    
    return all_pass


def test_3_positive_coordinates():
    """Test 3: Verify no negative coordinates in bolt positions."""
    print("\n" + "="*80)
    print("TEST 3: No Negative Coordinates in Bolts")
    print("="*80)
    
    # Create test structure at positive location
    members = [
        {
            'id': 'col_pos',
            'type': 'Column',
            'start': [5000.0, 4000.0, 0.0],
            'end': [5000.0, 4000.0, 4000.0],
            'profile': {'area': 20000.0}
        },
        {
            'id': 'beam_pos',
            'type': 'Beam',
            'start': [5000.0, 4000.0, 4000.0],
            'end': [8000.0, 4000.0, 4000.0],
            'profile': {'area': 15000.0}
        }
    ]
    
    plates, bolts = synthesize_connections(members)
    
    all_pass = True
    negative_count = 0
    
    for bolt in bolts:
        pos = bolt.get('position', [0, 0, 0])
        print(f"Bolt {bolt.get('id')}: {pos}")
        
        for i, coord in enumerate(pos):
            if coord < -10:
                print(f"  ✗ Negative coordinate at axis {i}: {coord}")
                negative_count += 1
                all_pass = False
    
    if all_pass:
        print(f"\n✓ PASSED: All {len(bolts)} bolts have positive coordinates")
    else:
        print(f"\n✗ FAILED: {negative_count} bolts with negative coordinates")
    
    return all_pass


def test_4_weld_size_not_zero():
    """Test 4: Verify weld sizes are calculated (not 0.0)."""
    print("\n" + "="*80)
    print("TEST 4: Weld Sizes Calculated (Not 0.0)")
    print("="*80)
    
    members = [
        {
            'id': 'col_weld',
            'type': 'Column',
            'start': [0.0, 0.0, 0.0],
            'end': [0.0, 0.0, 5000.0],
            'profile': {'area': 25000.0}
        },
        {
            'id': 'beam_weld',
            'type': 'Beam',
            'start': [0.0, 0.0, 5000.0],
            'end': [8000.0, 0.0, 5000.0],
            'profile': {'area': 18000.0}
        }
    ]
    
    plates, bolts = synthesize_connections(members)
    
    all_pass = True
    
    for plate in plates:
        weld_specs = plate.get('weld_specifications', {})
        weld_size = weld_specs.get('size_mm', 0.0)
        
        print(f"\nPlate {plate.get('id')}: weld_size={weld_size} mm")
        
        if weld_size == 0.0:
            print(f"✗ FAILED: Weld size is 0.0")
            all_pass = False
        elif weld_size < 3.0:
            print(f"✗ FAILED: Weld size too small ({weld_size} mm, min is 3.2 mm)")
            all_pass = False
        else:
            print(f"✓ PASSED: Weld size calculated ({weld_size} mm)")
    
    return all_pass


def test_5_plate_bolt_connection_tracking():
    """Test 5: Verify plates and bolts have member connection tracking."""
    print("\n" + "="*80)
    print("TEST 5: Plate-Bolt-Member Connection Tracking")
    print("="*80)
    
    members = [
        {
            'id': 'track_col',
            'type': 'Column',
            'start': [0.0, 0.0, 0.0],
            'end': [0.0, 0.0, 3000.0],
            'profile': {'area': 20000.0}
        },
        {
            'id': 'track_beam',
            'type': 'Beam',
            'start': [0.0, 0.0, 3000.0],
            'end': [6000.0, 0.0, 3000.0],
            'profile': {'area': 15000.0}
        }
    ]
    
    plates, bolts = synthesize_connections(members)
    
    all_pass = True
    
    for plate in plates:
        plate_id = plate.get('id')
        members_list = plate.get('members', [])
        
        print(f"\nPlate {plate_id}:")
        print(f"  Connected members: {members_list}")
        
        if not members_list:
            print(f"  ✗ FAILED: No member tracking")
            all_pass = False
        elif len(members_list) != 2:
            print(f"  ✗ FAILED: Expected 2 members, got {len(members_list)}")
            all_pass = False
        else:
            print(f"  ✓ PASSED: Correctly tracking {len(members_list)} members")
    
    for bolt in bolts:
        plate_ref = bolt.get('plate_id')
        if not plate_ref:
            print(f"\n✗ FAILED: Bolt {bolt.get('id')} has no plate reference")
            all_pass = False
    
    return all_pass


def test_6_multiple_connections():
    """Test 6: Verify multiple connections handled correctly."""
    print("\n" + "="*80)
    print("TEST 6: Multiple Connections in Structure")
    print("="*80)
    
    # Create a structure with 4 connections (simple frame)
    members = [
        {'id': 'col_0', 'type': 'Column', 'start': [0.0, 0.0, 0.0], 'end': [0.0, 0.0, 5000.0], 'profile': {'area': 20000.0}},
        {'id': 'col_1', 'type': 'Column', 'start': [6000.0, 0.0, 0.0], 'end': [6000.0, 0.0, 5000.0], 'profile': {'area': 20000.0}},
        {'id': 'beam_0', 'type': 'Beam', 'start': [0.0, 0.0, 5000.0], 'end': [6000.0, 0.0, 5000.0], 'profile': {'area': 15000.0}},
        {'id': 'beam_1', 'type': 'Beam', 'start': [0.0, 0.0, 2500.0], 'end': [6000.0, 0.0, 2500.0], 'profile': {'area': 12000.0}},
    ]
    
    plates, bolts = synthesize_connections(members)
    
    print(f"\nGenerated {len(plates)} plates and {len(bolts)} bolts")
    
    # Should have at least 2 connections (beam-col at top, beam-col at mid)
    if len(plates) < 2:
        print(f"✗ FAILED: Expected at least 2 plates, got {len(plates)}")
        return False
    
    # Check all plates have different positions
    positions = [tuple(p.get('position', [0, 0, 0])) for p in plates]
    unique_positions = set(positions)
    
    if len(unique_positions) != len(positions):
        print(f"✗ FAILED: Some plates at same position (duplicates detected)")
        return False
    
    print(f"✓ PASSED: All {len(plates)} plates at unique positions")
    return True


def main():
    """Run all tests."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "COORDINATE ORIGIN PROBLEM - TEST SUITE" + " "*20 + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        ("Joint Location Calculation", test_1_joint_location_calculation),
        ("No Hardcoded [0,0,0]", test_2_no_hardcoded_zero_zero_zero),
        ("Positive Coordinates", test_3_positive_coordinates),
        ("Weld Size Calculation", test_4_weld_size_not_zero),
        ("Connection Tracking", test_5_plate_bolt_connection_tracking),
        ("Multiple Connections", test_6_multiple_connections),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Coordinate origin problem FIXED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
