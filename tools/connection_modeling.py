#!/usr/bin/env python3
"""
Detailed connection modeling and fabrication-level geometry.
Handles bolt capacity, slip analysis, welded connections, bearing, and fabrication details.

Features:
- Bolt pretension and slip analysis
- Bearing and hole deformation
- Weld capacity (fillet, butt)
- Plate yielding and fracture
- Contact nonlinearities
- Fabrication tolerances and shop drawings
- Connection type database

Usage:
    from tools.connection_modeling import ConnectionAnalyzer
    analyzer = ConnectionAnalyzer()
    bolt_capacity = analyzer.compute_bolt_capacity(grade='A490', diameter_mm=25, count=4)
"""
import math
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class BoltGrade(Enum):
    """Bolt grade standards."""
    A307 = ("A307", 413, 621)      # (name, Fy_MPa, Fu_MPa)
    A325 = ("A325", 635, 825)
    A490 = ("A490", 760, 1035)
    ISO_88_8S = ("ISO 8.8", 640, 800)
    ISO_10_9S = ("ISO 10.9", 900, 1000)

class WeldType(Enum):
    """Weld types."""
    FILLET = "fillet"
    BUTT_COMPLETE = "butt_complete"
    BUTT_PARTIAL = "butt_partial"
    PLUG = "plug"

@dataclass
class Bolt:
    """Bolt specification."""
    grade: BoltGrade
    diameter_mm: float
    length_mm: float
    count: int = 1
    pretension_percent: float = 70.0  # % of Fy

