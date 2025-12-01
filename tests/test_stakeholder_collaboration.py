#!/usr/bin/env python3
"""
Test suite for stakeholder collaboration module.
"""
import sys
import pytest
from tools.stakeholder_collaboration import StakeholderManager, Stakeholder


class TestStakeholderRegistration:
    """Test stakeholder registration."""
    
    def test_register_single_stakeholder(self):
        """Test registering single stakeholder."""
        mgr = StakeholderManager()
        result = mgr.register_stakeholder('John Doe', 'ACME Corp', 'Structural', 'Engineer', 'john@acme.com')
        
        assert result['name'] == 'John Doe'
        assert result['organization'] == 'ACME Corp'
        assert result['stakeholder_id'] == 1
        assert 'registered_date' in result
    
    def test_register_multiple_stakeholders(self):
        """Test registering multiple stakeholders."""
        mgr = StakeholderManager()
        
        mgr.register_stakeholder('Alice', 'Org1', 'Structural', 'Lead', 'alice@org1.com')
        mgr.register_stakeholder('Bob', 'Org2', 'Wind', 'Specialist', 'bob@org2.com')
        mgr.register_stakeholder('Carol', 'Org3', 'Geo', 'Designer', 'carol@org3.com')
        
        assert len(mgr.stakeholders) == 3
    
    def test_stakeholder_object_creation(self):
        """Test Stakeholder dataclass."""
        s = Stakeholder('Test', 'TestOrg', 'Testing', 'Validator', 'test@test.com')
        
        assert s.name == 'Test'
        assert s.organization == 'TestOrg'
        assert s.expertise == 'Testing'


class TestExpertiseMatrix:
    """Test expertise matrix generation."""
    
    def test_expertise_matrix_empty(self):
        """Test matrix with no stakeholders."""
        mgr = StakeholderManager()
        matrix = mgr.expertise_matrix()
        
        assert matrix['total_stakeholders'] == 0
        assert len(matrix['expertise_areas']) == 0
    
    def test_expertise_matrix_single(self):
        """Test matrix with single stakeholder."""
        mgr = StakeholderManager()
        mgr.register_stakeholder('Alice', 'Org1', 'Structural', 'Lead', 'alice@org1.com')
        
        matrix = mgr.expertise_matrix()
        assert matrix['total_stakeholders'] == 1
        assert 'Structural' in matrix['expertise_areas']
        assert 'Alice' in matrix['expertise_areas']['Structural']
    
    def test_expertise_matrix_multiple_same_expertise(self):
        """Test matrix with multiple stakeholders in same expertise."""
        mgr = StakeholderManager()
        mgr.register_stakeholder('Alice', 'Org1', 'Structural', 'Lead', 'alice@org1.com')
        mgr.register_stakeholder('Bob', 'Org1', 'Structural', 'Engineer', 'bob@org1.com')
        mgr.register_stakeholder('Carol', 'Org2', 'Wind', 'Specialist', 'carol@org2.com')
        
        matrix = mgr.expertise_matrix()
        assert len(matrix['expertise_areas']['Structural']) == 2
        assert len(matrix['expertise_areas']['Wind']) == 1
    
    def test_expertise_matrix_roles(self):
        """Test role collection in matrix."""
        mgr = StakeholderManager()
        mgr.register_stakeholder('Alice', 'Org1', 'Structural', 'Lead', 'alice@org1.com')
        mgr.register_stakeholder('Bob', 'Org2', 'Wind', 'Specialist', 'bob@org2.com')
        
        matrix = mgr.expertise_matrix()
        assert 'Lead' in matrix['roles']
        assert 'Specialist' in matrix['roles']
    
    def test_expertise_matrix_team_list(self):
        """Test team list in matrix."""
        mgr = StakeholderManager()
        mgr.register_stakeholder('Alice', 'Org1', 'Structural', 'Lead', 'alice@org1.com')
        
        matrix = mgr.expertise_matrix()
        assert len(matrix['team']) == 1
        assert matrix['team'][0]['name'] == 'Alice'


