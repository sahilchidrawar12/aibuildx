# DATASETS REQUIRED FOR 100% ACCURACY - DETAILED INVENTORY

**Date:** 2 December 2025  
**Status:** Comprehensive data collection plan  
**Total Data Volume:** 600,000+ entries  
**Collection Timeline:** 6-10 weeks  
**Team Effort:** 1,050 hours

---

## 1. CRITICAL DATASETS (Highest Priority)

### 1.1 CONNECTION EXAMPLES DATABASE (50,000+ items)

**Format:** JSON files in `data/connection_library/`

#### Required Fields:
```json
{
  "id": "CONN_001_ASCE",
  "connection_type": "bolted_moment_connection",
  "primary_members": ["W36x300 beam", "W14x132 column"],
  "secondary_members": ["PL 1-1/2 x 20 x 24 end plate"],
  "bolt_config": {
    "grade": "A325",
    "diameter_inch": 0.875,
    "count": 8,
    "pattern": "2x4 grid",
    "spacing_inch": 3.0,
    "edge_distance_inch": 1.5
  },
  "weld_config": {
    "type": "fillet",
    "size_inch": 0.375,
    "length_inch": 24,
    "process": "SMAW"
  },
  "capacity_kips": 850.0,
  "slip_critical": false,
  "prying_action_considered": true,
  "validation_status": "hand_calc_verified",
  "source": "AISC Design Examples",
  "applicable_standards": ["AISC 360-22", "AWS D1.1"]
}
```

#### Data Sources:
- [ ] AISC Design Examples (100+ connection designs)
- [ ] AISC Connection Design Handbook (300+ precedents)
- [ ] SteelDay Conference proceedings (200+ case studies)
- [ ] Previous project bid packages (500+ designs)
- [ ] Steel fabrication shop examples (1,000+ configurations)
- [ ] Research publications (100+ test results)
- [ ] University labs (50+ experimental validations)

#### Breakdown by Category:
| Category | Count | Source | Priority |
|----------|-------|--------|----------|
| Bolted flush end plates | 5,000 | AISC, Fabricators | CRITICAL |
| Bolted extended end plates | 5,000 | AISC, Fabricators | CRITICAL |
| Bolted reduced beam section (RBS) | 3,000 | Research labs | HIGH |
| Bolted angle connections | 2,000 | Historical projects | HIGH |
| Welded moment connections | 8,000 | AISC, Research | CRITICAL |
| Welded shear connections | 5,000 | Fabricators | HIGH |
| T-stub connections (prying) | 4,000 | Research labs | CRITICAL |
| Slip-critical connections | 3,000 | AISC 360-22 | CRITICAL |
| Column base connections | 3,000 | Historical projects | HIGH |
| Gusset plate connections | 2,000 | Bridge projects | HIGH |
| CJP weld details | 2,000 | AWS D1.1 | HIGH |
| Coped beam connections | 1,000 | Fabricators | MEDIUM |
| **TOTAL** | **43,000** | | |

**Collection Effort:** 150 hours  
**Estimated Completion:** 4-6 weeks with team

---

### 1.2 STEEL SECTIONS DATABASE (1,800+ unique profiles)

**Format:** CSV + JSON in `data/section_properties/`

#### AISC Sections (400+):
```
W-Shapes: W44x335 through W4x13 (100+)
M-Shapes: M50x18.4 through M3x2.9 (30+)
S-Shapes: S50x57.6 through S3x5.7 (30+)
HP-Shapes: HP36x300 through HP8x36 (20+)
Channels: C15x50 through MC12x10.6 (60+)
Angles: L8x8x1 through L2x2x1/8 (100+)
HSS (Square): HSS20x20x1.25 through HSS2x2x1/8 (80+)
HSS (Rectangular): HSS20x12x1.25 through HSS2x1x1/8 (60+)
HSS (Circular): Ø20x1.25 through Ø1x1/8 (40+)
Structural Tees: WT36x150 through WT2x1.5 (50+)
```

#### Eurocode Sections (600+):
```
IPE Series: IPE 100-550 (25 sizes)
HEA Series: HEA 100-1000 (32 sizes)
HEB Series: HEB 100-1000 (32 sizes)
HEM Series: HEM 100-1000 (32 sizes)
UPN Series: UPN 50-400 (30 sizes)
L Series: L 20x3 through L 200x200x30 (80+)
Circular hollow: ∅16.0 through ∅508 (100+)
Square hollow: 20x2.0 through 500x25 (100+)
Rectangular hollow: 30x20x2 through 600x400x20 (200+)
```

