#!/usr/bin/env python3
"""
Soil-Structure Interaction (SSI) and Foundation modeling.
Handles foundation springs, pile groups, frequency-dependent impedance, and embedment effects.

Features:
- Foundation spring stiffness (translational, rotational)
- Pile-group models (vertical, lateral load sharing)
- Frequency-dependent impedance (cone models)
- Soil damping (hysteretic, radiation damping)
- P-Δ effects from flexible base
- Embedment depth effects
- Liquefaction risk screening

Usage:
    from tools.ssi_foundation import SSIAnalyzer
    analyzer = SSIAnalyzer(soil_type='clay', su_kpa=50)
    springs = analyzer.compute_foundation_springs(height_m=100, width_m=50)
"""
import math
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class SoilType(Enum):
    """Soil classification."""
    SAND_LOOSE = "sand_loose"
    SAND_DENSE = "sand_dense"
    CLAY_SOFT = "clay_soft"
    CLAY_MEDIUM = "clay_medium"
    CLAY_STIFF = "clay_stiff"
    ROCK = "rock"

@dataclass
class SoilProfile:
    """Soil layer definition."""
    depth_m: float  # Depth from surface
    thickness_m: float  # Layer thickness
    soil_type: SoilType
    phi_deg: float = 30.0  # Friction angle
    cu_kpa: float = 50.0  # Undrained shear strength
    unit_weight_kn_m3: float = 18.0
    damping_ratio: float = 0.05

