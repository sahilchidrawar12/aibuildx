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
    nodes, updated = snap_nodes(members, tolerance)
    # ensure continuity at intersections: if a node has >2 connections, mark as joint
    counts = {}
    for m in updated:
        counts.setdefault(m.get('node_start'), 0)
        counts.setdefault(m.get('node_end'), 0)
        counts[m['node_start']] += 1
        counts[m['node_end']] += 1
    joints = [n for n in nodes if counts.get(n['id'],0) > 2]
    logger.info("Generated %d joints", len(joints))
    return joints
