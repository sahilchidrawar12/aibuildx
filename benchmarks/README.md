Benchmarks and Validation
=========================

This folder contains benchmark definitions and instructions to run validation cases used to measure accuracy of the pipeline versus reference models.

Purpose
- Provide a reproducible set of benchmark cases representing a range of structural complexity:
  - Very tall buildings (super-tall / mega-tall)
  - Long-span bridges and cable-stayed / suspension systems
  - Large stadium roofs and large membrane/shell structures
  - Complex mixed structures (towers with outriggers, mega trusses)

Contents
- `benchmarks.yaml`: canonical list of benchmark cases and metadata (source, expected reference files, notes).
- `setup_benchmarks.py`: helper script to prepare a local benchmarks workspace and provide download instructions for public data.
- `metrics.md` (in repo root `validation/accuracy_metrics.md`): defines metrics and comparison methodology.

How to use
1. Review `benchmarks.yaml` to identify target cases and reference sources.
2. Run `python3 tools/setup_benchmarks.py --workspace benchmarks/workspace` to create folders and instructions.
3. Place downloaded reference files (FEA models, experimental results, wind-tunnel pressure maps) into `benchmarks/workspace/<case>/reference/` per the generated README.
4. Implement exporters from this repo to your chosen solver (OpenSees / CalculiX / Abaqus) and run comparisons as described in `validation/accuracy_metrics.md`.

Licensing and data
- Many high-fidelity benchmark datasets are proprietary. Where possible, we reference open/public datasets (research papers, ASCE/other published benchmarks). Users must obtain and store proprietary datasets locally; the helper script above documents where to place them.

Contact
- For help integrating your solver or adding a benchmark, open an issue or request guidance in the repo.