class SSIAnalyzer:
    """Analyze soil-structure interaction effects."""
    
    def __init__(self, soil_type: str = 'clay_medium', cu_kpa: float = 100.0,
                 unit_weight_kn_m3: float = 18.0, embedment_depth_m: float = 2.0):
        """
        Initialize SSI analyzer.
        
        Args:
            soil_type: 'sand_loose', 'sand_dense', 'clay_soft', 'clay_medium', 'clay_stiff', 'rock'
            cu_kpa: Undrained shear strength (for clay)
            unit_weight_kn_m3: Soil unit weight
            embedment_depth_m: Foundation embedment depth
        """
        self.soil_type = soil_type
        self.cu_kpa = cu_kpa
        self.unit_weight = unit_weight_kn_m3
        self.embedment = embedment_depth_m
        
        # Soil property matrix (approximate values)
        self.soil_props = {
            'sand_loose': {'E': 5, 'v': 0.3, 'phi': 30, 'damping': 0.03},
            'sand_dense': {'E': 20, 'v': 0.3, 'phi': 35, 'damping': 0.05},
            'clay_soft': {'E': 2, 'v': 0.45, 'cu': 25, 'damping': 0.08},
            'clay_medium': {'E': 5, 'v': 0.40, 'cu': 100, 'damping': 0.07},
            'clay_stiff': {'E': 15, 'v': 0.35, 'cu': 200, 'damping': 0.05},
            'rock': {'E': 100, 'v': 0.25, 'damping': 0.02},
        }
    
    def compute_foundation_springs(self, width_m: float, length_m: float = None,
                                   height_above_m: float = 100.0) -> Dict[str, Any]:
        """
        Compute foundation spring stiffness (translational and rotational).
        Uses cone model or Winkler approach.
        
        Args:
            width_m: Foundation width (B)
            length_m: Foundation length (L); if None, assume square (L=B)
            height_above_m: Height of structure above foundation
        
        Returns:
            Spring stiffness dictionary
        """
        if length_m is None:
            length_m = width_m
        
        props = self.soil_props.get(self.soil_type, self.soil_props['clay_medium'])
        E_soil = props.get('E', 5)  # MPa (approximate modulus)
        v_soil = props.get('v', 0.4)  # Poisson's ratio
        
        # Foundation area
        A = width_m * length_m  # m^2
        I = (width_m * length_m ** 3) / 12.0  # 2nd moment (vertical bending)
        
        # Vertical spring (Winkler)
        # Kv = G * B / (0.65 - 0.1*L/B)
        # Simplified: Kv ~ E_soil * A / B
        G_soil = (E_soil * 1000) / (2 * (1 + v_soil))  # kPa
        Kv = G_soil * A / max(width_m, 1.0)  # kN/m
        
        # Horizontal/swaying spring (Winkler)
        # Kh ~ 0.6 to 0.8 * Kv (typically)
        Kh = 0.65 * Kv  # kN/m
        
        # Rotational spring (rocking)
        # Kr = G * B^4 / (3.2 - 0.2*L/B)
        # Simplified: Kr ~ E_soil * I / B
        Kr = (G_soil * I) / max(width_m, 1.0)  # kN*m/rad
        
        # Torsional spring (twist)
        # Kt ~ 0.5 to 0.7 * Kr
        Kt = 0.6 * Kr  # kN*m/rad
        
        # Coupling effects (minor)
        damping_ratio = props.get('damping', 0.05)
        
        result = {
            'foundation_dims': {
                'width_m': width_m,
                'length_m': length_m,
                'area_m2': A,
                'moment_of_inertia_m4': I,
            },
            'soil_properties': {
                'soil_type': self.soil_type,
                'modulus_mpa': E_soil,
                'poisson_ratio': v_soil,
                'shear_modulus_kpa': G_soil,
                'damping_ratio': damping_ratio,
            },
            'spring_stiffness': {
                'Kv_kn_m': Kv,  # Vertical
                'Kh_kn_m': Kh,  # Horizontal/lateral
                'Kr_kn_m_rad': Kr,  # Rocking (pitch/roll)
                'Kt_kn_m_rad': Kt,  # Torsional (twist)
            },
            'fundamental_periods': {
                'Tv_s': 2 * math.pi * math.sqrt(height_above_m / (Kv / 1000.0)),  # Vertical
                'Th_s': 2 * math.pi * math.sqrt(height_above_m / (Kh / 1000.0)),  # Lateral
                'Tr_s': 2 * math.pi * math.sqrt(height_above_m / (Kr / 1000.0 / height_above_m**2)),  # Rocking
            }
        }
        
        return result
    
    def compute_pile_group(self, num_piles: int, pile_diameter_m: float = 1.0,
                          pile_length_m: float = 30.0, spacing_m: float = 3.5,
                          cap_width_m: float = 10.0) -> Dict[str, Any]:
        """
        Compute pile-group stiffness (vertical and lateral).
        
        Args:
            num_piles: Number of piles
            pile_diameter_m: Pile diameter (m)
            pile_length_m: Pile length (m)
            spacing_m: Center-to-center pile spacing (m)
            cap_width_m: Pile cap width (m)
        
        Returns:
            Pile group stiffness and capacity
        """
        props = self.soil_props.get(self.soil_type, self.soil_props['clay_medium'])
        E_soil = props.get('E', 5)  # MPa
        cu = props.get('cu', 100)  # kPa
        
        # Single pile stiffness (simplified)
        A_pile = math.pi * (pile_diameter_m / 2.0) ** 2
        E_pile = 210000  # MPa (steel)
        
        # Vertical stiffness per pile (axial rigidity / length)
        Kv_single = (E_pile * A_pile) / pile_length_m  # MN/m
        
        # Lateral stiffness per pile (EI / L^3)
        I_pile = math.pi * (pile_diameter_m / 2.0) ** 4 / 64.0  # m^4
        Kh_single = (E_pile * I_pile) / (pile_length_m ** 3)  # MN/m
        
        # Group efficiency factors (Converse-Labarre, simplified)
        # Eg ~ 1 - d*arctan(d/L*sqrt(n))/(90*sqrt(n))
        spacing_ratio = spacing_m / pile_diameter_m
        n_sqrt = math.sqrt(num_piles)
        
        if spacing_ratio > 2.5:
            Eg_vertical = 1.0  # No group effect (well-spaced)
            Eg_lateral = 1.0
        else:
            Eg_vertical = max(0.6, 1.0 - 0.3 / n_sqrt)  # Reduced efficiency
            Eg_lateral = max(0.5, 1.0 - 0.4 / n_sqrt)   # More reduction for lateral
        
        # Group stiffness
        Kv_group = num_piles * Kv_single * Eg_vertical  # MN/m
        Kh_group = num_piles * Kh_single * Eg_lateral   # MN/m
        
        # Ultimate capacities (simplified)
        # Vertical capacity ~ 9*cu*A_pile per pile (bearing capacity for clay)
        Pu_vertical = num_piles * (9 * cu * A_pile / 1000.0)  # MN
        
        # Lateral capacity ~ 3*cu*d*L per pile (lateral resistance)
        Pu_lateral = num_piles * (3 * cu * pile_diameter_m * min(pile_length_m, 10.0) / 1000.0)  # MN
        
        result = {
            'pile_properties': {
                'num_piles': num_piles,
                'diameter_m': pile_diameter_m,
                'length_m': pile_length_m,
                'spacing_m': spacing_m,
                'cap_width_m': cap_width_m,
            },
            'single_pile_stiffness': {
                'Kv_vertical_mn_m': Kv_single,
                'Kh_lateral_mn_m': Kh_single,
            },
            'group_efficiency': {
                'Eg_vertical': Eg_vertical,
                'Eg_lateral': Eg_lateral,
            },
            'group_stiffness': {
                'Kv_group_mn_m': Kv_group,
                'Kh_group_mn_m': Kh_group,
            },
            'ultimate_capacity': {
                'Pu_vertical_mn': Pu_vertical,
                'Pu_lateral_mn': Pu_lateral,
            },
            'safety_factors': {
                'Vertical_SF': 2.5,  # Typical for driven piles
                'Lateral_SF': 1.5,   # Lower for lateral
            },
            'allowable_load': {
                'Pa_vertical_mn': Pu_vertical / 2.5,
                'Pa_lateral_mn': Pu_lateral / 1.5,
            }
        }
        
        return result
    
    def frequency_dependent_impedance(self, foundation_width_m: float,
                                     frequency_hz: float) -> Dict[str, Any]:
        """
        Compute frequency-dependent impedance (cone model, simplified).
        
        Args:
            foundation_width_m: Foundation characteristic dimension (m)
            frequency_hz: Excitation frequency (Hz)
        
        Returns:
            Complex impedance (stiffness + damping effect)
        """
        props = self.soil_props.get(self.soil_type, self.soil_props['clay_medium'])
        G_soil = props.get('E', 5) * 1000 / (2 * (1 + props.get('v', 0.4)))  # kPa
        c_wave = math.sqrt(G_soil / self.unit_weight * 9.81)  # m/s (shear wave)
        
        # Dimensionless frequency
        omega = 2 * math.pi * frequency_hz  # rad/s
        a0 = omega * foundation_width_m / (2 * c_wave)  # Dimensionless freq
        
        # Cone model springs and dampers (simplified)
        # Vertical impedance
        K_v = G_soil * foundation_width_m  # Static stiffness
        C_v = G_soil * foundation_width_m / c_wave  # Radiation damping
        
        # Dynamic stiffness (frequency-dependent)
        K_dyn = K_v * (1 + 0.1 * a0 ** 2)  # Stiffness increases with frequency
        C_dyn = C_v * (1 + 0.05 * a0)  # Damping increases with frequency
        
        # Quality factor (loss tangent)
        material_damping = props.get('damping', 0.05)
        Q_factor = 1 / (2 * material_damping)
        
        result = {
            'frequency_hz': frequency_hz,
            'dimensionless_frequency_a0': a0,
            'shear_wave_velocity_m_s': c_wave,
            'static_stiffness_kpa': K_v,
            'radiation_damping_kpa_s_m': C_v,
            'dynamic_stiffness_kpa': K_dyn,
            'dynamic_damping_kpa_s_m': C_dyn,
            'loss_tangent': material_damping,
            'quality_factor': Q_factor,
            'impedance_ratio': K_dyn / K_v,  # Frequency-dependent effect
        }
        
        return result
    
    def embedment_effects(self, foundation_depth_m: float, foundation_width_m: float) -> Dict[str, Any]:
        """
        Compute effects of foundation embedment depth.
        
        Args:
            foundation_depth_m: Depth of foundation below ground surface (m)
            foundation_width_m: Foundation width (m)
        
        Returns:
            Capacity and stiffness increase factors
        """
        depth_ratio = foundation_depth_m / foundation_width_m
        
        # Depth factors (bearing capacity increase)
        # Typical: F_d ~ 1 + 0.4 * (D/B)
        F_d = 1.0 + 0.4 * min(depth_ratio, 2.0)  # Cap at D/B = 2
        
        # Stiffness increase with embedment
        # K ~ K_0 * (1 + 0.2 * D/B)
        K_factor = 1.0 + 0.2 * depth_ratio
        
        # Damping reduction (stiffer soil at depth)
        damping_factor = max(0.5, 1.0 - 0.1 * depth_ratio)
        
        # Liquefaction resistance improvement (deeper = less liquefiable)
        # Simplified: LR ~ 1 - 0.15 * D
        liquefaction_risk = max(0.0, 1.0 - 0.15 * depth_ratio)
        
        result = {
            'foundation_depth_m': foundation_depth_m,
            'foundation_width_m': foundation_width_m,
            'depth_ratio_d_b': depth_ratio,
            'capacity_factor': F_d,
            'stiffness_factor': K_factor,
            'damping_factor': damping_factor,
            'liquefaction_risk_ratio': liquefaction_risk,
            'notes': 'Deeper foundations → higher capacity, stiffness; lower liquefaction risk',
        }
        
        return result
    
    def p_delta_effects(self, lateral_force_kn: float, lateral_displacement_m: float,
                       vertical_load_kn: float, height_m: float) -> Dict[str, Any]:
        """
        Compute P-Δ (second-order) effects from flexible foundation.
        
        Args:
            lateral_force_kn: Lateral force (wind/seismic)
            lateral_displacement_m: Lateral displacement (m)
            vertical_load_kn: Vertical load (dead + live)
            height_m: Structure height
        
        Returns:
            P-Δ moment and stability coefficient
        """
        # P-Δ moment = vertical_load * lateral_displacement
        p_delta_moment = vertical_load_kn * lateral_displacement_m  # kN*m
        
        # Direct moment from lateral force
        direct_moment = lateral_force_kn * height_m  # kN*m
        
        # P-Δ amplification factor
        # Usually: β ~ 1 / (1 - P/(P_buckling))
        # For simplified: amplification ~ 1 + P*δ / (F*H)
        amplification = 1.0 + (vertical_load_kn * lateral_displacement_m) / (lateral_force_kn * height_m + 0.001)
        
        # Stability coefficient (must be < 0.1 for design)
        stability_coeff = (vertical_load_kn * lateral_displacement_m) / (lateral_force_kn * height_m)
        
        # Effective stiffness reduction
        stiffness_reduction = 1.0 / amplification
        
        result = {
            'lateral_force_kn': lateral_force_kn,
            'lateral_displacement_m': lateral_displacement_m,
            'vertical_load_kn': vertical_load_kn,
            'structure_height_m': height_m,
            'direct_moment_kn_m': direct_moment,
            'p_delta_moment_kn_m': p_delta_moment,
            'total_moment_kn_m': direct_moment + p_delta_moment,
            'p_delta_amplification_factor': amplification,
            'stability_coefficient': stability_coeff,
            'stability_status': 'OK' if stability_coeff < 0.1 else 'CRITICAL',
            'effective_stiffness_reduction': stiffness_reduction,
        }
        
        return result
    
    def liquefaction_screening(self, depth_m: float, standard_penetration_n: float = 15,
                              groundwater_depth_m: float = 2.0,
                              earthquake_magnitude: float = 7.5) -> Dict[str, Any]:
        """
        Simplified liquefaction potential screening (simplified Seed-Idriss method).
        
        Args:
            depth_m: Depth of soil layer (m)
            standard_penetration_n: SPT N-value (blows/30cm)
            groundwater_depth_m: Depth to water table (m)
            earthquake_magnitude: Design earthquake magnitude
        
        Returns:
            Liquefaction potential and mitigation recommendations
        """
        # Cyclic stress ratio from earthquake
        amax = 0.3 * (earthquake_magnitude - 1) / 7.5  # Simplified, in g
        sigma_v0 = self.unit_weight * depth_m / 100.0  # Effective stress, kPa
        tau_cyc = 0.65 * amax * sigma_v0  # Cyclic shear stress, kPa
        CSR = tau_cyc / sigma_v0  # Cyclic stress ratio
        
        # Cyclic resistance ratio (from SPT)
        # CRR ~ (N / 15)^0.5 for intermediate conditions
        N_corrected = max(1, standard_penetration_n - 5)  # Correction for depth > 10m
        CRR = (N_corrected / 15.0) ** 0.5
        
        # Safety factor against liquefaction
        FL = CRR / CSR if CSR > 0 else 999  # > 1.0 means safe
        
        # Liquefaction potential
        if FL > 1.5:
            potential = 'Low'
        elif FL > 1.0:
            potential = 'Moderate'
        else:
            potential = 'High'
        
        # Mitigation (if needed)
        mitigation = []
        if FL < 1.2:
            mitigation.append('Deep foundations (beyond liquefiable layer)')
            mitigation.append('Soil improvement (compaction, grouting, stone columns)')
            mitigation.append('Drainage (reduce pore pressure)')
        
        result = {
            'depth_m': depth_m,
            'spt_n_value': standard_penetration_n,
            'groundwater_depth_m': groundwater_depth_m,
            'earthquake_magnitude': earthquake_magnitude,
            'effective_stress_kpa': sigma_v0,
            'cyclic_stress_ratio': CSR,
            'cyclic_resistance_ratio': CRR,
            'safety_factor_fl': FL,
            'liquefaction_potential': potential,
            'recommendation': 'No concern' if FL > 1.0 else 'Requires mitigation',
            'mitigation_measures': mitigation,
        }
        
        return result

