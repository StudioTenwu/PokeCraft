"""Pydantic models for agent data validation."""
from pydantic import BaseModel, Field, field_validator


class AgentData(BaseModel):
    """Schema for LLM-generated agent data with runtime validation.

    This model ensures that agent data from the LLM matches our expected
    schema and provides clear error messages when validation fails.
    """

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Agent name",
    )
    backstory: str = Field(
        min_length=10,
        max_length=500,
        description="2-3 sentence backstory for the agent",
    )
    personality_traits: list[str] = Field(
        min_length=1,
        max_length=5,
        description="List of personality traits (1-5 traits)",
    )
    avatar_prompt: str = Field(
        min_length=10,
        description="Detailed prompt for avatar image generation",
    )

    @field_validator("personality_traits")
    @classmethod
    def traits_must_be_nonempty(cls, v: list[str]) -> list[str]:
        """Ensure no empty trait strings."""
        if any(not trait.strip() for trait in v):
            msg = "Personality traits cannot be empty strings"
            raise ValueError(msg)
        return v

    @field_validator("name", "backstory", "avatar_prompt")
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
