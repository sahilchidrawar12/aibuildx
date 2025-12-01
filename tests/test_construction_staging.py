#!/usr/bin/env python3
"""Tests for construction staging."""
import pytest
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.construction_staging import ConstructionScheduler

class TestStageCreation:
    """Test stage creation and scheduling."""
    
    def test_create_stage_basic(self):
        """Test basic stage creation."""
        scheduler = ConstructionScheduler()
        stage = scheduler.create_stage(1, 'Foundation', ['col1', 'col2'], duration_days=14)
        
        assert stage['stage_number'] == 1
        assert stage['name'] == 'Foundation'
        assert stage['member_count'] == 2
        assert stage['duration_days'] == 14
        print(f"✓ Stage created: {stage['name']}, {stage['member_count']} members, {stage['duration_days']} days")
    
    def test_multiple_stages(self):
        """Test multiple stage scheduling."""
        scheduler = ConstructionScheduler()
        
        stage1 = scheduler.create_stage(1, 'Stage 1', ['m1', 'm2'], duration_days=7)
        stage2 = scheduler.create_stage(2, 'Stage 2', ['m3', 'm4'], duration_days=7)
        stage3 = scheduler.create_stage(3, 'Stage 3', ['m5', 'm6'], duration_days=7)
        
        assert stage1['cumulative_days'] == 7
        assert stage2['cumulative_days'] == 14
        assert stage3['cumulative_days'] == 21
        print(f"✓ Multi-stage scheduling: Total {stage3['cumulative_days']} days")
    
    def test_stage_with_supports(self):
        """Test stage with temporary supports."""
        scheduler = ConstructionScheduler()
        stage = scheduler.create_stage(1, 'Columns', ['col1', 'col2'],
                                       temp_supports_list=['brace1', 'brace2', 'shore1'],
                                       duration_days=10)
        
        assert stage['support_count'] == 3
        assert len(stage['temporary_supports']) == 3

class TestShoreDesign:
    """Test temporary shore design."""
    
    def test_shore_design_basic(self):
        """Test basic shore capacity calculation."""
        scheduler = ConstructionScheduler()
        shore = scheduler.design_temporary_shore(load_kn=5.0, shore_height_m=4.0)
        
        assert shore['capacity']['design_capacity_kn'] > 0
        assert shore['capacity']['safety_factor'] > 0
        print(f"✓ Shore capacity: {shore['capacity']['design_capacity_kn']:.1f} kN, SF={shore['capacity']['safety_factor']:.2f}")
    
    def test_shore_slenderness(self):
        """Test slenderness effects on shore capacity."""
        scheduler = ConstructionScheduler()
        
        shore_short = scheduler.design_temporary_shore(load_kn=5.0, shore_height_m=2.0)
        shore_long = scheduler.design_temporary_shore(load_kn=5.0, shore_height_m=8.0)
        
        # Longer shore has lower capacity (higher slenderness)
        assert shore_long['capacity']['design_capacity_kn'] < shore_short['capacity']['design_capacity_kn']
        print(f"✓ Slenderness effect: 2m={shore_short['capacity']['design_capacity_kn']:.1f}, 8m={shore_long['capacity']['design_capacity_kn']:.1f} kN")
    
    def test_shore_status_ok(self):
        """Test shore with adequate capacity."""
        scheduler = ConstructionScheduler()
        shore = scheduler.design_temporary_shore(load_kn=2.0, shore_height_m=3.0)
        
        assert shore['capacity']['status'] in ['OK', 'CHECK', 'FAIL']
        assert shore['capacity']['safety_factor'] > 1.0

class TestErectionLoads:
    """Test erection load assessment."""
    
    def test_erection_loads_basic(self):
        """Test basic erection load calculation."""
        scheduler = ConstructionScheduler()
        loads = scheduler.assess_erection_loads(member_type='beam', member_length_m=25.0,
                                               member_weight_kn=400.0, lift_points=2)
        
        assert loads['dynamic_loads']['lifting_condition_kn'] > loads['static_loads']['per_lift_point_kn']
        assert loads['critical_condition']['critical_load_kn'] > 0
        print(f"✓ Erection loads: Static={loads['static_loads']['per_lift_point_kn']:.1f}, Critical={loads['critical_condition']['critical_load_kn']:.1f} kN")
    
    def test_dynamic_amplification(self):
        """Test dynamic amplification factors."""
        scheduler = ConstructionScheduler()
        loads = scheduler.assess_erection_loads(member_type='column', member_length_m=10.0,
                                               member_weight_kn=200.0, lift_points=1)
        
        # Check DAF values
        assert loads['dynamic_loads']['daf_lifting'] == 1.25
        assert loads['dynamic_loads']['daf_swinging'] == 1.15
        assert loads['dynamic_loads']['daf_placing'] == 1.10
        
        # Lifting should be critical
        assert loads['critical_condition']['governs'] == 'lifting'
    
    def test_lift_point_scaling(self):
        """Test load distribution across lift points."""
        scheduler = ConstructionScheduler()
        
        loads_2pt = scheduler.assess_erection_loads(member_type='beam', member_length_m=20.0,
                                                    member_weight_kn=400.0, lift_points=2)
        loads_4pt = scheduler.assess_erection_loads(member_type='beam', member_length_m=20.0,
                                                    member_weight_kn=400.0, lift_points=4)
        
        # More lift points = lower per-point load
        assert loads_4pt['static_loads']['per_lift_point_kn'] < loads_2pt['static_loads']['per_lift_point_kn']

