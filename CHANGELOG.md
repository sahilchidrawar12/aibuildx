# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0] - 2025-12-01
### Added
- Consolidated multi-agent pipeline implementation (`src/pipeline/pipeline_v2.py`) with IFC exporter, ML hooks, clash detection, CNC CSV exporter, and correction loop.
- Sample DXF generator and pipeline runner scripts in `scripts/`.
- Synthetic ML training helpers and models (`src/pipeline/ml_models.py`, `scripts/train_models.py`).
- Tests for pipeline, IFC export, and CNC export (`tests/`).
- GitHub Actions CI workflow (`.github/workflows/ci.yml`).

### Notes
- IFC geometry generation uses `ifcopenshell` when available; otherwise the pipeline produces JSON-friendly placeholders.
- ML models are synthetic placeholders; replace with domain-specific datasets and models for production.
