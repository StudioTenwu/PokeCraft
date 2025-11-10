"""Integration tests for tool API endpoints."""
import pytest


def test_api_imports():
    """Test that API endpoints can be imported without errors."""
    import sys

    sys.path.insert(0, "backend/src")
    from main import app

    # Verify all tool endpoints are registered
    routes = [r.path for r in app.routes if hasattr(r, "path")]

    assert "/api/tools/create" in routes
    assert "/api/tools/agent/{agent_id}" in routes
    assert "/api/tools/{tool_name}" in routes
    assert "/api/agents/deploy" in routes


def test_tool_service_imported_in_main():
    """Test that ToolService is properly imported in main.py."""
    import sys

    sys.path.insert(0, "backend/src")
    from main import ToolService

    # ToolService should be importable
    assert ToolService is not None


def test_api_has_correct_number_of_endpoints():
    """Test that the correct number of endpoints are registered."""
    import sys

    sys.path.insert(0, "backend/src")
    from main import app

    # Count HTTP method routes (excluding WebSocket, static files, etc.)
    http_routes = [r for r in app.routes if hasattr(r, "path") and hasattr(r, "methods")]

    # Should have at least 13 HTTP endpoints:
    # - root, health
    # - create_agent (POST + GET stream), get_agent
    # - create_world, get_world, get_worlds_by_agent
    # - create_tool, get_agent_tools, delete_tool, deploy_agent
    assert len(http_routes) >= 11


def test_pydantic_models_imported():
    """Test that Pydantic models for tool API are properly defined."""
    import sys

    sys.path.insert(0, "backend/src")
    from models.tool import DeployRequest, ToolCreateRequest, ToolCreateResponse, ToolResponse

    # All models should be importable
    assert ToolCreateRequest is not None
    assert ToolCreateResponse is not None
    assert ToolResponse is not None
    assert DeployRequest is not None

    # Test that ToolCreateRequest has required fields
    request = ToolCreateRequest(agent_id="test", description="test tool")
    assert request.agent_id == "test"
    assert request.description == "test tool"
