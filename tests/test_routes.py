"""
Integration tests for Flask routes.
Uses Flask's test client so no real server needs to be running.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    """Create a Flask test client with mocked heavy dependencies."""
    # Mock heavy ML / data modules before importing app
    mock_modules = {
        'torch': MagicMock(),
        'torchvision': MagicMock(),
        'torchvision.transforms': MagicMock(),
        'PIL': MagicMock(),
        'PIL.Image': MagicMock(),
        'openai': MagicMock(),
    }
    with patch.dict('sys.modules', mock_modules):
        # Reset AgentMemory singleton
        from agents.base import AgentMemory
        AgentMemory._instance = None

        from app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        with app.test_client() as c:
            yield c


class TestPageRoutes:
    """Test that all public GET pages return 200 and correct templates."""

    def test_home_page(self, client):
        """Home page should return 200."""
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'Krishi Mitr' in resp.data or b'Farm' in resp.data

    def test_services_page(self, client):
        """Services page should return 200."""
        resp = client.get('/services')
        assert resp.status_code == 200

    def test_about_page(self, client):
        """About page should return 200."""
        resp = client.get('/about')
        assert resp.status_code == 200

    def test_crop_form_page(self, client):
        """Crop agent form should return 200."""
        resp = client.get('/agent/crop')
        assert resp.status_code == 200

    def test_fertilizer_form_page(self, client):
        """Fertilizer agent form should return 200."""
        resp = client.get('/agent/fertilizer')
        assert resp.status_code == 200

    def test_sustainability_form_page(self, client):
        """Sustainability agent form should return 200."""
        resp = client.get('/agent/sustainability')
        assert resp.status_code == 200

    def test_irrigation_form_page(self, client):
        """Irrigation agent form should return 200."""
        resp = client.get('/agent/irrigation')
        assert resp.status_code == 200

    def test_yield_form_page(self, client):
        """Yield prediction form should return 200."""
        resp = client.get('/yield')
        assert resp.status_code == 200


class TestAuthRoutes:
    """Test auth-adjacent routes."""

    def test_login_redirects(self, client):
        """Login should redirect to dashboard."""
        resp = client.get('/login')
        assert resp.status_code in (302, 301, 308)

    def test_logout_redirects(self, client):
        """Logout should redirect to home."""
        resp = client.get('/logout')
        assert resp.status_code in (302, 301, 308)


class TestAPIRoutes:
    """Test API endpoints."""

    def test_memory_api(self, client):
        """GET /api/memory should return JSON."""
        resp = client.get('/api/memory')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_agent_api_post(self, client):
        """POST /api/agent/<name> should process JSON payload."""
        with patch('app.orchestrator') as mock_orch:
            mock_orch.dispatch.return_value = {"status": "ok", "result": {}}
            resp = client.post(
                '/api/agent/crop',
                json={"nitrogen": 90, "phosphorous": 42, "pottasium": 43},
                content_type='application/json'
            )
            assert resp.status_code == 200

    def test_chatbot_status_api(self, client):
        """GET /api/chatbot/status should return JSON."""
        resp = client.get('/api/chatbot/status')
        assert resp.status_code == 200
        data = resp.get_json()
        assert "status" in data


class TestErrorHandling:
    """Test that error cases don't crash the server."""

    def test_404_for_unknown_route(self, client):
        """Unknown routes should return 404."""
        resp = client.get('/this-does-not-exist')
        assert resp.status_code == 404

    def test_crop_predict_without_form_data(self, client):
        """POST /crop-predict without form data should not crash (may redirect or error)."""
        resp = client.post('/crop-predict')
        # Should not be a 500 — either redirect or render with error
        assert resp.status_code != 500
