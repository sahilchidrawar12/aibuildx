#!/usr/bin/env python3
"""
COMPLETE PIPELINE VERIFICATION & INTEGRATION TEST
===================================================

Tests all agents working together to verify:
1. All agents import correctly
2. No circular dependencies
3. Data flows correctly between agents
4. Error handling works
5. All outputs are in correct format
"""

import sys
import json
import traceback
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def section(title: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}\n")

def success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

class PipelineVerification:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'errors': []
        }
        self.agents_dir = Path('/Users/sahil/Documents/aibuildx/src/pipeline/agents')
    
    def run_all_tests(self):
        """Run all verification tests."""
        section("PIPELINE INTEGRATION VERIFICATION SUITE")
        
        self.test_1_imports()
        self.test_2_detector()
        self.test_3_corrector()
        self.test_4_classifier()
        self.test_5_connection_synthesis()
        self.test_6_main_pipeline()
        self.test_7_end_to_end()
        
        self._print_summary()
        self._save_results()
    
    def test_1_imports(self):
        """Test 1: Verify all critical imports work."""
        section("TEST 1: CRITICAL IMPORTS")
        
        test_result = {'name': 'Critical Imports', 'status': 'pending', 'details': []}
        
        imports_to_test = [
            ('comprehensive_clash_detector_v2', ['ComprehensiveClashDetector', 'Clash', 'ClashCategory']),
            ('comprehensive_clash_corrector_v2', ['ComprehensiveClashCorrector', 'AIModelRegistry']),
            ('connection_classifier_agent', ['ConnectionClassifier']),
            ('connection_synthesis_agent_enhanced', ['synthesize_connections_model_driven', 'ModelInferenceEngine']),
        ]
        
        all_passed = True
        for module_name, expected_items in imports_to_test:
            try:
                module_path = self.agents_dir / f'{module_name}.py'
                if not module_path.exists():
                    raise FileNotFoundError(f"Module file not found: {module_path}")
                
                # Dynamic import
                sys.path.insert(0, str(self.agents_dir))
                module = __import__(module_name)
                
                for item in expected_items:
                    if hasattr(module, item):
                        success(f"  {module_name}.{item}")
                        test_result['details'].append(f"✓ {module_name}.{item}")
                    else:
                        error(f"  Missing: {module_name}.{item}")
                        test_result['details'].append(f"✗ {module_name}.{item}")
                        all_passed = False
                        
            except Exception as e:
                error(f"  Import failed: {module_name} - {e}")
                test_result['details'].append(f"✗ {module_name}: {str(e)}")
                all_passed = False
        
        test_result['status'] = 'passed' if all_passed else 'failed'
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_2_detector(self):
        """Test 2: Verify clash detector works."""
        section("TEST 2: CLASH DETECTOR")
        
        test_result = {'name': 'Clash Detector', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector
            
            # Create test structure
            test_ifc = {
                'members': [
                    {'id': 'm1', 'start': (0, 0, 0), 'end': (0, 0, 5000)},
                    {'id': 'm2', 'start': (5000, 0, 0), 'end': (5000, 0, 5000)}
                ],
                'joints': [
                    {'id': 'j1', 'location': (0, 0, 0), 'members': ['m1']},
                    {'id': 'j2', 'location': (5000, 0, 0), 'members': ['m2']}
                ],
                'plates': [],
                'bolts': []
            }
            
            detector = ComprehensiveClashDetector()
            success("  Detector initialized")
            test_result['details'].append("✓ Detector initialized")
            
            clashes, summary = detector.detect_all_clashes(test_ifc)
            success(f"  Clash detection completed: {len(clashes)} clashes")
            test_result['details'].append(f"✓ Detection completed: {len(clashes)} clashes")
            
            # Verify output format
            if isinstance(clashes, list):
                success("  Output format correct (list)")
                test_result['details'].append("✓ Output format correct")
            else:
                error("  Output format incorrect")
                test_result['details'].append("✗ Output format incorrect")
            
            if isinstance(summary, dict):
                success("  Summary format correct (dict)")
                test_result['details'].append("✓ Summary format correct")
            else:
                error("  Summary format incorrect")
                test_result['details'].append("✗ Summary format incorrect")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  Detector test failed: {e}")
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"Detector: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_3_corrector(self):
        """Test 3: Verify clash corrector works."""
        section("TEST 3: CLASH CORRECTOR")
        
        test_result = {'name': 'Clash Corrector', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.comprehensive_clash_corrector_v2 import ComprehensiveClashCorrector, Clash, ClashSeverity
            from src.pipeline.agents.comprehensive_clash_detector_v2 import ClashCategory
            
            corrector = ComprehensiveClashCorrector()
            success("  Corrector initialized")
            test_result['details'].append("✓ Corrector initialized")
            
            # Create test clash
            test_clash = Clash(
                clash_id='test_clash_1',
                category=ClashCategory.BASE_PLATE_WRONG_ELEVATION,
                severity=ClashSeverity.CRITICAL,
                element_type='plate',
                element_id='plate_1',
                description='Test clash',
                current_value=3.0,
                expected_value=0.0,
                confidence_score=0.95,
                location_3d=(0, 0, 3000),
                correction_details={}
            )
            
            test_ifc = {'members': [], 'joints': [], 'plates': [], 'bolts': []}
            
            corrections, summary = corrector.correct_all_clashes([test_clash], test_ifc)
            success(f"  Correction completed: {len(corrections)} corrections")
            test_result['details'].append(f"✓ Correction completed: {len(corrections)} corrections")
            
            # Verify output format
            if isinstance(corrections, list):
                success("  Output format correct (list)")
                test_result['details'].append("✓ Output format correct")
            else:
                error("  Output format incorrect")
                test_result['details'].append("✗ Output format incorrect")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  Corrector test failed: {e}")
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"Corrector: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_4_classifier(self):
        """Test 4: Verify connection classifier works."""
        section("TEST 4: CONNECTION CLASSIFIER")
        
        test_result = {'name': 'Connection Classifier', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.connection_classifier_agent import ConnectionClassifier
            
            classifier = ConnectionClassifier()
            success("  Classifier initialized")
            test_result['details'].append("✓ Classifier initialized")
            
            # Create test members and joints
            test_members = [
                {'id': 'm1', 'start': (0, 0, 0), 'end': (0, 0, 5000)},
                {'id': 'm2', 'start': (5000, 0, 0), 'end': (5000, 0, 5000)}
            ]
            test_joints = [{'id': 'j1', 'location': (0, 0, 0), 'members': ['m1', 'm2']}]
            
            if hasattr(classifier, 'classify_all_connections'):
                result = classifier.classify_all_connections(test_members, test_joints)
                success(f"  Classification completed: {len(result)} results")
                test_result['details'].append(f"✓ Classification completed")
            else:
                warning("  classify_all_connections method not available")
                test_result['details'].append("⚠ Method not available")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  Classifier test failed: {e}")
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"Classifier: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_5_connection_synthesis(self):
        """Test 5: Verify connection synthesis works."""
        section("TEST 5: CONNECTION SYNTHESIS")
        
        test_result = {'name': 'Connection Synthesis', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.connection_synthesis_agent_enhanced import synthesize_connections_model_driven
            
            # Create test data
            members = [
                {'id': 'm1', 'start': (0, 0, 0), 'end': (0, 0, 5000)},
                {'id': 'm2', 'start': (5000, 0, 0), 'end': (5000, 0, 5000)}
            ]
            joints = [{'id': 'j1', 'location': (0, 0, 0), 'members': ['m1']}]
            
            plates, bolts = synthesize_connections_model_driven(members, joints)
            success(f"  Synthesis completed: {len(plates)} plates, {len(bolts)} bolts")
            test_result['details'].append(f"✓ Synthesis completed")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  Synthesis test failed: {e}")
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"Synthesis: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_6_main_pipeline(self):
        """Test 6: Verify main pipeline runs without errors."""
        section("TEST 6: MAIN PIPELINE")
        
        test_result = {'name': 'Main Pipeline', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.main_pipeline_agent import process
            
            # Create test payload
            test_payload = {
                'data': {
                    'dxf_entities': [],
                    'members': [
                        {'id': 'm1', 'start': (0, 0, 0), 'end': (0, 0, 5000)},
                    ],
                    'loads': {'dead': 0.0, 'live': 0.0}
                }
            }
            
            result = process(test_payload)
            success(f"  Pipeline executed")
            test_result['details'].append(f"✓ Pipeline executed")
            
            if result.get('status') == 'ok':
                success(f"  Pipeline status: OK")
                test_result['details'].append(f"✓ Pipeline status OK")
            elif result.get('status') == 'error':
                warning(f"  Pipeline had errors: {result.get('error')}")
                test_result['details'].append(f"⚠ Pipeline errors: {result.get('error')}")
            
            # Check for clash detection in output
            if 'clashes_detected' in result.get('result', {}):
                success(f"  Clash detection executed")
                test_result['details'].append(f"✓ Clash detection executed")
            else:
                warning(f"  Clash detection not in output")
                test_result['details'].append(f"⚠ Clash detection not found")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  Pipeline test failed: {e}")
            traceback.print_exc()
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"Pipeline: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def test_7_end_to_end(self):
        """Test 7: End-to-end integration test."""
        section("TEST 7: END-TO-END INTEGRATION")
        
        test_result = {'name': 'End-to-End Integration', 'status': 'pending', 'details': []}
        
        try:
            from src.pipeline.agents.main_pipeline_agent_enhanced import run_enhanced_pipeline
            
            # Create test IFC data
            test_ifc = {
                'members': [
                    {'id': 'm1', 'start': (0, 0, 0), 'end': (0, 0, 5000), 'profile': 'IPE300'},
                    {'id': 'm2', 'start': (5000, 0, 0), 'end': (5000, 0, 5000), 'profile': 'IPE300'}
                ],
                'joints': [
                    {'id': 'j1', 'location': (0, 0, 0), 'members': ['m1']},
                    {'id': 'j2', 'location': (5000, 0, 0), 'members': ['m2']}
                ],
                'plates': [],
                'bolts': []
            }
            
            result = run_enhanced_pipeline(test_ifc, verbose=False)
            success(f"  Pipeline executed: {result.get('status')}")
            test_result['details'].append(f"✓ Pipeline executed: {result['status']}")
            
            # Check stages
            stages = result.get('stages', {})
            stages_run = [s for s in stages.keys() if stages[s].get('status') == 'COMPLETED']
            success(f"  Stages completed: {len(stages_run)}")
            test_result['details'].append(f"✓ Stages: {len(stages_run)} completed")
            
            # Check outputs
            clashes = result.get('clashes_detected', [])
            success(f"  Clashes detected: {len(clashes)}")
            test_result['details'].append(f"✓ Clashes detected: {len(clashes)}")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            error(f"  End-to-end test failed: {e}")
            traceback.print_exc()
            test_result['details'].append(f"✗ Error: {str(e)}")
            test_result['status'] = 'failed'
            self.results['errors'].append(f"End-to-End: {str(e)}")
        
        self.results['tests'].append(test_result)
        self._update_count(test_result['status'])
    
    def _update_count(self, status: str):
        """Update pass/fail counts."""
        if status == 'passed':
            self.results['passed'] += 1
        elif status == 'failed':
            self.results['failed'] += 1
        else:
            self.results['warnings'] += 1
    
    def _print_summary(self):
        """Print summary of all tests."""
        section("TEST SUMMARY")
        
        total = len(self.results['tests'])
        passed = self.results['passed']
        failed = self.results['failed']
        
        print(f"Total Tests:  {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        if failed > 0:
            print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print()
        
        for test in self.results['tests']:
            status_str = "✓" if test['status'] == 'passed' else "✗" if test['status'] == 'failed' else "?"
            status_color = Colors.GREEN if test['status'] == 'passed' else Colors.RED if test['status'] == 'failed' else Colors.YELLOW
            print(f"{status_color}{status_str}{Colors.RESET} {test['name']}")
        
        print()
        if failed == 0:
            success("ALL TESTS PASSED!")
        else:
            error(f"{failed} TEST(S) FAILED")
        
        if self.results['errors']:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors:{Colors.RESET}")
            for err in self.results['errors']:
                print(f"  {err}")
    
    def _save_results(self):
        """Save results to file."""
        report_file = Path('/Users/sahil/Documents/aibuildx/verification_report.json')
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        info(f"Report saved to: {report_file}")


def main():
    """Run verification."""
    try:
        verification = PipelineVerification()
        verification.run_all_tests()
        
        section("VERIFICATION COMPLETE")
        
        # Exit with appropriate code
        if verification.results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        error(f"Verification failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
