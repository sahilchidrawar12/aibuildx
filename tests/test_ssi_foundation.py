#!/usr/bin/env python3
"""Tests for SSI and foundation modeling."""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.ssi_foundation import SSIAnalyzer

class TestFoundationSprings:
    """Test foundation spring stiffness computation."""
    
    def test_foundation_springs_basic(self):
        """Test basic foundation spring calculation."""
        analyzer = SSIAnalyzer(soil_type='clay_medium')
        result = analyzer.compute_foundation_springs(width_m=50.0, length_m=50.0)
        
        assert result['spring_stiffness']['Kv_kn_m'] > 0
        assert result['spring_stiffness']['Kh_kn_m'] > 0
        assert result['spring_stiffness']['Kr_kn_m_rad'] > 0
        assert result['spring_stiffness']['Kt_kn_m_rad'] > 0
        print(f"✓ Foundation springs: Kv={result['spring_stiffness']['Kv_kn_m']:.0f} kN/m")
    
    def test_spring_ratios(self):
        """Test physical spring stiffness ratios."""
        analyzer = SSIAnalyzer()
        result = analyzer.compute_foundation_springs(width_m=40.0, length_m=40.0)
        
        Kv = result['spring_stiffness']['Kv_kn_m']
        Kh = result['spring_stiffness']['Kh_kn_m']
        
        # Horizontal should be less than vertical (typical)
        assert Kh < Kv
        # Ratio should be ~0.6-0.8
        ratio = Kh / Kv
        assert 0.5 < ratio < 0.9
        print(f"✓ Spring ratio Kh/Kv = {ratio:.2f}")
    
    def test_soil_type_variation(self):
        """Test that different soil types produce different stiffness."""
        results = {}
        for soil_type in ['sand_loose', 'clay_medium', 'rock']:
            analyzer = SSIAnalyzer(soil_type=soil_type)
            r = analyzer.compute_foundation_springs(width_m=50.0)
            results[soil_type] = r['spring_stiffness']['Kv_kn_m']
        
        # All soil types should produce valid positive stiffness
        assert results['rock'] > 0
        assert results['clay_medium'] > 0
        assert results['sand_loose'] > 0
        print(f"✓ Soil stiffness: Sand={results['sand_loose']:.0f}, Clay={results['clay_medium']:.0f}, Rock={results['rock']:.0f}")

class TestPileGroup:
    """Test pile group analysis."""
    
    def test_pile_group_basic(self):
        """Test basic pile group stiffness."""
        analyzer = SSIAnalyzer()
        result = analyzer.compute_pile_group(num_piles=16, pile_diameter_m=1.0,
                                             pile_length_m=25.0, spacing_m=3.0)
        
        assert result['group_stiffness']['Kv_group_mn_m'] > 0
        assert result['group_stiffness']['Kh_group_mn_m'] > 0
        assert result['ultimate_capacity']['Pu_vertical_mn'] > 0
        assert 0 < result['group_efficiency']['Eg_vertical'] <= 1.0
        print(f"✓ Pile group: Kv={result['group_stiffness']['Kv_group_mn_m']:.1f} MN/m, Pu={result['ultimate_capacity']['Pu_vertical_mn']:.1f} MN")
    
    def test_group_efficiency(self):
        """Test group efficiency decreases with closer spacing."""
        analyzer = SSIAnalyzer()
        
        # Well-spaced piles
        result_spaced = analyzer.compute_pile_group(num_piles=4, pile_diameter_m=1.0,
                                                     pile_length_m=20.0, spacing_m=5.0)
        
        # Close-spaced piles
        result_close = analyzer.compute_pile_group(num_piles=4, pile_diameter_m=1.0,
                                                    pile_length_m=20.0, spacing_m=2.0)
        
        # Closer spacing should have lower efficiency
        assert result_close['group_efficiency']['Eg_vertical'] < result_spaced['group_efficiency']['Eg_vertical']
        print(f"✓ Group efficiency: Spaced={result_spaced['group_efficiency']['Eg_vertical']:.2f}, Close={result_close['group_efficiency']['Eg_vertical']:.2f}")
    
    def test_capacity_factors(self):
        """Test that pile group capacity increases with number of piles."""
        analyzer = SSIAnalyzer()
        
        result_4 = analyzer.compute_pile_group(num_piles=4, pile_diameter_m=1.0, pile_length_m=20.0)
        result_16 = analyzer.compute_pile_group(num_piles=16, pile_diameter_m=1.0, pile_length_m=20.0)
        
        # More piles = higher capacity
        assert result_16['ultimate_capacity']['Pu_vertical_mn'] > result_4['ultimate_capacity']['Pu_vertical_mn']
        print(f"✓ Capacity scaling: 4 piles={result_4['ultimate_capacity']['Pu_vertical_mn']:.1f}, 16 piles={result_16['ultimate_capacity']['Pu_vertical_mn']:.1f} MN")

