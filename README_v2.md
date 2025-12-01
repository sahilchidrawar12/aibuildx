# AI Structural Steel Pipeline (Production-Grade v1.0)

A comprehensive, production-oriented 17-agent structural steel pipeline that converts raw 2D/3D input (DXF/IFC) into LOD500 Tekla/Revit-ready IFC models with:
- Optimized sections (cost-driven and code-compliant)
- Fabrication-ready details (copes, holes, bevels, welds, bolts)
- Clash-free structures (hard, soft, functional, and multi-discipline clash detection)
- Complete reports (BOM, CNC/DSTV files, erection plans, risk assessments)
- Iterative auto-correction loop (removes clashes, fixes errors, optimizes cost)

## The 17 Agents

1. **Miner** — Extract geometry from DXF/IFC  
2. **Engineer** — Standardize and classify members  
3. **Load Path Resolver** — Compute axial, bending, and shear loads  
4. **Stability Agent** — Check slenderness and buckling  
5. **Optimizer** — Select economical sections (cost DB aware)  
6. **Connection Designer** — Design bolted/welded joints  
7. **Fabrication Detailing** — Add copes, holes, bevels, stiffeners  
8. **Fabrication Standards** — Validate and auto-correct plate/weld sizes  
9. **Erection Planner** — Assign assembly sequence  
10. **Safety Compliance** — Check OSHA/Eurocode guidelines  
11. **Analysis Model Generator** — Create FEA node/element model  
12. **Builder (IFC)** — Generate LOD500 IFC with extruded profiles and fasteners  
13. **Validator** — Check code compliance (capacity, bolt/weld, clearance)  
14. **Clasher (4 types)** — Hard, soft, functional, and MEP clash detection  
15. **Risk Detector** — Assign risk scores per member  
16. **Reporter** — Generate BOM, CNC, DSTV, and shop drawings  
17. **Correction Loop** — Iteratively fix errors (upsizes, nudges geometry, locks selections)

## Quick Start

### 1. Setup Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Full Pipeline

```bash
cd /Users/sahil/Documents/aibuildx
PYTHONPATH=. python3 scripts/run_pipeline.py --input examples/sample_input.json --out_dir outputs
```

Alternatively, for developers and backwards compatibility use the Python API wrapper:

```bash
python -c "from src.pipeline import pipeline_compat as pc; pc.run_pipeline('examples/sample_input.json', out_dir='outputs')"
```

Notes:
- `run_pipeline(input_data, out_dir=None)` accepts a path to `.json` (auto-loaded), `.dxf` or `.ifc` files, or an in-memory list/dict containing `members`.
- When `out_dir` is provided the compatibility layer will write `result.json` and selected outputs like `cnc.json`, `dstv.json`, `reporter.json`, and `final.json` when available.

### 3. Train ML Models (Optional)

```bash
PYTHONPATH=. python3 scripts/train_models.py
```

Trains placeholder DecisionTree models and saves to `models/`.

### 4. Export CNC/DSTV

```bash
PYTHONPATH=. python3 scripts/export_cnc.py examples/sample_input.json
```

Outputs `outputs/cnc.csv` (master) and `outputs/dstv_parts/` (per-member DSTV-like files).

### 5. Run Tests

```bash
# Full test suite (requires pytest):
pytest -q tests/test_all_agents.py

# Manual smoke test (no external deps):
PYTHONPATH=. python3 scripts/run_pipeline.py --input examples/sample_input.json --out_dir outputs
```

## Features

### Clash Detection (4 Types)

1. **Hard Clashes** — Beam–Beam, Beam–Column, Plate–Bolt overlaps  
2. **Soft Clashes** — Insufficient clearance (<50mm by default)  
3. **Functional Clashes** — Misalignment, hole mismatch, orientation errors  
4. **MEP Clashes** — Steel vs. duct/pipe/cable interference  

### Cost Database

Edit `src/pipeline/cost_db.yaml` to customize section prices, bolt costs, weld costs, and labor rates. The optimizer uses this to minimize total cost.

### Connection Types

