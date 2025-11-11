"""Registry for game action sets and game engine factory."""
import logging
from typing import Any

from src.game_engine import GameEngine, GridNavigationEngine
from src.models.game_actions import GameActionSet, GRID_NAVIGATION_ACTIONS

logger = logging.getLogger(__name__)


# Registry mapping game_type strings to GameActionSet objects
ACTION_SETS: dict[str, GameActionSet] = {
    "grid_navigation": GRID_NAVIGATION_ACTIONS,
}


def get_action_set_for_game(game_type: str) -> GameActionSet | None:
    """Get the action set for a specific game type.

    Args:
        game_type: Type of game (e.g., "grid_navigation")

    Returns:
        GameActionSet if game type is registered, None otherwise
    """
    action_set = ACTION_SETS.get(game_type)
    if action_set:
        logger.info(f"Retrieved action set for game type: {game_type}")
    else:
        logger.warning(f"No action set found for game type: {game_type}")
    return action_set


def create_game_engine(
    game_type: str, world_id: str, action_set: GameActionSet, world_state: dict[str, Any]
) -> GameEngine | None:
    """Factory function to create appropriate game engine for a game type.

    Args:
        game_type: Type of game (e.g., "grid_navigation")
        world_id: ID of the world
        action_set: Set of actions available
        world_state: Current world state

    Returns:
        GameEngine instance if game type is supported, None otherwise
    """
    logger.info(f"Creating game engine for game type: {game_type}, world: {world_id}")

    if game_type == "grid_navigation":
        return GridNavigationEngine(world_id, action_set, world_state)
    else:
        logger.error(f"Unsupported game type: {game_type}")
        return None


def list_available_game_types() -> list[str]:
    """List all registered game types.

    Returns:
        List of game type strings
    """
    return list(ACTION_SETS.keys())


def register_action_set(game_type: str, action_set: GameActionSet) -> None:
    """Register a new action set for a game type.

    This allows for dynamic registration of new game types at runtime.

    Args:
        game_type: Type of game
        action_set: Action set to register
    """
    if game_type in ACTION_SETS:
        logger.warning(f"Overwriting existing action set for game type: {game_type}")
    ACTION_SETS[game_type] = action_set
    logger.info(f"Registered action set for game type: {game_type}")
