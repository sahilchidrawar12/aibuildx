
def validator_agent(full_json):
    report = {'errors': [], 'warnings': [], 'members': []}
    for m in full_json['members']:
        errs = []
        if m['length'] <= 0:
            errs.append('zero_length')
        if 'selection' not in m:
            errs.append('no_section_selected')
        report['members'].append({'id': m['id'], 'errors': errs})
        report['errors'].extend(errs)
    return report


def _segment_segment_distance(a0, a1, b0, b1):
    import numpy as _np
    u = _np.array([a1[i]-a0[i] for i in range(3)])
    v = _np.array([b1[i]-b0[i] for i in range(3)])
    w0 = _np.array([a0[i]-b0[i] for i in range(3)])
    a = _np.dot(u,u)
    b = _np.dot(u,v)
    c = _np.dot(v,v)
    d = _np.dot(u,w0)
    e = _np.dot(v,w0)
    denom = a*c - b*b
    s = 0.0
    t = 0.0
    if denom != 0.0:
        s = (b*e - c*d) / denom
        t = (a*e - b*d) / denom
    s = max(0.0, min(1.0, s))
    t = max(0.0, min(1.0, t))
    cp = _np.array(a0) + s * u
    cq = _np.array(b0) + t * v
    return float(_np.linalg.norm(cp - cq))


def clasher_agent(full_json, tol=0.02):
    clashes = []
    mems = full_json['members']
    n = len(mems)
    for i in range(n):
        for j in range(i+1, n):
            a = mems[i]
            b = mems[j]
            if a['start'] == b['start'] or a['end'] == b['end'] or a['start'] == b['end'] or a['end']==b['start']:
                continue
            d = _segment_segment_distance(a['start'], a['end'], b['start'], b['end'])
            if d < tol:
                clashes.append({'a': a['id'], 'b': b['id'], 'dist_m': d})
    return {'clashes': clashes}


def risk_detector(full_json):
    out = {'members': []}
    for m in full_json['members']:
        score = 0
        if m.get('stability', {}).get('buckling_risk') == 'high':
            score += 50
        if m.get('safety', {}).get('status') == 'review':
            score += 20
        if any(c['dist_m'] < 0.02 for c in (full_json.get('clash_list') or [])):
            score += 30
        level = 'low' if score < 20 else 'medium' if score < 60 else 'high'
        out['members'].append({'id': m['id'], 'risk_score': score, 'risk_level': level})
    return out


def reporter_agent(full_json, out_dir=None):
    import csv
    bom = []
    for m in full_json['members']:
        sel = m.get('selection', {})
        bom.append({'id': m['id'], 'section': sel.get('section_name'), 'weight_kg': sel.get('weight_kg', 0)})
    return {'bom': bom, 'members': full_json['members']}


def correction_loop(full_json, max_iters=5):
    model = full_json
    for it in range(max_iters):
        clashes = clasher_agent(model)['clashes']
        val = validator_agent(model)
        if not clashes and not val['errors']:
            model['correction_iters'] = it
            return model
        for c in clashes:
            a = next((m for m in model['members'] if m['id']==c['a']), None)
            b = next((m for m in model['members'] if m['id']==c['b']), None)
            if a and b:
                v = a['orientation']
                a['start'] = [a['start'][0]+0.01*v[0], a['start'][1]+0.01*v[1], a['start'][2]+0.01*v[2]]
                a['end'] = [a['end'][0]+0.01*v[0], a['end'][1]+0.01*v[1], a['end'][2]+0.01*v[2]]
        model = engineer_standardize({'members': [{'start': m['start'], 'end': m['end'], 'length': length(m['start'], m['end']), 'layer': m.get('layer')} for m in model['members']]})
        model = load_path_resolver(model)
        model = stability_agent(model)
        model = optimizer_agent(model)
        model = connection_designer(model)
        model = fabrication_detailing(model)
        model = fabrication_standards(model)
        model = erection_planner(model)
        model = safety_compliance(model)
        model['clash_list'] = clasher_agent(model)['clashes']
    model['correction_iters'] = max_iters
    return model


