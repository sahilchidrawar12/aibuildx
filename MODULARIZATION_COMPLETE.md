---
title: AIBuildX Modularization - Complete File Structure
description: Comprehensive breakdown of all modular files created from pipeline_v2.py
---

# AIBuildX Complete Modularization

## Overview

The original `pipeline_v2.py` (2,872 lines) has been systematically decomposed into **organized modular files** across 12 categories, providing:

- **Better maintainability**: Each class/function in its own file
- **Easier testing**: Isolated modules can be tested independently  
- **Improved reusability**: Import specific modules as needed
- **Clear organization**: Feature categories map to directory structure
- **Comprehensive documentation**: Each file fully documented

## Directory Structure

```
/src/pipeline/
│
├── geometry/               # FEATURE 1: Coordinate Systems & Geometry
│   ├── __init__.py
│   ├── coordinate_system.py        ✓ CoordinateSystemManager
│   ├── rotation_matrix.py          ✓ RotationMatrix3D
│   ├── curved_member.py            ✓ CurvedMemberHandler
│   ├── camber_calculator.py        ✓ CamberCalculator
│   ├── skew_cut.py                 ✓ SkewCutGeometry
│   └── eccentricity.py             ✓ EccentricityResolver
│
├── sections/               # FEATURE 2: Advanced Section Properties
│   ├── __init__.py
│   ├── compound_section.py         ✓ CompoundSectionBuilder
│   ├── web_opening.py              ✓ WebOpeningHandler
│   ├── torsional.py                ✓ TorsionalPropertyCalculator
│   └── plastic_analysis.py         ✓ PlasticAnalysisProperties
│
├── materials/              # FEATURE 5: Material Specifications
│   ├── __init__.py
│   ├── databases.py                ✓ Material & Bolt Databases
│   ├── material_selector.py        (To create)
│   └── coating.py                  (To create)
│
├── loads/                  # FEATURE 6: Load Analysis Engine
│   ├── __init__.py
│   ├── load_combinations.py        (To create)
│   ├── wind_loads.py               (To create)
│   ├── seismic.py                  (To create)
│   ├── pdelta.py                   (To create)
│   └── influence_lines.py          (To create)
│
├── compliance/             # FEATURE 7: Code Compliance Checkers
│   ├── __init__.py
│   ├── aisc360.py                  (To create)
│   └── aisc341.py                  (To create)
│
├── catalogs/               # Connection, Weld, Section Catalogs
│   ├── __init__.py
│   ├── connection_types.py         (To create)
│   ├── weld_types.py               (To create)
│   └── section_catalog.py          ✓ SECTION_CATALOG, EUROCODE_CATALOG
│
├── utils/                  # Utility Functions
│   ├── __init__.py
│   ├── geometry_utils.py           (To create)
│   └── section_selector.py         (To create)
│
├── agents/                 # 24 Agent Functions (Pipeline Stages)
│   ├── __init__.py
│   ├── miner.py                    (To create)
│   ├── engineer.py                 (To create)
│   ├── load_resolver.py            (To create)
│   ├── stability.py                (To create)
│   ├── optimizer.py                (To create)
│   ├── connection_designer.py      (To create)
│   ├── fabrication.py              (To create)
│   ├── erection.py                 (To create)
│   ├── analysis.py                 (To create)
│   ├── validator.py                (To create)
│   ├── ifc_builder.py              (To create)
│   ├── clash_detection.py          (To create)
│   ├── clash_advanced.py           (To create)
│   ├── risk.py                     (To create)
│   ├── reporter.py                 (To create)
│   ├── cnc_exporter.py             (To create)
│   ├── dstv_exporter.py            (To create)
│   ├── correction_loop.py          (To create)
│   └── main_pipeline.py            (To create - Pipeline class)
│
├── errors/                 # FEATURE 16: Error Handling & Robustness
│   ├── __init__.py
│   ├── validators.py               (To create)
│   ├── fallback.py                 (To create)
│   ├── logger.py                   (To create)
│   └── warnings.py                 (To create)
│
├── performance/            # FEATURE 17: Performance Optimization
│   ├── __init__.py
│   ├── parallel_processor.py       (To create)
│   ├── spatial_index.py            (To create)
│   └── cache.py                    (To create)
│
├── ml/                     # FEATURE 19: ML Enhancements
│   ├── __init__.py
│   ├── connection_classifier.py    (To create)
│   ├── load_predictor.py           (To create)
│   └── anomaly_detector.py         (To create)
│
└── regulatory/             # FEATURE 20: Regulatory Compliance
    ├── __init__.py
    ├── ibc_checker.py              (To create)
    ├── fire_rating.py              (To create)
    ├── ada_checker.py              (To create)
    ├── carbon_calc.py              (To create)
    ├── osha_gen.py                 (To create)
    └── compliance_module.py        (To create)
```

## Files Created So Far (✓ Status)

### Geometry Module (6 classes)
- ✓ **coordinate_system.py** - WCS/UCS/Tekla coordinate transformations
- ✓ **rotation_matrix.py** - 3D rotation matrices and transformations
- ✓ **curved_member.py** - Arc, spline, and polyline handling
- ✓ **camber_calculator.py** - Deflection compensation for fabrication
- ✓ **skew_cut.py** - Bevel angles and cope calculations
- ✓ **eccentricity.py** - Work point vs. centerline offsets

### Sections Module (4 classes)
- ✓ **compound_section.py** - Built-up I-beams, box sections, composite sections
- ✓ **web_opening.py** - Castellated and cellular beams
- ✓ **torsional.py** - J and Cw torsional properties, LTB analysis
- ✓ **plastic_analysis.py** - Plastic section moduli and moment capacity