class TestPilotStudyPlanning:
    """Test pilot study planning."""
    
    def test_plan_pilot_study_basic(self):
        """Test basic pilot study plan."""
        mgr = StakeholderManager()
        pilot = mgr.plan_pilot_study('TestCase', 'Building', ['Challenge1', 'Challenge2'])
        
        assert pilot['case_name'] == 'TestCase'
        assert pilot['case_type'] == 'Building'
        assert 'Challenge1' in pilot['primary_challenges']
        assert 'start_date' in pilot
        assert 'end_date' in pilot
    
    def test_plan_pilot_study_duration(self):
        """Test pilot study with custom duration."""
        mgr = StakeholderManager()
        pilot = mgr.plan_pilot_study('Case', 'Building', [], duration_weeks=16)
        
        assert pilot['duration_weeks'] == 16
        assert 'budget_estimate_hours' in pilot
    
    def test_plan_pilot_study_phases(self):
        """Test pilot study phases."""
        mgr = StakeholderManager()
        pilot = mgr.plan_pilot_study('Case', 'Building', [])
        
        assert 'study_phases' in pilot
        assert len(pilot['study_phases']) == 4
        assert 'Phase 1: Data Collection' in pilot['study_phases']
        assert 'Phase 2: Model Development' in pilot['study_phases']
    
    def test_plan_pilot_study_success_criteria(self):
        """Test pilot study success criteria."""
        mgr = StakeholderManager()
        pilot = mgr.plan_pilot_study('Case', 'Building', [])
        
        assert 'success_criteria' in pilot
        assert len(pilot['success_criteria']) >= 5
        assert any('5mm' in str(c) for c in pilot['success_criteria'])
    
    def test_plan_multiple_pilots(self):
        """Test planning multiple pilot studies."""
        mgr = StakeholderManager()
        
        mgr.plan_pilot_study('Case1', 'Building', [])
        mgr.plan_pilot_study('Case2', 'Bridge', [])
        mgr.plan_pilot_study('Case3', 'Tower', [])
        
        assert len(mgr.pilot_studies) == 3


class TestValidationStudyFramework:
    """Test validation study framework."""
    
    def test_validation_study_basic(self):
        """Test basic validation study framework."""
        mgr = StakeholderManager()
        validation = mgr.validation_study_framework('TestCase')
        
        assert validation['case'] == 'TestCase'
        assert 'date' in validation
        assert 'validation_domains' in validation
    
    def test_validation_study_domains(self):
        """Test validation domains."""
        mgr = StakeholderManager()
        validation = mgr.validation_study_framework('Case')
        
        domains = validation['validation_domains']
        assert 'Geometric Validation' in domains
        assert 'Modal Analysis' in domains
        assert 'Static Response' in domains
        assert 'Dynamic Response' in domains
        assert 'Connection Design' in domains
    
    def test_validation_domain_attributes(self):
        """Test domain attributes."""
        mgr = StakeholderManager()
        validation = mgr.validation_study_framework('Case')
        
        domain = validation['validation_domains']['Geometric Validation']
        assert 'description' in domain
        assert 'acceptance_criteria' in domain
        assert 'validator' in domain
        assert 'status' in domain
        assert domain['status'] == 'PENDING'
    
    def test_validation_recommendation(self):
        """Test final recommendation."""
        mgr = StakeholderManager()
        validation = mgr.validation_study_framework('Case')
        
        assert 'final_recommendation' in validation
        assert validation['final_recommendation'] == 'PENDING VALIDATION'


class TestFeedbackAndIteration:
    """Test feedback and iteration tracking."""
    
    def test_log_feedback_basic(self):
        """Test logging basic feedback."""
        mgr = StakeholderManager()
        feedback = mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Add damping')
        
        assert feedback['case'] == 'Case1'
        assert feedback['from_stakeholder'] == 'John'
        assert feedback['category'] == 'Model'
        assert feedback['comment'] == 'Add damping'
        assert 'timestamp' in feedback
    
    def test_log_feedback_priority(self):
        """Test feedback with priorities."""
        mgr = StakeholderManager()
        
        high = mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Critical fix', 'HIGH')
        medium = mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Nice to have', 'MEDIUM')
        low = mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Minor', 'LOW')
        
        assert high['priority'] == 'HIGH'
        assert medium['priority'] == 'MEDIUM'
        assert low['priority'] == 'LOW'
    
    def test_feedback_status(self):
        """Test feedback status tracking."""
        mgr = StakeholderManager()
        feedback = mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Comment')
        
        assert feedback['status'] == 'NEW'
        assert feedback['resolution'] is None
    
    def test_feedback_log_accumulation(self):
        """Test feedback log accumulation."""
        mgr = StakeholderManager()
        
        mgr.feedback_and_iteration('Case1', 'John', 'Model', 'Comment1')
        mgr.feedback_and_iteration('Case1', 'Jane', 'Analysis', 'Comment2')
        mgr.feedback_and_iteration('Case2', 'Bob', 'Reporting', 'Comment3')
        
        assert len(mgr.feedback_log) == 3
    
    def test_feedback_categories(self):
        """Test different feedback categories."""
        mgr = StakeholderManager()
        
        categories = ['Model', 'Analysis', 'Reporting', 'Validation', 'Documentation']
        for i, cat in enumerate(categories):
            mgr.feedback_and_iteration(f'Case{i}', 'Reviewer', cat, 'Comment')
        
        assert len(mgr.feedback_log) == len(categories)


