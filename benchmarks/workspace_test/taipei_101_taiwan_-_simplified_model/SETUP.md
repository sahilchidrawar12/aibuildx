
# Setup Instructions for: Taipei 101 (Taiwan) - Simplified Model

## Overview
504 m tall; tuned mass damper (660 tons), 8-section tower, steel moment frame

Category: super-tall
Difficulty: medium-high

## Reference Data Sources
- Sinn et al. 2004: Effective Liquid Dampers for Tuned Mass Dampers (JSCEJ)
- Taipei 101 public technical documentation

## Expected Validation Outputs
- Natural frequency with TMD: ~0.08 Hz (±10%)
- TMD response to wind/seismic excitation (damping ratio validation)
- Max acceleration at top <0.1g (compare to target spec)

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
   - `python3 tools/validate_benchmark.py --benchmark taipei_101_taiwan_-_simplified_model --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Focus on TMD integration and damping validation; full model not required

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
