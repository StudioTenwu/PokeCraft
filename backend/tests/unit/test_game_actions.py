"""Unit tests for game action models."""
import pytest
from pydantic import ValidationError

from src.models.game_actions import (
    ActionParameter,
    GameAction,
    GameActionSet,
    ParameterType,
    GRID_NAVIGATION_ACTIONS,
)


class TestActionParameter:
    """Tests for ActionParameter model."""

    def test_create_required_parameter(self) -> None:
        """Test creating a required parameter."""
        param = ActionParameter(
            name="direction",
            type=ParameterType.STRING,
            required=True,
            description="Direction to move",
        )
        assert param.name == "direction"
        assert param.type == ParameterType.STRING
        assert param.required is True
        assert param.description == "Direction to move"
        assert param.default is None

    def test_create_optional_parameter_with_default(self) -> None:
        """Test creating an optional parameter with default value."""
        param = ActionParameter(
            name="steps",
            type=ParameterType.INTEGER,
            required=False,
            description="Number of steps",
            default=1,
        )
        assert param.name == "steps"
        assert param.type == ParameterType.INTEGER
        assert param.required is False
        assert param.default == 1

    def test_parameter_requires_name(self) -> None:
        """Test that parameter requires a name."""
        with pytest.raises(ValidationError):
            ActionParameter(
                type=ParameterType.STRING,
                required=True,
                description="Test",
            )

    def test_parameter_requires_type(self) -> None:
        """Test that parameter requires a type."""
        with pytest.raises(ValidationError):
            ActionParameter(
                name="test",
                required=True,
                description="Test",
            )

    def test_all_parameter_types(self) -> None:
        """Test all parameter types are valid."""
        types = [
            ParameterType.STRING,
            ParameterType.INTEGER,
            ParameterType.BOOLEAN,
            ParameterType.ARRAY,
            ParameterType.OBJECT,
        ]
        for param_type in types:
            param = ActionParameter(
                name="test",
                type=param_type,
                required=True,
                description="Test parameter",
            )
            assert param.type == param_type


class TestGameAction:
    """Tests for GameAction model."""

    def test_create_action_without_parameters(self) -> None:
        """Test creating an action with no parameters."""
        action = GameAction(
            action_id="wait",
            name="Wait",
            description="Wait for one turn",
        )
        assert action.action_id == "wait"
        assert action.name == "Wait"
        assert action.description == "Wait for one turn"
        assert action.parameters == []

    def test_create_action_with_parameters(self) -> None:
        """Test creating an action with parameters."""
        action = GameAction(
            action_id="move",
            name="Move",
            description="Move in a direction",
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
        )
        assert action.action_id == "move"
        assert len(action.parameters) == 2
        assert action.parameters[0].name == "direction"
        assert action.parameters[1].name == "steps"

    def test_get_parameter_by_name(self) -> None:
        """Test retrieving a parameter by name."""
        action = GameAction(
            action_id="move",
            name="Move",
            description="Move in a direction",
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
        )

        # Test finding existing parameter
        direction_param = action.get_parameter("direction")
        assert direction_param is not None
        assert direction_param.name == "direction"
        assert direction_param.type == ParameterType.STRING

        steps_param = action.get_parameter("steps")
        assert steps_param is not None
        assert steps_param.name == "steps"
        assert steps_param.default == 1

    def test_get_parameter_not_found(self) -> None:
        """Test retrieving a non-existent parameter."""
        action = GameAction(
            action_id="wait",
            name="Wait",
            description="Wait for one turn",
        )
        param = action.get_parameter("nonexistent")
        assert param is None

    def test_action_requires_id_name_description(self) -> None:
        """Test that action requires id, name, and description."""
        with pytest.raises(ValidationError):
            GameAction(name="Test", description="Test action")

        with pytest.raises(ValidationError):
            GameAction(action_id="test", description="Test action")

        with pytest.raises(ValidationError):
            GameAction(action_id="test", name="Test")


