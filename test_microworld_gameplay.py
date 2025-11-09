"""
Round 58: Microworld Gameplay Integration
Integrates agent systems into actual gameplay. Children raise agents in microworld,
deploy them to real tasks (homework, robots, games), and see them grow.

Connects: Agent Mind (55) + Personality (56) + Learning (57) into playable game.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class GameplayMode(Enum):
    RAISING = "raising"  # Nurturing agent in microworld
    EMPATHIZER = "empathizer"  # First-person experience as agent
    DEPLOYING = "deploying"  # Testing agent on real task
    REFLECTING = "reflecting"  # Learning from deployment


class AgentStats:
    def __init__(self):
        self.intelligence: float = 0.3
        self.personality: float = 0.4
        self.experience: float = 0.2
        self.empathy: float = 0.3

    def overall(self) -> float:
        return (self.intelligence + self.personality + self.experience + self.empathy) / 4.0

    def to_dict(self) -> Dict:
        return {
            "intelligence": self.intelligence,
            "personality": self.personality,
            "experience": self.experience,
            "empathy": self.empathy,
            "overall": self.overall()
        }


@dataclass
class Quest:
    quest_id: str
    title: str
    description: str = ""
    completed: bool = False
    reward_intelligence: float = 0.1
    reward_personality: float = 0.05
    reward_experience: float = 0.1

    def complete(self) -> bool:
        self.completed = True
        return True

    def to_dict(self) -> Dict:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "completed": self.completed
        }


@dataclass
class DeploymentTask:
    task_id: str
    task_type: str  # homework, game, robot, art
    description: str = ""
    success: bool = False
    difficulty: float = 0.5
    reward: float = 0.1

    def complete_task(self, agent_success: bool) -> bool:
        self.success = agent_success
        return True

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "type": self.task_type,
            "difficulty": self.difficulty,
            "success": self.success
        }


class EmpathizerView:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.perceived_world: Dict = {}
        self.available_tools: List[str] = []
        self.available_memory: Dict = {}
        self.feeling: str = "neutral"

    def step_into_agent(self) -> Dict:
        """Show child what agent perceives and has available"""
        return {
            "perception": self.perceived_world,
            "tools": self.available_tools,
            "memory": self.available_memory,
            "feeling": self.feeling
        }

    def set_perception(self, world: Dict) -> bool:
        self.perceived_world = world
        return True

    def add_tool(self, tool_name: str) -> bool:
        if tool_name not in self.available_tools:
            self.available_tools.append(tool_name)
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "tools_available": len(self.available_tools),
            "memory_entries": len(self.available_memory),
            "feeling": self.feeling
        }


class GameSession:
    def __init__(self, player_id: str, agent_id: str):
        self.player_id = player_id
        self.agent_id = agent_id
        self.mode = GameplayMode.RAISING
        self.agent_stats = AgentStats()
        self.quests: List[Quest] = []
        self.completed_quests: int = 0
        self.deployments: List[DeploymentTask] = []
        self.empathizer = EmpathizerView(agent_id)
        self.playtime_hours: float = 0.0

    def add_quest(self, quest: Quest) -> bool:
        self.quests.append(quest)
        return True

    def complete_quest(self, quest_id: str) -> bool:
        for quest in self.quests:
            if quest.quest_id == quest_id:
                if quest.complete():
                    self.completed_quests += 1
                    self.agent_stats.intelligence += quest.reward_intelligence
                    self.agent_stats.personality += quest.reward_personality
                    self.agent_stats.experience += quest.reward_experience
                    self._normalize_stats()
                    return True
        return False

    def deploy_agent(self, task: DeploymentTask) -> bool:
        self.deployments.append(task)
        self.mode = GameplayMode.DEPLOYING
        return True

    def record_deployment_result(self, task_id: str, success: bool) -> bool:
        for task in self.deployments:
            if task.task_id == task_id:
                if task.complete_task(success):
                    if success:
                        self.agent_stats.experience += task.reward
                        self.agent_stats.intelligence += task.reward * 0.5
                    self._normalize_stats()
                    self.mode = GameplayMode.REFLECTING
                    return True
        return False

    def enter_empathizer_mode(self) -> Dict:
        self.mode = GameplayMode.EMPATHIZER
        return self.empathizer.step_into_agent()

    def _normalize_stats(self):
        self.agent_stats.intelligence = min(1.0, self.agent_stats.intelligence)
        self.agent_stats.personality = min(1.0, self.agent_stats.personality)
        self.agent_stats.experience = min(1.0, self.agent_stats.experience)
        self.agent_stats.empathy = min(1.0, self.agent_stats.empathy)

    def advance_playtime(self, hours: float) -> bool:
        self.playtime_hours += hours
        self.agent_stats.empathy += hours * 0.01
        self._normalize_stats()
        return True

    def to_dict(self) -> Dict:
        return {
            "player_id": self.player_id,
            "agent_id": self.agent_id,
            "mode": self.mode.value,
            "agent_stats": self.agent_stats.to_dict(),
            "quests_completed": self.completed_quests,
            "deployments": len(self.deployments),
            "playtime_hours": self.playtime_hours
        }


class GameFactory:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}

    def start_game(self, player_id: str, agent_id: str) -> GameSession:
        session = GameSession(player_id, agent_id)
        self.sessions[player_id] = session
        return session

    def get_session(self, player_id: str) -> Optional[GameSession]:
        return self.sessions.get(player_id)

    def to_dict(self) -> Dict:
        return {
            "total_sessions": len(self.sessions),
            "avg_playtime": sum(s.playtime_hours for s in self.sessions.values()) / len(self.sessions) if self.sessions else 0.0
        }


# Tests
def test_agent_stats_creation():
    stats = AgentStats()
    assert stats.intelligence == 0.3

def test_agent_stats_overall():
    stats = AgentStats()
    overall = stats.overall()
    assert 0.0 <= overall <= 1.0

def test_quest_creation():
    q = Quest("q1", "Learn Perception")
    assert q.quest_id == "q1"
    assert q.completed is False

def test_quest_complete():
    q = Quest("q1", "Learn Perception")
    assert q.complete() is True

def test_deployment_task():
    t = DeploymentTask("t1", "homework", "math")
    assert t.task_type == "homework"

def test_deployment_complete():
    t = DeploymentTask("t1", "homework")
    assert t.complete_task(True) is True

def test_empathizer_view():
    e = EmpathizerView("agent1")
    assert e.agent_id == "agent1"

def test_empathizer_add_tool():
    e = EmpathizerView("agent1")
    assert e.add_tool("calculator") is True

def test_empathizer_step_into():
    e = EmpathizerView("agent1")
    view = e.step_into_agent()
    assert "tools" in view

def test_game_session_creation():
    session = GameSession("player1", "agent1")
    assert session.player_id == "player1"
    assert session.mode == GameplayMode.RAISING

def test_game_session_add_quest():
    session = GameSession("player1", "agent1")
    q = Quest("q1", "Test Quest")
    assert session.add_quest(q) is True

def test_game_session_complete_quest():
    session = GameSession("player1", "agent1")
    q = Quest("q1", "Test")
    session.add_quest(q)
    assert session.complete_quest("q1") is True
    assert session.completed_quests == 1

def test_game_session_quest_reward():
    session = GameSession("player1", "agent1")
    before = session.agent_stats.intelligence
    q = Quest("q1", "Test", reward_intelligence=0.2)
    session.add_quest(q)
    session.complete_quest("q1")
    after = session.agent_stats.intelligence
    assert after > before

def test_game_session_deploy():
    session = GameSession("player1", "agent1")
    task = DeploymentTask("t1", "homework")
    assert session.deploy_agent(task) is True

def test_game_session_deployment_result():
    session = GameSession("player1", "agent1")
    task = DeploymentTask("t1", "homework")
    session.deploy_agent(task)
    assert session.record_deployment_result("t1", True) is True
    assert session.mode == GameplayMode.REFLECTING

def test_game_session_empathizer():
    session = GameSession("player1", "agent1")
    view = session.enter_empathizer_mode()
    assert session.mode == GameplayMode.EMPATHIZER

def test_game_session_playtime():
    session = GameSession("player1", "agent1")
    assert session.advance_playtime(1.0) is True
    assert session.playtime_hours == 1.0

def test_game_session_stat_bounds():
    session = GameSession("player1", "agent1")
    # Simulate many quest completions
    for i in range(20):
        q = Quest(f"q{i}", "Test", reward_intelligence=0.1)
        session.add_quest(q)
        session.complete_quest(f"q{i}")
    # Stats should never exceed 1.0
    assert session.agent_stats.intelligence <= 1.0

def test_game_factory_start():
    factory = GameFactory()
    session = factory.start_game("player1", "agent1")
    assert session is not None

def test_game_factory_retrieve():
    factory = GameFactory()
    factory.start_game("player1", "agent1")
    session = factory.get_session("player1")
    assert session is not None

def test_complete_gameplay_workflow():
    """Full game session: raise agent, quest, deploy, reflect"""
    factory = GameFactory()
    session = factory.start_game("child1", "curious_bot")

    # Raising phase: complete quests
    session.add_quest(Quest("q1", "Learn Perception", reward_intelligence=0.1))
    session.add_quest(Quest("q2", "Master Memory", reward_experience=0.15))
    session.complete_quest("q1")
    session.complete_quest("q2")

    # Empathizer phase: experience as agent
    view = session.enter_empathizer_mode()
    assert session.mode == GameplayMode.EMPATHIZER

    # Deployment phase: test on real task
    task = DeploymentTask("homework_1", "homework", "solve_math_problem")
    session.deploy_agent(task)
    session.record_deployment_result("homework_1", True)

    # Reflection phase
    assert session.mode == GameplayMode.REFLECTING

    # Verify growth
    state = session.to_dict()
    assert state["quests_completed"] == 2
    assert state["deployments"] == 1
    assert state["agent_stats"]["overall"] > 0.3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
