"""Integration tests for actions endpoint."""
from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app


class TestActionsAPI:
    """Integration tests for actions retrieval API."""

    @pytest.fixture()
    def client(self):
        """Create test client for FastAPI app."""
        with TestClient(app) as test_client:
            yield test_client

    @pytest.fixture()
    async def test_world(self, client):
        """Create a test world for actions endpoint testing."""
        # Create a test agent first
        agent_response = client.post(
            "/api/agents/create",
            json={"description": "Test agent for actions endpoint"}
        )
        agent_id = agent_response.json()["id"]

        # Create a test world
        world_response = client.post(
            "/api/worlds/create",
            json={
                "agent_id": agent_id,
                "description": "A test world for actions"
            }
        )
        world = world_response.json()
        return world

    def test_get_actions_returns_grouped_actions(self, client, test_world):
        """Should return actions grouped by category for a valid world."""
        # Act
        response = client.get(f"/api/actions/{test_world['id']}")

        # Assert
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Verify structure
        assert "world" in data
        assert "actions" in data

        # Verify world info
        assert data["world"]["id"] == test_world["id"]
        assert data["world"]["name"] == test_world["name"]
        assert data["world"]["game_type"] == test_world["game_type"]

        # Verify actions are grouped
        actions = data["actions"]
        assert isinstance(actions, dict)

        # For grid_navigation, we should have actions
        # (categories may vary, but we should have at least some actions)
        total_actions = sum(len(actions_list) for actions_list in actions.values())
        assert total_actions > 0

        # Verify action structure
        for category, action_list in actions.items():
            if len(action_list) > 0:
                action = action_list[0]
                assert "action_id" in action
                assert "name" in action
                assert "description" in action
                assert "parameters" in action
                assert isinstance(action["parameters"], list)

    def test_get_actions_404_for_invalid_world(self, client):
        """Should return 404 for non-existent world ID."""
        # Act
        response = client.get("/api/actions/invalid-world-id-12345")

        # Assert
        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
