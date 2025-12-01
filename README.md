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

Validation and developer notes
------------------------------

- Quick IFC sanity check (requires `ifcopenshell`):

```bash
# open IFC and print counts of common entities
PYTHONPATH=. python3 - <<'PY'
import ifcopenshell
model = ifcopenshell.open('outputs/model.ifc')
print('Products:', len(model.by_type('IfcProduct')))
print('BuildingElementProxy:', len(model.by_type('IfcBuildingElementProxy')))
PY
```

- Run the pipeline in a clean output folder and inspect produced files:

```bash
rm -rf outputs && mkdir outputs
PYTHONPATH=. python3 scripts/run_pipeline.py --input examples/sample_input.json --out_dir outputs
ls -la outputs
```

- Developer tips:
	- Use `PYTHONPATH=.` when running scripts from the repository root so the `src` package imports correctly.
	- To retrain the tiny synthetic ML models used in examples, run `PYTHONPATH=. python3 scripts/train_models.py`.

Changelog
---------

See `CHANGELOG.md` for release notes and high-level changes in this repository.
