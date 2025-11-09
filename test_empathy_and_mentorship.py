"""
Rounds 41-42: Empathy & Mentorship
- Round 41: First-Person Experience Mode (see through agent's eyes)
- Round 42: Mentorship Guidance System (guide player development)
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class SensorType(Enum):
    """Agent perception types in first-person mode"""
    TEXT = "text"
    VISION = "vision"
    MEMORY = "memory"
    EMOTION = "emotion"
    COMMUNICATION = "communication"


class MentorshipPhase(Enum):
    """Stages of mentorship"""
    ONBOARDING = "onboarding"  # Learn basic concepts
    EXPLORATION = "exploration"  # Explore freely
    CHALLENGE = "challenge"  # Take on difficult tasks
    MASTERY = "mastery"  # Refine skills to excellence


@dataclass
class SensorReading:
    """Data from agent sensor"""
    sensor_type: SensorType
    data: Any
    timestamp: float = 0.0
    relevance: float = 1.0  # 0.0-1.0

    def to_dict(self) -> Dict:
        return {
            "sensor": self.sensor_type.value,
            "relevance": self.relevance,
            "timestamp": self.timestamp
        }


@dataclass
class FirstPersonExperience:
    """First-person view through agent's sensors"""
    experience_id: str
    agent_id: str
    duration: float = 0.0
    sensors_active: List[SensorType] = field(default_factory=list)
    readings: List[SensorReading] = field(default_factory=list)
    task_objective: str = ""
    confusion_level: float = 0.0  # 0.0-1.0, how confused agent is
    confidence_level: float = 0.5  # 0.0-1.0

    def add_sensor(self, sensor_type: SensorType) -> bool:
        """Activate sensor for experience"""
        if sensor_type not in self.sensors_active:
            self.sensors_active.append(sensor_type)
        return True

    def add_reading(self, reading: SensorReading) -> bool:
        """Record sensor reading"""
        self.readings.append(reading)
        return True

    def get_agent_perspective(self) -> Dict:
        """Get what agent perceives"""
        return {
            "objective": self.task_objective,
            "sensors": [s.value for s in self.sensors_active],
            "confusion": self.confusion_level,
            "confidence": self.confidence_level,
            "reading_count": len(self.readings)
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.experience_id,
            "agent_id": self.agent_id,
            "duration": self.duration,
            "readings": len(self.readings),
            "confusion": self.confusion_level,
            "confidence": self.confidence_level
        }


class EmpathySystem:
    """Enable players to experience agents' perspective"""

    def __init__(self):
        self.experiences: Dict[str, FirstPersonExperience] = {}
        self.experience_history: Dict[str, List[str]] = {}  # agent_id -> exp_ids

    def create_experience(self, exp_id: str, agent_id: str, objective: str) -> FirstPersonExperience:
        """Start first-person experience"""
        experience = FirstPersonExperience(exp_id, agent_id, task_objective=objective)
        self.experiences[exp_id] = experience

        if agent_id not in self.experience_history:
            self.experience_history[agent_id] = []
        self.experience_history[agent_id].append(exp_id)

        return experience

    def get_experience(self, exp_id: str) -> Optional[FirstPersonExperience]:
        """Get active experience"""
        return self.experiences.get(exp_id)

    def end_experience(self, exp_id: str, duration: float) -> bool:
        """End experience and record duration"""
        exp = self.get_experience(exp_id)
        if not exp:
            return False
        exp.duration = duration
        return True

    def get_agent_learning_insights(self, agent_id: str) -> Dict:
        """Get insights about agent from experiences"""
        if agent_id not in self.experience_history:
            return {}

        total_confusion = 0.0
        total_confidence = 0.0
        count = len(self.experience_history[agent_id])

        for exp_id in self.experience_history[agent_id]:
            exp = self.experiences.get(exp_id)
            if exp:
                total_confusion += exp.confusion_level
                total_confidence += exp.confidence_level

        if count == 0:
            return {}

        return {
            "avg_confusion": total_confusion / count,
            "avg_confidence": total_confidence / count,
            "experiences_count": count,
            "insights": f"Agent struggles with {int((total_confusion / count) * 100)}% of tasks"
        }

    def to_dict(self) -> Dict:
        return {
            "active_experiences": len(self.experiences),
            "agents_tracked": len(self.experience_history)
        }