#### British Standard Sections (300+):
```
UB Sections: 76x76 through 914x419 (40+)
UC Sections: 152x152 through 356x406 (30+)
PFC Sections: 100x50 through 430x100 (30+)
Angles: L 20x3 through L 200x200x30 (50+)
Channels: 76x38 through 432x102 (30+)
Circular: ∅16 through ∅508 (50+)
Square: 20x2 through 500x25 (50+)
Rectangular: 30x20x2 through 600x400x25 (40+)
```

#### Chinese GB Sections (500+):
```
H-Shaped: HW100x100 through HW1000x1000 (100+)
H Light: HN100x100 through HN700x300 (50+)
I-Beams: I 10-56 series (100+)
Channels: C 80-400 series (40+)
Angles: L 25x3 through L 250x250x30 (100+)
Hollow sections: Various sizes (150+)
```

#### Required Properties per Section:
```json
{
  "profile_name": "W36x300",
  "standard": "AISC 360-22",
  "member_type": "I-beam",
  "section_class": "COMPACT",
  "nominal_depth_inch": 36.0,
  "nominal_width_inch": 12.2,
  "area_in2": 88.3,
  "weight_lb_ft": 300.0,
  "ix_in4": 36100.0,
  "iy_in4": 1190.0,
  "rx_inch": 20.3,
  "ry_inch": 3.68,
  "zx_in3": 2010.0,
  "zy_in3": 195.0,
  "sx_in3": 1980.0,
  "sy_in3": 195.0,
  "tf_inch": 0.945,
  "tw_inch": 0.604,
  "flange_slenderness": 6.47,
  "web_slenderness": 59.6,
  "cost_per_lb_usd": 0.65,
  "availability": "stock"
}
```

**Collection Effort:** 80 hours  
**Sources:** AISC, Eurocode, BS, GB standards (all freely available)  
**Estimated Completion:** 2-3 weeks

---

### 1.3 DESIGN DECISION PRECEDENTS (100,000+ examples)

**Format:** JSON in `data/design_decisions/`

#### Required Structure:
```json
{
  "project_id": "PROJ_2023_001",
  "project_name": "Downtown Office Tower",
  "year": 2023,
  "member_id": "B-F3-G2",
  "member_type": "floor_beam",
  "span_feet": 32.5,
  "tributary_load_psf": 85,
  "member_selected": "W27x102",
  "alternatives_considered": ["W24x117", "W30x90"],
  "selection_reason": "Minimum height to clear mechanical duct",
  "load_analysis": {
    "dead_load": 1.45,
    "live_load": 0.85,
    "lrfd_factored": 2.83
  },
  "utilization_ratio": 0.87,
  "cost_comparison": {
    "selected": 1825,
    "alternative_1": 1950,
    "alternative_2": 1680
  },
  "notes": "Selected despite cost premium due to depth constraint"
}
```

#### Data Sources:
- [ ] 50 completed projects from past 5 years
- [ ] 2,000 members per project avg
- [ ] Total: 100,000+ design decisions
- [ ] Include: Why each section was chosen, not just what was chosen

**Collection Effort:** 120 hours  
**Estimated Completion:** 6-8 weeks (requires project archaeology)

---

### 1.4 HISTORICAL CLASH EXAMPLES (100,000+ items)

**Format:** JSON in `data/clash_library/`

#### Required Structure:
```json
{
  "clash_id": "CLASH_2023_001_047",
  "project": "Shanghai Tower",
  "member1": {
    "id": "B-F42-G5",
    "type": "beam",
    "profile": "W24x68",
    "start": [1000.0, 500.0, 420.0],
    "end": [1000.0, 2500.0, 420.0]
  },
  "member2": {
    "id": "BR-42A",
    "type": "brace",
    "profile": "HSS 4x4x1/4",
    "start": [950.0, 600.0, 415.0],
    "end": [1050.0, 2400.0, 425.0]
  },
  "clash_type": "hard_clash",
  "minimum_distance_mm": 0.0,
  "severity": "CRITICAL",
  "resolution": {
    "method": "member_offset",
    "details": "Offset beam 50mm north",
    "cost_impact": 2500,
    "schedule_impact_days": 0
  },
  "detected_by_ai": false,
  "notes": "Missed by CAD reviewer, found during erection"
}
```

#### Data Categories:
- [ ] Hard clashes (touching/overlapping): 20,000
- [ ] Soft clashes (< 50mm gap): 30,000
- [ ] Fabrication clashes (bolt access, weld): 20,000
- [ ] Erection clashes (temporary setup): 15,000
- [ ] Near-misses (< 5mm separation): 15,000

