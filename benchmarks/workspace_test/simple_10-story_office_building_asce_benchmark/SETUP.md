
# Setup Instructions for: Simple 10-Story Office Building (ASCE Benchmark)

## Overview
Published ASCE 7 example steel MRF; 3D model; gravity + lateral loads

Category: benchmark-reference
Difficulty: low

## Reference Data Sources
- ASCE 7-10 / 7-22 design examples and commentary
- NIST / AISC published FEA models and hand-calculation results

## Expected Validation Outputs
- Story shears and moments within 5% of published solution
- Natural frequencies within 3% of published
- Deflections within 5% of hand-calculation

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
   - `python3 tools/validate_benchmark.py --benchmark simple_10-story_office_building_asce_benchmark --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Low risk, published reference; use as sanity check and CI baseline

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
