"""Auto-repair / self-healing engine: fills missing data heuristically."""
from typing import List, Dict,Any
from .profile_db import profile_mapper, MATERIAL_CATALOG
from .node_resolution import auto_generate_joints
from .logging_setup import get_logger

logger = get_logger("auto_repair")

def infer_missing_profiles(members: List[Dict[str,Any]]):
    for m in members:
        if not m.get('profile'):
            prof = profile_mapper(m.get('tag') or m.get('label') or m.get('annotation', ''), layer=m.get('layer'))
            if prof:
                m['profile'] = prof
                logger.info("Inferred profile for member %s", m.get('id'))

def infer_materials(entities: List[Dict[str,Any]]):
    for e in entities:
        if not e.get('material'):
            # guess by role
            role = (e.get('role') or '').lower()
            if 'column' in role:
                e['material'] = {"name":"S355", **MATERIAL_CATALOG['S355']}
            else:
                e['material'] = {"name":"S235", **MATERIAL_CATALOG['S235']}
            logger.info("Assigned default material %s to %s", e['material']['name'], e.get('id'))

def repair_pipeline(input_payload: Dict[str,Any]) -> Dict[str,Any]:
    members = input_payload.get('members', [])
    plates = input_payload.get('plates', [])
    infer_missing_profiles(members)
    infer_materials(members)
    # ensure nodes/joints
    joints = auto_generate_joints(members)
    input_payload.setdefault('joints', joints)
    logger.info("Auto repair completed. Members:%d Plates:%d Joints:%d", len(members), len(plates), len(joints))
    return input_payload
