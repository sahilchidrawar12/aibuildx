# Accuracy Metrics & Validation Methodology

## Overview
This document defines how to measure and report accuracy of the structural pipeline against reference models and experimental data.

## Metric Categories

### 1. Geometry Fidelity

**Node Coordinate Error**
- Metric: Mean absolute error (MAE) and max error in mm
- Formula: `error_mm = sqrt((x_model - x_ref)^2 + (y_model - y_ref)^2 + (z_model - z_ref)^2)`
- Target: ≤ 5 mm for fabrication-critical elements, ≤ 10 mm for secondary members
- Acceptance: MAE ≤ 2 mm, max ≤ 5 mm

**Topology Correctness**
- Metric: Percentage of members/plates/connections correctly matched to reference
- Formula: `(correct_entities / total_entities) × 100%`
- Target: ≥ 98%
- Acceptance: ≥ 95%

**Element Count Agreement**
- Metric: Relative error in number of elements
- Formula: `|(count_model - count_ref) / count_ref × 100%|`
- Target: ≤ 5%
- Acceptance: ≤ 10%

### 2. Modal Analysis (Natural Frequencies & Mode Shapes)

**Frequency Accuracy**
- Metric: Relative percent error in Hz
- Formula: `|f_model - f_ref| / f_ref × 100%`
- Target: ≤ 10% for global modes (1st-10th), ≤ 15% for higher modes
- Acceptance: ≤ 15% for global modes

**Mode Shape Correlation (MAC)**
- Metric: Modal Assurance Criterion (MAC) between model and reference modes
- Formula: `MAC_{ij} = |{φ_i^T φ_j}|^2 / ({φ_i^T φ_i}{φ_j^T φ_j})`
- Range: 0 (uncorrelated) to 1 (perfect match)
- Target: ≥ 0.90 for global modes
- Acceptance: ≥ 0.80

**Damping Ratio**
- Metric: Comparison of critical damping %
- Formula: `|ζ_model - ζ_ref| / ζ_ref × 100%`
- Target: ≤ 25% (damping is typically uncertain)
- Acceptance: ≤ 50%

### 3. Static Response (Displacements & Internal Forces)

**Nodal Displacement Error**
- Metric: Relative percent error at key locations
- Formula: `|u_model - u_ref| / |u_ref| × 100%`
- Target: ≤ 10% for primary response (main span/roof deflection, column tops)
- Acceptance: ≤ 15%
- Special: Check max and RMS across all nodes

**Internal Forces (Axial, Shear, Moment)**
- Metric: Percent error per element type
- Formula: `|F_model - F_ref| / max(|F_ref|, F_limit) × 100%`
- Target: ≤ 10% for primary members, ≤ 20% for secondary
- Acceptance: ≤ 15% primary, ≤ 25% secondary

**Reaction Forces**
- Metric: Percent error at supports
- Formula: `|R_model - R_ref| / |R_ref| × 100%`
- Target: ≤ 5% (must satisfy equilibrium)
- Acceptance: ≤ 10%

**Stress Distribution**
- Metric: Peak stress and stress concentration factor (Kt) comparison
- Formula: `|σ_peak_model - σ_peak_ref| / σ_peak_ref × 100%`
- Target: ≤ 15% for local peaks, ≤ 10% for global stress envelope
- Acceptance: ≤ 20%

### 4. Dynamic Response (Time-History & Response Spectrum)

**Peak Acceleration / Velocity / Displacement**
- Metric: Relative error in peak values
- Formula: `|peak_model - peak_ref| / |peak_ref| × 100%`
- Target: ≤ 15%
- Acceptance: ≤ 25%

**RMS Response**
- Metric: Root-mean-square error over time window
- Formula: `RMS_error = sqrt(mean[(x_model(t) - x_ref(t))^2]) / max(|x_ref(t)|) × 100%`
- Target: ≤ 20%
- Acceptance: ≤ 30%

**Response Spectrum Envelope**
- Metric: Percent error in spectral amplitude
- Formula: `|S_model(f) - S_ref(f)| / S_ref(f) × 100%` (per frequency bin)
- Target: ≤ 15% (within expected amplification zone)
- Acceptance: ≤ 25%

### 5. Connection & Local Behavior

**Bolt Capacity Prediction**
- Metric: Ratio of predicted capacity to reference (test or detailed FEA)
- Formula: `prediction_ratio = φRn_model / φRn_ref`
- Target: 0.95 ≤ ratio ≤ 1.05 (match certified design)
- Acceptance: 0.85 ≤ ratio ≤ 1.15 (conservative predictions acceptable)

**Bearing & Tear-Out Checks**
- Metric: Margin (overprediction) vs. detailed analysis or test
- Formula: `margin = φRn_model / demand`
- Target: 1.0 ≤ margin ≤ 1.5 (safe, not overly conservative)
- Acceptance: 0.8 ≤ margin ≤ 2.0

**Weld Capacity Error**
- Metric: Percent error in throat thickness or stress
- Formula: `|t_eff_model - t_eff_ref| / t_eff_ref × 100%`
- Target: ≤ 20%
- Acceptance: ≤ 30%

