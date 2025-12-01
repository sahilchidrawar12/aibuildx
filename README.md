# AI Structural Steel Pipeline (Prototype)

This repository contains a minimal, production-oriented prototype of a multi-agent structural steel pipeline. It demonstrates 17 agents from geometry mining to a correction loop, using Python, `ezdxf`, and `ifcopenshell`.

Quick start

1. Create and activate a venv (macOS/zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Generate sample DXF and run the pipeline:

```bash
python3 scripts/generate_sample_dxf.py --out examples/sample_frame.dxf
PYTHONPATH=. python3 scripts/run_pipeline.py --input examples/sample_input.json --out_dir outputs
```

3. Train placeholder ML models (optional):

```bash
PYTHONPATH=. python3 scripts/train_models.py
```

4. Export CNC CSV directly:

```bash
PYTHONPATH=. python3 scripts/export_cnc.py examples/sample_input.json
```

Notes

- `ifcopenshell` may require platform-specific installation steps (see https://ifcopenshell.org/). If unavailable, the pipeline falls back to JSON-only IFC placeholders.
- The included ML models are synthetic placeholders. Replace with domain datasets for production.
