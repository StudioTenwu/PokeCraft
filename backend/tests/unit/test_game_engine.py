"""Unit tests for game engine."""
import pytest
from typing import Any

from src.game_engine import (
    ActionResult,
    GameEngine,
    GridNavigationEngine,
)
from src.models.game_actions import (
    GameActionSet,
    GameAction,
    ActionParameter,
    ParameterType,
    GRID_NAVIGATION_ACTIONS,
)


class TestActionResult:
    """Tests for ActionResult model."""

    def test_create_successful_result(self) -> None:
        """Test creating a successful action result."""
        result = ActionResult(
            success=True,
            state_delta={"position": [5, 7]},
            message="Moved successfully",
        )
        assert result.success is True
        assert result.state_delta == {"position": [5, 7]}
        assert result.message == "Moved successfully"
        assert result.error is None

    def test_create_failed_result(self) -> None:
        """Test creating a failed action result."""
        result = ActionResult(
            success=False,
            message="Action failed",
            error="Invalid direction",
        )
        assert result.success is False
        assert result.message == "Action failed"
        assert result.error == "Invalid direction"
        assert result.state_delta == {}

    def test_create_result_without_state_delta(self) -> None:
        """Test creating result without state changes."""
        result = ActionResult(
            success=True,
            message="Waited for 1 turn",
        )
        assert result.state_delta == {}


class MockGameEngine(GameEngine):
    """Mock game engine for testing base class behavior."""

    def __init__(self, world_id: str, action_set: GameActionSet) -> None:
        super().__init__(world_id, action_set)
        self.executed_action: str | None = None
        self.executed_params: dict[str, Any] | None = None

    def _execute_action_impl(
        self, action_id: str, parameters: dict[str, Any]
    ) -> ActionResult:
        """Mock implementation that records execution."""
        self.executed_action = action_id
        self.executed_params = parameters
        return ActionResult(
            success=True,
            message=f"Executed {action_id}",
        )


class TestGameEngine:
    """Tests for GameEngine base class."""

    def test_initialize_engine(self) -> None:
        """Test initializing a game engine."""
        action_set = GameActionSet(
            game_type="test",
            actions=[
                GameAction(
                    action_id="test_action",
                    name="Test",
                    description="Test action",
                ),
            ],
        )
        engine = MockGameEngine("world_123", action_set)
        assert engine.world_id == "world_123"
        assert engine.action_set == action_set

    def test_execute_unknown_action(self) -> None:
        """Test executing an action that doesn't exist."""
        action_set = GameActionSet(game_type="test", actions=[])
        engine = MockGameEngine("world_123", action_set)

        result = engine.execute_action("unknown", {})
        assert result.success is False
        assert "Unknown action" in result.message
        assert result.error is not None

    def test_execute_action_with_valid_parameters(self) -> None:
        """Test executing an action with valid parameters."""
        action_set = GameActionSet(
            game_type="test",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move agent",
                    parameters=[
                        ActionParameter(
                            name="direction",
                            type=ParameterType.STRING,
                            required=True,
                            description="Direction to move",
                        ),
                    ],
                ),
            ],
        )
        engine = MockGameEngine("world_123", action_set)

        result = engine.execute_action("move", {"direction": "north"})
        assert result.success is True
        assert engine.executed_action == "move"
        assert engine.executed_params == {"direction": "north"}

    def test_execute_action_missing_required_parameter(self) -> None:
        """Test executing an action without a required parameter."""
        action_set = GameActionSet(
            game_type="test",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move agent",
                    parameters=[
                        ActionParameter(
                            name="direction",
                            type=ParameterType.STRING,
                            required=True,
                            description="Direction to move",
                        ),
                    ],
                ),
            ],
        )
        engine = MockGameEngine("world_123", action_set)

        result = engine.execute_action("move", {})
        assert result.success is False
        assert "Invalid parameters" in result.message
        assert "direction" in result.error

    def test_validate_parameter_types(self) -> None:
        """Test parameter type validation."""
        action_set = GameActionSet(
            game_type="test",
            actions=[
                GameAction(
                    action_id="test",
                    name="Test",
                    description="Test action",
                    parameters=[
                        ActionParameter(
                            name="count",
                            type=ParameterType.INTEGER,
                            required=True,
                            description="Count",
                        ),
                        ActionParameter(
                            name="name",
                            type=ParameterType.STRING,
                            required=True,
                            description="Name",
                        ),
                        ActionParameter(
                            name="enabled",
                            type=ParameterType.BOOLEAN,
                            required=True,
                            description="Enabled",
                        ),
                    ],
                ),
            ],
        )
        engine = MockGameEngine("world_123", action_set)

        # Test invalid integer
        result = engine.execute_action("test", {
            "count": "not_an_int",
            "name": "test",
            "enabled": True,
        })
        assert result.success is False
        assert "must be an integer" in result.error

        # Test invalid string
        result = engine.execute_action("test", {
            "count": 5,
            "name": 123,
            "enabled": True,
        })
        assert result.success is False
        assert "must be a string" in result.error

        # Test invalid boolean
        result = engine.execute_action("test", {
            "count": 5,
            "name": "test",
            "enabled": "not_a_bool",
        })
        assert result.success is False
        assert "must be a boolean" in result.error

    def test_optional_parameters_with_defaults(self) -> None:
        """Test that optional parameters work correctly."""
        action_set = GameActionSet(
            game_type="test",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move agent",
                    parameters=[
                        ActionParameter(
                            name="direction",
                            type=ParameterType.STRING,
                            required=True,
                            description="Direction to move",
                        ),
                        ActionParameter(
                            name="steps",
                            type=ParameterType.INTEGER,
                            required=False,
                            description="Number of steps",
                            default=1,
                        ),
                    ],
                ),
            ],
        )
        engine = MockGameEngine("world_123", action_set)

        # Should succeed with only required parameter
        result = engine.execute_action("move", {"direction": "north"})
        assert result.success is True


