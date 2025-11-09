"""Level and challenge data models"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Difficulty(str, Enum):
    """Challenge difficulty levels"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Challenge(BaseModel):
    """A specific challenge within a level"""

    id: str = Field(..., description="Unique challenge identifier")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="What the learner needs to do")
    difficulty: Difficulty = Field(..., description="Challenge difficulty")
    hints: List[str] = Field(
        default_factory=list,
        description="Progressive hints for stuck learners"
    )
    success_criteria: Dict[str, Any] = Field(
        ...,
        description="Criteria for completing the challenge"
    )


class Level(BaseModel):
    """A course level"""

    id: str = Field(..., description="Unique level identifier")
    number: int = Field(..., ge=1, description="Level number")
    title: str = Field(..., description="Level title")
    description: str = Field(..., description="What learners will learn")
    estimated_minutes: int = Field(..., gt=0, description="Estimated completion time")
    learning_objectives: List[str] = Field(
        ...,
        description="What learners will be able to do after this level"
    )
    initial_prompt: str = Field(
        ...,
        description="Starting system prompt for the level"
    )
    available_tools: List[str] = Field(
        ...,
        description="Tools available in this level"
    )
    grid_config: Dict[str, Any] = Field(
        ...,
        description="Grid world configuration for this level"
    )
    challenges: List[Challenge] = Field(
        default_factory=list,
        description="Challenges in this level"
    )
    next_level_id: Optional[str] = Field(
        None,
        description="ID of the next level"
    )


class LevelProgress(BaseModel):
    """User's progress through a level"""

    level_id: str = Field(..., description="Level being tracked")
    completed_challenges: List[str] = Field(
        default_factory=list,
        description="IDs of completed challenges"
    )
    attempts: int = Field(default=0, description="Number of attempts")
    best_score: float = Field(default=0.0, description="Best score achieved")
    hints_used: int = Field(default=0, description="Number of hints used")
    completed: bool = Field(default=False, description="Whether level is complete")
    completion_time_seconds: Optional[int] = Field(
        None,
        description="Time taken to complete (if finished)"
    )
