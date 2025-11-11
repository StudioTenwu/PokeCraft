"""Pydantic models for the action system."""
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Valid parameter types for action parameters."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ActionParameter(BaseModel):
    """Defines a parameter for an action.

    Attributes:
        name: The parameter name
        type: The parameter type (string, integer, boolean, etc.)
        required: Whether this parameter is required
        description: Human-readable description of the parameter
        default: Optional default value if not required
    """

    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    required: bool = Field(default=True, description="Whether parameter is required")
    description: str = Field(..., description="Parameter description")
    default: Any = Field(default=None, description="Default value if not required")


class GameAction(BaseModel):
    """Defines a single action with parameters.

    Attributes:
        action_id: Unique identifier for this action
        name: Human-readable name
        description: Description of what the action does
        parameters: List of parameters this action accepts
    """

    action_id: str = Field(..., description="Unique action identifier")
    name: str = Field(..., description="Human-readable action name")
    description: str = Field(..., description="What this action does")
    parameters: list[ActionParameter] = Field(
        default_factory=list, description="List of parameters"
    )

    def get_parameter(self, param_name: str) -> ActionParameter | None:
        """Get a parameter by name.

        Args:
            param_name: Name of the parameter to find

        Returns:
            ActionParameter if found, None otherwise
        """
        for param in self.parameters:
            if param.name == param_name:
                return param
        return None


class GameActionSet(BaseModel):
    """Complete set of actions for a game type.

    Attributes:
        game_type: Type of game (e.g., "grid_navigation")
        actions: List of available actions
    """

    game_type: str = Field(..., description="Type of game")
    actions: list[GameAction] = Field(..., description="Available actions")

    def get_action(self, action_id: str) -> GameAction | None:
        """Get an action by ID.

        Args:
            action_id: ID of the action to find

        Returns:
            GameAction if found, None otherwise
        """
        for action in self.actions:
            if action.action_id == action_id:
                return action
        return None

    def list_action_ids(self) -> list[str]:
        """Get list of all action IDs.

        Returns:
            List of action IDs
        """
        return [action.action_id for action in self.actions]


# Define the action set for grid navigation game
GRID_NAVIGATION_ACTIONS = GameActionSet(
    game_type="grid_navigation",
    actions=[
        GameAction(
            action_id="move",
            name="Move",
            description="Move the agent in a cardinal direction (north, south, east, west)",
            parameters=[
                ActionParameter(
                    name="direction",
                    type=ParameterType.STRING,
                    required=True,
                    description="Direction to move: 'north', 'south', 'east', or 'west'",
                ),
                ActionParameter(
                    name="steps",
                    type=ParameterType.INTEGER,
                    required=False,
                    description="Number of steps to move (default: 1)",
                    default=1,
                ),
            ],
        ),
        GameAction(
            action_id="pickup",
            name="Pick Up Item",
            description="Pick up an item at the current position",
            parameters=[
                ActionParameter(
                    name="item_type",
                    type=ParameterType.STRING,
                    required=False,
                    description="Specific item type to pick up (optional)",
                    default=None,
                ),
            ],
        ),
        GameAction(
            action_id="wait",
            name="Wait",
            description="Wait for one turn without taking action",
            parameters=[
                ActionParameter(
                    name="turns",
                    type=ParameterType.INTEGER,
                    required=False,
                    description="Number of turns to wait (default: 1)",
                    default=1,
                ),
            ],
        ),
    ],
)