class Pipeline:
    def __init__(self):
        pass

    def run_from_dxf_entities(self, dxf_entities, out_dir=None):
        a = miner_from_dxf(dxf_entities)
        b = engineer_standardize(a)
        c = load_path_resolver(b)
        d = stability_agent(c)
        e = optimizer_agent(d)
        f = connection_designer(e)
        g = fabrication_detailing(f)
        h = fabrication_standards(g)
        i = erection_planner(h)
        j = safety_compliance(i)
        k = analysis_model_generator(j)
        l = builder_ifc(h, out_path=os.path.join(out_dir or 'outputs','model.ifc'))
        v = validator_agent(h)
        clash = clasher_agent(h)
        h['clash_list'] = clash['clashes']
        r = risk_detector({**h, 'clash_list': clash['clashes']})
        rep = reporter_agent(h, out_dir=out_dir)
        final = correction_loop(h)
        return {
            'miner': a,
            'engineer': b,
            'loads': c,
            'stability': d,
            'optimizer': e,
            'connections': f,
            'fabrication': g,
            'standards': h,
            'erection': i,
            'safety': j,
            'analysis': k,
            'ifc': l,
            'validator': v,
            'clashes': clash,
            'risk': r,
            'reporter': rep,
            'final': final
        }


if __name__ == '__main__':
    sample = [
        {'start': [0,0,0], 'end': [5,0,0], 'layer': 'BEAMS'},
        {'start': [5,0,0], 'end': [5,0,3], 'layer': 'COLUMNS'},
        {'start': [0,0,0], 'end': [0,5,0], 'layer': 'BEAMS'},
    ]
    p = Pipeline()
    out = p.run_from_dxf_entities(sample, out_dir='outputs')
    print(json.dumps({'summary': {'members': len(out['miner']['members']), 'ifc': out['ifc']}}, indent=2))
