#!/usr/bin/env python3
"""Tests for validation suite."""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.validation_suite import AccuracyValidator

class TestGeometryValidation:
    """Test geometry validation."""
    
    def test_node_geometry_perfect(self):
        """Test perfect match."""
        validator = AccuracyValidator()
        nodes_comp = [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
        nodes_ref = [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
        result = validator.validate_node_geometry(nodes_comp, nodes_ref)
        assert result.passes
        assert result.mean_absolute_error == 0.0
    
    def test_node_geometry_within_tolerance(self):
        """Test within tolerance."""
        validator = AccuracyValidator()
        nodes_comp = [(0, 0, 0), (10.003, 0.002, 0.001)]
        nodes_ref = [(0, 0, 0), (10, 0, 0)]
        result = validator.validate_node_geometry(nodes_comp, nodes_ref, tolerance_mm=5.0)
        assert result.passes

class TestModalValidation:
    """Test modal analysis validation."""
    
    def test_frequency_validation_good(self):
        """Test good frequency match."""
        validator = AccuracyValidator()
        computed = [0.50, 0.25, 0.15]
        reference = [0.48, 0.24, 0.14]
        result = validator.validate_modal_frequencies(computed, reference, tolerance_percent=10.0)
        assert result.passes
        print(f"✓ Frequency: {result.notes}")
    
    def test_mac_validation(self):
        """Test MAC matrix."""
        validator = AccuracyValidator()
        mode1_comp = [1.0, 0.5, 0.2, 0.1]
        mode1_ref = [1.0, 0.48, 0.19, 0.11]
        result = validator.validate_mac_matrix([mode1_comp], [mode1_ref], tolerance=0.85)
        assert result['passes']
        assert result['diagonal_macs'][0] > 0.85

class TestStaticValidation:
    """Test static analysis validation."""
    
    def test_displacement_validation(self):
        """Test displacement validation."""
        validator = AccuracyValidator()
        computed = [10.2, 5.1, 3.0, 1.5]
        reference = [10.0, 5.0, 3.1, 1.6]
        result = validator.validate_static_displacements(computed, reference, tolerance_percent=10.0)
        assert result.passes
    
    def test_force_validation(self):
        """Test reaction force validation."""
        validator = AccuracyValidator()
        computed = [100.5, 99.8, 50.2]
        reference = [100.0, 100.0, 50.0]
        result = validator.validate_reaction_forces(computed, reference, tolerance_percent=15.0)
        assert result.passes

class TestAcceptanceChecklist:
    """Test acceptance criteria."""
    
    def test_checklist_structure(self):
        """Test checklist has expected structure."""
        validator = AccuracyValidator()
        checklist = validator.acceptance_checklist()
        
        expected_keys = ['geometry', 'modal', 'static', 'dynamic', 'connections']
        for key in expected_keys:
            assert key in checklist

def main():
    """Run tests."""
    print("Validation Suite Tests")
    print("=" * 60)
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    main()
