"""
Advanced Agent Reasoning Engine for AICraft (Round 13).
Provides decision-making, goal planning, and problem-solving capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ReasoningStrategy(Enum):
    """Strategies an agent can use to reason."""
    REACTIVE = "reactive"  # Respond to immediate stimulus
    DELIBERATIVE = "deliberative"  # Plan before acting
    HYBRID = "hybrid"  # Mix of reactive and deliberative


class GoalType(Enum):
    """Types of goals."""
    IMMEDIATE = "immediate"  # Execute now
    SHORT_TERM = "short_term"  # Hours to days
    LONG_TERM = "long_term"  # Weeks to months
    ABSTRACT = "abstract"  # Philosophical/value goals


@dataclass
class Goal:
    """A goal the agent works toward."""
    goal_id: str
    description: str
    goal_type: GoalType
    priority: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    progress: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    parent_goal: Optional[str] = None
    subgoals: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate priority."""
        self.priority = max(0.0, min(1.0, self.priority))

    def start(self) -> bool:
        """Begin working on goal."""
        if self.status != "pending":
            return False
        self.status = "in_progress"
        return True

    def update_progress(self, new_progress: float) -> bool:
        """Update progress toward goal."""
        if not 0.0 <= new_progress <= 1.0:
            return False
        self.progress = new_progress
        return True

    def complete(self) -> bool:
        """Mark goal as completed."""
        if self.status != "in_progress":
            return False
        self.status = "completed"
        self.progress = 1.0
        return True

    def add_subgoal(self, subgoal_id: str) -> bool:
        """Add a subgoal."""
        if subgoal_id not in self.subgoals:
            self.subgoals.append(subgoal_id)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize goal."""
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "type": self.goal_type.name,
            "status": self.status,
            "progress": self.progress,
            "priority": self.priority,
            "subgoals": self.subgoals
        }


@dataclass
class ReasoningPath:
    """A chain of reasoning to reach a conclusion."""
    path_id: str
    reasoning_type: ReasoningStrategy
    steps: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 0.0
    alternatives: List['ReasoningPath'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_step(self, step_description: str, supporting_evidence: List[str] = None) -> bool:
        """Add a reasoning step."""
        self.steps.append({
            "timestamp": datetime.now().isoformat(),
            "description": step_description,
            "evidence": supporting_evidence or []
        })
        return True

    def set_conclusion(self, conclusion: str, confidence: float) -> bool:
        """Set the reasoning conclusion."""
        if not 0.0 <= confidence <= 1.0:
            return False

        self.conclusion = conclusion
        self.confidence = confidence
        return True

    def add_alternative(self, alternative: 'ReasoningPath') -> bool:
        """Add an alternative reasoning path."""
        if alternative not in self.alternatives:
            self.alternatives.append(alternative)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize reasoning path."""
        return {
            "path_id": self.path_id,
            "reasoning_type": self.reasoning_type.value,
            "steps": len(self.steps),
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "alternatives": len(self.alternatives)
        }


class DecisionMaker:
    """Makes decisions based on goals and reasoning."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.active_goals: Dict[str, Goal] = {}
        self.completed_goals: List[Goal] = []
        self.reasoning_paths: List[ReasoningPath] = []
        self.decisions_made: List[Dict[str, Any]] = []
        self.preferred_strategy = ReasoningStrategy.HYBRID

    def set_goal(self, goal: Goal) -> bool:
        """Add a goal."""
        if goal.goal_id in self.active_goals:
            return False
        self.active_goals[goal.goal_id] = goal
        return True

    def prioritize_goal(self, goal_id: str, new_priority: float) -> bool:
        """Change goal priority."""
        if goal_id not in self.active_goals:
            return False

        if not 0.0 <= new_priority <= 1.0:
            return False

        self.active_goals[goal_id].priority = new_priority
        return True

    def get_top_goals(self, limit: int = 5) -> List[Goal]:
        """Get highest priority goals."""
        sorted_goals = sorted(
            self.active_goals.values(),
            key=lambda g: (g.priority, -g.created_at.timestamp()),
            reverse=True
        )
        return sorted_goals[:limit]

    def create_reasoning_path(self, path_type: ReasoningStrategy) -> ReasoningPath:
        """Create a reasoning path."""
        path_id = f"path_{len(self.reasoning_paths)}"
        path = ReasoningPath(path_id, path_type)
        self.reasoning_paths.append(path)
        return path

    def make_decision(self, decision_description: str, reasoning: ReasoningPath) -> bool:
        """Record a decision made."""
        self.decisions_made.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision_description,
            "reasoning_path": reasoning.path_id,
            "confidence": reasoning.confidence
        })
        return True

    def complete_goal(self, goal_id: str) -> bool:
        """Mark a goal as completed."""
        if goal_id not in self.active_goals:
            return False

        goal = self.active_goals[goal_id]
        if goal.complete():
            self.completed_goals.append(goal)
            del self.active_goals[goal_id]
            return True

        return False

    def get_decision_quality(self) -> float:
        """Calculate decision quality based on confidence."""
        if not self.decisions_made:
            return 0.5

        avg_confidence = sum(d["confidence"] for d in self.decisions_made) / len(self.decisions_made)
        return avg_confidence

    def get_reasoning_summary(self) -> Dict[str, Any]:
        """Get summary of reasoning."""
        return {
            "agent_id": self.agent_id,
            "active_goals": len(self.active_goals),
            "completed_goals": len(self.completed_goals),
            "reasoning_paths": len(self.reasoning_paths),
            "decisions_made": len(self.decisions_made),
            "avg_decision_confidence": self.get_decision_quality(),
            "preferred_strategy": self.preferred_strategy.value
        }


class ProblemSolver:
    """Solves problems using multiple approaches."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.problems: Dict[str, Dict[str, Any]] = {}
        self.solutions: List[Dict[str, Any]] = []
        self.approach_history: List[Dict[str, Any]] = []

    def identify_problem(self, problem_id: str, description: str, severity: float = 0.5) -> bool:
        """Identify a problem."""
        if problem_id in self.problems:
            return False

        self.problems[problem_id] = {
            "description": description,
            "severity": severity,
            "identified_at": datetime.now().isoformat(),
            "approaches": []
        }
        return True

    def try_approach(self, problem_id: str, approach: str, success: bool) -> bool:
        """Try an approach to solving a problem."""
        if problem_id not in self.problems:
            return False

        self.approach_history.append({
            "timestamp": datetime.now().isoformat(),
            "problem_id": problem_id,
            "approach": approach,
            "success": success
        })

        self.problems[problem_id]["approaches"].append({
            "approach": approach,
            "success": success
        })

        if success:
            self.solutions.append({
                "problem_id": problem_id,
                "approach": approach,
                "timestamp": datetime.now().isoformat()
            })

        return True

    def get_success_rate(self, problem_id: Optional[str] = None) -> float:
        """Get success rate of approaches."""
        if not self.approach_history:
            return 0.0

        if problem_id:
            attempts = [a for a in self.approach_history if a["problem_id"] == problem_id]
        else:
            attempts = self.approach_history

        if not attempts:
            return 0.0

        successes = sum(1 for a in attempts if a["success"])
        return successes / len(attempts)

    def get_problem_status(self) -> Dict[str, Any]:
        """Get status of all problems."""
        solved = len([s for s in self.solutions])
        total = len(self.problems)

        return {
            "agent_id": self.agent_id,
            "total_problems": total,
            "solved_problems": solved,
            "unsolved_problems": total - solved,
            "overall_success_rate": self.get_success_rate(),
            "total_approaches": len(self.approach_history)
        }