"""
Minimal prototype implementation of the 17-agent structural steel pipeline.
Each agent accepts and returns Python dicts (JSON-serializable) to chain them.
Heuristics are provided and designed so ML models can be plugged in.
"""
import math
import json
import uuid
    try:
        import ifcopenshell
    except Exception:
        return {'ifc': None, 'note': 'ifcopenshell not installed, returning JSON fallback', 'model_json': full_json}

    if out_path is None:
        out_path = os.path.join('outputs', 'model.ifc')

    ifc = ifcopenshell.file(schema='IFC4')
    # simple header and owner history
    person = ifc.create_entity('IfcPerson', GivenName='AI')
    org = ifc.create_entity('IfcOrganization', Name='aibuildx')
    person_and_org = ifc.create_entity('IfcPersonAndOrganization', ThePerson=person, TheOrganization=org)
    app = ifc.create_entity('IfcApplication', ApplicationDeveloper=org, Version='0.1')
    ow_hist = ifc.create_entity('IfcOwnerHistory', OwningUser=person_and_org, OwningApplication=app)

    project = ifc.create_entity('IfcProject', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='AI Project', OwnerHistory=ow_hist)
    context = ifc.create_entity('IfcGeometricRepresentationContext', ContextIdentifier='Model', ContextType='Model', CoordinateSpaceDimension=3, Precision=1e-5)
    project.RepresentationContexts = [context]

    site = ifc.create_entity('IfcSite', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Site')
    building = ifc.create_entity('IfcBuilding', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Building')
    storey = ifc.create_entity('IfcBuildingStorey', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Storey')

    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=project, RelatedObjects=[site])
    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=site, RelatedObjects=[building])
    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=building, RelatedObjects=[storey])

    # small geometry catalog: map section name -> geometry dims (mm -> m)
    SECTION_GEOM = {
        'W8x10': {'type': 'I', 'width': 0.203, 'depth': 0.203, 'web_thk': 0.005, 'flange_thk': 0.006},
        'W10x12': {'type': 'I', 'width': 0.254, 'depth': 0.254, 'web_thk': 0.006, 'flange_thk': 0.007},
        'HSS100x100x6': {'type': 'Rect', 'width': 0.100, 'depth': 0.100, 'thickness': 0.006}
    }

    products = []
    for m in full_json['members']:
        gid = ifcopenshell.guid.compress(uuid.uuid4().hex)
        name = m.get('selection', {}).get('section_name') or m.get('type')
        proxy = ifc.create_entity('IfcBuildingElementProxy', GlobalId=gid, Name=str(name))

        # create local placement at member start
        start = m['start']
        placement_point = ifc.create_entity('IfcCartesianPoint', start)
        axis2placement = ifc.create_entity('IfcAxis2Placement3D', placement_point)
        local_placement = ifc.create_entity('IfcLocalPlacement', PlacementRelTo=None, RelativePlacement=axis2placement)
        proxy.ObjectPlacement = local_placement

        # attempt to create swept geometry if section known
        geom = SECTION_GEOM.get(name)
        rep_items = []
        if geom is not None:
            # create profile
            if geom['type'] == 'I':
                prof = ifc.create_entity('IfcIShapeProfileDef', ProfileType='AREA', ProfileName=name,
                                         OverallWidth=geom['width'], OverallDepth=geom['depth'],
                                         WebThickness=geom['web_thk'], FlangeThickness=geom['flange_thk'])
            else:
                prof = ifc.create_entity('IfcRectangleProfileDef', ProfileType='AREA', ProfileName=name,
                                         XDim=geom['width'], YDim=geom['depth'])

            # extrusion direction is member axis
            axis = unit_vector(m['start'], m['end'])
            depth = m.get('length', 0.0)
            # create extrusion placement for profile (at origin)
            prof_pos = ifc.create_entity('IfcAxis2Placement3D', ifc.create_entity('IfcCartesianPoint', (0.0, 0.0, 0.0)))
            try:
                extruded = ifc.create_entity('IfcExtrudedAreaSolid', SweptArea=prof, Position=prof_pos,
                                             ExtrudedDirection=ifc.create_entity('IfcDirection', axis), Depth=depth)
                rep_items.append(extruded)
            except Exception:
                rep_items = []

        # always add PSET with semantic/fabrication data
        props = []
        def make_prop(namep, val):
            if isinstance(val, (int, float)):
                nominal = ifc.create_entity('IfcReal', float(val))
            else:
                nominal = ifc.create_entity('IfcText', str(val))
            return ifc.create_entity('IfcPropertySingleValue', Name=str(namep), NominalValue=nominal)

        props.append(make_prop('start', m['start']))
        props.append(make_prop('end', m['end']))
        props.append(make_prop('length_m', m.get('length')))
        props.append(make_prop('member_type', m.get('type')))
        sel = m.get('selection', {})
        props.append(make_prop('section', sel.get('section_name')))
        props.append(make_prop('weight_kg', sel.get('weight_kg')))

        pset = ifc.create_entity('IfcPropertySet', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Pset_AIBuildX', HasProperties=props)
        ifc.create_entity('IfcRelDefinesByProperties', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatedObjects=[proxy], RelatingPropertyDefinition=pset)

        # Create representation if we have rep_items
        if rep_items:
            shape = ifc.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body', RepresentationType='SweptSolid', Items=rep_items)
            pd = ifc.create_entity('IfcProductDefinitionShape', Representations=[shape])
            proxy.Representation = pd

        products.append(proxy)

    # contain products in storey
    ifc.create_entity('IfcRelContainedInSpatialStructure', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingStructure=storey, RelatedElements=products)

    try:
        # ensure output dir exists
        out_dir = os.path.dirname(out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        ifc.write(out_path)
        return {'ifc': out_path, 'note': 'IFC written with basic swept solids and PSETs.'}
    except Exception as e:
        return {'ifc': None, 'note': f'Failed to write IFC: {e}'}
        })
    return out


