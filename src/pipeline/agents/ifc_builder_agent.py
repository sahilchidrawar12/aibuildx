"""IFC Builder agent: creates lightweight IFC-like export structures (scaffold).

Returns a small dictionary representing IFC entities for members.
"""
from typing import Dict, Any, List


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    members = input_data.get('members', [])
    entities: List[Dict[str, Any]] = []
    for i, m in enumerate(members):
        entities.append({'id': f'M{i}', 'type': 'IfcMember', 'length': m.get('length')})
    return {'status': 'ok', 'ifc_entities': entities}


class IFCBuilderAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
