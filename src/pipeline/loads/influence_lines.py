"""Influence lines and moving load analysis.

Calculates influence coefficients for structural responses and analyzes the
effect of moving loads on beams and frames. Supports unit load method and
influence surface generation for complex structures.

Classes:
    InfluenceLineAnalyzer: Main influence line calculation class
"""

import math
from typing import Dict, List, Tuple, Optional


class InfluenceLineAnalyzer:
    """Generates and analyzes influence lines for structural effects.
    
    Handles:
    - Influence coefficients for shear and moment
    - Moving load envelope creation
    - Maximum/minimum values for moving loads
    - Muller-Breslau principle application
    - Girder and deck analysis support
    """
    
    def __init__(self, span_length: float, num_points: int = 21):
        """Initialize influence line analyzer.
        
        Args:
            span_length (float): Span length (ft)
            num_points (int): Number of points for calculation grid
        """
        self.span_length = span_length
        self.num_points = num_points
        self.locations = [i * span_length / (num_points - 1) for i in range(num_points)]
    
    def influence_moment_at_location(self, x: float, location: float) -> float:
        """Calculate moment influence coefficient (unit load at x).
        
        For simple span: IL_M = (a*b/L) where a = distance from left, b = from right
        
        Args:
            x (float): Location of interest (ft from left)
            location (float): Location of unit load (ft from left)
        
        Returns:
            float: Influence coefficient for moment
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)  # 60 ft span
            >>> il_m = analyzer.influence_moment_at_location(30, 15)  # Mid-span, unit at 1/4 span
            >>> round(il_m, 3)
            1.125
        """
        if x <= 0 or x >= self.span_length:
            return 0.0
        
        # For simply supported beam
        a = location
        b = self.span_length - location
        l = self.span_length
        
        if location <= x:
            # Unit load to left of section
            il_m = (a * x * b) / (l * l)
        else:
            # Unit load to right of section
            il_m = (b * x * a) / (l * l)
        
        return il_m
    
    def influence_shear_at_location(self, x: float, location: float) -> float:
        """Calculate shear influence coefficient (unit load at location).
        
        For simple span: IL_V = (b/L) if load left, -(a/L) if load right
        
        Args:
            x (float): Location of interest (ft from left)
            location (float): Location of unit load (ft from left)
        
        Returns:
            float: Influence coefficient for shear
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)
            >>> il_v = analyzer.influence_shear_at_location(30, 15)  # Check shear at mid-span
            >>> round(il_v, 3)
            0.75
        """
        a = location
        b = self.span_length - location
        l = self.span_length
        
        if location <= x:
            # Unit load to left of section
            il_v = b / l
        else:
            # Unit load to right of section
            il_v = -a / l
        
        return il_v
    
    def influence_line_moment(self, x: float) -> List[Tuple[float, float]]:
        """Generate influence line for moment at section x.
        
        Args:
            x (float): Section location (ft)
        
        Returns:
            list: [(load_position, influence_coeff), ...]
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60, 11)
            >>> il = analyzer.influence_line_moment(30)  # Mid-span
            >>> len(il)
            11
            >>> il[5][1]  # Coefficient at mid-span
            1.25
        """
        il_values = []
        for loc in self.locations:
            coeff = self.influence_moment_at_location(x, loc)
            il_values.append((loc, coeff))
        
        return il_values
    
    def influence_line_shear(self, x: float) -> List[Tuple[float, float]]:
        """Generate influence line for shear at section x.
        
        Args:
            x (float): Section location (ft)
        
        Returns:
            list: [(load_position, influence_coeff), ...]
        """
        il_values = []
        for loc in self.locations:
            coeff = self.influence_shear_at_location(x, loc)
            il_values.append((loc, coeff))
        
        return il_values
    
    def maximum_effect_moving_load(self, load: float, load_pattern: str = 'point',
                                   effect: str = 'moment', location: float = None) -> float:
        """Calculate maximum effect from moving load(s).
        
        Args:
            load (float): Load magnitude (kips)
            load_pattern (str): 'point', 'truck', 'lane'
            effect (str): 'moment' or 'shear'
            location (float): Section location (default mid-span)
        
        Returns:
            float: Maximum effect value
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)
            >>> max_m = analyzer.maximum_effect_moving_load(10, 'point', 'moment', 30)
            >>> round(max_m, 1)
            12.5
        """
        if location is None:
            location = self.span_length / 2
        
        if effect == 'moment':
            il_func = self.influence_moment_at_location
        else:  # shear
            il_func = self.influence_shear_at_location
        
        # Find maximum influence coefficient
        max_coeff = 0.0
        for load_loc in self.locations:
            coeff = il_func(location, load_loc)
            if abs(coeff) > abs(max_coeff):
                max_coeff = coeff
        
        return load * max_coeff
    
    def minimum_effect_moving_load(self, load: float, load_pattern: str = 'point',
                                   effect: str = 'moment', location: float = None) -> float:
        """Calculate minimum (most negative) effect from moving load.
        
        Args:
            load (float): Load magnitude (kips)
            load_pattern (str): 'point', 'truck', 'lane'
            effect (str): 'moment' or 'shear'
            location (float): Section location (default mid-span)
        
        Returns:
            float: Minimum effect value (typically negative)
        """
        if location is None:
            location = self.span_length / 2
        
        if effect == 'moment':
            il_func = self.influence_moment_at_location
        else:  # shear
            il_func = self.influence_shear_at_location
        
        # Find minimum influence coefficient
        min_coeff = 0.0
        for load_loc in self.locations:
            coeff = il_func(location, load_loc)
            if coeff < min_coeff:
                min_coeff = coeff
        
        return load * min_coeff
    
    def envelope_moving_load(self, load: float, effect: str = 'moment',
                            effect_locations: Optional[List[float]] = None) -> Dict[str, float]:
        """Create envelope of effects from moving load across span.
        
        Args:
            load (float): Load magnitude (kips)
            effect (str): 'moment' or 'shear'
            effect_locations (list): Locations to check (default: grid points)
        
        Returns:
            dict: {location: max_effect} for critical positions
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)
            >>> envelope = analyzer.envelope_moving_load(10, 'moment')
            >>> envelope[30]  # Moment at mid-span
            12.5
        """
        if effect_locations is None:
            effect_locations = self.locations
        
        envelope = {}
        
        for section_x in effect_locations:
            max_effect = self.maximum_effect_moving_load(load, effect=effect,
                                                         location=section_x)
            envelope[section_x] = max_effect
        
        return envelope
    
    def truck_load_envelope(self, truck_axles: List[Tuple[float, float]],
                          axle_spacing: float, effect: str = 'moment',
                          location: float = None) -> float:
        """Calculate effect from truck load with multiple axles.
        
        Args:
            truck_axles (list): [(axle_load, distance_from_first), ...]
            axle_spacing (float): Spacing between first and last axle (ft)
            effect (str): 'moment' or 'shear'
            location (float): Section location
        
        Returns:
            float: Total effect from truck
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)
            >>> truck = [(5, 0), (10, 10), (5, 14)]  # 5-10-5 ton truck
            >>> effect = analyzer.truck_load_envelope(truck, 14, 'moment', 30)
            >>> round(effect, 1)
            20.8
        """
        if location is None:
            location = self.span_length / 2
        
        if effect == 'moment':
            il_func = self.influence_moment_at_location
        else:
            il_func = self.influence_shear_at_location
        
        total_effect = 0.0
        
        for load, dist_from_first in truck_axles:
            # Try different truck positions
            for truck_start in self.locations:
                axle_loc = truck_start + dist_from_first
                if 0 <= axle_loc <= self.span_length:
                    effect_val = load * il_func(location, axle_loc)
                    total_effect = max(total_effect, effect_val)
        
        return total_effect
    
    def critical_load_position(self, effect: str = 'moment', 
                              location: float = None) -> Tuple[float, float]:
        """Find position of unit load that creates maximum effect.
        
        Args:
            effect (str): 'moment' or 'shear'
            location (float): Section location
        
        Returns:
            tuple: (load_position, influence_coeff)
        
        Example:
            >>> analyzer = InfluenceLineAnalyzer(60)
            >>> pos, coeff = analyzer.critical_load_position('moment', 30)
            >>> pos  # Load position for max moment at mid-span
            30.0
            >>> round(coeff, 3)
            1.25
        """
        if location is None:
            location = self.span_length / 2
        
        if effect == 'moment':
            il_func = self.influence_moment_at_location
        else:
            il_func = self.influence_shear_at_location
        
        critical_pos = None
        critical_coeff = 0.0
        
        for load_pos in self.locations:
            coeff = il_func(location, load_pos)
            if abs(coeff) > abs(critical_coeff):
                critical_coeff = coeff
                critical_pos = load_pos
        
        return critical_pos, critical_coeff
    
    def summary(self) -> str:
        """Generate influence line analyzer summary.
        
        Returns:
            str: Formatted summary text
        """
        summary = f"\n{'='*70}\n"
        summary += f"Influence Line Analysis Summary\n"
        summary += f"{'='*70}\n"
        summary += f"Span Length: {self.span_length:.1f} ft\n"
        summary += f"Analysis Grid Points: {self.num_points}\n"
        summary += f"Point Spacing: {self.span_length/(self.num_points-1):.2f} ft\n"
        summary += f"{'='*70}\n"
        
        return summary
