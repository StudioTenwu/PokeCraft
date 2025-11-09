"""
Round 39: Learning Environments and Challenges

Create structured learning contexts where agents practice skills and overcome
challenges. Environments provide scaffolding, constraints, and meaningful goals
that guide agent development.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any


class EnvironmentType(Enum):
    """Types of learning environments"""
    SANDBOX = "sandbox"  # Free exploration
    PUZZLE = "puzzle"  # Specific challenges to solve
    SIMULATION = "simulation"  # Real-world simulation
    COLLABORATION = "collaboration"  # Multi-agent cooperation
    EXPLORATION = "exploration"  # Discovery-based learning


class ChallengeType(Enum):
    """Types of challenges within environments"""
    REASONING = "reasoning"  # Logic puzzles
    CREATIVITY = "creativity"  # Open-ended creation
    COMMUNICATION = "communication"  # Dialogue challenges
    PROBLEM_SOLVING = "problem_solving"  # Multi-step problems
    COLLABORATION = "collaboration"  # Team challenges
    PHYSICAL = "physical"  # Robot movement challenges
    ARTISTIC = "artistic"  # Music, drawing, writing


class DifficultyLevel(Enum):
    """Progression through environment difficulty"""
    TUTORIAL = "tutorial"  # First time guidance
    EASY = "easy"  # Simple challenges
    MEDIUM = "medium"  # Moderate challenges
    HARD = "hard"  # Difficult challenges
    EXPERT = "expert"  # Master-level challenges


@dataclass
class EnvironmentConstraint:
    """Constraint within an environment"""
    constraint_id: str
    name: str
    description: str
    enforce_strict: bool = True  # If True, failure if constraint violated
    penalty: float = 0.0  # 0.0-1.0, performance penalty if violated

    def to_dict(self) -> Dict:
        return {
            "id": self.constraint_id,
            "name": self.name,
            "description": self.description,
            "strict": self.enforce_strict,
            "penalty": self.penalty
        }


@dataclass
class EnvironmentGoal:
    """Primary goal of the environment"""
    goal_id: str
    description: str
    success_criteria: str  # How to measure success
    reward: float = 1.0  # 0.0-1.0, completion reward
    time_limit: Optional[float] = None  # Seconds, None for unlimited

    def is_time_exceeded(self, elapsed: float) -> bool:
        """Check if time limit exceeded"""
        if self.time_limit is None:
            return False
        return elapsed > self.time_limit

    def to_dict(self) -> Dict:
        return {
            "id": self.goal_id,
            "description": self.description,
            "success_criteria": self.success_criteria,
            "reward": self.reward,
            "time_limit": self.time_limit
        }


@dataclass
class Challenge:
    """Specific challenge within an environment"""
    challenge_id: str
    challenge_type: ChallengeType
    difficulty: DifficultyLevel
    description: str
    goal: EnvironmentGoal
    constraints: List[EnvironmentConstraint] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # Challenge IDs
    rewards: Dict[str, float] = field(default_factory=dict)  # skill -> reward
    completion_count: int = 0
    best_performance: float = 0.0  # 0.0-1.0

    def add_constraint(self, constraint: EnvironmentConstraint) -> bool:
        """Add constraint to challenge"""
        self.constraints.append(constraint)
        return True

    def add_prerequisite(self, challenge_id: str) -> bool:
        """Add prerequisite challenge"""
        if challenge_id not in self.prerequisites:
            self.prerequisites.append(challenge_id)
        return True

    def add_skill_reward(self, skill_name: str, reward: float) -> bool:
        """Add skill reward for completion"""
        if not (0.0 <= reward <= 1.0):
            return False
        self.rewards[skill_name] = reward
        return True

    def record_completion(self, performance: float) -> bool:
        """Record successful challenge completion"""
        if not (0.0 <= performance <= 1.0):
            return False
        self.completion_count += 1
        self.best_performance = max(self.best_performance, performance)
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.challenge_id,
            "type": self.challenge_type.value,
            "difficulty": self.difficulty.value,
            "description": self.description,
            "completions": self.completion_count,
            "best_performance": self.best_performance
        }


@dataclass
class LearningEnvironment:
    """Learning environment providing scaffolded challenges"""
    environment_id: str
    environment_type: EnvironmentType
    name: str
    description: str
    difficulty: DifficultyLevel
    challenges: Dict[str, Challenge] = field(default_factory=dict)
    primary_goal: Optional[EnvironmentGoal] = None
    max_agents: int = 1  # 1 for solo, >1 for multi-agent
    time_limit: Optional[float] = None  # Total time limit
    completion_count: int = 0
    avg_performance: float = 0.5

    def add_challenge(self, challenge: Challenge) -> bool:
        """Add challenge to environment"""
        if challenge.challenge_id in self.challenges:
            return False
        self.challenges[challenge.challenge_id] = challenge
        return True

    def get_available_challenges(self, completed: List[str]) -> List[Challenge]:
        """Get challenges available based on completed challenges"""
        available = []
        for challenge in self.challenges.values():
            # Check if all prerequisites are met
            prereqs_met = all(p in completed for p in challenge.prerequisites)
            if prereqs_met and challenge.challenge_id not in completed:
                available.append(challenge)
        return available

    def record_completion(self, performance: float) -> bool:
        """Record environment completion"""
        if not (0.0 <= performance <= 1.0):
            return False
        self.completion_count += 1
        # Update average performance
        self.avg_performance = (self.avg_performance * (self.completion_count - 1) + performance) / self.completion_count
        return True

    def get_learning_path_recommendation(self, completed: List[str]) -> Optional[str]:
        """Recommend next challenge based on completed challenges"""
        available = self.get_available_challenges(completed)
        if not available:
            return None
        # Recommend easiest available challenge
        easiest = min(available, key=lambda c: (c.difficulty.value, c.challenge_id))
        return easiest.challenge_id

    def to_dict(self) -> Dict:
        return {
            "id": self.environment_id,
            "type": self.environment_type.value,
            "name": self.name,
            "difficulty": self.difficulty.value,
            "challenges": len(self.challenges),
            "completions": self.completion_count,
            "avg_performance": self.avg_performance
        }


@dataclass
class EnvironmentSession:
    """Active session in a learning environment"""
    session_id: str
    environment_id: str
    agent_id: str
    started_at: float = 0.0
    elapsed_time: float = 0.0
    completed_challenges: List[str] = field(default_factory=list)
    current_challenge: Optional[str] = None
    performance_history: List[float] = field(default_factory=list)
    is_active: bool = True

    def start_challenge(self, challenge_id: str) -> bool:
        """Start a challenge"""
        if not self.is_active:
            return False
        self.current_challenge = challenge_id
        return True

    def complete_challenge(self, challenge_id: str, performance: float) -> bool:
        """Complete a challenge"""
        if not (0.0 <= performance <= 1.0):
            return False
        if challenge_id != self.current_challenge:
            return False
        self.completed_challenges.append(challenge_id)
        self.performance_history.append(performance)
        self.current_challenge = None
        return True

    def advance_time(self, delta: float) -> bool:
        """Advance session time"""
        if delta < 0:
            return False
        self.elapsed_time += delta
        return True

    def get_average_performance(self) -> float:
        """Calculate average performance"""
        if not self.performance_history:
            return 0.5
        return sum(self.performance_history) / len(self.performance_history)

    def end_session(self) -> bool:
        """End the session"""
        self.is_active = False
        return True

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "completed": len(self.completed_challenges),
            "current": self.current_challenge,
            "avg_performance": self.get_average_performance(),
            "elapsed_time": self.elapsed_time
        }


class EnvironmentManager:
    """Manage learning environments and agent progress"""

    def __init__(self):
        self.environments: Dict[str, LearningEnvironment] = {}
        self.sessions: Dict[str, EnvironmentSession] = {}
        self.agent_progress: Dict[str, Dict[str, List[str]]] = {}  # agent_id -> env_id -> completed

    def register_environment(self, env: LearningEnvironment) -> bool:
        """Register a learning environment"""
        if env.environment_id in self.environments:
            return False
        self.environments[env.environment_id] = env
        return True

    def create_session(self, session_id: str, environment_id: str, agent_id: str) -> Optional[EnvironmentSession]:
        """Create a new learning session"""
        if environment_id not in self.environments:
            return None
        if session_id in self.sessions:
            return None

        session = EnvironmentSession(session_id, environment_id, agent_id)
        self.sessions[session_id] = session

        # Initialize progress tracking
        if agent_id not in self.agent_progress:
            self.agent_progress[agent_id] = {}
        if environment_id not in self.agent_progress[agent_id]:
            self.agent_progress[agent_id][environment_id] = []

        return session

    def get_session(self, session_id: str) -> Optional[EnvironmentSession]:
        """Get active session"""
        return self.sessions.get(session_id)

    def complete_challenge(self, session_id: str, challenge_id: str, performance: float) -> bool:
        """Complete a challenge in a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        if not session.complete_challenge(challenge_id, performance):
            return False

        # Update agent progress
        env_id = session.environment_id
        if challenge_id not in self.agent_progress[session.agent_id][env_id]:
            self.agent_progress[session.agent_id][env_id].append(challenge_id)

        # Update environment
        env = self.environments[env_id]
        if challenge_id in env.challenges:
            env.challenges[challenge_id].record_completion(performance)

        return True

    def get_recommended_challenge(self, session_id: str) -> Optional[str]:
        """Get recommended next challenge for session"""
        session = self.get_session(session_id)
        if not session:
            return None

        env = self.environments[session.environment_id]
        completed = self.agent_progress[session.agent_id][session.environment_id]
        return env.get_learning_path_recommendation(completed)

    def get_agent_environment_progress(self, agent_id: str, env_id: str) -> float:
        """Get agent's progress percentage in environment"""
        if agent_id not in self.agent_progress:
            return 0.0
        if env_id not in self.agent_progress[agent_id]:
            return 0.0

        env = self.environments.get(env_id)
        if not env:
            return 0.0

        completed_count = len(self.agent_progress[agent_id][env_id])
        total_count = len(env.challenges)
        if total_count == 0:
            return 0.0

        return completed_count / total_count

    def to_dict(self) -> Dict:
        return {
            "environments": len(self.environments),
            "active_sessions": sum(1 for s in self.sessions.values() if s.is_active),
            "agents_tracked": len(self.agent_progress)
        }


