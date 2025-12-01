"""Lightweight IFC generator that emits simple JSON-like IFC structures.
This is a helper for producing IfcBeam/IfcColumn/IfcPlate/IfcFastener entries.
"""
from typing import Dict, Any, List
import uuid

def _new_guid():
    return str(uuid.uuid4())

def generate_ifc_beam(member: Dict[str,Any]) -> Dict[str,Any]:
    return {"type":"IfcBeam","id": _new_guid(), "length": member.get('length'), "profile": member.get('profile'), "start": member.get('start'), "end": member.get('end')}

def generate_ifc_column(member: Dict[str,Any]) -> Dict[str,Any]:
    return {"type":"IfcColumn","id": _new_guid(), "length": member.get('length'), "profile": member.get('profile'), "start": member.get('start'), "end": member.get('end')}

def generate_ifc_plate(plate: Dict[str,Any]) -> Dict[str,Any]:
    return {"type":"IfcPlate","id": _new_guid(), "outline": plate.get('outline'), "thickness": plate.get('thickness')}

def generate_ifc_fastener(bolt: Dict[str,Any]) -> Dict[str,Any]:
    return {"type":"IfcFastener","id": _new_guid(), "diameter": bolt.get('diameter'), "position": bolt.get('pos')}

def export_ifc_model(members: List[Dict[str,Any]], plates: List[Dict[str,Any]], bolts: List[Dict[str,Any]]) -> Dict[str,Any]:
    model = {"beams":[],"columns":[],"plates":[],"fasteners":[]}
    for m in members:
        typ = m.get('role','beam').lower()
        if 'column' in typ:
            model['columns'].append(generate_ifc_column(m))
        else:
            model['beams'].append(generate_ifc_beam(m))
    for p in plates:
        model['plates'].append(generate_ifc_plate(p))
    for b in bolts:
        model['fasteners'].append(generate_ifc_fastener(b))
    return model
