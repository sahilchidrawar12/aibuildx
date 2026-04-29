#!/usr/bin/env python3
"""
Simple validation test for Tekla objects and IFC generation.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def load_sample_data():
    """Load sample pipeline result."""
    output_dirs = [
        '/Users/sahil/Documents/aibuildx/outputs/04664a46',
        '/Users/sahil/Documents/aibuildx/outputs/062e2ad6'
    ]

    for output_dir in output_dirs:
        result_path = f"{output_dir}/result.json"
        if Path(result_path).exists():
            with open(result_path, 'r') as f:
                return json.load(f)

    # Fallback synthetic data
    return {
        "miner": {
            "members": [
                {
                    "id": "beam_1",
                    "start": [0.0, 0.0, 0.0],
                    "end": [3000.0, 0.0, 0.0],
                    "length": 3000.0,
                    "layer": "BEAMS",
                    "role": "beam",
                    "profile": "HEA200",
                    "material": "S355",
                    "rotation": 0.0,
                    "dir": [1.0, 0.0, 0.0]
                },
                {
                    "id": "column_1",
                    "start": [0.0, 0.0, 0.0],
                    "end": [0.0, 0.0, 3000.0],
                    "length": 3000.0,
                    "layer": "COLUMNS",
                    "role": "column",
                    "profile": "HEA300",
                    "material": "S235",
                    "dir": [0.0, 0.0, 1.0]
                }
            ]
        }
    }

def convert_pipeline_result_to_tekla_objects(result):
    """Fixed conversion function."""
    objects = []
    warnings = []

    if not isinstance(result, dict):
        return objects, ['Pipeline result is not a JSON object']

    members = result.get('miner', {}).get('members', [])
    if not isinstance(members, list):
        members = []

    for member in members:
        if not isinstance(member, dict):
            continue

        start = member.get('start') or member.get('start_point') or []
        end = member.get('end') or member.get('end_point') or []

        if not (isinstance(start, list) and isinstance(end, list) and len(start) == 3 and len(end) == 3):
            warnings.append(f"Skipping member {member.get('id', 'unknown')}: invalid geometry")
            continue

        if start == end:
            warnings.append(f"Skipping member {member.get('id', 'unknown')}: zero-length geometry")
            continue

        member_type = str(member.get('type', 'beam')).lower()
        if member_type not in {'beam', 'column'}:
            member_type = 'beam'

        # Normalize profile
        profile = _normalize_profile_value(member.get('profile') or member.get('section'))

        # Normalize material
        material = _normalize_material_value(member.get('material'))

        object_id = member.get('id') or str(uuid.uuid4())

        tekla_obj = {
            'id': object_id,
            'type': member_type,
            'name': member.get('name') or object_id,
            'start_point': start,
            'end_point': end,
            'profile': profile,
            'material': material
        }

        # Add rotation_angle for beams
        if member_type == 'beam':
            tekla_obj['rotation_angle'] = float(member.get('rotation', 0.0))

        objects.append(tekla_obj)

    return objects, warnings

def _normalize_profile_value(profile):
    if profile is None:
        return 'HEA200'
    if isinstance(profile, str):
        return profile
    if isinstance(profile, dict):
        return profile.get('profile') or profile.get('name') or profile.get('profile_name') or 'HEA200'
    return str(profile)

def _normalize_material_value(material):
    if material is None:
        return 'S355'
    if isinstance(material, str):
        return material
    if isinstance(material, dict):
        return material.get('name') or 'S355'
    return str(material)

def validate_tekla_objects(objects):
    """Validate Tekla objects."""
    errors = []
    for i, obj in enumerate(objects):
        if 'rotation_angle' not in obj and obj.get('type') == 'beam':
            errors.append(f"Beam {i} missing rotation_angle")
        if not isinstance(obj.get('start_point'), list) or len(obj.get('start_point', [])) != 3:
            errors.append(f"Object {i} invalid start_point")
        if not isinstance(obj.get('end_point'), list) or len(obj.get('end_point', [])) != 3:
            errors.append(f"Object {i} invalid end_point")
    return errors

def test_ifc_generation():
    """Test IFC generation."""
    try:
        from pipeline.ifc_generator import export_ifc_model

        # Sample data
        members = [
            {
                'id': 'beam_1',
                'start': [0.0, 0.0, 0.0],
                'end': [3000.0, 0.0, 0.0],
                'length': 3000.0,
                'layer': 'BEAMS',
                'profile': {'name': 'HEA200', 'depth': 190, 'width': 200, 'area': 5380},
                'material': {'name': 'S355'},
                'dir': [1.0, 0.0, 0.0]
            }
        ]

        ifc_data = export_ifc_model(members, [], [])
        return len(ifc_data.get('beams', [])) > 0, "IFC generation successful"
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 Testing Tekla Objects and IFC Generation\n")

    # Load data
    data = load_sample_data()
    members = data.get('miner', {}).get('members', [])
    print(f"📊 Loaded {len(members)} members from pipeline output")

    # Test Tekla conversion
    print("\n1️⃣ Testing Tekla Object Conversion...")
    import uuid
    tekla_objects, warnings = convert_pipeline_result_to_tekla_objects(data)
    print(f"   Converted {len(tekla_objects)} objects")

    if warnings:
        print(f"   ⚠️  Warnings: {warnings}")

    # Validate
    errors = validate_tekla_objects(tekla_objects)
    if errors:
        print(f"   ❌ Validation errors: {len(errors)}")
        for error in errors[:3]:
            print(f"      - {error}")
    else:
        print("   ✅ All objects valid")

    # Test IFC
    print("\n2️⃣ Testing IFC Generation...")
    ifc_success, ifc_message = test_ifc_generation()
    print(f"   {'✅' if ifc_success else '❌'} {ifc_message}")

    # Summary
    print("\n📈 SUMMARY")
    print("=" * 30)
    tekla_pass = len(errors) == 0
    total_tests = 2
    passed = (1 if tekla_pass else 0) + (1 if ifc_success else 0)
    print(f"Tekla Objects: {'✅ PASS' if tekla_pass else '❌ FAIL'}")
    print(f"IFC Generation: {'✅ PASS' if ifc_success else '❌ FAIL'}")
    print(f"Success Rate: {passed}/{total_tests} ({passed/total_tests*100:.1f}%)")

    if not tekla_pass or not ifc_success:
        print("\n🔧 ISSUES FOUND:")
        if not tekla_pass:
            print("   - Tekla objects have validation errors")
        if not ifc_success:
            print("   - IFC generation failed")

    return passed == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)