class TestGridNavigationEngine:
    """Tests for GridNavigationEngine."""

    def test_initialize_grid_navigation_engine(self) -> None:
        """Test initializing grid navigation engine."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [0, 0],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)
        assert engine.world_id == "world_123"
        assert engine.world_state == world_state

    def test_move_north(self) -> None:
        """Test moving north."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [1, 1],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "north"})
        assert result.success is True
        assert result.state_delta["agent_position"] == [1, 0]
        assert result.state_delta["agent_moved_from"] == [1, 1]
        assert result.state_delta["agent_moved_to"] == [1, 0]

    def test_move_south(self) -> None:
        """Test moving south."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [1, 1],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "south"})
        assert result.success is True
        assert result.state_delta["agent_position"] == [1, 2]

    def test_move_east(self) -> None:
        """Test moving east."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [1, 1],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "east"})
        assert result.success is True
        assert result.state_delta["agent_position"] == [2, 1]

    def test_move_west(self) -> None:
        """Test moving west."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [1, 1],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "west"})
        assert result.success is True
        assert result.state_delta["agent_position"] == [0, 1]

    def test_move_multiple_steps(self) -> None:
        """Test moving multiple steps."""
        world_state = {
            "grid": [[".", ".", ".", ".", "."]],
            "agent_position": [2, 0],
            "width": 5,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "east", "steps": 2})
        assert result.success is True
        assert result.state_delta["agent_position"] == [4, 0]

    def test_move_at_boundary(self) -> None:
        """Test moving when already at boundary."""
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."], [".", ".", "."]],
            "agent_position": [0, 0],
            "width": 3,
            "height": 3,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        # Try to move north from top edge
        result = engine.execute_action("move", {"direction": "north"})
        assert result.success is True
        assert result.state_delta == {}  # No movement
        assert "boundary" in result.message.lower()

        # Try to move west from left edge
        result = engine.execute_action("move", {"direction": "west"})
        assert result.success is True
        assert result.state_delta == {}
        assert "boundary" in result.message.lower()

    def test_move_clamped_at_boundary(self) -> None:
        """Test that movement is clamped at world boundaries."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        # Try to move 5 steps east from middle (should clamp to edge)
        result = engine.execute_action("move", {"direction": "east", "steps": 5})
        assert result.success is True
        assert result.state_delta["agent_position"] == [2, 0]  # Clamped to max

    def test_move_invalid_direction(self) -> None:
        """Test moving with invalid direction."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("move", {"direction": "up"})
        assert result.success is False
        assert "Invalid direction" in result.message

    def test_pickup_item(self) -> None:
        """Test picking up an item."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("pickup", {})
        assert result.success is True
        assert "inventory_added" in result.state_delta
        assert "cell_cleared" in result.state_delta
        assert result.state_delta["cell_cleared"] == [1, 0]

    def test_pickup_specific_item_type(self) -> None:
        """Test picking up a specific item type."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("pickup", {"item_type": "coin"})
        assert result.success is True
        assert result.state_delta["inventory_added"] == "coin"

    def test_wait_action(self) -> None:
        """Test waiting."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("wait", {})
        assert result.success is True
        assert result.state_delta["turns_waited"] == 1

    def test_wait_multiple_turns(self) -> None:
        """Test waiting multiple turns."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("wait", {"turns": 3})
        assert result.success is True
        assert result.state_delta["turns_waited"] == 3

    def test_execute_unknown_action(self) -> None:
        """Test executing an unknown action in grid navigation."""
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }
        engine = GridNavigationEngine("world_123", GRID_NAVIGATION_ACTIONS, world_state)

        result = engine.execute_action("fly", {})
        assert result.success is False
        assert "Unknown action" in result.message
