"""Shared world state manager for tool access."""
from typing import Any


class WorldStateManager:
    """Thread-safe world state manager that tools can query."""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    def set_world(self, world_id: str, world_state: dict[str, Any]) -> None:
        """Store world state for a given world ID."""
        self._states[world_id] = world_state

    def get_world(self, world_id: str) -> dict[str, Any] | None:
        """Retrieve world state by world ID."""
        return self._states.get(world_id)

    def update_position(self, world_id: str, new_position: list[int]) -> None:
        """Update agent position in world state."""
        if world_id in self._states:
            self._states[world_id]["agent_position"] = new_position


# Global instance for tool access
state_manager = WorldStateManager()
