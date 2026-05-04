"""Node resolution utilities to snap and auto-generate joints."""
from typing import List, Dict,Any, Tuple
import math
from ..utils.logging_setup import get_logger

logger = get_logger("node_resolution")

def snap_nodes(members: List[Dict[str,Any]], tolerance: float=10.0) -> Tuple[List[Dict[str,Any]], List[Dict[str,Any]]]:
    # use geometry_agent.merge_nodes behaviour but return updated members referencing node ids
    from ..geometry.geometry_agent import merge_nodes
    nodes, mapping = merge_nodes(members, tolerance=tolerance)
    # update members to include node ids
    def key(pt):
        return (int(round(pt[0])), int(round(pt[1])), int(round(pt[2])))
    for m in members:
        m['node_start'] = mapping.get(key(tuple(m.get('start',(0,0,0)))))
        m['node_end'] = mapping.get(key(tuple(m.get('end',(0,0,0)))))
    logger.info("Snapped %d members to %d nodes", len(members), len(nodes))
    return nodes, members

def _member_direction(member: Dict[str,Any]) -> List[float]:
    start = member.get('start', (0,0,0))
    end = member.get('end', (0,0,0))
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.hypot(math.hypot(dx, dy), dz) or 1.0
    return [dx / length, dy / length, dz / length]


def _angle_between(v1: List[float], v2: List[float]) -> float:
    dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(v1, v2))))
    angle = math.degrees(math.acos(dot))
    return min(angle, 180.0 - angle)


def auto_generate_joints(members: List[Dict[str,Any]], tolerance: float=10.0) -> List[Dict[str,Any]]:
    """Auto-generate joints from nodes where members meet.

    Joints are generated for:
      - nodes with 3+ connected members
      - nodes with 2 connected members that are not collinear or have differing roles

    This ensures structural connections are represented for beams/columns/braces
    and improves IFC/connection synthesis topology for Tekla export.
    """
    nodes, updated = snap_nodes(members, tolerance)
    node_members = {}
    node_positions = {n['id']: (n['x'], n['y'], n['z']) for n in nodes}

    for m in updated:
        member_id = m.get('id')
        for node_key in ('node_start', 'node_end'):
            node_id = m.get(node_key)
            if node_id is None:
                continue
            node_members.setdefault(node_id, [])
            if member_id not in node_members[node_id]:
                node_members[node_id].append(member_id)

    joints = []
    for node_id, member_ids in node_members.items():
        if not member_ids:
            continue

        members_at_node = [m for m in updated if m.get('id') in member_ids]
        member_count = len(members_at_node)
        create_joint = member_count > 2
        joint_type = 'Bolted'

        if member_count == 2:
            dir1 = _member_direction(members_at_node[0])
            dir2 = _member_direction(members_at_node[1])
            angle = _angle_between(dir1, dir2)
            role1 = (members_at_node[0].get('role') or '').lower()
            role2 = (members_at_node[1].get('role') or '').lower()
            if angle > 15.0 or (role1 and role2 and role1 != role2):
                create_joint = True
                joint_type = 'Moment' if angle > 60.0 else 'Angle'
            else:
                joint_type = 'Splice'

        if not create_joint:
            continue

        position = list(node_positions.get(node_id, (0.0, 0.0, 0.0)))
        joints.append({
            'id': f"joint_{node_id}",
            'position': position,
            'location': position,
            'x': position[0],
            'y': position[1],
            'z': position[2],
            'node_id': node_id,
            'members': member_ids,
            'member_count': member_count,
            'type': joint_type,
            'connection_type': 'bolted' if joint_type != 'Splice' else 'splice',
        })

    logger.info(f"Generated {len(joints)} joints with position fields and member references")
    for j in joints:
        logger.debug(f"  Joint: id={j['id']}, position={j['position']}, members={j['members']}, type={j['type']}")

    return joints