def load_path_resolver(std_json):
    # Assign simple loads based on span and type.
    members = std_json['members']
    out = {'members': []}
    for m in members:
        span = m['length']
        if m['type'] == 'beam':
            w = 5.0  # kN/m uniform load heuristic
            axial = 0.1 * span  # small axial
            moment = w * span**2 / 8.0
            shear = w * span / 2.0
        elif m['type'] == 'column':
            axial = 50.0 * (1 if span<3 else span/3)  # kN
            moment = 0.2 * axial * span
            shear = axial * 0.05
        else:  # brace
            axial = 20.0
            moment = 0.1 * axial * span
            shear = axial * 0.05
        out['members'].append({**m, 'loads': {'axial_kN': axial, 'moment_kNm': moment, 'shear_kN': shear}})
    return out


def stability_agent(loaded_json):
    out = {'members': []}
    for m in loaded_json['members']:
        L = m['length']
        # assume a neutral radius gyration r ~ 0.05*m for small sections
        r = max(0.02, 0.05 * L)
        slenderness = L / r if r>0 else float('inf')
        buckling_risk = 'low'
        if slenderness > 200:
            buckling_risk = 'high'
        elif slenderness > 120:
            buckling_risk = 'medium'
        out['members'].append({**m, 'stability': {'slenderness': slenderness, 'buckling_risk': buckling_risk}})
    return out


def optimizer_agent(stable_json):
    out = {'members': [], 'totals': {}}
    total_weight = 0.0
    total_cost = 0.0
    for m in stable_json['members']:
        axial = m['loads']['axial_kN'] * 1000.0
        moment = m['loads']['moment_kNm'] * 1000.0
        span = m['length']
        section = pick_section_for_member(axial, moment, span)
        weight = section['weight_kg_per_m'] * span
        cost = weight * section['price_per_kg']
        total_weight += weight
        total_cost += cost
        out['members'].append({**m, 'selection': {'section_name': section['name'], 'weight_kg': weight, 'estimated_cost': cost}})
    out['totals'] = {'weight_kg': total_weight, 'cost_currency': total_cost}
    return out


