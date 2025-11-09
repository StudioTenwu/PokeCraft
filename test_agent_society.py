"""
Test suite for Multi-Agent Collaboration & Society (Round 8).
Tests agent-to-agent collaboration, societies, and emergent behaviors.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from agent_core import Agent, AgentState, Task
from agent_personality import Personality, PersonalityTrait
from agent_memory import Memory
from agent_toolkit import Toolkit, ToolDefinition, ToolCategory


class AgentRole(str):
    """Roles agents can take in collaboration."""
    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    OBSERVER = "observer"
    MEDIATOR = "mediator"
    SPECIALIST = "specialist"


class CollaborationMetrics:
    """Tracks collaboration effectiveness."""

    def __init__(self):
        self.total_messages = 0
        self.successful_exchanges = 0
        self.failed_exchanges = 0
        self.resolution_time = 0.0  # seconds
        self.consensus_rate = 0.0  # 0.0-1.0
        self.participation_scores: Dict[str, float] = {}
        self.conflict_resolution_count = 0

    def record_message(self, sender_id: str, success: bool):
        """Record a message exchange."""
        self.total_messages += 1
        if success:
            self.successful_exchanges += 1
        else:
            self.failed_exchanges += 1

        if sender_id not in self.participation_scores:
            self.participation_scores[sender_id] = 0.0
        self.participation_scores[sender_id] += 1.0 if success else 0.5

    def get_health_score(self) -> float:
        """Calculate overall collaboration health (0.0-1.0)."""
        if self.total_messages == 0:
            return 0.0

        success_rate = self.successful_exchanges / self.total_messages
        return (success_rate * 0.6 + self.consensus_rate * 0.4)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metrics."""
        return {
            "total_messages": self.total_messages,
            "successful_exchanges": self.successful_exchanges,
            "failed_exchanges": self.failed_exchanges,
            "resolution_time": self.resolution_time,
            "consensus_rate": self.consensus_rate,
            "health_score": self.get_health_score(),
            "participation_scores": self.participation_scores
        }


