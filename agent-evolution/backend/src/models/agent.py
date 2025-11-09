"""Agent-related data models"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for an AI agent"""

    system_prompt: str = Field(
        ...,
        description="The system prompt that defines agent behavior"
    )
    available_tools: List[str] = Field(
        default_factory=list,
        description="List of tool names the agent can use"
    )
    max_steps: int = Field(
        default=50,
        description="Maximum steps before agent stops"
    )
    model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="LLM model to use (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4', 'gemini-pro')"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )


class AgentThought(BaseModel):
    """A single reasoning step from the agent"""

    thought: str = Field(..., description="Agent's internal reasoning")
    step_number: int = Field(..., description="Step number in the episode")
    timestamp: float = Field(..., description="Unix timestamp")


class AgentAction(BaseModel):
    """An action taken by the agent"""

    action_type: str = Field(..., description="Type of action (e.g., 'move', 'collect')")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action parameters"
    )
    step_number: int = Field(..., description="Step number in the episode")
    thought: Optional[str] = Field(
        None,
        description="Reasoning behind this action"
    )


class AgentObservation(BaseModel):
    """What the agent observes from the environment"""

    observation: str = Field(..., description="Natural language description of observation")
    grid_state: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured grid state data"
    )
    step_number: int = Field(..., description="Step number in the episode")
    reward: float = Field(default=0.0, description="Reward received")
    done: bool = Field(default=False, description="Whether episode is complete")
