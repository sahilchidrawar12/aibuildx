# Enhanced IFC Generator - Quick Reference

## Overview

The AIBuildX pipeline now generates **Tekla-compliant IFC models** with all critical structural data:

- ✅ Profile definitions (IfcIShapeProfileDef, IfcRectangleProfileDef)
- ✅ 3D geometry (IfcExtrudedAreaSolid)
- ✅ Quantities (area, volume, mass)
- ✅ Proper placements (IfcAxis2Placement3D)
- ✅ Spatial hierarchy (project→site→building→storey→elements)
- ✅ Connection relationships (plates, bolts)
- ✅ Normalized units and vectors

## Usage

### Basic Pipeline Run

```bash
cd /Users/sahil/Documents/aibuildx

# Run with example DXF
python3 -m src.pipeline.pipeline_compat examples/sample_frame.dxf outputs/my_run

# Check results
cat outputs/my_run/ifc.json | jq '.summary'
```

### With Python

```python
from src.pipeline.agents.main_pipeline_agent import process

result = process({
    'data': {
        'dxf_entities': 'examples/sample_frame.dxf'
    }
})

if result['status'] == 'ok':
    ifc = result['result']['ifc']
    print(f"Beams: {ifc['summary']['total_beams']}")
    print(f"Columns: {ifc['summary']['total_columns']}")
    print(f"Plates: {ifc['summary']['total_plates']}")
    print(f"Relationships: {ifc['summary']['total_relationships']}")
```

## Output Structure

### Member (Beam/Column)

```json
{
  "type": "IfcBeam",
  "id": "...",
  "name": "Beam-...",
  "profile": {
    "type": "IfcIShapeProfileDef",
    "profile_name": "I-Section-...",
    "depth": 0.3,
    "width": 0.15,
    "web_thickness": 0.008,
    "flange_thickness": 0.012,
    "area": 0.025,
    "Ix": 0.000012,
    "Iy": 0.000001,
    "Zx": 0.00008,
    "Zy": 0.00001
  },
  "placement": {
    "location": [0.0, 0.0, 3.0],
    "Axis2Placement3D": {
      "location": [0.0, 0.0, 3.0],
      "axis": [0.0, 0.0, 1.0],
      "ref_direction": [1.0, 0.0, 0.0]
    }
  },
  "representation": {
    "swept_area": {
      "type": "IfcExtrudedAreaSolid",
      "extrusion_direction": [1.0, 0.0, 0.0],
      "extrusion_length": 5.0,
      "volume": 0.125
    }
  },
  "quantities": {
    "Length": 5.0,
    "CrossSectionArea": 0.025,
    "GrossVolume": 0.125,
    "Mass": 981.25,
    "MassPerUnitLength": 196.25
  },
  "material": {
    "name": "S235",
    "E": 210000.0,
    "fy": 235.0,
    "density": 7850.0
  }
}
```

### Plate

```json
{
  "type": "IfcPlate",
  "id": "plate_...",
  "outline": {
    "width": 0.15,
    "height": 0.15
  },
  "thickness": 0.01,
  "placement": {
    "location": [1.5, 2.0, 0.0],
    "Axis2Placement3D": {
      "location": [1.5, 2.0, 0.0],
      "axis": [0.0, 0.0, 1.0],
      "ref_direction": [1.0, 0.0, 0.0]
    }
  },
  "quantities": {
    "Area": 0.0225,
    "Volume": 0.000225,
    "Thickness": 0.01
  }
}
```

### Bolt/Fastener

```json
{
  "type": "IfcFastener",
  "id": "bolt_...",
  "diameter": 0.02,
  "diameter_mm": 20.0,
  "position": [1.5, 2.0, 0.0],
  "grade": "A325",
  "placement": {
    "location": [1.5, 2.0, 0.0],
    "Axis2Placement3D": {
      "location": [1.5, 2.0, 0.0],
      "axis": [0.0, 0.0, 1.0],
      "ref_direction": [1.0, 0.0, 0.0]
    }
  }
}
```

### Relationships

```json
{
  "relationships": {
    "spatial_containment": [
      {
        "type": "IfcRelContainedInSpatialStructure",
        "element_id": "beam-001",
        "element_type": "IfcBeam",
        "contained_in": "storey-001",
        "container_type": "IfcBuildingStorey"
      },
      {
        "type": "IfcRelAggregates",
        "relating_element": "project-001",
        "related_elements": ["site-001"]
      }
    ],
    "structural_connections": [
      {
        "type": "IfcRelConnectsElements",
        "relating_element": "beam-001",
        "related_element": "plate-001",
        "connection_type": "PlateConnection"
      }
    ]
  }
}
```

