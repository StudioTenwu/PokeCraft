"""Integration tests for world API endpoints."""
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from models.world import WorldData


@pytest.fixture
def mock_world_data():
    """Create mock world data for testing."""
    return WorldData(
        name="Integration Test World",
        description="A world for API integration tests",
        grid=[
            ["grass", "grass", "path", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "path", "grass", "water", "water", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "path", "grass", "water", "water", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "path", "grass", "grass", "grass", "wall", "wall", "grass", "grass"],
            ["grass", "grass", "path", "grass", "grass", "grass", "wall", "wall", "grass", "grass"],
            ["grass", "grass", "path", "path", "path", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "goal"],
            ["grass", "grass", "grass", "grass", "path", "path", "path", "path", "path", "path"]
        ],
        agent_start=[2, 0]
    )


def test_create_world_endpoint(mock_world_data):
    """Test POST /api/worlds/create endpoint."""
    # Mock the world generator
    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        response_dict = {
            "name": mock_world_data.name,
            "description": mock_world_data.description,
            "grid": mock_world_data.grid,
            "agent_start": mock_world_data.agent_start
        }
        json_str = json.dumps(response_dict)
        mock_message.result = f"<output><![CDATA[\n{json_str}\n]]></output>"
        yield mock_message

    with patch('src.llm_world_generator.query', side_effect=mock_query_generator):
        with TestClient(app) as client:
            response = client.post(
                "/api/worlds/create",
                json={
                    "agent_id": "test-agent-123",
                    "description": "a peaceful meadow with a pond"
                }
            )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["agent_id"] == "test-agent-123"
    assert "name" in data  # Name can vary based on LLM response
    assert data["width"] == 10
    assert data["height"] == 10
    assert len(data["agent_position"]) == 2
    assert len(data["grid"]) == 10
    assert len(data["grid"][0]) == 10



def test_create_world_endpoint_missing_fields():
    """Test that endpoint validates required fields."""
    with TestClient(app) as client:
        # Missing description
        response = client.post(
            "/api/worlds/create",
            json={"agent_id": "test-agent"}
        )

    assert response.status_code == 422  # Validation error



def test_get_world_endpoint(mock_world_data):
    """Test GET /api/worlds/{world_id} endpoint."""
    # First create a world
    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        response_dict = {
            "name": mock_world_data.name,
            "description": mock_world_data.description,
            "grid": mock_world_data.grid,
            "agent_start": mock_world_data.agent_start
        }
        json_str = json.dumps(response_dict)
        mock_message.result = f"<output><![CDATA[\n{json_str}\n]]></output>"
        yield mock_message

    with patch('src.llm_world_generator.query', side_effect=mock_query_generator):
        with TestClient(app) as client:
            # Create world
            create_response = client.post(
                "/api/worlds/create",
                json={
                    "agent_id": "test-agent-456",
                    "description": "test world"
                }
            )
            world_id = create_response.json()["id"]

            # Get world
            get_response = client.get(f"/api/worlds/{world_id}")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == world_id
    assert data["agent_id"] == "test-agent-456"



def test_get_world_endpoint_not_found():
    """Test GET /api/worlds/{world_id} returns 404 for non-existent world."""
    with TestClient(app) as client:
        response = client.get("/api/worlds/non-existent-id")

    assert response.status_code == 404



def test_get_worlds_by_agent_endpoint(mock_world_data):
    """Test GET /api/worlds/agent/{agent_id} endpoint."""
    agent_id = "test-agent-multi"

    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        response_dict = {
            "name": mock_world_data.name,
            "description": mock_world_data.description,
            "grid": mock_world_data.grid,
            "agent_start": mock_world_data.agent_start
        }
        json_str = json.dumps(response_dict)
        mock_message.result = f"<output><![CDATA[\n{json_str}\n]]></output>"
        yield mock_message

    with patch('src.llm_world_generator.query', side_effect=mock_query_generator):
        with TestClient(app) as client:
            # Create multiple worlds for same agent
            client.post(
                "/api/worlds/create",
                json={"agent_id": agent_id, "description": "world 1"}
            )
            client.post(
                "/api/worlds/create",
                json={"agent_id": agent_id, "description": "world 2"}
            )

            # Get all worlds for agent
            response = client.get(f"/api/worlds/agent/{agent_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(w["agent_id"] == agent_id for w in data)



def test_create_world_endpoint_error_handling(mock_world_data):
    """Test that endpoint handles errors gracefully."""
    # Mock generator to raise exception
    async def mock_query_error(*args, **kwargs):
        raise Exception("LLM Error")

    with patch('src.llm_world_generator.query', side_effect=mock_query_error):
        with TestClient(app) as client:
            response = client.post(
                "/api/worlds/create",
                json={
                    "agent_id": "test-agent",
                    "description": "test"
                }
            )

    # Should still return 200 with fallback world
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "grid" in data