# ===== Tests =====

def test_environment_constraint():
    """Test creating environment constraint"""
    constraint = EnvironmentConstraint(
        "c1",
        "No external tools",
        "Agent cannot use external APIs"
    )
    assert constraint.constraint_id == "c1"


def test_environment_goal():
    """Test creating environment goal"""
    goal = EnvironmentGoal(
        "g1",
        "Solve the puzzle",
        "Find the correct combination"
    )
    assert goal.goal_id == "g1"


def test_goal_time_exceeded():
    """Test time limit checking"""
    goal = EnvironmentGoal("g1", "Quick task", "Do it fast", time_limit=10.0)
    assert goal.is_time_exceeded(5.0) is False
    assert goal.is_time_exceeded(15.0) is True


def test_challenge_creation():
    """Test creating challenge"""
    goal = EnvironmentGoal("g1", "Solve puzzle", "Get it right")
    challenge = Challenge(
        "ch1",
        ChallengeType.REASONING,
        DifficultyLevel.MEDIUM,
        "Logic puzzle",
        goal
    )
    assert challenge.challenge_id == "ch1"


def test_add_constraint_to_challenge():
    """Test adding constraint to challenge"""
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    constraint = EnvironmentConstraint("c1", "Constraint", "description")
    assert challenge.add_constraint(constraint) is True


