"""Pydantic models for tool-related API requests and responses."""
from pydantic import BaseModel, Field


class ToolCreateRequest(BaseModel):
    """Request model for creating a new tool."""

    agent_id: str = Field(..., description="ID of the agent this tool is for")
    world_id: str = Field(..., description="ID of the world this tool will be used in")
    description: str = Field(..., description="Natural language description of the tool")


class ToolResponse(BaseModel):
    """Response model for a tool."""

    id: str
    agent_id: str
    name: str
    description: str | None
    code: str
    category: str | None
    created_at: str


class ToolCreateResponse(BaseModel):
    """Response model for tool creation."""

    tool_name: str
    code: str
    explanation: str
    tool_id: str | None = None


class DeployRequest(BaseModel):
    """Request model for deploying an agent."""

    agent_id: str = Field(..., description="ID of the agent to deploy")
    world_id: str = Field(..., description="ID of the world to deploy in")
    goal: str = Field(..., description="Goal for the agent to accomplish")
