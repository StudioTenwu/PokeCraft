"""
Test suite for Advanced Agent Reasoning Engine (Round 13).
Tests agent decision-making, goal planning, and problem solving.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
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


class Goal:
    """A goal the agent works toward."""

    def __init__(self, goal_id: str, description: str, goal_type: GoalType, priority: float = 0.5):
        self.goal_id = goal_id
        self.description = description
        self.goal_type = goal_type
        self.priority = max(0.0, min(1.0, priority))
        self.created_at = datetime.now()
        self.status = "pending"  # pending, in_progress, completed, failed, abandoned
        self.progress: float = 0.0  # 0.0-1.0
        self.dependencies: List[str] = []  # Other goal IDs this depends on
        self.parent_goal: Optional[str] = None
        self.subgoals: List[str] = []

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


class ReasoningPath:
    """A chain of reasoning to reach a conclusion."""

    def __init__(self, path_id: str, reasoning_type: ReasoningStrategy):
        self.path_id = path_id
        self.reasoning_type = reasoning_type
        self.steps: List[Dict[str, Any]] = []
        self.conclusion: Optional[str] = None
        self.confidence: float = 0.0  # 0.0-1.0
        self.alternatives: List['ReasoningPath'] = []
        self.created_at = datetime.now()

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


# ===== TESTS =====

def test_goal_creation():
    """Test creating goals."""
    goal = Goal("g1", "Learn perception", GoalType.SHORT_TERM, 0.8)
    assert goal.goal_id == "g1"
    assert goal.priority == 0.8
    assert goal.status == "pending"


def test_goal_lifecycle():
    """Test goal lifecycle."""
    goal = Goal("g1", "Task", GoalType.IMMEDIATE)

    assert goal.start()
    assert goal.status == "in_progress"

    assert goal.update_progress(0.5)
    assert goal.progress == 0.5

    assert goal.complete()
    assert goal.status == "completed"
    assert goal.progress == 1.0


def test_goal_subgoals():
    """Test goal hierarchy."""
    goal = Goal("g1", "Main goal", GoalType.LONG_TERM)
    assert goal.add_subgoal("sub1")
    assert goal.add_subgoal("sub2")
    assert len(goal.subgoals) == 2


def test_reasoning_path_creation():
    """Test creating reasoning paths."""
    path = ReasoningPath("p1", ReasoningStrategy.DELIBERATIVE)
    assert path.path_id == "p1"
    assert path.reasoning_type == ReasoningStrategy.DELIBERATIVE


def test_reasoning_step_addition():
    """Test adding reasoning steps."""
    path = ReasoningPath("p1", ReasoningStrategy.HYBRID)

    assert path.add_step("Consider factors", ["fact1", "fact2"])
    assert len(path.steps) == 1


def test_reasoning_conclusion():
    """Test setting reasoning conclusion."""
    path = ReasoningPath("p1", ReasoningStrategy.DELIBERATIVE)
    path.add_step("Analyze data")

    assert path.set_conclusion("Best action is X", 0.85)
    assert path.confidence == 0.85


def test_reasoning_alternatives():
    """Test alternative reasoning paths."""
    path1 = ReasoningPath("p1", ReasoningStrategy.REACTIVE)
    path2 = ReasoningPath("p2", ReasoningStrategy.DELIBERATIVE)

    assert path1.add_alternative(path2)
    assert len(path1.alternatives) == 1


def test_decision_maker_goal_setting():
    """Test setting goals."""
    dm = DecisionMaker("agent_1")
    goal = Goal("g1", "Learn", GoalType.SHORT_TERM, 0.7)

    assert dm.set_goal(goal)
    assert "g1" in dm.active_goals


def test_decision_maker_prioritization():
    """Test goal prioritization."""
    dm = DecisionMaker("agent_1")
    goal = Goal("g1", "Learn", GoalType.SHORT_TERM, 0.5)
    dm.set_goal(goal)

    assert dm.prioritize_goal("g1", 0.9)
    assert dm.active_goals["g1"].priority == 0.9


def test_get_top_goals():
    """Test getting top priority goals."""
    dm = DecisionMaker("agent_1")
    g1 = Goal("g1", "Task 1", GoalType.IMMEDIATE, 0.3)
    g2 = Goal("g2", "Task 2", GoalType.SHORT_TERM, 0.8)
    g3 = Goal("g3", "Task 3", GoalType.LONG_TERM, 0.9)

    dm.set_goal(g1)
    dm.set_goal(g2)
    dm.set_goal(g3)

    top = dm.get_top_goals(2)
    assert top[0].goal_id == "g3"
    assert top[1].goal_id == "g2"


def test_create_reasoning_path():
    """Test creating reasoning paths through decision maker."""
    dm = DecisionMaker("agent_1")
    path = dm.create_reasoning_path(ReasoningStrategy.DELIBERATIVE)

    assert path is not None
    assert len(dm.reasoning_paths) == 1


def test_make_decision():
    """Test making decisions."""
    dm = DecisionMaker("agent_1")
    path = dm.create_reasoning_path(ReasoningStrategy.HYBRID)
    path.set_conclusion("Do X", 0.8)

    assert dm.make_decision("Execute plan X", path)
    assert len(dm.decisions_made) == 1


def test_complete_goal():
    """Test completing goals."""
    dm = DecisionMaker("agent_1")
    goal = Goal("g1", "Task", GoalType.IMMEDIATE)
    dm.set_goal(goal)
    goal.start()

    assert dm.complete_goal("g1")
    assert "g1" not in dm.active_goals
    assert len(dm.completed_goals) == 1


def test_decision_quality():
    """Test calculating decision quality."""
    dm = DecisionMaker("agent_1")
    path1 = dm.create_reasoning_path(ReasoningStrategy.DELIBERATIVE)
    path1.set_conclusion("C1", 0.9)

    path2 = dm.create_reasoning_path(ReasoningStrategy.REACTIVE)
    path2.set_conclusion("C2", 0.7)

    dm.make_decision("D1", path1)
    dm.make_decision("D2", path2)

    quality = dm.get_decision_quality()
    assert 0.7 <= quality <= 0.9


def test_problem_solver_identification():
    """Test identifying problems."""
    ps = ProblemSolver("agent_1")
    assert ps.identify_problem("p1", "Cannot process images", 0.8)
    assert "p1" in ps.problems


def test_problem_solver_approaches():
    """Test trying approaches."""
    ps = ProblemSolver("agent_1")
    ps.identify_problem("p1", "Issue", 0.6)

    assert ps.try_approach("p1", "Approach A", False)
    assert ps.try_approach("p1", "Approach B", True)

    assert len(ps.approach_history) == 2
    assert len(ps.solutions) == 1


def test_problem_solver_success_rate():
    """Test calculating success rate."""
    ps = ProblemSolver("agent_1")
    ps.identify_problem("p1", "Problem", 0.5)

    ps.try_approach("p1", "A1", True)
    ps.try_approach("p1", "A2", True)
    ps.try_approach("p1", "A3", False)

    rate = ps.get_success_rate("p1")
    assert rate == pytest.approx(0.666, abs=0.01)


def test_reasoning_summary():
    """Test getting reasoning summary."""
    dm = DecisionMaker("agent_1")
    g = Goal("g1", "Task", GoalType.IMMEDIATE)
    dm.set_goal(g)
    g.start()  # Must start before completing
    dm.complete_goal("g1")

    summary = dm.get_reasoning_summary()
    assert summary["completed_goals"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
