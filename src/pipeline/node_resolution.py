"""Node resolution utilities to snap and auto-generate joints."""
from typing import List, Dict,Any, Tuple
import math
from .logging_setup import get_logger

logger = get_logger("node_resolution")

def snap_nodes(members: List[Dict[str,Any]], tolerance: float=10.0) -> Tuple[List[Dict[str,Any]], List[Dict[str,Any]]]:
    # use geometry_agent.merge_nodes behaviour but return updated members referencing node ids
    from .geometry_agent import merge_nodes
    nodes, mapping = merge_nodes(members, tolerance=tolerance)
    # update members to include node ids
    def key(pt):
        return (int(round(pt[0])), int(round(pt[1])), int(round(pt[2])))
    for m in members:
        m['node_start'] = mapping.get(key(tuple(m.get('start',(0,0,0)))))
        m['node_end'] = mapping.get(key(tuple(m.get('end',(0,0,0)))))
    logger.info("Snapped %d members to %d nodes", len(members), len(nodes))
    return nodes, members

def auto_generate_joints(members: List[Dict[str,Any]], tolerance: float=10.0) -> List[Dict[str,Any]]:
    """Auto-generate joints from nodes where 3+ members meet.
    
    CRITICAL FIX: Joints must include 'position' field with [x, y, z] coordinates.
    This is required by connection_synthesis and IFC generation.
    
    ALSO FIXED: Populate 'members' array with member IDs that connect at each joint.
    This is required for connection topology and IFC relationships.
    """
    nodes, updated = snap_nodes(members, tolerance)
    # ensure continuity at intersections: if a node has >2 connections, mark as joint
    counts = {}
    node_members = {}  # Track which members connect to each node
    
    for m in updated:
        node_start = m.get('node_start')
        node_end = m.get('node_end')
        member_id = m.get('id')
        
        counts.setdefault(node_start, 0)
        counts.setdefault(node_end, 0)
        counts[node_start] += 1
        counts[node_end] += 1
        
        # Track member connections to nodes
        if node_start not in node_members:
            node_members[node_start] = []
        if node_end not in node_members:
            node_members[node_end] = []
        
        if member_id not in node_members[node_start]:
            node_members[node_start].append(member_id)
        if member_id not in node_members[node_end]:
            node_members[node_end].append(member_id)
    
    # Convert nodes to joints with proper 'position' field AND member references
    joints = []
    for n in nodes:
        if counts.get(n['id'], 0) > 2:
            node_id = n['id']
            # CRITICAL FIX: Add 'position' field with [x, y, z] coordinates
            # This ensures connection_synthesis and IFC generation work correctly
            joint = {
                'id': f"joint_{node_id}",
                'position': [n['x'], n['y'], n['z']],  # ✅ FIXED: Explicit position field
                'location': [n['x'], n['y'], n['z']],  # Alternate key for IFC
                'x': n['x'],
                'y': n['y'],
                'z': n['z'],
                'node_id': node_id,
                'members': node_members.get(node_id, []),  # ✅ FIXED: Populate member references
                'type': 'Bolted',
            }
            joints.append(joint)
    
    logger.info(f"Generated {len(joints)} joints with position fields and member references")
    for j in joints:
        logger.debug(f"  Joint: id={j['id']}, position={j['position']}, members={j['members']}")
    
    return joints