def test_add_prerequisite():
    """Test adding prerequisite challenge"""
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    assert challenge.add_prerequisite("ch0") is True


def test_add_skill_reward():
    """Test adding skill reward"""
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    assert challenge.add_skill_reward("logic", 0.5) is True


def test_record_completion():
    """Test recording challenge completion"""
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    assert challenge.record_completion(0.8) is True
    assert challenge.completion_count == 1
    assert challenge.best_performance == 0.8


def test_learning_environment_creation():
    """Test creating learning environment"""
    env = LearningEnvironment(
        "env1",
        EnvironmentType.PUZZLE,
        "Logic Puzzles",
        "A collection of logic puzzles",
        DifficultyLevel.EASY
    )
    assert env.environment_id == "env1"
    assert len(env.challenges) == 0


def test_add_challenge_to_environment():
    """Test adding challenge to environment"""
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    assert env.add_challenge(challenge) is True


def test_get_available_challenges():
    """Test getting available challenges based on completion"""
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")

    # Create challenges with prerequisites
    ch1 = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    ch2 = Challenge("ch2", ChallengeType.REASONING, DifficultyLevel.MEDIUM, "desc", goal)
    ch2.add_prerequisite("ch1")

    env.add_challenge(ch1)
    env.add_challenge(ch2)

    # Initially only ch1 is available
    available = env.get_available_challenges([])
    assert len(available) == 1
    assert available[0].challenge_id == "ch1"

    # After completing ch1, ch2 becomes available
    available = env.get_available_challenges(["ch1"])
    assert len(available) == 1
    assert available[0].challenge_id == "ch2"


