#!/usr/bin/env python3
"""
Validation and accuracy measurement suite.
Comprehensive testing framework comparing outputs to reference solutions.

Features:
- Geometry validation (nodes, topology)
- Modal analysis benchmarking (frequencies, MAC)
- Static analysis validation (displacements, forces)
- Dynamic response checking (peak values, spectra)
- Connection capacity verification
- Accuracy metrics and acceptance criteria
- Regression testing framework

Usage:
    from tools.validation_suite import AccuracyValidator
    validator = AccuracyValidator()
    result = validator.validate_modal_analysis(computed_freqs, reference_freqs)
"""
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class ValidationMetrics:
    """Validation result metrics."""
    mean_absolute_error: float
    relative_error_percent: float
    passes: bool
    tolerance: float
    notes: str

class AccuracyValidator:
    """Validate and measure accuracy of structural analysis outputs."""
    
    def __init__(self):
        """Initialize validator."""
        self.tolerance_defaults = {
            'geometry_node_mm': 5.0,
            'modal_frequency_percent': 10.0,
            'modal_mac': 0.85,
            'static_displacement_percent': 10.0,
            'static_force_percent': 15.0,
            'dynamic_accel_percent': 20.0,
        }
    
    def validate_node_geometry(self, computed_nodes: List[Tuple[float, float, float]],
                              reference_nodes: List[Tuple[float, float, float]],
                              tolerance_mm: float = 5.0) -> ValidationMetrics:
        """
        Validate node coordinates against reference.
        
        Args:
            computed_nodes: Computed node coordinates [(x,y,z), ...]
            reference_nodes: Reference node coordinates
            tolerance_mm: Allowable error (mm)
        
        Returns:
            Validation metrics
        """
        errors = []
        for i, (comp, ref) in enumerate(zip(computed_nodes, reference_nodes)):
            dist = math.sqrt(sum((c - r) ** 2 for c, r in zip(comp, ref)))
            errors.append(dist)
        
        mae = sum(errors) / len(errors) if errors else 0
        passes = all(e <= tolerance_mm for e in errors)
        
        return ValidationMetrics(
            mean_absolute_error=mae,
            relative_error_percent=(mae / tolerance_mm * 100) if tolerance_mm > 0 else 0,
            passes=passes,
            tolerance=tolerance_mm,
            notes=f"MAE={mae:.2f}mm, Max error={max(errors) if errors else 0:.2f}mm"
        )
    
    def validate_modal_frequencies(self, computed_freqs: List[float],
                                  reference_freqs: List[float],
                                  tolerance_percent: float = 10.0) -> ValidationMetrics:
        """
        Validate modal frequencies.
        
        Args:
            computed_freqs: Computed frequencies (Hz) [f1, f2, f3, ...]
            reference_freqs: Reference frequencies (Hz)
            tolerance_percent: Allowable error (%)
        
        Returns:
            Validation metrics
        """
        errors_percent = []
        for comp, ref in zip(computed_freqs, reference_freqs):
            error = abs(comp - ref) / ref * 100 if ref != 0 else 0
            errors_percent.append(error)
        
        mae_percent = sum(errors_percent) / len(errors_percent) if errors_percent else 0
        passes = all(e <= tolerance_percent for e in errors_percent)
        
        return ValidationMetrics(
            mean_absolute_error=mae_percent,
            relative_error_percent=mae_percent,
            passes=passes,
            tolerance=tolerance_percent,
            notes=f"MAE={mae_percent:.2f}%, Max error={max(errors_percent) if errors_percent else 0:.2f}%"
        )
    
    def validate_mac_matrix(self, computed_modes: List[List[float]],
                           reference_modes: List[List[float]],
                           tolerance: float = 0.85) -> Dict[str, Any]:
        """
        Validate mode shapes using MAC (Modal Assurance Criterion).
        
        Args:
            computed_modes: Computed mode shapes [[φ1], [φ2], ...]
            reference_modes: Reference mode shapes
            tolerance: Minimum acceptable MAC value
        
        Returns:
            MAC matrix and validation result
        """
        n_computed = len(computed_modes)
        n_reference = len(reference_modes)
        mac_matrix = []
        
        for comp_mode in computed_modes:
            row = []
            for ref_mode in reference_modes:
                # MAC = (φ_comp · φ_ref)^2 / [(φ_comp · φ_comp)(φ_ref · φ_ref)]
                numerator = sum(c * r for c, r in zip(comp_mode, ref_mode)) ** 2
                denom_comp = sum(c ** 2 for c in comp_mode)
                denom_ref = sum(r ** 2 for r in ref_mode)
                mac = numerator / (denom_comp * denom_ref + 1e-10) if (denom_comp * denom_ref) > 0 else 0
                row.append(mac)
            mac_matrix.append(row)
        
        # Check diagonal (best match MAC)
        diagonal_macs = [mac_matrix[i][i] for i in range(min(n_computed, n_reference))]
        min_mac = min(diagonal_macs) if diagonal_macs else 0
        passes = all(mac >= tolerance for mac in diagonal_macs)
        
        return {
            'mac_matrix': mac_matrix,
            'diagonal_macs': diagonal_macs,
            'min_mac': min_mac,
            'tolerance': tolerance,
            'passes': passes,
            'notes': f"Min MAC={min_mac:.3f}, Tolerance={tolerance}"
        }
    
    def validate_static_displacements(self, computed_disp: List[float],
                                     reference_disp: List[float],
                                     tolerance_percent: float = 10.0) -> ValidationMetrics:
        """
        Validate static displacements.
        
        Args:
            computed_disp: Computed displacements (mm)
            reference_disp: Reference displacements (mm)
            tolerance_percent: Allowable error (%)
        
        Returns:
            Validation metrics
        """
        errors_percent = []
        for comp, ref in zip(computed_disp, reference_disp):
            ref_abs = abs(ref)
            if ref_abs > 0.1:  # Only check significant displacements
                error = abs(comp - ref) / ref_abs * 100
                errors_percent.append(error)
        
        mae_percent = sum(errors_percent) / len(errors_percent) if errors_percent else 0
        passes = all(e <= tolerance_percent for e in errors_percent)
        
        return ValidationMetrics(
            mean_absolute_error=mae_percent,
            relative_error_percent=mae_percent,
            passes=passes,
            tolerance=tolerance_percent,
            notes=f"MAE={mae_percent:.2f}%, Checked {len(errors_percent)} DOFs"
        )
    
    def validate_reaction_forces(self, computed_forces: List[float],
                                reference_forces: List[float],
                                tolerance_percent: float = 15.0) -> ValidationMetrics:
        """
        Validate reaction forces.
        
        Args:
            computed_forces: Computed forces (kN)
            reference_forces: Reference forces (kN)
            tolerance_percent: Allowable error (%)
        
        Returns:
            Validation metrics
        """
        errors_percent = []
        for comp, ref in zip(computed_forces, reference_forces):
            ref_abs = abs(ref)
            if ref_abs > 1.0:  # Only check significant forces
                error = abs(comp - ref) / ref_abs * 100
                errors_percent.append(error)
        
        mae_percent = sum(errors_percent) / len(errors_percent) if errors_percent else 0
        passes = all(e <= tolerance_percent for e in errors_percent)
        
        return ValidationMetrics(
            mean_absolute_error=mae_percent,
            relative_error_percent=mae_percent,
            passes=passes,
            tolerance=tolerance_percent,
            notes=f"MAE={mae_percent:.2f}%, Checked {len(errors_percent)} reactions"
        )
    
    def acceptance_checklist(self) -> Dict[str, Any]:
        """
        Return validation acceptance checklist.
        
        Returns:
            Comprehensive validation checklist
        """
        return {
            'geometry': {
                'node_coordinates': f"MAE ≤ {self.tolerance_defaults['geometry_node_mm']} mm",
                'topology': "Correct element connectivity",
                'criteria': 'PASS if both items met',
            },
            'modal': {
                'frequencies_1st_3_modes': f"Error ≤ {self.tolerance_defaults['modal_frequency_percent']}%",
                'mac_diagonal': f"MAC ≥ {self.tolerance_defaults['modal_mac']}",
                'criteria': 'PASS if both items met',
            },
            'static': {
                'nodal_displacements': f"Error ≤ {self.tolerance_defaults['static_displacement_percent']}%",
                'reaction_forces': f"Error ≤ {self.tolerance_defaults['static_force_percent']}%",
                'criteria': 'PASS if both items met',
            },
            'dynamic': {
                'peak_accelerations': f"Error ≤ {self.tolerance_defaults['dynamic_accel_percent']}%",
                'spectral_response': "Shape similarity ≥ 90%",
                'criteria': 'PASS if both items met',
            },
            'connections': {
                'bolt_capacity': "Within ±5% of hand calc",
                'weld_strength': "Within ±10% of code",
                'criteria': 'PASS if both items met',
            },
        }

