# COMPREHENSIVE CLASH DETECTION v2.0 - QUICK START GUIDE

## 🚀 5-Minute Setup

### Step 1: Import the System

```python
from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector
from src.pipeline.agents.comprehensive_clash_corrector_v2 import ComprehensiveClashCorrector
from src.pipeline.agents.main_pipeline_agent_enhanced import run_enhanced_pipeline
```

### Step 2: Prepare Your IFC Data

```python
ifc_data = {
    'members': [
        {'id': 'COL-1', 'start': [0, 0, 0], 'end': [0, 0, 5]},
        {'id': 'BM-1', 'start': [0, 0, 5], 'end': [5, 0, 5]}
    ],
    'joints': [],
    'plates': [
        {
            'id': 'BASE-1', 
            'position': [0, 0, 0],
            'members': ['COL-1'],
            'outline': {'width_mm': 400, 'height_mm': 400},
            'thickness_mm': 25,
            'material': 'A36'
        }
    ],
    'bolts': [
        {
            'id': 'B1', 
            'position': [0.1, 0.1, 0],
            'plate_id': 'BASE-1',
            'diameter_mm': 20,
            'material': 'A325'
        }
    ],
    'welds': [
        {
            'id': 'W1',
            'position': [0, 0, 0],
            'plate_id': 'BASE-1',
            'size_mm': 8,
            'penetration_mm': 6.4
        }
    ],
    'anchors': [
        {
            'id': 'A1',
            'position': [0.15, 0.15, -0.3],
            'plate_id': 'BASE-1',
            'diameter_mm': 25,
            'embedment_mm': 600
        }
    ],
    'foundation': {'elevation': -0.5, 'size_mm': 2000}
}
```

### Step 3: Run Clash Detection

```python
detector = ComprehensiveClashDetector()
clashes, summary = detector.detect_all_clashes(ifc_data)

print(f"Total clashes: {summary['total']}")
print(f"Critical: {summary['critical']}")
print(f"Major: {summary['major']}")
```

### Step 4: Apply Corrections

```python
corrector = ComprehensiveClashCorrector()
corrections, corr_summary = corrector.correct_all_clashes(clashes, ifc_data)

print(f"Corrected: {corr_summary['corrected']}")
print(f"Success rate: {corr_summary['corrected'] / corr_summary['total']:.1%}")
```

### Step 5: Full Pipeline Validation

```python
result = run_enhanced_pipeline(ifc_data, verbose=True)

print(f"Status: {result['status']}")
print(f"Recommendation: {result['validation_report']['recommendation']}")
```

---

## 📊 Understanding the Output

### Clash Object Structure

```python
Clash(
    clash_id='CLASH_000001',
    category=ClashCategory.BASE_PLATE_WRONG_ELEVATION,
    severity=ClashSeverity.CRITICAL,
    element_type='plate',
    element_id='BASE-1',
    description='Base plate at Z=0.5m, should be Z≈0m',
    current_value=0.5,
    expected_value=0.0,
    confidence_score=0.98
)
```

### Summary Dictionary

```python
summary = {
    'total': 11,
    'critical': 4,
    'major': 6,
    'moderate': 1,
    'minor': 0,
    'by_category': {
        'base_plate_wrong_elevation': 1,
        'base_plate_undersizing': 1,
        'bolt_edge_distance_too_small': 3,
        'weld_penetration_insufficient': 2,
        'plate_thickness_inadequate': 2,
        'connection_eccentricity_excessive': 2
    }
}
```

### Validation Report

```python
report = {
    'overall_status': 'PASSED',
    'initial_clashes': 15,
    'corrected_clashes': 12,
    'remaining_clashes': 3,
    'critical_remaining': 0,
    'geometry_valid': True,
    'welds_fasteners_valid': True,
    'anchorage_foundation_valid': True,
    'recommendation': '✓ STRUCTURE READY FOR PRODUCTION - All validations passed'
}
```

---

## 🔧 Common Operations

### Detect Only Specific Clash Types

```python
detector = ComprehensiveClashDetector()
clashes, summary = detector.detect_all_clashes(ifc_data)

# Filter for critical clashes only
critical_clashes = [c for c in clashes if c.severity.name == 'CRITICAL']

# Filter for base plate clashes
base_plate_clashes = [c for c in clashes if 'base_plate' in c.category.value]

# Filter by element type
plate_clashes = [c for c in clashes if c.element_type == 'plate']
```

### Manual Element Inspection

```python
# Find all bolts on a plate
plate_id = 'BASE-1'
plate_bolts = [b for b in ifc_data['bolts'] if b.get('plate_id') == plate_id]

# Check base plate properties
base_plates = [p for p in ifc_data['plates'] if 'base' in p.get('id', '').lower()]

# Inspect foundation setup
foundation = ifc_data.get('foundation', {})
print(f"Foundation elevation: {foundation.get('elevation')}m")
print(f"Foundation size: {foundation.get('size_mm')}mm")
```

### Export Results to JSON

```python
import json

# Export validation report
report = result['validation_report']
with open('validation_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

# Export clashes with details
clash_data = [{
    'id': c.clash_id,
    'category': c.category.value,
    'severity': c.severity.name,
    'description': c.description,
    'element': c.element_id,
    'confidence': c.confidence_score
} for c in clashes]

with open('clashes.json', 'w') as f:
    json.dump(clash_data, f, indent=2)
```

---

