"""
Consolidated pipeline implementation (v2) with agents and IFC geometry exporter.
"""
import math
import json
import uuid
import os

# Small catalog
SECTION_CATALOG = [
    {"name": "W8x10", "area": 0.013, "Ixx": 8e-5, "weight_kg_per_m": 12.0, "price_per_kg": 1.2},
    {"name": "W10x12", "area": 0.020, "Ixx": 2.0e-4, "weight_kg_per_m": 17.0, "price_per_kg": 1.15},
    {"name": "HSS100x100x6", "area": 0.018, "Ixx": 1.6e-4, "weight_kg_per_m": 15.5, "price_per_kg": 1.25},
]

# section geometry approximations for IFC swept profiles
SECTION_GEOM = {
    'W8x10':{'type':'I','width':0.203,'depth':0.203,'web_thk':0.005,'flange_thk':0.006},
    'W10x12':{'type':'I','width':0.254,'depth':0.254,'web_thk':0.006,'flange_thk':0.007},
    'HSS100x100x6':{'type':'HollowRect','outer_w':0.100,'outer_h':0.100,'thickness':0.006},
    'REC200x50':{'type':'Rect','width':0.200,'depth':0.050,'thickness':0.005},
}

try:
    from .ml_models import load_member_type_classifier
except Exception:
    def load_member_type_classifier():
        return None
try:
    from .ml_models import load_section_selector
except Exception:
    def load_section_selector():
        return None


def length(p0, p1):
    return math.dist((p0[0], p0[1], p0[2]), (p1[0], p1[1], p1[2]))


def unit_vector(p0, p1):
    L = length(p0, p1)
    if L == 0:
        return (0,0,0)
    return ((p1[0]-p0[0])/L, (p1[1]-p0[1])/L, (p1[2]-p0[2])/L)


def vec_angle_deg(v):
    vx,vy,vz = v
    horiz = math.hypot(vx, vy)
    return math.degrees(math.atan2(abs(vz), horiz))


def pick_section_for_member(axial_force, bending_moment, span):
    candidates = []
    for s in SECTION_CATALOG:
        axial_capacity = s['area'] * 250e6 * 0.6
        bending_capacity = s['Ixx'] * 250e6 * 0.6 / (span/2 if span>0.01 else 0.01)
        if axial_force <= axial_capacity and bending_moment <= bending_capacity:
            cost = s['weight_kg_per_m'] * span * s['price_per_kg']
            candidates.append((cost, s))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    return SECTION_CATALOG[0]


def miner_from_dxf(dxf_entities):
    members = []
    for ent in dxf_entities:
        members.append({'id': str(uuid.uuid4()), 'start': ent['start'], 'end': ent['end'], 'length': length(ent['start'], ent['end']), 'layer': ent.get('layer')})
    return {'members': members}


def engineer_standardize(input_json):
    clf = None
    try:
        clf = load_member_type_classifier()
    except Exception:
        clf = None
    members = input_json['members']
    out = {'members': []}
    for m in members:
        v = unit_vector(m['start'], m['end'])
        angle = vec_angle_deg(v)
        typ = None
        if clf is not None:
            try:
                pred = clf.predict([[m.get('length',0.0), angle]])[0]
                typ = {0:'beam',1:'column',2:'brace'}.get(int(pred), None)
            except Exception:
                typ = None
        if typ is None:
            if angle > 60: typ = 'column'
            elif angle < 20: typ = 'beam'
            else: typ = 'brace'
        out['members'].append({'id': m['id'], 'start': m['start'], 'end': m['end'], 'length': m['length'], 'type': typ, 'orientation': v, 'layer': m.get('layer')})
    return out


def load_path_resolver(std_json):
    out = {'members': []}
    for m in std_json['members']:
        span = m['length']
        if m['type']=='beam':
            w=5.0; axial=0.1*span; moment=w*span**2/8.0; shear=w*span/2.0
        elif m['type']=='column':
            axial=50.0*(1 if span<3 else span/3); moment=0.2*axial*span; shear=axial*0.05
        else:
            axial=20.0; moment=0.1*axial*span; shear=axial*0.05
        out['members'].append({**m, 'loads': {'axial_kN': axial, 'moment_kNm': moment, 'shear_kN': shear}})
    return out


