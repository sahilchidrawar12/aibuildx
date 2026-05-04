"""Robust miner for extracting structural members from DXF and IFC.

This module provides helpers to extract line-based members from DXF files (via ezdxf)
and to extract IfcMember/IfcBeam/IfcColumn elements from an IFC file (via ifcopenshell).

Outputs a standardized list of member dicts: {id, start, end, length, source, raw}
"""
import uuid
import math
import logging

try:
    import ezdxf
except Exception:
    ezdxf = None

try:
    import ifcopenshell
except Exception:
    ifcopenshell = None

logger = logging.getLogger(__name__)


def length(p0, p1):
    return math.dist((p0[0], p0[1], p0[2]), (p1[0], p1[1], p1[2]))


def _line_to_member(start, end, source='dxf', raw=None):
    s = (float(start[0]), float(start[1]), float(start[2]))
    e = (float(end[0]), float(end[1]), float(end[2]))
    return {'id': str(uuid.uuid4()), 'start': s, 'end': e, 'length': length(s, e), 'source': source, 'raw': raw}


def extract_from_dxf(path_or_entities):
    """Extract line-like members from a DXF file path or a list of entities.

    If `path_or_entities` is string path -> use ezdxf to read modelspace lines and LWPolylines.
    If it's already a list of dict-like entities (start/end) we pass them through.
    """
    members = []
    if isinstance(path_or_entities, str):
        if ezdxf is None:
            raise RuntimeError('ezdxf not installed')
        doc = ezdxf.readfile(path_or_entities)
        msp = doc.modelspace()
        for e in msp:
            t = e.dxftype()
            if t == 'LINE':
                start = (e.dxf.start.x, e.dxf.start.y, getattr(e.dxf.start, 'z', 0.0))
                end = (e.dxf.end.x, e.dxf.end.y, getattr(e.dxf.end, 'z', 0.0))
                members.append(_line_to_member(start, end, source='dxf', raw={'dxf_type': 'LINE'}))
            elif t in ('LWPOLYLINE', 'POLYLINE'):
                # break polyline into segments
                pts = [(float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0) for p in e.get_points()]
                for i in range(len(pts)-1):
                    members.append(_line_to_member(pts[i], pts[i+1], source='dxf', raw={'dxf_type': t}))
            # else: skip TEXT, POINT, etc.
    else:
        # assume list of start/end dicts
        for ent in path_or_entities:
            st = ent.get('start')
            ed = ent.get('end')
            if st and ed:
                members.append(_line_to_member(st, ed, source='json', raw=ent))
    return {'members': members}


def extract_from_ifc(ifc_path_or_model):
    """Extract members from an IFC file path or a loaded ifcopenshell model.

    Returns members with geometry approximated from IfcCartesianPoint coordinates where available.
    """
    if ifcopenshell is None:
        raise RuntimeError('ifcopenshell not installed')
    model = None
    if isinstance(ifc_path_or_model, str):
        model = ifcopenshell.open(ifc_path_or_model)
    else:
        model = ifc_path_or_model
    members = []
    # gather typical structural element types
    types = ['IfcMember', 'IfcBeam', 'IfcColumn', 'IfcBuildingElementProxy']
    for t in types:
        for ent in model.by_type(t):
            try:
                # attempt to read placement/representation to find end/start; fallback to bounding boxes
                # Many Ifc elements will have an ObjectPlacement and Representation - we attempt centroid only
                geom = None
                rep = ent.Representation if hasattr(ent, 'Representation') else None
                # fallback: attempt to look for IfcCartesianPoint values in attributes
                coords = None
                if hasattr(ent, 'ObjectPlacement') and getattr(ent.ObjectPlacement, 'RelativePlacement', None):
                    rp = ent.ObjectPlacement.RelativePlacement
                    if hasattr(rp, 'Location') and rp.Location:
                        p = rp.Location
                        if hasattr(p, 'Coordinates'):
                            coords = tuple(float(x) for x in p.Coordinates)
                # build a very small member if no geometry: use centroid repeated
                if coords is None:
                    coords = (0.0, 0.0, 0.0)
                # naive: store degenerate member at that point
                members.append({'id': str(uuid.uuid4()), 'start': coords, 'end': coords, 'length': 0.0, 'source': 'ifc', 'raw': {'ifc_type': t, 'name': getattr(ent, 'Name', None)}})
            except Exception:
                logger.exception('Failed to parse IFC entity %s', getattr(ent, 'GlobalId', ''))
    return {'members': members}