class AgentSociety:
    """A collaborative group of agents."""

    def __init__(self, society_id: str, max_members: int = 10):
        self.society_id = society_id
        self.members: Dict[str, Agent] = {}
        self.roles: Dict[str, str] = {}  # agent_id -> role
        self.max_members = max_members
        self.created_at = datetime.now()
        self.active = True
        self.shared_goals: List[str] = []
        self.shared_memory: List[Dict[str, Any]] = []  # Collective memory
        self.collaboration_metrics = CollaborationMetrics()
        self.conflict_log: List[Dict[str, Any]] = []

    def add_member(self, agent: Agent, role: str = AgentRole.CONTRIBUTOR) -> bool:
        """Add an agent to the society."""
        if len(self.members) >= self.max_members:
            return False

        if agent.agent_id in self.members:
            return False

        self.members[agent.agent_id] = agent
        self.roles[agent.agent_id] = role
        return True

    def remove_member(self, agent_id: str) -> bool:
        """Remove an agent from the society."""
        if agent_id not in self.members:
            return False

        del self.members[agent_id]
        del self.roles[agent_id]
        return True

    def set_member_role(self, agent_id: str, role: str) -> bool:
        """Change an agent's role in the society."""
        if agent_id not in self.members:
            return False

        self.roles[agent_id] = role
        return True

    def get_members_by_role(self, role: str) -> List[Agent]:
        """Get all agents with a specific role."""
        return [
            agent for agent_id, agent in self.members.items()
            if self.roles[agent_id] == role
        ]

    def add_shared_goal(self, goal: str) -> bool:
        """Add a shared goal for the society."""
        if goal not in self.shared_goals:
            self.shared_goals.append(goal)
            return True
        return False

    def record_conflict(self, agent_ids: List[str], description: str, resolution: str = None):
        """Log a conflict between agents."""
        self.conflict_log.append({
            "timestamp": datetime.now(),
            "agents": agent_ids,
            "description": description,
            "resolution": resolution
        })
        self.collaboration_metrics.conflict_resolution_count += 1

    def record_collaboration(self, agent_ids: List[str], success: bool):
        """Record a successful or failed collaboration."""
        for agent_id in agent_ids:
            self.collaboration_metrics.record_message(agent_id, success)

    def get_cohesion_score(self) -> float:
        """Calculate society cohesion (0.0-1.0)."""
        if not self.members:
            return 0.0

        # More members = more potential complexity
        member_factor = min(len(self.members) / 10.0, 1.0)

        # Shared goals indicate alignment
        goal_factor = min(len(self.shared_goals) / 5.0, 1.0)

        # Low conflict = high cohesion
        if self.collaboration_metrics.total_messages == 0:
            conflict_factor = 0.5
        else:
            conflict_rate = (
                self.collaboration_metrics.conflict_resolution_count /
                self.collaboration_metrics.total_messages
            )
            conflict_factor = max(0.0, 1.0 - conflict_rate)

        return (member_factor * 0.3 + goal_factor * 0.4 + conflict_factor * 0.3)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize society state."""
        return {
            "society_id": self.society_id,
            "member_count": len(self.members),
            "roles": self.roles,
            "shared_goals": self.shared_goals,
            "active": self.active,
            "cohesion_score": self.get_cohesion_score(),
            "metrics": self.collaboration_metrics.to_dict(),
            "created_at": self.created_at.isoformat()
        }


class CollaborativeTask:
    """A task that requires multiple agents to collaborate."""

    def __init__(
        self, task_id: str, description: str,
        required_agents: int, difficulty: float = 0.5
    ):
        self.task_id = task_id
        self.description = description
        self.required_agents = required_agents
        self.difficulty = difficulty
        self.assigned_agents: List[str] = []
        self.status = "pending"  # pending, in_progress, completed, failed
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result: Dict[str, Any] = None
        self.contributions: Dict[str, Any] = {}  # agent_id -> contribution

    def assign_agent(self, agent_id: str) -> bool:
        """Assign an agent to the task."""
        if len(self.assigned_agents) >= self.required_agents:
            return False

        if agent_id in self.assigned_agents:
            return False

        self.assigned_agents.append(agent_id)
        return True

    def start(self) -> bool:
        """Start the collaborative task."""
        if len(self.assigned_agents) < self.required_agents:
            return False

        self.status = "in_progress"
        self.started_at = datetime.now()
        return True

    def record_contribution(self, agent_id: str, contribution: Any) -> bool:
        """Record an agent's contribution."""
        if agent_id not in self.assigned_agents:
            return False

        self.contributions[agent_id] = contribution
        return True

    def complete(self, result: Dict[str, Any]) -> bool:
        """Mark the task as completed."""
        if self.status != "in_progress":
            return False

        self.status = "completed"
        self.completed_at = datetime.now()
        self.result = result
        return True

    def fail(self) -> bool:
        """Mark the task as failed."""
        if self.status != "in_progress":
            return False

        self.status = "failed"
        return True

    def get_execution_time(self) -> float:
        """Get execution time in seconds."""
        if not self.started_at:
            return 0.0

        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task state."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "assigned_agents": self.assigned_agents,
            "required_agents": self.required_agents,
            "execution_time": self.get_execution_time(),
            "contributions": self.contributions,
            "result": self.result
        }


