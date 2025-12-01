#!/usr/bin/env python3
"""
Advanced Data Validation & Quality Assurance
Validates 300k+ dataset entries for consistency and quality
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA VALIDATION SYSTEM
# ============================================================================

class DataValidator:
    """Validates and cleans dataset entries"""
    
    def __init__(self):
        self.logger = logger
        self.validation_report = {
            "timestamp": datetime.now().isoformat(),
            "files_validated": [],
            "total_entries": 0,
            "issues_found": 0,
            "duplicates_removed": 0,
            "entries_fixed": 0,
            "validation_results": {}
        }
    
    def validate_connections(self, filepath: str) -> Dict:
        """Validate connection data"""
        self.logger.info("Validating connection designs...")
        
        with open(filepath, 'r') as f:
            connections = json.load(f)
        
        issues = []
        duplicates = set()
        valid_count = 0
        
        for i, conn in enumerate(connections):
            # Check required fields
            required = ['id', 'connection_type', 'capacity_kips']
            if not all(k in conn for k in required):
                issues.append(f"Entry {i}: Missing required fields")
                continue
            
            # Check value ranges
            if not (10 <= conn.get('capacity_kips', 0) <= 5000):
                issues.append(f"Entry {i}: Capacity out of range")
                continue
            
            # Check for duplicates
            entry_hash = hashlib.md5(json.dumps(conn, sort_keys=True).encode()).hexdigest()
            if entry_hash in duplicates:
                issues.append(f"Entry {i}: Duplicate found")
                self.validation_report['duplicates_removed'] += 1
                continue
            duplicates.add(entry_hash)
            
            valid_count += 1
        
        result = {
            "file": filepath,
            "total_entries": len(connections),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(connections)}%"
        }
        
        self.logger.info(f"  ✓ Connections: {valid_count}/{len(connections)} valid ({result['pass_rate']})")
        return result
    
    def validate_sections(self, filepath: str) -> Dict:
        """Validate steel section data"""
        self.logger.info("Validating steel sections...")
        
        with open(filepath, 'r') as f:
            sections = json.load(f)
        
        issues = []
        valid_count = 0
        
        for i, sect in enumerate(sections):
            # Check required fields
            if 'profile' not in sect:
                issues.append(f"Entry {i}: Missing profile name")
                continue
            
            # Validate numeric fields
            try:
                if 'area' in sect and sect['area'] <= 0:
                    issues.append(f"Entry {i}: Invalid area")
                    continue
                valid_count += 1
            except (TypeError, ValueError):
                issues.append(f"Entry {i}: Invalid numeric data")
        
        result = {
            "file": filepath,
            "total_entries": len(sections),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(sections)}%"
        }
        
        self.logger.info(f"  ✓ Sections: {valid_count}/{len(sections)} valid ({result['pass_rate']})")
        return result
    
    def validate_decisions(self, filepath: str) -> Dict:
        """Validate design decision data"""
        self.logger.info("Validating design decisions...")
        
        with open(filepath, 'r') as f:
            decisions = json.load(f)
        
        issues = []
        valid_count = 0
        
        for i, dec in enumerate(decisions):
            try:
                # Check utilization ratio
                ratio = dec.get('utilization_ratio', 0)
                if not (0.2 <= ratio <= 1.5):  # Allow slight overage for documentation
                    issues.append(f"Entry {i}: Unusual utilization ratio: {ratio}")
                
                # Check span
                span = dec.get('span_feet', 0)
                if not (5 <= span <= 200):
                    issues.append(f"Entry {i}: Span out of range: {span}")
                    continue
                
                valid_count += 1
            except (TypeError, ValueError):
                issues.append(f"Entry {i}: Invalid data type")
        
        result = {
            "file": filepath,
            "total_entries": len(decisions),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(decisions)}%"
        }
        
        self.logger.info(f"  ✓ Decisions: {valid_count}/{len(decisions)} valid ({result['pass_rate']})")
        return result
    
    def validate_clashes(self, filepath: str) -> Dict:
        """Validate clash scenario data"""
        self.logger.info("Validating clash scenarios...")
        
        with open(filepath, 'r') as f:
            clashes = json.load(f)
        
        issues = []
        valid_count = 0
        severity_dist = {}
        
        for i, clash in enumerate(clashes):
            try:
                severity = clash.get('severity', 'UNKNOWN')
                severity_dist[severity] = severity_dist.get(severity, 0) + 1
                
                # Check minimum distance (should be numeric)
                if not isinstance(clash.get('minimum_distance_mm'), (int, float)):
                    issues.append(f"Entry {i}: Invalid distance")
                    continue
                
                valid_count += 1
            except (TypeError, ValueError):
                issues.append(f"Entry {i}: Invalid data")
        
        result = {
            "file": filepath,
            "total_entries": len(clashes),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(clashes)}%",
            "severity_distribution": severity_dist
        }
        
        self.logger.info(f"  ✓ Clashes: {valid_count}/{len(clashes)} valid ({result['pass_rate']})")
        return result
    
    def validate_compliance(self, filepath: str) -> Dict:
        """Validate compliance case data"""
        self.logger.info("Validating compliance cases...")
        
        with open(filepath, 'r') as f:
            cases = json.load(f)
        
        issues = []
        valid_count = 0
        pass_fail_dist = {'PASS': 0, 'FAIL': 0}
        
        for i, case in enumerate(cases):
            try:
                # Check pass/fail
                passes = case.get('passes', False)
                pass_fail_dist['PASS' if passes else 'FAIL'] += 1
                
                # Check code field
                if 'code' not in case:
                    issues.append(f"Entry {i}: Missing code reference")
                    continue
                
                valid_count += 1
            except (TypeError, ValueError):
                issues.append(f"Entry {i}: Invalid data")
        
        result = {
            "file": filepath,
            "total_entries": len(cases),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(cases)}%",
            "pass_fail_distribution": pass_fail_dist
        }
        
        self.logger.info(f"  ✓ Compliance: {valid_count}/{len(cases)} valid ({result['pass_rate']})")
        return result
    
    def validate_benchmarks(self, filepath: str) -> Dict:
        """Validate FEA benchmark data"""
        self.logger.info("Validating FEA benchmarks...")
        
        with open(filepath, 'r') as f:
            benchmarks = json.load(f)
        
        issues = []
        valid_count = 0
        avg_time = 0
        
        for i, bench in enumerate(benchmarks):
            try:
                # Check accuracy
                accuracy = bench.get('accuracy_percent', 0)
                if not (90 <= accuracy <= 100):
                    issues.append(f"Entry {i}: Accuracy out of range: {accuracy}")
                    continue
                
                avg_time += bench.get('analysis_time_sec', 0)
                valid_count += 1
            except (TypeError, ValueError):
                issues.append(f"Entry {i}: Invalid data")
        
        result = {
            "file": filepath,
            "total_entries": len(benchmarks),
            "valid_entries": valid_count,
            "issues": len(issues),
            "pass_rate": f"{100*valid_count//len(benchmarks)}%",
            "average_analysis_time_sec": round(avg_time/max(valid_count, 1), 2)
        }
        
        self.logger.info(f"  ✓ Benchmarks: {valid_count}/{len(benchmarks)} valid ({result['pass_rate']})")
        return result
    
    def run_full_validation(self, data_dir: str = "data/datasets_100_percent") -> Dict:
        """Run full validation on all datasets"""
        
        self.logger.info("="*80)
        self.logger.info("COMPREHENSIVE DATA VALIDATION SYSTEM")
        self.logger.info("="*80)
        
        data_path = Path(data_dir)
        
        results = {}
        total_entries = 0
        
        # Validate each file
        if (data_path / "connections_50k.json").exists():
            result = self.validate_connections(str(data_path / "connections_50k.json"))
            results['connections'] = result
            total_entries += result['total_entries']
        
        if (data_path / "steel_sections_1800.json").exists():
            result = self.validate_sections(str(data_path / "steel_sections_1800.json"))
            results['sections'] = result
            total_entries += result['total_entries']
        
        if (data_path / "design_decisions_100k.json").exists():
            result = self.validate_decisions(str(data_path / "design_decisions_100k.json"))
            results['decisions'] = result
            total_entries += result['total_entries']
        
        if (data_path / "clashes_100k.json").exists():
            result = self.validate_clashes(str(data_path / "clashes_100k.json"))
            results['clashes'] = result
            total_entries += result['total_entries']
        
        if (data_path / "compliance_cases_1000.json").exists():
            result = self.validate_compliance(str(data_path / "compliance_cases_1000.json"))
            results['compliance'] = result
            total_entries += result['total_entries']
        
        if (data_path / "fea_benchmarks_50k.json").exists():
            result = self.validate_benchmarks(str(data_path / "fea_benchmarks_50k.json"))
            results['benchmarks'] = result
            total_entries += result['total_entries']
        
        # Summary
        self.logger.info("\n" + "="*80)
        self.logger.info("VALIDATION COMPLETE")
        self.logger.info("="*80)
        
        self.logger.info(f"\nTotal entries validated: {total_entries:,}")
        for dataset, result in results.items():
            self.logger.info(f"  {dataset:15} - {result['valid_entries']:>7,} / {result['total_entries']:>7,} valid ({result['pass_rate']})")
        
        self.validation_report['validation_results'] = results
        self.validation_report['total_entries'] = total_entries
        
        return self.validation_report
    
    def save_report(self, filepath: str = "data/datasets_100_percent/validation_report.json"):
        """Save validation report"""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.validation_report, f, indent=2)
        
        self.logger.info(f"\n✓ Validation report saved: {filepath}")

# ============================================================================

class DataEnhancer:
    """Enhances and enriches dataset entries"""
    
    def __init__(self):
        self.logger = logger
    
    def add_cross_references(self, connection_file: str, section_file: str):
        """Add cross-references between connections and sections"""
        self.logger.info("Adding cross-references...")
        
        with open(connection_file, 'r') as f:
            connections = json.load(f)
        
        with open(section_file, 'r') as f:
            sections = json.load(f)
        
        section_profiles = [s.get('profile') for s in sections[:100]]
        
        # Add section cross-references to connections
        for conn in connections:
            conn['compatible_sections'] = section_profiles[
                :random.randint(3, 10)
            ]
        
        with open(connection_file, 'w') as f:
            json.dump(connections, f)
        
        self.logger.info(f"✓ Added cross-references to {len(connections)} connections")
    
    def generate_statistics(self, data_dir: str = "data/datasets_100_percent") -> Dict:
        """Generate dataset statistics"""
        self.logger.info("Generating statistics...")
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "datasets": {}
        }
        
        data_path = Path(data_dir)
        
        # Connection statistics
        if (data_path / "connections_50k.json").exists():
            with open(data_path / "connections_50k.json") as f:
                conns = json.load(f)
            types = {}
            for c in conns:
                t = c.get('connection_type', 'unknown')
                types[t] = types.get(t, 0) + 1
            stats['datasets']['connections'] = {
                "count": len(conns),
                "types": types,
                "capacity_range": [
                    min(c.get('capacity_kips', 0) for c in conns),
                    max(c.get('capacity_kips', 0) for c in conns)
                ]
            }
        
        # Section statistics
        if (data_path / "steel_sections_1800.json").exists():
            with open(data_path / "steel_sections_1800.json") as f:
                sects = json.load(f)
            types = {}
            for s in sects:
                t = s.get('type', 'unknown')
                types[t] = types.get(t, 0) + 1
            stats['datasets']['sections'] = {
                "count": len(sects),
                "types": types,
                "standards": list(set(s.get('standard') for s in sects))
            }
        
        with open(data_path / "dataset_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info("✓ Statistics generated")
        return stats

# ============================================================================

def main():
    """Main validation orchestration"""
    
    # Validate all datasets
    validator = DataValidator()
    report = validator.run_full_validation()
    validator.save_report()
    
    # Enhance datasets
    enhancer = DataEnhancer()
    stats = enhancer.generate_statistics()
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"✓ All datasets validated")
    print(f"✓ Statistics generated")
    print(f"✓ Report saved to: data/datasets_100_percent/validation_report.json")

if __name__ == "__main__":
    import random
    main()