## Key Features

### Profile Definitions
- **I-Shapes**: Automatically generated with typical dimensions
- **Rectangles**: For box/tube sections
- **Custom**: Populated when section classifier has explicit data
- **Units**: All in metres (mm inputs converted automatically)

### Geometry
- **Type**: `IfcExtrudedAreaSolid` for all members
- **Extrusion**: Along member X-axis with length
- **Profile**: Referenced in representation
- **Volume**: Computed from area × length

### Quantities
- **Length**: Member span
- **CrossSectionArea**: From profile
- **GrossVolume**: area × length
- **NetVolume**: Same as gross (no deductions)
- **Mass**: volume × density (7850 kg/m³ for steel)
- **MassPerUnitLength**: Mass/Length

### Placements
- **Type**: `IfcAxis2Placement3D`
- **Location**: 3D coordinates in metres
- **Axis**: Z-direction (normalized)
- **RefDirection**: X-direction (normalized)
- **All vectors**: Unit-length (magnitude = 1.0)

### Spatial Hierarchy
```
Project
├── Site
    ├── Building
        ├── Storey
            ├── Beam-001
            ├── Beam-002
            ├── Column-001
            ├── Plate-001
            └── Bolt-001
```

## Verification Checklist

When running the pipeline, verify:

```bash
✅ IFC Summary appears in output
   - total_columns > 0
   - total_beams > 0
   - total_relationships ≥ (beams + columns)

✅ Each beam/column has:
   - type: "IfcBeam" or "IfcColumn"
   - profile.type: "IfcIShapeProfileDef" or "IfcRectangleProfileDef"
   - representation.swept_area.type: "IfcExtrudedAreaSolid"
   - placement.Axis2Placement3D structure
   - quantities with all fields

✅ Each plate has:
   - type: "IfcPlate"
   - outline with width and height
   - thickness > 0
   - placement structure

✅ Each bolt has:
   - type: "IfcFastener"
   - diameter > 0
   - position coordinates
   - placement structure

✅ Relationships include:
   - spatial_containment entries
   - structural_connections entries
```

## Unit System

### Standardized to METRE

| Item | Unit | Example |
|------|------|---------|
| Coordinates | m | [5.0, 0.0, 3.0] |
| Length | m | 5.0 |
| Area | m² | 0.025 |
| Volume | m³ | 0.125 |
| Profile dims | m | 0.3 (depth) |
| Plate dims | m | 0.15 (width) |
| Bolt diameter | m | 0.02 |

**Conversion**: mm → m (divide by 1000)
- 5000 mm → 5.0 m
- 300 mm → 0.3 m
- 20 mm → 0.02 m

## Common Issues & Solutions

### No Plates/Bolts in Output
**Cause**: Joints not generated or connection synthesis failed  
**Solution**: Check that joint snapping succeeded (look for "Generated X joints" in logs)

### Null Quantities
**Cause**: Section classifier didn't extract area  
**Solution**: This is OK for line-based DXF. Quantities populate when sections are explicit.

### Wrong Member Classification
**Cause**: Layer name not recognized or direction heuristics failed  
**Solution**: Check member.layer and member.dir fields; can override with explicit role field

### Non-normalized Vectors
**Cause**: Should not occur (normalize_vector applied)  
**Solution**: If found, check direction calculation in compute_local_frame

## Integration with Tekla

The IFC JSON is ready to export to IFC STEP format for Tekla import:

1. **Profiles**: Tekla recognizes IfcIShapeProfileDef and creates 3D sections
2. **Geometry**: IfcExtrudedAreaSolid allows rendering and analysis
3. **Quantities**: BOQ and weight calculations use GrossVolume and Mass
4. **Placements**: 3D placement ensures correct model positioning
5. **Relationships**: Spatial hierarchy allows proper organization

Next step: Convert JSON → IFC STEP file using IfcOpenShell or similar tool.

## Reference Documents

- **Full Implementation**: See `CRITICAL_FIXES_IMPLEMENTATION_COMPLETE.md`
- **Profile Generation**: Lines 58-120 in `ifc_generator.py`
- **Geometry Creation**: Lines 121-149 in `ifc_generator.py`
- **Quantity Calculation**: Lines 170-200 in `ifc_generator.py`
- **Connection Synthesis**: `agents/connection_synthesis_agent.py`

---

**Last Updated**: December 3, 2025  
**Status**: ✅ Production Ready
