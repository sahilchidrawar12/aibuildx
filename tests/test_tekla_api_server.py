import pytest
from fastapi.testclient import TestClient
from scripts.api_server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert data['models_available'] >= 0


def test_tekla_status_endpoint():
    response = client.get('/api/v1/tekla/status')
    assert response.status_code == 200
    data = response.json()
    assert data['connected'] is False
    assert data['active_connections'] == 0


def test_tekla_create_without_connection():
    response = client.post('/api/v1/tekla/create', json={
        'objects': []
    })
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False
    assert 'No Tekla connection' in data['errors'][0]


def test_tekla_sync_without_connection():
    response = client.post('/api/v1/tekla/sync')
    assert response.status_code == 503
    data = response.json()
    assert 'detail' in data
    assert data['detail'] == 'No Tekla connection available'
