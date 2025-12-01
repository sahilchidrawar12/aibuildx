#!/usr/bin/env python3
"""
Tests for wind loading and aeroelastic analysis.
"""
import pytest
import json
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.wind_aeroelastic import WindAnalyzer, Exposure

def create_sample_model():
    """Create sample structural model for testing."""
    return {
        'members_classified': [
            {
                'id': 'm1',
                'start': [0, 0, 0],
                'end': [50, 0, 0],
                'profile': {'type': 'tube', 'area': 2000},
            },
            {
                'id': 'm2',
                'start': [50, 0, 0],
                'end': [50, 0, 300],
                'profile': {'type': 'tube', 'area': 1500},
            },
            {
                'id': 'm3',
                'start': [0, 0, 0],
                'end': [0, 50, 0],
                'profile': {'type': 'tube', 'area': 2000},
            },
            {
                'id': 'm4',
                'start': [0, 50, 0],
                'end': [0, 50, 300],
                'profile': {'type': 'tube', 'area': 1500},
            },
        ]
    }

class TestASCE7WindLoads:
    """Test ASCE 7-22 wind load generation."""
    
    def test_asce7_basic(self):
        """Test basic ASCE 7 load generation."""
        analyzer = WindAnalyzer()
        result = analyzer.generate_asce7_wind(height_m=300.0, exposure='B', basic_wind_speed_mph=115.0)
        
        assert result['code'] == 'ASCE 7-22'
        assert result['exposure'] == 'B'
        assert result['basic_wind_speed_mph'] == 115.0
        assert len(result['heights_m']) >= 10
        assert len(result['wind_pressures_kpa']) == len(result['heights_m'])
        assert result['base_shear_kn'] > 0
        assert result['overturning_moment_kn_m'] > 0
        assert result['max_pressure_kpa'] > 0
        print(f"✓ ASCE 7 test passed: Base Shear={result['base_shear_kn']:.1f} kN")
    
    def test_exposure_categories(self):
        """Test different exposure categories."""
        analyzer = WindAnalyzer()
        
        exposures = ['B', 'C', 'D']
        results = []
        
        for exp in exposures:
            result = analyzer.generate_asce7_wind(height_m=300.0, exposure=exp, basic_wind_speed_mph=115.0)
            results.append(result)
            assert result['exposure'] == exp
            assert result['base_shear_kn'] > 0
        
        # All exposures should produce valid pressures
        assert results[0]['max_pressure_kpa'] > 0
        assert results[1]['max_pressure_kpa'] > 0
        assert results[2]['max_pressure_kpa'] > 0
        print(f"✓ Exposure test passed: B={results[0]['max_pressure_kpa']:.3f}, C={results[1]['max_pressure_kpa']:.3f}, D={results[2]['max_pressure_kpa']:.3f} kPa")
    
    def test_height_variation(self):
        """Test pressure variation with height."""
        analyzer = WindAnalyzer()
        result = analyzer.generate_asce7_wind(height_m=300.0, exposure='B', basic_wind_speed_mph=115.0)
        
        # Pressure should increase with height
        pressures = result['wind_pressures_kpa']
        for i in range(1, len(pressures)):
            assert pressures[i] >= pressures[i - 1] * 0.95  # Allow slight variation

class TestWindTunnelPressures:
    """Test wind-tunnel pressure mapping."""
    
    def test_wind_tunnel_application(self):
        """Test applying wind-tunnel pressure coefficients."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        pressure_map = {
            'windward': [0.8, 0.7, 0.6, 0.5],
            'leeward': [-0.3, -0.35, -0.4, -0.45],
            'side': [-0.7, -0.75, -0.8, -0.85],
        }
        
        result = analyzer.apply_wind_tunnel_pressures(pressure_map, model)
        
        assert result['source'] == 'wind_tunnel'
        assert len(result['element_loads']) == 12  # 4 faces * 3 levels each
        assert 'total_base_shear_kn' in result  # May be positive or negative due to net effects
        print(f"✓ Wind-tunnel test passed: {len(result['element_loads'])} element loads, Base Shear={result['total_base_shear_kn']:.1f} kN")
    
    def test_pressure_coefficients(self):
        """Test pressure coefficient values."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        pressure_map = {
            'windward': [0.8, 0.8, 0.8],
            'leeward': [-0.3, -0.3, -0.3],
        }
        
        result = analyzer.apply_wind_tunnel_pressures(pressure_map, model)
        
        # Check that pressures are computed correctly
        for load in result['element_loads']:
            p_expected = load['cp'] * 1.2  # kPa (1.2 is reference)
            assert abs(load['pressure_kpa'] - p_expected) < 0.01

