# Benchmarks Workspace

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
- `burj_khalifa_dubai_-_simplified_model/`: Burj Khalifa (Dubai) - Simplified Model (super-tall)
- `shanghai_tower_china_-_simplified_model/`: Shanghai Tower (China) - Simplified Model (super-tall)
- `taipei_101_taiwan_-_simplified_model/`: Taipei 101 (Taiwan) - Simplified Model (super-tall)
- `one_world_trade_center_new_york_-_simplified_model/`: One World Trade Center (New York) - Simplified Model (super-tall)
- `petronas_towers_kuala_lumpur_-_simplified_model/`: Petronas Towers (Kuala Lumpur) - Simplified Model (super-tall)
- `akashi_kaikyo_bridge_japan_-_main_span_section/`: Akashi Kaikyo Bridge (Japan) - Main Span Section (long-span-bridge)
- `beijing_national_stadium_bird's_nest_-_roof_section/`: Beijing National Stadium (Bird's Nest) - Roof Section (large-roof)
- `simple_10-story_office_building_asce_benchmark/`: Simple 10-Story Office Building (ASCE Benchmark) (benchmark-reference)
- `cantilever_beam_with_distributed_load_mechanics_validation/`: Cantilever Beam with Distributed Load (Mechanics Validation) (validation-basic)
- `wind_tunnel_pressure_distribution_on_high-rise_simplified_aero_coupling/`: Wind Tunnel Pressure Distribution on High-Rise (Simplified Aero Coupling) (wind-aero)

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
