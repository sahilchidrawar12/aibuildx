import uuid

def _normalize_profile_value(profile):
    if profile is None:
        return 'HEA200'
    if isinstance(profile, str):
        return profile
    if isinstance(profile, dict):
        return profile.get('profile') or profile.get('name') or profile.get('profile_name') or 'HEA200'
    return str(profile)

def convert_pipeline_result_to_tekla_objects(result):
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

        profile = _normalize_profile_value(member.get('profile') or member.get('section'))
        material = member.get('material') or 'S355'
        object_id = member.get('id') or str(uuid.uuid4())

        objects.append({
            'id': object_id,
            'type': member_type,
            'name': member.get('name') or object_id,
            'start_point': start,
            'end_point': end,
            'profile': profile,
            'material': material
        })

    return objects, warnings

# Test
result = {
    'miner': {
        'members': [
            {
                'id': 'beam-001',
                'start': [0.0, 0.0, 0.0],
                'end': [3000.0, 0.0, 0.0],
                'length': 3000.0,
                'layer': 'BEAMS',
                'role': 'beam',
                'profile': {'name': 'HEA200'},
                'material': 'S355'
            }
        ]
    }
}
objects, warnings = convert_pipeline_result_to_tekla_objects(result)
print('Objects:', objects)
print('Warnings:', warnings)