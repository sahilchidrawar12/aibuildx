
# Setup Instructions for: Akashi Kaikyo Bridge (Japan) - Main Span Section

## Overview
1991 m main span suspension bridge; longest main span worldwide; complex cable & deck system

Category: long-span-bridge
Difficulty: very-high

## Reference Data Sources
- Nagarajaiah & Narasimhan 2006: Seismic Response & Aerodynamic Performance (EQ Spec Isol Damp)
- Wind tunnel studies and published modal data
- Honshu-Shikoku Bridge Authority (HSBA) technical reports

## Expected Validation Outputs
- First symmetric vertical mode: ~0.055 Hz (±5%)
- First lateral mode: ~0.10 Hz (±5%)
- Cable tension distribution along deck (compare to measured)
- Wind-induced flutter derivatives and aeroelastic stability

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
   - `python3 tools/validate_benchmark.py --benchmark akashi_kaikyo_bridge_japan_-_main_span_section --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
Cable stiffness and geometric nonlinearity (sag & tension) critical; wind flutter is key validation

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
