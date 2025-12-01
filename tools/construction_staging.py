#!/usr/bin/env python3
"""
Construction-stage analysis and erection sequencing.
Handles staged construction, temporary supports, erection loads, and stability checks.

Features:
- Stage sequencing and scheduling
- Temporary support design
- Erection load assessment
- Construction stability checks
- Partial structure analysis
- Propping and reshore design

Usage:
    from tools.construction_staging import ConstructionScheduler
    scheduler = ConstructionScheduler()
    stage = scheduler.create_stage(name='Stage 1', members=['col1', 'beam1'], supports=['temp1'])
"""
import math
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

class SupportType(Enum):
    """Temporary support type."""
    SHORE = "shore"
    BRACE = "brace"
    STRAND = "strand"
    SCAFFOLD = "scaffold"

@dataclass
class Stage:
    """Construction stage definition."""
    stage_number: int
    name: str
    installed_members: List[str] = field(default_factory=list)
    erected_members: List[str] = field(default_factory=list)
    temporary_supports: List[str] = field(default_factory=list)
    removed_supports: List[str] = field(default_factory=list)
    duration_days: int = 7
    description: str = ""
    
class ConstructionScheduler:
    """Schedule and analyze construction stages."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.stages = []
        self.start_date = datetime.now()
        self.temporary_supports = {}
    
    def create_stage(self, stage_number: int, name: str, members_list: List[str],
                     temp_supports_list: List[str] = None, duration_days: int = 7) -> Dict[str, Any]:
        """
        Create a construction stage.
        
        Args:
            stage_number: Sequential stage ID
            name: Stage name (e.g., 'Foundation', 'Columns', 'Beams L1-5')
            members_list: Members erected in this stage
            temp_supports_list: Temporary supports added
            duration_days: Expected duration
        
        Returns:
            Stage dictionary
        """
        if temp_supports_list is None:
            temp_supports_list = []
        
        stage = Stage(
            stage_number=stage_number,
            name=name,
            erected_members=members_list,
            temporary_supports=temp_supports_list,
            duration_days=duration_days,
        )
        
        self.stages.append(stage)
        
        stage_date = self.start_date + timedelta(days=sum(s.duration_days for s in self.stages[:-1]))
        
        result = {
            'stage_number': stage_number,
            'name': name,
            'members_erected': members_list,
            'member_count': len(members_list),
            'temporary_supports': temp_supports_list,
            'support_count': len(temp_supports_list),
            'duration_days': duration_days,
            'scheduled_date': stage_date.strftime('%Y-%m-%d'),
            'cumulative_days': sum(s.duration_days for s in self.stages),
        }
        
        return result
    
    def design_temporary_shore(self, load_kn: float, shore_height_m: float,
                              buckling_length_m: float = None, pipe_diameter_mm: float = 114.3) -> Dict[str, Any]:
        """
        Design temporary shore for formwork support.
        
        Args:
            load_kn: Load per shore (kN)
            shore_height_m: Shore length (m)
            buckling_length_m: Effective buckling length (if None, use shore_height)
            pipe_diameter_mm: Standard pipe diameter (mm)
        
        Returns:
            Shore design capacity and check
        """
        if buckling_length_m is None:
            buckling_length_m = shore_height_m
        
        # Standard pipe properties (Example: Ø114.3 x 3.2mm)
        A_pipe = 1130  # mm^2 (approximate for 114.3 x 3.2)
        I_pipe = 9.05e4  # mm^4
        r_pipe = math.sqrt(I_pipe / A_pipe)  # Radius of gyration
        
        # Steel properties (temporary pipe)
        E_steel = 200000  # MPa
        fy_temp = 250  # MPa (temporary)
        
        # Euler buckling stress
        lambda_ratio = (buckling_length_m * 1000.0) / r_pipe  # Slenderness ratio
        
        if lambda_ratio < 100:
            # Inelastic buckling (Johnson formula)
            fe = (fy_temp / (1 + (fy_temp * lambda_ratio ** 2) / (math.pi ** 2 * E_steel))) * A_pipe / 1000.0  # kN
        else:
            # Elastic buckling (Euler)
            fe = (math.pi ** 2 * E_steel * A_pipe) / (1000.0 * lambda_ratio ** 2)  # kN
        
        # Design capacity (0.75 * theoretical)
        capacity = 0.75 * fe
        
        # Safety factor
        sf = capacity / load_kn if load_kn > 0 else 999
        status = 'OK' if sf > 1.5 else ('CHECK' if sf > 1.0 else 'FAIL')
        
        result = {
            'shore_properties': {
                'pipe_diameter_mm': pipe_diameter_mm,
                'area_mm2': A_pipe,
                'radius_gyration_mm': r_pipe,
                'height_m': shore_height_m,
                'buckling_length_m': buckling_length_m,
            },
            'load_analysis': {
                'applied_load_kn': load_kn,
                'slenderness_ratio': lambda_ratio,
                'buckling_type': 'Inelastic' if lambda_ratio < 100 else 'Elastic',
            },
            'capacity': {
                'theoretical_capacity_kn': fe,
                'design_capacity_kn': capacity,
                'safety_factor': sf,
                'status': status,
            }
        }
        
        return result
    
    def assess_erection_loads(self, member_type: str, member_length_m: float,
                             member_weight_kn: float, lift_points: int = 2) -> Dict[str, Any]:
        """
        Assess loads during erection (lifting, swinging).
        
        Args:
            member_type: 'beam', 'column', 'deck_panel'
            member_length_m: Member length
            member_weight_kn: Dead load
            lift_points: Number of lift points
        
        Returns:
            Erection load envelopes and impact factors
        """
        # Dynamic amplification factors (DAF)
        daf_lifting = 1.25  # 25% impact from lifting
        daf_swinging = 1.15  # 15% impact from swinging
        daf_placing = 1.10   # 10% impact from placement
        
        # Load per lift point
        static_per_point = member_weight_kn / lift_points
        
        # Transverse load (swinging) - typically 5-10% horizontal
        transverse = 0.075 * member_weight_kn  # 7.5% horizontal
        
        # Dynamic loads
        lifting_load = daf_lifting * static_per_point
        swinging_load = daf_swinging * (static_per_point + transverse / 2.0)
        placing_load = daf_placing * static_per_point
        
        # Combined critical condition
        critical_load = max(lifting_load, swinging_load, placing_load)
        
        result = {
            'member_properties': {
                'type': member_type,
                'length_m': member_length_m,
                'weight_kn': member_weight_kn,
                'lift_points': lift_points,
            },
            'static_loads': {
                'per_lift_point_kn': static_per_point,
                'transverse_kn': transverse,
            },
            'dynamic_loads': {
                'lifting_condition_kn': lifting_load,
                'swinging_condition_kn': swinging_load,
                'placing_condition_kn': placing_load,
                'daf_lifting': daf_lifting,
                'daf_swinging': daf_swinging,
                'daf_placing': daf_placing,
            },
            'critical_condition': {
                'critical_load_kn': critical_load,
                'governs': 'lifting' if lifting_load == critical_load else ('swinging' if swinging_load == critical_load else 'placing'),
            },
            'sling_angle_effect': {
                'best_angle_deg': 90,  # Vertical slings
                'worst_angle_deg': 45,  # 45° slings increase load
                'sling_tension_kn': critical_load / (2.0 * math.cos(math.radians(45.0))),  # Rough estimate
            }
        }
        
        return result
    
    def construction_stability_check(self, stage_number: int, members_erected: Dict[str, float],
                                     temp_supports: Dict[str, float]) -> Dict[str, Any]:
        """
        Check structural stability during construction.
        
        Args:
            stage_number: Stage being analyzed
            members_erected: {member_id: weight_kn} for erected members
            temp_supports: {support_id: capacity_kn} for temporary supports
        
        Returns:
            Stability assessment and recommendations
        """
        # Total weight erected
        total_weight = sum(members_erected.values())
        
        # Total support capacity
        total_capacity = sum(temp_supports.values())
        
        # Stability ratio
        stability_ratio = total_capacity / total_weight if total_weight > 0 else 999
        
        # Check P-Δ (second order)
        # Assume center of mass at 60% of stage height
        stage_height_m = 4.0 * stage_number  # Rough estimate
        
        # Lateral acceleration during construction (conservative 0.05g)
        lateral_accel = 0.05 * 9.81  # m/s^2
        
        # Lateral force
        lateral_force = total_weight * lateral_accel / 9.81  # kN
        
        # Lateral deflection (rough estimate)
        lateral_deflection_m = lateral_force / (total_capacity / stage_height_m + 1.0) / 1000.0
        
        # P-Δ effect
        p_delta_amplification = 1.0 + (lateral_deflection_m * total_weight) / (lateral_force * stage_height_m + 0.1)
        
        # Check slenderness
        slenderness = stage_height_m / (total_capacity / total_weight + 0.1)
        
        # Stability status
        if stability_ratio >= 2.0 and slenderness < 50:
            status = 'STABLE'
        elif stability_ratio >= 1.5 and slenderness < 100:
            status = 'MARGINAL'
        else:
            status = 'UNSTABLE'
        
        result = {
            'stage': stage_number,
            'total_weight_erected_kn': total_weight,
            'total_support_capacity_kn': total_capacity,
            'stability_ratio': stability_ratio,
            'stability_status': status,
            'recommendations': [],
            'lateral_analysis': {
                'stage_height_m': stage_height_m,
                'lateral_force_kn': lateral_force,
                'lateral_deflection_m': lateral_deflection_m,
                'p_delta_amplification': p_delta_amplification,
            },
            'slenderness': slenderness,
            'slenderness_ratio_check': 'OK' if slenderness < 100 else 'ADD BRACING',
        }
        
        # Add recommendations
        if stability_ratio < 1.5:
            result['recommendations'].append('Add temporary bracing')
        if slenderness > 100:
            result['recommendations'].append('Add lateral bracing (reduce slenderness)')
        if p_delta_amplification > 1.2:
            result['recommendations'].append('Check second-order effects; consider additional supports')
        
        if not result['recommendations']:
            result['recommendations'].append('Stage is stable; proceed as planned')
        
        return result
    
    def schedule_timeline(self, total_stories: int, stories_per_stage: int = 3,
                         days_per_stage: int = 7) -> Dict[str, Any]:
        """
        Generate construction schedule timeline.
        
        Args:
            total_stories: Total number of stories
            stories_per_stage: Stories erected per stage
            days_per_stage: Days per stage
        
        Returns:
            Schedule with stage-by-stage timeline
        """
        num_stages = math.ceil(total_stories / stories_per_stage)
        
        schedule = {
            'project': f'{total_stories}-Story Building',
            'total_stages': num_stages,
            'total_duration_days': num_stages * days_per_stage,
            'total_duration_weeks': (num_stages * days_per_stage) / 7.0,
            'stories_per_stage': stories_per_stage,
            'stages': [],
        }
        
        for s in range(num_stages):
            start_story = s * stories_per_stage + 1
            end_story = min((s + 1) * stories_per_stage, total_stories)
            stage_date = self.start_date + timedelta(days=s * days_per_stage)
            
            schedule['stages'].append({
                'stage': s + 1,
                'stories': f'{start_story}-{end_story}',
                'start_date': stage_date.strftime('%Y-%m-%d'),
                'end_date': (stage_date + timedelta(days=days_per_stage)).strftime('%Y-%m-%d'),
                'duration_days': days_per_stage,
                'cumulative_days': (s + 1) * days_per_stage,
            })
        
        schedule['completion_date'] = (self.start_date + timedelta(days=num_stages * days_per_stage)).strftime('%Y-%m-%d')
        
        return schedule

def main():
    """Example construction scheduling."""
    print("Construction Staging & Erection Analysis")
    print("=" * 60)
    
    scheduler = ConstructionScheduler()
    
    # Create stages
    print("\n1. Construction Stages:")
    stage1 = scheduler.create_stage(1, 'Foundation & Basement', ['col1', 'col2', 'col3', 'col4'], duration_days=30)
    print(f"   Stage {stage1['stage_number']}: {stage1['name']}")
    print(f"   Members: {stage1['member_count']}, Date: {stage1['scheduled_date']}")
    
    stage2 = scheduler.create_stage(2, 'Columns (L1-5)', ['col_l1', 'col_l2', 'col_l3'], 
                                    temp_supports_list=['brace_1', 'brace_2', 'brace_3'], duration_days=21)
    print(f"   Stage {stage2['stage_number']}: {stage2['name']}")
    
    # Temporary shore design
    print("\n2. Temporary Shore Design (2 kN per shore, 6m height):")
    shore = scheduler.design_temporary_shore(load_kn=2.0, shore_height_m=6.0)
    print(f"   Slenderness ratio: {shore['load_analysis']['slenderness_ratio']:.0f}")
    print(f"   Design capacity: {shore['capacity']['design_capacity_kn']:.1f} kN")
    print(f"   Safety factor: {shore['capacity']['safety_factor']:.2f} ({shore['capacity']['status']})")
    
    # Erection loads
    print("\n3. Erection Loads (Beam, 30m, 500 kN, 2 lift points):")
    erect = scheduler.assess_erection_loads(member_type='beam', member_length_m=30.0,
                                            member_weight_kn=500.0, lift_points=2)
    print(f"   Static per point: {erect['static_loads']['per_lift_point_kn']:.1f} kN")
    print(f"   Lifting condition: {erect['dynamic_loads']['lifting_condition_kn']:.1f} kN")
    print(f"   Critical load: {erect['critical_condition']['critical_load_kn']:.1f} kN ({erect['critical_condition']['governs']})")
    
    # Stability check
    print("\n4. Construction Stability (Stage 2, 6 columns @ 300 kN, 3 braces @ 150 kN each):")
    stability = scheduler.construction_stability_check(
        stage_number=2,
        members_erected={'col1': 300, 'col2': 300, 'col3': 300, 'col4': 300, 'col5': 300, 'col6': 300},
        temp_supports={'brace1': 150, 'brace2': 150, 'brace3': 150}
    )
    print(f"   Total weight: {stability['total_weight_erected_kn']:.0f} kN")
    print(f"   Total capacity: {stability['total_support_capacity_kn']:.0f} kN")
    print(f"   Stability ratio: {stability['stability_ratio']:.2f} ({stability['stability_status']})")
    print(f"   Recommendation: {stability['recommendations'][0]}")
    
    # Schedule timeline
    print("\n5. Project Schedule (60 stories, 3 per stage, 7 days per stage):")
    sched = scheduler.schedule_timeline(total_stories=60, stories_per_stage=3, days_per_stage=7)
    print(f"   Total stages: {sched['total_stages']}")
    print(f"   Total duration: {sched['total_duration_weeks']:.1f} weeks ({sched['total_duration_days']} days)")
    print(f"   Completion: {sched['completion_date']}")
    print(f"   First stage: {sched['stages'][0]['stories']} (start {sched['stages'][0]['start_date']})")
    print(f"   Last stage: {sched['stages'][-1]['stories']} (end {sched['stages'][-1]['end_date']})")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
