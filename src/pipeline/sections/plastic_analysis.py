"""
Plastic Analysis Properties for calculating plastic section moduli and moment capacities.
Used for plastic limit state analysis and load factor design.
"""


class PlasticAnalysisProperties:
    """Calculate plastic section moduli and moment capacity"""
    
    @staticmethod
    def plastic_section_modulus(area_mm2, yield_stress_mpa, depth_mm):
        """
        Estimate plastic section modulus Zp.
        
        For rolled I-beams: Zp typically 1.1-1.2x Sx
        Zp is the first moment of area about the neutral axis at yield.
        
        Args:
            area_mm2: Gross area in mm2
            yield_stress_mpa: Yield stress in MPa
            depth_mm: Member depth in mm
            
        Returns:
            Plastic section modulus Zp in mm3
        """
        # Elastic section modulus (approximate for I-beam)
        sx = (area_mm2 * depth_mm) / 4  # Rough estimate
        
        # Plastic section modulus (typically 1.15x elastic for I-beams)
        zp = 1.15 * sx
        
        return zp
    
    @staticmethod
    def plastic_moment_capacity(zp_mm3, fy_mpa):
        """
        Calculate plastic moment capacity Mp.
        
        Mp = Zp * Fy (ignoring reduction factors for now)
        
        Args:
            zp_mm3: Plastic section modulus in mm3
            fy_mpa: Yield stress in MPa
            
        Returns:
            Plastic moment capacity in kNm
        """
        # Mp in N*mm
        mp_nmm = zp_mm3 * fy_mpa
        
        # Convert to kNm
        mp_knm = mp_nmm / 1e6
        
        return mp_knm
    
    @staticmethod
    def shape_factor(section_type):
        """
        Return shape factor (Zp/Sx ratio) for different section types.
        
        Shape factor indicates how efficiently a section uses material beyond yield.
        
        Args:
            section_type: 'I-beam', 'box', 'angle', 'channel', 'pipe', etc.
            
        Returns:
            Shape factor (Zp/Sx ratio)
        """
        shape_factors = {
            'I-beam': 1.15,
            'wide_flange': 1.15,
            'box_rect': 1.27,
            'box_square': 1.27,
            'pipe_round': 1.27,
            'angle': 1.50,
            'channel': 1.25,
            'tee': 1.10,
            'circular': 1.27,
            'rect_solid': 1.50,
        }
        return shape_factors.get(section_type, 1.15)
    
    @staticmethod
    def plastic_analysis_check(sx_mm3, zp_mm3, applied_moment_knm, fy_mpa):
        """
        Check section under plastic analysis (ultimate strength).
        
        Args:
            sx_mm3: Elastic section modulus in mm3
            zp_mm3: Plastic section modulus in mm3
            applied_moment_knm: Applied moment in kNm
            fy_mpa: Yield stress in MPa
            
        Returns:
            Dictionary with capacity check
        """
        # Elastic capacity at yield
        my_knm = (sx_mm3 * fy_mpa) / 1e6
        
        # Plastic capacity (ultimate)
        mp_knm = PlasticAnalysisProperties.plastic_moment_capacity(zp_mm3, fy_mpa)
        
        # Reserve capacity beyond initial yield
        reserve = mp_knm - my_knm
        
        unity_elastic = applied_moment_knm / my_knm if my_knm > 0 else 0
        unity_plastic = applied_moment_knm / mp_knm if mp_knm > 0 else 0
        
        return {
            'My_kNm': my_knm,
            'Mp_kNm': mp_knm,
            'applied_moment_kNm': applied_moment_knm,
            'unity_check_elastic': unity_elastic,
            'unity_check_plastic': unity_plastic,
            'reserve_capacity_kNm': reserve,
            'safety_margin': (mp_knm - applied_moment_knm) / applied_moment_knm if applied_moment_knm > 0 else float('inf'),
            'pass_elastic': unity_elastic <= 1.0,
            'pass_plastic': unity_plastic <= 1.0
        }
    
    @staticmethod
    def redistribution_factor(moment_ratio):
        """
        Moment redistribution factor for continuous beams in plastic design.
        
        AISC allows moment redistribution in continuous beams if rotation capacity adequate.
        
        Args:
            moment_ratio: Ratio of negative to positive moment in continuous system
            
        Returns:
            Maximum allowed redistribution percentage
        """
        # Simplified AISC rule: allow up to 10% redistribution
        # More sophisticated analysis would consider span ratios, load patterns
        if moment_ratio > 1.5:
            return 0.05  # Conservative for high redistribution
        elif moment_ratio > 1.0:
            return 0.10
        else:
            return 0.15  # Maximum for favorable moment ratios
    
    @staticmethod
    def inelastic_analysis_results(elastic_moments_dict, section_props_dict, fy_mpa):
        """
        Summarize inelastic (plastic) analysis results for all design sections.
        
        Args:
            elastic_moments_dict: {'section_id': moment_knm, ...}
            section_props_dict: {'section_id': {'sx': mm3, 'zp': mm3}, ...}
            fy_mpa: Yield stress
            
        Returns:
            Analysis summary for all sections
        """
        results = {}
        
        for sec_id, moment_knm in elastic_moments_dict.items():
            props = section_props_dict.get(sec_id, {})
            sx = props.get('sx', 1000)
            zp = props.get('zp', 1150)
            
            check = PlasticAnalysisProperties.plastic_analysis_check(sx, zp, moment_knm, fy_mpa)
            results[sec_id] = check
        
        return results
