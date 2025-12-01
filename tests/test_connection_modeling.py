#!/usr/bin/env python3
"""Tests for connection modeling."""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.connection_modeling import ConnectionAnalyzer

class TestBoltCapacity:
    """Test bolt capacity calculations."""
    
    def test_bolt_capacity_basic(self):
        """Test basic bolt capacity."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=4)
        
        assert result['design_capacity']['tension_kn'] > 0
        assert result['design_capacity']['shear_single_kn'] > 0
        assert result['design_capacity']['bearing_kn'] > 0
        print(f"✓ Bolt capacity: T={result['design_capacity']['tension_kn']:.1f}, S={result['design_capacity']['shear_single_kn']:.1f}, B={result['design_capacity']['bearing_kn']:.1f} kN")
    
    def test_bolt_grade_variation(self):
        """Test different bolt grades."""
        analyzer = ConnectionAnalyzer()
        
        grades = ['A307', 'A325', 'A490']
        capacities = {}
        
        for grade in grades:
            result = analyzer.compute_bolt_capacity(grade=grade, diameter_mm=25.0, count=1)
            capacities[grade] = result['design_capacity']['tension_kn']
        
        # A490 > A325 > A307
        assert capacities['A490'] > capacities['A325'] > capacities['A307']
        print(f"✓ Grade comparison: A307={capacities['A307']:.1f}, A325={capacities['A325']:.1f}, A490={capacities['A490']:.1f} kN")
    
    def test_bolt_count_scaling(self):
        """Test that capacity scales with bolt count."""
        analyzer = ConnectionAnalyzer()
        
        result_1 = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=1)
        result_4 = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=4)
        
        # 4 bolts should have ~4x capacity
        ratio = result_4['design_capacity']['tension_kn'] / result_1['design_capacity']['tension_kn']
        assert 3.5 < ratio < 4.5  # Allow some variation
        print(f"✓ Bolt count scaling: 1 bolt={result_1['design_capacity']['tension_kn']:.1f}, 4 bolts={result_4['design_capacity']['tension_kn']:.1f} kN (ratio={ratio:.2f})")

class TestSlipAnalysis:
    """Test slip resistance analysis."""
    
    def test_slip_basic(self):
        """Test basic slip analysis."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.analyze_slip(normal_force_kn=0, friction_coefficient=0.33,
                                      pretension_percent=70.0, diameter_mm=25.0)
        
        assert result['slip_capacity']['capacity_from_pretension_kn'] > 0
        assert result['bolt_pretension']['pretension_force_kn'] > 0
        print(f"✓ Slip capacity: {result['slip_capacity']['capacity_from_pretension_kn']:.1f} kN")
    
    def test_friction_effect(self):
        """Test that friction increases slip capacity."""
        analyzer = ConnectionAnalyzer()
        
        result_low = analyzer.analyze_slip(normal_force_kn=0, friction_coefficient=0.30, diameter_mm=25.0)
        result_high = analyzer.analyze_slip(normal_force_kn=0, friction_coefficient=0.40, diameter_mm=25.0)
        
        # Higher friction = higher slip capacity
        assert result_high['slip_capacity']['capacity_from_pretension_kn'] > result_low['slip_capacity']['capacity_from_pretension_kn']

class TestWeldCapacity:
    """Test weld capacity calculations."""
    
    def test_fillet_weld(self):
        """Test fillet weld capacity."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.compute_weld_capacity(weld_type='fillet', weld_size_mm=8.0,
                                               weld_length_mm=200.0)
        
        assert result['capacity']['capacity_kn'] > 0
        assert result['capacity']['failure_mode'] == 'Weld metal yielding'
        print(f"✓ Fillet weld: {result['capacity']['capacity_kn']:.1f} kN")
    
    def test_butt_weld(self):
        """Test butt weld capacity."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.compute_weld_capacity(weld_type='butt_complete', weld_size_mm=10.0,
                                               weld_length_mm=300.0)
        
        assert result['capacity']['capacity_kn'] > 0
        assert result['capacity']['failure_mode'] == 'Base metal yielding'
    
    def test_weld_process_effect(self):
        """Test that weld process affects capacity."""
        analyzer = ConnectionAnalyzer()
        
        result_smaw = analyzer.compute_weld_capacity(weld_type='fillet', weld_size_mm=8.0,
                                                     weld_length_mm=200.0, weld_process='SMAW')
        result_saw = analyzer.compute_weld_capacity(weld_type='fillet', weld_size_mm=8.0,
                                                    weld_length_mm=200.0, weld_process='SAW')
        
        # SAW typically stronger
        assert result_saw['capacity']['capacity_kn'] >= result_smaw['capacity']['capacity_kn']