- Beam-to-Column: shear tabs, end plates, moment connections
- Beam-to-Beam: splices (bolted/welded)
- Column-to-Base: base plates, anchor bolts
- Bracing: gusset plates, tension rods
- Truss: bolted node plates, welded K/N/X/T joints
- Secondary: purlins, girts, sag rods

### Weld Types

Fillet, Butt, Plug, Slot, Spot, Seam, CJP, PJP, Groove, Bevel, U, V, J-groove, Edge, Corner.

### IFC LOD500 Features

- Accurate profile definitions (`IfcIShapeProfileDef`, `IfcRectangleProfileDef`, `IfcCircleProfileDef`)
- `IfcExtrudedAreaSolid` swept solids with correct placement and orientation
- `IfcFastener` bolts linked to connections and members
- Rich PSETs: `Pset_AIBuildX`, `Pset_Connection`, `Pset_Bolt`

### CNC/DSTV Output

- Master CSV: `outputs/cnc.csv`
- Per-part DSTV: `outputs/dstv_parts/*.dstv`
- Includes hole coordinates (local and global XYZ)
- Machine-ready format

## Output Files

```
outputs/
├── model.ifc                 # LOD500 IFC model
├── cnc.csv                   # Master CNC bill
├── dstv_parts/
│   ├── <id>.dstv             # Per-part DSTV file
│   └── dstv_index.csv        # DSTV index
├── analysis.json             # FEA model
├── clashes.json              # Clash report
├── validator.json            # Validation report
└── final.json                # Final corrected model
```

## Optional Dependencies

```bash
pip install numpy pandas ifcopenshell trimesh
```

- `numpy` — Faster distance calculations
- `ifcopenshell` — Real IFC export (vs JSON fallback)
- `trimesh` — Mesh-based clash detection
- `scikit-learn` — Better ML training

## Configuration

Edit `SECTION_CATALOG` in `src/pipeline/pipeline_v2.py` to add custom sections.  
Adjust load assumptions in `load_path_resolver()`.  
Tune safety margins in `validator_agent()`.

## Testing All 17 Agents

```bash
# Create venv and install:
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run smoke test (all agents):
PYTHONPATH=. python3 scripts/run_pipeline.py --input examples/sample_input.json --out_dir outputs

# Expected output summary:
# ✅ ALL 17 AGENTS COMPLETED SUCCESSFULLY!
# • Members processed: 2
# • Total structural weight: 120.0 kg
# • Estimated cost: $144.00
# • Validator errors: 2
# • Validator warnings: 1
# • Hard clashes detected: 0
# • Soft clashes (clearance): 2
# • Functional clashes: 0
# • Correction iterations: 2
```

## Migration Notes (Developer)

- Toggle migration of common utilities in `src/pipeline/pipeline_v2.py`:
	- `MIGRATE_COMMON_UTILS = True` — replace local geometry/sections/loads classes with modular implementations at import time.
	- `MIGRATE_COMMON_UTILS = False` — keep legacy in-file implementations.

- Toggle agent orchestration migration:
	- `MIGRATE_AGENT_ORCHESTRATION = True` — `Pipeline.run_from_dxf_entities` delegates to `src.pipeline.agents.main_pipeline_agent` and attaches agent outputs under `agents_orchestration`.
	- `MIGRATE_AGENT_ORCHESTRATION = False` — legacy orchestration retained.

- Run tests in the workspace virtualenv (recommended):

```bash
# activate venv
source .venv/bin/activate
# run full test suite
/Users/sahil/Documents/aibuildx/.venv/bin/python -m pytest -q
```

These toggles allow progressive migration with non-destructive compatibility.

## Performance

- 2 members: ~0.5s (pure Python)
- 100+ members: Install `numpy`/`trimesh` for faster clash detection

## Troubleshooting

- **No `ifcopenshell`?** Falls back to JSON IFC representation.
- **Slow clashes?** Install `numpy` and `trimesh`.
- **ML models?** Optional; pipeline runs without them.

---

**Version:** 1.0 (Production) | **All 17 Agents Implemented & Tested** | **December 2025**
