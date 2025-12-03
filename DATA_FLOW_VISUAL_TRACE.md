# Visual Data Flow Trace: Where Joints/Connections/Bolts Get Lost

## Pipeline Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MAIN_PIPELINE_AGENT.PY - process() function                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 1: Parse DXF ──────────────────────────────────────────────────┐
│ Line 52-61: DXF Parser                                               │
│ INPUT:  sample_frame.dxf                                             │
│ OUTPUT: members = 14 members                                         │
│         out['members'] = 14 ✓                                        │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 2: Geometry Agent ─────────────────────────────────────────────┐
│ Line 63-71: Set coordinate system, merge nodes, resolve orientation  │
│ INPUT:  14 members                                                   │
│ OUTPUT: members (updated)                                            │
│         out['members'] = 14 ✓                                        │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 3: Node Resolution & Joints ───────────────────────────────────┐
│ Line 73-75: node_resolution.py functions                             │
│ INPUT:  14 members                                                   │
│ PROCESS:                                                             │
│   - snap_nodes(members) → 10 nodes                                   │
│   - auto_generate_joints(members) → 3 joints ✓✓✓                   │
│                                                                      │
│ OUTPUT: nodes = 10 nodes                                             │
│         joints = 3 joints ✓✓✓                                       │
│         out['nodes'] = 10 ✓                                          │
│         out['joints'] = 3 ✓                                          │
│                                                                      │
│ DATA STATE AT LINE 77:                                               │
│   out = {                                                            │
│     'members': [14 items],                                           │
│     'nodes': [10 items],                                             │
│     'joints': [3 items] ← IMPORTANT!                                 │
│   }                                                                  │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 4: Classification ─────────────────────────────────────────────┐
│ Line 78-90: section_classifier, material_classifier                  │
│ INPUT:  14 members                                                   │
│ OUTPUT: members (with profiles and materials)                        │
│         out['members_classified'] = 14 ✓                             │
│ DATA STATE: out['joints'] = 3 ✓ (unchanged)                          │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ STEP 5: Load Combinations ──────────────────────────────────────────┐
│ Line 91-95                                                           │
│ OUTPUT: out['load_combinations']                                     │
│ DATA STATE: out['joints'] = 3 ✓ (unchanged)                          │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
        [... STEPS 6-11 OMITTED FOR BREVITY ...]
                              ↓
┌─ STEP 12: Connection Synthesis ──────────────────────────────────────┐
│ Line 109-113: connection_synthesis_agent.synthesize_connections()    │
│ INPUT:  members = 14, joints = 3 ✓                                   │
│ PROCESS:                                                             │
│   for j in joints:          ← Iterate 3 times                       │
│     plate = create_plate()  ← 1 plate per joint                      │
│     for bolt in pattern:    ← 4 bolts per plate                      │
│       bolts.append()        ← 4 bolts per plate                      │
│                                                                      │
│ OUTPUT: plates_synth = 3 plates ✓✓✓                                  │
│         bolts_synth = 12 bolts ✓✓✓✓✓✓✓✓✓✓✓✓                          │
│         out['plates'] = 3 ✓                                          │
│         out['bolts'] = 12 ✓                                          │
│                                                                      │
│ DATA STATE AT LINE 113:                                              │
│   out = {                                                            │
│     'members': [14 items],                                           │
│     'nodes': [10 items],                                             │
│     'joints': [3 items] ✓   ← GENERATED                              │
│     'plates': [3 items] ✓   ← GENERATED                              │
│     'bolts': [12 items] ✓   ← GENERATED                              │
│   }                                                                  │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
        [... STEPS 13-21 OMITTED ...]
                              ↓
