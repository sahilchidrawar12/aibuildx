#!/usr/bin/env python3
"""Test script: Complete pipeline with connection parsing."""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/sahil/Documents/aibuildx')

from src.pipeline.agents.main_pipeline_agent import MainPipelineAgent


def test_pipeline_with_dxf(dxf_path: str):
    """Test the complete pipeline with a DXF file."""
    
    print(f"\n{'='*70}")
    print(f"Testing AIBuildX Pipeline with: {dxf_path}")
    print(f"{'='*70}\n")
    
    agent = MainPipelineAgent()
    
    payload = {
        'data': {
            'dxf_entities': dxf_path
        }
    }
    
    result = agent.run(payload)
    
    print(f"Pipeline Status: {result.get('status')}\n")
    
    out = result.get('result', {})
    
    # Print summary
    print("PIPELINE OUTPUT SUMMARY:")
    print("-" * 70)
    
    if out.get('error'):
        print(f"❌ Error: {out['error']}\n")
        return
    
    print(f"✓ Miner: Extracted entities")
    print(f"  - Members: {len(out.get('members_classified', []))}")
    
    print(f"\n✓ Geometry Agent: Processed members")
    print(f"  - Nodes: {len(out.get('nodes', []))}")
    
    print(f"\n✓ Node Resolution & Auto-generated Joints")
    print(f"  - Auto-generated joints: {len([j for j in out.get('joints', []) if j.get('connection_type') == 'auto'])}")
    
    circles_parsed = out.get('circles_parsed', 0)
    print(f"\n✓ Connection Parser Agent")
    print(f"  - Circles parsed: {circles_parsed}")
    
    # Count parsed vs auto joints
    all_joints = out.get('joints', [])
    parsed_joints = [j for j in all_joints if 'members' in j and len(j.get('members', [])) > 0]
    auto_joints = [j for j in all_joints if 'members' not in j or len(j.get('members', [])) == 0]
    
    print(f"  - Joints with member links: {len(parsed_joints)}")
    if parsed_joints:
        print(f"    Connection types: {set(j.get('connection_type', 'unknown') for j in parsed_joints)}")
    
    print(f"\n✓ Connection Synthesis Agent")
    plates = out.get('plates', [])
    bolts = out.get('bolts', [])
    print(f"  - Generated plates: {len(plates)}")
    print(f"  - Generated bolts: {len(bolts)}")
    
    if plates:
        print(f"    Sample plate: {plates[0].get('id')} at {plates[0].get('position')}")
    
    if bolts:
        print(f"    Sample bolt: {bolts[0].get('id')} (diameter: {bolts[0].get('diameter')}mm)")
    
    print(f"\n✓ IFC Export")
    ifc = out.get('ifc', {})
    print(f"  - Status: {ifc.get('status', 'unknown')}")
    print(f"  - Summary: {ifc.get('summary', {})}")
    
    print(f"\n{'='*70}")
    print("DETAILED JOINT INFORMATION:")
    print(f"{'='*70}\n")
    
    for i, joint in enumerate(parsed_joints[:3], 1):  # Show first 3
        print(f"Joint {i}: {joint.get('id')}")
        print(f"  Position: {joint.get('position')}")
        print(f"  Members: {joint.get('members')}")
        print(f"  Connection Type: {joint.get('connection_type')}")
        print(f"  Detected Members:")
        for m in joint.get('detected_members', [])[:2]:
            print(f"    - {m.get('id')} (distance: {m.get('distance_from_center'):.1f}mm)")
        print()
    
    if circles_parsed > 0 and len(plates) > 0 and len(bolts) > 0:
        print("✅ SUCCESS: Pipeline correctly converted circles → joints → plates/bolts!")
    else:
        print("⚠️  INFO: Check output above for details")


if __name__ == '__main__':
    # Test with DXF that has circles
    test_dxf = '/Users/sahil/Documents/aibuildx/uploads/93e45ff5_test.dxf'
    
    if Path(test_dxf).exists():
        test_pipeline_with_dxf(test_dxf)
    else:
        print(f"DXF file not found: {test_dxf}")
        sys.exit(1)
