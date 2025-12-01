"""Erection sequencing heuristics: simple level-by-level and gravity-first ordering."""
from typing import List, Dict,Any

def sequence_erection(members: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    # Simple algorithm: sort by level (z of centroid) ascending, then by role (columns first)
    def z_centroid(m):
        s = m.get('start',(0,0,0))
        e = m.get('end',(0,0,0))
        return (s[2]+e[2])/2.0
    def keyfunc(m):
        role = m.get('role','')
        role_priority = 0 if 'column' in role.lower() else 1
        return (z_centroid(m), role_priority)
    ordered = sorted(members, key=keyfunc)
    # annotate sequence index
    for i,m in enumerate(ordered):
        m['erection_seq'] = i+1
    return ordered