def connection_designer(opt_json):
    out = {'members': []}
    for m in opt_json['members']:
        # simple connection rule: bolted end plate for beams, welded for columns
        if m['type'] == 'beam':
            conn = {'type': 'bolted_end_plate', 'plate_thk_mm': 12, 'bolt_dia_mm': 20, 'bolt_count': max(4, int(m['length'] // 2))}
        elif m['type'] == 'column':
            conn = {'type': 'welded_base', 'weld_size_mm': 8}
        else:
            conn = {'type': 'gusset', 'plate_thk_mm': 10, 'bolt_count': 4}
        out['members'].append({**m, 'connection': conn})
    return out


def fabrication_detailing(conn_json):
    out = {'members': []}
    for m in conn_json['members']:
        details = {}
        # add typical copes on beam ends joining to columns
        if m['type'] == 'beam':
            details['copes'] = True
            details['holes'] = {'type': 'slotted', 'size_mm': [22, 40]}
        elif m['type'] == 'column':
            details['stiffeners'] = True
            details['bevels'] = {'on': True, 'angle_deg': 60}
        else:
            details['gusset_prep'] = 'standard'
        out['members'].append({**m, 'fabrication': details})
    return out


def fabrication_standards(fab_json):
    out = {'members': []}
    for m in fab_json['members']:
        fab = m.get('fabrication', {})
        # enforce minimum plate thickness
        if 'plate_thk_mm' in m.get('connection', {}):
            pt = m['connection']['plate_thk_mm']
            if pt < 6:
                m['connection']['plate_thk_mm'] = 6
        # ensure weld sizes meet rule-of-thumb
        if m['connection'].get('weld_size_mm') and m['connection']['weld_size_mm'] < 3:
            m['connection']['weld_size_mm'] = 3
        # hole tolerances
        if 'holes' in fab:
            fab['hole_tol_mm'] = 1.0
        out['members'].append({**m, 'fabrication': fab, 'standards_checked': True})
    return out


def erection_planner(std_json):
    # simple elevation-based sequence: highest columns first, then beams by elevation mid-point
    members = std_json['members']
    def midz(m):
        return (m['start'][2] + m['end'][2]) / 2.0
    sorted_members = sorted(members, key=lambda mm: (0 if mm['type']=='column' else 1, -midz(mm)))
    for i, m in enumerate(sorted_members):
        m['erection_order'] = i+1
    return {'members': sorted_members}


def safety_compliance(erect_json):
    out = {'members': []}
    for m in erect_json['members']:
        risk = 'ok'
        notes = []
        if m['type'] == 'column' and m['length'] > 10:
            risk = 'review'
            notes.append('temporary bracing recommended')
        if m.get('connection', {}).get('bolt_count', 0) >= 8:
            notes.append('heavy bolting operation')
        out['members'].append({**m, 'safety': {'status': risk, 'notes': notes}})
    return out


def analysis_model_generator(full_json):
    # produce a skeletal representation: nodes (unique coords) and elements with connectivity
    nodes = {}
    node_list = []
    def get_node_id(coord):
        key = tuple(round(c, 4) for c in coord)
        if key in nodes:
            return nodes[key]
        nid = len(nodes) + 1
        nodes[key] = nid
        node_list.append({'id': nid, 'coord': coord})
        return nid
    elements = []
    for m in full_json['members']:
        n1 = get_node_id(m['start'])
        n2 = get_node_id(m['end'])
        elements.append({'id': m['id'], 'n1': n1, 'n2': n2, 'section': m.get('selection', {}).get('section_name')})
    return {'nodes': node_list, 'elements': elements}


def builder_ifc(full_json, out_path=None):
    try:
        import ifcopenshell
    except Exception:
        return {'ifc': None, 'note': 'ifcopenshell not installed, returning JSON fallback', 'model_json': full_json}

    if out_path is None:
        out_path = os.path.join('outputs', 'model.ifc')

    # create minimal IFC hierarchy and proxies with PSETs containing semantic and fabrication data.
    ifc = ifcopenshell.file(schema='IFC4')
    person = ifc.create_entity('IfcPerson', GivenName='AI')
    org = ifc.create_entity('IfcOrganization', Name='aibuildx')
    person_and_org = ifc.create_entity('IfcPersonAndOrganization', ThePerson=person, TheOrganization=org)
    app = ifc.create_entity('IfcApplication', ApplicationDeveloper=org, Version='0.1')
    ow_hist = ifc.create_entity('IfcOwnerHistory', OwningUser=person_and_org, OwningApplication=app)

    project = ifc.create_entity('IfcProject', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='AI Project', OwnerHistory=ow_hist)
    context = ifc.create_entity('IfcGeometricRepresentationContext', ContextIdentifier='Model', ContextType='Model', CoordinateSpaceDimension=3, Precision=1e-5)
    project.RepresentationContexts = [context]

    site = ifc.create_entity('IfcSite', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Site')
    building = ifc.create_entity('IfcBuilding', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Building')
    storey = ifc.create_entity('IfcBuildingStorey', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Storey')

    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=project, RelatedObjects=[site])
    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=site, RelatedObjects=[building])
    ifc.create_entity('IfcRelAggregates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingObject=building, RelatedObjects=[storey])

    products = []
    for m in full_json['members']:
        gid = ifcopenshell.guid.compress(uuid.uuid4().hex)
        name = m.get('selection', {}).get('section_name') or m.get('type')
        proxy = ifc.create_entity('IfcBuildingElementProxy', GlobalId=gid, Name=str(name))

        # create a simple property set with start/end/length/section and fabrication notes
        props = []
        def make_single(name, val):
            if isinstance(val, (int, float)):
                nominal = ifc.create_entity('IfcReal', val)
            else:
                nominal = ifc.create_entity('IfcText', str(val))
            return ifc.create_entity('IfcPropertySingleValue', Name=str(name), NominalValue=nominal)

        props.append(make_single('start', m['start']))
        props.append(make_single('end', m['end']))
        props.append(make_single('length_m', m.get('length')))
        props.append(make_single('member_type', m.get('type')))
        sel = m.get('selection', {})
        props.append(make_single('section', sel.get('section_name')))
        props.append(make_single('weight_kg', sel.get('weight_kg')))

        pset = ifc.create_entity('IfcPropertySet', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Pset_AIBuildX', HasProperties=props)
        ifc.create_entity('IfcRelDefinesByProperties', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatedObjects=[proxy], RelatingPropertyDefinition=pset)

        products.append(proxy)

    ifc.create_entity('IfcRelContainedInSpatialStructure', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingStructure=storey, RelatedElements=products)

    try:
        ifc.write(out_path)
        return {'ifc': out_path, 'note': 'IFC written (proxies + PSETs). For full LOD500 include swept/solid geometry generation.'}
    except Exception as e:
        return {'ifc': None, 'note': f'Failed to write IFC: {e}'}


def validator_agent(full_json):
    report = {'errors': [], 'warnings': [], 'members': []}
    for m in full_json['members']:
        errs = []
        if m['length'] <= 0:
            errs.append('zero_length')
        if 'selection' not in m:
            errs.append('no_section_selected')
        report['members'].append({'id': m['id'], 'errors': errs})
        report['errors'].extend(errs)
    return report


def _segment_segment_distance(a0, a1, b0, b1):
    # Compute shortest distance between two segments in 3D (returns float)
    # Algorithm from geometric tools: use parametric form and clamp to segment extents
    import numpy as _np
    u = _np.array([a1[i]-a0[i] for i in range(3)])
    v = _np.array([b1[i]-b0[i] for i in range(3)])
    w0 = _np.array([a0[i]-b0[i] for i in range(3)])
    a = _np.dot(u,u)
    b = _np.dot(u,v)
    c = _np.dot(v,v)
    d = _np.dot(u,w0)
    e = _np.dot(v,w0)
    denom = a*c - b*b
    s = 0.0
    t = 0.0
    if denom != 0.0:
        s = (b*e - c*d) / denom
        t = (a*e - b*d) / denom
    s = max(0.0, min(1.0, s))
    t = max(0.0, min(1.0, t))
    cp = _np.array(a0) + s * u
    cq = _np.array(b0) + t * v
    return float(_np.linalg.norm(cp - cq))


def clasher_agent(full_json, tol=0.02):
    # Improved clash detection using exact shortest distance between 3D segments.
    clashes = []
    mems = full_json['members']
    n = len(mems)
    for i in range(n):
        for j in range(i+1, n):
            a = mems[i]
            b = mems[j]
            # ignore adjacent connections (sharing a node)
            if a['start'] == b['start'] or a['end'] == b['end'] or a['start'] == b['end'] or a['end'] == b['start']:
                continue
            d = _segment_segment_distance(a['start'], a['end'], b['start'], b['end'])
            if d < tol:
                clashes.append({'a': a['id'], 'b': b['id'], 'dist_m': d})
    return {'clashes': clashes}


def risk_detector(full_json):
    out = {'members': []}
    for m in full_json['members']:
        score = 0
        if m.get('stability', {}).get('buckling_risk') == 'high':
            score += 50
        if m.get('safety', {}).get('status') == 'review':
            score += 20
        if any(c['dist_m'] < 0.02 for c in (full_json.get('clash_list') or [])):
            score += 30
        level = 'low' if score < 20 else 'medium' if score < 60 else 'high'
        out['members'].append({'id': m['id'], 'risk_score': score, 'risk_level': level})
    return out


def reporter_agent(full_json, out_dir=None):
    # produce BOM CSV-like structure and JSON reports
    import csv
    bom = []
    for m in full_json['members']:
        sel = m.get('selection', {})
        bom.append({'id': m['id'], 'section': sel.get('section_name'), 'weight_kg': sel.get('weight_kg', 0)})
    # We return structured data (caller can write CSVs)
    return {'bom': bom, 'members': full_json['members']}


def correction_loop(full_json, max_iters=5):
    # Very basic auto-correction logic: try to resolve clashes by nudging members slightly or selecting bigger sections
    model = full_json
    for it in range(max_iters):
        clashes = clasher_agent(model)['clashes']
        val = validator_agent(model)
        if not clashes and not val['errors']:
            model['correction_iters'] = it
            return model
        # For each clash, nudge the shorter member slightly along normal
        for c in clashes:
            a = next((m for m in model['members'] if m['id']==c['a']), None)
            b = next((m for m in model['members'] if m['id']==c['b']), None)
            if a and b:
                # nudge a by 1cm along its orientation
                v = a['orientation']
                a['start'] = [a['start'][0]+0.01*v[0], a['start'][1]+0.01*v[1], a['start'][2]+0.01*v[2]]
                a['end'] = [a['end'][0]+0.01*v[0], a['end'][1]+0.01*v[1], a['end'][2]+0.01*v[2]]
        # Re-run some agents to re-evaluate selections and checks
        model = engineer_standardize({'members': [{'start': m['start'], 'end': m['end'], 'length': length(m['start'], m['end']), 'layer': m.get('layer')} for m in model['members']]})
        model = load_path_resolver(model)
        model = stability_agent(model)
        model = optimizer_agent(model)
        model = connection_designer(model)
        model = fabrication_detailing(model)
        model = fabrication_standards(model)
        model = erection_planner(model)
        model = safety_compliance(model)
        # attach clash info if any
        model['clash_list'] = clasher_agent(model)['clashes']
    model['correction_iters'] = max_iters
    return model


# Pipeline runner
class Pipeline:
    def __init__(self):
        pass

    def run_from_dxf_entities(self, dxf_entities, out_dir=None):
        a = miner_from_dxf(dxf_entities)
        b = engineer_standardize(a)
        c = load_path_resolver(b)
        d = stability_agent(c)
        e = optimizer_agent(d)
        f = connection_designer(e)
        g = fabrication_detailing(f)
        h = fabrication_standards(g)
        i = erection_planner(h)
        j = safety_compliance(i)
        k = analysis_model_generator(j)
        l = builder_ifc(h, out_path=None)
        v = validator_agent(h)
        clash = clasher_agent(h)
        # attach clash info
        h['clash_list'] = clash['clashes']
        r = risk_detector({**h, 'clash_list': clash['clashes']})
        rep = reporter_agent(h, out_dir=out_dir)
        final = correction_loop(h)
        return {
            'miner': a,
            'engineer': b,
            'loads': c,
            'stability': d,
            'optimizer': e,
            'connections': f,
            'fabrication': g,
            'standards': h,
            'erection': i,
            'safety': j,
            'analysis': k,
            'ifc': l,
            'validator': v,
            'clashes': clash,
            'risk': r,
            'reporter': rep,
            'final': final
        }


if __name__ == '__main__':
    # quick local test
    sample = [
        {'start': [0,0,0], 'end': [5,0,0], 'layer': 'BEAMS'},
        {'start': [5,0,0], 'end': [5,0,3], 'layer': 'COLUMNS'},
        {'start': [0,0,0], 'end': [0,5,0], 'layer': 'BEAMS'},
    ]
    p = Pipeline()
    out = p.run_from_dxf_entities(sample)
    print(json.dumps({'summary': {'members': len(out['miner']['members'])}}, indent=2))
