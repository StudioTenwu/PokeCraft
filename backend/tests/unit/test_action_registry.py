"""Unit tests for action registry."""
import pytest

from src.action_registry import (
    ACTION_SETS,
    get_action_set_for_game,
    create_game_engine,
    list_available_game_types,
    register_action_set,
)
from src.game_engine import GridNavigationEngine
from src.models.game_actions import (
    GameActionSet,
    GameAction,
    ActionParameter,
    ParameterType,
)


class TestActionRegistry:
    """Tests for action registry module."""

    def test_action_sets_contains_grid_navigation(self) -> None:
        """Test that ACTION_SETS contains grid_navigation."""
        assert "grid_navigation" in ACTION_SETS
        action_set = ACTION_SETS["grid_navigation"]
        assert action_set.game_type == "grid_navigation"
        assert len(action_set.actions) > 0

    def test_get_action_set_for_game_valid(self) -> None:
        """Test getting action set for valid game type."""
        action_set = get_action_set_for_game("grid_navigation")
        assert action_set is not None
        assert action_set.game_type == "grid_navigation"

    def test_get_action_set_for_game_invalid(self) -> None:
        """Test getting action set for invalid game type."""
        action_set = get_action_set_for_game("nonexistent_game")
        assert action_set is None

    def test_list_available_game_types(self) -> None:
        """Test listing available game types."""
        game_types = list_available_game_types()
        assert isinstance(game_types, list)
        assert "grid_navigation" in game_types

    def test_create_game_engine_grid_navigation(self) -> None:
        """Test creating a grid navigation game engine."""
        action_set = get_action_set_for_game("grid_navigation")
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }

        engine = create_game_engine(
            "grid_navigation", "world_123", action_set, world_state
        )

        assert engine is not None
        assert isinstance(engine, GridNavigationEngine)
        assert engine.world_id == "world_123"
        assert engine.action_set == action_set

    def test_create_game_engine_unsupported_type(self) -> None:
        """Test creating engine for unsupported game type."""
        action_set = GameActionSet(game_type="unsupported", actions=[])
        world_state = {}

        engine = create_game_engine("unsupported", "world_123", action_set, world_state)

        assert engine is None

    def test_register_new_action_set(self) -> None:
        """Test registering a new action set."""
        # Create a custom action set
        custom_action_set = GameActionSet(
            game_type="custom_game",
            actions=[
                GameAction(
                    action_id="custom_action",
                    name="Custom Action",
                    description="A custom action",
                ),
            ],
        )

        # Register it
        register_action_set("custom_game", custom_action_set)

        # Verify it's registered
        assert "custom_game" in ACTION_SETS
        retrieved_set = get_action_set_for_game("custom_game")
        assert retrieved_set is not None
        assert retrieved_set.game_type == "custom_game"

        # Clean up
        del ACTION_SETS["custom_game"]

    def test_register_overwrites_existing(self) -> None:
        """Test that registering an existing game type overwrites it."""
        # Create a new action set with same game type
        new_action_set = GameActionSet(
            game_type="grid_navigation",
            actions=[
                GameAction(
                    action_id="new_action",
                    name="New Action",
                    description="A new action",
                ),
            ],
        )

        # Save original
        original_set = get_action_set_for_game("grid_navigation")

        # Register new one
        register_action_set("grid_navigation", new_action_set)

        # Verify it was overwritten
        retrieved_set = get_action_set_for_game("grid_navigation")
        assert retrieved_set.list_action_ids() == ["new_action"]

        # Restore original
        register_action_set("grid_navigation", original_set)


class TestActionRegistryIntegration:
    """Integration tests for action registry with game engines."""

    def test_full_workflow_get_action_set_and_create_engine(self) -> None:
        """Test full workflow of getting action set and creating engine."""
        # 1. Get action set for game type
        action_set = get_action_set_for_game("grid_navigation")
        assert action_set is not None

        # 2. Create world state
        world_state = {
            "grid": [[".", ".", "."], [".", ".", "."]],
            "agent_position": [0, 0],
            "width": 3,
            "height": 2,
        }

        # 3. Create engine
        engine = create_game_engine(
            "grid_navigation", "world_test", action_set, world_state
        )
        assert engine is not None

        # 4. Execute an action
        result = engine.execute_action("move", {"direction": "east"})
        assert result.success is True
        assert result.state_delta["agent_position"] == [1, 0]

    def test_engine_creation_with_all_grid_actions(self) -> None:
        """Test that created engine can execute all grid navigation actions."""
        action_set = get_action_set_for_game("grid_navigation")
        world_state = {
            "grid": [[".", ".", "."]],
            "agent_position": [1, 0],
            "width": 3,
            "height": 1,
        }

        engine = create_game_engine(
            "grid_navigation", "world_test", action_set, world_state
        )

        # Test move
        result = engine.execute_action("move", {"direction": "north"})
        assert result.success is True or result.message  # Success or boundary message

        # Test pickup
        result = engine.execute_action("pickup", {})
        assert result.success is True

        # Test wait
        result = engine.execute_action("wait", {})
        assert result.success is True
