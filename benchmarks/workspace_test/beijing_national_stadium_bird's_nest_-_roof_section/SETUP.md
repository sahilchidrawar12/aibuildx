
# Setup Instructions for: Beijing National Stadium (Bird's Nest) - Roof Section

## Overview
Large stadium roof; complex truss + membrane system; 91,000 capacity

Category: large-roof
Difficulty: high

## Reference Data Sources
- Wei et al. 2008: Structural Design & Analysis of Beijing National Stadium (Struct. Des. Long Span Buildings)
- Wind tunnel pressure data (partial public release)

## Expected Validation Outputs
- Natural frequencies (first 3 modes): ~0.7, 0.9, 1.2 Hz (±10%)
- Max deflection under snow/wind: <span/250 (target accuracy ±5%)
- Roof membrane tension distribution
- Connection forces in truss joints

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
   - `python3 tools/validate_benchmark.py --benchmark beijing_national_stadium_bird's_nest_-_roof_section --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Membrane coupling and large displacements; wind pressure distribution critical

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
