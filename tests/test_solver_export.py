import sys
sys.path.insert(0, '.')
from src.pipeline.agents import main_pipeline_agent
from tools.export_to_opensees import OpenSeesExporter
from tools.mesh_generator import MeshGenerator
import json
from pathlib import Path

# Create a simple test payload
payload = {
    'data': {
        'dxf_entities': [
            {'id': 'm1', 'start': [0, 0, 0], 'end': [6000, 0, 0], 'profile': 'IPE200'},
            {'id': 'm2', 'start': [6000, 0, 0], 'end': [6000, 0, 3000], 'profile': 'IPE160'},
        ]
    }
}

# Run pipeline
print("1. Running pipeline...")
result = main_pipeline_agent.process(payload)
print(f"   Status: {result['status']}")

if result['status'] == 'ok':
    pipeline_output = result['result']
    
    # Test OpenSees exporter
    print("\n2. Testing OpenSees exporter...")
    exporter = OpenSeesExporter()
    tcl_script = exporter.export(result)
    
    # Write TCL
    tcl_path = Path('outputs/test_model.tcl')
    tcl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tcl_path, 'w') as f:
        f.write(tcl_script)
    print(f"   ✓ Wrote {tcl_path}")
    print(f"   Nodes: {exporter.node_id - 1}, Elements: {exporter.elem_id - 1}")
    
    # Test mesh generator
    print("\n3. Testing mesh generator...")
    gen = MeshGenerator(method='quads')
    mesh = gen.generate(result, target_element_size=500.0)
    
    # Write mesh
    mesh_path = Path('outputs/test_mesh.json')
    with open(mesh_path, 'w') as f:
        json.dump(mesh, f, indent=2)
    print(f"   ✓ Wrote {mesh_path}")
    print(f"   Nodes: {mesh['metadata']['num_nodes']}, Elements: {mesh['metadata']['num_elements']}")
    
    print("\n✓ All tests passed!")
else:
    print(f"   Error: {result['result'].get('error', 'Unknown')}")