class TestGameActionSet:
    """Tests for GameActionSet model."""

    def test_create_action_set(self) -> None:
        """Test creating an action set."""
        action_set = GameActionSet(
            game_type="grid_navigation",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move in a direction",
                ),
                GameAction(
                    action_id="wait",
                    name="Wait",
                    description="Wait for one turn",
                ),
            ],
        )
        assert action_set.game_type == "grid_navigation"
        assert len(action_set.actions) == 2

    def test_get_action_by_id(self) -> None:
        """Test retrieving an action by ID."""
        action_set = GameActionSet(
            game_type="test_game",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move in a direction",
                ),
                GameAction(
                    action_id="wait",
                    name="Wait",
                    description="Wait for one turn",
                ),
            ],
        )

        move_action = action_set.get_action("move")
        assert move_action is not None
        assert move_action.action_id == "move"
        assert move_action.name == "Move"

        wait_action = action_set.get_action("wait")
        assert wait_action is not None
        assert wait_action.action_id == "wait"

    def test_get_action_not_found(self) -> None:
        """Test retrieving a non-existent action."""
        action_set = GameActionSet(
            game_type="test_game",
            actions=[
                GameAction(
                    action_id="move",
                    name="Move",
                    description="Move in a direction",
                ),
            ],
        )
        action = action_set.get_action("nonexistent")
        assert action is None

    def test_list_action_ids(self) -> None:
        """Test listing all action IDs."""
        action_set = GameActionSet(
            game_type="test_game",
            actions=[
                GameAction(action_id="move", name="Move", description="Move"),
                GameAction(action_id="wait", name="Wait", description="Wait"),
                GameAction(action_id="pickup", name="Pickup", description="Pickup"),
            ],
        )
        action_ids = action_set.list_action_ids()
        assert action_ids == ["move", "wait", "pickup"]

    def test_empty_action_set(self) -> None:
        """Test creating an empty action set."""
        action_set = GameActionSet(game_type="empty_game", actions=[])
        assert action_set.game_type == "empty_game"
        assert len(action_set.actions) == 0
        assert action_set.list_action_ids() == []


class TestGridNavigationActions:
    """Tests for the GRID_NAVIGATION_ACTIONS constant."""

    def test_action_set_exists(self) -> None:
        """Test that GRID_NAVIGATION_ACTIONS is defined."""
        assert GRID_NAVIGATION_ACTIONS is not None
        assert isinstance(GRID_NAVIGATION_ACTIONS, GameActionSet)

    def test_game_type(self) -> None:
        """Test that game type is correct."""
        assert GRID_NAVIGATION_ACTIONS.game_type == "grid_navigation"

    def test_has_move_action(self) -> None:
        """Test that move action exists and is configured correctly."""
        move = GRID_NAVIGATION_ACTIONS.get_action("move")
        assert move is not None
        assert move.action_id == "move"
        assert move.name == "Move"
        assert "direction" in [p.name for p in move.parameters]

        # Check direction parameter
        direction_param = move.get_parameter("direction")
        assert direction_param is not None
        assert direction_param.type == ParameterType.STRING
        assert direction_param.required is True

        # Check steps parameter
        steps_param = move.get_parameter("steps")
        assert steps_param is not None
        assert steps_param.type == ParameterType.INTEGER
        assert steps_param.required is False
        assert steps_param.default == 1

    def test_has_pickup_action(self) -> None:
        """Test that pickup action exists and is configured correctly."""
        pickup = GRID_NAVIGATION_ACTIONS.get_action("pickup")
        assert pickup is not None
        assert pickup.action_id == "pickup"
        assert pickup.name == "Pick Up Item"

        # Check item_type parameter
        item_type_param = pickup.get_parameter("item_type")
        assert item_type_param is not None
        assert item_type_param.type == ParameterType.STRING
        assert item_type_param.required is False
        assert item_type_param.default is None

    def test_has_wait_action(self) -> None:
        """Test that wait action exists and is configured correctly."""
        wait = GRID_NAVIGATION_ACTIONS.get_action("wait")
        assert wait is not None
        assert wait.action_id == "wait"
        assert wait.name == "Wait"

        # Check turns parameter
        turns_param = wait.get_parameter("turns")
        assert turns_param is not None
        assert turns_param.type == ParameterType.INTEGER
        assert turns_param.required is False
        assert turns_param.default == 1

    def test_all_actions_present(self) -> None:
        """Test that all expected actions are present."""
        action_ids = GRID_NAVIGATION_ACTIONS.list_action_ids()
        assert "move" in action_ids
        assert "pickup" in action_ids
        assert "wait" in action_ids
        assert len(action_ids) == 3
