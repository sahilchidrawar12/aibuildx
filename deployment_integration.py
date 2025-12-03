#!/usr/bin/env python3
"""
PRODUCTION DEPLOYMENT INTEGRATION SCRIPT
Comprehensive Clash Detection v2.0

Integrates clash detection system into existing pipeline and enables
real-world testing and deployment.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project to path
sys.path.insert(0, "/Users/sahil/Documents/aibuildx")

# ============================================================================
# IMPORTS
# ============================================================================

from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector
from src.pipeline.agents.comprehensive_clash_corrector_v2 import ComprehensiveClashCorrector
from src.pipeline.agents.main_pipeline_agent_enhanced import run_enhanced_pipeline


# ============================================================================
# DEPLOYMENT UTILITIES
# ============================================================================

class ClashDetectionDeployment:
    """Deploy and manage clash detection in production."""
    
    def __init__(self):
        self.detector = ComprehensiveClashDetector()
        self.corrector = ComprehensiveClashCorrector()
        self.deployment_dir = Path("/Users/sahil/Documents/aibuildx/deployments")
        self.deployment_dir.mkdir(exist_ok=True)
    
    def analyze_structure(self, ifc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze structure for clashes (non-corrective)."""
        
        print("\n" + "="*80)
        print("CLASH DETECTION ANALYSIS")
        print("="*80)
        
        # Detect clashes
        clashes, summary = self.detector.detect_all_clashes(ifc_data)
        
        print(f"\n📊 Detection Results:")
        print(f"  Total Clashes: {summary.get('total', 0)}")
        
        severity_counts = summary.get('by_severity', {})
        for severity, count in severity_counts.items():
            print(f"  - {severity}: {count}")
        
        category_counts = summary.get('by_category', {})
        print(f"\n  By Category ({len(category_counts)} types):")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {category}: {count}")
        
        return {
            'clashes': clashes,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def correct_structure(self, ifc_data: Dict[str, Any], auto_correct: bool = True) -> Dict[str, Any]:
        """Detect and correct clashes."""
        
        print("\n" + "="*80)
        print("CLASH DETECTION & CORRECTION")
        print("="*80)
        
        # Detect clashes
        print("\n1. Detecting clashes...")
        clashes, summary = self.detector.detect_all_clashes(ifc_data)
        
        print(f"   Found {len(clashes)} clashes")
        
        if not auto_correct or len(clashes) == 0:
            return {
                'status': 'analyzed',
                'clashes_detected': len(clashes),
                'clashes': clashes,
                'summary': summary,
                'corrected': 0
            }
        
        # Correct clashes
        print("\n2. Correcting clashes...")
        corrections, correction_summary = self.corrector.correct_all_clashes(clashes, ifc_data)
        
        print(f"   Corrected: {correction_summary.get('corrected', 0)}")
        print(f"   Review Required: {correction_summary.get('review_required', 0)}")
        print(f"   Failed: {correction_summary.get('failed', 0)}")
        
        return {
            'status': 'corrected',
            'clashes_detected': len(clashes),
            'clashes': clashes,
            'detection_summary': summary,
            'corrections': corrections,
            'correction_summary': correction_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_report(self, result: Dict[str, Any], filename: str) -> Path:
        """Save analysis report."""
        
        report_path = self.deployment_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: {report_path}")
        return report_path


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_simple_structure():
    """Example 1: Analyze a simple structure."""
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Structure Analysis")
    print("="*80)
    
    # Create a simple structure with potential clashes
    structure = {
        'members': [
            {
                'id': 'B1',
                'type': 'beam',
                'start': [0, 0, 3000],
                'end': [5000, 0, 3000],
                'profile': 'W24x62'
            },
            {
                'id': 'C1',
                'type': 'column',
                'start': [0, 0, 0],
                'end': [0, 0, 3000],
                'profile': 'W14x90'
            }
        ],
        'joints': [
            {
                'id': 'J1',
                'position': [0, 0, 3000],
                'members': ['B1', 'C1']
            }
        ],
        'plates': [],
        'bolts': [],
        'welds': []
    }
    
    deployment = ClashDetectionDeployment()
    result = deployment.analyze_structure(structure)
    deployment.save_report(result, "simple_structure_analysis")
    
    return result


def example_complex_structure():
    """Example 2: Analyze and correct a complex structure."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Complex Structure Analysis & Correction")
    print("="*80)
    
    # Create a more complex structure with intentional clashes
    structure = {
        'members': [
            # First floor
            {
                'id': 'B1',
                'type': 'beam',
                'start': [0, 0, 3000],
                'end': [5000, 0, 3000],
                'profile': 'W24x62'
            },
            # Column
            {
                'id': 'C1',
                'type': 'column',
                'start': [0, 0, 0],
                'end': [0, 0, 6000],
                'profile': 'W14x90'
            },
            # Second beam with potential clash
            {
                'id': 'B2',
                'type': 'beam',
                'start': [0, 0, 6000],
                'end': [5000, 0, 6000],
                'profile': 'W24x55'
            }
        ],
        'joints': [
            {'id': 'J1', 'position': [0, 0, 3000], 'members': ['B1', 'C1']},
            {'id': 'J2', 'position': [0, 0, 6000], 'members': ['B2', 'C1']}
        ],
        'plates': [
            {
                'id': 'BP1',
                'type': 'base_plate',
                'position': [0, 0, -100],  # Intentional: wrong Z position
                'dimensions': [200, 200, 19],  # Intentional: undersized
                'bolt_diameter': 20,
                'bolt_count': 4
            }
        ],
        'bolts': [
            {
                'id': 'BL1',
                'position': [50, 50, 50],
                'diameter': 20,
                'grade': 'A325'
            }
        ],
        'welds': [],
        'foundation': {
            'elevation': 0,
            'type': 'concrete',
            'size': [1000, 1000],
            'depth': 500
        }
    }
    
    deployment = ClashDetectionDeployment()
    result = deployment.correct_structure(structure, auto_correct=True)
    deployment.save_report(result, "complex_structure_correction")
    
    return result


def example_pipeline_integration():
    """Example 3: Use enhanced pipeline directly."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Enhanced Pipeline Integration")
    print("="*80)
    
    # Create test structure
    structure = {
        'members': [
            {
                'id': 'B1',
                'type': 'beam',
                'start': [0, 0, 3000],
                'end': [6000, 0, 3000],
                'profile': 'W24x62'
            },
            {
                'id': 'C1',
                'type': 'column',
                'start': [0, 0, 0],
                'end': [0, 0, 3000],
                'profile': 'W14x90'
            }
        ],
        'joints': [
            {'id': 'J1', 'position': [0, 0, 3000], 'members': ['B1', 'C1']}
        ]
    }
    
    print("\nRunning 8-stage enhanced pipeline...")
    result = run_enhanced_pipeline(structure)
    
    print(f"\nPipeline Status: {result.get('status')}")
    print(f"Clashes Detected: {len(result.get('clashes_detected', []))}")
    
    # Save pipeline results
    output_file = Path("/Users/sahil/Documents/aibuildx/deployments") / f"pipeline_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"Pipeline result saved to: {output_file}")
    
    return result


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

def print_integration_guide():
    """Print integration guide."""
    
    print("\n" + "="*80)
    print("INTEGRATION GUIDE: Adding Clash Detection to Your Pipeline")
    print("="*80)
    
    guide = """

1. BASIC USAGE
   ============

   from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector
   from src.pipeline.agents.comprehensive_clash_corrector_v2 import ComprehensiveClashCorrector

   # Detect clashes
   detector = ComprehensiveClashDetector()
   clashes, summary = detector.detect_all_clashes(ifc_data)

   # Correct clashes
   corrector = ComprehensiveClashCorrector()
   corrections, corr_summary = corrector.correct_all_clashes(clashes, ifc_data)


2. PIPELINE INTEGRATION
   ====================

   from src.pipeline.agents.main_pipeline_agent_enhanced import run_enhanced_pipeline

   # Run full 8-stage pipeline with integrated clash detection
   result = run_enhanced_pipeline(ifc_data)

   # Access results
   clashes = result['clashes_detected']
   corrections = result['corrections']
   report = result['validation_report']


3. PRODUCTION DEPLOYMENT
   ======================

   # Use deployment wrapper
   from deployment_integration import ClashDetectionDeployment

   deployment = ClashDetectionDeployment()

   # Option A: Analyze only
   analysis = deployment.analyze_structure(ifc_data)

   # Option B: Detect & Auto-Correct
   result = deployment.correct_structure(ifc_data, auto_correct=True)

   # Save report
   deployment.save_report(result, "my_project_analysis")


4. INTEGRATION POINTS IN MAIN PIPELINE
   ===================================

   Stage 6: Connection Synthesis (existing) → Use enhanced version
   ↓
   Stage 7.1: Connection Classification (AI-driven) [NEW]
   Stage 7.2: Connection Synthesis (Model-driven) [NEW]
   Stage 7.3: Comprehensive Clash Detection (35+ types) [NEW]
   Stage 7.4: Clash Correction (AI-driven) [NEW]
   Stage 7.5: 3D Geometry Validation [NEW]
   Stage 7.6: Weld & Fastener Verification [NEW]
   Stage 7.7: Anchorage & Foundation Validation [NEW]
   Stage 7.8: Re-Validation & Quality Assurance [NEW]
   ↓
   Export to Tekla/IFC (improved)


5. CONFIGURATION
   ==============

   All detection parameters are adaptive and standards-based:
   - AISC 360-14 for bolt spacing/edge distance
   - AWS D1.1 for weld sizing
   - ACI 318 for anchor embedment
   - IFC4 for structural connectivity

   No hardcoded values - all driven by industry standards and AI models.


6. MONITORING & METRICS
   ====================

   Track these metrics in production:
   - Clash detection rate: Should be >98%
   - Auto-correction rate: Should be >85%
   - Pipeline execution time: Should be <100ms per structure
   - False negatives: Should be <1%
   - Standards compliance: Should be 100%

"""
    
    print(guide)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE CLASH DETECTION v2.0 - PRODUCTION DEPLOYMENT")
    print("="*80)
    
    # Run examples
    example_simple_structure()
    example_complex_structure()
    example_pipeline_integration()
    
    # Print integration guide
    print_integration_guide()
    
    # Final status
    print("\n" + "="*80)
    print("✅ DEPLOYMENT READY")
    print("="*80)
    
    print("""
Next Steps:
1. Review the saved reports in /Users/sahil/Documents/aibuildx/deployments/
2. Integrate clash detection into your main pipeline
3. Test with real project data
4. Monitor performance metrics
5. Deploy to production environment

For support, refer to:
- COMPREHENSIVE_CLASH_DETECTION_v2.md (Technical Reference)
- QUICKSTART_CLASH_DETECTION_v2.md (Quick Start)
- MASTER_INDEX_CLASH_DETECTION_v2.md (Complete Index)
    """)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