def stability_agent(loaded_json):
    out={'members':[]}
    for m in loaded_json['members']:
        L=m['length']; r=max(0.02,0.05*L); sl=L/r if r>0 else float('inf')
        br='low'
        if sl>200: br='high'
        elif sl>120: br='medium'
        out['members'].append({**m, 'stability': {'slenderness': sl, 'buckling_risk': br}})
    return out


def optimizer_agent(stable_json):
    out={'members':[],'totals':{}}
    tw=0.0; tc=0.0
    selector = None
    try:
        selector = load_section_selector()
    except Exception:
        selector = None
    for m in stable_json['members']:
        axial=m['loads']['axial_kN']*1000.0; moment=m['loads']['moment_kNm']*1000.0; span=m['length']
        section = None
        if selector is not None:
            try:
                idx = int(selector.predict([[axial, moment, span]])[0])
                # map idx to SECTION_CATALOG safely
                if 0 <= idx < len(SECTION_CATALOG):
                    section = SECTION_CATALOG[idx]
            except Exception:
                section = None
        if section is None:
            section = pick_section_for_member(axial, moment, span)
        w=section['weight_kg_per_m']*span; cost=w*section['price_per_kg']
        tw+=w; tc+=cost
        out['members'].append({**m, 'selection': {'section_name': section['name'], 'weight_kg': w, 'estimated_cost': cost}})
    out['totals']={'weight_kg':tw,'cost_currency':tc}
    return out