**Collection Effort:** 150 hours  
**Sources:** CAD model clash reports, erection field reports, site photos

---

## 2. HIGH-PRIORITY SUPPORTING DATASETS

### 2.1 CODE COMPLIANCE CASE STUDIES (1,000+ examples)

**Format:** JSON in `data/compliance_cases/`

#### Fields:
```json
{
  "case_id": "COMP_AISC_001",
  "code_section": "AISC 360-22 Section E3",
  "topic": "Elastic Buckling of Columns",
  "member": "W14x132",
  "fy_ksi": 50,
  "unbraced_length_ft": 15,
  "result": {
    "lambda": 78.2,
    "lambda_c": 73.8,
    "elastic_buckling": true,
    "fcr_ksi": 28.7,
    "applied_stress_ksi": 22.4,
    "passes": true
  },
  "explanation": "Column is slender (λ > λc), uses elastic formula",
  "common_mistakes": [
    "Forgetting π² in formula",
    "Using wrong radius of gyration"
  ]
}
```

**Collection Effort:** 60 hours  
**Sources:** AISC commentary, design examples, textbooks

---

### 2.2 STRUCTURAL ANALYSIS RESULTS (50,000+ models)

**Format:** HDF5/NetCDF in `data/analysis_benchmarks/`

#### Data per Model:
- Frequencies (1st-10th modes)
- Mode shapes (node displacements)
- Static deflections (load cases)
- Dynamic response spectra
- Connection forces (internal)

**Collection Effort:** 120 hours  
**Sources:** OpenSees benchmarks, SAP2000 examples, research papers

---

### 2.3 FABRICATION DETAILS (10,000+ drawings)

**Format:** DXF + JSON in `data/fabrication_details/`

#### Includes:
- Cope dimensions & shapes
- Bolt hole patterns
- Weld access hole designs
- Stiffener plate layouts
- Connection assembly details

**Collection Effort:** 100 hours

---

## 3. MEDIUM-PRIORITY DATASETS

### 3.1 REAL DXF FILES (10,000+ actual drawings)

**Format:** DWG/DXF in `data/dwg_archive/`

#### Sources:
- [ ] Previous completed projects
- [ ] Public BIM libraries
- [ ] University projects
- [ ] Open-source architecture databases

**Collection Effort:** 100 hours

---

### 3.2 ERECTION SEQUENCES (500+ plans)

**Format:** JSON + PDF in `data/erection_plans/`

**Collection Effort:** 50 hours

---

### 3.3 GEOTECHNICAL PROFILES (10,000+ sites)

**Format:** CSV in `data/geotechnical/`

**Collection Effort:** 80 hours

---

## 4. QUICK START: MINIMUM VIABLE DATASET

**For MVP (Can reach 98% accuracy):**
- [ ] 20,000 connection examples
- [ ] 1,000 steel sections
- [ ] 50,000 design decisions
- [ ] 500 compliance cases
- [ ] 1,000 fabrication details

**Effort:** 300 hours  
**Timeline:** 4-5 weeks  
**Expected Accuracy:** 97.5-98.0%

---

## 5. DATA COLLECTION STRATEGY

### Phase 1: Public Sources (Weeks 1-2)
**Effort:** 80 hours | **Cost:** $0

- [ ] AISC Manual 15th Edition (sections, design examples)
- [ ] Eurocode 3 Part 1-1 (sections, design guidance)
- [ ] AWS D1.1 (weld specifications)
- [ ] ASCE 7-22 (loads, examples)
- [ ] AISC Design Examples downloads
- [ ] GitHub structural repositories
- [ ] Open-source BIM models

**Action:** Assign to 1 engineer full-time

---

### Phase 2: Scraped/Parsed Data (Weeks 2-4)
**Effort:** 200 hours | **Cost:** $0-2,000

- [ ] Parse AISC section tables into database
- [ ] Extract Eurocode properties
- [ ] Digitize fabrication standards
- [ ] OCR compliance examples
- [ ] Scrape supplier catalogs (anonymized)

**Action:** Assign to 2 engineers + 1 data technician

---

### Phase 3: Project Archaeology (Weeks 4-6)
**Effort:** 300 hours | **Cost:** $5,000-10,000

- [ ] Digitize previous project data
- [ ] Extract design decisions from archives
- [ ] Photograph/scan fabrication shop details
- [ ] Interview engineers on connection logic
- [ ] Collect field erection photos