class TestStabilityCheck:
    """Test construction stability assessment."""
    
    def test_stability_check_stable(self):
        """Test stable construction configuration."""
        scheduler = ConstructionScheduler()
        stability = scheduler.construction_stability_check(
            stage_number=2,
            members_erected={'col1': 100, 'col2': 100, 'col3': 100, 'col4': 100},
            temp_supports={'brace1': 100, 'brace2': 100, 'brace3': 100}
        )
        
        assert stability['stability_ratio'] > 0
        assert stability['stability_status'] in ['STABLE', 'MARGINAL', 'UNSTABLE']
        print(f"✓ Stability: Ratio={stability['stability_ratio']:.2f}, Status={stability['stability_status']}")
    
    def test_stability_insufficient_support(self):
        """Test unstable configuration with insufficient support."""
        scheduler = ConstructionScheduler()
        stability = scheduler.construction_stability_check(
            stage_number=5,
            members_erected={'col1': 500, 'col2': 500, 'col3': 500},
            temp_supports={'brace1': 50}  # Very low capacity
        )
        
        assert stability['stability_ratio'] < 1.5
        assert stability['stability_status'] != 'STABLE'
        assert len(stability['recommendations']) > 0
    
    def test_p_delta_effects(self):
        """Test P-Δ second-order effects."""
        scheduler = ConstructionScheduler()
        stability = scheduler.construction_stability_check(
            stage_number=10,  # High stage
            members_erected={'col' + str(i): 200 for i in range(1, 11)},
            temp_supports={'brace1': 300, 'brace2': 300}
        )
        
        assert stability['lateral_analysis']['p_delta_amplification'] > 1.0
        assert stability['lateral_analysis']['lateral_deflection_m'] > 0

class TestScheduleTimeline:
    """Test project scheduling timeline."""
    
    def test_schedule_basic(self):
        """Test basic project schedule."""
        scheduler = ConstructionScheduler()
        schedule = scheduler.schedule_timeline(total_stories=30, stories_per_stage=3, days_per_stage=7)
        
        assert schedule['total_stages'] == 10
        assert schedule['total_duration_days'] == 70
        assert schedule['total_duration_weeks'] == 10.0
        print(f"✓ Schedule: {schedule['total_stages']} stages, {schedule['total_duration_weeks']:.1f} weeks")
    
    def test_schedule_stage_details(self):
        """Test schedule stage details."""
        scheduler = ConstructionScheduler()
        schedule = scheduler.schedule_timeline(total_stories=20, stories_per_stage=5, days_per_stage=10)
        
        assert len(schedule['stages']) == 4
        
        # Check first stage
        assert schedule['stages'][0]['stage'] == 1
        assert schedule['stages'][0]['stories'] == '1-5'
        assert schedule['stages'][0]['duration_days'] == 10
        
        # Check last stage
        assert schedule['stages'][-1]['stage'] == 4
        assert schedule['stages'][-1]['stories'] == '16-20'
    
    def test_schedule_high_rise(self):
        """Test schedule for high-rise building (60 stories)."""
        scheduler = ConstructionScheduler()
        schedule = scheduler.schedule_timeline(total_stories=60, stories_per_stage=3, days_per_stage=7)
        
        assert schedule['total_stages'] == 20
        assert schedule['total_duration_weeks'] == 20.0
        assert schedule['total_duration_days'] == 140
        print(f"✓ High-rise (60 stories): {schedule['total_stages']} stages, {schedule['total_duration_weeks']:.0f} weeks")

class TestIntegration:
    """Integration tests."""
    
    def test_full_construction_workflow(self):
        """Test complete construction workflow."""
        scheduler = ConstructionScheduler()
        
        # Create foundation stage
        stage1 = scheduler.create_stage(1, 'Foundation', ['fdn1', 'fdn2'], 
                                        temp_supports_list=['shore1', 'shore2', 'shore3'],
                                        duration_days=30)
        
        # Design temporary shores
        shore = scheduler.design_temporary_shore(load_kn=10.0, shore_height_m=5.0)
        
        # Check stability
        stability = scheduler.construction_stability_check(
            stage_number=1,
            members_erected={'fdn1': 500, 'fdn2': 500},
            temp_supports={'shore1': 50, 'shore2': 50, 'shore3': 50}
        )
        
        # Generate schedule
        schedule = scheduler.schedule_timeline(total_stories=50, stories_per_stage=2, days_per_stage=5)
        
        assert stage1['name'] == 'Foundation'
        assert shore['capacity']['design_capacity_kn'] > 0
        assert stability['stability_status'] in ['STABLE', 'MARGINAL', 'UNSTABLE']
        assert schedule['total_stages'] > 0
        
        print("✓ Full construction workflow completed")
    
    def test_multi_story_analysis(self):
        """Test analysis of multi-story construction."""
        scheduler = ConstructionScheduler()
        
        # Columns for 20 stories
        for stage in range(1, 5):
            col_names = [f'col_L{i}_{j}' for i in range((stage-1)*5+1, stage*5+1) for j in range(1, 5)]
            stage_result = scheduler.create_stage(stage, f'Columns L{(stage-1)*5+1}-{stage*5}',
                                                  col_names, duration_days=14)
            assert stage_result['member_count'] == 20

def main():
    """Run all tests."""
    print("Construction Staging Tests")
    print("=" * 60)
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    main()
