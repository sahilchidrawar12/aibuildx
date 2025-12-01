from src.pipeline.node_resolution import snap_nodes, auto_generate_joints

def test_snap_nodes_and_joints():
    members = [
        {"id":"m1","start":(0,0,0),"end":(1000,0,0)},
        {"id":"m2","start":(1000,0,0),"end":(2000,0,0)},
        {"id":"m3","start":(1000,0,0),"end":(1000,1000,0)}
    ]
    nodes, updated_members = snap_nodes(members, tolerance=5.0)
    assert len(nodes) >= 4
    joints = auto_generate_joints(members, tolerance=5.0)
    # node at (1000,0,0) should be a joint
    assert any(j['x']==1000 for j in joints)
