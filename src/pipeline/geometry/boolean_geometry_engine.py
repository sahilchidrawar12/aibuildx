#!/usr/bin/env python3
"""
3D Boolean Geometry Engine
Handles geometric intersections, subtractions, and unions for coping/notching
"""

import math
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from ..utils.logging_setup import get_logger

logger = get_logger("boolean_geometry")

@dataclass
class BoundingBox:
    """3D bounding box for collision detection"""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float

@dataclass
class Triangle:
    """3D triangle for mesh operations"""
    v1: Tuple[float, float, float]
    v2: Tuple[float, float, float]
    v3: Tuple[float, float, float]

@dataclass
class Mesh:
    """3D mesh representation"""
    vertices: List[Tuple[float, float, float]]
    triangles: List[Triangle]
    bounding_box: BoundingBox

class BooleanGeometryEngine:
    """
    3D Boolean Operations Engine
    Performs geometric intersections and subtractions for coping
    """

    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance  # mm tolerance for operations

    def subtract_geometry(self, solid1: Dict[str, Any], solid2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform 3D Boolean subtraction: solid1 - solid2
        Used for coping beams to fit columns
        """
        logger.debug(f"Performing Boolean subtraction with tolerance {self.tolerance}mm")

        # Convert to mesh representations
        mesh1 = self._dict_to_mesh(solid1)
        mesh2 = self._dict_to_mesh(solid2)

        # Check for intersection
        if not self._bounding_boxes_intersect(mesh1.bounding_box, mesh2.bounding_box):
            logger.debug("No intersection detected, returning solid1 unchanged")
            return solid1

        # Perform mesh boolean subtraction
        result_mesh = self._mesh_subtract(mesh1, mesh2)

        # Convert back to dict representation
        result = self._mesh_to_dict(result_mesh)
        result['operation'] = 'boolean_subtract'
        result['tolerance_mm'] = self.tolerance

        return result

    def intersect_geometry(self, solid1: Dict[str, Any], solid2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform 3D Boolean intersection
        Used for finding overlap regions
        """
        mesh1 = self._dict_to_mesh(solid1)
        mesh2 = self._dict_to_mesh(solid2)

        result_mesh = self._mesh_intersect(mesh1, mesh2)
        result = self._mesh_to_dict(result_mesh)
        result['operation'] = 'boolean_intersect'

        return result

    def union_geometry(self, solid1: Dict[str, Any], solid2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform 3D Boolean union
        Used for combining geometric elements
        """
        mesh1 = self._dict_to_mesh(solid1)
        mesh2 = self._dict_to_mesh(solid2)

        result_mesh = self._mesh_union(mesh1, mesh2)
        result = self._mesh_to_dict(result_mesh)
        result['operation'] = 'boolean_union'

        return result

    def _dict_to_mesh(self, solid: Dict[str, Any]) -> Mesh:
        """Convert dictionary representation to mesh"""
        # Handle different solid types
        solid_type = solid.get('type', 'box')

        if solid_type == 'box':
            return self._create_box_mesh(solid)
        elif solid_type == 'cylinder':
            return self._create_cylinder_mesh(solid)
        elif solid_type == 'profile':
            return self._create_profile_mesh(solid)
        else:
            # Generic mesh
            vertices = solid.get('vertices', [])
            triangles = solid.get('triangles', [])
            bbox = self._calculate_bounding_box(vertices)

            mesh_triangles = [Triangle(*t) for t in triangles]
            return Mesh(vertices, mesh_triangles, bbox)

    def _create_box_mesh(self, solid: Dict[str, Any]) -> Mesh:
        """Create mesh for box geometry"""
        width = solid.get('width_mm', 100)
        height = solid.get('height_mm', 100)
        depth = solid.get('depth_mm', 10)
        position = solid.get('position', [0, 0, 0])

        x, y, z = position
        w, h, d = width/2, height/2, depth/2

        vertices = [
            (x-w, y-h, z-d), (x+w, y-h, z-d), (x+w, y+h, z-d), (x-w, y+h, z-d),  # Bottom
            (x-w, y-h, z+d), (x+w, y-h, z+d), (x+w, y+h, z+d), (x-w, y+h, z+d)   # Top
        ]

        triangles = [
            Triangle((0, 1, 2)), Triangle((0, 2, 3)),  # Bottom
            Triangle((4, 5, 6)), Triangle((4, 6, 7)),  # Top
            Triangle((0, 1, 5)), Triangle((0, 5, 4)),  # Front
            Triangle((1, 2, 6)), Triangle((1, 6, 5)),  # Right
            Triangle((2, 3, 7)), Triangle((2, 7, 6)),  # Back
            Triangle((3, 0, 4)), Triangle((3, 4, 7))   # Left
        ]

        bbox = BoundingBox(x-w, x+w, y-h, y+h, z-d, z+d)
        return Mesh(vertices, triangles, bbox)

    def _create_cylinder_mesh(self, solid: Dict[str, Any]) -> Mesh:
        """Create mesh for cylindrical geometry"""
        radius = solid.get('radius_mm', 50)
        height = solid.get('height_mm', 100)
        position = solid.get('position', [0, 0, 0])
        segments = solid.get('segments', 16)

        x, y, z = position
        vertices = []
        triangles = []

        # Create vertices
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vx = x + radius * math.cos(angle)
            vy = y + radius * math.sin(angle)
            vertices.extend([(vx, vy, z), (vx, vy, z + height)])

        # Create triangles for sides
        for i in range(segments):
            i1 = i * 2
            i2 = ((i + 1) % segments) * 2
            i3 = i1 + 1
            i4 = i2 + 1

            triangles.extend([
                Triangle((i1, i2, i3)),
                Triangle((i2, i4, i3))
            ])

        # Add end caps (simplified)
        center_bottom = len(vertices)
        center_top = len(vertices) + 1
        vertices.extend([(x, y, z), (x, y, z + height)])

        # Bottom cap
        for i in range(segments):
            i1 = i * 2
            i2 = ((i + 1) % segments) * 2
            triangles.append(Triangle((center_bottom, i1, i2)))

        # Top cap
        for i in range(segments):
            i1 = i * 2 + 1
            i2 = ((i + 1) % segments) * 2 + 1
            triangles.append(Triangle((center_top, i2, i1)))

        bbox = BoundingBox(x-radius, x+radius, y-radius, y+radius, z, z+height)
        return Mesh(vertices, triangles, bbox)

    def _create_profile_mesh(self, solid: Dict[str, Any]) -> Mesh:
        """Create mesh for structural profile"""
        profile_name = solid.get('profile_name', 'W12x50')
        length = solid.get('length_mm', 1000)
        position = solid.get('position', [0, 0, 0])
        rotation = solid.get('rotation_deg', 0)

        # Simplified I-beam representation
        # In full implementation, would use actual profile geometry from database
        bf = solid.get('bf_mm', 150)  # Flange width
        tf = solid.get('tf_mm', 10)  # Flange thickness
        d = solid.get('d_mm', 300)   # Depth
        tw = solid.get('tw_mm', 8)   # Web thickness

        x, y, z = position
        l = length / 2

        # Create vertices for I-beam extrusion
        vertices = [
            # Bottom flange
            (x - bf/2, y - d/2, z - l), (x + bf/2, y - d/2, z - l),
            (x + bf/2, y - d/2 + tf, z - l), (x - bf/2, y - d/2 + tf, z - l),
            (x - bf/2, y - d/2, z + l), (x + bf/2, y - d/2, z + l),
            (x + bf/2, y - d/2 + tf, z + l), (x - bf/2, y - d/2 + tf, z + l),

            # Top flange
            (x - bf/2, y + d/2 - tf, z - l), (x + bf/2, y + d/2 - tf, z - l),
            (x + bf/2, y + d/2, z - l), (x - bf/2, y + d/2, z - l),
            (x - bf/2, y + d/2 - tf, z + l), (x + bf/2, y + d/2 - tf, z + l),
            (x + bf/2, y + d/2, z + l), (x - bf/2, y + d/2, z + l),

            # Web
            (x - tw/2, y - d/2 + tf, z - l), (x + tw/2, y - d/2 + tf, z - l),
            (x + tw/2, y + d/2 - tf, z - l), (x - tw/2, y + d/2 - tf, z - l),
            (x - tw/2, y - d/2 + tf, z + l), (x + tw/2, y - d/2 + tf, z + l),
            (x + tw/2, y + d/2 - tf, z + l), (x - tw/2, y + d/2 - tf, z + l)
        ]

        # Simplified triangulation (would be more complex in reality)
        triangles = []
        # Add triangles for flanges and web (simplified)

        bbox = BoundingBox(x - bf/2, x + bf/2, y - d/2, y + d/2, z - l, z + l)
        return Mesh(vertices, triangles, bbox)

    def _mesh_subtract(self, mesh1: Mesh, mesh2: Mesh) -> Mesh:
        """Perform mesh boolean subtraction"""
        # Simplified implementation
        # In full implementation, would use proper mesh boolean operations

        # For now, return mesh1 with modified geometry near intersection
        # This is a placeholder - real implementation would use libraries like CGAL

        logger.warning("Using simplified mesh subtraction - full implementation needed")

        # Find intersection region and remove geometry
        intersection_bbox = self._intersection_bbox(mesh1.bounding_box, mesh2.bounding_box)

        # Simplified: remove triangles that intersect the subtraction volume
        filtered_triangles = []
        for triangle in mesh1.triangles:
            if not self._triangle_intersects_bbox(triangle, intersection_bbox):
                filtered_triangles.append(triangle)

        return Mesh(mesh1.vertices, filtered_triangles, mesh1.bounding_box)

    def _mesh_intersect(self, mesh1: Mesh, mesh2: Mesh) -> Mesh:
        """Perform mesh boolean intersection"""
        # Placeholder implementation
        return Mesh([], [], BoundingBox(0, 0, 0, 0, 0, 0))

    def _mesh_union(self, mesh1: Mesh, mesh2: Mesh) -> Mesh:
        """Perform mesh boolean union"""
        # Placeholder implementation
        combined_vertices = mesh1.vertices + mesh2.vertices
        combined_triangles = mesh1.triangles + mesh2.triangles
        combined_bbox = self._union_bbox(mesh1.bounding_box, mesh2.bounding_box)
        return Mesh(combined_vertices, combined_triangles, combined_bbox)

    def _bounding_boxes_intersect(self, bbox1: BoundingBox, bbox2: BoundingBox) -> bool:
        """Check if two bounding boxes intersect"""
        return (bbox1.max_x >= bbox2.min_x and bbox1.min_x <= bbox2.max_x and
                bbox1.max_y >= bbox2.min_y and bbox1.min_y <= bbox2.max_y and
                bbox1.max_z >= bbox2.min_z and bbox1.min_z <= bbox2.max_z)

    def _intersection_bbox(self, bbox1: BoundingBox, bbox2: BoundingBox) -> BoundingBox:
        """Calculate intersection bounding box"""
        return BoundingBox(
            max(bbox1.min_x, bbox2.min_x),
            min(bbox1.max_x, bbox2.max_x),
            max(bbox1.min_y, bbox2.min_y),
            min(bbox1.max_y, bbox2.max_y),
            max(bbox1.min_z, bbox2.min_z),
            min(bbox1.max_z, bbox2.max_z)
        )

    def _union_bbox(self, bbox1: BoundingBox, bbox2: BoundingBox) -> BoundingBox:
        """Calculate union bounding box"""
        return BoundingBox(
            min(bbox1.min_x, bbox2.min_x),
            max(bbox1.max_x, bbox2.max_x),
            min(bbox1.min_y, bbox2.min_y),
            max(bbox1.max_y, bbox2.max_y),
            min(bbox1.min_z, bbox2.min_z),
            max(bbox1.max_z, bbox2.max_z)
        )

    def _triangle_intersects_bbox(self, triangle: Triangle, bbox: BoundingBox) -> bool:
        """Check if triangle intersects bounding box"""
        # Simplified check - check if any vertex is inside bbox
        for vertex in [triangle.v1, triangle.v2, triangle.v3]:
            if (bbox.min_x <= vertex[0] <= bbox.max_x and
                bbox.min_y <= vertex[1] <= bbox.max_y and
                bbox.min_z <= vertex[2] <= bbox.max_z):
                return True
        return False

    def _calculate_bounding_box(self, vertices: List[Tuple[float, float, float]]) -> BoundingBox:
        """Calculate bounding box from vertices"""
        if not vertices:
            return BoundingBox(0, 0, 0, 0, 0, 0)

        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]

        return BoundingBox(min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    def _mesh_to_dict(self, mesh: Mesh) -> Dict[str, Any]:
        """Convert mesh back to dictionary representation"""
        return {
            'type': 'mesh',
            'vertices': mesh.vertices,
            'triangles': [(t.v1, t.v2, t.v3) for t in mesh.triangles],
            'bounding_box': {
                'min_x': mesh.bounding_box.min_x,
                'max_x': mesh.bounding_box.max_x,
                'min_y': mesh.bounding_box.min_y,
                'max_y': mesh.bounding_box.max_y,
                'min_z': mesh.bounding_box.min_z,
                'max_z': mesh.bounding_box.max_z
            },
            'vertex_count': len(mesh.vertices),
            'triangle_count': len(mesh.triangles)
        }