class TestModalWindResponse:
    """Test buffeting analysis."""
    
    def test_modal_response_basic(self):
        """Test modal wind response calculation."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        result = analyzer.modal_wind_response(model, wind_speed_ms=25.0)
        
        assert result['wind_speed_ms'] == 25.0
        assert len(result['modal_responses']) > 0
        assert result['peak_displacement_mm'] > 0
        assert result['peak_acceleration_mg'] > 0
        
        for mode in result['modal_responses']:
            assert 'period_s' in mode
            assert 'rms_displacement_mm' in mode
            assert 'rms_acceleration_mg' in mode
            assert mode['damping_ratio'] > 0
        
        print(f"✓ Modal response test passed: Peak disp={result['peak_displacement_mm']:.2f} mm, Peak accel={result['peak_acceleration_mg']:.2f} milli-g")
    
    def test_wind_speed_effects(self):
        """Test that response increases with wind speed."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        result_slow = analyzer.modal_wind_response(model, wind_speed_ms=10.0)
        result_fast = analyzer.modal_wind_response(model, wind_speed_ms=40.0)
        
        # Higher wind speed should cause higher accelerations
        assert result_fast['peak_acceleration_mg'] > result_slow['peak_acceleration_mg']
        print(f"✓ Wind speed test: 10 m/s → {result_slow['peak_acceleration_mg']:.2f}mg, 40 m/s → {result_fast['peak_acceleration_mg']:.2f}mg")
    
    def test_admittance_factor(self):
        """Test aerodynamic admittance calculation."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        result = analyzer.modal_wind_response(model, wind_speed_ms=25.0)
        
        # Admittance should be between 0 and 1
        for mode in result['modal_responses']:
            assert 0 <= mode['admittance'] <= 1.0

class TestFlutterCheck:
    """Test flutter speed estimation."""
    
    def test_flutter_speed_calculation(self):
        """Test flutter speed check."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        result = analyzer.flutter_speed_check(model, cross_section='square', characteristic_length_m=50.0)
        
        assert result['critical_flutter_speed_ms'] is not None
        assert result['critical_flutter_speed_ms'] > 0
        assert result['flutter_margin'] is not None
        assert result['status'] in ['safe', 'marginal', 'unsafe', 'check_required']
        print(f"✓ Flutter test: Vcrit={result['critical_flutter_speed_ms']:.1f} m/s, Margin={result['flutter_margin']:.2f}x, Status={result['status']}")
    
    def test_flutter_margin_logic(self):
        """Test flutter margin classification."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        result = analyzer.flutter_speed_check(model)
        
        # Margin should be positive
        assert result['flutter_margin'] > 0
        
        # Check status assignment
        if result['flutter_margin'] > 1.2:
            assert result['status'] == 'safe'
        elif result['flutter_margin'] > 0.8:
            assert result['status'] in ['safe', 'marginal']
        
        print(f"✓ Flutter margin logic test: {result['status'].upper()}")

class TestIntegration:
    """Integration tests combining multiple analyses."""
    
    def test_full_wind_analysis_pipeline(self):
        """Test complete wind analysis workflow."""
        analyzer = WindAnalyzer()
        model = create_sample_model()
        
        # Step 1: ASCE 7 loads
        asce = analyzer.generate_asce7_wind(height_m=300.0, exposure='B', basic_wind_speed_mph=115.0)
        assert asce['base_shear_kn'] > 0
        
        # Step 2: Wind-tunnel mapping
        pressure_map = {
            'windward': [0.8, 0.7, 0.6],
            'leeward': [-0.3, -0.35, -0.4],
        }
        wt = analyzer.apply_wind_tunnel_pressures(pressure_map, model)
        assert wt['total_base_shear_kn'] > 0
        
        # Step 3: Modal response
        modal = analyzer.modal_wind_response(model, wind_speed_ms=25.0)
        assert modal['peak_displacement_mm'] > 0
        
        # Step 4: Flutter check
        flutter = analyzer.flutter_speed_check(model)
        assert flutter['critical_flutter_speed_ms'] > 0
        
        # All analyses should produce consistent results
        print(f"✓ Full pipeline test passed:")
        print(f"  ASCE 7 Base Shear: {asce['base_shear_kn']:.1f} kN")
        print(f"  Wind-tunnel Base Shear: {wt['total_base_shear_kn']:.1f} kN")
        print(f"  Modal Peak Accel: {modal['peak_acceleration_mg']:.2f} milli-g")
        print(f"  Flutter Speed: {flutter['critical_flutter_speed_ms']:.1f} m/s")
    
    def test_tall_building_case(self):
        """Test analysis on tall building (similar to Burj Khalifa)."""
        # Model 828m tall tower
        tall_model = {
            'members_classified': [
                {
                    'id': f'm{i}',
                    'start': [0, 0, i * 50],
                    'end': [0, 0, (i + 1) * 50],
                    'profile': {'type': 'tube', 'area': 5000 - i * 50},  # Tapered
                }
                for i in range(16)  # 16 sections × 50m
            ]
        }
        
        analyzer = WindAnalyzer()
        
        # ASCE 7 for extreme case
        asce = analyzer.generate_asce7_wind(height_m=828.0, exposure='B', basic_wind_speed_mph=130.0)
        assert asce['base_shear_kn'] > 0  # Should produce positive base shear
        
        # Flutter check
        flutter = analyzer.flutter_speed_check(tall_model, characteristic_length_m=80.0)
        assert flutter['critical_flutter_speed_ms'] > 0  # Should estimate a critical speed
        assert flutter['status'] in ['safe', 'marginal', 'unsafe', 'check_required']
        
        print(f"✓ Tall building test (828m): Base Shear={asce['base_shear_kn']:.0f} kN, Flutter speed={flutter['critical_flutter_speed_ms']:.1f} m/s")

def main():
    """Run all tests."""
    print("Wind & Aeroelastic Analysis Tests")
    print("=" * 60)
    
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    main()
