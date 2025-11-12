"""Unit tests for agent export endpoint."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def mock_agent_service():
    """Mock agent service."""
    service = AsyncMock()
    return service


@pytest.fixture
def app_with_mock_service(mock_agent_service):
    """Create FastAPI app with mock agent service."""
    from src.main import app
    app.state.agent_service = mock_agent_service
    return app


@pytest.fixture
def client(app_with_mock_service):
    """Create test client."""
    return TestClient(app_with_mock_service)


def test_export_agent_success(client, mock_agent_service):
    """Test successful agent export."""
    # Setup mock
    agent_id = "test-agent-123"
    mock_agent_data = {
        "id": agent_id,
        "name": "Test Agent",
        "backstory": "A test agent backstory",
        "personality_traits": ["friendly", "helpful"],
        "avatar_url": "http://example.com/avatar.png"
    }
    mock_agent_service.get_agent.return_value = mock_agent_data

    # Make request
    response = client.get(f"/api/agents/{agent_id}/export")

    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "Test Agent"
    assert data["backstory"] == "A test agent backstory"
    assert data["personality_traits"] == ["friendly", "helpful"]
    assert data["avatar_url"] == "http://example.com/avatar.png"


def test_export_agent_not_found(client, mock_agent_service):
    """Test agent export when agent doesn't exist."""
    # Setup mock
    mock_agent_service.get_agent.return_value = None

    # Make request
    response = client.get("/api/agents/nonexistent-id/export")

    # Verify
    assert response.status_code == 404
    assert response.json()["detail"] == "Agent not found"


def test_export_agent_only_includes_required_fields(client, mock_agent_service):
    """Test that export only includes chrome extension required fields."""
    # Setup mock with extra fields
    agent_id = "test-agent-456"
    mock_agent_data = {
        "id": agent_id,
        "name": "Test Agent",
        "backstory": "A test agent backstory",
        "personality_traits": ["friendly", "helpful"],
        "avatar_url": "http://example.com/avatar.png",
        "created_at": "2025-01-01T00:00:00",
        "extra_field": "should not be included"
    }
    mock_agent_service.get_agent.return_value = mock_agent_data

    # Make request
    response = client.get(f"/api/agents/{agent_id}/export")

    # Verify only required fields are present
    assert response.status_code == 200
    data = response.json()
    expected_fields = {"id", "name", "backstory", "personality_traits", "avatar_url"}
    assert set(data.keys()) == expected_fields