def connection_designer(opt_json):
    out={'members':[]}
    for m in opt_json['members']:
        if m['type']=='beam': conn={'type':'bolted_end_plate','plate_thk_mm':12,'bolt_dia_mm':20,'bolt_count':max(4,int(m['length']//2))}
        elif m['type']=='column': conn={'type':'welded_base','weld_size_mm':8}
        else: conn={'type':'gusset','plate_thk_mm':10,'bolt_count':4}
        out['members'].append({**m,'connection':conn})
    return out


def fabrication_detailing(conn_json):
    out={'members':[]}
    for m in conn_json['members']:
        details={}
        if m['type']=='beam': details['copes']=True; details['holes']={'type':'slotted','size_mm':[22,40]}
        elif m['type']=='column': details['stiffeners']=True; details['bevels']={'on':True,'angle_deg':60}
        else: details['gusset_prep']='standard'
        out['members'].append({**m,'fabrication':details})
    return out


def fabrication_standards(fab_json):
    out={'members':[]}
    for m in fab_json['members']:
        fab=m.get('fabrication',{})
        if 'plate_thk_mm' in m.get('connection',{}):
            pt=m['connection']['plate_thk_mm'];
            if pt<6: m['connection']['plate_thk_mm']=6
        if m['connection'].get('weld_size_mm') and m['connection']['weld_size_mm']<3:
            m['connection']['weld_size_mm']=3
        if 'holes' in fab: fab['hole_tol_mm']=1.0
        out['members'].append({**m,'fabrication':fab,'standards_checked':True})
    return out


def erection_planner(std_json):
    members=std_json['members']
    def midz(m): return (m['start'][2]+m['end'][2])/2.0
    sorted_members=sorted(members,key=lambda mm:(0 if mm['type']=='column' else 1,-midz(mm)))
    for i,m in enumerate(sorted_members): m['erection_order']=i+1
    return {'members':sorted_members}


def safety_compliance(erect_json):
    out={'members':[]}
    for m in erect_json['members']:
        risk='ok'; notes=[]
        if m['type']=='column' and m['length']>10: risk='review'; notes.append('temporary bracing recommended')
        if m.get('connection',{}).get('bolt_count',0)>=8: notes.append('heavy bolting operation')
        out['members'].append({**m,'safety':{'status':risk,'notes':notes}})
    return out


def analysis_model_generator(full_json):
    nodes={}; node_list=[]
    def get_node_id(coord):
        key=tuple(round(c,4) for c in coord)
        if key in nodes: return nodes[key]
        nid=len(nodes)+1; nodes[key]=nid; node_list.append({'id':nid,'coord':coord}); return nid
    elements=[]
    for m in full_json['members']:
        n1=get_node_id(m['start']); n2=get_node_id(m['end'])
        elements.append({'id':m['id'],'n1':n1,'n2':n2,'section':m.get('selection',{}).get('section_name')})
    return {'nodes':node_list,'elements':elements}


def validator_agent(full_json):
    errors=[]; warnings=[]
    for m in full_json['members']:
        if m.get('length',0.0)<=0: errors.append({'id':m['id'],'err':'nonpositive length'})
        if not m.get('selection'):
            warnings.append({'id':m['id'],'warn':'no section selected'})
    return {'errors':errors,'warnings':warnings}


def builder_ifc(full_json, out_path=None):
    try:
        import ifcopenshell
    except Exception:
        return {'ifc':None,'note':'ifcopenshell not installed, returning JSON fallback','model_json':full_json}
    if out_path is None: out_path=os.path.join('outputs','model.ifc')
    ifc=ifcopenshell.file(schema='IFC4')
    person=ifc.create_entity('IfcPerson',GivenName='AI')
    org=ifc.create_entity('IfcOrganization',Name='aibuildx')
    pao=ifc.create_entity('IfcPersonAndOrganization',ThePerson=person,TheOrganization=org)
    app=ifc.create_entity('IfcApplication',ApplicationDeveloper=org,Version='0.1')
    ow_hist=ifc.create_entity('IfcOwnerHistory',OwningUser=pao,OwningApplication=app)
    project=ifc.create_entity('IfcProject',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='AI Project',OwnerHistory=ow_hist)
    context=ifc.create_entity('IfcGeometricRepresentationContext',ContextIdentifier='Model',ContextType='Model',CoordinateSpaceDimension=3,Precision=1e-5)
    project.RepresentationContexts=[context]
    site=ifc.create_entity('IfcSite',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Site')
    building=ifc.create_entity('IfcBuilding',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Building')
    storey=ifc.create_entity('IfcBuildingStorey',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Storey')
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=project,RelatedObjects=[site])
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=site,RelatedObjects=[building])
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=building,RelatedObjects=[storey])

    SECTION_GEOM={
        'W8x10':{'type':'I','width':0.203,'depth':0.203,'web_thk':0.005,'flange_thk':0.006},
        'W10x12':{'type':'I','width':0.254,'depth':0.254,'web_thk':0.006,'flange_thk':0.007},
        'HSS100x100x6':{'type':'HollowRect','outer_w':0.100,'outer_h':0.100,'thickness':0.006},
        'REC200x50':{'type':'Rect','width':0.200,'depth':0.050,'thickness':0.005},
    }

    products=[]
    for m in full_json['members']:
        gid=ifcopenshell.guid.compress(uuid.uuid4().hex); name=m.get('selection',{}).get('section_name') or m.get('type')
        proxy=ifc.create_entity('IfcBuildingElementProxy',GlobalId=gid,Name=str(name))
        start = m['start']
        start_coords = (float(start[0]), float(start[1]), float(start[2]))
        placement_point = ifc.create_entity('IfcCartesianPoint', start_coords)
        # compute axis and a stable ref direction for profile orientation
        axis_vec = unit_vector(m['start'], m['end'])
        # choose a reference direction not parallel to axis_vec
        if abs(axis_vec[2]) < 0.9:
            ref_candidate = (0.0, 0.0, 1.0)
        else:
            ref_candidate = (0.0, 1.0, 0.0)
        # ensure ref is not parallel: simple Gram-Schmidt
        import math as _math
        ax = _math.sqrt(axis_vec[0]*axis_vec[0] + axis_vec[1]*axis_vec[1] + axis_vec[2]*axis_vec[2]) or 1.0
        a_norm = (axis_vec[0]/ax, axis_vec[1]/ax, axis_vec[2]/ax)
        # projection of ref_candidate onto axis
        proj = (a_norm[0]*ref_candidate[0] + a_norm[1]*ref_candidate[1] + a_norm[2]*ref_candidate[2])
        ref = (ref_candidate[0] - proj*a_norm[0], ref_candidate[1] - proj*a_norm[1], ref_candidate[2] - proj*a_norm[2])
        # normalize ref
        ref_len = (_math.sqrt(ref[0]*ref[0] + ref[1]*ref[1] + ref[2]*ref[2]) or 1.0)
        ref_dir = (ref[0]/ref_len, ref[1]/ref_len, ref[2]/ref_len)
        axis_dir = (float(a_norm[0]), float(a_norm[1]), float(a_norm[2]))
        ref_dir = (float(ref_dir[0]), float(ref_dir[1]), float(ref_dir[2]))
        axis_point = ifc.create_entity('IfcCartesianPoint', start_coords)
        axis_entity = ifc.create_entity('IfcDirection', axis_dir)
        ref_entity = ifc.create_entity('IfcDirection', ref_dir)
        axis2placement = ifc.create_entity('IfcAxis2Placement3D', axis_point, axis_entity, ref_entity)
        local_placement = ifc.create_entity('IfcLocalPlacement', PlacementRelTo=None, RelativePlacement=axis2placement)
        proxy.ObjectPlacement = local_placement
        geom=SECTION_GEOM.get(name); rep_items=[]
        if geom is not None:
            if geom['type']=='I':
                prof=ifc.create_entity('IfcIShapeProfileDef',ProfileType='AREA',ProfileName=name,OverallWidth=geom['width'],OverallDepth=geom['depth'],WebThickness=geom['web_thk'],FlangeThickness=geom['flange_thk'])
            elif geom['type']=='Rect':
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom['width'],YDim=geom['depth'])
            elif geom['type']=='HollowRect':
                # ifcopenshell/IFC doesn't have a simple hollow rectangle profile type; approximate using outer rectangle
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom['outer_w'],YDim=geom['outer_h'])
                # we add a property to indicate wall thickness so downstream tools can interpret as hollow
                if 'thickness' in geom:
                    # will be added to PSET below
                    pass
            else:
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom.get('width',0.1),YDim=geom.get('depth',0.05))
            axis=unit_vector(m['start'],m['end']); depth=m.get('length',0.0)
            origin_pt=ifc.create_entity('IfcCartesianPoint',(0.0,0.0,0.0))
            prof_pos=ifc.create_entity('IfcAxis2Placement3D', origin_pt, ifc.create_entity('IfcDirection',(0.0,0.0,1.0)), ifc.create_entity('IfcDirection',(1.0,0.0,0.0)))
            try:
                dir_vals=(float(axis[0]), float(axis[1]), float(axis[2]))
                extruded=ifc.create_entity('IfcExtrudedAreaSolid', SweptArea=prof, Position=prof_pos, ExtrudedDirection=ifc.create_entity('IfcDirection', dir_vals), Depth=depth)
                rep_items.append(extruded)
            except Exception:
                rep_items=[]
        props=[]
        def make_prop(namep,val):
            if isinstance(val,(int,float)):
                nominal=ifc.create_entity('IfcReal',float(val))
            else:
                nominal=ifc.create_entity('IfcText',str(val))
            return ifc.create_entity('IfcPropertySingleValue',Name=str(namep),NominalValue=nominal)
        props.append(make_prop('start',m['start'])); props.append(make_prop('end',m['end'])); props.append(make_prop('length_m',m.get('length')))
        props.append(make_prop('member_type',m.get('type'))); sel=m.get('selection',{}); props.append(make_prop('section',sel.get('section_name')))
        props.append(make_prop('weight_kg',sel.get('weight_kg')))
        pset=ifc.create_entity('IfcPropertySet',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Pset_AIBuildX',HasProperties=props)
        ifc.create_entity('IfcRelDefinesByProperties',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatedObjects=[proxy],RelatingPropertyDefinition=pset)
        if rep_items:
            shape=ifc.create_entity('IfcShapeRepresentation',ContextOfItems=context,RepresentationIdentifier='Body',RepresentationType='SweptSolid',Items=rep_items)
            pd=ifc.create_entity('IfcProductDefinitionShape',Representations=[shape]); proxy.Representation=pd
        products.append(proxy)
    ifc.create_entity('IfcRelContainedInSpatialStructure',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingStructure=storey,RelatedElements=products)
    try:
        out_dir=os.path.dirname(out_path);
        if out_dir and not os.path.exists(out_dir): os.makedirs(out_dir,exist_ok=True)
        ifc.write(out_path)
        return {'ifc':out_path,'note':'IFC written with basic swept solids and PSETs.'}
    except Exception as e:
        return {'ifc':None,'note':f'Failed to write IFC: {e}'}


def _segment_segment_distance(a0,a1,b0,b1):
    import numpy as _np
    u=_np.array([a1[i]-a0[i] for i in range(3)]); v=_np.array([b1[i]-b0[i] for i in range(3)])
    w0=_np.array([a0[i]-b0[i] for i in range(3)]); a=_np.dot(u,u); b=_np.dot(u,v); c=_np.dot(v,v)
    d=_np.dot(u,w0); e=_np.dot(v,w0); denom=a*c-b*b
    s=0.0; t=0.0
    if denom!=0.0: s=(b*e-c*d)/denom; t=(a*e-b*d)/denom
    s=max(0.0,min(1.0,s)); t=max(0.0,min(1.0,t))
    cp=_np.array(a0)+s*u; cq=_np.array(b0)+t*v
    return float(_np.linalg.norm(cp-cq))


def clasher_agent(full_json,tol=0.02):
    clashes=[]; mems=full_json['members']; n=len(mems)
    for i in range(n):
        for j in range(i+1,n):
            a=mems[i]; b=mems[j]
            if a['start']==b['start'] or a['end']==b['end'] or a['start']==b['end'] or a['end']==b['start']: continue
            d=_segment_segment_distance(a['start'],a['end'],b['start'],b['end'])
            if d<tol: clashes.append({'a':a['id'],'b':b['id'],'dist_m':d})
    return {'clashes':clashes}


def mesh_clasher_agent(full_json, tol=0.0):
    """Coarse mesh/solid clash approximation:
    - Stage 1: AABB overlap check using member length and section outer dims
    - Stage 2: precise centerline segment-segment distance compared to bounding radii
    Returns: {'clashes': [...]}
    """
    clashes = []
    mems = full_json['members']
    # helper to get outer half-diagonal (approx bounding radius) from selection/section
    def bounding_radius(m):
        sel = m.get('selection', {})
        name = sel.get('section_name')
        # fallback dims
        w = 0.05; h = 0.05
        if name and name in SECTION_GEOM:
            g = SECTION_GEOM[name]
            if g.get('type') in ('I','Rect','HollowRect'):
                if g.get('type') == 'I':
                    w = g.get('width', w); h = g.get('depth', h)
                elif g.get('type') == 'Rect':
                    w = g.get('width', w); h = g.get('depth', h)
                elif g.get('type') == 'HollowRect':
                    w = g.get('outer_w', w); h = g.get('outer_h', h)
        # radius ~ half diagonal
        return 0.5 * math.hypot(w, h)

    def aabb_for_member(m):
        x_coords = [m['start'][0], m['end'][0]]
        y_coords = [m['start'][1], m['end'][1]]
        z_coords = [m['start'][2], m['end'][2]]
        r = bounding_radius(m)
        return (min(x_coords)-r, min(y_coords)-r, min(z_coords)-r), (max(x_coords)+r, max(y_coords)+r, max(z_coords)+r), r

    n = len(mems)
    for i in range(n):
        for j in range(i+1, n):
            a = mems[i]; b = mems[j]
            if a['id'] == b['id']: continue
            # quick skip for shared nodes
            if a['start'] == b['start'] or a['end'] == b['end'] or a['start'] == b['end'] or a['end'] == b['start']:
                continue
            a_min, a_max, ra = aabb_for_member(a)
            b_min, b_max, rb = aabb_for_member(b)
            # check AABB overlap
            overlap = not (a_max[0] < b_min[0] or a_min[0] > b_max[0] or a_max[1] < b_min[1] or a_min[1] > b_max[1] or a_max[2] < b_min[2] or a_min[2] > b_max[2])
            if not overlap:
                continue
            # refined check: segment-segment distance
            d = _segment_segment_distance(a['start'], a['end'], b['start'], b['end'])
            # compare against sum of bounding radii (plus tolerance)
            if d <= (ra + rb + tol):
                clashes.append({'a': a['id'], 'b': b['id'], 'dist_m': d, 'radius_sum': (ra + rb)})
    return {'clashes': clashes}


def risk_detector(full_json):
    out={'members':[]}
    for m in full_json['members']:
        score=0
        if m.get('stability',{}).get('buckling_risk')=='high': score+=50
        if m.get('safety',{}).get('status')=='review': score+=20
        if any(c['dist_m']<0.02 for c in (full_json.get('clash_list') or [])): score+=30
        level='low' if score<20 else 'medium' if score<60 else 'high'
        out['members'].append({'id':m['id'],'risk_score':score,'risk_level':level})
    return out


def reporter_agent(full_json,out_dir=None):
    bom=[]
    for m in full_json['members']:
        sel=m.get('selection',{}); bom.append({'id':m['id'],'section':sel.get('section_name'),'weight_kg':sel.get('weight_kg',0)})
    return {'bom':bom,'members':full_json['members']}


def cnc_exporter(full_json, out_path=None):
    """Export simple CNC/DSTV-style CSV from fabrication details.

    Columns: member_id, section, length_m, weight_kg, bolt_count, hole_type, hole_size_mm
    """
    import csv
    if out_path is None:
        out_path = os.path.join('outputs', 'cnc.csv')
    rows = []
    for m in full_json['members']:
        sel = m.get('selection', {})
        fab = m.get('fabrication', {})
        conn = m.get('connection', {})
        hole = fab.get('holes', {}) if isinstance(fab.get('holes', {}), dict) else {}
        hole_type = hole.get('type') if hole else ''
        hole_size = ''
        if hole and isinstance(hole.get('size_mm'), (list, tuple)):
            hole_size = 'x'.join(str(int(x)) for x in hole.get('size_mm'))
        elif hole and hole.get('size_mm'):
            hole_size = str(hole.get('size_mm'))
        rows.append({
            'member_id': m['id'],
            'section': sel.get('section_name','UNKNOWN'),
            'length_m': float(m.get('length',0.0)),
            'weight_kg': float(sel.get('weight_kg',0.0)),
            'bolt_count': int(conn.get('bolt_count',0)) if conn else 0,
            'hole_type': hole_type or '',
            'hole_size_mm': hole_size,
        })
    # ensure directory
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, 'w', newline='') as csvfile:
        fieldnames = ['member_id','section','length_m','weight_kg','bolt_count','hole_type','hole_size_mm']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return {'cnc_csv': out_path, 'rows': rows}