### Materials Module (1 created, 2 pending)
- ✓ **databases.py** - MATERIAL_DATABASE, BOLT_SPECIFICATIONS, BOLT_STRENGTH
- ⏳ **material_selector.py** - Material grade optimization
- ⏳ **coating.py** - Paint and galvanizing specifications

### Catalogs Module (1 created, 2 pending)
- ✓ **section_catalog.py** - SECTION_CATALOG (19 AISC + 10 Eurocode sections), SECTION_GEOM
- ⏳ **connection_types.py** - CONNECTION_TYPES catalog (6 categories, 20+ subtypes)
- ⏳ **weld_types.py** - WELD_TYPES catalog (fillet, butt, plug, slot, spot, seam, advanced)

## Features Mapping

| Feature | Module | Status |
|---------|--------|--------|
| 1. Geometry & Coordinates | geometry/ | ✓ Complete (6 classes) |
| 2. Advanced Sections | sections/ | ✓ Complete (4 classes) |
| 3. Connection Design | agents/connection_designer + catalogs/connection_types | ⏳ Partial |
| 4. Weld Design | catalogs/weld_types + agents/fabrication | ⏳ Partial |
| 5. Material Specs | materials/ | ✓ Database, 2 classes pending |
| 6. Load Analysis | loads/ | ⏳ All pending (5 classes) |
| 7. Code Compliance | compliance/ | ⏳ All pending (2 classes) |
| 8. Fabrication | agents/fabrication | ⏳ Pending |
| 9. Clash Detection | agents/clash_detection + agents/clash_advanced | ⏳ Pending |
| 10. IFC Export | agents/ifc_builder | ⏳ Pending |
| 11. CNC/DSTV Export | agents/cnc_exporter + agents/dstv_exporter | ⏳ Pending |
| 12. Tekla Integration | geometry/coordinate_system | ✓ Foundation |
| 13. Advanced FEA | agents/analysis | ⏳ Pending |
| 14. QA/Documentation | agents/reporter | ⏳ Pending |
| 15. Interoperability | agents/ifc_builder + cnc/dstv | ⏳ Pending |
| 16. Error Handling | errors/ | ⏳ All pending (4 classes) |
| 17. Performance | performance/ | ⏳ All pending (3 classes) |
| 18. Visualization | catalogs/section_catalog + others | ✓ Data ready |
| 19. ML Enhancements | ml/ | ⏳ All pending (3 classes) |
| 20. Regulatory | regulatory/ | ⏳ All pending (6 classes) |

**Total Classes Created: 13 (out of 38+)**
**Total Files Created: 13 (out of 70+)**

## How to Import

```python
# Import from geometry module
from src.pipeline.geometry import CoordinateSystemManager, RotationMatrix3D

# Import from sections module
from src.pipeline.sections import CompoundSectionBuilder, PlasticAnalysisProperties

# Import from materials module
from src.pipeline.materials.databases import MATERIAL_DATABASE, BOLT_SPECIFICATIONS

# Import from catalogs module
from src.pipeline.catalogs.section_catalog import SECTION_CATALOG, get_section_by_name

# Import specific classes
from src.pipeline.geometry.curved_member import CurvedMemberHandler
from src.pipeline.sections.torsional import TorsionalPropertyCalculator
```

## Next Steps (Priority Order)

1. **Complete Materials Module** (2 files)
   - material_selector.py (MaterialSelector)
   - coating.py (CoatingSpecifier)

2. **Create Catalogs Module** (2 files)
   - connection_types.py (CONNECTION_TYPES)
   - weld_types.py (WELD_TYPES)

3. **Create Loads Module** (5 files)
   - load_combinations.py
   - wind_loads.py
   - seismic.py
   - pdelta.py
   - influence_lines.py

4. **Create Compliance Module** (2 files)
   - aisc360.py
   - aisc341.py

5. **Create Agent Files** (19+ files)
   - Each agent becomes a separate module

6. **Create Error/Performance/ML/Regulatory Modules** (16 files total)

7. **Create Utility Module** (2 files)
   - geometry_utils.py
   - section_selector.py

8. **Update main pipeline_v2.py**
   - Add imports from all modules
   - Keep Pipeline class orchestration
   - Preserve agent pipeline execution

## Benefits of This Structure

✅ **Modular Architecture**: Each feature in its own module
✅ **Easy Testing**: Test individual classes independently
✅ **Scalability**: Add new modules without touching core
✅ **Maintainability**: Clear ownership of each feature
✅ **Documentation**: Each file self-documented
✅ **Reusability**: Import specific modules in other projects
✅ **Version Control**: Easier to track changes per feature
✅ **Collaboration**: Multiple developers can work on different modules simultaneously

## Statistics

- **Total Classes**: 38+ (20 feature categories)
- **Total Functions**: 100+ utility functions
- **Total Lines of Code**: ~2,900 (from original pipeline_v2.py)
- **Modules Planned**: 12
- **Subdirectories**: 12
- **Files Target**: 70+

## Execution Flow

The Pipeline class (in agents/main_pipeline.py) orchestrates all agents in sequence:

```
miner → engineer → load_path_resolver → stability_agent → optimizer_agent →
connection_designer → fabrication_detailing → fabrication_standards → 
erection_planner → safety_compliance → analysis_model_generator → 
validator_agent → builder_ifc → (parallel) clash detection → risk_detector →
reporter_agent → cnc_exporter → dstv_exporter → correction_loop
```

Each agent is a pure function taking input JSON and producing output JSON.

---

**Last Updated**: December 2025
**Status**: 13/70+ files created (18% complete)
**Recommendation**: Continue with remaining 57 files following same pattern
