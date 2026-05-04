#!/usr/bin/env python3
"""
Phase 3 Profile Optimization Test Script
Tests the complete profile optimization system for Bird's Nest stadium
"""

from src.pipeline.profile_optimizer import ProfileOptimizer, optimize_birds_nest_stadium, generate_optimization_report

def test_phase3_optimization():
    """Test Phase 3 profile optimization system"""
    print('=== PHASE 3 PROFILE OPTIMIZATION TEST ===')

    # Initialize optimizer
    optimizer = ProfileOptimizer()

    # Test I-beam optimization
    beam_loads = {'axial_kn': 500, 'moment_knm': 200, 'shear_kn': 150}
    beam_result = optimizer.optimize_i_beam(beam_loads, 8.0)
    print(f'Optimized I-beam: {beam_result.get("name", "None")}')
    print(f'Weight: {beam_result.get("properties", {}).get("weight_kg_per_m", 0):.1f} kg/m')

    # Test HSS optimization
    brace_loads = {'axial_kn': 800, 'shear_kn': 100}
    hss_result = optimizer.optimize_hss(brace_loads, 6.0, shape='rectangular')
    print(f'Optimized HSS: {hss_result.get("name", "None")}')
    print(f'Weight: {hss_result.get("properties", {}).get("weight_kg_per_m", 0):.1f} kg/m')

    # Test Bird's Nest optimization
    print('\n=== BIRD\'S NEST STADIUM OPTIMIZATION ===')
    birds_nest_system = optimize_birds_nest_stadium()
    report = generate_optimization_report(birds_nest_system)
    print(report[:1500] + '...\n[Report truncated for display]')

    print('\nPhase 3 optimization test completed successfully!')

    # Save detailed report
    with open('phase3_optimization_report.txt', 'w') as f:
        f.write(report)

    print('Detailed report saved to phase3_optimization_report.txt')

if __name__ == '__main__':
    test_phase3_optimization()