┌─ STEP 22: IFC EXPORT (THE CRITICAL POINT) ──────────────────────────┐
│ Line 160-163: ifc_generator.export_ifc_model()                       │
│                                                                      │
│ CODE:                                                                │
│   ifc_model = export_ifc_model(                                      │
│       members,                ← 14 members ✓ PASSED                  │
│       out.get('plates') or data.get('plates', []),                   │
│                              ← 3 plates ✓ PASSED                     │
│       out.get('bolts') or data.get('bolts', [])                      │
│                              ← 12 bolts ✓ PASSED                     │
│       # ❌ out['joints'] NOT PASSED! ← CRITICAL MISS!               │
│   )                                                                  │
│                                                                      │
│ FUNCTION SIGNATURE (ifc_generator.py:472):                           │
│   def export_ifc_model(members: List[Dict[str,Any]],                │
│                        plates: List[Dict[str,Any]],                 │
│                        bolts: List[Dict[str,Any]]) → Dict[str,Any]: │
│       # ❌ NO 'joints' PARAMETER ← CAN'T RECEIVE IT                 │
│                                                                      │
│ INSIDE export_ifc_model():                                           │
│   Line 499: model = {                                                │
│       "beams": [],      ✓ Initialized                                │
│       "columns": [],    ✓ Initialized                                │
│       "plates": [],     ✓ Initialized                                │
│       "fasteners": [],  ✓ Initialized                                │
│       "joints": []      ❌ MISSING (not initialized)                 │
│   }                                                                  │
│                                                                      │
│   Line 542-604: Process members                                      │
│       for m in members:  ← 14 iterations                             │
│           generate_ifc_beam() or generate_ifc_column()               │
│           model['beams'].append() or model['columns'].append()       │
│       RESULT: 6 beams, 4 columns ✓✓✓✓✓✓✓✓✓✓                         │
│                                                                      │
│   Line 607-634: Process plates                                       │
│       for p in plates:  ← 3 iterations expected                      │
│           ifc_plate = generate_ifc_plate(p)  ← Potential failure?   │
│           model['plates'].append(ifc_plate)                          │
│           plate_map[p.get('id')] = ifc_plate['id']                   │
│       RESULT: model['plates'] = [] ❌ EMPTY!                         │
│       REASON: Likely silent exception in generate_ifc_plate()        │
│       CONSEQUENCE: plate_map = {} (empty dict)                       │
│                                                                      │
│   Line 636-655: Process bolts/fasteners                              │
│       for b in bolts:  ← 12 iterations expected                      │
│           ifc_fastener = generate_ifc_fastener(b)  ← Creates ✓      │
│           model['fasteners'].append(ifc_fastener)                    │
│                                                                      │
│           plate_id = b.get('plate_id')  ← 'plate_joint_0', etc      │
│           if plate_id and plate_id in plate_map:  ← FAILS! ❌       │
│               # plate_map is empty because plates failed            │
│               model['relationships']['structural_connections']      │
│               .append(connection)                                    │
│       RESULT: model['fasteners'] = [] ❌ EMPTY!                      │
│       RESULT: structural_connections = [] ❌ EMPTY!                  │
│                                                                      │
│   Line 657: No processing for joints (doesn't exist)                 │
│       # NO LOOP FOR JOINTS!                                         │
│       RESULT: model['joints'] = [] ❌ EMPTY!                         │
│                                                                      │
│ RETURN: ifc_model                                                    │
│ DATA STATE AT RETURN:                                                │
│   {                                                                  │
│     "beams": [6 items] ✓                                             │
│     "columns": [4 items] ✓                                           │
│     "plates": [] ❌ EMPTY                                            │
│     "fasteners": [] ❌ EMPTY                                         │
│     "joints": [] ❌ EMPTY                                            │
│     "relationships": {                                               │
│       "spatial_containment": [13 items] ✓                           │
│       "structural_connections": [] ❌ EMPTY                         │
│     }                                                                │
│   }                                                                  │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ RETURN TO USER ─────────────────────────────────────────────────────┐
│ Line 180: out['ifc'] = ifc_model                                     │
│ out['ifc'] now contains the IFC model WITH empty plates/fasteners    │
│                                                                      │
│ USER SEES: ifc (2).json with:                                        │
│   - Beams: 6 ✓                                                       │
│   - Columns: 4 ✓                                                     │
│   - Plates: 0 ❌                                                     │
│   - Fasteners: 0 ❌                                                  │
│   - Joints: 0 ❌                                                     │
│   - Connections: 0 ❌                                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Data Loss Timeline

```
TIME  | LOCATION                          | DATA PRESENT? | STATUS
------|-----------------------------------|---------------|--------------------
T+5s  | auto_generate_joints()            | 3 joints ✓    | GENERATED
      | out['joints'] = joints            | 3 joints ✓    | STORED
------|-----------------------------------|---------------|--------------------
T+6s  | synthesize_connections()          | 3 plates ✓    | GENERATED
      | out['plates'] = plates_synth      | 3 plates ✓    | STORED
------|-----------------------------------|---------------|--------------------
T+6s  | synthesize_connections()          | 12 bolts ✓    | GENERATED
      | out['bolts'] = bolts_synth        | 12 bolts ✓    | STORED
------|-----------------------------------|---------------|--------------------
T+8s  | Main pipeline line 160-163        | 3 joints ✓✓✓  | ❌ NOT PASSED!
      | Function call to export_ifc_model | 3 plates ✓    | PASSED
      |                                   | 12 bolts ✓    | PASSED
------|-----------------------------------|---------------|--------------------
T+8s  | Inside export_ifc_model()         | ✗ joints      | ❌ NOT RECEIVED
      | Function receives parameters     | 3 plates ✓    | RECEIVED
      |                                   | 12 bolts ✓    | RECEIVED
------|-----------------------------------|---------------|--------------------
T+8s  | IFC model initialization          | ✓ beams        | PREPARED
      | model['beams'] = []               | ✓ columns      | PREPARED
      | model['plates'] = []              | ✗ joints       | ❌ MISSING
      | model['joints'] = []?             | ? plates       | ?
      | model['fasteners'] = []           | ? bolts        | ?
------|-----------------------------------|---------------|--------------------
T+9s  | Processing plates                 | 3 plates      | ❌ FAIL (exception)
      | generate_ifc_plate() fails?       | plate_map = {} | CONSEQUENCE
------|-----------------------------------|---------------|--------------------
T+9s  | Processing bolts                  | 12 bolts      | PARTIALLY OK
      | if plate_id in plate_map          | plate_map = {} | ❌ FAILS CHECK
      | Connection linking fails          | 0 connections | RESULT
------|-----------------------------------|---------------|--------------------
T+9s  | export_ifc_model() returns        | 0 plates      | ❌ EMPTY
      | to main_pipeline_agent            | 0 bolts       | ❌ EMPTY
      |                                   | 0 joints      | ❌ EMPTY
      |                                   | 0 connections | ❌ EMPTY
------|-----------------------------------|---------------|--------------------
T+9s  | out['ifc'] = ifc_model            | See above     | USER OUTPUT
      | JSON written to file              | Incomplete    | BROKEN
------|-----------------------------------|---------------|--------------------
```

---

## The Three Failures

### Failure #1: Joints Lost (100% Confirmed)
```
out['joints'] = 3 items
    ↓
export_ifc_model(members, plates, bolts)  ← NO joints parameter
    ↓
Inside export_ifc_model: joints = ??? (undefined)
    ↓
IFC model returned: "joints": [] ✗
```

### Failure #2: Plates Lost (>95% Probable)
```
out['plates'] = 3 items
    ↓
export_ifc_model(members, plates, bolts)  ← plates parameter ✓
    ↓
Inside export_ifc_model():
    for p in plates:  ← Should iterate 3 times
        ifc_plate = generate_ifc_plate(p)  ← EXCEPTION HERE?
        model['plates'].append(ifc_plate)  ← Never executed
    ↓
IFC model returned: "plates": [] ✗
```

**Diagnosis**: Add try-catch logging to find the exact exception.

### Failure #3: Bolts/Connections Lost (100% Confirmed)
```
out['bolts'] = 12 items (each with 'plate_id' reference)
    ↓
export_ifc_model(members, plates, bolts)  ← bolts parameter ✓
    ↓
Inside export_ifc_model():
    plate_map = {}  ← Empty because plates failed!
    
    for b in bolts:
        ifc_fastener = generate_ifc_fastener(b)  ← Creates OK
        model['fasteners'].append(ifc_fastener)  ← Appends
        
        plate_id = b.get('plate_id')  ← 'plate_joint_0'
        if plate_id and plate_id in plate_map:  ← CONDITION FAILS!
            # This block never executes
            model['relationships']['structural_connections']
            .append(connection)
    ↓
IFC model returned: "fasteners": [12 items] but
                   "structural_connections": [] ✗
```

---

## Evidence from Test Output

When pipeline ran:
```
Step 1: ML member role inference for 14 members     ✓
Step 2: ML profile selection for 14 members         ✓
Step 3: ML material selection for 14 members        ✓
Step 4: Generating spatial nodes and joints
  - Generated 3 joints                              ✓
```

But IFC output shows:
```
{
  "summary": {
    "total_columns": 4,
    "total_beams": 6,
    "total_plates": 0,        ← Should be 3!
    "total_fasteners": 0,     ← Should be 12!
    "total_relationships": 13 ← Should be 13 + connections!
  }
}
```

---

## Summary

**Connections/Bolts/Joints Missing Because:**

1. **Joints**: Generated (confirmed: "3 joints") but never passed to IFC export
2. **Plates**: Generated (supposed to be 3) but likely fail during conversion
3. **Bolts**: Generated (supposed to be 12) but cannot link to missing plates
4. **Connections**: Cannot exist without plate_map being populated

**Data Flow**: `Generated → Stored in out[] → Partially Passed to IFC → Lost Inside IFC Export`

**Next Step**: Implement the fixes to restore the data flow.
