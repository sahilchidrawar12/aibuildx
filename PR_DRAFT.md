PR Draft: Modularize pipeline_v2 into packages and add compatibility shim

Summary

This PR splits the large monolithic `src/pipeline/pipeline_v2.py` file into focused modules under `src/pipeline/`:

- geometry/
- sections/
- materials/
- catalogs/
- loads/
- compliance/
- agents/
- support/
- utils/

A compatibility shim `src/pipeline/pipeline_compat.py` was added and `pipeline_v2.py` was updated with non-destructive `globals().setdefault` and toggleable migration overrides. The aim is to allow incremental migration without breaking existing imports.

Key changes

- Moved or created ~40 new files under `src/pipeline/*` implementing discrete responsibilities.
- Implemented `main_pipeline_agent` to orchestrate the pipeline using modular functions.
- Added `run_pipeline` and `Pipeline.run_from_dxf_entities` wrappers in `pipeline_compat.py`.
- Added `MIGRATE_COMMON_UTILS` and `MIGRATE_AGENT_ORCHESTRATION` toggles to `pipeline_v2.py`.
- Added README updates: `README_v2.md` and `README_MODULAR.md` (migration notes and checklists).

Tests

- Ran full test suite in workspace venv: `27 passed, 1 skipped`.

Migration notes

- These changes are backwards compatible by default. Consumers can keep importing from
  `src.pipeline.pipeline_v2` while gradually switching to the modular APIs:
  - `from src.pipeline.materials import MaterialSelector`
  - `from src.pipeline.agents import MainPipelineAgent`

Follow-ups

- Refactor/flesh out remaining agent implementations with production logic.
- Add unit tests for the new agent modules.
- Remove the compatibility shim after migration completion (propose timeline).

Suggested commit message

"Modularize pipeline_v2 into packages; add compatibility shim and agent orchestrator. Tests: 27 passed, 1 skipped."

Reviewer notes

- Focus review on compatibility shims and the toggles behavior in `pipeline_v2.py`.
- Verify that optional dependencies (ifcopenshell, trimesh) are still optional and do not block imports.