def test_learning_path_recommendation():
    """Test getting learning path recommendation"""
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")

    ch1 = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    ch2 = Challenge("ch2", ChallengeType.REASONING, DifficultyLevel.MEDIUM, "desc", goal)
    ch2.add_prerequisite("ch1")

    env.add_challenge(ch1)
    env.add_challenge(ch2)

    # Recommend ch1 first
    recommended = env.get_learning_path_recommendation([])
    assert recommended == "ch1"

    # Recommend ch2 after ch1
    recommended = env.get_learning_path_recommendation(["ch1"])
    assert recommended == "ch2"


def test_environment_session():
    """Test creating environment session"""
    session = EnvironmentSession("sess1", "env1", "a1")
    assert session.session_id == "sess1"
    assert session.is_active is True


def test_start_challenge():
    """Test starting challenge in session"""
    session = EnvironmentSession("sess1", "env1", "a1")
    assert session.start_challenge("ch1") is True
    assert session.current_challenge == "ch1"


def test_complete_challenge_in_session():
    """Test completing challenge in session"""
    session = EnvironmentSession("sess1", "env1", "a1")
    session.start_challenge("ch1")
    assert session.complete_challenge("ch1", 0.85) is True
    assert len(session.completed_challenges) == 1


def test_session_performance_tracking():
    """Test tracking performance in session"""
    session = EnvironmentSession("sess1", "env1", "a1")
    session.start_challenge("ch1")
    session.complete_challenge("ch1", 0.8)
    session.start_challenge("ch2")
    session.complete_challenge("ch2", 0.9)

    avg = session.get_average_performance()
    assert abs(avg - 0.85) < 0.01


def test_advance_time():
    """Test advancing session time"""
    session = EnvironmentSession("sess1", "env1", "a1")
    assert session.advance_time(10.0) is True
    assert session.elapsed_time == 10.0


def test_environment_manager():
    """Test environment manager"""
    manager = EnvironmentManager()
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    assert manager.register_environment(env) is True


def test_create_session():
    """Test creating session through manager"""
    manager = EnvironmentManager()
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    manager.register_environment(env)

    session = manager.create_session("sess1", "env1", "a1")
    assert session is not None
    assert session.agent_id == "a1"


