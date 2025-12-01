"""Geometry Agent: validate geometry, global CS, node resolution, 3D generation."""
from typing import List, Dict, Any, Tuple
import math
from .logging_setup import get_logger

logger = get_logger("geometry_agent")

def set_global_coordinate_system(data: Dict[str,Any], origin: Tuple[float,float,float]=(0,0,0)):
    data.setdefault("global_cs", {})
    data["global_cs"]["origin"] = list(origin)
    logger.info("Global coordinate system set to %s", origin)
    return data

def merge_nodes(members: List[Dict[str,Any]], tolerance: float = 10.0) -> Tuple[List[Dict[str,Any]], Dict[Tuple[int,int,int], int]]:
    """Merge nodes within tolerance (mm). Returns new nodes list and mapping from raw coord to node id."""
    nodes = []
    mapping = {}
    def round_key(pt):
        return (int(round(pt[0])), int(round(pt[1])), int(round(pt[2])))

    for m in members:
        a = tuple(m.get("start", (0,0,0)))
        b = tuple(m.get("end", (0,0,0)))
        for pt in (a,b):
            key = round_key(pt)
            if key in mapping:
                continue
            # check existing nodes
            found = None
            for i,n in enumerate(nodes):
                dx = n["x"]-pt[0]
                dy = n["y"]-pt[1]
                dz = n["z"]-pt[2]
                if math.hypot(math.hypot(dx,dy),dz) <= tolerance:
                    found = i
                    break
            if found is not None:
                mapping[key] = found
            else:
                nid = len(nodes)
                nodes.append({"id": nid, "x": pt[0], "y": pt[1], "z": pt[2]})
                mapping[key] = nid

    logger.info("Merged %d nodes (tolerance=%s mm)", len(nodes), tolerance)
    return nodes, mapping

def resolve_member_orientation(member: Dict[str,Any]) -> Dict[str,Any]:
    """Compute length, direction vector, and rotation about longitudinal axis for a member."""
    s = member.get("start", (0,0,0))
    e = member.get("end", (0,0,0))
    dx = e[0]-s[0]
    dy = e[1]-s[1]
    dz = e[2]-s[2]
    L = math.hypot(math.hypot(dx,dy),dz)
    if L == 0:
        logger.warning("Zero length member encountered")
        return member
    ux,uy,uz = dx/L, dy/L, dz/L
    # rotation angle in XY-plane
    rot = math.degrees(math.atan2(uy, ux))
    member.update({"length": L, "dir": (ux,uy,uz), "rotation": rot})
    return member
