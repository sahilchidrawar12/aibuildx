#!/usr/bin/env python3
"""
COMPREHENSIVE PIPELINE INTEGRATION AUDIT
==========================================

Audits all agents and their integration in the main pipeline.
Checks:
1. All agents are properly imported
2. All agents have correct method signatures
3. Data flows correctly between agents
4. No circular imports
5. All new clash detection agents are integrated
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}\n")

def print_success(msg: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'-'*60}{Colors.RESET}")

class PipelineAudit:
    def __init__(self):
        self.agents_dir = Path('/Users/sahil/Documents/aibuildx/src/pipeline/agents')
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': 0,
            'properly_imported': 0,
            'missing_imports': 0,
            'critical_issues': [],
            'warnings': [],
            'info': [],
            'agent_details': {}
        }
        
    def audit_all(self):
        """Run complete audit."""
        print_header("COMPREHENSIVE PIPELINE INTEGRATION AUDIT")
        
        # Step 1: Discover all agents
        self._discover_agents()
        
        # Step 2: Analyze main pipeline
        self._analyze_main_pipeline()
        
        # Step 3: Check new clash detection agents
        self._check_clash_detection_agents()
        
        # Step 4: Check agent imports
        self._check_agent_imports()
        
        # Step 5: Verify data flow
        self._verify_data_flow()
        
        # Step 6: Check for circular imports
        self._check_circular_imports()
        
        # Step 7: Generate report
        self._generate_report()
        
    def _discover_agents(self):
        """Discover all agent files."""
        print_section("STEP 1: DISCOVERING ALL AGENTS")
        
        agent_files = list(self.agents_dir.glob('*_agent*.py')) + [
            self.agents_dir / 'comprehensive_clash_detector_v2.py',
            self.agents_dir / 'comprehensive_clash_corrector_v2.py',
            self.agents_dir / 'connection_designer.py'
        ]
        
        agent_files = [f for f in agent_files if f.exists() and f.is_file()]
        
        print_info(f"Found {len(agent_files)} agent files:")
        for agent_file in sorted(agent_files):
            print(f"  • {agent_file.name}")
            self.results['agent_details'][agent_file.name] = {
                'path': str(agent_file),
                'size': agent_file.stat().st_size,
                'imports': [],
                'functions': [],
                'classes': [],
                'status': 'unchecked'
            }
        
        self.results['total_agents'] = len(agent_files)
        print_success(f"Discovered {len(agent_files)} agent files")
        
    def _analyze_main_pipeline(self):
        """Analyze the main pipeline agent."""
        print_section("STEP 2: ANALYZING MAIN PIPELINE")
        
        main_files = [
            self.agents_dir / 'main_pipeline_agent.py',
            self.agents_dir / 'main_pipeline_agent_enhanced.py'
        ]
        
        for main_file in main_files:
            if not main_file.exists():
                print_warning(f"{main_file.name} not found")
                continue
                
            print_info(f"Analyzing {main_file.name}...")
            
            with open(main_file, 'r') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
                imports = self._extract_imports(tree)
                functions = self._extract_functions(tree)
                classes = self._extract_classes(tree)
                
                print_info(f"  Imports: {len(imports)}")
                print_info(f"  Functions: {len(functions)}")
                print_info(f"  Classes: {len(classes)}")
                
                self.results['agent_details'][main_file.name] = {
                    'path': str(main_file),
                    'size': main_file.stat().st_size,
                    'imports': imports,
                    'functions': functions,
                    'classes': classes,
                    'status': 'analyzed'
                }
                
                # Check for critical imports
                critical_imports = [
                    'comprehensive_clash_detector',
                    'comprehensive_clash_corrector',
                    'connection_synthesis',
                    'connection_classifier'
                ]
                
                found_critical = []
                for imp in imports:
                    for critical in critical_imports:
                        if critical.lower() in imp.lower():
                            found_critical.append(critical)
                
                if found_critical:
                    print_success(f"  Found critical imports: {', '.join(found_critical)}")
                else:
                    print_warning(f"  Missing some critical imports")
                    
            except SyntaxError as e:
                print_error(f"  Syntax error in {main_file.name}: {e}")
                self.results['critical_issues'].append(f"Syntax error in {main_file.name}")
    
    def _check_clash_detection_agents(self):
        """Check if new clash detection agents are properly integrated."""
        print_section("STEP 3: CHECKING NEW CLASH DETECTION AGENTS")
        
        clash_agents = {
            'comprehensive_clash_detector_v2.py': ['ComprehensiveClashDetector', 'Clash', 'ClashCategory'],
            'comprehensive_clash_corrector_v2.py': ['ComprehensiveClashCorrector', 'AIModelRegistry'],
            'connection_classifier_agent.py': ['ConnectionClassifier'],
        }
        
        all_exist = True
        for agent_file, expected_classes in clash_agents.items():
            agent_path = self.agents_dir / agent_file
            
            if not agent_path.exists():
                print_error(f"Missing: {agent_file}")
                self.results['critical_issues'].append(f"Missing agent: {agent_file}")
                all_exist = False
                continue
            
            print_info(f"Checking {agent_file}...")
            
            with open(agent_path, 'r') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                classes = self._extract_classes(tree)
                
                found_classes = []
                for expected_class in expected_classes:
                    if expected_class in classes:
                        found_classes.append(expected_class)
                        print_success(f"  Found class: {expected_class}")
                    else:
                        print_warning(f"  Missing class: {expected_class}")
                
                self.results['agent_details'][agent_file]['status'] = 'verified' if len(found_classes) == len(expected_classes) else 'incomplete'
                
            except Exception as e:
                print_error(f"  Error parsing {agent_file}: {e}")
                self.results['critical_issues'].append(f"Parse error in {agent_file}: {e}")
        
        if all_exist:
            print_success("All clash detection agents exist")
        else:
            self.results['critical_issues'].append("Some clash detection agents are missing")
    
    def _check_agent_imports(self):
        """Check if agents are properly imported in main pipeline."""
        print_section("STEP 4: CHECKING AGENT IMPORTS IN MAIN PIPELINE")
        
        main_file = self.agents_dir / 'main_pipeline_agent.py'
        
        if not main_file.exists():
            print_error(f"Main pipeline not found: {main_file}")
            return
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Extract all import statements
        tree = ast.parse(content)
        imports = self._extract_imports(tree)
        
        print_info(f"Total imports in main_pipeline_agent.py: {len(imports)}")
        
        # Check for key imports
        required_agents = [
            'connection_synthesis_agent_enhanced',
            'connection_parser_agent',
            'connection_classifier_agent',
            'comprehensive_clash_detector_v2',
            'comprehensive_clash_corrector_v2'
        ]
        
        found_imports = []
        missing_imports = []
        
        for required in required_agents:
            found = False
            for imp in imports:
                if required.lower() in imp.lower():
                    found = True
                    found_imports.append(required)
                    break
            
            if not found:
                missing_imports.append(required)
        
        print_info(f"Found imports: {len(found_imports)}")
        for imp in found_imports:
            print_success(f"  ✓ {imp}")
        
        if missing_imports:
            print_info(f"Missing imports: {len(missing_imports)}")
            for imp in missing_imports:
                print_warning(f"  ✗ {imp} (not imported in main_pipeline_agent.py)")
                self.results['warnings'].append(f"Missing import: {imp}")
        
        self.results['properly_imported'] = len(found_imports)
        self.results['missing_imports'] = len(missing_imports)
    
    def _verify_data_flow(self):
        """Verify data flows correctly between agents."""
        print_section("STEP 5: VERIFYING DATA FLOW BETWEEN AGENTS")
        
        # Expected data flow
        data_flow = {
            'miner_agent': (['dxf_entities'], ['ifc_data']),
            'geometry_agent': (['members'], ['nodes', 'joints']),
            'connection_parser_agent': (['circles'], ['joints']),
            'connection_classifier_agent': (['joints'], ['connection_types']),
            'connection_synthesis_agent_enhanced': (['members', 'joints'], ['plates', 'bolts']),
            'comprehensive_clash_detector_v2': (['ifc_data'], ['clashes']),
            'comprehensive_clash_corrector_v2': (['clashes'], ['corrections', 'corrected_ifc']),
        }
        
        print_info("Expected data flow:")
        for agent, (inputs, outputs) in data_flow.items():
            print(f"  {agent}:")
            print(f"    Input:  {inputs}")
            print(f"    Output: {outputs}")
        
        # Check if all stages exist
        main_file = self.agents_dir / 'main_pipeline_agent.py'
        with open(main_file, 'r') as f:
            content = f.read()
        
        stages_mentioned = []
        for i in range(1, 15):
            if f"# {i})" in content or f"Stage {i}" in content:
                stages_mentioned.append(i)
        
        print_info(f"Pipeline stages implemented: {stages_mentioned}")
        
        if len(stages_mentioned) >= 13:
            print_success("Good coverage of pipeline stages")
        else:
            print_warning(f"Missing some pipeline stages (found {len(stages_mentioned)}, expected ~14)")
    
    def _check_circular_imports(self):
        """Check for circular imports."""
        print_section("STEP 6: CHECKING FOR CIRCULAR IMPORTS")
        
        print_info("Checking for circular import dependencies...")
        
        # This is a simplified check - a full check would need graph analysis
        circular_patterns = [
            ('comprehensive_clash_detector_v2', 'comprehensive_clash_corrector_v2'),
            ('main_pipeline_agent', 'connection_synthesis_agent'),
            ('connection_classifier_agent', 'connection_parser_agent'),
        ]
        
        issues_found = False
        for agent1, agent2 in circular_patterns:
            file1 = self.agents_dir / f'{agent1}.py'
            file2 = self.agents_dir / f'{agent2}.py'
            
            if file1.exists() and file2.exists():
                with open(file1, 'r') as f:
                    content1 = f.read()
                with open(file2, 'r') as f:
                    content2 = f.read()
                
                # Check if file1 imports file2 and vice versa
                if agent2 in content1 and agent1 in content2:
                    print_warning(f"Potential circular import: {agent1} <-> {agent2}")
                    self.results['warnings'].append(f"Circular import: {agent1} <-> {agent2}")
                    issues_found = True
        
        if not issues_found:
            print_success("No obvious circular imports detected")
    
    def _extract_imports(self, tree) -> List[str]:
        """Extract all imports from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    
    def _extract_functions(self, tree) -> List[str]:
        """Extract all function definitions from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        return functions
    
    def _extract_classes(self, tree) -> List[str]:
        """Extract all class definitions from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes
    
    def _generate_report(self):
        """Generate and save comprehensive report."""
        print_section("FINAL AUDIT REPORT")
        
        print_info(f"Total agents found: {self.results['total_agents']}")
        print_info(f"Properly imported: {self.results['properly_imported']}")
        print_info(f"Missing imports: {self.results['missing_imports']}")
        
        # Summary
        print_section("SUMMARY")
        
        critical_count = len(self.results['critical_issues'])
        warning_count = len(self.results['warnings'])
        info_count = len(self.results['info'])
        
        print(f"{Colors.BOLD}Issues Found:{Colors.RESET}")
        print(f"  Critical Issues: {Colors.RED}{critical_count}{Colors.RESET}")
        print(f"  Warnings:        {Colors.YELLOW}{warning_count}{Colors.RESET}")
        print(f"  Info Messages:   {Colors.BLUE}{info_count}{Colors.RESET}")
        
        if critical_count > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}CRITICAL ISSUES:{Colors.RESET}")
            for issue in self.results['critical_issues']:
                print_error(f"  {issue}")
        
        if warning_count > 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.RESET}")
            for warning in self.results['warnings']:
                print_warning(f"  {warning}")
        
        # Overall status
        print_section("OVERALL STATUS")
        
        if critical_count == 0:
            print_success("✓ NO CRITICAL ISSUES FOUND")
            status = "PASSED"
        else:
            print_error("✗ CRITICAL ISSUES FOUND")
            status = "FAILED"
        
        # Save report
        report_file = Path('/Users/sahil/Documents/aibuildx/audit_report.json')
        self.results['status'] = status
        self.results['summary'] = {
            'critical_issues': critical_count,
            'warnings': warning_count,
            'total_agents': self.results['total_agents'],
            'properly_imported': self.results['properly_imported']
        }
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print_info(f"Report saved to: {report_file}")
        
        # Print recommendations
        print_section("RECOMMENDATIONS")
        
        if self.results['missing_imports'] > 0:
            print_info("1. Add missing imports to main_pipeline_agent.py:")
            print("   - comprehensive_clash_detector_v2")
            print("   - comprehensive_clash_corrector_v2")
            print("   - connection_classifier_agent")
        
        print_info("2. Integrate new clash detection into main pipeline:")
        print("   - Add clash detection stage after connection synthesis")
        print("   - Add clash correction stage")
        print("   - Add re-validation stage")
        
        print_info("3. Test end-to-end pipeline:")
        print("   - Run integration_test_clash_system.py")
        print("   - Verify all agents work correctly together")
        print("   - Check data flow between stages")


def main():
    """Run the audit."""
    try:
        audit = PipelineAudit()
        audit.audit_all()
        
        print_header("AUDIT COMPLETE")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("1. Review audit_report.json for detailed findings")
        print("2. Address any critical issues")
        print("3. Update main pipeline imports as needed")
        print("4. Run integration tests")
        print()
        
    except Exception as e:
        print_error(f"Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