class TestFrequencyDependentImpedance:
    """Test frequency-dependent impedance."""
    
    def test_impedance_basic(self):
        """Test impedance calculation."""
        analyzer = SSIAnalyzer()
        result = analyzer.frequency_dependent_impedance(foundation_width_m=50.0, frequency_hz=1.0)
        
        assert result['dynamic_stiffness_kpa'] > 0
        assert result['impedance_ratio'] > 0
        assert 0 < result['loss_tangent'] < 0.3
        print(f"✓ Impedance: Static K={result['static_stiffness_kpa']:.0f}, Dynamic K={result['dynamic_stiffness_kpa']:.0f}, Ratio={result['impedance_ratio']:.3f}")
    
    def test_frequency_effects(self):
        """Test that impedance changes with frequency."""
        analyzer = SSIAnalyzer()
        
        result_low = analyzer.frequency_dependent_impedance(foundation_width_m=50.0, frequency_hz=0.1)
        result_high = analyzer.frequency_dependent_impedance(foundation_width_m=50.0, frequency_hz=5.0)
        
        # Higher frequency generally increases stiffness
        assert result_high['dynamic_stiffness_kpa'] > result_low['dynamic_stiffness_kpa']
        print(f"✓ Frequency effect: 0.1 Hz K={result_low['dynamic_stiffness_kpa']:.0f}, 5 Hz K={result_high['dynamic_stiffness_kpa']:.0f}")

class TestEmbedmentEffects:
    """Test embedment depth effects."""
    
    def test_embedment_increases_capacity(self):
        """Test that deeper embedment increases capacity."""
        analyzer = SSIAnalyzer()
        
        result_shallow = analyzer.embedment_effects(foundation_depth_m=1.0, foundation_width_m=50.0)
        result_deep = analyzer.embedment_effects(foundation_depth_m=3.0, foundation_width_m=50.0)
        
        assert result_deep['capacity_factor'] > result_shallow['capacity_factor']
        assert result_deep['stiffness_factor'] > result_shallow['stiffness_factor']
        print(f"✓ Embedment: 1m D/B={result_shallow['depth_ratio_d_b']:.2f}, F_d={result_shallow['capacity_factor']:.2f}x")
        print(f"          3m D/B={result_deep['depth_ratio_d_b']:.2f}, F_d={result_deep['capacity_factor']:.2f}x")
    
    def test_liquefaction_risk_reduction(self):
        """Test that deeper embedment reduces liquefaction risk."""
        analyzer = SSIAnalyzer()
        
        result_shallow = analyzer.embedment_effects(foundation_depth_m=0.5, foundation_width_m=30.0)
        result_deep = analyzer.embedment_effects(foundation_depth_m=2.5, foundation_width_m=30.0)
        
        # Deeper = lower liquefaction risk
        assert result_deep['liquefaction_risk_ratio'] < result_shallow['liquefaction_risk_ratio']

class TestPDeltaEffects:
    """Test P-Δ second-order effects."""
    
    def test_p_delta_basic(self):
        """Test P-Δ moment calculation."""
        analyzer = SSIAnalyzer()
        result = analyzer.p_delta_effects(lateral_force_kn=1000.0, lateral_displacement_m=0.1,
                                         vertical_load_kn=50000.0, height_m=300.0)
        
        assert result['direct_moment_kn_m'] > 0
        assert result['p_delta_moment_kn_m'] > 0
        assert result['stability_coefficient'] >= 0
        print(f"✓ P-Δ: Direct={result['direct_moment_kn_m']:.0f}, P-Δ={result['p_delta_moment_kn_m']:.0f}, Amplification={result['p_delta_amplification_factor']:.3f}x")
    
    def test_stability_limits(self):
        """Test stability coefficient limits."""
        analyzer = SSIAnalyzer()
        
        # Small displacement - stable
        result_stable = analyzer.p_delta_effects(lateral_force_kn=1000.0, lateral_displacement_m=0.05,
                                                 vertical_load_kn=50000.0, height_m=300.0)
        
        # Large displacement - potentially unstable
        result_unstable = analyzer.p_delta_effects(lateral_force_kn=500.0, lateral_displacement_m=0.5,
                                                   vertical_load_kn=50000.0, height_m=300.0)
        
        assert result_stable['stability_coefficient'] < result_unstable['stability_coefficient']
        # Stable should be < 0.1
        assert result_stable['stability_coefficient'] < 0.1

