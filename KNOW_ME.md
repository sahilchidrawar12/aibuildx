**Project Overview**: This repository implements a 2D→3D structural engineering pipeline that processes geometry and metadata and generates Tekla-ready enriched data (IFC-like JSON and a Tekla plugin scaffold). The code is agent-based and modular under `src/pipeline/`.

- **Key modules**: `src/pipeline/main_pipeline_agent.py` (orchestrator), `src/pipeline/geometry_agent.py`, `src/pipeline/profile_db.py`, `src/pipeline/connection_capacity.py`, `src/pipeline/ifc_generator.py`, `src/pipeline/auto_repair_engine.py`, and supporting helpers.
- **Outputs**: `outputs/final.json` (aggregated pipeline results), `outputs/ifc.json` (IFC-like export). A Tekla plugin scaffold lives in `tekla_integration/`.

**Quickstart — Developer (macOS / Linux)**

1) Create a virtualenv and install minimal test tooling (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest pytest-cov flake8
```

2) Run the tests quickly (may require optional heavy deps if tests import `ifcopenshell`/`ezdxf`):

```bash
pytest -q --maxfail=1 --disable-warnings --cov=src
```

3) Run a quick pipeline demo (calls the orchestrator) from repo root:

```bash
python3 - <<'PY'
import sys
sys.path.insert(0,'.')
from src.pipeline.agents import main_pipeline_agent
payload = {
    'members': [
        {'id':'m1','start':[0,0,0],'end':[6000,0,0],'profile':'IPE200'},
        {'id':'m2','start':[0,0,0],'end':[0,4000,0],'profile':'IPE160'}
    ],
    'connections': [],
}
out = main_pipeline_agent.process(payload)
print(out['status'])
PY
```

4) Generate an expanded section catalog (if needed):

```bash
python3 tools/generate_section_catalog.py --seed data/section_catalog.csv --out data/section_catalog_full.csv --mult 5
```

**Tekla plugin build (Windows only)**

- Requirements: Windows, Visual Studio/MSBuild, Tekla Structures installation (for Tekla assemblies). See `tekla_integration/README_Tekla.md`.
- Build and package with PowerShell from `tekla_integration`:

```powershell
.\package_plugin.ps1 -Configuration Release -OutputZip .\TeklaPlugin.zip
```

**Notes & Caveats**

- The engineering checks (bolt, bearing, block-shear, weld heuristics, stability) are conservative heuristics suitable for prototyping and early validation. For design or code compliance, verify results with a licensed engineer and certified design software.
- The Tekla C# project is scaffolded and cannot be compiled in this macOS environment; you must compile and validate in Windows with Tekla.
- Some tests may import heavy external packages (e.g., `ifcopenshell`, `trimesh`). If such tests fail locally, install those optional dependencies or run targeted tests.

**Where to look next**

- `src/pipeline/connection_capacity.py` — bolt, bearing, block shear and end-plate helpers.
- `src/pipeline/profile_db.py` and `data/section_catalog_full.csv` — section lookup and fuzzy mapper.
- `tekla_integration/` — C# scaffolding and packaging helper.

If you want, I can now:
- run the full test suite here (I will attempt to install test tooling and run `pytest`),
- run the pipeline demo and save outputs under `outputs/demo/`, or
- prepare a PR summary and suggested reviewers.

Tell me which of those you want next.