class AgentSocietyManager:
    """Manages multiple societies and their interactions."""

    def __init__(self):
        self.societies: Dict[str, AgentSociety] = {}
        self.collaborative_tasks: Dict[str, CollaborativeTask] = {}
        self.agent_societies: Dict[str, List[str]] = {}  # agent_id -> [society_ids]

    def create_society(self, society_id: str, max_members: int = 10) -> AgentSociety:
        """Create a new society."""
        if society_id in self.societies:
            return None

        society = AgentSociety(society_id, max_members)
        self.societies[society_id] = society
        return society

    def add_agent_to_society(self, agent_id: str, society_id: str, role: str = AgentRole.CONTRIBUTOR) -> bool:
        """Add an agent to a society."""
        if society_id not in self.societies:
            return False

        society = self.societies[society_id]
        # Agents aren't directly added here, would need the Agent object

        if agent_id not in self.agent_societies:
            self.agent_societies[agent_id] = []

        if society_id not in self.agent_societies[agent_id]:
            self.agent_societies[agent_id].append(society_id)

        return True

    def create_collaborative_task(
        self, task_id: str, description: str,
        society_id: str, required_agents: int,
        difficulty: float = 0.5
    ) -> CollaborativeTask:
        """Create a collaborative task within a society."""
        if society_id not in self.societies:
            return None

        task = CollaborativeTask(task_id, description, required_agents, difficulty)
        self.collaborative_tasks[task_id] = task
        return task

    def get_society_collaboration_health(self, society_id: str) -> float:
        """Get overall collaboration health of a society."""
        if society_id not in self.societies:
            return 0.0

        society = self.societies[society_id]
        return society.collaboration_metrics.get_health_score()

    def get_agent_collaboration_impact(self, agent_id: str) -> float:
        """Calculate an agent's impact on collaborations."""
        total_impact = 0.0
        society_count = 0

        for society_id in self.agent_societies.get(agent_id, []):
            if society_id in self.societies:
                society = self.societies[society_id]
                if agent_id in society.collaboration_metrics.participation_scores:
                    score = society.collaboration_metrics.participation_scores[agent_id]
                    total_impact += score
                    society_count += 1

        if society_count == 0:
            return 0.0

        return total_impact / society_count

    def dissolve_society(self, society_id: str) -> bool:
        """Dissolve a society."""
        if society_id not in self.societies:
            return False

        society = self.societies[society_id]
        society.active = False

        # Remove society from agents' society lists
        for agent_id in list(self.agent_societies.keys()):
            if society_id in self.agent_societies[agent_id]:
                self.agent_societies[agent_id].remove(society_id)

        return True


# ===== TESTS =====

def test_society_creation():
    """Test creating an agent society."""
    society = AgentSociety("society_1", max_members=5)

    assert society.society_id == "society_1"
    assert society.max_members == 5
    assert len(society.members) == 0
    assert society.active


def test_add_remove_members():
    """Test adding and removing members to society."""
    society = AgentSociety("society_1")
    agent1 = Agent("agent_1")
    agent2 = Agent("agent_2")

    # Add members
    assert society.add_member(agent1, AgentRole.LEADER)
    assert society.add_member(agent2, AgentRole.CONTRIBUTOR)
    assert len(society.members) == 2

    # Remove member
    assert society.remove_member(agent1.agent_id)
    assert len(society.members) == 1
    assert agent1.agent_id not in society.members


def test_society_roles():
    """Test member roles in society."""
    society = AgentSociety("society_1")
    agent1 = Agent("agent_1")
    agent2 = Agent("agent_2")
    agent3 = Agent("agent_3")

    society.add_member(agent1, AgentRole.LEADER)
    society.add_member(agent2, AgentRole.CONTRIBUTOR)
    society.add_member(agent3, AgentRole.OBSERVER)

    # Get members by role
    leaders = society.get_members_by_role(AgentRole.LEADER)
    assert len(leaders) == 1
    assert leaders[0].agent_id == agent1.agent_id

    contributors = society.get_members_by_role(AgentRole.CONTRIBUTOR)
    assert len(contributors) == 1

    # Change role
    assert society.set_member_role(agent2.agent_id, AgentRole.SPECIALIST)
    assert agent2.agent_id in [a.agent_id for a in society.get_members_by_role(AgentRole.SPECIALIST)]


def test_shared_goals():
    """Test adding shared goals to society."""
    society = AgentSociety("society_1")

    assert society.add_shared_goal("goal_1")
    assert society.add_shared_goal("goal_2")
    assert not society.add_shared_goal("goal_1")  # Duplicate
    assert len(society.shared_goals) == 2


def test_collaboration_metrics():
    """Test tracking collaboration metrics."""
    metrics = CollaborationMetrics()

    metrics.record_message("agent_1", success=True)
    metrics.record_message("agent_1", success=True)
    metrics.record_message("agent_2", success=False)

    assert metrics.total_messages == 3
    assert metrics.successful_exchanges == 2
    assert metrics.failed_exchanges == 1
    assert metrics.get_health_score() > 0.0


def test_conflict_logging():
    """Test recording conflicts in society."""
    society = AgentSociety("society_1")
    agent1 = Agent("agent_1")
    agent2 = Agent("agent_2")

    society.add_member(agent1)
    society.add_member(agent2)

    society.record_conflict(
        [agent1.agent_id, agent2.agent_id],
        "Disagreement on approach",
        "Negotiated compromise"
    )

    assert len(society.conflict_log) == 1
    assert society.conflict_log[0]["description"] == "Disagreement on approach"


