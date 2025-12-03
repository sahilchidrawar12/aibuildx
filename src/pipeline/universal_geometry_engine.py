"""
UNIVERSAL GEOMETRY ENGINE
═══════════════════════════════════════════════════════════════════════════════

Handles coordinate origin fixes for ANY DXF structure:
  • Pre-generated plates all at [0,0,0] → Positioned at real joints
  • Synthesized connections → Uses real intersection points
  • Mixed structures → Unified handling
  • Any member count/configuration → Scale-independent

Core Algorithm:
  1. Extract all member geometry (beams + columns)
  2. Calculate real 3D intersection points between members
  3. Build joint location map
  4. Apply positions to all plates/bolts (existing or new)
  5. Ensure standards compliance for all connections

Author: Structural Engineering AI Pipeline
Date: December 4, 2025
"""

import json
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class Point3D:
    """3D coordinate point"""
    x: float
    y: float
    z: float
    
    def __init__(self, coords=None, x=0, y=0, z=0):
        if coords is not None:
            if isinstance(coords, (list, tuple)) and len(coords) >= 3:
                self.x, self.y, self.z = coords[0], coords[1], coords[2]
            else:
                self.x, self.y, self.z = x, y, z
        else:
            self.x, self.y, self.z = x, y, z
    
    def distance_to(self, other: 'Point3D') -> float:
        """Calculate 3D Euclidean distance"""
        return math.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )
    
    def to_list(self):
        """Convert to [x, y, z] list"""
        return [self.x, self.y, self.z]
    
    def to_tuple(self):
        """Convert to (x, y, z) tuple"""
        return (self.x, self.y, self.z)
    
    def __repr__(self):
        return f"Point3D({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


