import os
import json
import uuid
import pytest
import tempfile
from pathlib import Path
from cli import ConversionCLI


class TestCLI:
    """Tests for CLI tool."""

    def test_convert_json_input(self, tmp_path):
        """Test conversion of JSON input file."""
        # Create sample input
        members = [
            {'id': str(uuid.uuid4()), 'start': [0, 0, 0], 'end': [6, 0, 0], 'length': 6.0, 'layer': 'BEAMS'},
            {'id': str(uuid.uuid4()), 'start': [6, 0, 0], 'end': [6, 0, 4], 'length': 4.0, 'layer': 'COLUMNS'},
        ]
        input_file = tmp_path / 'input.json'
        with open(input_file, 'w') as f:
            json.dump(members, f)
        
        output_dir = tmp_path / 'output'
        ret = ConversionCLI.convert(str(input_file), str(output_dir))
        
        assert ret == 0
        assert (output_dir / 'result.json').exists() or (output_dir / 'final.json').exists()

    def test_convert_nonexistent_file(self):
        """Test conversion with nonexistent input."""
        ret = ConversionCLI.convert('nonexistent.dwg', '/tmp/output')
        assert ret == 1

    def test_validate_valid_json(self, tmp_path):
        """Test validation of valid JSON."""
        data = {
            'miner': {'members': [{'id': '1', 'start': [0, 0, 0], 'end': [6, 0, 0]}]},
            'engineer': {},
            'validator': {'errors': [], 'warnings': []}
        }
        input_file = tmp_path / 'model.json'
        with open(input_file, 'w') as f:
            json.dump(data, f)
        
        ret = ConversionCLI.validate(str(input_file))
        assert ret == 0

    def test_validate_invalid_json(self, tmp_path):
        """Test validation of invalid JSON (missing required keys)."""
        data = {'some_key': 'value'}  # Missing miner, engineer, etc.
        input_file = tmp_path / 'model.json'
        with open(input_file, 'w') as f:
            json.dump(data, f)
        
        ret = ConversionCLI.validate(str(input_file))
        # Should return 0 but with warnings (not critical)
        assert ret == 0

    def test_batch_conversion(self, tmp_path):
        """Test batch conversion from config."""
        # Create config file
        config = {
            'jobs': [
                {'input': str(tmp_path / 'input1.json'), 'output': str(tmp_path / 'out1')},
                {'input': str(tmp_path / 'input2.json'), 'output': str(tmp_path / 'out2')},
            ]
        }
        
        # Create input files
        for i in range(1, 3):
            input_file = tmp_path / f'input{i}.json'
            with open(input_file, 'w') as f:
                json.dump([{'id': f'm{i}', 'start': [0, 0, 0], 'end': [1, 0, 0]}], f)
        
        config_file = tmp_path / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        ret = ConversionCLI.batch(str(config_file))
        assert ret == 0


class TestWebAPI:
    """Tests for web API endpoints."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_index_page(self, client):
        """Test loading index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'DWG' in response.data or b'Tekla' in response.data

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_upload_missing_file(self, client):
        """Test upload without file."""
        response = client.post('/api/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_download_nonexistent_file(self, client):
        """Test download of nonexistent file."""
        response = client.get('/api/download/nonexistent_job/file.json')
        assert response.status_code == 404


class TestTeklaIntegration:
    """Tests for Tekla Structures integration."""

    def test_member_data_creation(self):
        """Test creation of MemberData objects."""
        # This requires the Tekla .NET module to be built
        # Placeholder test
        pass

    def test_connection_data_creation(self):
        """Test creation of ConnectionData objects."""
        # Placeholder test
        pass

    def test_model_statistics(self):
        """Test model statistics calculation."""
        # Placeholder test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
