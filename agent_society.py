"""
Multi-Agent Collaboration & Society System for AICraft (Round 8).
Enables agents to form societies, collaborate on tasks, and exhibit emergent behaviors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class AgentRole(Enum):
    """Roles agents can take in collaboration."""
    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    OBSERVER = "observer"
    MEDIATOR = "mediator"
    SPECIALIST = "specialist"


class TaskStatus(Enum):
    """Status of collaborative tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CollaborationMetrics:
    """Tracks collaboration effectiveness."""
    total_messages: int = 0
    successful_exchanges: int = 0
    failed_exchanges: int = 0
    resolution_time: float = 0.0  # seconds
    consensus_rate: float = 0.0  # 0.0-1.0
    conflict_resolution_count: int = 0
    participation_scores: Dict[str, float] = field(default_factory=dict)

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
            "participation_scores": self.participation_scores,
            "conflict_resolution_count": self.conflict_resolution_count
        }


@dataclass
class ConflictRecord:
    """Record of a conflict between agents."""
    timestamp: datetime
    agents: List[str]
    description: str
    resolution: Optional[str] = None
    severity: float = 0.5  # 0.0-1.0
    impact: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize conflict record."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agents": self.agents,
            "description": self.description,
            "resolution": self.resolution,
            "severity": self.severity,
            "impact": self.impact
        }


class AgentSociety:
    """A collaborative group of agents with shared goals and dynamics."""

    def __init__(self, society_id: str, max_members: int = 10):
        self.society_id = society_id
        self.members: Dict[str, Any] = {}  # agent_id -> Agent
        self.roles: Dict[str, str] = {}  # agent_id -> role
        self.max_members = max_members
        self.created_at = datetime.now()
        self.active = True
        self.shared_goals: List[str] = []
        self.shared_memory: List[Dict[str, Any]] = []  # Collective memory
        self.collaboration_metrics = CollaborationMetrics()
        self.conflict_log: List[ConflictRecord] = []

    def add_member(self, agent: Any, role: str = "contributor") -> bool:
        """Add an agent to the society."""
        if len(self.members) >= self.max_members:
            return False

        agent_id = agent.agent_id if hasattr(agent, 'agent_id') else str(agent)
        if agent_id in self.members:
            return False

        self.members[agent_id] = agent
        self.roles[agent_id] = role
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

    def get_members_by_role(self, role: str) -> List[Any]:
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

    def add_to_shared_memory(self, entry: Dict[str, Any]):
        """Add entry to shared memory."""
        entry["timestamp"] = datetime.now()
        self.shared_memory.append(entry)

    def record_conflict(
        self, agent_ids: List[str], description: str,
        resolution: Optional[str] = None, severity: float = 0.5
    ):
        """Log a conflict between agents."""
        conflict = ConflictRecord(
            timestamp=datetime.now(),
            agents=agent_ids,
            description=description,
            resolution=resolution,
            severity=severity
        )
        self.conflict_log.append(conflict)
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
                max(self.collaboration_metrics.total_messages, 1)
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
            "conflict_count": len(self.conflict_log),
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
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
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

        self.status = TaskStatus.IN_PROGRESS
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
        if self.status != TaskStatus.IN_PROGRESS:
            return False

        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        return True

    def fail(self) -> bool:
        """Mark the task as failed."""
        if self.status != TaskStatus.IN_PROGRESS:
            return False

        self.status = TaskStatus.FAILED
        return True

    def get_execution_time(self) -> float:
        """Get execution time in seconds."""
        if not self.started_at:
            return 0.0

        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def get_completion_rate(self) -> float:
        """Get percentage of contributions received (0.0-1.0)."""
        if not self.assigned_agents:
            return 0.0

        return len(self.contributions) / len(self.assigned_agents)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task state."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "assigned_agents": self.assigned_agents,
            "required_agents": self.required_agents,
            "execution_time": self.get_execution_time(),
            "completion_rate": self.get_completion_rate(),
            "contributions_count": len(self.contributions),
            "result": self.result,
            "created_at": self.created_at.isoformat()
        }


class AgentSocietyManager:
    """Manages multiple societies, interactions, and emergent dynamics."""

    def __init__(self):
        self.societies: Dict[str, AgentSociety] = {}
        self.collaborative_tasks: Dict[str, CollaborativeTask] = {}
        self.agent_societies: Dict[str, List[str]] = {}  # agent_id -> [society_ids]
        self.inter_society_relations: Dict[str, Dict[str, float]] = {}  # relations between societies

    def create_society(self, society_id: str, max_members: int = 10) -> Optional[AgentSociety]:
        """Create a new society."""
        if society_id in self.societies:
            return None

        society = AgentSociety(society_id, max_members)
        self.societies[society_id] = society
        self.inter_society_relations[society_id] = {}
        return society

    def add_agent_to_society(
        self, agent_id: str, society_id: str, role: str = "contributor"
    ) -> bool:
        """Add an agent to a society."""
        if society_id not in self.societies:
            return False

        if agent_id not in self.agent_societies:
            self.agent_societies[agent_id] = []

        if society_id not in self.agent_societies[agent_id]:
            self.agent_societies[agent_id].append(society_id)

        return True

    def create_collaborative_task(
        self, task_id: str, description: str,
        society_id: str, required_agents: int,
        difficulty: float = 0.5
    ) -> Optional[CollaborativeTask]:
        """Create a collaborative task within a society."""
        if society_id not in self.societies:
            return None

        if task_id in self.collaborative_tasks:
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

    def set_society_relation(self, society_id_1: str, society_id_2: str, relation_strength: float) -> bool:
        """Set relation strength between two societies (0.0-1.0)."""
        if society_id_1 not in self.societies or society_id_2 not in self.societies:
            return False

        relation_strength = max(0.0, min(1.0, relation_strength))

        if society_id_2 not in self.inter_society_relations[society_id_1]:
            self.inter_society_relations[society_id_1][society_id_2] = relation_strength
            if society_id_1 not in self.inter_society_relations[society_id_2]:
                self.inter_society_relations[society_id_2][society_id_1] = relation_strength

        return True

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

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall health of the entire society system."""
        if not self.societies:
            return {"health_score": 0.0, "society_count": 0}

        total_health = sum(
            self.get_society_collaboration_health(sid)
            for sid in self.societies.keys()
        )

        avg_health = total_health / len(self.societies) if self.societies else 0.0

        return {
            "health_score": avg_health,
            "society_count": len(self.societies),
            "total_agents": len(self.agent_societies),
            "task_count": len(self.collaborative_tasks),
            "active_societies": sum(1 for s in self.societies.values() if s.active)
        }