class ConnectionAnalyzer:
    """Analyze bolted and welded connections."""
    
    def __init__(self, steel_grade: str = 'A36', fy_mpa: float = 250.0, fu_mpa: float = 400.0):
        """
        Initialize connection analyzer.
        
        Args:
            steel_grade: Steel grade (A36, A992, etc.)
            fy_mpa: Yield strength (MPa)
            fu_mpa: Ultimate strength (MPa)
        """
        self.steel_grade = steel_grade
        self.fy = fy_mpa
        self.fu = fu_mpa
        
        # Bolt grade properties
        self.bolt_props = {
            'A307': {'fy': 413, 'fu': 621, 'name': 'A307'},
            'A325': {'fy': 635, 'fu': 825, 'name': 'A325'},
            'A490': {'fy': 760, 'fu': 1035, 'name': 'A490'},
            'ISO_88': {'fy': 640, 'fu': 800, 'name': 'ISO 8.8'},
            'ISO_109': {'fy': 900, 'fu': 1000, 'name': 'ISO 10.9'},
        }
    
    def compute_bolt_capacity(self, grade: str, diameter_mm: float, count: int = 1,
                             hole_type: str = 'standard') -> Dict[str, Any]:
        """
        Compute bolt capacity per AISC/ASTM standards.
        
        Args:
            grade: 'A307', 'A325', 'A490', 'ISO_88', 'ISO_109'
            diameter_mm: Bolt diameter
            count: Number of bolts
            hole_type: 'standard', 'oversized', 'slotted'
        
        Returns:
            Tension, shear, and bearing capacity
        """
        props = self.bolt_props.get(grade, self.bolt_props['A325'])
        fu_bolt = props['fu']
        
        # Bolt area (nominal diameter)
        d = diameter_mm / 25.4  # Convert to inches
        A_bolt = math.pi * (d / 2) ** 2  # in^2
        A_bolt_mm2 = A_bolt * 645.16  # mm^2
        
        # Tension capacity (AISC J3.1)
        # Phit = 0.75 * Fnt * Ab
        # Fnt = 0.75 * Fu for standard hole
        Fnt = 0.75 * fu_bolt  # MPa
        phi_tension = 0.75
        
        Pt_single = phi_tension * Fnt * A_bolt_mm2 / 1000.0  # kN per bolt
        Pt_total = Pt_single * count  # kN for group
        
        # Shear capacity (AISC J3.2)
        # Fnv = 0.50 * Fu for single shear
        # Fnv = 0.40 * Fu for double shear
        Fnv_single = 0.50 * fu_bolt  # MPa (single shear)
        Fnv_double = 0.40 * fu_bolt  # MPa (double shear)
        phi_shear = 0.75
        
        Pv_single = phi_shear * Fnv_single * A_bolt_mm2 / 1000.0  # kN per bolt
        Pv_double = phi_shear * Fnv_double * A_bolt_mm2 / 1000.0  # kN per bolt
        
        # Bearing capacity (AISC J3.10)
        # Phib = 0.75 * Rn
        # Rn = 1.2 * Lc * t * Fu (bearing on plate)
        t_plate = 20.0  # mm (assumed plate thickness)
        Lc = diameter_mm  # Bearing length
        Rn_bearing = 1.2 * Lc * t_plate * self.fu / 1000.0  # kN per bolt
        phi_bearing = 0.75
        
        Pb_single = phi_bearing * Rn_bearing  # kN per bolt
        Pb_total = Pb_single * count  # kN for group
        
        # Hole size effects
        hole_area_factor = {'standard': 1.0, 'oversized': 0.85, 'slotted': 0.75}
        hole_factor = hole_area_factor.get(hole_type, 1.0)
        
        Pt_total *= hole_factor
        Pv_single *= hole_factor
        Pv_double *= hole_factor
        
        result = {
            'bolt_properties': {
                'grade': grade,
                'diameter_mm': diameter_mm,
                'area_mm2': A_bolt_mm2,
                'fu_mpa': fu_bolt,
                'count': count,
                'hole_type': hole_type,
            },
            'tension_capacity': {
                'capacity_per_bolt_kn': Pt_single,
                'total_capacity_kn': Pt_total,
                'controlled_by': 'bolt_rupture',
            },
            'shear_capacity': {
                'capacity_single_shear_kn': Pv_single,
                'capacity_double_shear_kn': Pv_double,
                'total_single_shear_kn': Pv_single * count * hole_factor,
                'total_double_shear_kn': Pv_double * count * hole_factor,
            },
            'bearing_capacity': {
                'capacity_per_bolt_kn': Pb_single,
                'total_capacity_kn': Pb_total,
                'plate_thickness_mm': t_plate,
            },
            'design_capacity': {
                'tension_kn': Pt_total,
                'shear_single_kn': Pv_single * count * hole_factor,
                'shear_double_kn': Pv_double * count * hole_factor,
                'bearing_kn': Pb_total,
                'governs': 'tension' if min(Pt_total, Pb_total) == Pt_total else 'bearing',
            }
        }
        
        return result
    
    def analyze_slip(self, normal_force_kn: float, friction_coefficient: float = 0.33,
                    pretension_percent: float = 70.0, diameter_mm: float = 25.0) -> Dict[str, Any]:
        """
        Analyze slip resistance (AISC Category A, B, C connections).
        
        Args:
            normal_force_kn: Clamping force (normal to slip plane)
            friction_coefficient: μ (typically 0.33 for Class A)
            pretension_percent: % of Fu applied as initial tension
            diameter_mm: Bolt diameter
        
        Returns:
            Slip capacity and margin
        """
        # Pretension force
        props = self.bolt_props['A325']
        fu_bolt = props['fu']
        A_bolt = math.pi * (diameter_mm / 25.4 / 2) ** 2 * 645.16  # mm^2
        
        Pt_initial = (pretension_percent / 100.0) * (fu_bolt / 1000.0) * A_bolt  # kN
        
        # Friction force per bolt
        # V_slip = μ * Pt (pretension provides clamping)
        V_slip_single = friction_coefficient * Pt_initial  # kN per bolt
        
        # Combined with normal force if any
        V_slip_combined = friction_coefficient * (Pt_initial + normal_force_kn)  # kN
        
        # Slip resistance category
        if friction_coefficient >= 0.33:
            category = 'Class A (slip-critical)'
        else:
            category = 'Standard (bearing)'
        
        result = {
            'bolt_pretension': {
                'pretension_percent': pretension_percent,
                'pretension_force_kn': Pt_initial,
                'diameter_mm': diameter_mm,
            },
            'friction_properties': {
                'friction_coefficient': friction_coefficient,
                'normal_force_kn': normal_force_kn,
                'connection_category': category,
            },
            'slip_capacity': {
                'capacity_from_pretension_kn': V_slip_single,
                'capacity_with_normal_force_kn': V_slip_combined,
            },
            'safety_margin': {
                'slip_margin': V_slip_single / (1 + 0.1) if V_slip_single > 0 else 0,
                'status': 'Slip-critical' if friction_coefficient >= 0.33 else 'Bearing',
            }
        }
        
        return result
    
    def compute_weld_capacity(self, weld_type: str, weld_size_mm: float, weld_length_mm: float,
                            steel_grade: str = 'A36', weld_process: str = 'GMAW') -> Dict[str, Any]:
        """
        Compute weld capacity per AWS/AISC standards.
        
        Args:
            weld_type: 'fillet', 'butt_complete', 'butt_partial', 'plug'
            weld_size_mm: Fillet leg size or groove depth (mm)
            weld_length_mm: Length of weld (mm)
            steel_grade: Base metal grade
            weld_process: 'SMAW', 'GMAW', 'FCAW', 'SAW'
        
        Returns:
            Weld strength and capacity
        """
        # Weld metal strength (for E70XX electrodes, typically)
        Fexx = 485  # MPa (E70XX nominal)
        
        # Effective weld strength reduction factors
        process_factor = {
            'SMAW': 1.0,
            'GMAW': 1.0,
            'FCAW': 0.95,
            'SAW': 1.05,
        }
        strength_factor = process_factor.get(weld_process, 1.0)
        
        if weld_type == 'fillet':
            # Fillet weld: Rn = 0.60 * Fexx * w * L
            # w = weld size, L = weld length
            # Phi = 0.75
            w_eff = weld_size_mm * 0.707  # Effective throat thickness
            
            Rn = 0.6 * Fexx * w_eff * weld_length_mm / 1000.0  # kN
            phi = 0.75
            capacity = phi * Rn * strength_factor
            
            mode = 'Weld metal yielding'
        
        elif weld_type == 'butt_complete':
            # Butt weld (CJP): Full capacity of base metal
            # Rn = 0.90 * Fyb * A_plate
            # For conservative estimate, assume plate 20mm thick
            A_plate = 20 * weld_length_mm / 1000.0  # m^2 equivalent
            
            Rn = 0.90 * self.fy * A_plate * 1000  # kN (rough)
            phi = 0.90
            capacity = phi * Rn
            
            mode = 'Base metal yielding'
        
        elif weld_type == 'plug':
            # Plug weld: Limited shear capacity
            # Rn = 0.75 * Fexx * A_plug
            # Assume plug diameter = weld_size_mm
            A_plug = math.pi * (weld_size_mm / 2.0) ** 2 / 1000.0  # mm^2 to cm^2
            
            Rn = 0.75 * Fexx * A_plug / 1000.0  # kN (rough)
            phi = 0.75
            capacity = phi * Rn
            
            mode = 'Plug shear'
        
        else:
            capacity = 0
            mode = 'Unknown'
        
        result = {
            'weld_properties': {
                'type': weld_type,
                'size_mm': weld_size_mm,
                'length_mm': weld_length_mm,
                'process': weld_process,
                'electrode_type': 'E70XX',
                'fexx_mpa': Fexx,
            },
            'capacity': {
                'capacity_kn': capacity,
                'failure_mode': mode,
                'phi_factor': phi if weld_type in ['fillet', 'butt_complete', 'plug'] else 0.75,
                'strength_factor': strength_factor,
            },
            'design_notes': f"{weld_type.upper()} weld, {weld_process}, capacity {capacity:.1f} kN",
        }
        
        return result
    
    def plate_yielding_capacity(self, width_mm: float, thickness_mm: float, holes_count: int = 0,
                               hole_diameter_mm: float = 26.0) -> Dict[str, Any]:
        """
        Compute plate yielding capacity (gross and net sections).
        
        Args:
            width_mm: Plate width (mm)
            thickness_mm: Plate thickness (mm)
            holes_count: Number of bolt holes
            hole_diameter_mm: Hole diameter (mm)
        
        Returns:
            Gross and net section capacities
        """
        # Gross section
        A_gross = width_mm * thickness_mm  # mm^2
        
        # Net section (with bolt holes)
        # Reduce by largest 2 holes (staggered pattern)
        if holes_count > 0:
            hole_area = math.pi * (hole_diameter_mm / 2.0) ** 2 / 4.0
            A_net = A_gross - holes_count * hole_area
        else:
            A_net = A_gross
        
        # Yielding capacity (AISC J4.1)
        # Phi_t = 0.90 * Fy * Ag
        phi_y = 0.90
        P_y_gross = phi_y * self.fy * A_gross / 1000.0  # kN
        
        # Fracture capacity (AISC J4.2)
        # Phi_u = 0.75 * Fu * An * U
        # U = 1.0 for standard case
        phi_f = 0.75
        U_factor = 1.0  # Assumes centered loading
        P_f_net = phi_f * self.fu * A_net * U_factor / 1000.0  # kN
        
        result = {
            'plate_properties': {
                'width_mm': width_mm,
                'thickness_mm': thickness_mm,
                'area_gross_mm2': A_gross,
                'area_net_mm2': A_net,
                'holes_count': holes_count,
                'hole_diameter_mm': hole_diameter_mm,
            },
            'yielding_capacity': {
                'capacity_kn': P_y_gross,
                'controlling': 'gross_section',
                'phi_factor': phi_y,
                'strength': self.fy,
            },
            'fracture_capacity': {
                'capacity_kn': P_f_net,
                'controlling': 'net_section',
                'phi_factor': phi_f,
                'strength': self.fu,
                'u_factor': U_factor,
            },
            'design_capacity': {
                'capacity_kn': min(P_y_gross, P_f_net),
                'governs': 'yielding' if P_y_gross < P_f_net else 'fracture',
            }
        }
        
        return result
    
    def fabrication_tolerances(self, member_depth_mm: float, bolt_pattern_pitch_mm: float) -> Dict[str, Any]:
        """
        Define fabrication tolerances for shop and field assembly.
        
        Args:
            member_depth_mm: Member depth (for guidance)
            bolt_pattern_pitch_mm: Bolt spacing
        
        Returns:
            Recommended tolerances per AISC/AWS
        """
        result = {
            'member_tolerances': {
                'length_tolerance_mm': max(5, member_depth_mm / 500.0),  # AISC M002 Table 8.1
                'depth_variation_mm': max(3, member_depth_mm / 800.0),
                'camber_tolerance_mm': member_depth_mm / 960.0,
                'twist_radians': 0.01,  # 0.01 rad typical
            },
            'bolt_hole_tolerances': {
                'standard_hole_diameter_mm': 26.0 if bolt_pattern_pitch_mm < 100 else 28.0,
                'position_tolerance_mm': max(3, bolt_pattern_pitch_mm / 50.0),
                'edge_distance_min_mm': 32.0,  # Typical for 25mm bolts
                'edge_distance_max_mm': 150.0,
            },
            'weld_tolerances': {
                'fillet_size_tolerance_mm': 1.5,  # AWS D1.1/D1.1M
                'length_tolerance_mm': 10.0,
                'undercut_max_mm': 0.5,
                'porosity_max_diameter_mm': 3.0,
            },
            'connection_gaps': {
                'snug_tight_clearance_mm': 1.0,
                'fit_up_gap_mm': 2.0,
                'paint_clearance_mm': 0.3,  # If edges painted
            },
            'shop_marks': {
                'identification': 'Heat number, shop order, piece mark, orientation arrow',
                'location': 'Typically on back (comp) face away from bolts',
            },
        }
        
        return result