### 6. Wind & Aeroelastic Response

**Base Shear (Code-Based)**
- Metric: Comparison to ASCE 7 / Eurocode formula
- Formula: `|V_base_model - V_base_code| / V_base_code × 100%`
- Target: ≤ 5%
- Acceptance: ≤ 10%

**Story Shear Distribution**
- Metric: Relative error in story shears
- Formula: `|V_story_i_model - V_story_i_ref| / max(V_story) × 100%`
- Target: ≤ 5% at each story
- Acceptance: ≤ 10%

**Flutter Speed & Damping**
- Metric: Relative error in critical flutter speed (Vcrit)
- Formula: `|Vcrit_model - Vcrit_ref| / Vcrit_ref × 100%`
- Target: ≤ 15% (aeroelasticity is inherently uncertain)
- Acceptance: ≤ 25%

### 7. Construction Staging & Erection

**Temporary Support Force**
- Metric: Peak force during erection phases
- Formula: `|F_temp_model - F_temp_ref| / max(|F_temp_ref|) × 100%`
- Target: ≤ 20%
- Acceptance: ≤ 30%

**Out-of-Plumbness Detection**
- Metric: Correctly identifies whether temporary supports are adequate
- Formula: `binary: [stable=1, unstable=0]` (if detected correctly)
- Target: 100% accuracy in identifying stability margin
- Acceptance: ≥ 95%

## Composite Accuracy Score

**Definition**
- Percentage of all tests (across all benchmarks) that pass their target thresholds
- Formula: `accuracy_score = (passing_tests / total_tests) × 100%`

**Tiers**
- **Green (≥ 90%)**: Production-ready, suitable for preliminary design
- **Yellow (70–89%)**: Suitable for concept studies, requires validation by licensed engineer
- **Red (< 70%)**: Not ready for production; requires substantial development

## Test Harness Implementation

### Python Test Runner
```python
def run_validation(benchmark_case, model_path, reference_path, solver='opensees'):
    """
    Compare pipeline output to reference model.
    Returns: dict with pass/fail per metric and detailed error report.
    """
    # 1. Load reference data
    ref_data = load_reference(reference_path)
    
    # 2. Run pipeline on model
    pipeline_output = run_pipeline(model_path)
    
    # 3. Export to solver (e.g., OpenSees)
    solver_model = export_to_solver(pipeline_output, solver)
    
    # 4. Run analysis (modal, static, dynamic per case)
    solver_output = run_solver(solver_model)
    
    # 5. Post-process and extract metrics
    metrics = compute_metrics(pipeline_output, ref_data, solver_output)
    
    # 6. Compare to targets
    results = compare_to_targets(metrics, benchmark_case)
    
    return results
```

### Metrics JSON Output
```json
{
  "benchmark": "Burj Khalifa - Simplified Model",
  "timestamp": "2025-12-02T10:30:00Z",
  "pipeline_version": "1.0.0",
  "tests_passed": 8,
  "tests_failed": 2,
  "total_tests": 10,
  "accuracy_score": 80.0,
  "status": "yellow",
  "metrics": {
    "geometry": {
      "node_mae_mm": 2.3,
      "node_max_error_mm": 4.8,
      "status": "pass"
    },
    "modal": {
      "freq_1_model_hz": 0.109,
      "freq_1_ref_hz": 0.110,
      "error_percent": 0.9,
      "mac_1": 0.92,
      "status": "pass"
    },
    "wind_base_shear": {
      "model_kN": 450.2,
      "ref_kN": 455.0,
      "error_percent": 1.1,
      "status": "pass"
    }
  },
  "details": [
    {"test": "Frequency Mode 1", "pass": true, "expected": "0.110 Hz", "actual": "0.109 Hz"},
    {"test": "Max Drift", "pass": false, "expected": "<H/500", "actual": "H/480"}
  ]
}
```

## Regression Tracking

Store results in a database (CSV or JSON lines) to track performance over commits:
```
date, commit_hash, benchmark, metric, target, actual, status
2025-12-02, abc123, burj_khalifa, freq_1_error_pct, <=10, 0.9, pass
2025-12-02, abc123, shanghai_tower, node_mae_mm, <=5, 2.4, pass
```

## Validation Checklist

- [ ] All geometry nodes within tolerance
- [ ] Modal frequencies match reference within target error
- [ ] MAC values > 0.80 for global modes
- [ ] Static displacements within target error
- [ ] Internal forces (axial, shear, moment) acceptable
- [ ] Wind base shear matches code / reference
- [ ] Connection capacities realistic (not overly conservative)
- [ ] No numerical warnings or convergence issues
- [ ] Execution time within acceptable range
- [ ] All outputs reproducible (deterministic)

## References

- ASCE 7: Minimum Design Loads and Associated Criteria for Buildings and Other Structures
- EN 1991-1-4: Wind Actions
- Timoshenko & Gere: Theory of Elastic Stability
- Ewins: Modal Testing: Theory, Practice and Application (2nd ed.)
- SAP2000 / ETABS verification examples
- NIST Special Publications on structural dynamics