@dataclass
class MentorshipGoal:
    """Goal in mentorship progression"""
    goal_id: str
    phase: MentorshipPhase
    description: str
    completion_criteria: str
    xp_reward: float = 100.0  # Experience points
    is_completed: bool = False

    def complete(self) -> bool:
        """Mark goal as completed"""
        self.is_completed = True
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.goal_id,
            "phase": self.phase.value,
            "description": self.description,
            "completed": self.is_completed,
            "reward": self.xp_reward
        }


@dataclass
class MentorshipPath:
    """Personalized guidance path for player"""
    path_id: str
    player_id: str
    current_phase: MentorshipPhase = MentorshipPhase.ONBOARDING
    goals: List[MentorshipGoal] = field(default_factory=list)
    total_xp: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    is_active: bool = True

    def add_goal(self, goal: MentorshipGoal) -> bool:
        """Add mentorship goal"""
        self.goals.append(goal)
        return True

    def complete_goal(self, goal_id: str) -> bool:
        """Complete a goal"""
        for goal in self.goals:
            if goal.goal_id == goal_id:
                if goal.complete():
                    self.total_xp += goal.xp_reward
                    return True
        return False

    def get_available_goals(self) -> List[MentorshipGoal]:
        """Get uncompleted goals in current phase"""
        return [g for g in self.goals if not g.is_completed and g.phase == self.current_phase]

    def get_next_recommendation(self) -> Optional[str]:
        """Get next recommended action"""
        available = self.get_available_goals()
        if available:
            return f"Next: {available[0].description}"
        return "Congratulations! You've completed this phase."

    def advance_phase(self) -> bool:
        """Advance to next phase if all goals completed"""
        current_goals = [g for g in self.goals if g.phase == self.current_phase]
        if all(g.is_completed for g in current_goals):
            phases = list(MentorshipPhase)
            current_idx = phases.index(self.current_phase)
            if current_idx < len(phases) - 1:
                self.current_phase = phases[current_idx + 1]
                return True
        return False

    def to_dict(self) -> Dict:
        return {
            "player_id": self.player_id,
            "phase": self.current_phase.value,
            "total_xp": self.total_xp,
            "goals_completed": sum(1 for g in self.goals if g.is_completed),
            "goals_total": len(self.goals)
        }


class MentorshipSystem:
    """Guide player development through mentorship"""

    def __init__(self):
        self.paths: Dict[str, MentorshipPath] = {}

    def create_path(self, path_id: str, player_id: str) -> MentorshipPath:
        """Create mentorship path for player"""
        path = MentorshipPath(path_id, player_id)

        # Add onboarding goals
        path.add_goal(MentorshipGoal(
            "goal_learn_basics",
            MentorshipPhase.ONBOARDING,
            "Understand agent basics",
            "Learn about the 4 primitives",
            50.0
        ))
        path.add_goal(MentorshipGoal(
            "goal_first_agent",
            MentorshipPhase.ONBOARDING,
            "Create your first agent",
            "Successfully create an agent",
            100.0
        ))

        # Add exploration goals
        path.add_goal(MentorshipGoal(
            "goal_explore_tools",
            MentorshipPhase.EXPLORATION,
            "Explore tool unlocking",
            "Unlock at least 3 tools",
            75.0
        ))
        path.add_goal(MentorshipGoal(
            "goal_first_society",
            MentorshipPhase.EXPLORATION,
            "Create multi-agent society",
            "Form a society with 3+ agents",
            150.0
        ))

        self.paths[path_id] = path
        return path

    def get_path(self, path_id: str) -> Optional[MentorshipPath]:
        """Get mentorship path"""
        return self.paths.get(path_id)

    def complete_path_goal(self, path_id: str, goal_id: str) -> bool:
        """Mark goal as complete"""
        path = self.get_path(path_id)
        if not path:
            return False
        return path.complete_goal(goal_id)

    def get_player_guidance(self, path_id: str) -> Dict:
        """Get personalized guidance for player"""
        path = self.get_path(path_id)
        if not path:
            return {}

        return {
            "phase": path.current_phase.value,
            "next_action": path.get_next_recommendation(),
            "xp_earned": path.total_xp,
            "progress": f"{sum(1 for g in path.goals if g.is_completed)}/{len(path.goals)} goals"
        }

    def to_dict(self) -> Dict:
        return {
            "active_paths": sum(1 for p in self.paths.values() if p.is_active),
            "total_paths": len(self.paths)
        }


# ===== Tests =====

def test_sensor_reading():
    """Test sensor reading"""
    reading = SensorReading(SensorType.TEXT, "agent sees text")
    assert reading.sensor_type == SensorType.TEXT