class TestPlateYielding:
    """Test plate yielding and fracture."""
    
    def test_plate_capacity_basic(self):
        """Test basic plate capacity."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=15.0)
        
        assert result['design_capacity']['capacity_kn'] > 0
        print(f"✓ Plate capacity: {result['design_capacity']['capacity_kn']:.1f} kN")
    
    def test_hole_reduction(self):
        """Test that holes reduce net section."""
        analyzer = ConnectionAnalyzer()
        
        result_no_holes = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=15.0, holes_count=0)
        result_with_holes = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=15.0, holes_count=2)
        
        # With holes should have lower net section area
        assert result_with_holes['plate_properties']['area_net_mm2'] < result_no_holes['plate_properties']['area_gross_mm2']
    
    def test_thickness_scaling(self):
        """Test that capacity scales with thickness."""
        analyzer = ConnectionAnalyzer()
        
        result_10 = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=10.0)
        result_20 = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=20.0)
        
        # 20mm should have ~2x capacity of 10mm
        ratio = result_20['design_capacity']['capacity_kn'] / result_10['design_capacity']['capacity_kn']
        assert 1.8 < ratio < 2.2
        print(f"✓ Thickness scaling: 10mm={result_10['design_capacity']['capacity_kn']:.1f}, 20mm={result_20['design_capacity']['capacity_kn']:.1f} kN")

class TestFabricationTolerances:
    """Test fabrication tolerance definitions."""
    
    def test_tolerances_basic(self):
        """Test basic tolerance generation."""
        analyzer = ConnectionAnalyzer()
        result = analyzer.fabrication_tolerances(member_depth_mm=800.0, bolt_pattern_pitch_mm=100.0)
        
        assert result['member_tolerances']['length_tolerance_mm'] > 0
        assert result['bolt_hole_tolerances']['position_tolerance_mm'] > 0
        assert result['weld_tolerances']['fillet_size_tolerance_mm'] > 0
        print(f"✓ Tolerances: Length ±{result['member_tolerances']['length_tolerance_mm']:.1f}, Hole ±{result['bolt_hole_tolerances']['position_tolerance_mm']:.1f} mm")
    
    def test_tolerance_size_effect(self):
        """Test that larger members have larger tolerances."""
        analyzer = ConnectionAnalyzer()
        
        result_small = analyzer.fabrication_tolerances(member_depth_mm=500.0, bolt_pattern_pitch_mm=100.0)
        result_large = analyzer.fabrication_tolerances(member_depth_mm=2000.0, bolt_pattern_pitch_mm=100.0)
        
        # Larger member should have larger tolerance (or at least equal)
        assert result_large['member_tolerances']['length_tolerance_mm'] >= result_small['member_tolerances']['length_tolerance_mm']

class TestIntegration:
    """Integration tests."""
    
    def test_connection_design_flow(self):
        """Test complete connection design workflow."""
        analyzer = ConnectionAnalyzer()
        
        # Design bolted connection for 100 kN shear load
        load = 100.0  # kN
        
        # Try different bolt counts
        for count in [2, 4, 6]:
            bolt_cap = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=count)
            shear_cap = bolt_cap['design_capacity']['shear_single_kn']
            
            if shear_cap >= load:
                print(f"✓ 100 kN shear: {count} bolts sufficient ({shear_cap:.1f} kN available)")
                break
    
    def test_welded_connection_design(self):
        """Test welded connection design."""
        analyzer = ConnectionAnalyzer()
        
        # Design fillet weld for 50 kN load
        load = 50.0  # kN
        
        for length in [100, 150, 200]:
            weld = analyzer.compute_weld_capacity(weld_type='fillet', weld_size_mm=8.0,
                                                  weld_length_mm=length)
            if weld['capacity']['capacity_kn'] >= load:
                print(f"✓ 50 kN load: {length}mm fillet weld sufficient ({weld['capacity']['capacity_kn']:.1f} kN)")
                break
    
    def test_connection_interaction(self):
        """Test interaction between bolt and plate."""
        analyzer = ConnectionAnalyzer()
        
        # 4 A325 bolts, 25mm
        bolts = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=4)
        
        # Connected to 200x15 plate
        plate = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=15.0, holes_count=4)
        
        # Should not exceed plate capacity
        assert plate['design_capacity']['capacity_kn'] > 0
        print(f"✓ Connection: Bolts={bolts['design_capacity']['tension_kn']:.1f} kN, Plate={plate['design_capacity']['capacity_kn']:.1f} kN")

def main():
    """Run all tests."""
    print("Connection Modeling Tests")
    print("=" * 60)
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    main()
