
# Setup Instructions for: Shanghai Tower (China) - Simplified Model

## Overview
Second tallest (632 m); double-skin facade, mega-columns, tuned mass damper

Category: super-tall
Difficulty: high

## Reference Data Sources
- Guo et al. 2014: Shanghai Tower: Design and Construction of the World's Second Tallest Building (CTBUH)

## Expected Validation Outputs
- First 3 modal frequencies: ~0.14, 0.15, 0.20 Hz (±10%)
- Max story drift under design wind (±5%)
- Outrigger brace forces (node-to-node comparison)

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
   - `python3 tools/validate_benchmark.py --benchmark shanghai_tower_china_-_simplified_model --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Reference data from CTBUH conference publications; wind pressures from aerodynamic testing summary

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
