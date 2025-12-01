AIBuildX — Modular Pipeline Overview

This repository contains a modular refactor of a large monolithic pipeline originally
implemented in `src/pipeline/pipeline_v2.py`.

Goals
- Break the monolith into focused modules (geometry, sections, materials, loads,
  compliance, agents, support, utils) so each responsibility is clear.
- Provide a backwards-compatible shim so existing scripts that import names from
  `pipeline_v2` continue to work while the codebase migrates.

Layout (key packages)
- `src/pipeline/geometry/` — Coordinate systems, rotation matrices, curved member
  handling, camber and skew geometry utilities.
- `src/pipeline/sections/` — Advanced section builders and property calculators.
- `src/pipeline/materials/` — `databases.py`, `material_selector.py`, `coating.py`.
- `src/pipeline/loads/` — LoadCombinationAnalyzer, WindLoadAnalyzer, SeismicLoadAnalyzer,
  PDeltaAnalyzer, InfluenceLineAnalyzer.
- `src/pipeline/compliance/` — `aisc360.py`, `aisc341.py` compliance checkers.
- `src/pipeline/agents/` — Lightweight agent modules (miner, engineer, optimizer, etc.).
- `src/pipeline/support/` — Small helpers: caching, parallel helper, spatial index,
  validators, anomaly detection, and more.
- `src/pipeline/utils/` — small geometry helpers and logger.

Backwards compatibility
- `src/pipeline/pipeline_compat.py` is a compact shim that re-exports selected
  classes and functions from the modular packages under names used in the original
  monolith.
- `src/pipeline/pipeline_v2.py` has been patched with a non-destructive compatibility
  block at the end of the file that sets missing top-level names from
  `pipeline_compat` so older imports still function.

How to use
- New code should import from the modular packages directly, e.g.:

  ```py
  from src.pipeline.loads import LoadCombinationAnalyzer
  from src.pipeline.materials import MaterialSelector
  from src.pipeline.compliance import AISC360Checker
  from src.pipeline import agents
  ```

- For legacy code that imports from `src.pipeline.pipeline_v2`, the compatibility
  shim will provide common names. Alternatively, import the shim directly:

  ```py
  from src.pipeline.pipeline_compat import recommend_material_for_section, list_agents
  ```

Running tests
- A virtual environment is configured at `.venv/` for reproducible tests.
- To run the test suite (from repository root):

  ```bash
  /Users/sahil/Documents/aibuildx/.venv/bin/python -m pytest -q
  ```

- Or, using the active Python interpreter for your environment, run:

  ```bash
  python3 -m pytest -q
  ```

Developer notes
- The compatibility shim is intentionally conservative: it uses `globals().setdefault`
  so it will not overwrite the original definitions in `pipeline_v2.py`.
- New modules are lightweight and intended to be expanded with production logic where
  necessary; many of the agent modules are scaffolds for integration with external
  systems (CNC exporter, IFC builder, clash detection, etc.).

Contact
- If you want me to continue the migration (replace more monolith functions with
  delegated calls to the modules or create a full rewrite of `pipeline_v2.py`),
  say what components to prioritize and I'll proceed.

Migration checklist (recommended next steps)

1. Run the test-suite in the workspace venv to verify no regressions:

```bash
/Users/sahil/Documents/aibuildx/.venv/bin/python -m pytest -q
```

2. Turn on `MIGRATE_COMMON_UTILS` and `MIGRATE_AGENT_ORCHESTRATION` toggles in
  `src/pipeline/pipeline_v2.py` to exercise modular implementations.

3. Gradually replace agent internals with production implementations while
  keeping the compatibility shim active. Prefer adding small unit tests for
  each agent before changing behavior.

4. When ready, prepare a PR that documents the migration with the following
  items:
  - Summary of files moved/created
  - Tests added/updated and test results
  - Migration toggles and recommended timeline for removal of the shim

5. After merge, mark the compatibility shim for removal in a separate follow-up
  PR (providing a deprecation timeline).