## ✅ Testing & Validation

### Run Unit Tests

```bash
cd /Users/sahil/Documents/aibuildx
python src/pipeline/agents/test_comprehensive_clash_v2.py
```

### Test Individual Scenarios

```python
from test_comprehensive_clash_v2 import ComplexStructureGenerator

# Create 5-story structure
ifc = ComplexStructureGenerator.create_multi_story_frame()
result = run_enhanced_pipeline(ifc)

# Create structure with intentional clashes
ifc_with_clashes = ComplexStructureGenerator.create_structure_with_intentional_clashes()
result = run_enhanced_pipeline(ifc_with_clashes)
```

---

## 📋 Clash Categories Quick Reference

| Category | Count | Examples |
|----------|-------|----------|
| 3D Geometry | 5 | Intersections, overlaps, penetration |
| Plate-Member Alignment | 6 | Misalignment, offset, rotation |
| Base Plate | 8 | Elevation, sizing, anchoring |
| Welds | 7 | Missing, size, penetration |
| Bolt Spacing | 7 | Edge distance, spacing, diameter |
| Member Geometry | 5 | Span, slenderness, bracing |
| Connection Alignment | 6 | Eccentricity, moment, offset |
| Anchorage | 8 | Embedment, spacing, pullout |
| Plate Properties | 6 | Thickness, bearing, material |
| Bolt Properties | 5 | Diameter, material, capacity |
| Structural Logic | 4 | Orphans, floating elements |
| **TOTAL** | **35+** | **All clash types covered** |

---

## 🎯 Severity Levels Explained

| Severity | Symbol | Meaning | Action |
|----------|--------|---------|--------|
| CRITICAL | 🔴 | Fails structural analysis | Fix immediately |
| MAJOR | 🟠 | Needs correction | Fix before submission |
| MODERATE | 🟡 | Should fix | Fix if possible |
| MINOR | 🟢 | Can ignore | Document rationale |

---

## 📈 Performance Tips

### Optimize for Speed

```python
# Disable verbose logging
result = run_enhanced_pipeline(ifc_data, verbose=False)

# Process only critical clashes
detector = ComprehensiveClashDetector()
clashes, summary = detector.detect_all_clashes(ifc_data)
critical_only = [c for c in clashes if c.severity.value == 1]  # CRITICAL only
```

### Optimize for Accuracy

```python
# Use full pipeline
result = run_enhanced_pipeline(ifc_data, verbose=True)

# Enable cascading clash detection (automatic)
# System automatically checks for cascading issues

# Re-validate after corrections
clashes_after = detector.detect_all_clashes(result['final_ifc'])
```

---

## 🐛 Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run pipeline with debug output
result = run_enhanced_pipeline(ifc_data, verbose=True)
```

### Inspect Pipeline Stages

```python
result = run_enhanced_pipeline(ifc_data)

for stage_name, stage_data in result['stages'].items():
    print(f"\n{stage_name}:")
    print(f"  Status: {stage_data['status']}")
    for key, value in stage_data.items():
        if key != 'status':
            print(f"  {key}: {value}")
```

### Validate IFC Structure

```python
def validate_ifc(ifc_data):
    required = ['members', 'joints', 'plates', 'bolts', 'welds', 'anchors', 'foundation']
    
    for key in required:
        if key not in ifc_data:
            print(f"✗ Missing: {key}")
        else:
            print(f"✓ {key}: {len(ifc_data[key])} items")
    
    # Check coordinate validity
    for member in ifc_data.get('members', []):
        start = member.get('start')
        end = member.get('end')
        if not start or not end:
            print(f"✗ Member {member['id']} missing coordinates")
        elif len(start) != 3 or len(end) != 3:
            print(f"✗ Member {member['id']} has invalid coordinate format")

validate_ifc(ifc_data)
```

---

## 🔗 Integration Examples

### With Existing Pipeline

```python
# Existing pipeline stages 1-6 (DXF import, member extraction, etc.)
ifc_data = existing_pipeline(dwg_file)

# Add clash detection (new stages 7.1-7.8)
result = run_enhanced_pipeline(ifc_data)

# Export to TEKLA/IFC
if result['status'] == 'PASSED':
    export_to_ifc(result['final_ifc'], 'structure.ifc')
else:
    print(result['validation_report']['recommendation'])
```

### With TEKLA Integration

```python
# Import from TEKLA
tekla_structures = import_from_tekla('model.db')

# Detect clashes
result = run_enhanced_pipeline(tekla_structures)

# Report issues
for clash in result['clashes_detected']:
    tekla_mark_clash(clash.element_id, clash.description)
```

---

## 📞 Support Matrix

| Issue | Solution |
|-------|----------|
| "No clashes found" | Check IFC has intentional errors or data is perfect |
| "ML model not found" | System uses AISC/AWS formulas automatically |
| "Performance slow" | Use `verbose=False`, filter by severity |
| "Coordinates invalid" | Ensure all values are in meters (0-1000m range) |
| "Import errors" | Ensure `src/pipeline/agents` is in Python path |

---

## 📚 Additional Resources

- **Full Documentation:** `COMPREHENSIVE_CLASH_DETECTION_v2.md`
- **API Reference:** Check docstrings in source files
- **Test Cases:** `test_comprehensive_clash_v2.py`
- **Example Data:** Generated by `ComplexStructureGenerator`

---

**Ready to validate your structures? Run the Quick Start example now!** ✅