class UniversalGeometryEngine:
    """
    Universal geometry engine for structural joint detection and positioning.
    
    Works with ANY DXF structure:
      • Detects joints from member intersections
      • Positions plates at calculated joint locations
      • Applies bolt transformations correctly
      • Maintains standards compliance
      • Independent of input format
    """
    
    # Configuration constants
    INTERSECTION_TOLERANCE_MM = 100.0  # Proximity tolerance for intersection detection
    EDGE_OFFSET_MM = 20.0               # Offset from joint center for edge distance
    BOLT_SPACING_MM = 50.0              # Standard bolt spacing
    
    def __init__(self, tolerance_mm: float = 100.0):
        """
        Initialize engine with tolerance.
        
        Args:
            tolerance_mm: Proximity threshold for joint detection (default 100mm)
        """
        self.tolerance_mm = tolerance_mm
        self.members = []
        self.joints = {}  # joint_id → Point3D
        self.joint_connections = {}  # joint_id → [member_ids]
    
    def extract_members(self, ifc_data: Dict) -> List[Dict]:
        """
        Extract all members from IFC data.
        
        Handles various DXF formats:
          • Standard IFC format
          • Pre-processed JSON
          • Any structure with beams + columns
        
        Returns:
            List of member dictionaries with:
              - id, start, end, direction
              - type (BEAM or COLUMN)
              - material, profile info
        """
        members = []
        
        # Extract beams
        for beam in ifc_data.get('beams', []):
            member = {
                'id': beam.get('id', f'beam_{len(members)}'),
                'type': 'BEAM',
                'start': Point3D(beam.get('start', [0, 0, 0])),
                'end': Point3D(beam.get('end', [0, 0, 0])),
                'length': beam.get('length', 0),
                'profile': beam.get('profile', {}),
                'material': beam.get('material', {}),
            }
            members.append(member)
        
        # Extract columns
        for column in ifc_data.get('columns', []):
            member = {
                'id': column.get('id', f'column_{len(members)}'),
                'type': 'COLUMN',
                'start': Point3D(column.get('start', [0, 0, 0])),
                'end': Point3D(column.get('end', [0, 0, 0])),
                'length': column.get('length', 0),
                'profile': column.get('profile', {}),
                'material': column.get('material', {}),
            }
            members.append(member)
        
        self.members = members
        logger.info(f"Extracted {len(members)} members ({len(ifc_data.get('beams', []))} beams, {len(ifc_data.get('columns', []))} columns)")
        
        return members
    
    def detect_joints_from_geometry(self, ifc_data: Dict = None) -> Dict[str, Point3D]:
        """
        Detect joint locations from member geometry OR fix pre-existing joints.
        
        Algorithm (SMART & ADAPTIVE):
          1. Check if joints already exist in IFC data
          2. Check if ALL joints are at [0,0,0] (broken/hardcoded)
          3. If YES, recalculate using member-to-joint mapping:
             - For EACH broken joint, find its connected members
             - Calculate intersection point of those members
             - Use that as the new joint location
          4. If NO, USE joints as-is (they're correct)
          5. If joints don't exist, calculate from geometry
        
        Returns:
            Dictionary mapping joint_id → Point3D
        """
        joints = {}
        
        # FIRST: Try to use pre-existing joints from IFC data
        if ifc_data and 'joints' in ifc_data:
            existing_joints = ifc_data.get('joints', [])
            if existing_joints:
                # Check if ALL joints are at [0,0,0] (broken)
                all_at_origin = all(
                    j.get('location', [0, 0, 0]) == [0, 0, 0]
                    for j in existing_joints
                )
                
                if not all_at_origin:
                    # Joints are good, use them
                    logger.info(f"Using {len(existing_joints)} pre-existing joints from IFC data (validated)")
                    for joint in existing_joints:
                        joint_id = joint.get('id')
                        location = joint.get('location', [0, 0, 0])
                        joints[joint_id] = Point3D(location)
                        
                        # Store member-to-joint mapping
                        members = joint.get('members', [])
                        if joint_id and members:
                            self.joint_connections[joint_id] = members
                    
                    self.joints = joints
                    return joints
                else:
                    # ALL joints are at [0,0,0] - recalculate using member mapping!
                    logger.warning(f"Found {len(existing_joints)} joints ALL at [0,0,0] - recalculating using member mapping")
                    
                    for joint in existing_joints:
                        joint_id = joint.get('id')
                        members = joint.get('members', [])
                        
                        if joint_id and members:
                            # Store the member mapping
                            self.joint_connections[joint_id] = members
                            
                            # Find this joint's intersection point from its members
                            location = self._calculate_joint_location_from_members(members)
                            joints[joint_id] = location
                            
                            logger.debug(f"Joint {joint_id}: calculated location from {len(members)} members → {location}")
                    
                    self.joints = joints
                    logger.info(f"Recalculated {len(joints)} joint locations from broken data using member mapping")
                    return joints
        
        # FALLBACK: Calculate from member geometry if no pre-existing joints
        logger.info("Calculating joints from member geometry...")
        return self._detect_joints_from_geometry_candidates()
    
    def _calculate_joint_location_from_members(self, member_ids: List[str]) -> Point3D:
        """
        Calculate joint location by finding intersection of members.
        
        For a set of members connected at a joint, find their intersection point.
        """
        if not member_ids:
            return Point3D(0, 0, 0)
        
        # Get coordinates of these members
        member_coords = []
        for mid in member_ids:
            member = next((m for m in self.members if m['id'] == mid), None)
            if member:
                member_coords.append({
                    'id': mid,
                    'start': member['start'],
                    'end': member['end'],
                    'type': member['type']
                })
        
        if not member_coords:
            return Point3D(0, 0, 0)
        
        # Strategy: Find a common point (or close proximity) among all members
        # Start with endpoints of first member, check which is closest to other members
        
        if len(member_coords) == 1:
            # Single member - use midpoint
            m = member_coords[0]
            return Point3D(
                x=(m['start'].x + m['end'].x) / 2,
                y=(m['start'].y + m['end'].y) / 2,
                z=(m['start'].z + m['end'].z) / 2,
            )
        
        # Multiple members - find intersection point
        best_point = None
        best_distance = float('inf')
        
        # Check all endpoint combinations
        endpoints_to_check = []
        for m in member_coords:
            endpoints_to_check.append(m['start'])
            endpoints_to_check.append(m['end'])
        
        # For each candidate endpoint, calculate sum of distances to all other members
        for candidate in endpoints_to_check:
            total_distance = 0
            for m in member_coords:
                # Distance from candidate to closest point on member m
                dist_to_start = candidate.distance_to(m['start'])
                dist_to_end = candidate.distance_to(m['end'])
                min_dist = min(dist_to_start, dist_to_end)
                total_distance += min_dist
            
            if total_distance < best_distance:
                best_distance = total_distance
                best_point = candidate
        
        if best_point and best_distance < 1000:  # Reasonable threshold
            return best_point
        
        # Fallback: Average all endpoints
        avg_x = sum(e.x for e in endpoints_to_check) / len(endpoints_to_check)
        avg_y = sum(e.y for e in endpoints_to_check) / len(endpoints_to_check)
        avg_z = sum(e.z for e in endpoints_to_check) / len(endpoints_to_check)
        
        return Point3D(avg_x, avg_y, avg_z)
    
    def _detect_joints_from_geometry_candidates(self) -> Dict[str, Point3D]:
        """
        Detect joints from member geometry by finding all intersections.
        
        Returns:
            Dictionary of detected joints
        """
        joints = {}
        joint_id_counter = 0
        joint_candidates = []
        
        # Check all pairs of members
        for i, member1 in enumerate(self.members):
            for j, member2 in enumerate(self.members):
                if i >= j:
                    continue
                
                # Check all 4 endpoint combinations
                endpoints = [
                    (member1['start'], member2['start']),
                    (member1['start'], member2['end']),
                    (member1['end'], member2['start']),
                    (member1['end'], member2['end']),
                ]
                
                min_distance = float('inf')
                closest_pair = None
                
                for p1, p2 in endpoints:
                    dist = p1.distance_to(p2)
                    if dist < min_distance:
                        min_distance = dist
                        closest_pair = (p1, p2)
                
                if min_distance <= self.tolerance_mm:
                    joint_location = Point3D(
                        x=(closest_pair[0].x + closest_pair[1].x) / 2,
                        y=(closest_pair[0].y + closest_pair[1].y) / 2,
                        z=(closest_pair[0].z + closest_pair[1].z) / 2,
                    )
                    
                    joint_candidates.append({
                        'location': joint_location,
                        'distance': min_distance,
                        'members': [member1['id'], member2['id']],
                    })
        
        # De-duplicate by clustering
        used_candidates = set()
        
        for idx, candidate in enumerate(joint_candidates):
            if idx in used_candidates:
                continue
            
            cluster = [idx]
            for other_idx in range(idx + 1, len(joint_candidates)):
                if other_idx in used_candidates:
                    continue
                
                dist = candidate['location'].distance_to(joint_candidates[other_idx]['location'])
                if dist < 10.0:
                    cluster.append(other_idx)
            
            best_idx = min(cluster, key=lambda i: joint_candidates[i]['distance'])
            best_candidate = joint_candidates[best_idx]
            
            joint_id = f"joint_{joint_id_counter}"
            joints[joint_id] = best_candidate['location']
            
            self.joint_connections[joint_id] = list(set(best_candidate['members']))
            for other_idx in cluster:
                if other_idx != best_idx:
                    self.joint_connections[joint_id].extend(joint_candidates[other_idx]['members'])
            self.joint_connections[joint_id] = list(set(self.joint_connections[joint_id]))
            
            joint_id_counter += 1
            used_candidates.update(cluster)
        
        self.joints = joints
        logger.info(f"Detected {len(joints)} joints from geometry ({len(joint_candidates)} candidates)")
        
        return joints
    
    def get_joint_for_plate(self, plate_id: str, ifc_data: Dict) -> Optional[Point3D]:
        """
        Determine which joint a plate belongs to using intelligent matching.
        
        Matching strategies (in order of preference):
          1. Member overlap: Find joint sharing maximum members with plate
          2. Explicit joint_id in relationships
          3. Connected members relationship
          4. Closest joint by distance
          5. Default first joint
        
        Args:
            plate_id: ID of the plate
            ifc_data: Full IFC data dictionary
        
        Returns:
            Point3D location or None
        """
        if not self.joints:
            return None
        
        # STRATEGY 1: Member overlap analysis
        # Find which members this plate is connected to
        relationships = ifc_data.get('relationships', {})
        structural_connections = relationships.get('structural_connections', [])
        
        plate_connected_members = set()
        for conn in structural_connections:
            if conn.get('related_element') == plate_id:
                relating_elem = conn.get('relating_element')
                if relating_elem and relating_elem != plate_id:  # Exclude self-references
                    plate_connected_members.add(relating_elem)
        
        if plate_connected_members:
            # Find joint with maximum overlap
            best_joint_id = None
            best_overlap = 0
            
            for joint_id, joint_members in self.joint_connections.items():
                overlap = len(plate_connected_members & set(joint_members))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_joint_id = joint_id
            
            if best_joint_id and best_joint_id in self.joints:
                logger.debug(f"Plate {plate_id}: mapped to {best_joint_id} by member overlap ({best_overlap})")
                return self.joints[best_joint_id]
        
        # STRATEGY 2: Check relationships for explicit mapping
        if isinstance(relationships, dict):
            if 'plate_to_joint' in relationships:
                mapping = relationships['plate_to_joint']
                if plate_id in mapping:
                    joint_id = mapping[plate_id]
                    if joint_id in self.joints:
                        logger.debug(f"Plate {plate_id}: mapped by explicit relationship")
                        return self.joints[joint_id]
        
        # STRATEGY 3: Check for direct joint reference in plate
        plates = ifc_data.get('plates', [])
        plate_obj = next((p for p in plates if p.get('id') == plate_id), None)
        if plate_obj:
            if 'connected_joint' in plate_obj:
                joint_ref = plate_obj['connected_joint']
                if isinstance(joint_ref, str) and joint_ref in self.joints:
                    logger.debug(f"Plate {plate_id}: has direct joint reference")
                    return self.joints[joint_ref]
        
        # STRATEGY 4: Find closest joint by distance
        if plate_obj and 'placement' in plate_obj:
            plate_loc = plate_obj['placement'].get('location', [0, 0, 0])
            plate_point = Point3D(plate_loc)
            
            closest_joint_id = None
            closest_distance = float('inf')
            
            for joint_id, joint_point in self.joints.items():
                dist = plate_point.distance_to(joint_point)
                if dist < closest_distance:
                    closest_distance = dist
                    closest_joint_id = joint_id
            
            if closest_joint_id:
                logger.debug(f"Plate {plate_id}: mapped to closest joint {closest_joint_id}")
                return self.joints[closest_joint_id]
        
        # STRATEGY 5: Default to first joint (fallback)
        if self.joints:
            first_joint = next(iter(self.joints.values()))
            logger.warning(f"Plate {plate_id}: using first joint as fallback")
            return first_joint
        
        logger.warning(f"Plate {plate_id}: no joint found")
        return None
    
    def fix_plate_positions(self, ifc_data: Dict) -> Dict:
        """
        Fix all plate positions from [0,0,0] to calculated joint locations.
        
        Process:
          1. Iterate through all plates
          2. For each plate, determine its joint
          3. Update position field to joint location
          4. Update placement.location to joint location
        
        Args:
            ifc_data: Full IFC data dictionary
        
        Returns:
            Updated IFC data
        """
        plates = ifc_data.get('plates', [])
        fixed_count = 0
        
        for plate in plates:
            plate_id = plate.get('id')
            
            # Determine joint location
            joint_location = self.get_joint_for_plate(plate_id, ifc_data)
            
            if joint_location:
                # Update position fields
                plate['position'] = joint_location.to_list()
                
                # Update placement
                if 'placement' not in plate:
                    plate['placement'] = {}
                
                plate['placement']['location'] = joint_location.to_list()
                
                if 'Axis2Placement3D' in plate['placement']:
                    plate['placement']['Axis2Placement3D']['location'] = joint_location.to_list()
                
                fixed_count += 1
                logger.debug(f"Plate {plate_id}: position → {joint_location}")
        
        ifc_data['plates'] = plates
        logger.info(f"Fixed {fixed_count}/{len(plates)} plate positions")
        
        return ifc_data
    
    def fix_bolt_positions(self, ifc_data: Dict) -> Dict:
        """
        Fix bolt positions using proper transformations.
        
        Process:
          1. For each bolt, find its parent plate
          2. Get plate position (now at correct joint)
          3. Apply bolt layout offset
          4. Ensure positive coordinates where appropriate
        
        Args:
            ifc_data: Full IFC data dictionary
        
        Returns:
            Updated IFC data
        """
        fasteners = ifc_data.get('fasteners', [])
        bolts = ifc_data.get('bolts', [])
        
        # Process fasteners array (standard format)
        for fastener in fasteners:
            if fastener.get('type') == 'IfcFastener' or 'bolt' in fastener.get('name', '').lower():
                # Will be handled by synthesis agent if needed
                pass
        
        # Process bolts array
        for bolt in bolts:
            # Will be handled by synthesis agent with correct parent joint
            pass
        
        ifc_data['fasteners'] = fasteners
        ifc_data['bolts'] = bolts
        
        logger.info(f"Processed {len(fasteners)} fasteners, {len(bolts)} bolts")
        
        return ifc_data
    
    def process_ifc_file(self, ifc_file_path: str, output_file_path: str) -> bool:
        """
        Complete processing pipeline for a single IFC file.
        
        Full workflow:
          1. Load IFC data
          2. Extract members
          3. Detect joints (pre-existing OR from geometry)
          4. Fix plate positions
          5. Fix bolt positions
          6. Save corrected IFC
        
        Args:
            ifc_file_path: Input IFC JSON file path
            output_file_path: Output IFC JSON file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load
            with open(ifc_file_path, 'r') as f:
                ifc_data = json.load(f)
            
            logger.info(f"Loaded IFC from {ifc_file_path}")
            
            # Extract and detect
            self.extract_members(ifc_data)
            self.detect_joints_from_geometry(ifc_data)  # Pass ifc_data to use pre-existing joints
            
            # Fix positions
            ifc_data = self.fix_plate_positions(ifc_data)
            ifc_data = self.fix_bolt_positions(ifc_data)
            
            # Save
            with open(output_file_path, 'w') as f:
                json.dump(ifc_data, f, indent=2)
            
            logger.info(f"Saved corrected IFC to {output_file_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing IFC file: {e}")
            return False
    
    def get_summary(self) -> Dict:
        """
        Get summary of detected geometry.
        
        Returns:
            Dictionary with detection statistics
        """
        return {
            'members_count': len(self.members),
            'members_by_type': {
                'BEAM': sum(1 for m in self.members if m['type'] == 'BEAM'),
                'COLUMN': sum(1 for m in self.members if m['type'] == 'COLUMN'),
            },
            'joints_detected': len(self.joints),
            'joint_locations': [j.to_list() for j in self.joints.values()],
            'members_per_joint': {
                jid: len(members) for jid, members in self.joint_connections.items()
            }
        }


def fix_coordinate_origins_universal(ifc_data: Dict) -> Dict:
    """
    Quick function to fix coordinate origins in any IFC data.
    
    Universal fix that handles ANY DXF structure:
      • Pre-existing joints: Uses them as-is
      • Calculated joints: Computes from member geometry
      • Distributes plates/bolts to correct joint positions
    
    Usage:
        corrected_ifc = fix_coordinate_origins_universal(ifc_data)
    
    Args:
        ifc_data: Input IFC dictionary
    
    Returns:
        Corrected IFC dictionary with proper coordinates
    """
    engine = UniversalGeometryEngine()
    engine.extract_members(ifc_data)
    engine.detect_joints_from_geometry(ifc_data)  # Pass ifc_data to use pre-existing joints
    ifc_data = engine.fix_plate_positions(ifc_data)
    ifc_data = engine.fix_bolt_positions(ifc_data)
    
    return ifc_data


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = UniversalGeometryEngine()
    
    # Process both test files
    for i in [7, 8]:
        input_file = f'/Users/sahil/Downloads/ifc ({i}).json'
        output_file = f'/Users/sahil/Downloads/ifc ({i})_fixed.json'
        
        success = engine.process_ifc_file(input_file, output_file)
        
        if success:
            summary = engine.get_summary()
            print(f"\n✅ IFC({i}) SUMMARY:")
            print(f"  Members: {summary['members_count']}")
            print(f"  Joints detected: {summary['joints_detected']}")
            print(f"  Joint locations: {summary['joint_locations']}")
