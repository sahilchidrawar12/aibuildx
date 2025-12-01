
# Setup Instructions for: Wind Tunnel Pressure Distribution on High-Rise (Simplified Aero Coupling)

## Overview
Square tower subjected to uniform wind; validate pressure mapping & modal response

Category: wind-aero
Difficulty: medium

## Reference Data Sources
- ASCE 7 wind pressure coefficients (Cp tables)
- CIRIA Guide or EN1991-1-4 for wind loading

## Expected Validation Outputs
- Base shear vs. expected ASCE 7 formula within 5%
- Story shears decrease monotonically per code prediction (±3%)
- Modal response envelope match to spectral input within 10%

## Steps to Complete This Benchmark

1. **Obtain Reference Data**
   - Download or create reference model(s) from sources listed above
   - Place files in: `reference/`
   - Expected file formats: JSON (model def), CSV (data), or solver-native (e.g., .ops for OpenSees)

2. **Prepare Input Model**
   - Either:
     a) Use simplified synthetic model (create `input/model.json`)
     b) Convert reference CAD/BIM to JSON using the pipeline
   - Place input in: `input/model.json`

3. **Run Pipeline**
   - Execute: `python3 -c "
     import sys; sys.path.insert(0, '.')
     from src.pipeline.agents import main_pipeline_agent
     import json
     with open('input/model.json') as f:
         payload = json.load(f)
     result = main_pipeline_agent.process({'data': {'dxf_entities': payload}} )
     with open('output/pipeline_result.json', 'w') as f:
         json.dump(result, f, indent=2)
   "`

4. **Export to Solver**
   - Once solver exporter is implemented, run:
   - `python3 tools/export_to_opensees.py output/pipeline_result.json output/model.tcl`
   - (Or equivalent for CalculiX, Abaqus, etc.)

5. **Run Reference Solver**
   - Execute solver on reference model: e.g., `opensees output/reference.tcl`
   - Capture: frequencies, displacements, forces, connection capacities

6. **Run Validation**
   - Compare pipeline + solver output to reference
   - `python3 tools/validate_benchmark.py --benchmark wind_tunnel_pressure_distribution_on_high-rise_simplified_aero_coupling --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Validates wind load application and dynamic response; no experimental data needed (code-based)

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