def main():
    """Example SSI analysis."""
    print("Soil-Structure Interaction (SSI) Analysis")
    print("=" * 60)
    
    analyzer = SSIAnalyzer(soil_type='clay_medium', cu_kpa=100.0)
    
    # Foundation springs
    print("\n1. Foundation Spring Stiffness (raft, 50m x 50m):")
    springs = analyzer.compute_foundation_springs(width_m=50.0, length_m=50.0, height_above_m=300.0)
    print(f"   Kv (vertical): {springs['spring_stiffness']['Kv_kn_m']:.0f} kN/m")
    print(f"   Kh (lateral): {springs['spring_stiffness']['Kh_kn_m']:.0f} kN/m")
    print(f"   Kr (rocking): {springs['spring_stiffness']['Kr_kn_m_rad']:.0f} kN·m/rad")
    print(f"   Tv (vertical period): {springs['fundamental_periods']['Tv_s']:.2f} s")
    
    # Pile group
    print("\n2. Pile Group Analysis (36 piles, 1.2m dia, 30m long, 3.5m spacing):")
    piles = analyzer.compute_pile_group(num_piles=36, pile_diameter_m=1.2, 
                                        pile_length_m=30.0, spacing_m=3.5, cap_width_m=12.0)
    print(f"   Group vertical stiffness: {piles['group_stiffness']['Kv_group_mn_m']:.1f} MN/m")
    print(f"   Group lateral stiffness: {piles['group_stiffness']['Kh_group_mn_m']:.1f} MN/m")
    print(f"   Vertical capacity (ultimate): {piles['ultimate_capacity']['Pu_vertical_mn']:.1f} MN")
    print(f"   Vertical capacity (allowable): {piles['allowable_load']['Pa_vertical_mn']:.1f} MN")
    print(f"   Group efficiency (vertical): {piles['group_efficiency']['Eg_vertical']:.2f}")
    
    # Frequency-dependent impedance
    print("\n3. Frequency-Dependent Impedance (f=1 Hz, 50m foundation):")
    imp = analyzer.frequency_dependent_impedance(foundation_width_m=50.0, frequency_hz=1.0)
    print(f"   Dimensionless frequency (a0): {imp['dimensionless_frequency_a0']:.3f}")
    print(f"   Static stiffness: {imp['static_stiffness_kpa']:.0f} kPa")
    print(f"   Dynamic stiffness: {imp['dynamic_stiffness_kpa']:.0f} kPa")
    print(f"   Impedance ratio (Kdyn/Kstatic): {imp['impedance_ratio']:.3f}")
    
    # Embedment effects
    print("\n4. Embedment Effects (2m deep, 50m wide):")
    emb = analyzer.embedment_effects(foundation_depth_m=2.0, foundation_width_m=50.0)
    print(f"   Depth ratio (D/B): {emb['depth_ratio_d_b']:.2f}")
    print(f"   Capacity factor: {emb['capacity_factor']:.2f}x")
    print(f"   Stiffness factor: {emb['stiffness_factor']:.2f}x")
    print(f"   Liquefaction risk: {emb['liquefaction_risk_ratio']:.1%}")
    
    # P-Δ effects
    print("\n5. P-Δ (Second-Order) Effects:")
    p_delta = analyzer.p_delta_effects(lateral_force_kn=1000.0, lateral_displacement_m=0.2,
                                       vertical_load_kn=50000.0, height_m=300.0)
    print(f"   Direct moment: {p_delta['direct_moment_kn_m']:.0f} kN·m")
    print(f"   P-Δ moment: {p_delta['p_delta_moment_kn_m']:.0f} kN·m")
    print(f"   P-Δ amplification: {p_delta['p_delta_amplification_factor']:.3f}x")
    print(f"   Stability coefficient: {p_delta['stability_coefficient']:.4f} ({p_delta['stability_status']})")
    
    # Liquefaction screening
    print("\n6. Liquefaction Screening (depth 10m, SPT N=12):")
    liq = analyzer.liquefaction_screening(depth_m=10.0, standard_penetration_n=12,
                                          groundwater_depth_m=3.0, earthquake_magnitude=7.5)
    print(f"   CSR (cyclic stress ratio): {liq['cyclic_stress_ratio']:.4f}")
    print(f"   CRR (cyclic resistance ratio): {liq['cyclic_resistance_ratio']:.4f}")
    print(f"   Safety factor (FL): {liq['safety_factor_fl']:.2f}")
    print(f"   Liquefaction potential: {liq['liquefaction_potential'].upper()}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