**Action:** Assign to 1 engineer + 1 admin coordinator

---

### Phase 4: Synthetic Data Generation (Weeks 6-8)
**Effort:** 200 hours | **Cost:** $0

- [ ] Generate 20,000 synthetic connection variations
- [ ] Create clash scenarios algorithmically
- [ ] Generate design decision permutations
- [ ] Create corner-case test scenarios

**Action:** Python scripts to generate variations

---

## 6. DATA QUALITY REQUIREMENTS

### Validation Checklist:
- [ ] **Completeness:** No missing required fields
- [ ] **Accuracy:** Spot-check 10% of entries manually
- [ ] **Consistency:** No duplicates or near-duplicates
- [ ] **Format:** All JSON schema validated
- [ ] **Units:** Consistent (metric or imperial)
- [ ] **Sources:** Documented with references
- [ ] **Licensing:** Verify no copyright issues

### Quality Metrics:
- Target: 99% data quality
- Acceptance: Pass 99% of spot-checks

---

## 7. DATA STORAGE STRUCTURE

```
aibuildx/
└── data/
    ├── connection_library/
    │   ├── bolted_flush_end_plates/
    │   ├── bolted_extended_end_plates/
    │   ├── welded_moment_connections/
    │   ├── t_stub_connections/
    │   └── slip_critical_connections/
    ├── section_properties/
    │   ├── aisc_sections.csv
    │   ├── eurocode_sections.csv
    │   ├── british_sections.csv
    │   └── gb_sections.csv
    ├── design_decisions/
    │   ├── 2023_projects/
    │   ├── 2022_projects/
    │   └── archive/
    ├── clash_library/
    │   ├── hard_clashes/
    │   ├── soft_clashes/
    │   └── fabrication_clashes/
    ├── compliance_cases/
    │   ├── aisc_360/
    │   ├── asce_7/
    │   └── aws_d1_1/
    ├── analysis_benchmarks/
    │   ├── modal_analysis/
    │   ├── static_analysis/
    │   └── dynamic_analysis/
    ├── fabrication_details/
    │   ├── cope_details/
    │   ├── bolt_patterns/
    │   └── weld_details/
    ├── dwg_archive/
    │   ├── buildings/
    │   ├── bridges/
    │   └── stadiums/
    ├── erection_plans/
    │   └── (500+ plan PDFs)
    └── geotechnical/
        └── (10,000+ bore logs)
```

---

## 8. IMPLEMENTATION ROADMAP

| Week | Task | Owner | Hours | Status |
|------|------|-------|-------|--------|
| 1 | Public data collection | Engineer1 | 40 | [ ] |
| 2 | Parse AISC/Eurocode tables | Engineer1 | 40 | [ ] |
| 2-3 | Archive project archaeology | Admin | 60 | [ ] |
| 3-4 | Connection precedent digitization | Engineer2 | 80 | [ ] |
| 4 | Clash example compilation | Engineer2 | 50 | [ ] |
| 4-5 | Synthetic data generation | Engineer3 | 80 | [ ] |
| 5 | Data quality validation | All | 50 | [ ] |
| 6 | ML training set preparation | Engineer1 | 40 | [ ] |
| 6-7 | Database deployment | DevOps | 30 | [ ] |
| 7 | Final quality checks | All | 30 | [ ] |

**Total: ~500 hours over 7 weeks**

---

## 9. SUCCESS CRITERIA

- [ ] 50,000+ connection examples loaded
- [ ] 1,800+ steel sections in database
- [ ] 100,000+ design decisions cataloged
- [ ] 100,000+ clash examples available
- [ ] 1,000+ compliance case studies indexed
- [ ] All data passes quality checks
- [ ] ML models trained successfully
- [ ] 99%+ data consistency validation

---

## 10. ESTIMATED TIMELINE

**Aggressive:** 4-5 weeks (team of 3 engineers)  
**Conservative:** 8-10 weeks (team of 2 engineers)  
**MVP Only:** 2-3 weeks (single engineer, 300 hours)

---

## NEXT STEPS

1. **Assign Data Lead:** Responsible for overall coordination
2. **Create Data Intake Form:** Standardized collection template
3. **Set Up Database Infrastructure:** Server, backup, access controls
4. **Kick Off Public Data Collection:** Week 1
5. **Schedule Weekly Reviews:** Track progress and quality

---

**Status:** Ready to begin  
**Responsibility:** [TBD - Data Lead]  
**Funding Needed:** $5k-10k for project digitization  
**Expected Value:** $500k+ annual (from 5x productivity scaling)

