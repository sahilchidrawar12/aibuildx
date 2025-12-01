"""Comprehensive tests for all 17 pipeline agents and key functions."""
import os
import json
import uuid
import pytest
from src.pipeline import pipeline_v2 as pv2


class TestAgents:
    """Test all 17 agents."""

    @pytest.fixture
    def sample_members(self):
        """Create a small sample frame for testing."""
        return [
            {'id': str(uuid.uuid4()), 'start': [0.0, 0.0, 0.0], 'end': [6.0, 0.0, 0.0], 'length': 6.0, 'layer': 'BEAMS'},
            {'id': str(uuid.uuid4()), 'start': [6.0, 0.0, 0.0], 'end': [6.0, 0.0, 4.0], 'length': 4.0, 'layer': 'COLUMNS'},
            {'id': str(uuid.uuid4()), 'start': [0.0, 0.0, 0.0], 'end': [0.0, 6.0, 0.0], 'length': 6.0, 'layer': 'BEAMS'},
        ]

    def test_agent_1_miner(self, sample_members):
        """Test Miner agent (extract geometry from DXF/IFC)."""
        result = pv2.miner_from_dxf(sample_members)
        assert 'members' in result
        assert len(result['members']) == 3
        assert all('id' in m and 'start' in m and 'end' in m for m in result['members'])

    def test_agent_2_engineer(self, sample_members):
        """Test Engineer agent (standardize raw data)."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        assert 'members' in eng_out
        assert all('type' in m and m['type'] in ['beam', 'column', 'brace'] for m in eng_out['members'])
        assert all('orientation' in m and 'midpoint' in m for m in eng_out['members'])

    def test_agent_3_load_path_resolver(self, sample_members):
        """Test Load Path Resolver agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        assert 'members' in load_out
        assert all('loads' in m for m in load_out['members'])
        assert all('axial_kN' in m.get('loads', {}) for m in load_out['members'])

    def test_agent_4_stability(self, sample_members):
        """Test Stability Agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        assert 'members' in stab_out
        assert all('stability' in m for m in stab_out['members'])
        assert all('slenderness' in m.get('stability', {}) for m in stab_out['members'])

    def test_agent_5_optimizer(self, sample_members):
        """Test Optimizer agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        assert 'members' in opt_out
        assert all('selection' in m for m in opt_out['members'])
        assert all('section_name' in m.get('selection', {}) for m in opt_out['members'])
        assert 'totals' in opt_out and 'weight_kg' in opt_out['totals']

    def test_agent_6_connection_designer(self, sample_members):
        """Test Connection Designer agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        assert 'members' in conn_out
        assert all('connection' in m for m in conn_out['members'])

    def test_agent_7_fabrication_detailing(self, sample_members):
        """Test Fabrication Detailing agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        assert 'members' in fab_out
        assert all('fabrication' in m for m in fab_out['members'])

    def test_agent_8_fabrication_standards(self, sample_members):
        """Test Fabrication Standards agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        assert 'members' in std_out

    def test_agent_9_erection_planner(self, sample_members):
        """Test Erection Planner agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        erec_out = pv2.erection_planner(std_out)
        assert all('erection_order' in m for m in erec_out['members'])

    def test_agent_10_safety_compliance(self, sample_members):
        """Test Safety Compliance agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        erec_out = pv2.erection_planner(std_out)
        safe_out = pv2.safety_compliance(erec_out)
        assert all('safety' in m for m in safe_out['members'])

    def test_agent_11_analysis_model_generator(self, sample_members):
        """Test Analysis Model Generator agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        erec_out = pv2.erection_planner(std_out)
        safe_out = pv2.safety_compliance(erec_out)
        ana_out = pv2.analysis_model_generator(safe_out)
        assert 'nodes' in ana_out and 'elements' in ana_out

    def test_agent_12_builder_ifc(self, sample_members, tmp_path):
        """Test Builder IFC agent."""
        try:
            import ifcopenshell
        except Exception:
            pytest.skip("ifcopenshell not installed; skipping IFC builder test")
        sample = pv2.miner_from_dxf(sample_members)
        result = pv2.builder_ifc(sample, out_path=os.path.join(str(tmp_path), 'test.ifc'))
        assert result is not None

    def test_agent_13_validator(self, sample_members):
        """Test Validator agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        val_out = pv2.validator_agent(std_out)
        assert 'errors' in val_out and 'warnings' in val_out

    def test_agent_14a_clasher(self, sample_members):
        """Test Clasher agent (hard clashes)."""
        sample = pv2.miner_from_dxf(sample_members)
        result = pv2.clasher_agent(sample)
        assert 'clashes' in result

    def test_agent_14b_soft_clash_detector(self, sample_members):
        """Test soft clash detector (clearance)."""
        sample = pv2.miner_from_dxf(sample_members)
        result = pv2.soft_clash_detector(sample)
        assert 'soft_clashes' in result

    def test_agent_14c_functional_clash_detector(self, sample_members):
        """Test functional clash detector (misalignment)."""
        sample = pv2.miner_from_dxf(sample_members)
        result = pv2.functional_clash_detector(sample)
        assert 'functional_clashes' in result

    def test_agent_14d_mep_clash_detector(self, sample_members):
        """Test MEP clash detector (multi-discipline)."""
        sample = pv2.miner_from_dxf(sample_members)
        mep_data = [{'type': 'duct', 'start': [3.0, 0.0, 2.0], 'end': [3.0, 6.0, 2.0]}]
        result = pv2.mep_clash_detector(sample, mep_data=mep_data)
        assert 'mep_clashes' in result

    def test_agent_15_risk_detector(self, sample_members):
        """Test Risk Detector agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        risk_out = pv2.risk_detector({**std_out, 'clash_list': []})
        assert 'members' in risk_out

    def test_agent_16_reporter(self, sample_members):
        """Test Reporter agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        rep_out = pv2.reporter_agent(std_out)
        assert 'bom' in rep_out

    def test_agent_17_correction_loop(self, sample_members):
        """Test Correction Loop agent."""
        miner_out = pv2.miner_from_dxf(sample_members)
        eng_out = pv2.engineer_standardize(miner_out)
        load_out = pv2.load_path_resolver(eng_out)
        stab_out = pv2.stability_agent(load_out)
        opt_out = pv2.optimizer_agent(stab_out)
        conn_out = pv2.connection_designer(opt_out)
        fab_out = pv2.fabrication_detailing(conn_out)
        std_out = pv2.fabrication_standards(fab_out)
        corr_out = pv2.correction_loop(std_out, max_iters=2)
        assert 'correction_iters' in corr_out

    def test_pipeline_integration(self, sample_members, tmp_path):
        """Test full pipeline integration (all 17 agents)."""
        p = pv2.Pipeline()
        result = p.run_from_dxf_entities(sample_members, out_dir=str(tmp_path))
        # verify all 17 agent outputs are present
        assert 'miner' in result
        assert 'engineer' in result
        assert 'loads' in result
        assert 'stability' in result
        assert 'optimizer' in result
        assert 'connections' in result
        assert 'fabrication' in result
        assert 'standards' in result
        assert 'erection' in result
        assert 'safety' in result
        assert 'analysis' in result
        assert 'ifc' in result
        assert 'validator' in result
        assert 'clashes' in result
        assert 'mesh_clashes' in result
        assert 'soft_clashes' in result
        assert 'functional_clashes' in result
        assert 'mep_clashes' in result
        assert 'risk' in result
        assert 'reporter' in result
        assert 'final' in result
        assert 'cnc' in result
        assert 'dstv' in result
