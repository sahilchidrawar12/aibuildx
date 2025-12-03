"""
TEST SUITE: CLASH DETECTION & CORRECTION AGENTS
=================================================

Comprehensive test cases for the clash detection and correction system.
Run with: python -m pytest tests/test_clash_detection.py -v
"""

import pytest
import math
from typing import List, Dict, Any

# Import the agents
import sys
sys.path.insert(0, '/Users/sahil/Documents/aibuildx')

from src.pipeline.agents.clash_detection_correction_agent import (
    ClashDetector, ClashCorrector, ClashType, ClashSeverity, Clash
)
from src.pipeline.agents.connection_classifier_agent import (
    ConnectionClassifier, ConnectionCategory, ConnectionSubtype
)

# ============================================================================
# TEST FIXTURES: Sample data
# ============================================================================

@pytest.fixture
def basic_members():
    """Basic member structure: simple column."""
    return [
        {
            'id': 'col_1',
            'start': [0, 0, 0],
            'end': [0, 0, 3000],
            'section': 'W12x120',
            'material': 'A36'
        }
    ]

@pytest.fixture
def basic_joints():
    """Basic joint at column base."""
    return [
        {
            'id': 'joint_base',
            'position': [0, 0, 0],
            'members': ['col_1']
        },
        {
            'id': 'joint_roof',
            'position': [0, 0, 3000],
            'members': ['col_1']
        }
    ]

@pytest.fixture
def flawed_baseplate():
    """Base plate with multiple clashes."""
    return {
        'id': 'plate_base',
        'position': [0, 0, 3000],  # CLASH: wrong Z (should be 0)
        'location': [0, 0, 3000],
        'outline': {
            'width_mm': 150,    # CLASH: undersized (should be 400+)
            'height_mm': 150    # CLASH: undersized
        },
        'thickness_mm': 10,     # CLASH: too thin (should be 20+)
        'thickness': 0.01,
        'members': ['col_1']
    }

@pytest.fixture
def flawed_bolts():
    """Bolts with negative coordinates."""
    return [
        {
            'id': 'bolt_1',
            'position': [-0.05595, -0.05595, 0.0],  # CLASH: negative coords
            'pos': [-0.05595, -0.05595, 0.0],
            'diameter_mm': 25,
            'diameter': 0.025,
            'plate_id': 'plate_base'
        },
        {
            'id': 'bolt_2',
            'position': [-0.05595, 0.05595, 0.0],   # CLASH: negative coords
            'pos': [-0.05595, 0.05595, 0.0],
            'diameter_mm': 25,
            'diameter': 0.025,
            'plate_id': 'plate_base'
        }
    ]

@pytest.fixture
def good_baseplate():
    """Corrected base plate."""
    return {
        'id': 'plate_base',
        'position': [0, 0, 0],  # Corrected Z
        'location': [0, 0, 0],
        'outline': {
            'width_mm': 400,    # Corrected size
            'height_mm': 400
        },
        'thickness_mm': 25,     # Corrected thickness
        'thickness': 0.025,
        'members': ['col_1']
    }

@pytest.fixture
def good_bolts():
    """Corrected bolts."""
    return [
        {
            'id': 'bolt_1',
            'position': [0.0, 0.0, 0.0],  # Corrected: positive coords
            'pos': [0.0, 0.0, 0.0],
            'diameter_mm': 25,
            'diameter': 0.025,
            'plate_id': 'plate_base'
        },
        {
            'id': 'bolt_2',
            'position': [0.1, 0.0, 0.0],  # Corrected: positive coords
            'pos': [0.1, 0.0, 0.0],
            'diameter_mm': 25,
            'diameter': 0.025,
            'plate_id': 'plate_base'
        }
    ]

# ============================================================================
# TEST: CLASH DETECTION
# ============================================================================

