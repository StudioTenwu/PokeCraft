"""Game engine for executing actions and managing game state."""
import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from models.game_actions import GameActionSet, ParameterType

logger = logging.getLogger(__name__)


class ActionResult(BaseModel):
    """Result of executing an action.

    Attributes:
        success: Whether the action succeeded
        state_delta: Changes to apply to world state (DELTAS ONLY)
        message: Human-readable message about the action
        error: Optional error message if action failed
    """

    success: bool = Field(..., description="Whether action succeeded")
    state_delta: dict[str, Any] = Field(
        default_factory=dict, description="State changes (deltas only)"
    )
    message: str = Field(..., description="Human-readable result message")
    error: str | None = Field(default=None, description="Error message if failed")


class GameEngine(ABC):
    """Base class for game engines that execute actions.

    A GameEngine validates action parameters and executes actions
    within a specific game type (e.g., grid navigation, tower defense).
    """

    def __init__(self, world_id: str, action_set: GameActionSet) -> None:
        """Initialize the game engine.

        Args:
            world_id: ID of the world this engine operates on
            action_set: Set of actions available in this game
        """
        self.world_id = world_id
        self.action_set = action_set
        logger.info(
            f"Initialized {self.__class__.__name__} for world {world_id} "
            f"with {len(action_set.actions)} actions"
        )

    def execute_action(self, action_id: str, parameters: dict[str, Any]) -> ActionResult:
        """Validate and execute an action.

        Args:
            action_id: ID of the action to execute
            parameters: Parameters for the action

        Returns:
            ActionResult with success status, state deltas, and message
        """
        logger.info(f"Executing action '{action_id}' with parameters: {parameters}")

        # 1. Validate action exists
        action = self.action_set.get_action(action_id)
        if not action:
            logger.error(f"Action '{action_id}' not found in action set")
            return ActionResult(
                success=False,
                message=f"Unknown action: {action_id}",
                error=f"Action '{action_id}' is not available in this game",
            )

        # 2. Validate parameters
        try:
            self._validate_parameters(action_id, parameters)
        except ValueError as e:
            logger.error(f"Parameter validation failed: {e}")
            return ActionResult(
                success=False,
                message=f"Invalid parameters for {action_id}",
                error=str(e),
            )

        # 3. Execute action implementation
        try:
            result = self._execute_action_impl(action_id, parameters)
            logger.info(f"Action '{action_id}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return ActionResult(
                success=False,
                message=f"Failed to execute {action_id}",
                error=str(e),
            )

    def _validate_parameters(self, action_id: str, parameters: dict[str, Any]) -> None:
        """Validate action parameters against schema.

        Args:
            action_id: ID of the action
            parameters: Parameters to validate

        Raises:
            ValueError: If validation fails
        """
        action = self.action_set.get_action(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")

        # Check required parameters
        for param in action.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(f"Required parameter '{param.name}' is missing")

            # Validate parameter types if present
            if param.name in parameters:
                value = parameters[param.name]
                self._validate_parameter_type(param.name, value, param.type)

    def _validate_parameter_type(
        self, param_name: str, value: Any, expected_type: ParameterType
    ) -> None:
        """Validate a single parameter's type.

        Args:
            param_name: Name of the parameter
            value: Value to validate
            expected_type: Expected ParameterType

        Raises:
            ValueError: If type validation fails
        """
        if expected_type == ParameterType.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Parameter '{param_name}' must be a string")
        elif expected_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                raise ValueError(f"Parameter '{param_name}' must be an integer")
        elif expected_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Parameter '{param_name}' must be a boolean")
        elif expected_type == ParameterType.ARRAY:
            if not isinstance(value, list):
                raise ValueError(f"Parameter '{param_name}' must be an array")
        elif expected_type == ParameterType.OBJECT:
            if not isinstance(value, dict):
                raise ValueError(f"Parameter '{param_name}' must be an object")

    @abstractmethod
    def _execute_action_impl(
        self, action_id: str, parameters: dict[str, Any]
    ) -> ActionResult:
        """Implementation-specific action execution.

        Subclasses must implement this method to define game-specific behavior.

        Args:
            action_id: ID of the action to execute
            parameters: Validated parameters

        Returns:
            ActionResult with state deltas and message
        """
        pass


class GridNavigationEngine(GameEngine):
    """Game engine for grid navigation games.

    Handles movement, item pickup, and waiting actions in a 2D grid world.
    """

    def __init__(
        self, world_id: str, action_set: GameActionSet, world_state: dict[str, Any]
    ) -> None:
        """Initialize the grid navigation engine.

        Args:
            world_id: ID of the world
            action_set: Available actions
            world_state: Current world state (grid, agent_position, etc.)
        """
        super().__init__(world_id, action_set)
        self.world_state = world_state

    def _execute_action_impl(
        self, action_id: str, parameters: dict[str, Any]
    ) -> ActionResult:
        """Execute grid navigation actions.

        Args:
            action_id: Action to execute ("move", "pickup", "wait")
            parameters: Action parameters

        Returns:
            ActionResult with state deltas
        """
        if action_id == "move":
            return self._execute_move(parameters)
        elif action_id == "pickup":
            return self._execute_pickup(parameters)
        elif action_id == "wait":
            return self._execute_wait(parameters)
        else:
            return ActionResult(
                success=False,
                message=f"Unknown action: {action_id}",
                error=f"Action {action_id} is not implemented",
            )

    def _execute_move(self, parameters: dict[str, Any]) -> ActionResult:
        """Execute a move action.

        Args:
            parameters: Must contain "direction", optionally "steps"

        Returns:
            ActionResult with position delta
        """
        direction = parameters["direction"]
        steps = parameters.get("steps", 1)

        # Get current position
        current_pos = self.world_state.get("agent_position", [0, 0])
        width = self.world_state.get("width", 10)
        height = self.world_state.get("height", 10)

        # Calculate new position based on direction
        x, y = current_pos
        if direction == "north":
            y = max(0, y - steps)
        elif direction == "south":
            y = min(height - 1, y + steps)
        elif direction == "east":
            x = min(width - 1, x + steps)
        elif direction == "west":
            x = max(0, x - steps)
        else:
            return ActionResult(
                success=False,
                message=f"Invalid direction: {direction}",
                error="Direction must be 'north', 'south', 'east', or 'west'",
            )

        new_pos = [x, y]

        # Check if position actually changed
        if new_pos == current_pos:
            return ActionResult(
                success=True,
                state_delta={},
                message=f"Cannot move {direction} - at boundary",
            )

        # Return state delta
        return ActionResult(
            success=True,
            state_delta={
                "agent_position": new_pos,
                "agent_moved_from": current_pos,
                "agent_moved_to": new_pos,
            },
            message=f"Moved {direction} to position {new_pos}",
        )

    def _execute_pickup(self, parameters: dict[str, Any]) -> ActionResult:
        """Execute a pickup action.

        Args:
            parameters: Optionally contains "item_type"

        Returns:
            ActionResult with inventory delta
        """
        item_type = parameters.get("item_type")
        current_pos = self.world_state.get("agent_position", [0, 0])

        # Check if there's an item at current position
        # (In a real implementation, would check grid state)
        # For now, simulate picking up an item
        return ActionResult(
            success=True,
            state_delta={
                "inventory_added": item_type or "item",
                "cell_cleared": current_pos,
            },
            message=f"Picked up {item_type or 'item'} at position {current_pos}",
        )

    def _execute_wait(self, parameters: dict[str, Any]) -> ActionResult:
        """Execute a wait action.

        Args:
            parameters: Optionally contains "turns"

        Returns:
            ActionResult with turn count delta
        """
        turns = parameters.get("turns", 1)

        return ActionResult(
            success=True,
            state_delta={
                "turns_waited": turns,
            },
            message=f"Waited for {turns} turn(s)",
        )