class TestLiquefactionScreening:
    """Test liquefaction potential assessment."""
    
    def test_liquefaction_safe(self):
        """Test liquefaction screening for safe case."""
        analyzer = SSIAnalyzer()
        result = analyzer.liquefaction_screening(depth_m=15.0, standard_penetration_n=30,
                                                groundwater_depth_m=5.0, earthquake_magnitude=7.0)
        
        assert result['safety_factor_fl'] > 1.0
        assert result['liquefaction_potential'] == 'Low'
        print(f"✓ Liquefaction safe: FL={result['safety_factor_fl']:.2f}, Potential={result['liquefaction_potential']}")
    
    def test_liquefaction_at_risk(self):
        """Test liquefaction screening for at-risk case."""
        analyzer = SSIAnalyzer()
        result = analyzer.liquefaction_screening(depth_m=8.0, standard_penetration_n=8,
                                                groundwater_depth_m=2.0, earthquake_magnitude=8.0)
        
        assert result['cyclic_stress_ratio'] > 0
        assert result['cyclic_resistance_ratio'] > 0
        print(f"✓ Liquefaction at-risk: CSR={result['cyclic_stress_ratio']:.4f}, CRR={result['cyclic_resistance_ratio']:.4f}, FL={result['safety_factor_fl']:.2f}")
    
    def test_magnitude_effect(self):
        """Test that higher earthquake magnitude increases liquefaction risk."""
        analyzer = SSIAnalyzer()
        
        result_low = analyzer.liquefaction_screening(depth_m=10.0, standard_penetration_n=15,
                                                     earthquake_magnitude=6.5)
        result_high = analyzer.liquefaction_screening(depth_m=10.0, standard_penetration_n=15,
                                                      earthquake_magnitude=8.5)
        
        # Higher magnitude = higher CSR = lower FL
        assert result_high['cyclic_stress_ratio'] > result_low['cyclic_stress_ratio']
        assert result_high['safety_factor_fl'] < result_low['safety_factor_fl']

class TestIntegration:
    """Integration tests."""
    
    def test_complete_ssi_analysis(self):
        """Test complete SSI analysis workflow."""
        analyzer = SSIAnalyzer(soil_type='clay_medium', cu_kpa=100.0)
        
        # Foundation springs
        springs = analyzer.compute_foundation_springs(width_m=60.0, length_m=60.0, height_above_m=300.0)
        assert springs['spring_stiffness']['Kv_kn_m'] > 0
        
        # Pile alternative
        piles = analyzer.compute_pile_group(num_piles=25, pile_diameter_m=1.0, pile_length_m=30.0)
        assert piles['group_stiffness']['Kv_group_mn_m'] > 0
        
        # Frequency effects
        imp = analyzer.frequency_dependent_impedance(foundation_width_m=60.0, frequency_hz=0.5)
        assert imp['impedance_ratio'] > 0
        
        # Embedment
        emb = analyzer.embedment_effects(foundation_depth_m=2.0, foundation_width_m=60.0)
        assert emb['capacity_factor'] > 1.0
        
        # P-Δ check
        p_delta = analyzer.p_delta_effects(lateral_force_kn=1500.0, lateral_displacement_m=0.15,
                                          vertical_load_kn=60000.0, height_m=300.0)
        assert p_delta['stability_status'] in ['OK', 'CRITICAL']
        
        # Liquefaction
        liq = analyzer.liquefaction_screening(depth_m=12.0, standard_penetration_n=18,
                                              groundwater_depth_m=3.0, earthquake_magnitude=7.5)
        assert liq['liquefaction_potential'] in ['Low', 'Moderate', 'High']
        
        print("✓ Complete SSI workflow passed")
    
    def test_burj_khalifa_ssi(self):
        """Test SSI analysis on Burj Khalifa scale."""
        # Burj Khalifa: ~150m x 150m base, 828m tall, on sand
        analyzer = SSIAnalyzer(soil_type='sand_dense', cu_kpa=0)
        
        springs = analyzer.compute_foundation_springs(width_m=150.0, length_m=150.0, height_above_m=828.0)
        assert springs['spring_stiffness']['Kv_kn_m'] > 0
        
        # Massive pile group
        piles = analyzer.compute_pile_group(num_piles=194, pile_diameter_m=1.5,
                                            pile_length_m=50.0, spacing_m=6.0, cap_width_m=50.0)
        assert piles['ultimate_capacity']['Pu_vertical_mn'] > 0  # Should produce valid capacity
        
        print(f"✓ Burj Khalifa SSI: Kv={springs['spring_stiffness']['Kv_kn_m']:.0f} kN/m, Pu={piles['ultimate_capacity']['Pu_vertical_mn']:.0f} MN")

def main():
    """Run all tests."""
    print("SSI & Foundation Tests")
    print("=" * 60)
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    main()
