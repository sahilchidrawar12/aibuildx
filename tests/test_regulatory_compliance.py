#!/usr/bin/env python3
"""
Test suite for regulatory compliance module.
"""
import sys
import pytest
from tools.regulatory_compliance import CertificationManager, DesignAssumption


class TestDesignAssumptions:
    """Test design assumptions."""
    
    def test_create_assumption_basic(self):
        """Test creating basic assumption."""
        assumption = DesignAssumption('Steel grade', 'AISC', 'F_y = 50 ksi')
        
        assert assumption.category == 'Steel grade'
        assert assumption.standard == 'AISC'
        assert assumption.value == 'F_y = 50 ksi'
    
    def test_assumption_fields(self):
        """Test assumption field access."""
        assumption = DesignAssumption('Loading', 'ASCE7', 'Wind at 115 mph')
        
        assert hasattr(assumption, 'category')
        assert hasattr(assumption, 'standard')
        assert hasattr(assumption, 'value')


class TestCertificationManager:
    """Test certification manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        mgr = CertificationManager()
        
        assert mgr is not None
        assert isinstance(mgr, CertificationManager)
    
    def test_design_assumptions_basic(self):
        """Test design assumptions generation."""
        mgr = CertificationManager()
        
        assumptions = mgr.design_assumptions()
        
        assert 'assumptions' in assumptions
        assert isinstance(assumptions['assumptions'], dict)
        assert len(assumptions['assumptions']) >= 3
    
    def test_design_assumptions_categories(self):
        """Test assumption categories."""
        mgr = CertificationManager()
        
        assumptions = mgr.design_assumptions()
        
        categories = list(assumptions['assumptions'].keys())
        assert 'materials' in categories or len(categories) > 0
    
    def test_design_verification_checklist(self):
        """Test design verification checklist."""
        mgr = CertificationManager()
        
        checklist = mgr.design_verification_checklist()
        
        assert 'geometry' in checklist or len(checklist) >= 3
    
    def test_checklist_items_structure(self):
        """Test checklist items structure."""
        mgr = CertificationManager()
        
        checklist = mgr.design_verification_checklist()
        
        # Check geometry section exists
        assert 'geometry' in checklist
        
        geom_items = list(checklist['geometry'].keys())
        for key in geom_items[:1]:
            item = checklist['geometry'][key]
            assert 'status' in item
    
    def test_log_verification_step(self):
        """Test logging verification step."""
        mgr = CertificationManager()
        
        result = mgr.log_verification_step('Geometry', 'Check connectivity', 'PASS', 'Engineer A')
        
        assert result['step'] == 'Check connectivity'
        assert result['status'] == 'PASS'
        assert 'timestamp' in result
    
    def test_log_multiple_steps(self):
        """Test logging multiple verification steps."""
        mgr = CertificationManager()
        
        mgr.log_verification_step('Geometry', 'Step 1', 'PASS', 'Engineer')
        mgr.log_verification_step('Loading', 'Step 2', 'PASS', 'Engineer')
        mgr.log_verification_step('Analysis', 'Step 3', 'CONDITIONAL', 'Engineer')
        
        # Verify they're tracked
        assert len(mgr.verification_steps) >= 3
    
    def test_calculation_traceability(self):
        """Test calculation traceability."""
        mgr = CertificationManager()
        
        trace = mgr.calculation_traceability('CALC_001', 'Base shear calc', {'height': 100}, {'shear': 500})
        
        assert 'calculation_id' in trace
        assert trace['calculation_id'] == 'CALC_001'
    
    def test_traceability_entries(self):
        """Test traceability entry structure."""
        mgr = CertificationManager()
        
        trace = mgr.calculation_traceability('CALC_001', 'Test', {}, {})
        
        assert 'description' in trace
        assert 'reference_code' in trace
    
    def test_third_party_certification_requirements(self):
        """Test third-party certification requirements."""
        mgr = CertificationManager()
        
        requirements = mgr.third_party_certification_requirements()
        
        assert 'certifications_needed' in requirements
        assert isinstance(requirements['certifications_needed'], dict)
    
    def test_certification_types(self):
        """Test different certification types."""
        mgr = CertificationManager()
        
        requirements = mgr.third_party_certification_requirements()
        
        cert_names = list(requirements['certifications_needed'].keys())
        assert len(cert_names) >= 1
    
    def test_certification_sign_off(self):
        """Test certification sign-off."""
        mgr = CertificationManager()
        
        signoff = mgr.certification_sign_off('Alice Smith', 'PE12345', 'NY')
        
        assert signoff['certifier'] == 'Alice Smith'
        assert signoff['pe_license_number'] == 'PE12345'
        assert signoff['jurisdiction'] == 'NY'
        assert 'certification_date' in signoff
    
    def test_certification_sign_off_validity(self):
        """Test certification sign-off validity."""
        mgr = CertificationManager()
        
        signoff = mgr.certification_sign_off('Engineer', 'LIC001', 'CA')
        
        assert 'verification_items_checked' in signoff
        assert 'total_verification_items' in signoff


class TestVerificationLog:
    """Test verification log tracking."""
    
    def test_verification_log_accumulation(self):
        """Test verification log accumulation."""
        mgr = CertificationManager()
        
        steps = ['Check 1', 'Check 2', 'Check 3']
        for step in steps:
            mgr.log_verification_step('Category', step, 'PASS', 'Engineer')
        
        assert len(mgr.verification_steps) == len(steps)
    
    def test_verification_log_status_tracking(self):
        """Test status tracking in verification log."""
        mgr = CertificationManager()
        
        mgr.log_verification_step('Geom', 'Critical check', 'PASS', 'Eng')
        mgr.log_verification_step('Load', 'Review item', 'CONDITIONAL', 'Eng')
        mgr.log_verification_step('Anal', 'Concern', 'FAIL', 'Eng')
        
        statuses = [entry['status'] for entry in mgr.verification_steps]
        assert 'PASS' in statuses
        assert 'CONDITIONAL' in statuses


class TestComplianceWorkflow:
    """Test compliance workflow."""
    
    def test_complete_compliance_workflow(self):
        """Test complete compliance workflow."""
        mgr = CertificationManager()
        
        # Get assumptions
        assumptions = mgr.design_assumptions()
        assert 'assumptions' in assumptions
        
        # Get checklist
        checklist = mgr.design_verification_checklist()
        assert 'geometry' in checklist
        
        # Log steps
        mgr.log_verification_step('Geom', 'Check', 'PASS', 'Eng')
        mgr.log_verification_step('Load', 'Check', 'PASS', 'Eng')
        
        # Get traceability
        traceability = mgr.calculation_traceability('C1', 'Desc', {}, {})
        assert 'calculation_id' in traceability
        
        # Get certifications
        certs = mgr.third_party_certification_requirements()
        assert 'certifications_needed' in certs
        
        # Sign off
        signoff = mgr.certification_sign_off('Eng', 'LIC', 'NY')
        assert signoff['certifier'] == 'Eng'
    
    def test_multi_project_management(self):
        """Test managing multiple projects."""
        mgr1 = CertificationManager()
        mgr2 = CertificationManager()
        
        mgr1.log_verification_step('Geom', 'P1 Step', 'PASS', 'E')
        mgr2.log_verification_step('Geom', 'P2 Step', 'PASS', 'E')
        
        # Each manager has independent log
        assert len(mgr1.verification_steps) == 1
        assert len(mgr2.verification_steps) == 1


class TestIntegration:
    """Integration tests for regulatory compliance."""
    
    def test_full_certification_package(self):
        """Test full certification package generation."""
        mgr = CertificationManager()
        
        # Gather all compliance documents
        package = {
            'assumptions': mgr.design_assumptions(),
            'checklist': mgr.design_verification_checklist(),
            'traceability': mgr.calculation_traceability('C1', 'D', {}, {}),
            'certifications': mgr.third_party_certification_requirements(),
        }
        
        # Verify all components present
        assert 'assumptions' in package
        assert 'checklist' in package
        assert 'traceability' in package
        assert 'certifications' in package
        
        # Verify each has content
        assert len(package['assumptions']['assumptions']) > 0
        assert len(package['checklist']) > 0
    
    def test_design_flow_to_certification(self):
        """Test flow from design to certification."""
        mgr = CertificationManager()
        
        # Start with design assumptions
        design = mgr.design_assumptions()
        
        # Run verification checks
        mgr.log_verification_step('G', 'Check geometry', 'PASS', 'E')
        mgr.log_verification_step('L', 'Check loads', 'PASS', 'E')
        mgr.log_verification_step('C', 'Check capacity', 'PASS', 'E')
        
        # Get traceability
        trace = mgr.calculation_traceability('C1', 'Trace', {}, {})
        
        # Finalize with certification
        signoff = mgr.certification_sign_off('PE', 'LIC', 'NY')
        
        assert len(mgr.verification_steps) == 3
        assert signoff['certifier'] == 'PE'
    
    def test_large_verification_suite(self):
        """Test large verification suite."""
        mgr = CertificationManager()
        
        # Log many verification steps
        for i in range(20):
            status = 'PASS' if i % 2 == 0 else 'CONDITIONAL'
            mgr.log_verification_step('Cat', f'Check {i+1}', status, 'E')
        
        assert len(mgr.verification_steps) == 20
        
        # Certifications still accessible
        certs = mgr.third_party_certification_requirements()
        assert 'certifications_needed' in certs


def main():
    """Run tests."""
    pytest.main([__file__, '-v'])

if __name__ == '__main__':
    main()
