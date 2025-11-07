"""Environment-related data models"""

from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Position(BaseModel):
    """2D position in the grid"""

    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def distance_to(self, other: "Position") -> float:
        """Manhattan distance to another position"""
        return abs(self.x - other.x) + abs(self.y - other.y)


class EntityType(str, Enum):
    """Types of entities in the grid world"""

    AGENT = "agent"
    GOAL = "goal"
    OBSTACLE = "obstacle"
    TREE = "tree"
    STONE = "stone"
    WATER = "water"
    LAVA = "lava"
    KEY = "key"
    DOOR = "door"
    CRAFTING_TABLE = "crafting_table"


class Entity(BaseModel):
    """An entity in the grid world"""

    id: str = Field(..., description="Unique entity identifier")
    type: EntityType = Field(..., description="Type of entity")
    position: Position = Field(..., description="Current position")
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties (e.g., locked=True for doors)"
    )


class Tool(BaseModel):
    """A tool the agent can use"""

    name: str = Field(..., description="Tool name (e.g., 'move_up', 'collect')")
    description: str = Field(..., description="What the tool does")
    parameters: List[str] = Field(
        default_factory=list,
        description="Required parameters"
    )
    available: bool = Field(
        default=True,
        description="Whether tool is currently available"
    )


class GridState(BaseModel):
    """Complete state of the grid world"""

    width: int = Field(..., gt=0, description="Grid width")
    height: int = Field(..., gt=0, description="Grid height")
    entities: List[Entity] = Field(
        default_factory=list,
        description="All entities in the grid"
    )
    agent_position: Position = Field(..., description="Current agent position")
    agent_inventory: Dict[str, int] = Field(
        default_factory=dict,
        description="Agent's inventory (item_name -> count)"
    )
    step_count: int = Field(default=0, description="Steps taken in episode")
    total_reward: float = Field(default=0.0, description="Cumulative reward")
    is_done: bool = Field(default=False, description="Whether episode is complete")

    def get_entity_at(self, position: Position) -> Optional[Entity]:
        """Get entity at a specific position"""
        for entity in self.entities:
            if entity.position == position:
                return entity
        return None

    def to_natural_language(self) -> str:
        """Convert grid state to natural language description"""
        description = f"You are at position ({self.agent_position.x}, {self.agent_position.y}). "

        # Describe nearby entities
        nearby = []
        for entity in self.entities:
            dist = self.agent_position.distance_to(entity.position)
            if dist <= 2 and entity.type != EntityType.AGENT:
                direction = self._get_direction(self.agent_position, entity.position)
                nearby.append(f"{entity.type.value} {direction}")

        if nearby:
            description += f"Nearby: {', '.join(nearby)}. "

        # Describe inventory
        if self.agent_inventory:
            items = [f"{count}x {item}" for item, count in self.agent_inventory.items()]
            description += f"Inventory: {', '.join(items)}. "

        return description

    @staticmethod
    def _get_direction(from_pos: Position, to_pos: Position) -> str:
        """Get relative direction from one position to another"""
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y

        if abs(dx) > abs(dy):
            return "to the right" if dx > 0 else "to the left"
        else:
            return "below" if dy > 0 else "above"