def test_first_person_experience():
    """Test first-person experience"""
    exp = FirstPersonExperience("exp1", "a1", task_objective="Solve puzzle")
    assert exp.agent_id == "a1"


def test_add_sensor():
    """Test adding sensor to experience"""
    exp = FirstPersonExperience("exp1", "a1")
    assert exp.add_sensor(SensorType.TEXT) is True
    assert SensorType.TEXT in exp.sensors_active


def test_get_agent_perspective():
    """Test getting agent perspective"""
    exp = FirstPersonExperience("exp1", "a1", task_objective="Solve puzzle")
    exp.add_sensor(SensorType.TEXT)
    exp.confusion_level = 0.3
    perspective = exp.get_agent_perspective()
    assert perspective["objective"] == "Solve puzzle"
    assert perspective["confusion"] == 0.3


def test_empathy_system():
    """Test empathy system"""
    system = EmpathySystem()
    exp = system.create_experience("exp1", "a1", "Solve puzzle")
    assert exp is not None


def test_empathy_system_get_learning_insights():
    """Test getting learning insights"""
    system = EmpathySystem()
    exp = system.create_experience("exp1", "a1", "Test")
    exp.confusion_level = 0.4
    exp.confidence_level = 0.6

    insights = system.get_agent_learning_insights("a1")
    assert "avg_confusion" in insights


def test_mentorship_goal():
    """Test mentorship goal"""
    goal = MentorshipGoal("g1", MentorshipPhase.ONBOARDING, "Learn basics", "criteria")
    assert goal.goal_id == "g1"


def test_complete_mentorship_goal():
    """Test completing goal"""
    goal = MentorshipGoal("g1", MentorshipPhase.ONBOARDING, "Learn basics", "criteria")
    assert goal.complete() is True
    assert goal.is_completed is True


def test_mentorship_path():
    """Test mentorship path"""
    path = MentorshipPath("p1", "player1")
    goal = MentorshipGoal("g1", MentorshipPhase.ONBOARDING, "Learn", "criteria")
    path.add_goal(goal)
    assert len(path.goals) == 1


def test_get_available_goals():
    """Test getting available goals"""
    path = MentorshipPath("p1", "player1")
    goal = MentorshipGoal("g1", MentorshipPhase.ONBOARDING, "Learn", "criteria")
    path.add_goal(goal)

    available = path.get_available_goals()
    assert len(available) == 1


def test_advance_phase():
    """Test advancing mentorship phase"""
    path = MentorshipPath("p1", "player1", current_phase=MentorshipPhase.ONBOARDING)
    goal = MentorshipGoal("g1", MentorshipPhase.ONBOARDING, "Learn", "criteria")
    path.add_goal(goal)

    # Can't advance with incomplete goals
    assert path.advance_phase() is False

    # Complete goal and advance
    path.complete_goal("g1")
    assert path.advance_phase() is True
    assert path.current_phase == MentorshipPhase.EXPLORATION


def test_mentorship_system():
    """Test mentorship system"""
    system = MentorshipSystem()
    path = system.create_path("p1", "player1")
    assert path is not None
    assert path.current_phase == MentorshipPhase.ONBOARDING


def test_complete_path_goal():
    """Test completing goal through system"""
    system = MentorshipSystem()
    path = system.create_path("p1", "player1")

    assert system.complete_path_goal("p1", "goal_learn_basics") is True


def test_get_player_guidance():
    """Test getting player guidance"""
    system = MentorshipSystem()
    path = system.create_path("p1", "player1")

    guidance = system.get_player_guidance("p1")
    assert "phase" in guidance
    assert "next_action" in guidance


def test_complete_empathy_workflow():
    """Test complete empathy and mentorship workflow"""
    empathy = EmpathySystem()
    mentorship = MentorshipSystem()

    # Player starts mentorship
    path = mentorship.create_path("p1", "player1")
    assert path.current_phase == MentorshipPhase.ONBOARDING

    # Player enters first-person experience with agent
    exp = empathy.create_experience("exp1", "a1", "Learn basics")
    exp.add_sensor(SensorType.TEXT)
    exp.add_sensor(SensorType.MEMORY)
    exp.confusion_level = 0.2
    exp.confidence_level = 0.8

    # Experience provides insights
    insights = empathy.get_agent_learning_insights("a1")
    assert insights["avg_confidence"] == 0.8

    # Player completes mentorship goal
    mentorship.complete_path_goal("p1", "goal_learn_basics")
    guidance = mentorship.get_player_guidance("p1")
    assert "goals" in guidance["progress"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
