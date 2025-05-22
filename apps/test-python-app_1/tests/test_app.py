import pytest
from app import app # Import the Flask app instance from our app.py

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello from Microservice A (Python/Flask)!" in response.data

def test_health_check(client):
    """Test the /health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "UP", "service": "test-python-app_1"}