class TestCaseStudyDocumentation:
    """Test case study documentation."""
    
    def test_case_study_basic(self):
        """Test basic case study documentation."""
        mgr = StakeholderManager()
        doc = mgr.case_study_documentation('BurjKhalifa', 'Building')
        
        assert doc['case_study'] == 'BurjKhalifa'
        assert doc['structure_info']['type'] == 'Building'
        assert 'date_generated' in doc
    
    def test_case_study_with_height(self):
        """Test case study with height."""
        mgr = StakeholderManager()
        doc = mgr.case_study_documentation('BurjKhalifa', 'Building', height_m=828)
        
        assert doc['structure_info']['height_m'] == 828
    
    def test_case_study_with_features(self):
        """Test case study with key features."""
        mgr = StakeholderManager()
        features = ['828m height', 'triangular plan', 'wind-responsive']
        doc = mgr.case_study_documentation('BurjKhalifa', 'Building', height_m=828, key_features=features)
        
        assert len(doc['structure_info']['key_features']) == 3
        assert 'triangular plan' in doc['structure_info']['key_features']
    
    def test_case_study_sections(self):
        """Test case study sections."""
        mgr = StakeholderManager()
        doc = mgr.case_study_documentation('Case', 'Building')
        
        assert 'sections' in doc
        assert len(doc['sections']) == 8
        
        section_titles = [s['section'] for s in doc['sections']]
        assert 'Executive Summary' in section_titles
        assert 'Methodology' in section_titles
        assert 'Conclusions' in section_titles
    
    def test_case_study_attachments(self):
        """Test case study attachments."""
        mgr = StakeholderManager()
        doc = mgr.case_study_documentation('Case', 'Building')
        
        assert 'attached_outputs' in doc
        assert len(doc['attached_outputs']) >= 4
        assert any('FE model' in str(a) for a in doc['attached_outputs'])


class TestIntegration:
    """Integration tests for stakeholder collaboration."""
    
    def test_full_collaboration_workflow(self):
        """Test full collaboration workflow."""
        mgr = StakeholderManager()
        
        # Register team
        mgr.register_stakeholder('Alice', 'BigStructures', 'Structural', 'Lead', 'alice@big.com')
        mgr.register_stakeholder('Bob', 'WindSolutions', 'Wind', 'Specialist', 'bob@wind.com')
        
        # Plan pilot study
        pilot = mgr.plan_pilot_study('BurjKhalifa', 'Building', 
                                     ['Wind', 'SSI', 'Construction'])
        
        # Get expertise matrix
        matrix = mgr.expertise_matrix()
        
        # Log feedback
        mgr.feedback_and_iteration('BurjKhalifa', 'Alice', 'Model', 'Add damping')
        
        # Generate documentation
        doc = mgr.case_study_documentation('BurjKhalifa', 'Building', 828)
        
        assert len(mgr.stakeholders) == 2
        assert len(mgr.pilot_studies) == 1
        assert matrix['total_stakeholders'] == 2
        assert len(mgr.feedback_log) == 1
        assert doc['case_study'] == 'BurjKhalifa'
    
    def test_multiple_case_collaboration(self):
        """Test collaboration across multiple case studies."""
        mgr = StakeholderManager()
        
        # Register stakeholders
        for i in range(3):
            mgr.register_stakeholder(f'Expert{i}', f'Org{i}', f'Field{i}', f'Role{i}', f'expert{i}@org.com')
        
        cases = ['BurjKhalifa', 'ShanghaiTower', 'AkashiKaikyo']
        for case in cases:
            mgr.plan_pilot_study(case, 'Structure', ['Challenge'])
            mgr.validation_study_framework(case)
            mgr.case_study_documentation(case, 'Structure')
        
        assert len(mgr.pilot_studies) == 3
        assert len(mgr.stakeholders) == 3
    
    def test_feedback_workflow_for_case(self):
        """Test complete feedback workflow for a case."""
        mgr = StakeholderManager()
        
        mgr.register_stakeholder('Alice', 'Org', 'Struct', 'Lead', 'alice@org.com')
        mgr.register_stakeholder('Bob', 'Org', 'Wind', 'Specialist', 'bob@org.com')
        
        case = 'TestBuilding'
        
        # Initial plan
        mgr.plan_pilot_study(case, 'Building', ['Wind'])
        
        # Feedback from reviewers
        mgr.feedback_and_iteration(case, 'Alice', 'Model', 'Include slabs', 'HIGH')
        mgr.feedback_and_iteration(case, 'Bob', 'Analysis', 'Check flutter', 'MEDIUM')
        
        assert len(mgr.feedback_log) == 2
        assert mgr.feedback_log[0]['priority'] == 'HIGH'
        assert mgr.feedback_log[1]['priority'] == 'MEDIUM'


def main():
    """Run tests."""
    pytest.main([__file__, '-v'])

if __name__ == '__main__':
    main()