class TestClashDetection:
    """Test cases for ClashDetector."""

    def test_detect_base_plate_wrong_elevation(self, basic_members, basic_joints, flawed_baseplate):
        """Test detection of base plate at wrong Z elevation."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [],
            'welds': []
        })

        # Check for BASEPLATE_WRONG_ELEVATION clash
        wrong_elev_clashes = [c for c in clashes if c.clash_type == ClashType.BASEPLATE_WRONG_ELEVATION]
        assert len(wrong_elev_clashes) > 0, "Should detect base plate wrong elevation"
        
        clash = wrong_elev_clashes[0]
        assert clash.severity == ClashSeverity.CRITICAL, "Wrong elevation should be CRITICAL"
        assert clash.current_value == 3000, "Should report current Z = 3000"

    def test_detect_base_plate_undersized(self, basic_members, basic_joints, flawed_baseplate):
        """Test detection of undersized base plate."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [],
            'welds': []
        })

        # Check for PLATE_UNDERSIZED clash
        undersized_clashes = [c for c in clashes if c.clash_type == ClashType.PLATE_UNDERSIZED]
        assert len(undersized_clashes) > 0, "Should detect undersized plate"
        
        clash = undersized_clashes[0]
        assert clash.severity == ClashSeverity.MAJOR, "Undersized plate should be MAJOR"

    def test_detect_plate_too_thin(self, basic_members, basic_joints, flawed_baseplate):
        """Test detection of plate too thin."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [],
            'welds': []
        })

        # Check for PLATE_TOO_THIN clash
        thin_clashes = [c for c in clashes if c.clash_type == ClashType.PLATE_TOO_THIN]
        assert len(thin_clashes) > 0, "Should detect too thin plate"

    def test_detect_bolt_negative_coords(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test detection of bolts with negative coordinates."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        # Check for BOLT_NEGATIVE_COORDS clash
        neg_bolts = [c for c in clashes if c.clash_type == ClashType.BOLT_NEGATIVE_COORDS]
        assert len(neg_bolts) >= 2, "Should detect 2 bolts with negative coords"
        
        for clash in neg_bolts:
            assert clash.severity == ClashSeverity.CRITICAL, "Negative bolts should be CRITICAL"

    def test_detect_bolt_outside_plate(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test detection of bolts outside parent plate."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,  # Bolts outside 150×150 plate
            'welds': []
        })

        # Check for BOLT_OUTSIDE_PLATE clash
        outside_clashes = [c for c in clashes if c.clash_type == ClashType.BOLT_OUTSIDE_PLATE]
        assert len(outside_clashes) > 0, "Should detect bolts outside plate"

    def test_clash_summary_counts(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test clash summary statistics."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        assert summary['total'] > 0, "Should detect at least 1 clash"
        assert summary['critical'] > 0, "Should have at least 1 CRITICAL clash"
        assert summary['major'] > 0, "Should have at least 1 MAJOR clash"
        print(f"✓ Detected {summary['total']} clashes: {summary['critical']} critical, {summary['major']} major")

    def test_no_clashes_in_good_model(self, basic_members, basic_joints, good_baseplate, good_bolts):
        """Test that good model has no clashes."""
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [good_baseplate],
            'bolts': good_bolts,
            'welds': []
        })

        # May still have minor issues, but no CRITICAL or MAJOR
        critical_major = [c for c in clashes if c.severity in [ClashSeverity.CRITICAL, ClashSeverity.MAJOR]]
        assert len(critical_major) == 0, f"Good model should have 0 critical/major clashes, got {len(critical_major)}"

# ============================================================================
# TEST: CLASH CORRECTION
# ============================================================================

class TestClashCorrection:
    """Test cases for ClashCorrector."""

    def test_correct_base_plate_elevation(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test correction of base plate wrong elevation."""
        detector = ClashDetector()
        clashes, _ = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate.copy()],
            'bolts': [b.copy() for b in flawed_bolts],
            'welds': []
        })

        corrector = ClashCorrector(detector)
        ifc_corrected, corrections = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [b for b in flawed_bolts],
            'welds': []
        })

        # Check plate Z was corrected
        corrected_plate = ifc_corrected['plates'][0]
        assert corrected_plate['position'][2] == 0, f"Plate Z should be 0, got {corrected_plate['position'][2]}"
        print(f"✓ Corrected base plate Z from 3000 to {corrected_plate['position'][2]}")

    def test_correct_bolt_negative_coords(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test correction of bolt negative coordinates."""
        detector = ClashDetector()
        detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        corrector = ClashCorrector(detector)
        ifc_corrected, corrections = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        # Check bolts were corrected
        corrected_bolts = ifc_corrected['bolts']
        for bolt in corrected_bolts:
            assert bolt['position'][0] >= 0, f"Bolt X should be positive, got {bolt['position'][0]}"
            assert bolt['position'][1] >= 0, f"Bolt Y should be positive, got {bolt['position'][1]}"
            print(f"✓ Corrected bolt {bolt['id']} coords to {bolt['position']}")

    def test_correct_undersized_plate(self, basic_members, basic_joints, flawed_baseplate):
        """Test correction of undersized plate."""
        detector = ClashDetector()
        detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [],
            'welds': []
        })

        corrector = ClashCorrector(detector)
        ifc_corrected, corrections = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': [],
            'welds': []
        })

        # Check plate dimensions were corrected
        corrected_plate = ifc_corrected['plates'][0]
        width = corrected_plate['outline']['width_mm']
        height = corrected_plate['outline']['height_mm']
        
        assert width >= 300, f"Plate width should be >= 300, got {width}"
        assert height >= 300, f"Plate height should be >= 300, got {height}"
        print(f"✓ Corrected plate dimensions to {width}×{height}mm")

    def test_corrections_count(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test that corrections are properly counted."""
        detector = ClashDetector()
        detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        corrector = ClashCorrector(detector)
        ifc_corrected, corrections = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        assert len(corrections) > 0, "Should have applied corrections"
        print(f"✓ Applied {len(corrections)} corrections:")
        for correction in corrections:
            print(f"  - {correction['action']}: {correction['element_id']}")

    def test_re_validation_after_correction(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test that re-validation finds fewer clashes after correction."""
        # Initial detection
        detector1 = ClashDetector()
        clashes1, summary1 = detector1.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        initial_count = summary1['total']

        # Correction
        corrector = ClashCorrector(detector1)
        ifc_corrected, _ = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })

        # Re-detection
        detector2 = ClashDetector()
        clashes2, summary2 = detector2.detect_all_clashes(ifc_corrected)

        final_count = summary2['total']

        assert final_count < initial_count, f"Should reduce clashes from {initial_count} to <{final_count}"
        print(f"✓ Reduced clashes from {initial_count} to {final_count}")

# ============================================================================
# TEST: CONNECTION CLASSIFICATION
# ============================================================================

class TestConnectionClassification:
    """Test cases for ConnectionClassifier."""

    def test_classify_base_connection(self, basic_members, basic_joints):
        """Test classification of base connection."""
        classifier = ConnectionClassifier()
        classifications = classifier.classify_all_connections(basic_members, basic_joints)

        # Should have at least one classification
        assert len(classifications) > 0, "Should have classifications"

        # Base joint should be classified as base_plate
        base_joints = [c for c in classifications if c.category == ConnectionCategory.BASE_PLATE]
        assert len(base_joints) > 0, "Should classify base joint as base_plate"

        classification = base_joints[0]
        assert classification.confidence_score > 70, "Base plate confidence should be > 70%"
        print(f"✓ Classified base connection with {classification.confidence_score:.1f}% confidence")

    def test_base_connection_parameters(self, basic_members, basic_joints):
        """Test base connection parameter estimates."""
        classifier = ConnectionClassifier()
        classifications = classifier.classify_all_connections(basic_members, basic_joints)

        base_joints = [c for c in classifications if c.category == ConnectionCategory.BASE_PLATE]
        assert len(base_joints) > 0

        classification = base_joints[0]

        # Check estimated parameters
        assert classification.estimated_plate_dimensions_mm[0] >= 300, "Base plate width should be >= 300mm"
        assert classification.estimated_plate_dimensions_mm[1] >= 300, "Base plate height should be >= 300mm"
        assert classification.estimated_bolt_diameter_mm > 15, "Bolt diameter should be > 15mm"
        assert classification.estimated_bolt_count >= 4, "Bolt count should be >= 4"
        print(f"✓ Base plate estimated params: {classification.estimated_plate_dimensions_mm[0]}mm, "
              f"{classification.estimated_bolt_count} bolts")

    def test_work_point_offset(self, basic_members, basic_joints):
        """Test work point offset calculation."""
        classifier = ConnectionClassifier()
        classifications = classifier.classify_all_connections(basic_members, basic_joints)

        for classification in classifications:
            if classification.category == ConnectionCategory.BASE_PLATE:
                # Base plate should have negative offset (toward bottom)
                assert classification.work_point_offset_mm < 0, "Base plate offset should be negative"
                print(f"✓ Base plate work point offset: {classification.work_point_offset_mm}mm")

            elif classification.category == ConnectionCategory.ROOF_PLATE:
                # Roof plate should have positive offset (toward top)
                assert classification.work_point_offset_mm > 0, "Roof plate offset should be positive"
                print(f"✓ Roof plate work point offset: {classification.work_point_offset_mm}mm")

# ============================================================================
# TEST: INTEGRATION
# ============================================================================

class TestIntegration:
    """Integration tests for full pipeline."""

    def test_full_pipeline_detect_and_correct(self, basic_members, basic_joints, flawed_baseplate, flawed_bolts):
        """Test full detect-correct-revalidate pipeline."""
        
        # Step 1: Classify connections
        classifier = ConnectionClassifier()
        classifications = classifier.classify_all_connections(basic_members, basic_joints)
        assert len(classifications) > 0, "Should classify connections"
        
        # Step 2: Detect clashes
        detector = ClashDetector()
        clashes, summary = detector.detect_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })
        initial_clashes = summary['total']
        assert initial_clashes > 0, "Should detect clashes"
        print(f"✓ Step 1: Detected {initial_clashes} clashes")
        
        # Step 3: Correct clashes
        corrector = ClashCorrector(detector)
        ifc_corrected, corrections = corrector.correct_all_clashes({
            'members': basic_members,
            'joints': basic_joints,
            'plates': [flawed_baseplate],
            'bolts': flawed_bolts,
            'welds': []
        })
        assert len(corrections) > 0, "Should apply corrections"
        print(f"✓ Step 2: Applied {len(corrections)} corrections")
        
        # Step 4: Re-validate
        detector_final = ClashDetector()
        clashes_final, summary_final = detector_final.detect_all_clashes(ifc_corrected)
        final_clashes = summary_final['total']
        
        assert final_clashes < initial_clashes, "Should reduce clashes"
        print(f"✓ Step 3: Re-validated - reduced clashes from {initial_clashes} to {final_clashes}")
        
        print(f"\n✓✓✓ FULL PIPELINE SUCCESSFUL ✓✓✓")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Run with: python tests/test_clash_detection.py
    pytest.main([__file__, '-v', '--tb=short'])
