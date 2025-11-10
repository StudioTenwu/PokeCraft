"""Pydantic models for world data validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


# Type alias for valid tile types
TileType = Literal["grass", "wall", "water", "path", "goal"]


class WorldData(BaseModel):
    """Schema for LLM-generated world data with runtime validation.

    This model ensures that world data from the LLM matches our expected
    schema and provides clear error messages when validation fails.
    """

    name: str = Field(
        min_length=1,
        max_length=100,
        description="World name",
    )
    description: str = Field(
        min_length=10,
        max_length=500,
        description="Brief description of the world",
    )
    grid: list[list[TileType]] = Field(
        description="10x10 grid of tile types",
    )
    agent_start: list[int] = Field(
        min_length=2,
        max_length=2,
        description="Agent starting position [x, y]",
    )

    @field_validator("grid")
    @classmethod
    def grid_must_be_10x10(cls, v: list[list[str]]) -> list[list[str]]:
        """Ensure grid is exactly 10x10."""
        if len(v) != 10:
            msg = f"Grid must have exactly 10 rows, got {len(v)}"
            raise ValueError(msg)

        for i, row in enumerate(v):
            if len(row) != 10:
                msg = f"Grid row {i} must have exactly 10 columns, got {len(row)}"
                raise ValueError(msg)

        return v

    @field_validator("agent_start")
    @classmethod
    def agent_start_within_bounds(cls, v: list[int]) -> list[int]:
        """Ensure agent start position is within grid bounds."""
        x, y = v
        if not (0 <= x < 10 and 0 <= y < 10):
            msg = f"Agent start position [{x}, {y}] is out of bounds (must be 0-9)"
            raise ValueError(msg)
        return v

    @field_validator("name", "description")
    @classmethod
    def strings_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure strings are not just whitespace."""
        if not v.strip():
            msg = "Field cannot be only whitespace"
            raise ValueError(msg)
        return v.strip()

    model_config = {
        "frozen": True,  # Immutable after creation
        "str_strip_whitespace": True,  # Auto-strip whitespace
    }
