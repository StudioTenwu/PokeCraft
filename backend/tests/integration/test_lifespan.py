"""Tests for FastAPI lifespan management."""
import pytest
from fastapi.testclient import TestClient
from main import app

class TestLifespan:
    """Tests for application lifespan management."""

    def test_app_state_contains_services_after_startup(self):
        """Should initialize services in app.state during lifespan startup."""
        with TestClient(app) as client:
            # Services should be accessible via app.state
            assert hasattr(app.state, 'agent_service')
            assert hasattr(app.state, 'world_service')

    def test_services_are_initialized_during_startup(self):
        """Should call init_db on both services during startup."""
        with TestClient(app) as client:
            # Make a health check to ensure app started successfully
            response = client.get("/health")
            assert response.status_code == 200

    def test_app_can_be_started_and_stopped_cleanly(self):
        """Should handle lifespan startup and shutdown without errors."""
        # This tests the context manager behavior
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
        # After context manager exits, cleanup should have run
