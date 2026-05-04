"""Simple clash avoidance intelligence: shift plates/bolts and check clearances."""
from typing import List, Dict,Any
import math

def bbox(entity: Dict[str,Any]) -> Dict[str,float]:
    # Very rough bounding box from start/end or outline
    if 'start' in entity and 'end' in entity:
        s = entity['start']; e = entity['end']
        xmin = min(s[0], e[0]); xmax = max(s[0], e[0])
        ymin = min(s[1], e[1]); ymax = max(s[1], e[1])
        zmin = min(s[2], e[2]); zmax = max(s[2], e[2])
        return {'xmin':xmin,'xmax':xmax,'ymin':ymin,'ymax':ymax,'zmin':zmin,'zmax':zmax}
    if 'outline' in entity:
        xs = [p[0] for p in entity['outline']]
        ys = [p[1] for p in entity['outline']]
        return {'xmin':min(xs),'xmax':max(xs),'ymin':min(ys),'ymax':max(ys),'zmin':0,'zmax':0}
    return {'xmin':0,'xmax':0,'ymin':0,'ymax':0,'zmin':0,'zmax':0}

def overlaps(a: Dict[str,float], b: Dict[str,float], clearance: float=1.0) -> bool:
    if a['xmax'] + clearance < b['xmin'] or b['xmax'] + clearance < a['xmin']:
        return False
    if a['ymax'] + clearance < b['ymin'] or b['ymax'] + clearance < a['ymin']:
        return False
    if a['zmax'] + clearance < b['zmin'] or b['zmax'] + clearance < a['zmin']:
        return False
    return True

def avoid_clashes(plates: List[Dict[str,Any]], bolts: List[Dict[str,Any]], clearance_mm: float=2.0) -> Dict[str,int]:
    shifted = 0
    for i,p in enumerate(plates):
        bi = bbox(p)
        for j,q in enumerate(plates):
            if i==j: continue
            bj = bbox(q)
            if overlaps(bi,bj, clearance=clearance_mm):
                # shift plate q slightly in z
                q.setdefault('shifted_z',0)
                q['shifted_z'] += clearance_mm
                shifted += 1
    # adjust bolts if overlapping
    for b in bolts:
        bb = bbox(b)
        for p in plates:
            bp = bbox(p)
            if overlaps(bb,bp, clearance=clearance_mm):
                b.setdefault('shifted', True)
                shifted += 1
    return {"shifted": shifted}
