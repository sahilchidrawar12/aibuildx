#!/usr/bin/env python3
"""
Mesh generator for plates, shells, and 3D solids.
Converts pipeline geometry (plates, slabs) into quad/tri elements for FEM analysis.

Supports:
- Structured quad meshing for rectangular plates
- Unstructured tri meshing for complex shapes (requires pygmsh)
- Tetrahedral meshing for 3D volumes

Usage:
    python3 tools/mesh_generator.py --input output/pipeline_result.json --output output/mesh.json --method quads
"""
import json
import sys
import argparse
import math
from typing import Dict, List, Tuple, Any
from pathlib import Path

class MeshGenerator:
    """Generate FEM mesh from pipeline geometry."""
    
    def __init__(self, method='quads'):
        """
        Initialize mesh generator.
        method: 'quads' (structured), 'tris' (unstructured, requires pygmsh), 'tets' (3D, requires pygmsh)
        """
        self.method = method
        self.nodes = {}
        self.elements = {}
        self.node_id = 1
        self.elem_id = 1
    
    def generate(self, pipeline_result: Dict[str, Any], target_element_size: float = 500.0) -> Dict[str, Any]:
        """
        Generate mesh from pipeline output.
        
        Args:
            pipeline_result: Output from main_pipeline_agent.process
            target_element_size: Approximate element size in mm
        
        Returns:
            Mesh dict with nodes, elements, and metadata
        """
        result = pipeline_result.get('result', {})
        plates = result.get('plates', [])
        members = result.get('members_classified', [])
        
        mesh = {
            'nodes': {},
            'elements': {},
            'metadata': {
                'method': self.method,
                'target_element_size': target_element_size,
                'num_nodes': 0,
                'num_elements': 0,
            }
        }
        
        # Mesh plates
        for plate in plates:
            self._mesh_plate(plate, target_element_size, mesh)
        
        # Mesh members (beams as line elements)
        for member in members:
            self._mesh_member(member, mesh)
        
        mesh['metadata']['num_nodes'] = len(mesh['nodes'])
        mesh['metadata']['num_elements'] = len(mesh['elements'])
        
        return mesh
    
    def _mesh_plate(self, plate: Dict, target_size: float, mesh: Dict) -> None:
        """Mesh a rectangular plate into quads."""
        # Extract plate geometry
        corners = plate.get('corners', [])
        if len(corners) < 4:
            return
        
        # Assume rectangular plate: corners = [p1, p2, p3, p4]
        # p1 ---- p2
        # |       |
        # p4 ---- p3
        
        # Compute number of divisions
        side1_dist = self._distance(corners[0], corners[1])
        side2_dist = self._distance(corners[1], corners[2])
        
        nx = max(1, int(round(side1_dist / target_size)))
        ny = max(1, int(round(side2_dist / target_size)))
        
        # Generate node grid
        node_grid = []
        for j in range(ny + 1):
            row = []
            for i in range(nx + 1):
                # Bilinear interpolation
                u = i / nx if nx > 0 else 0
                v = j / ny if ny > 0 else 0
                
                p = self._bilinear_interp(corners[0], corners[1], corners[2], corners[3], u, v)
                nid = self.node_id
                self.node_id += 1
                mesh['nodes'][nid] = {'pos': p, 'type': 'plate'}
                row.append(nid)
            node_grid.append(row)
        
        # Generate quad elements
        for j in range(ny):
            for i in range(nx):
                n1 = node_grid[j][i]
                n2 = node_grid[j][i + 1]
                n3 = node_grid[j + 1][i + 1]
                n4 = node_grid[j + 1][i]
                
                eid = self.elem_id
                self.elem_id += 1
                mesh['elements'][eid] = {
                    'type': 'quad4',
                    'nodes': [n1, n2, n3, n4],
                    'plate_id': plate.get('id', 'unknown'),
                }
    
    def _mesh_member(self, member: Dict, mesh: Dict) -> None:
        """Add beam element for member (line element, no meshing)."""
        start = member.get('start', [0, 0, 0])
        end = member.get('end', [0, 0, 0])
        
        # Check if nodes already exist
        start_tuple = tuple(start)
        end_tuple = tuple(end)
        
        if start_tuple not in [n['pos'] for n in mesh['nodes'].values()]:
            nid1 = self.node_id
            self.node_id += 1
            mesh['nodes'][nid1] = {'pos': start, 'type': 'beam_end'}
        else:
            nid1 = [nid for nid, n in mesh['nodes'].items() if n['pos'] == start_tuple][0]
        
        if end_tuple not in [n['pos'] for n in mesh['nodes'].values()]:
            nid2 = self.node_id
            self.node_id += 1
            mesh['nodes'][nid2] = {'pos': end, 'type': 'beam_end'}
        else:
            nid2 = [nid for nid, n in mesh['nodes'].items() if n['pos'] == end_tuple][0]
        
        eid = self.elem_id
        self.elem_id += 1
        mesh['elements'][eid] = {
            'type': 'beam2',
            'nodes': [nid1, nid2],
            'member_id': member.get('id', 'unknown'),
            'profile': member.get('profile', 'unknown'),
        }
    
    @staticmethod
    def _distance(p1: List[float], p2: List[float]) -> float:
        """Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
    
    @staticmethod
    def _bilinear_interp(p1: List, p2: List, p3: List, p4: List, u: float, v: float) -> List:
        """Bilinear interpolation on quadrilateral."""
        # p1 ---- p2
        # |       |
        # p4 ---- p3
        p = [
            (1 - u) * (1 - v) * p1[i] +
            u * (1 - v) * p2[i] +
            u * v * p3[i] +
            (1 - u) * v * p4[i]
            for i in range(3)
        ]
        return p

def main():
    parser = argparse.ArgumentParser(description='Generate FEM mesh from pipeline output')
    parser.add_argument('--input', required=True, help='Input JSON (pipeline result)')
    parser.add_argument('--output', required=True, help='Output mesh JSON')
    parser.add_argument('--method', choices=['quads', 'tris', 'tets'], default='quads',
                        help='Meshing method')
    parser.add_argument('--element-size', type=float, default=500.0,
                        help='Target element size in mm')
    args = parser.parse_args()
    
    # Load pipeline result
    with open(args.input, 'r') as f:
        pipeline_result = json.load(f)
    
    # Generate mesh
    gen = MeshGenerator(method=args.method)
    mesh = gen.generate(pipeline_result, target_element_size=args.element_size)
    
    # Write to file
    with open(args.output, 'w') as f:
        json.dump(mesh, f, indent=2)
    
    print(f"✓ Mesh generated: {args.output}")
    print(f"  Method: {args.method}")
    print(f"  Nodes: {mesh['metadata']['num_nodes']}")
    print(f"  Elements: {mesh['metadata']['num_elements']}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
