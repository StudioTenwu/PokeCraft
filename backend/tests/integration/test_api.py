"""Integration tests for FastAPI endpoints."""
from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app


class TestAgentAPI:
    """Integration tests for agent creation API."""

    @pytest.fixture()
    def client(self):
        """Create test client for FastAPI app."""
        with TestClient(app) as test_client:
            yield test_client

    def test_root_endpoint_returns_api_info(self, client):
        """Should return API information at root endpoint."""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "message" in data
        assert "AICraft" in data["message"]
        assert "endpoints" in data

    def test_health_endpoint_returns_healthy(self, client):
        """Should return healthy status."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"status": "healthy"}

    def test_create_agent_endpoint_with_valid_description(self, client):
        """Should create agent with valid description."""
        # Arrange
        mock_agent = {
            "id": "test-123",
            "name": "Sir Valor",
            "backstory": "A brave knight.",
            "personality_traits": ["brave", "loyal"],
            "avatar_url": "/static/avatars/test-123.png",
        }

        # Mock after the app has started up (services are in app.state)
        with patch.object(client.app.state.agent_service, 'create_agent', return_value=mock_agent):
            # Act
            response = client.post(
                "/api/agents/create", json={"description": "A brave knight"},
            )

            # Assert
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert data["name"] == "Sir Valor"
            assert data["id"] == "test-123"

    def test_create_agent_endpoint_requires_description(self, client):
        """Should return 422 when description is missing."""
        # Act
        response = client.post("/api/agents/create", json={})

        # Assert
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_agent_endpoint_handles_service_error(self, client):
        """Should return 500 when service raises exception."""
        # Arrange
        with patch.object(client.app.state.agent_service, 'create_agent', side_effect=Exception("LLM service unavailable")):
            # Act
            response = client.post("/api/agents/create", json={"description": "A wizard"})

            # Assert
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert "detail" in response.json()

    def test_get_agent_endpoint_returns_agent(self, client):
        """Should retrieve agent by ID."""
        # Arrange
        mock_agent = {
            "id": "agent-456",
            "name": "Merlin",
            "backstory": "A wise wizard.",
            "personality_traits": ["wise", "patient"],
            "avatar_url": "/static/avatars/agent-456.png",
        }

        with patch.object(client.app.state.agent_service, 'get_agent', return_value=mock_agent):
            # Act
            response = client.get("/api/agents/agent-456")

            # Assert
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert data["name"] == "Merlin"

    def test_get_agent_endpoint_returns_404_when_not_found(self, client):
        """Should return 404 when agent doesn't exist."""
        # Arrange
        with patch.object(client.app.state.agent_service, 'get_agent', return_value=None):
            # Act
            response = client.get("/api/agents/nonexistent")

            # Assert
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert "detail" in response.json()

    def test_cors_headers_allow_frontend_origin(self, client):
        """Should include CORS headers for frontend."""
        # Act
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        # Assert
        assert response.status_code == HTTPStatus.OK
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_create_agent_endpoint_returns_all_fields(self, client):
        """Should return all required agent fields."""
        # Arrange
        mock_agent = {
            "id": "full-test",
            "name": "Complete Agent",
            "backstory": "A fully detailed agent for testing.",
            "personality_traits": ["friendly", "helpful", "curious"],
            "avatar_url": "/static/avatars/full-test.png",
        }

        with patch.object(client.app.state.agent_service, 'create_agent', return_value=mock_agent):
            # Act
            response = client.post(
                "/api/agents/create", json={"description": "A detailed test agent"},
            )

            # Assert
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "backstory" in data
            assert "personality_traits" in data
            assert "avatar_url" in data
            assert isinstance(data["personality_traits"], list)