def test_complete_challenge_through_manager():
    """Test completing challenge through manager"""
    manager = EnvironmentManager()
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")
    challenge = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    env.add_challenge(challenge)
    manager.register_environment(env)

    session = manager.create_session("sess1", "env1", "a1")
    session.start_challenge("ch1")

    assert manager.complete_challenge("sess1", "ch1", 0.8) is True


def test_get_recommended_challenge():
    """Test getting recommended challenge"""
    manager = EnvironmentManager()
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")

    ch1 = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    ch2 = Challenge("ch2", ChallengeType.REASONING, DifficultyLevel.MEDIUM, "desc", goal)
    ch2.add_prerequisite("ch1")

    env.add_challenge(ch1)
    env.add_challenge(ch2)
    manager.register_environment(env)

    session = manager.create_session("sess1", "env1", "a1")

    # First recommendation is ch1
    recommended = manager.get_recommended_challenge("sess1")
    assert recommended == "ch1"


def test_agent_progress_tracking():
    """Test tracking agent progress"""
    manager = EnvironmentManager()
    env = LearningEnvironment("env1", EnvironmentType.PUZZLE, "Puzzles", "desc", DifficultyLevel.EASY)
    goal = EnvironmentGoal("g1", "Test", "criteria")

    ch1 = Challenge("ch1", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)
    ch2 = Challenge("ch2", ChallengeType.REASONING, DifficultyLevel.EASY, "desc", goal)

    env.add_challenge(ch1)
    env.add_challenge(ch2)
    manager.register_environment(env)

    session = manager.create_session("sess1", "env1", "a1")
    session.start_challenge("ch1")
    manager.complete_challenge("sess1", "ch1", 0.8)

    progress = manager.get_agent_environment_progress("a1", "env1")
    assert progress == 0.5  # 1 out of 2 challenges


def test_complete_environment_workflow():
    """Test complete learning environment workflow"""
    # Create manager
    manager = EnvironmentManager()

    # Create environment
    env = LearningEnvironment(
        "logic_puzzles",
        EnvironmentType.PUZZLE,
        "Logic Challenges",
        "Learn logical reasoning",
        DifficultyLevel.EASY
    )

    # Create challenges with progression
    goal1 = EnvironmentGoal("g1", "Solve simple logic", "Get it right")
    ch1 = Challenge("ch1_simple", ChallengeType.REASONING, DifficultyLevel.EASY, "Simple logic", goal1)
    ch1.add_skill_reward("logic", 0.3)

    goal2 = EnvironmentGoal("g2", "Solve advanced logic", "Get it right")
    ch2 = Challenge("ch2_advanced", ChallengeType.REASONING, DifficultyLevel.MEDIUM, "Advanced logic", goal2)
    ch2.add_prerequisite("ch1_simple")
    ch2.add_skill_reward("logic", 0.7)

    env.add_challenge(ch1)
    env.add_challenge(ch2)
    manager.register_environment(env)

    # Create session for agent
    session = manager.create_session("sess_explorer", "logic_puzzles", "explorer_ai")
    assert session is not None

    # Agent starts with simple challenge
    recommended = manager.get_recommended_challenge("sess_explorer")
    assert recommended == "ch1_simple"

    # Agent completes simple challenge
    session.start_challenge("ch1_simple")
    assert manager.complete_challenge("sess_explorer", "ch1_simple", 0.9) is True

    # Now advanced challenge is available
    recommended = manager.get_recommended_challenge("sess_explorer")
    assert recommended == "ch2_advanced"

    # Agent completes advanced challenge
    session.start_challenge("ch2_advanced")
    assert manager.complete_challenge("sess_explorer", "ch2_advanced", 0.85) is True

    # Verify progress
    progress = manager.get_agent_environment_progress("explorer_ai", "logic_puzzles")
    assert progress == 1.0  # All challenges completed

    # Verify performance
    avg_perf = session.get_average_performance()
    assert abs(avg_perf - 0.875) < 0.01  # Average of 0.9 and 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