def correction_loop(full_json,max_iters=5):
    model=full_json
    for it in range(max_iters):
        clashes=clasher_agent(model)['clashes']; val=validator_agent(model)
        if not clashes and not val['errors']: model['correction_iters']=it; return model
        for c in clashes:
            a=next((m for m in model['members'] if m['id']==c['a']),None); b=next((m for m in model['members'] if m['id']==c['b']),None)
            if a and b:
                v=a['orientation']; a['start']=[a['start'][0]+0.01*v[0],a['start'][1]+0.01*v[1],a['start'][2]+0.01*v[2]]; a['end']=[a['end'][0]+0.01*v[0],a['end'][1]+0.01*v[1],a['end'][2]+0.01*v[2]]
        model=engineer_standardize({'members':[{'start':m['start'],'end':m['end'],'length':length(m['start'],m['end']),'layer':m.get('layer')} for m in model['members']]})
        model=load_path_resolver(model); model=stability_agent(model); model=optimizer_agent(model); model=connection_designer(model)
        model=fabrication_detailing(model); model=fabrication_standards(model); model=erection_planner(model); model=safety_compliance(model)
        model['clash_list']=clasher_agent(model)['clashes']
    model['correction_iters']=max_iters; return model


class Pipeline:
    def __init__(self): pass
    def run_from_dxf_entities(self,dxf_entities,out_dir=None):
        a=miner_from_dxf(dxf_entities); b=engineer_standardize(a); c=load_path_resolver(b); d=stability_agent(c)
        e=optimizer_agent(d); f=connection_designer(e); g=fabrication_detailing(f); h=fabrication_standards(g)
        i=erection_planner(h); j=safety_compliance(i); k=analysis_model_generator(j)
        l=builder_ifc(h,out_path=os.path.join(out_dir or 'outputs','model.ifc'))
        v = validator_agent(h)
        clash = clasher_agent(h)
        mesh_clash = mesh_clasher_agent(h)
        # prefer mesh-based clashes for final reporting
        h['clash_list'] = mesh_clash['clashes'] if mesh_clash['clashes'] else clash['clashes']
        r = risk_detector({**h, 'clash_list': h['clash_list']})
        rep = reporter_agent(h, out_dir=out_dir)
        final = correction_loop(h)
        cnc = cnc_exporter(h, out_path=os.path.join(out_dir or 'outputs','cnc.csv'))
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
            'mesh_clashes': mesh_clash,
            'risk': r,
            'reporter': rep,
            'final': final,
            'cnc': cnc,
        }


if __name__=='__main__':
    sample=[{'start':[0,0,0],'end':[6,0,0],'layer':'BEAMS'},{'start':[6,0,0],'end':[6,0,4],'layer':'COLUMNS'},{'start':[0,0,0],'end':[0,6,0],'layer':'BEAMS'}]
    p=Pipeline(); out=p.run_from_dxf_entities(sample,out_dir='outputs'); print(json.dumps({'summary':{'members':len(out['miner']['members']),'ifc':out['ifc']}},indent=2))
