#!/usr/bin/env python3
"""
Structural BIM Audit - Defect Report Generator
"""

import json
import math

def main():
    # Load the structural data
    with open('outputs/integrity_converted_structural_data.json', 'r') as f:
        data = json.load(f)

    print("DEFECT REPORT - Structural BIM Audit")
    print("=" * 50)

    # 1. Material Property Validation
    print("\n1. MATERIAL PROPERTY VALIDATION:")
    materials = {}
    for member in data['result']['miner']['members']:
        mat_name = member['material']['name']
        fy = member['material']['fy']
        E = member['material']['E']
        if mat_name not in materials:
            materials[mat_name] = (fy, E)

    standards = {
        'ASTM A992': (345.0, 200000.0),
        'ASTM A572 Gr50': (345.0, 200000.0),
        'S235': (235.0, 210000.0),
        'S355': (355.0, 210000.0)
    }

    for mat, (fy, E) in materials.items():
        expected = standards.get(mat)
        if expected and abs(fy - expected[0]) < 1e-6 and abs(E - expected[1]) < 1e-6:
            print(f"  ✅ {mat}: fy={fy} MPa, E={E} MPa - COMPLIANT")
        else:
            print(f"  ❌ {mat}: fy={fy} MPa, E={E} MPa - NON-COMPLIANT")

    # 2. Object-Oriented Optimization
    print("\n2. OBJECT-ORIENTED OPTIMIZATION:")
    profiles = set(member['profile']['name'] for member in data['result']['miner']['members'])
    if len(profiles) == 1:
        print("  ✅ Single profile definition - NO BIM BLOAT")
        print("  RECOMMENDATION: Implement centralized ProfileDef reference")
    else:
        print(f"  ⚠️ {len(profiles)} unique profiles - BIM BLOAT DETECTED")
        print("  RECOMMENDATION: Consolidate to centralized ProfileDef")

    # 3. Geometric & Topological Integrity
    print("\n3. GEOMETRIC & TOPOLOGICAL INTEGRITY:")

    members = data['result']['miner']['members']

    # Collect all connection points
    connection_points = set()
    member_endpoints = {}  # member_id -> (start_tuple, end_tuple)

    for member in members:
        start = tuple(member['start'])
        end = tuple(member['end'])
        connection_points.add(start)
        connection_points.add(end)
        member_endpoints[member['id']] = (start, end)

    # Check topological connectivity
    connected_members = set()
    disconnected_ends = set()

    for member_id, (start, end) in member_endpoints.items():
        # Check if end connects to any other member's start
        end_connected = False
        for other_id, (other_start, other_end) in member_endpoints.items():
            if other_id != member_id:
                dist_to_other_start = math.sqrt(sum((a - b)**2 for a, b in zip(end, other_start)))
                if dist_to_other_start <= 1.0:  # Within 1mm tolerance
                    end_connected = True
                    connected_members.add((member_id, other_id))
                    break

        if not end_connected:
            disconnected_ends.add(member_id)

    # Report connectivity
    if connected_members:
        print(f"  ✅ Connected member pairs: {len(connected_members)}")
        for pair in sorted(connected_members):
            print(f"    {pair[0]} ↔ {pair[1]}")
    else:
        print("  ⚠️ No connected member pairs found")

    if disconnected_ends:
        print(f"  ❌ Disconnected member ends: {len(disconnected_ends)}")
        for mid in sorted(disconnected_ends):
            end_point = member_endpoints[mid][1]
            print(f"    {mid} end at {end_point} - NO CONNECTION")
    else:
        print("  ✅ All member ends are connected")

    # Check for floating structures
    z_coords = []
    for member in members:
        z_coords.extend([member['start'][2], member['end'][2]])
    min_z, max_z = min(z_coords), max(z_coords)

    # Check if structure touches ground (Z=0)
    touches_ground = any(abs(z) < 1.0 for z in z_coords)  # Within 1mm of Z=0

    if min_z >= -1.0 and touches_ground:  # Allow slight negative for tolerance
        print(f"  ✅ Z-coordinates: {min_z:.1f} to {max_z:.1f} mm - GROUNDED")
    elif min_z < -1.0:
        print(f"  ⚠️ Z-coordinates: {min_z:.1f} to {max_z:.1f} mm - BELOW GROUND")
    else:
        print(f"  ⚠️ Z-coordinates: {min_z:.1f} to {max_z:.1f} mm - FLOATING (no ground connection)")

    # Check for geometric validity (no zero-length members)
    zero_length_members = []
    for member in members:
        if member['length_mm'] < 1.0:  # Less than 1mm
            zero_length_members.append(member['id'])

    if zero_length_members:
        print(f"  ❌ Zero-length members: {zero_length_members}")
    else:
        print("  ✅ All members have valid lengths")

    # 4. Extrusion & Orientation Logic
    print("\n4. EXTRUSION & ORIENTATION LOGIC:")
    for member in members:
        start = member['start']
        end = member['end']
        length = member['length_mm']
        expected_dir = [
            (end[0] - start[0]) / length,
            (end[1] - start[1]) / length,
            (end[2] - start[2]) / length
        ]
        actual_dir = member['ifc_extruded_area_solid']['extrudedDirection']
        diff = sum(abs(a - e) for a, e in zip(actual_dir, expected_dir))
        if diff < 1e-5:
            print(f"  ✅ {member['id']}: Extrusion direction CORRECT")
        else:
            print(f"  ❌ {member['id']}: Extrusion direction MISMATCH (diff: {diff:.6f})")

    # Corrected Version
    print("\n5. CORRECTED JSON SNIPPET:")
    print("The following shows a corrected member with proper connections and optimizations:")

    # Create a corrected version for member_3 to connect to member_2
    corrected_member_3 = members[2].copy()
    corrected_member_3['start'] = [10000.0, 0.0, 5000.0]  # Connect to member_2 end

    corrected_snippet = {
        "id": "member_3_corrected",
        "start": corrected_member_3['start'],
        "end": corrected_member_3['end'],
        "profile": {"$ref": "#/definitions/W10x77_ProfileDef"},  # Centralized reference
        "material": corrected_member_3['material'],
        "ifc_extruded_area_solid": corrected_member_3['ifc_extruded_area_solid']
    }

    print(json.dumps(corrected_snippet, indent=2))

    print("\n" + "=" * 50)
    print("AUDIT COMPLETE - Issues identified and corrections proposed")

if __name__ == "__main__":
    main()