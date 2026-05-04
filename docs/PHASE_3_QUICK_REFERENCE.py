"""
QUICK REFERENCE - PHASE 3 CREATED MODULES
═════════════════════════════════════════════════════════════════════════════

LOADS MODULE IMPORTS
────────────────────
from src.pipeline.loads import LoadCombinationAnalyzer
from src.pipeline.loads import WindLoadAnalyzer  
from src.pipeline.loads import SeismicLoadAnalyzer
from src.pipeline.loads import PDeltaAnalyzer
from src.pipeline.loads import InfluenceLineAnalyzer

QUICK EXAMPLES:

  # Load Combinations
  analyzer = LoadCombinationAnalyzer('LRFD')
  analyzer.add_load_case('D', {'moment': 100})
  analyzer.add_load_case('L', {'moment': 50})
  combos = analyzer.calculate_combinations()
  max_m, min_m, combo_id, _ = analyzer.get_envelope('moment')
  
  # Wind Loads
  wind = WindLoadAnalyzer(v_design=110, exposure='C', risk_cat='II')
  q_z = wind.velocity_pressure(30)  # Velocity pressure at 30 ft
  pressures = wind.wall_pressures(30, 25)
  base = wind.base_shear(width=100, height=60, mean_roof_height=55)
  
  # Seismic Forces
  seismic = SeismicLoadAnalyzer(s_s=0.5, s_1=0.2, site_class='D')
  sdc_short, sdc_long = seismic.design_category()
  v = seismic.base_shear(weight=1000000, period=1.2)
  sa = seismic.spectral_acceleration(period=1.2)
  
  # P-Delta Effects
  analyzer = PDeltaAnalyzer()
  m_pd = analyzer.p_delta_moment(axial_load=500000, deflection=0.5)
  theta = analyzer.stability_coefficient(total_gravity=2000000,
                                         story_height=144,
                                         first_order_shear=150000,
                                         first_order_drift=1.0)
  amplified_drift = analyzer.drift_amplification(1.0, theta)
  
  # Influence Lines
  il = InfluenceLineAnalyzer(span_length=60, num_points=21)
  envelope = il.envelope_moving_load(load=10, effect='moment')
  truck_effect = il.truck_load_envelope(
      truck_axles=[(5, 0), (10, 10), (5, 14)],
      axle_spacing=14,
      effect='moment',
      location=30
  )

═════════════════════════════════════════════════════════════════════════════

COMPLIANCE MODULE IMPORTS
──────────────────────────
from src.pipeline.compliance import AISC360Checker
from src.pipeline.compliance import AISC341SeismicChecker

QUICK EXAMPLES:

  # AISC 360 General Design
  checker = AISC360Checker(fy=50, fu=65)
  
  # Tension capacity
  p_yield, p_rupture = checker.tensile_capacity(area_gross=10, area_net=8.5)
  
  # Compression capacity (column)
  pc = checker.compression_capacity(area=20, slenderness_ratio=100)
  
  # Bending capacity
  mn = checker.bending_capacity(section_modulus=100,
                                laterally_braced_length=15,
                                radius_gyration_y=2)
  
  # Combined loading check
  ok, util = checker.combined_loading_check(demand_moment=80,
                                            capacity_moment=100,
                                            demand_shear=20,
                                            capacity_shear=30)
  
  # Column-beam interaction
  ok, util = checker.column_beam_interaction(demand_axial=200,
                                             capacity_axial=400,
                                             demand_moment=50,
                                             capacity_moment=100)
  
  # Weld capacity
  weld_cap = checker.weld_capacity(size=0.5, length=20, type_weld='fillet')
  
  # AISC 341 Seismic Design
  seismic = AISC341SeismicChecker(sdc='D', system_type='SMRF', fy=50)
  
  # Capacity design moment
  m_cap = seismic.capacity_design_moment(moment_demand=100)
  
  # Strong-column weak-beam ratio
  ok, ratio = seismic.beam_column_moment_ratio(sum_column_moments=250,
                                                sum_beam_moments=200)
  
  # Panel zone check
  ok, ratio = seismic.panel_zone_thickness(panel_width=24, max_thickness=0.5)
  
  # Story drift limit
  max_drift = seismic.story_drift_limit(story_height=144)  # inches
  
  # Design category
  if seismic.requires_seismic_provisions():
      print(seismic.weld_requirement())  # Gets weld spec
      print(seismic.bolt_requirement())  # Gets bolt spec

═════════════════════════════════════════════════════════════════════════════

CATALOGS MODULE IMPORTS
────────────────────────
from src.pipeline.catalogs import CONNECTION_TYPES, CONNECTION_CRITERIA
from src.pipeline.catalogs import WELD_TYPES, ELECTRODE_SPECS
from src.pipeline.catalogs import get_connection_by_name, list_connection_types
from src.pipeline.catalogs import get_weld_by_name, list_weld_types
from src.pipeline.catalogs import weld_strength_per_length

QUICK EXAMPLES:

  # Connection Types
  bolted_simple = get_connection_by_name('BOLTED', 'simple_shear')
  print(bolted_simple['load_type'])  # 'shear'
  
  # List all connection types
  all_types = list_connection_types('BOLTED')
  # ['simple_shear', 'tension', 'combined', 'bearing', 'slip_critical']
  
  # Get connection materials
  materials = get_connection_by_name('BOLTED', 'simple_shear')
  print(materials['bolt_grades'])  # ['A325', 'A490']
  
  # Weld types
  fillet = get_weld_by_name('FILLET', 'fillet_general')
  print(fillet['typical_applications'])
  
  # List all weld types
  all_welds = list_weld_types('FILLET')
  
  # Weld strength per length (kips/inch)
  strength = weld_strength_per_length(weld_size=0.5, electrode_grade='E70XX')
  
  # Electrode properties
  from src.pipeline.catalogs.weld_types import get_electrode_by_grade
  e70 = get_electrode_by_grade('E70XX')
  print(e70['tensile_strength_ksi'])  # 70
  
  # Connection criteria
  from src.pipeline.catalogs.connection_types import CONNECTION_CRITERIA
  criteria = CONNECTION_CRITERIA['simple_shear']
  print(criteria['min_bolts'])  # 2
  
  # Weld quality standards
  from src.pipeline.catalogs.weld_types import WELD_QUALITY_STANDARDS
  full_ut = WELD_QUALITY_STANDARDS['full_ut']
  print(full_ut['inspection_method'])  # 'Full UT coverage'

═════════════════════════════════════════════════════════════════════════════

CLASS METHODS REFERENCE
────────────────────────

LoadCombinationAnalyzer Methods:
  • add_load_case(load_type, values)
  • calculate_combinations() → Dict
  • get_envelope(effect) → (max, min, max_combo, min_combo)
  • get_critical_combination(effect) → Dict
  • capacity_check(capacity, effect) → (bool, ratio)
  • summary() → str

WindLoadAnalyzer Methods:
  • velocity_pressure(height) → float
  • gust_factor(height, mean_roof_height) → float
  • design_pressure(height, mean_roof_height, cp, directional) → float
  • wall_pressures(height, mean_roof_height) → Dict
  • roof_pressures(mean_roof_height) → Dict
  • force_on_area(area, height, mean_roof_height, cp) → float
  • base_shear(width, height, mean_roof_height) → float
  • summary() → str

SeismicLoadAnalyzer Methods:
  • design_category() → (str, str)
  • fundamental_period(height, system_type) → float
  • spectral_acceleration(period) → float
  • base_shear(weight, period, height) → float
  • vertical_distribution(story_weights, story_heights, period) → list
  • summary() → str

PDeltaAnalyzer Methods:
  • p_delta_moment(axial_load, deflection) → float
  • amplification_factor(first_order_moment, second_order_moment) → float
  • stability_coefficient(total_gravity, story_height, first_order_shear, first_order_drift) → float
  • p_delta_amplification(theta, num_stories) → float
  • effective_length_factor(k_initial, theta) → float
  • second_order_analysis(first_order_moments, p_delta_moments) → Dict
  • column_check(axial_force, moment, bending_capacity, axial_capacity) → (bool, ratio)
  • sway_check(theta, threshold) → (bool, str)
  • drift_amplification(first_order_drift, theta) → float
  • summary(theta, m1, m_pd) → str

InfluenceLineAnalyzer Methods:
  • influence_moment_at_location(x, location) → float
  • influence_shear_at_location(x, location) → float
  • influence_line_moment(x) → List[(pos, coeff)]
  • influence_line_shear(x) → List[(pos, coeff)]
  • maximum_effect_moving_load(load, load_pattern, effect, location) → float
  • minimum_effect_moving_load(load, load_pattern, effect, location) → float
  • envelope_moving_load(load, effect, effect_locations) → Dict
  • truck_load_envelope(truck_axles, axle_spacing, effect, location) → float
  • critical_load_position(effect, location) → (pos, coeff)
  • summary() → str

AISC360Checker Methods:
  • tensile_capacity(area_gross, area_net) → (p_yield, p_rupture)
  • compression_capacity(area, slenderness_ratio) → float
  • bending_capacity(section_modulus, laterally_braced_length, radius_gyration_y, section_type) → float
  • shear_capacity(area_web, thickness, height) → float
  • combined_loading_check(demand_moment, capacity_moment, demand_shear, capacity_shear) → (bool, ratio)
  • column_beam_interaction(demand_axial, capacity_axial, demand_moment, capacity_moment) → (bool, ratio)
  • bolt_tension_capacity(diameter, grade, num_bolts) → float
  • weld_capacity(size, length, type_weld, metal) → float
  • summary() → str

AISC341SeismicChecker Methods:
  • requires_seismic_provisions() → bool
  • capacity_design_moment(moment_demand) → float
  • beam_column_moment_ratio(sum_column_moments, sum_beam_moments) → (bool, ratio)
  • beam_depth_limitation(beam_depth, story_height) → (bool, ratio)
  • panel_zone_thickness(panel_width, max_thickness) → (bool, ratio)
  • weld_requirement() → str
  • bolt_requirement() → str
  • connection_demand(member_capacity) → float
  • shear_connection_demand(shear_demand) → float
  • story_drift_limit(story_height) → float
  • expected_strength_factor() → float
  • required_ductility() → Dict
  • seismic_demand_check(member_capacity, seismic_demand) → (bool, ratio)
  • summary() → str

═════════════════════════════════════════════════════════════════════════════

COMMON USAGE PATTERNS
──────────────────────

Pattern 1: Load Combination with Design Check
  analyzer = LoadCombinationAnalyzer('LRFD')
  analyzer.add_load_case('D', {'moment': 100, 'shear': 10})
  analyzer.add_load_case('L', {'moment': 75, 'shear': 8})
  combos = analyzer.calculate_combinations()
  max_m, _, _, _ = analyzer.get_envelope('moment')
  checker = AISC360Checker(50, 65)
  ok, util = checker.capacity_check(capacity=200, moment=max_m)

Pattern 2: Seismic Design with Capacity Design
  seismic = SeismicLoadAnalyzer(0.5, 0.2, 'D', 'II')
  v_base = seismic.base_shear(weight=1000000, period=1.2)
  checker_seismic = AISC341SeismicChecker('D', 'SMRF')
  m_demand_capacity = checker_seismic.capacity_design_moment(100)

Pattern 3: Weld Selection Based on Connection Type
  conn_type = get_connection_by_name('BOLTED', 'moment_connection')
  weld_spec = get_weld_by_name('FILLET', 'fillet_load_carrying')
  strength_per_inch = weld_strength_per_length(0.5, 'E70XX')

═════════════════════════════════════════════════════════════════════════════

FILES AND LOCATION REFERENCE
──────────────────────────────

All files located in: /Users/sahil/Documents/aibuildx/src/pipeline/

Loads Module:
  src/pipeline/loads/load_combinations.py
  src/pipeline/loads/wind_loads.py
  src/pipeline/loads/seismic.py
  src/pipeline/loads/pdelta.py
  src/pipeline/loads/influence_lines.py
  src/pipeline/loads/__init__.py

Compliance Module:
  src/pipeline/compliance/aisc360.py
  src/pipeline/compliance/aisc341.py
  src/pipeline/compliance/__init__.py

Catalogs Module (New in Phase 3):
  src/pipeline/catalogs/connection_types.py
  src/pipeline/catalogs/weld_types.py
  src/pipeline/catalogs/__init__.py  (updated)

═════════════════════════════════════════════════════════════════════════════
End of Phase 3 Quick Reference
═════════════════════════════════════════════════════════════════════════════
"""

print(__doc__)
