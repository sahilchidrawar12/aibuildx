"""Load combinations and envelope analysis for structural design.

Implements AISC and LRFD/ASD load combination patterns according to building
codes. Calculates envelope of critical load cases for member design.

Classes:
    LoadCombinationAnalyzer: Main class for load combination logic
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class LoadCombinationAnalyzer:
    """Analyzes and envelopes multiple load combinations for design.
    
    Handles AISC 360 and IBC load combination rules, including:
    - LRFD (Load and Resistance Factor Design) combinations
    - ASD (Allowable Stress Design) combinations
    - Wind and seismic load modifiers
    - Snow load combinations
    - Live load reduction factors
    """
    
    # AISC 360 LRFD Load Combinations
    LRFD_COMBINATIONS = {
        1: {'D': 1.4},                                    # Dead load
        2: {'D': 1.2, 'L': 1.6, 'Lr': 0.5},             # Live + roof
        3: {'D': 1.2, 'L': 1.6, 'S': 0.5},              # Live + snow
        4: {'D': 1.2, 'L': 1.0, 'Lr': 1.6},             # Roof live
        5: {'D': 1.2, 'L': 1.0, 'S': 1.6},              # Snow
        6: {'D': 1.2, 'W': 1.0},                        # Wind only
        7: {'D': 0.9, 'W': 1.0},                        # Wind with reduced dead
        8: {'D': 1.2, 'E': 1.0},                        # Seismic
        9: {'D': 0.9, 'E': 1.0},                        # Seismic reduced dead
    }
    
    # ASD Load Combinations
    ASD_COMBINATIONS = {
        1: {'D': 1.0},
        2: {'D': 1.0, 'L': 1.0},
        3: {'D': 1.0, 'Lr': 1.0},
        4: {'D': 1.0, 'S': 1.0},
        5: {'D': 1.0, 'L': 0.75, 'Lr': 0.75},
        6: {'D': 1.0, 'L': 0.75, 'S': 0.75},
        7: {'D': 0.6, 'W': 1.0},
        8: {'D': 1.0, 'W': 0.75},
    }
    
    def __init__(self, method: str = 'LRFD'):
        """Initialize load combination analyzer.
        
        Args:
            method (str): 'LRFD' or 'ASD' design method
        """
        self.method = method
        self.combinations = self.LRFD_COMBINATIONS if method == 'LRFD' else self.ASD_COMBINATIONS
        self.load_cases: Dict[str, Dict[str, float]] = {}  # Load type -> values
        self.results: Dict[int, Dict[str, float]] = {}     # Combination -> results
    
    def add_load_case(self, load_type: str, values: Dict[str, float]) -> None:
        """Add load case values (shear, moment, deflection, etc).
        
        Args:
            load_type (str): 'D' (dead), 'L' (live), 'W' (wind), 'E' (seismic), etc
            values (dict): Load effects {'shear': V, 'moment': M, 'reaction': R, etc}
        """
        self.load_cases[load_type] = values
    
    def calculate_combinations(self) -> Dict[int, Dict[str, float]]:
        """Calculate all load combination envelopes.
        
        Returns:
            dict: {combo_id: {'shear': max_V, 'moment': max_M, ...}}
        
        Example:
            >>> analyzer = LoadCombinationAnalyzer('LRFD')
            >>> analyzer.add_load_case('D', {'shear': 10, 'moment': 50})
            >>> analyzer.add_load_case('L', {'shear': 15, 'moment': 75})
            >>> combos = analyzer.calculate_combinations()
            >>> combos[2]['moment']  # 1.2*50 + 1.6*75 = 180
            180.0
        """
        self.results = {}
        
        for combo_id, factors in self.combinations.items():
            combo_result = defaultdict(float)
            
            # Sum factored load effects
            for load_type, factor in factors.items():
                if load_type in self.load_cases:
                    for effect_name, effect_value in self.load_cases[load_type].items():
                        combo_result[effect_name] += factor * effect_value
            
            if combo_result:
                self.results[combo_id] = dict(combo_result)
        
        return self.results
    
    def get_envelope(self, effect: str = 'moment') -> Tuple[float, float, int, int]:
        """Get envelope (max and min) of an effect across all combinations.
        
        Args:
            effect (str): Effect name ('moment', 'shear', 'reaction', etc)
        
        Returns:
            tuple: (max_value, min_value, max_combo_id, min_combo_id)
        """
        if not self.results:
            self.calculate_combinations()
        
        values = [(v.get(effect, 0), combo_id) 
                  for combo_id, v in self.results.items()]
        
        if not values:
            return 0.0, 0.0, 0, 0
        
        max_val, max_combo = max(values, key=lambda x: x[0])
        min_val, min_combo = min(values, key=lambda x: x[0])
        
        return max_val, min_val, max_combo, min_combo
    
    def get_critical_combination(self, effect: str = 'moment') -> Dict[str, any]:
        """Get the critical (governing) load combination.
        
        Args:
            effect (str): Effect to check ('moment', 'shear', 'reaction')
        
        Returns:
            dict: {combo_id, value, load_factors, load_case_values}
        """
        max_val, min_val, max_combo, min_combo = self.get_envelope(effect)
        
        # Governs in tension (positive) or compression (negative)
        if abs(max_val) > abs(min_val):
            governing = max_combo
            governing_value = max_val
        else:
            governing = min_combo
            governing_value = min_val
        
        return {
            'combination_id': governing,
            'value': governing_value,
            'factors': self.combinations[governing],
            'effects': self.results[governing]
        }
    
    def capacity_check(self, capacity: float, effect: str = 'moment') -> Tuple[bool, float]:
        """Check if capacity is sufficient for all combinations.
        
        Args:
            capacity (float): Available capacity (e.g., moment capacity)
            effect (str): Effect to check
        
        Returns:
            tuple: (passes, utilization_ratio)
        
        Example:
            >>> analyzer.capacity_check(capacity=200, effect='moment')
            (True, 0.85)  # 85% utilized, safe
        """
        max_demand, _, _, _ = self.get_envelope(effect)
        ratio = max_demand / capacity if capacity > 0 else float('inf')
        return ratio <= 1.0, ratio
    
    def summary(self) -> str:
        """Generate summary of all combinations and envelopes.
        
        Returns:
            str: Formatted summary text
        """
        if not self.results:
            self.calculate_combinations()
        
        summary_text = f"\n{'='*70}\n"
        summary_text += f"Load Combination Summary ({self.method})\n"
        summary_text += f"{'='*70}\n"
        summary_text += f"Total Combinations: {len(self.results)}\n\n"
        
        # Get all effect types
        effects = set()
        for result_dict in self.results.values():
            effects.update(result_dict.keys())
        
        for effect in sorted(effects):
            max_val, min_val, max_combo, min_combo = self.get_envelope(effect)
            summary_text += f"{effect.upper()}:\n"
            summary_text += f"  Max: {max_val:.2f} (Combo {max_combo})\n"
            summary_text += f"  Min: {min_val:.2f} (Combo {min_combo})\n"
        
        summary_text += f"{'='*70}\n"
        return summary_text
