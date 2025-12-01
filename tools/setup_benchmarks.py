#!/usr/bin/env python3
"""
Setup benchmarks workspace and provide instructions for gathering reference data.
Usage:
    python3 tools/setup_benchmarks.py --workspace benchmarks/workspace
"""
import argparse
import json
import os
from pathlib import Path
import yaml

def load_benchmarks_yaml(yaml_path):
    """Load benchmarks.yaml and return the list of benchmark definitions."""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('benchmarks', [])

def create_benchmark_folder(workspace_path, benchmark):
    """Create folder structure for a single benchmark."""
    name = benchmark['name']
    safe_name = name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    bench_dir = Path(workspace_path) / safe_name
    
    # Create subdirectories
    (bench_dir / 'input').mkdir(parents=True, exist_ok=True)
    (bench_dir / 'reference').mkdir(parents=True, exist_ok=True)
    (bench_dir / 'output').mkdir(parents=True, exist_ok=True)
    (bench_dir / 'reports').mkdir(parents=True, exist_ok=True)
    
    # Write metadata
    metadata = {
        'name': benchmark['name'],
        'description': benchmark.get('description', ''),
        'category': benchmark.get('category', 'unknown'),
        'difficulty': benchmark.get('difficulty', 'unknown'),
        'reference_sources': benchmark.get('reference_sources', []),
        'expected_outputs': benchmark.get('expected_outputs', []),
        'notes': benchmark.get('notes', ''),
    }
    
    with open(bench_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Write setup instructions
    instructions = f"""
# Setup Instructions for: {benchmark['name']}

## Overview
{benchmark.get('description', 'N/A')}

Category: {benchmark.get('category', 'unknown')}
Difficulty: {benchmark.get('difficulty', 'unknown')}

## Reference Data Sources
{_format_sources(benchmark.get('reference_sources', []))}

## Expected Validation Outputs
{_format_outputs(benchmark.get('expected_outputs', []))}

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
     result = main_pipeline_agent.process({{'data': {{'dxf_entities': payload}}}} )
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
   - `python3 tools/validate_benchmark.py --benchmark {safe_name} --workspace .`

7. **Review Report**
   - Check: `reports/accuracy_report.json`
   - Review per-metric pass/fail and error percentages

## Notes
{benchmark.get('notes', 'N/A')}

---
For help: see `validation/accuracy_metrics.md` for metric definitions and acceptance thresholds.
"""
    
    with open(bench_dir / 'SETUP.md', 'w') as f:
        f.write(instructions)
    
    print(f"✓ Created {bench_dir}")
    return bench_dir

def _format_sources(sources):
    """Format source list as markdown."""
    if not sources:
        return "- (None provided)"
    return '\n'.join(f"- {src}" for src in sources)

def _format_outputs(outputs):
    """Format expected outputs as markdown."""
    if not outputs:
        return "- (To be determined)"
    return '\n'.join(f"- {out}" for out in outputs)

def main():
    parser = argparse.ArgumentParser(
        description='Setup benchmarks workspace for validation'
    )
    parser.add_argument(
        '--workspace',
        default='benchmarks/workspace',
        help='Root workspace directory to create'
    )
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Load benchmarks
    benchmarks_yaml = Path('benchmarks/benchmarks.yaml')
    if not benchmarks_yaml.exists():
        print(f"Error: {benchmarks_yaml} not found")
        return 1
    
    benchmarks = load_benchmarks_yaml(benchmarks_yaml)
    print(f"Loaded {len(benchmarks)} benchmarks from {benchmarks_yaml}")
    
    # Create folders for each benchmark
    for benchmark in benchmarks:
        create_benchmark_folder(workspace, benchmark)
    
    # Write workspace README
    readme_path = workspace / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(f"""# Benchmarks Workspace

This folder contains organized benchmark cases and instructions.

## Structure
Each benchmark has its own folder with:
- `input/`: Model definition (JSON or CAD)
- `reference/`: Reference data (solver outputs, experimental, published results)
- `output/`: Pipeline and solver outputs
- `reports/`: Validation reports and metrics
- `metadata.json`: Benchmark metadata
- `SETUP.md`: Detailed setup instructions

## Benchmarks
{_list_benchmarks(benchmarks)}

## Quick Start
1. Pick a benchmark folder
2. Follow `SETUP.md` in that folder
3. Run the validation harness
4. Review `reports/accuracy_report.json`

## Adding a New Benchmark
1. Edit `benchmarks/benchmarks.yaml`
2. Re-run: `python3 tools/setup_benchmarks.py --workspace benchmarks/workspace`
3. Follow the generated `SETUP.md`

---
For metric definitions and acceptance thresholds, see `validation/accuracy_metrics.md`
""")
    print(f"\n✓ Workspace setup complete at {workspace}")
    print(f"✓ README: {readme_path}")
    
    return 0

def _list_benchmarks(benchmarks):
    """Format benchmark list for README."""
    lines = []
    for b in benchmarks:
        safe_name = b['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
        lines.append(f"- `{safe_name}/`: {b['name']} ({b.get('category', 'unknown')})")
    return '\n'.join(lines)

if __name__ == '__main__':
    exit(main())