def test_society_cohesion():
    """Test calculating society cohesion."""
    society = AgentSociety("society_1")
    agent1 = Agent("agent_1")
    agent2 = Agent("agent_2")

    society.add_member(agent1)
    society.add_member(agent2)
    society.add_shared_goal("goal_1")
    society.add_shared_goal("goal_2")

    # Record successful collaborations
    society.record_collaboration([agent1.agent_id, agent2.agent_id], success=True)

    cohesion = society.get_cohesion_score()
    assert 0.0 <= cohesion <= 1.0
    assert cohesion > 0.0


def test_collaborative_task_creation():
    """Test creating a collaborative task."""
    task = CollaborativeTask(
        "task_1",
        "Solve complex problem",
        required_agents=2,
        difficulty=0.7
    )

    assert task.task_id == "task_1"
    assert task.required_agents == 2
    assert task.status == "pending"
    assert len(task.assigned_agents) == 0


def test_collaborative_task_assignment():
    """Test assigning agents to collaborative task."""
    task = CollaborativeTask("task_1", "Task", required_agents=2)

    assert task.assign_agent("agent_1")
    assert task.assign_agent("agent_2")
    assert not task.assign_agent("agent_3")  # Already full
    assert len(task.assigned_agents) == 2


def test_collaborative_task_lifecycle():
    """Test full lifecycle of collaborative task."""
    task = CollaborativeTask("task_1", "Task", required_agents=2)

    # Can't start without enough agents
    assert not task.start()

    # Assign agents
    task.assign_agent("agent_1")
    task.assign_agent("agent_2")

    # Start task
    assert task.start()
    assert task.status == "in_progress"
    assert task.started_at is not None

    # Record contributions
    assert task.record_contribution("agent_1", {"contribution": "data"})
    assert task.record_contribution("agent_2", {"contribution": "analysis"})

    # Complete task
    assert task.complete({"result": "success"})
    assert task.status == "completed"
    assert task.completed_at is not None
    assert task.get_execution_time() >= 0.0


def test_society_manager_creation():
    """Test managing multiple societies."""
    manager = AgentSocietyManager()

    society1 = manager.create_society("society_1", max_members=5)
    society2 = manager.create_society("society_2", max_members=3)

    assert society1 is not None
    assert society2 is not None
    assert "society_1" in manager.societies
    assert "society_2" in manager.societies


def test_society_manager_collaborative_task():
    """Test creating collaborative tasks through manager."""
    manager = AgentSocietyManager()
    manager.create_society("society_1")

    task = manager.create_collaborative_task(
        "task_1",
        "Group project",
        "society_1",
        required_agents=3,
        difficulty=0.6
    )

    assert task is not None
    assert "task_1" in manager.collaborative_tasks


def test_agent_collaboration_impact():
    """Test calculating agent collaboration impact."""
    manager = AgentSocietyManager()
    society = manager.create_society("society_1")

    agent1_id = "agent_1"
    manager.add_agent_to_society(agent1_id, "society_1")

    # Record collaborations
    society.collaboration_metrics.record_message(agent1_id, True)
    society.collaboration_metrics.record_message(agent1_id, True)

    impact = manager.get_agent_collaboration_impact(agent1_id)
    assert impact >= 0.0


def test_society_dissolution():
    """Test dissolving a society."""
    manager = AgentSocietyManager()
    society = manager.create_society("society_1")

    agent1_id = "agent_1"
    manager.add_agent_to_society(agent1_id, "society_1")

    assert manager.dissolve_society("society_1")
    assert not society.active
    assert "society_1" not in manager.agent_societies.get(agent1_id, [])


def test_max_members_limit():
    """Test max members limit on society."""
    society = AgentSociety("society_1", max_members=2)
    agent1 = Agent("agent_1")
    agent2 = Agent("agent_2")
    agent3 = Agent("agent_3")

    assert society.add_member(agent1)
    assert society.add_member(agent2)
    assert not society.add_member(agent3)  # Exceeds limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
