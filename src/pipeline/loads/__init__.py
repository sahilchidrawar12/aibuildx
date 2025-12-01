"""Loads module for structural analysis.

Provides load combination analysis, wind load calculations, seismic force
determination, P-Delta effects, and moving load influence lines.

Classes:
    LoadCombinationAnalyzer: Load combination envelope analysis
    WindLoadAnalyzer: Wind load per ASCE 7
    SeismicLoadAnalyzer: Seismic force per IBC/ASCE 41
    PDeltaAnalyzer: Second-order P-Delta effects
    InfluenceLineAnalyzer: Moving load and influence lines

Import Examples:
    from src.pipeline.loads import LoadCombinationAnalyzer
    from src.pipeline.loads import WindLoadAnalyzer
    from src.pipeline.loads import SeismicLoadAnalyzer
    from src.pipeline.loads import PDeltaAnalyzer
    from src.pipeline.loads import InfluenceLineAnalyzer
    
    # Load combination analysis
    analyzer = LoadCombinationAnalyzer('LRFD')
    analyzer.add_load_case('D', {'moment': 100})
    analyzer.add_load_case('L', {'moment': 50})
    combos = analyzer.calculate_combinations()
    
    # Wind loads
    wind = WindLoadAnalyzer(v_design=110, exposure='C')
    q_z = wind.velocity_pressure(30)  # At 30 ft height
    pressures = wind.wall_pressures(30, 25)
    
    # Seismic forces
    seismic = SeismicLoadAnalyzer(s_s=0.5, s_1=0.2)
    v = seismic.base_shear(weight=1000000)
    
    # P-Delta
    analyzer = PDeltaAnalyzer()
    m_pd = analyzer.p_delta_moment(500000, 0.5)
    theta = analyzer.stability_coefficient(2000000, 144, 150000, 1.0)
    
    # Influence lines
    il = InfluenceLineAnalyzer(60)
    envelope = il.envelope_moving_load(10, 'moment')
"""

from .load_combinations import LoadCombinationAnalyzer
from .wind_loads import WindLoadAnalyzer
from .seismic import SeismicLoadAnalyzer
from .pdelta import PDeltaAnalyzer
from .influence_lines import InfluenceLineAnalyzer

__all__ = [
    'LoadCombinationAnalyzer',
    'WindLoadAnalyzer',
    'SeismicLoadAnalyzer',
    'PDeltaAnalyzer',
    'InfluenceLineAnalyzer',
]
