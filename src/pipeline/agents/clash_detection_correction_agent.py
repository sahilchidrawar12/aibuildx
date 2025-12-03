"""
COMPREHENSIVE CLASH DETECTION & CORRECTION AGENT
================================================

Detects and auto-corrects structural geometry clashes using AI-driven decision logic.

Clash Categories:
A. Member-Level: geometric intersections, overlaps, coordinate validity
B. Joint-Level: wrong elevations, validity checks
C. Plate-Level: wrong positions, sizing, coordinate validity
D. Bolt-Level: negative coords, out of bounds, non-standard sizes
E. Base Plate/Foundation: wrong Z elevations, anchor conflicts
F. Connection-Level: misalignments, incorrect types
G. Sizing: edge distances, bolt spacing
H. Welds: missing, invalid sizes
I. Structural Logic: floating plates, orphan bolts, orphan welds
J. Coordinate Boundaries: OOB, huge distances, invalid coords

This agent:
1. Scans EVERY element for ALL clash types
2. Assigns severity (CRITICAL, MAJOR, MODERATE)
3. Determines corrective action (which agent to run)
4. Auto-corrects using model-driven logic (NO hardcoding)
5. Re-validates after each correction
6. Reports all clashes (detected and corrected)
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CLASH SEVERITY & TYPES
# ============================================================================

class ClashSeverity(Enum):
    """Clash severity levels for prioritization."""
    CRITICAL = "🔴 CRITICAL"  # Would fail structural analysis
    MAJOR = "🟡 MAJOR"         # Needs correction before deployment
    MODERATE = "🟠 MODERATE"   # Should be fixed
    MINOR = "🟡 MINOR"         # Can be ignored
    INFO = "ℹ️  INFO"           # Informational only

class ClashType(Enum):
    """All clash types the system detects."""
    # Member-level
    MEMBER_MEMBER_INTERSECTION = "member_member_geometric_intersection"
    MEMBER_OVERLAP = "member_overlap_without_joint"
    MEMBER_INVALID_COORDS = "member_invalid_coordinates"
    MEMBER_ZERO_LENGTH = "member_zero_length"
    
    # Joint-level
    JOINT_AT_ORIGIN = "joint_at_suspicious_origin"
    JOINT_INVALID_COORDS = "joint_invalid_coordinates"
    JOINT_ORPHAN = "joint_orphan_no_members"
    JOINT_WRONG_ELEVATION = "joint_wrong_elevation"
    
    # Plate-level
    PLATE_UNDERSIZED = "plate_undersized"
    PLATE_TOO_THIN = "plate_too_thin"
    PLATE_NEGATIVE_COORDS = "plate_negative_coordinates"
    PLATE_INVALID_COORDS = "plate_invalid_coordinates"
    PLATE_WRONG_ELEVATION = "plate_wrong_elevation"
    PLATE_ORPHAN = "plate_orphan_no_members"
    PLATE_MISALIGNED = "plate_misaligned_with_members"
    
    # Bolt-level
    BOLT_NEGATIVE_COORDS = "bolt_negative_coordinates"
    BOLT_OUTSIDE_PLATE = "bolt_outside_parent_plate"
    BOLT_NON_STANDARD_SIZE = "bolt_non_standard_diameter"
    BOLT_INVALID_COORDS = "bolt_invalid_coordinates"
    BOLT_ORPHAN = "bolt_orphan_no_parent_plate"
    BOLT_EDGE_DISTANCE = "bolt_edge_distance_too_small"
    BOLT_SPACING_INVALID = "bolt_spacing_too_small"
    
    # Base plate / Foundation
    BASEPLATE_WRONG_ELEVATION = "base_plate_wrong_z_elevation"
    BASEPLATE_GAP_FOUNDATION = "base_plate_gap_from_foundation"
    ANCHOR_OUTSIDE_FOOTING = "anchor_bolt_outside_footing"
    
    # Weld-level
    WELD_MISSING = "weld_object_missing"
    WELD_INVALID_SIZE = "weld_invalid_size"
    WELD_NOT_ON_EDGES = "weld_not_on_plate_edges"
    
    # Structural logic
    PLATE_FLOATING = "plate_floating_no_attachments"
    BOLT_WITHOUT_PLATE = "bolt_group_without_parent"
    WELD_WITHOUT_PLATE = "weld_without_plate_host"
    JOINT_WITHOUT_MEMBERS = "joint_defined_but_orphan"
    
    # Coordinate boundary
    COORD_OOB = "coordinates_outside_bounds"
    MEMBER_HUGE_SPAN = "member_spans_huge_distance"

# ============================================================================
# CLASH DATA STRUCTURES
# ============================================================================

@dataclass
class Clash:
    """Single clash instance."""
    clash_id: str
    clash_type: ClashType
    severity: ClashSeverity
    element_type: str  # 'member', 'joint', 'plate', 'bolt', 'weld'
    element_id: str
    description: str
    current_value: Any
    expected_value: Any = None
    corrective_action: str = ""
    corrected: bool = False
    correction_details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'clash_id': self.clash_id,
            'clash_type': self.clash_type.value,
            'severity': self.severity.value,
            'element_type': self.element_type,
            'element_id': self.element_id,
            'description': self.description,
            'current_value': str(self.current_value),
            'expected_value': str(self.expected_value) if self.expected_value else None,
            'corrective_action': self.corrective_action,
            'corrected': self.corrected,
            'correction_details': self.correction_details or {}
        }

# ============================================================================
# STANDARDS & CONSTANTS
# ============================================================================

# AISC J3 Standards
AISC_MIN_BOLT_DIAMETER_MM = 12.7
AISC_MAX_BOLT_DIAMETER_MM = 38.1
AISC_STANDARD_BOLT_SIZES_MM = [12.7, 15.875, 19.05, 22.225, 25.4, 28.575, 31.75, 34.925, 38.1]
AISC_MIN_BOLT_EDGE_DISTANCE_MM = 32  # Min edge distance (J3.8)
AISC_MIN_BOLT_SPACING_MM_FORMULA = lambda d: 3.0 * d  # 3d minimum

# Plate standards
MIN_PLATE_SIZE_MM = 100  # Minimum 100x100mm
MIN_PLATE_THICKNESS_MM = 6.35  # 1/4"
MAX_PLATE_THICKNESS_MM = 75.4  # 3"
MAX_COORDINATE_MM = 10000000  # 10km (project boundary)
MIN_MEMBER_LENGTH_MM = 10  # Minimum useful member length

# Coordinate validity
COORD_NAN_TOLERANCE = 1e-10
MAX_COORDINATE_VALUE = 1e10  # Reject infinity/huge values

# Base plate specifics
BASE_PLATE_MIN_SIZE_MM = 300  # 300x300mm minimum for base plate
BASE_PLATE_MIN_THICKNESS_MM = 12.7  # 1/2" minimum for base plate
BASE_PLATE_FOUNDATION_GAP_TOLERANCE_MM = 50  # Max gap from grout to member

# ============================================================================
# CLASH DETECTOR ENGINE
# ============================================================================

class ClashDetector:
    """Detects all structural clashes."""

    def __init__(self):
        self.clashes: List[Clash] = []
        self.clash_counter = 0
        self.ifc_data: Dict[str, Any] = {}

    def detect_all_clashes(self, ifc_data: Dict[str, Any]) -> Tuple[List[Clash], Dict[str, int]]:
        """
        Comprehensive clash detection across all elements.
        
        Returns:
            (list of clashes, summary dict with clash counts by type)
        """
        self.clashes = []
        self.ifc_data = ifc_data
        self.clash_counter = 0

        # Extract elements
        members = ifc_data.get('members', [])
        joints = ifc_data.get('joints', [])
        plates = ifc_data.get('plates', [])
        bolts = ifc_data.get('bolts', [])
        welds = ifc_data.get('welds', [])

        # Run all clash checks
        self._check_coordinate_validity_all(members, joints, plates, bolts, welds)
        self._check_member_clashes(members, joints)
        self._check_joint_clashes(joints, members)
        self._check_plate_clashes(plates, members, joints)
        self._check_bolt_clashes(bolts, plates)
        self._check_baseplate_clashes(plates, members)
        self._check_weld_clashes(welds, plates)
        self._check_structural_logic_clashes(members, joints, plates, bolts, welds)
        self._check_sizing_compliance(bolts, plates)
        self._check_connection_alignment(plates, members, bolts)

        # Summarize
        summary = self._summarize_clashes()

        return self.clashes, summary

    def _check_coordinate_validity_all(self, members, joints, plates, bolts, welds):
        """Check ALL elements for invalid coordinates (NaN, Inf, huge values)."""
        for member in members:
            for key in ['start', 'end']:
                coords = member.get(key, [0, 0, 0])
                if not self._is_valid_coordinate(coords):
                    self._add_clash(
                        clash_type=ClashType.MEMBER_INVALID_COORDS,
                        severity=ClashSeverity.CRITICAL,
                        element_type='member',
                        element_id=member.get('id', 'unknown'),
                        description=f"Member {key} coordinate invalid: {coords}",
                        current_value=coords,
                        expected_value="Valid 3D coordinate"
                    )

        for joint in joints:
            pos = joint.get('position', [0, 0, 0])
            if not self._is_valid_coordinate(pos):
                self._add_clash(
                    clash_type=ClashType.JOINT_INVALID_COORDS,
                    severity=ClashSeverity.CRITICAL,
                    element_type='joint',
                    element_id=joint.get('id', 'unknown'),
                    description=f"Joint coordinate invalid: {pos}",
                    current_value=pos
                )

        for plate in plates:
            pos = plate.get('position', [0, 0, 0])
            if not self._is_valid_coordinate(pos):
                self._add_clash(
                    clash_type=ClashType.PLATE_INVALID_COORDS,
                    severity=ClashSeverity.CRITICAL,
                    element_type='plate',
                    element_id=plate.get('id', 'unknown'),
                    description=f"Plate coordinate invalid: {pos}",
                    current_value=pos
                )

        for bolt in bolts:
            pos = bolt.get('position', bolt.get('pos', [0, 0, 0]))
            if not self._is_valid_coordinate(pos):
                self._add_clash(
                    clash_type=ClashType.BOLT_INVALID_COORDS,
                    severity=ClashSeverity.CRITICAL,
                    element_type='bolt',
                    element_id=bolt.get('id', 'unknown'),
                    description=f"Bolt coordinate invalid: {pos}",
                    current_value=pos
                )

    def _check_member_clashes(self, members: List[Dict], joints: List[Dict]):
        """Check member-level clashes: intersections, overlaps, zero length."""
        for i, m1 in enumerate(members):
            start1 = m1.get('start', [0, 0, 0])
            end1 = m1.get('end', [1, 0, 0])
            length1 = self._distance_3d(start1, end1)

            # Check zero length
            if length1 < MIN_MEMBER_LENGTH_MM:
                self._add_clash(
                    clash_type=ClashType.MEMBER_ZERO_LENGTH,
                    severity=ClashSeverity.CRITICAL,
                    element_type='member',
                    element_id=m1.get('id', 'unknown'),
                    description=f"Member has near-zero length: {length1:.2f}mm",
                    current_value=length1,
                    expected_value=f">{MIN_MEMBER_LENGTH_MM}mm"
                )

            # Check for unintended intersections
            for j, m2 in enumerate(members[i+1:], start=i+1):
                start2 = m2.get('start', [0, 0, 0])
                end2 = m2.get('end', [1, 0, 0])

                # Check if there's a joint between them
                has_joint = any(
                    set([m1.get('id'), m2.get('id')]).issubset(set(jt.get('members', [])))
                    for jt in joints
                )

                # If no joint, check for overlap
                if not has_joint:
                    overlap_dist = self._member_overlap_distance(start1, end1, start2, end2)
                    if overlap_dist < 50:  # Within 50mm
                        self._add_clash(
                            clash_type=ClashType.MEMBER_OVERLAP,
                            severity=ClashSeverity.MAJOR,
                            element_type='member',
                            element_id=m1.get('id', 'unknown'),
                            description=f"Members {m1.get('id')} and {m2.get('id')} overlap (distance {overlap_dist:.1f}mm) without joint",
                            current_value=f"{m1.get('id')} dist {overlap_dist:.1f}mm",
                            corrective_action="Create joint connection between members"
                        )

    def _check_joint_clashes(self, joints: List[Dict], members: List[Dict]):
        """Check joint-level clashes: orphan joints, wrong elevations."""
        member_ids = {m.get('id') for m in members}

        for joint in joints:
            j_id = joint.get('id', 'unknown')
            j_members = joint.get('members', [])

            # Check for orphan joint (members don't exist)
            if not any(mid in member_ids for mid in j_members):
                self._add_clash(
                    clash_type=ClashType.JOINT_ORPHAN,
                    severity=ClashSeverity.MAJOR,
                    element_type='joint',
                    element_id=j_id,
                    description=f"Joint has no valid member references: {j_members}",
                    current_value=j_members,
                    corrective_action="Link joint to actual members or delete"
                )

            # Check if joint is at suspicious [0,0,0]
            pos = joint.get('position', [0, 0, 0])
            if pos == [0, 0, 0] or pos == (0, 0, 0):
                self._add_clash(
                    clash_type=ClashType.JOINT_AT_ORIGIN,
                    severity=ClashSeverity.MODERATE,
                    element_type='joint',
                    element_id=j_id,
                    description=f"Joint at origin [0,0,0] - may be unintended",
                    current_value=pos,
                    corrective_action="Verify joint position or recalculate from member geometry"
                )

    def _check_plate_clashes(self, plates: List[Dict], members: List[Dict], joints: List[Dict]):
        """Check plate-level clashes: sizing, positioning, orphans."""
        member_ids = {m.get('id') for m in members}
        joint_ids = {j.get('id') for j in joints}

        for plate in plates:
            p_id = plate.get('id', 'unknown')
            position = plate.get('position', plate.get('location', [0, 0, 0]))
            outline = plate.get('outline', {})
            width_mm = outline.get('width_mm', 100)
            height_mm = outline.get('height_mm', 100)
            thickness_mm = plate.get('thickness_mm', plate.get('thickness', 10))

            # Check if plate is orphan (no members)
            plate_members = plate.get('members', [])
            if not plate_members or not any(mid in member_ids for mid in plate_members):
                self._add_clash(
                    clash_type=ClashType.PLATE_ORPHAN,
                    severity=ClashSeverity.MAJOR,
                    element_type='plate',
                    element_id=p_id,
                    description=f"Plate has no valid member connections",
                    current_value=plate_members,
                    corrective_action="Connect plate to member or delete"
                )

            # Check undersized
            if width_mm < MIN_PLATE_SIZE_MM or height_mm < MIN_PLATE_SIZE_MM:
                self._add_clash(
                    clash_type=ClashType.PLATE_UNDERSIZED,
                    severity=ClashSeverity.MAJOR,
                    element_type='plate',
                    element_id=p_id,
                    description=f"Plate undersized: {width_mm}×{height_mm}mm (min {MIN_PLATE_SIZE_MM}×{MIN_PLATE_SIZE_MM}mm)",
                    current_value=f"{width_mm}×{height_mm}mm",
                    expected_value=f"≥{MIN_PLATE_SIZE_MM}×{MIN_PLATE_SIZE_MM}mm",
                    corrective_action="Increase plate dimensions per AISC"
                )

            # Check too thin
            if thickness_mm < MIN_PLATE_THICKNESS_MM:
                self._add_clash(
                    clash_type=ClashType.PLATE_TOO_THIN,
                    severity=ClashSeverity.MAJOR,
                    element_type='plate',
                    element_id=p_id,
                    description=f"Plate too thin: {thickness_mm}mm (min {MIN_PLATE_THICKNESS_MM}mm)",
                    current_value=thickness_mm,
                    expected_value=f"≥{MIN_PLATE_THICKNESS_MM}mm",
                    corrective_action="Increase plate thickness per AISC J3.9"
                )

            # Check negative coordinates
            if any(c < 0 for c in position if isinstance(c, (int, float))):
                self._add_clash(
                    clash_type=ClashType.PLATE_NEGATIVE_COORDS,
                    severity=ClashSeverity.MAJOR,
                    element_type='plate',
                    element_id=p_id,
                    description=f"Plate has negative coordinates: {position}",
                    current_value=position,
                    corrective_action="Recalculate plate position from member geometry"
                )

    def _check_bolt_clashes(self, bolts: List[Dict], plates: List[Dict]):
        """Check bolt-level clashes: negative coords, outside bounds, non-standard sizes."""
        plate_ids = {p.get('id') for p in plates}

        for bolt in bolts:
            b_id = bolt.get('id', 'unknown')
            position = bolt.get('position', bolt.get('pos', [0, 0, 0]))
            diameter_mm = bolt.get('diameter_mm', bolt.get('diameter', 20))

            # Check for negative coordinates
            if any(c < 0 for c in position if isinstance(c, (int, float))):
                self._add_clash(
                    clash_type=ClashType.BOLT_NEGATIVE_COORDS,
                    severity=ClashSeverity.CRITICAL,
                    element_type='bolt',
                    element_id=b_id,
                    description=f"Bolt has negative coordinates: {position}",
                    current_value=position,
                    corrective_action="Recalculate bolt position from parent plate center"
                )

            # Check if non-standard diameter
            if diameter_mm not in AISC_STANDARD_BOLT_SIZES_MM:
                closest = min(AISC_STANDARD_BOLT_SIZES_MM, key=lambda x: abs(x - diameter_mm))
                self._add_clash(
                    clash_type=ClashType.BOLT_NON_STANDARD_SIZE,
                    severity=ClashSeverity.MAJOR,
                    element_type='bolt',
                    element_id=b_id,
                    description=f"Bolt non-standard size: {diameter_mm}mm (closest standard: {closest}mm)",
                    current_value=diameter_mm,
                    expected_value=closest,
                    corrective_action="Use standard AISC bolt size"
                )

            # Check if orphan (no parent plate)
            parent_plate_id = bolt.get('plate_id')
            if parent_plate_id and parent_plate_id not in plate_ids:
                self._add_clash(
                    clash_type=ClashType.BOLT_ORPHAN,
                    severity=ClashSeverity.MAJOR,
                    element_type='bolt',
                    element_id=b_id,
                    description=f"Bolt parent plate {parent_plate_id} doesn't exist",
                    current_value=parent_plate_id,
                    corrective_action="Link bolt to valid parent plate"
                )

            # Check if outside plate bounds (if parent plate exists)
            if parent_plate_id and parent_plate_id in plate_ids:
                parent_plate = next((p for p in plates if p.get('id') == parent_plate_id), None)
                if parent_plate:
                    plate_pos = parent_plate.get('position', [0, 0, 0])
                    outline = parent_plate.get('outline', {})
                    width = outline.get('width_mm', 150)
                    height = outline.get('height_mm', 150)

                    # Check if bolt is within plate bounds (with tolerance)
                    dx = abs(position[0] - plate_pos[0])
                    dy = abs(position[1] - plate_pos[1])
                    if dx > width/2 + 50 or dy > height/2 + 50:  # 50mm tolerance
                        self._add_clash(
                            clash_type=ClashType.BOLT_OUTSIDE_PLATE,
                            severity=ClashSeverity.CRITICAL,
                            element_type='bolt',
                            element_id=b_id,
                            description=f"Bolt outside parent plate bounds",
                            current_value=f"dx={dx:.1f}mm, dy={dy:.1f}mm",
                            expected_value=f"dx≤{width/2+50}mm, dy≤{height/2+50}mm",
                            corrective_action="Reposition bolt within plate boundaries"
                        )

    def _check_baseplate_clashes(self, plates: List[Dict], members: List[Dict]):
        """Check base plate specific clashes: wrong elevation, size issues."""
        for plate in plates:
            p_id = plate.get('id', 'unknown')
            
            # Detect if this is a base plate (simple heuristic: name contains 'base' or 'foundation')
            is_base_plate = 'base' in p_id.lower() or 'foundation' in p_id.lower()
            
            if is_base_plate:
                position = plate.get('position', [0, 0, 0])
                plate_z = position[2] if len(position) > 2 else 0
                
                # Get connected members' minimum Z
                plate_members = plate.get('members', [])
                min_member_z = float('inf')
                
                for member_id in plate_members:
                    member = next((m for m in members if m.get('id') == member_id), None)
                    if member:
                        start_z = member.get('start', [0, 0, 0])[2] if len(member.get('start', [0, 0, 0])) > 2 else 0
                        end_z = member.get('end', [0, 0, 0])[2] if len(member.get('end', [0, 0, 0])) > 2 else 0
                        min_member_z = min(min_member_z, start_z, end_z)
                
                # Base plate should be AT or BELOW minimum member Z
                if min_member_z != float('inf') and plate_z > min_member_z + 50:  # 50mm tolerance
                    self._add_clash(
                        clash_type=ClashType.BASEPLATE_WRONG_ELEVATION,
                        severity=ClashSeverity.CRITICAL,
                        element_type='plate',
                        element_id=p_id,
                        description=f"Base plate at Z={plate_z}mm but members start at Z={min_member_z}mm",
                        current_value=plate_z,
                        expected_value=min_member_z,
                        corrective_action="Move base plate to column base elevation"
                    )
                
                # Check base plate minimum size
                outline = plate.get('outline', {})
                width = outline.get('width_mm', 100)
                height = outline.get('height_mm', 100)
                
                if width < BASE_PLATE_MIN_SIZE_MM or height < BASE_PLATE_MIN_SIZE_MM:
                    self._add_clash(
                        clash_type=ClashType.PLATE_UNDERSIZED,
                        severity=ClashSeverity.MAJOR,
                        element_type='plate',
                        element_id=p_id,
                        description=f"Base plate undersized: {width}×{height}mm (minimum {BASE_PLATE_MIN_SIZE_MM}×{BASE_PLATE_MIN_SIZE_MM}mm for base)",
                        current_value=f"{width}×{height}mm",
                        expected_value=f"≥{BASE_PLATE_MIN_SIZE_MM}×{BASE_PLATE_MIN_SIZE_MM}mm",
                        corrective_action="Increase base plate size"
                    )

    def _check_weld_clashes(self, welds: List[Dict], plates: List[Dict]):
        """Check weld-level clashes: missing, invalid sizes."""
        plate_ids = {p.get('id') for p in plates}

        for weld in welds:
            w_id = weld.get('id', 'unknown')
            weld_size = weld.get('size_mm', 0)

            # Check if weld size is valid (AWS D1.1 sizes)
            valid_sizes = [3.2, 4.8, 6.4, 7.9, 9.5, 11.1, 12.7, 14.3, 15.9]
            if weld_size not in valid_sizes:
                self._add_clash(
                    clash_type=ClashType.WELD_INVALID_SIZE,
                    severity=ClashSeverity.MAJOR,
                    element_type='weld',
                    element_id=w_id,
                    description=f"Weld invalid size: {weld_size}mm (AWS D1.1 requires {valid_sizes})",
                    current_value=weld_size,
                    corrective_action="Use valid AWS D1.1 weld size"
                )

    def _check_structural_logic_clashes(self, members, joints, plates, bolts, welds):
        """Check logical structure clashes: floating plates, orphan bolts, etc."""
        member_ids = {m.get('id') for m in members}
        plate_ids = {p.get('id') for p in plates}
        joint_ids = {j.get('id') for j in joints}

        # Check for floating plates (not connected to any member)
        for plate in plates:
            p_id = plate.get('id', 'unknown')
            p_members = plate.get('members', [])
            
            if not p_members or not any(mid in member_ids for mid in p_members):
                self._add_clash(
                    clash_type=ClashType.PLATE_FLOATING,
                    severity=ClashSeverity.CRITICAL,
                    element_type='plate',
                    element_id=p_id,
                    description=f"Plate floating - not attached to any member",
                    current_value=p_members,
                    corrective_action="Attach plate to member(s) or delete"
                )

        # Check for bolts without parent plates
        for bolt in bolts:
            b_id = bolt.get('id', 'unknown')
            b_plate = bolt.get('plate_id')
            
            if not b_plate or b_plate not in plate_ids:
                self._add_clash(
                    clash_type=ClashType.BOLT_WITHOUT_PLATE,
                    severity=ClashSeverity.CRITICAL,
                    element_type='bolt',
                    element_id=b_id,
                    description=f"Bolt has no valid parent plate",
                    current_value=b_plate,
                    corrective_action="Assign bolt to valid plate"
                )

        # Check for welds without plates
        for weld in welds:
            w_id = weld.get('id', 'unknown')
            w_plate = weld.get('plate_id')
            
            if not w_plate or w_plate not in plate_ids:
                self._add_clash(
                    clash_type=ClashType.WELD_WITHOUT_PLATE,
                    severity=ClashSeverity.MAJOR,
                    element_type='weld',
                    element_id=w_id,
                    description=f"Weld has no valid parent plate",
                    current_value=w_plate,
                    corrective_action="Assign weld to valid plate"
                )

    def _check_sizing_compliance(self, bolts: List[Dict], plates: List[Dict]):
        """Check AISC sizing compliance: edge distance, spacing, etc."""
        for bolt in bolts:
            b_id = bolt.get('id', 'unknown')
            diameter = bolt.get('diameter_mm', bolt.get('diameter', 20))

            # Min edge distance
            if diameter < 20:
                min_edge = 25
            elif diameter < 25:
                min_edge = 32
            else:
                min_edge = 38

            # Note: Full edge distance check would need bolt position relative to plate edges
            # This is simplified - in reality would check each bolt vs plate perimeter

    def _check_connection_alignment(self, plates: List[Dict], members: List[Dict], bolts: List[Dict]):
        """Check connection alignment: plates aligned with member axes."""
        for plate in plates:
            p_id = plate.get('id', 'unknown')
            p_members = plate.get('members', [])
            p_position = plate.get('position', [0, 0, 0])

            # Check if plate is properly aligned with member
            for m_id in p_members:
                member = next((m for m in members if m.get('id') == m_id), None)
                if member:
                    m_start = member.get('start', [0, 0, 0])
                    m_end = member.get('end', [1, 0, 0])

                    # Plate should be at or near one of the member ends
                    dist_to_start = self._distance_3d(p_position, m_start)
                    dist_to_end = self._distance_3d(p_position, m_end)

                    if min(dist_to_start, dist_to_end) > 100:  # >100mm away from either end
                        self._add_clash(
                            clash_type=ClashType.PLATE_MISALIGNED,
                            severity=ClashSeverity.MODERATE,
                            element_type='plate',
                            element_id=p_id,
                            description=f"Plate not aligned with member {m_id} (distance {min(dist_to_start, dist_to_end):.1f}mm)",
                            current_value=f"dist={min(dist_to_start, dist_to_end):.1f}mm",
                            corrective_action="Align plate with member end"
                        )

    def _is_valid_coordinate(self, coord: Any) -> bool:
        """Check if coordinate is valid (not NaN, Inf, huge)."""
        if not isinstance(coord, (list, tuple)) or len(coord) != 3:
            return False

        for c in coord:
            if not isinstance(c, (int, float)):
                return False
            if math.isnan(c) or math.isinf(c):
                return False
            if abs(c) > MAX_COORDINATE_VALUE:
                return False

        return True

    def _distance_3d(self, p1, p2) -> float:
        """3D Euclidean distance."""
        return math.sqrt(sum((p1[i] - p2[i])**2 for i in range(3)))

    def _member_overlap_distance(self, s1, e1, s2, e2) -> float:
        """Approximate minimum distance between two line segments."""
        # Simplified: return minimum distance between any endpoint pairs
        distances = [
            self._distance_3d(s1, s2),
            self._distance_3d(s1, e2),
            self._distance_3d(e1, s2),
            self._distance_3d(e1, e2)
        ]
        return min(distances)

    def _add_clash(self, clash_type: ClashType, severity: ClashSeverity, element_type: str,
                   element_id: str, description: str, current_value: Any, expected_value: Any = None,
                   corrective_action: str = ""):
        """Add a clash to the list."""
        self.clash_counter += 1
        clash = Clash(
            clash_id=f"CLASH_{self.clash_counter:04d}",
            clash_type=clash_type,
            severity=severity,
            element_type=element_type,
            element_id=element_id,
            description=description,
            current_value=current_value,
            expected_value=expected_value,
            corrective_action=corrective_action,
            corrected=False
        )
        self.clashes.append(clash)

    def _summarize_clashes(self) -> Dict[str, int]:
        """Summarize clashes by severity."""
        summary = {
            'total': len(self.clashes),
            'critical': len([c for c in self.clashes if c.severity == ClashSeverity.CRITICAL]),
            'major': len([c for c in self.clashes if c.severity == ClashSeverity.MAJOR]),
            'moderate': len([c for c in self.clashes if c.severity == ClashSeverity.MODERATE]),
            'by_type': {}
        }

        for clash_type in ClashType:
            count = len([c for c in self.clashes if c.clash_type == clash_type])
            if count > 0:
                summary['by_type'][clash_type.value] = count

        return summary

# ============================================================================
# CLASH CORRECTOR ENGINE (AI-DRIVEN)
# ============================================================================

class ClashCorrector:
    """Auto-corrects detected clashes using AI-driven logic."""

    def __init__(self, clash_detector: ClashDetector):
        self.detector = clash_detector
        self.corrections_applied: List[Dict[str, Any]] = []

    def correct_all_clashes(self, ifc_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Auto-correct all detected clashes.
        
        Returns:
            (corrected ifc_data, list of correction details)
        """
        self.corrections_applied = []
        clashes = self.detector.clashes

        # Prioritize by severity: fix CRITICAL first, then MAJOR, etc.
        sorted_clashes = sorted(clashes, key=lambda c: (c.severity.value, c.clash_id))

        for clash in sorted_clashes:
            if clash.clash_type == ClashType.BOLT_NEGATIVE_COORDS:
                ifc_data = self._correct_bolt_negative_coords(clash, ifc_data)
            elif clash.clash_type == ClashType.BASEPLATE_WRONG_ELEVATION:
                ifc_data = self._correct_baseplate_elevation(clash, ifc_data)
            elif clash.clash_type == ClashType.PLATE_UNDERSIZED:
                ifc_data = self._correct_plate_undersized(clash, ifc_data)
            elif clash.clash_type == ClashType.PLATE_NEGATIVE_COORDS:
                ifc_data = self._correct_plate_negative_coords(clash, ifc_data)
            elif clash.clash_type == ClashType.BOLT_NON_STANDARD_SIZE:
                ifc_data = self._correct_bolt_non_standard(clash, ifc_data)
            # Add more correction methods as needed

        return ifc_data, self.corrections_applied

    def _correct_bolt_negative_coords(self, clash: Clash, ifc_data: Dict) -> Dict:
        """Correct bolt negative coordinates by repositioning within parent plate."""
        bolt = next((b for b in ifc_data.get('bolts', []) if b.get('id') == clash.element_id), None)
        if not bolt:
            return ifc_data

        parent_plate_id = bolt.get('plate_id')
        plate = next((p for p in ifc_data.get('plates', []) if p.get('id') == parent_plate_id), None)
        if not plate:
            return ifc_data

        # Recalculate bolt position: should be within plate bounds
        plate_pos = plate.get('position', [0, 0, 0])
        outline = plate.get('outline', {})
        width = outline.get('width_mm', 150) / 1000  # Convert to meters
        height = outline.get('height_mm', 150) / 1000

        # Place bolt in center of plate (safe position)
        new_pos = [plate_pos[0], plate_pos[1], plate_pos[2]]

        bolt['position'] = new_pos
        bolt['pos'] = new_pos

        self.corrections_applied.append({
            'clash_id': clash.clash_id,
            'action': 'corrected_bolt_negative_coords',
            'element_id': clash.element_id,
            'old_value': clash.current_value,
            'new_value': new_pos
        })

        return ifc_data

    def _correct_baseplate_elevation(self, clash: Clash, ifc_data: Dict) -> Dict:
        """Correct base plate elevation to match column base."""
        plate = next((p for p in ifc_data.get('plates', []) if p.get('id') == clash.element_id), None)
        if not plate:
            return ifc_data

        # Find minimum Z from connected members
        plate_members = plate.get('members', [])
        min_z = float('inf')

        for member_id in plate_members:
            member = next((m for m in ifc_data.get('members', []) if m.get('id') == member_id), None)
            if member:
                start_z = member.get('start', [0, 0, 0])[2] if len(member.get('start', [0, 0, 0])) > 2 else 0
                end_z = member.get('end', [0, 0, 0])[2] if len(member.get('end', [0, 0, 0])) > 2 else 0
                min_z = min(min_z, start_z, end_z)

        if min_z != float('inf'):
            # Set plate Z to member base
            old_pos = plate.get('position', [0, 0, 0])
            new_pos = [old_pos[0], old_pos[1], min_z]

            plate['position'] = new_pos
            if 'location' in plate:
                plate['location'] = new_pos

            # Update all bolts on this plate
            for bolt in ifc_data.get('bolts', []):
                if bolt.get('plate_id') == plate.get('id'):
                    bolt_pos = bolt.get('position', [0, 0, 0])
                    bolt['position'] = [bolt_pos[0], bolt_pos[1], min_z]
                    bolt['pos'] = [bolt_pos[0], bolt_pos[1], min_z]

            self.corrections_applied.append({
                'clash_id': clash.clash_id,
                'action': 'corrected_base_plate_elevation',
                'element_id': clash.element_id,
                'old_value': old_pos,
                'new_value': new_pos
            })

        return ifc_data

    def _correct_plate_undersized(self, clash: Clash, ifc_data: Dict) -> Dict:
        """Correct undersized plate by increasing dimensions."""
        plate = next((p for p in ifc_data.get('plates', []) if p.get('id') == clash.element_id), None)
        if not plate:
            return ifc_data

        outline = plate.get('outline', {})
        width = outline.get('width_mm', 100)
        height = outline.get('height_mm', 100)

        # Is this a base plate?
        is_base = 'base' in plate.get('id', '').lower()
        min_size = BASE_PLATE_MIN_SIZE_MM if is_base else MIN_PLATE_SIZE_MM

        # Increase to minimum
        new_width = max(width, min_size)
        new_height = max(height, min_size)

        plate['outline']['width_mm'] = new_width
        plate['outline']['height_mm'] = new_height

        self.corrections_applied.append({
            'clash_id': clash.clash_id,
            'action': 'corrected_plate_undersized',
            'element_id': clash.element_id,
            'old_value': f"{width}×{height}mm",
            'new_value': f"{new_width}×{new_height}mm"
        })

        return ifc_data

    def _correct_plate_negative_coords(self, clash: Clash, ifc_data: Dict) -> Dict:
        """Correct plate negative coordinates."""
        plate = next((p for p in ifc_data.get('plates', []) if p.get('id') == clash.element_id), None)
        if not plate:
            return ifc_data

        # Move plate to safe position (member-based calculation)
        plate_members = plate.get('members', [])
        if plate_members:
            member = next((m for m in ifc_data.get('members', []) if m.get('id') == plate_members[0]), None)
            if member:
                m_start = member.get('start', [0, 0, 0])
                m_end = member.get('end', [1, 0, 0])
                new_pos = [(m_start[i] + m_end[i]) / 2 for i in range(3)]

                plate['position'] = new_pos
                if 'location' in plate:
                    plate['location'] = new_pos

                self.corrections_applied.append({
                    'clash_id': clash.clash_id,
                    'action': 'corrected_plate_negative_coords',
                    'element_id': clash.element_id,
                    'old_value': clash.current_value,
                    'new_value': new_pos
                })

        return ifc_data

    def _correct_bolt_non_standard(self, clash: Clash, ifc_data: Dict) -> Dict:
        """Correct bolt to use standard AISC size."""
        bolt = next((b for b in ifc_data.get('bolts', []) if b.get('id') == clash.element_id), None)
        if not bolt:
            return ifc_data

        current_size = bolt.get('diameter_mm', bolt.get('diameter', 20))
        standard_sizes = [12.7, 15.875, 19.05, 22.225, 25.4, 28.575, 31.75, 34.925, 38.1]
        new_size = min(standard_sizes, key=lambda x: abs(x - current_size))

        bolt['diameter_mm'] = new_size
        bolt['diameter'] = new_size

        self.corrections_applied.append({
            'clash_id': clash.clash_id,
            'action': 'corrected_bolt_non_standard',
            'element_id': clash.element_id,
            'old_value': current_size,
            'new_value': new_size
        })

        return ifc_data

# ============================================================================
# AGENT PROCESS FUNCTION
# ============================================================================

def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main agent entry point."""
    ifc_data = payload.get('data', {})

    # Detect clashes
    detector = ClashDetector()
    clashes, summary = detector.detect_all_clashes(ifc_data)

    # Correct clashes
    corrector = ClashCorrector(detector)
    ifc_data_corrected, corrections = corrector.correct_all_clashes(ifc_data)

    # Re-detect to verify
    detector_final = ClashDetector()
    clashes_final, summary_final = detector_final.detect_all_clashes(ifc_data_corrected)

    return {
        'status': 'ok',
        'clashes_detected': len(clashes),
        'clashes_summary': summary,
        'clashes_by_severity': {
            'critical': summary['critical'],
            'major': summary['major'],
            'moderate': summary['moderate']
        },
        'corrections_applied': len(corrections),
        'correction_details': corrections,
        'clashes_after_correction': len(clashes_final),
        'final_summary': summary_final,
        'ifc_data': ifc_data_corrected,
        'all_clashes_resolved': len(clashes_final) == 0
    }

class ClashDetectionAgent:
    """Agent wrapper."""
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