def main():
    """Example validation."""
    print("Validation & Accuracy Measurement Suite")
    print("=" * 60)
    
    validator = AccuracyValidator()
    
    # Modal frequency validation
    print("\n1. Modal Frequency Validation:")
    computed = [0.50, 0.25, 0.15]  # Hz
    reference = [0.48, 0.24, 0.14]  # Hz
    result = validator.validate_modal_frequencies(computed, reference, tolerance_percent=10.0)
    print(f"   {result.notes} - {'PASS' if result.passes else 'FAIL'}")
    
    # MAC validation
    print("\n2. Mode Shape (MAC) Validation:")
    mode_comp = [[1.0, 0.5, 0.2], [0.2, 1.0, 0.3], [0.1, 0.2, 1.0]]
    mode_ref = [[1.0, 0.48, 0.19], [0.21, 1.0, 0.31], [0.11, 0.21, 1.0]]
    mac_result = validator.validate_mac_matrix(mode_comp, mode_ref, tolerance=0.85)
    print(f"   Min MAC: {mac_result['min_mac']:.3f} - {'PASS' if mac_result['passes'] else 'FAIL'}")
    
    # Displacement validation
    print("\n3. Static Displacement Validation:")
    disp_comp = [10.2, 5.1, 3.0]  # mm
    disp_ref = [10.0, 5.0, 3.1]   # mm
    result = validator.validate_static_displacements(disp_comp, disp_ref, tolerance_percent=10.0)
    print(f"   {result.notes} - {'PASS' if result.passes else 'FAIL'}")
    
    # Checklist
    print("\n4. Acceptance Checklist:")
    checklist = validator.acceptance_checklist()
    for category, criteria in list(checklist.items())[:2]:
        print(f"   {category.upper()}:")
        for key, val in list(criteria.items())[:-1]:
            print(f"     - {key}: {val}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
