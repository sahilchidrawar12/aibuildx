"""
CONNECTION CLASSIFIER AGENT
============================

Detects connection types from member geometry using AI-driven logic.

Connection types:
- base_plate: Column to foundation (bolted/welded/expansion)
- roof_plate: Column to roof/floor (bolted/welded)
- splice: Member to member along axis (bolted/welded)
- moment_connection: Frame corner connections
- shear_connection: Simple connections
- bracing: Diagonal bracing connections

This agent runs BEFORE connection synthesis to classify each connection,
enabling downstream agents to create correct geometry.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CONNECTION TYPE DEFINITIONS
# ============================================================================

class ConnectionCategory(Enum):
    """Main connection categories."""
    BASE_PLATE = "base_plate"
    ROOF_PLATE = "roof_plate"
    FLOOR_PLATE = "floor_plate"
    SPLICE = "splice"
    MOMENT_CONNECTION = "moment_connection"
    SHEAR_CONNECTION = "shear_connection"
    BRACING = "bracing"
    UNKNOWN = "unknown"

class ConnectionSubtype(Enum):
    """Connection subtypes within categories."""
    # Base plate
    BOLTED_BASE_PLATE = "bolted_base_plate"
    WELDED_BASE_PLATE = "welded_base_plate"
    EXPANSION_BASE_PLATE = "expansion_base_plate"
    
    # Roof/Floor plate
    BOLTED_END_PLATE = "bolted_end_plate"
    WELDED_END_PLATE = "welded_end_plate"
    
    # Splice
    BOLTED_SPLICE = "bolted_splice"
    WELDED_splice = "welded_splice"
    
    # Moment
    WELDED_MOMENT = "welded_moment"
    BOLTED_MOMENT = "bolted_moment"
    
    # Other
    BOLTED_ANGLE = "bolted_angle"
    UNKNOWN = "unknown"

@dataclass
class ConnectionClassification:
    """Connection classification result."""
    connection_id: str
    member_ids: List[str]
    category: ConnectionCategory
    subtype: ConnectionSubtype
    work_point_offset_mm: float  # Offset from member CL to work point
    plate_type: str  # 'end_plate', 'base_plate', 'clip_angle', etc.
    estimated_bolt_count: int
    estimated_bolt_diameter_mm: float
    estimated_plate_dimensions_mm: Tuple[float, float]  # width, height
    estimated_plate_thickness_mm: float
    confidence_score: float  # 0-100%
    reasoning: str

# ============================================================================
# STANDARDS & DETECTION RULES
# ============================================================================

# Based on AISC, AWS, and connection engineering standards

MEMBER_TYPES = {
    'W': 'wide_flange',
    'I': 'wide_flange',
    'C': 'channel',
    'WT': 'tee',
    'HSS': 'hollow_section',
    'PL': 'plate',
    'L': 'angle'
}

# Connection rules (simplified)
CONNECTION_RULES = {
    'base_plate': {
        'indicators': ['z_near_zero', 'vertical_member_ends_here', 'load_concentrated'],
        'min_plate_size_mm': 300,
        'typical_bolt_count': [4, 8, 12],
        'typical_bolt_diameter_mm': [20, 25, 32],
        'typical_thickness_mm': [20, 25, 30]
    },
    'roof_plate': {
        'indicators': ['z_near_max', 'horizontal_loads', 'top_member'],
        'min_plate_size_mm': 200,
        'typical_bolt_count': [4, 8],
        'typical_bolt_diameter_mm': [16, 20, 25],
        'typical_thickness_mm': [12, 16, 20]
    },
    'splice': {
        'indicators': ['members_collinear', 'same_axis', 'mid_span'],
        'min_plate_size_mm': 150,
        'typical_bolt_count': [4, 6, 8],
        'typical_bolt_diameter_mm': [16, 20],
        'typical_thickness_mm': [10, 12, 16]
    }
}

# ============================================================================
# CONNECTION CLASSIFIER
# ============================================================================

class ConnectionClassifier:
    """Classifies connections from member geometry."""

    def __init__(self):
        self.classifications: List[ConnectionClassification] = []
        self.project_bounds = None
        self.member_data_map = {}

    def classify_all_connections(self, members: List[Dict], joints: List[Dict]) -> List[ConnectionClassification]:
        """
        Classify all connections in the structure.
        
        Algorithm:
        1. Build member data map for quick lookup
        2. For each joint, extract connected members
        3. Analyze member geometry, directions, positions
        4. Match patterns to connection types
        5. Estimate connection parameters
        
        Returns:
            List of classified connections
        """
        self.classifications = []
        self.member_data_map = {m.get('id'): m for m in members}
        
        # Calculate project bounds for reference
        self._calculate_project_bounds(members, joints)

        # Process each joint (which represents a connection)
        for joint in joints:
            joint_id = joint.get('id', 'unknown')
            member_ids = joint.get('members', [])

            # Only process joints with 2+ members
            if len(member_ids) < 2:
                continue

            # Get member objects
            joint_members = [self.member_data_map.get(mid) for mid in member_ids if mid in self.member_data_map]
            
            if len(joint_members) < 2:
                continue

            # Classify this connection
            classification = self._classify_joint(joint, joint_members, member_ids)
            self.classifications.append(classification)

        return self.classifications

    def _calculate_project_bounds(self, members: List[Dict], joints: List[Dict]):
        """Calculate project bounding box for reference."""
        all_coords = []
        
        for m in members:
            all_coords.extend(m.get('start', [0, 0, 0]))
            all_coords.extend(m.get('end', [0, 0, 0]))
        
        for j in joints:
            all_coords.extend(j.get('position', [0, 0, 0]))

        if not all_coords:
            self.project_bounds = {'min_z': 0, 'max_z': 10000}
            return

        z_coords = [all_coords[i] for i in range(2, len(all_coords), 3) if i < len(all_coords)]
        self.project_bounds = {
            'min_z': min(z_coords) if z_coords else 0,
            'max_z': max(z_coords) if z_coords else 10000
        }

    def _classify_joint(self, joint: Dict, members: List[Dict], member_ids: List[str]) -> ConnectionClassification:
        """Classify a single joint/connection."""
        joint_id = joint.get('id', 'unknown')
        joint_pos = joint.get('position', [0, 0, 0])

        # Analyze member arrangement
        arrangement = self._analyze_member_arrangement(members, joint_pos)

        # Determine connection type based on arrangement
        if arrangement['type'] == 'vertical_to_horizontal':
            # Could be base plate or roof plate
            if self._is_base_level(joint_pos):
                category, subtype = self._classify_base_connection(members, joint_pos)
            else:
                category, subtype = self._classify_roof_floor_connection(members, joint_pos)
        
        elif arrangement['type'] == 'collinear':
            category = ConnectionCategory.SPLICE
            subtype = ConnectionSubtype.BOLTED_SPLICE  # Default to bolted
        
        elif arrangement['type'] == 'corner':
            category = ConnectionCategory.MOMENT_CONNECTION
            subtype = ConnectionSubtype.BOLTED_MOMENT
        
        else:
            category = ConnectionCategory.SHEAR_CONNECTION
            subtype = ConnectionSubtype.BOLTED_ANGLE

        # Calculate work point offset
        work_point_offset = self._calculate_work_point_offset(category, subtype, members, joint_pos)

        # Estimate connection parameters
        bolt_count, bolt_diameter = self._estimate_bolt_parameters(category, subtype, members)
        plate_dims, plate_thickness = self._estimate_plate_parameters(category, subtype, members)

        # Calculate confidence
        confidence = self._calculate_confidence(arrangement, category)

        reasoning = f"Arrangement: {arrangement['type']}. Members: {[m.get('id') for m in members]}. Position: Z={joint_pos[2]:.1f}mm"

        return ConnectionClassification(
            connection_id=f"{joint_id}_conn",
            member_ids=member_ids,
            category=category,
            subtype=subtype,
            work_point_offset_mm=work_point_offset,
            plate_type=self._get_plate_type(category, subtype),
            estimated_bolt_count=bolt_count,
            estimated_bolt_diameter_mm=bolt_diameter,
            estimated_plate_dimensions_mm=plate_dims,
            estimated_plate_thickness_mm=plate_thickness,
            confidence_score=confidence,
            reasoning=reasoning
        )

    def _analyze_member_arrangement(self, members: List[Dict], joint_pos: List[float]) -> Dict[str, Any]:
        """Analyze how members are arranged at the joint."""
        if len(members) < 2:
            return {'type': 'unknown', 'details': {}}

        # Get member directions
        directions = []
        for member in members:
            start = member.get('start', [0, 0, 0])
            end = member.get('end', [1, 0, 0])
            direction = self._normalize_vector(self._subtract_vectors(end, start))
            directions.append({
                'member': member.get('id'),
                'direction': direction,
                'vertical': self._is_vertical(direction),
                'horizontal': self._is_horizontal(direction)
            })

        # Analyze arrangement
        vertical_count = sum(1 for d in directions if d['vertical'])
        horizontal_count = sum(1 for d in directions if d['horizontal'])

        if vertical_count >= 1 and horizontal_count >= 1:
            arrangement_type = 'vertical_to_horizontal'
        elif self._are_collinear(directions):
            arrangement_type = 'collinear'
        elif len(directions) >= 2 and self._are_perpendicular(directions[0], directions[1]):
            arrangement_type = 'corner'
        else:
            arrangement_type = 'general'

        return {
            'type': arrangement_type,
            'vertical_count': vertical_count,
            'horizontal_count': horizontal_count,
            'directions': directions,
            'total_members': len(members)
        }

    def _is_base_level(self, position: List[float]) -> bool:
        """Check if position is near ground/foundation level."""
        z = position[2] if len(position) > 2 else 0
        
        # Base if within 5% of project min Z
        z_range = self.project_bounds['max_z'] - self.project_bounds['min_z']
        threshold = self.project_bounds['min_z'] + 0.05 * z_range
        
        return z <= threshold

    def _classify_base_connection(self, members: List[Dict], position: List[float]) -> Tuple[ConnectionCategory, ConnectionSubtype]:
        """Classify as base plate connection."""
        # All base connections use bolted_base_plate by default
        # Could be enhanced to detect welded vs bolted vs expansion
        return ConnectionCategory.BASE_PLATE, ConnectionSubtype.BOLTED_BASE_PLATE

    def _classify_roof_floor_connection(self, members: List[Dict], position: List[float]) -> Tuple[ConnectionCategory, ConnectionSubtype]:
        """Classify as roof/floor plate connection."""
        # Check if near roof
        z = position[2] if len(position) > 2 else 0
        z_range = self.project_bounds['max_z'] - self.project_bounds['min_z']
        threshold = self.project_bounds['min_z'] + 0.95 * z_range
        
        if z >= threshold:
            return ConnectionCategory.ROOF_PLATE, ConnectionSubtype.BOLTED_END_PLATE
        else:
            return ConnectionCategory.FLOOR_PLATE, ConnectionSubtype.BOLTED_END_PLATE

    def _calculate_work_point_offset(self, category: ConnectionCategory, subtype: ConnectionSubtype,
                                      members: List[Dict], position: List[float]) -> float:
        """Calculate offset from member center line to connection work point."""
        
        # Work point offset rules (from AISC, typical practice)
        offsets = {
            ConnectionCategory.BASE_PLATE: -150,  # Negative = toward member bottom
            ConnectionCategory.ROOF_PLATE: 150,   # Positive = toward member top
            ConnectionCategory.FLOOR_PLATE: 150,
            ConnectionCategory.SPLICE: 0,
            ConnectionCategory.MOMENT_CONNECTION: 0,
            ConnectionCategory.SHEAR_CONNECTION: 0
        }
        
        return offsets.get(category, 0)

    def _estimate_bolt_parameters(self, category: ConnectionCategory, subtype: ConnectionSubtype,
                                  members: List[Dict]) -> Tuple[int, float]:
        """Estimate bolt count and diameter for connection."""
        
        # Get connection parameters from rules
        rules = CONNECTION_RULES.get(category.value, {})
        
        # Estimate based on member size
        member = members[0] if members else {}
        
        # Estimate bolt diameter based on member size
        if category == ConnectionCategory.BASE_PLATE:
            bolt_diameter = 25  # Standard 25mm for base plates
            bolt_count = 8  # Standard 8 bolts for base plates
        elif category == ConnectionCategory.ROOF_PLATE or category == ConnectionCategory.FLOOR_PLATE:
            bolt_diameter = 20  # Standard 20mm for roof/floor
            bolt_count = 4  # Standard 4 bolts
        elif category == ConnectionCategory.SPLICE:
            bolt_diameter = 20
            bolt_count = 6
        else:
            bolt_diameter = 20
            bolt_count = 4

        return bolt_count, bolt_diameter

    def _estimate_plate_parameters(self, category: ConnectionCategory, subtype: ConnectionSubtype,
                                   members: List[Dict]) -> Tuple[Tuple[float, float], float]:
        """Estimate plate dimensions and thickness."""
        
        if category == ConnectionCategory.BASE_PLATE:
            # Base plates: typically 400×400 to 600×600mm
            width = 400
            height = 400
            thickness = 25  # 25mm typical for base plate
        
        elif category == ConnectionCategory.ROOF_PLATE or category == ConnectionCategory.FLOOR_PLATE:
            # End plates: typically 250×300 to 350×400mm
            width = 300
            height = 350
            thickness = 16  # 16mm typical
        
        elif category == ConnectionCategory.SPLICE:
            # Splice plates: match member size
            width = 200
            height = 250
            thickness = 12
        
        else:
            width = 200
            height = 250
            thickness = 12

        return (width, height), thickness

    def _get_plate_type(self, category: ConnectionCategory, subtype: ConnectionSubtype) -> str:
        """Get plate type string."""
        mapping = {
            ConnectionCategory.BASE_PLATE: 'base_plate',
            ConnectionCategory.ROOF_PLATE: 'end_plate',
            ConnectionCategory.FLOOR_PLATE: 'end_plate',
            ConnectionCategory.SPLICE: 'splice_plate',
            ConnectionCategory.MOMENT_CONNECTION: 'end_plate',
            ConnectionCategory.SHEAR_CONNECTION: 'clip_angle',
        }
        return mapping.get(category, 'unknown')

    def _calculate_confidence(self, arrangement: Dict[str, Any], category: ConnectionCategory) -> float:
        """Calculate confidence score for classification."""
        # Start with 100%
        confidence = 100.0
        
        # Reduce if unusual arrangement
        if arrangement['type'] == 'general':
            confidence -= 20
        
        # Reduce if borderline cases
        if category == ConnectionCategory.UNKNOWN:
            confidence -= 40

        return max(0, confidence)

    # ========== HELPER METHODS ==========

    def _normalize_vector(self, vec: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        length = math.sqrt(sum(v**2 for v in vec))
        if length == 0:
            return [0, 0, 0]
        return [v / length for v in vec]

    def _subtract_vectors(self, v1: List[float], v2: List[float]) -> List[float]:
        """Subtract v2 from v1."""
        return [v1[i] - v2[i] for i in range(min(len(v1), len(v2)))]

    def _is_vertical(self, direction: List[float]) -> bool:
        """Check if direction is predominantly vertical (Z axis)."""
        return abs(direction[2]) > 0.7

    def _is_horizontal(self, direction: List[float]) -> bool:
        """Check if direction is predominantly horizontal (XY plane)."""
        return abs(direction[2]) < 0.3

    def _are_collinear(self, directions: List[Dict]) -> bool:
        """Check if all directions are collinear (parallel or opposite)."""
        if len(directions) < 2:
            return False

        first = directions[0]['direction']
        for d in directions[1:]:
            # Calculate dot product (should be ±1 for collinear)
            dot = sum(first[i] * d['direction'][i] for i in range(3))
            if abs(abs(dot) - 1.0) > 0.1:  # Not collinear
                return False

        return True

    def _are_perpendicular(self, dir1: Dict, dir2: Dict) -> bool:
        """Check if directions are perpendicular."""
        # Calculate dot product (should be ~0 for perpendicular)
        dot = sum(dir1['direction'][i] * dir2['direction'][i] for i in range(3))
        return abs(dot) < 0.3

# ============================================================================
# AGENT PROCESS
# ============================================================================

def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main agent entry point."""
    members = payload.get('members', [])
    joints = payload.get('joints', [])

    # Classify all connections
    classifier = ConnectionClassifier()
    classifications = classifier.classify_all_connections(members, joints)

    # Convert to output format
    classification_list = [
        {
            'connection_id': c.connection_id,
            'member_ids': c.member_ids,
            'category': c.category.value,
            'subtype': c.subtype.value,
            'work_point_offset_mm': c.work_point_offset_mm,
            'plate_type': c.plate_type,
            'estimated_bolt_count': c.estimated_bolt_count,
            'estimated_bolt_diameter_mm': c.estimated_bolt_diameter_mm,
            'estimated_plate_dimensions_mm': c.estimated_plate_dimensions_mm,
            'estimated_plate_thickness_mm': c.estimated_plate_thickness_mm,
            'confidence_score': c.confidence_score,
            'reasoning': c.reasoning
        }
        for c in classifications
    ]

    return {
        'status': 'ok',
        'connections_classified': len(classifications),
        'classifications': classification_list,
        'summary': {
            'base_plates': len([c for c in classifications if c.category == ConnectionCategory.BASE_PLATE]),
            'roof_plates': len([c for c in classifications if c.category == ConnectionCategory.ROOF_PLATE]),
            'splices': len([c for c in classifications if c.category == ConnectionCategory.SPLICE]),
            'other': len([c for c in classifications if c.category not in [
                ConnectionCategory.BASE_PLATE, ConnectionCategory.ROOF_PLATE, ConnectionCategory.SPLICE
            ]])
        }
    }

class ConnectionClassifierAgent:
    """Agent wrapper."""
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
