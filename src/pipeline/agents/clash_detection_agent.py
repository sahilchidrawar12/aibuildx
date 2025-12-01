"""Clash detection agent: performs simple bounding-box clash checks (scaffold).

Returns list of clashing pair ids.
"""
from typing import Dict, Any, List, Tuple


def bbox_intersect(a: Tuple[float,float,float,float,float,float], b: Tuple[float,float,float,float,float,float]) -> bool:
    # a, b as (xmin,ymin,zmin,xmax,ymax,zmax)
    return not (a[3] < b[0] or a[0] > b[3] or a[4] < b[1] or a[1] > b[4] or a[5] < b[2] or a[2] > b[5])


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    elements = input_data.get('elements', [])
    clashes: List[Tuple[str,str]] = []
    for i in range(len(elements)):
        for j in range(i+1, len(elements)):
            a = elements[i].get('bbox')
            b = elements[j].get('bbox')
            if a and b and bbox_intersect(tuple(a), tuple(b)):
                clashes.append((elements[i].get('id'), elements[j].get('id')))
    return {'status': 'ok', 'clashes': clashes}


class ClashDetectionAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
