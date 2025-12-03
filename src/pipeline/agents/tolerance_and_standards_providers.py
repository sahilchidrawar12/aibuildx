"""
AI-driven tolerance and standards providers bridging to ModelInferenceEngine.

These providers expose get_tolerance(name) and get_standard_values(name)
so clash detection can be fully model-driven without hardcoded values.
"""
from typing import Any, List, Optional
import json
import os

try:
    from src.pipeline.agents.connection_synthesis_agent_enhanced import ModelInferenceEngine
except Exception:
    ModelInferenceEngine = None


class ToleranceProvider:
    """Fetch tolerances (meters) from an AI model or config via ModelInferenceEngine."""
    def __init__(self, engine: Optional[Any] = None, summary_path: Optional[str] = None):
        self.engine = engine or (ModelInferenceEngine if ModelInferenceEngine else None)
        self.summary_path = summary_path or os.path.join(os.getcwd(), 'models/phase3_validated/unified_training_summary.json')
        # Fallback map only used if engine cannot provide values
        self._fallback = {
            'SEGMENT_INTERSECT_TOL_M': 0.01,
            'PLATE_ELEV_ALIGN_TOL_M': 0.05,
            'PLATE_XY_ALIGN_TOL_M': 0.05,
            'ECCENTRICITY_TOL_M': 0.05,
            'FOUNDATION_GAP_MAX_M': 0.01,
            'SPACING_MIN_EPS_M': 0.001,
        }
        self._summary = self._load_summary()

    def _load_summary(self) -> dict:
        try:
            if os.path.exists(self.summary_path):
                with open(self.summary_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def get_tolerance(self, name: str) -> Optional[float]:
        # If engine has method, prefer it
        if self.engine and hasattr(self.engine, 'get_tolerance'):
            try:
                val = self.engine.get_tolerance(name)
                if val is not None:
                    return float(val)
            except Exception:
                pass
        # Try summary file
        try:
            tol = self._summary.get('tolerances', {}).get(name)
            if tol is not None:
                return float(tol)
        except Exception:
            pass
        return self._fallback.get(name)


class StandardsProvider:
    """Fetch standard values (mostly mm lists or material sets) from AI model/config."""
    def __init__(self, engine: Optional[Any] = None, summary_path: Optional[str] = None):
        self.engine = engine or (ModelInferenceEngine if ModelInferenceEngine else None)
        self.summary_path = summary_path or os.path.join(os.getcwd(), 'models/phase3_validated/unified_training_summary.json')
        self._fallback = {
            'weld_sizes_mm': [3.2, 4.8, 6.4, 7.9, 9.5, 11.1, 12.7, 14.3, 15.9, 19.1, 22.2],
            'bolt_diameters_mm': [12.7, 15.875, 19.05, 22.225, 25.4, 28.575, 31.75, 34.925, 38.1],
            'bolt_materials': ['A307', 'A325', 'A490'],
        }
        self._summary = self._load_summary()

    def _load_summary(self) -> dict:
        try:
            if os.path.exists(self.summary_path):
                with open(self.summary_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def get_standard_values(self, name: str) -> List[Any]:
        if self.engine and hasattr(self.engine, 'get_standards'):
            try:
                vals = self.engine.get_standards(name)
                if vals:
                    return list(vals)
            except Exception:
                pass
        # Try summary file
        try:
            vals = self._summary.get('standards', {}).get(name)
            if vals:
                return list(vals)
        except Exception:
            pass
        return self._fallback.get(name, [])