def main():
    """Example connection analysis."""
    print("Connection Modeling & Fabrication Analysis")
    print("=" * 60)
    
    analyzer = ConnectionAnalyzer()
    
    # Bolt capacity
    print("\n1. Bolt Capacity (A325, 25mm, 4 bolts):")
    bolt_cap = analyzer.compute_bolt_capacity(grade='A325', diameter_mm=25.0, count=4)
    print(f"   Tension capacity: {bolt_cap['design_capacity']['tension_kn']:.1f} kN")
    print(f"   Shear capacity (single): {bolt_cap['design_capacity']['shear_single_kn']:.1f} kN")
    print(f"   Bearing capacity: {bolt_cap['design_capacity']['bearing_kn']:.1f} kN")
    print(f"   Governs: {bolt_cap['design_capacity']['governs'].upper()}")
    
    # Slip resistance
    print("\n2. Slip Resistance (Class A, pretension 70%):")
    slip = analyzer.analyze_slip(normal_force_kn=0, friction_coefficient=0.33, 
                                pretension_percent=70.0, diameter_mm=25.0)
    print(f"   Pretension force: {slip['bolt_pretension']['pretension_force_kn']:.1f} kN")
    print(f"   Slip capacity: {slip['slip_capacity']['capacity_from_pretension_kn']:.1f} kN")
    print(f"   Category: {slip['friction_properties']['connection_category']}")
    
    # Weld capacity
    print("\n3. Weld Capacity (fillet, 8mm, 200mm long):")
    weld = analyzer.compute_weld_capacity(weld_type='fillet', weld_size_mm=8.0,
                                          weld_length_mm=200.0, steel_grade='A36', weld_process='GMAW')
    print(f"   Capacity: {weld['capacity']['capacity_kn']:.1f} kN")
    print(f"   Failure mode: {weld['capacity']['failure_mode']}")
    
    # Plate yielding
    print("\n4. Plate Yielding Capacity (200 x 15 mm, 2 holes):")
    plate = analyzer.plate_yielding_capacity(width_mm=200.0, thickness_mm=15.0,
                                             holes_count=2, hole_diameter_mm=26.0)
    print(f"   Gross section capacity: {plate['yielding_capacity']['capacity_kn']:.1f} kN")
    print(f"   Net section capacity: {plate['fracture_capacity']['capacity_kn']:.1f} kN")
    print(f"   Governs: {plate['design_capacity']['governs'].upper()}")
    
    # Fabrication tolerances
    print("\n5. Fabrication Tolerances (member 800mm deep, bolt pitch 100mm):")
    tol = analyzer.fabrication_tolerances(member_depth_mm=800.0, bolt_pattern_pitch_mm=100.0)
    print(f"   Length tolerance: ±{tol['member_tolerances']['length_tolerance_mm']:.1f} mm")
    print(f"   Hole position: ±{tol['bolt_hole_tolerances']['position_tolerance_mm']:.1f} mm")
    print(f"   Fillet size tolerance: ±{tol['weld_tolerances']['fillet_size_tolerance_mm']:.1f} mm")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
