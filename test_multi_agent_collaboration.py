"""
Round 17: Multi-Agent Collaboration Framework

Enable multiple agents to collaborate, communicate, and work together
in multi-agent societies with team dynamics and shared objectives.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


class CollaborationType(Enum):
    """Types of agent collaboration"""
    PARALLEL = "parallel"  # Work on same task independently
    SEQUENTIAL = "sequential"  # Hand off work in stages
    HIERARCHICAL = "hierarchical"  # Leader-follower structure
    CONSENSUS = "consensus"  # Collective decision making


class TeamRole(Enum):
    """Roles within a team"""
    LEADER = "leader"
    SPECIALIST = "specialist"
    SUPPORT = "support"
    LEARNER = "learner"


@dataclass
class Message:
    """Inter-agent communication"""
    sender_id: str
    receiver_id: str
    content: str
    message_type: str = "info"  # info, request, offer, feedback
    priority: float = 0.5

    def to_dict(self) -> Dict:
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "message_type": self.message_type,
            "priority": self.priority
        }


@dataclass
class TeamMember:
    """An agent participating in a team"""
    agent_id: str
    role: TeamRole
    skill_level: float = 0.5  # 0.0-1.0
    contribution_score: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0

    def send_message(self) -> bool:
        """Record sending a message"""
        self.messages_sent += 1
        return True

    def receive_message(self) -> bool:
        """Record receiving a message"""
        self.messages_received += 1
        return True

    def contribute_to_task(self, amount: float = 0.1) -> bool:
        """Contribute to team task"""
        self.contribution_score = min(1.0, self.contribution_score + amount)
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "skill_level": self.skill_level,
            "contribution_score": self.contribution_score,
            "messages": {"sent": self.messages_sent, "received": self.messages_received}
        }


@dataclass
class Team:
    """A team of collaborating agents"""
    team_id: str
    members: Dict[str, TeamMember] = field(default_factory=dict)
    collaboration_type: CollaborationType = CollaborationType.PARALLEL
    team_objective: str = ""
    cohesion_score: float = 0.5  # 0.0-1.0
    shared_memory: Dict = field(default_factory=dict)

    def add_member(self, member: TeamMember) -> bool:
        """Add agent to team"""
        if member.agent_id in self.members:
            return False
        self.members[member.agent_id] = member
        return True

    def remove_member(self, agent_id: str) -> bool:
        """Remove agent from team"""
        if agent_id not in self.members:
            return False
        del self.members[agent_id]
        return True

    def get_team_size(self) -> int:
        """Get number of team members"""
        return len(self.members)

    def set_objective(self, objective: str) -> bool:
        """Set team objective"""
        self.team_objective = objective
        return True

    def update_cohesion(self, factor: float) -> bool:
        """Update team cohesion score"""
        self.cohesion_score = max(0.0, min(1.0, self.cohesion_score + factor))
        return True

    def calculate_team_contribution(self) -> float:
        """Calculate average contribution of all members"""
        if not self.members:
            return 0.0
        total = sum(m.contribution_score for m in self.members.values())
        return total / len(self.members)

    def store_shared_knowledge(self, key: str, value) -> bool:
        """Store knowledge accessible to all team members"""
        self.shared_memory[key] = value
        return True

    def to_dict(self) -> Dict:
        return {
            "team_id": self.team_id,
            "size": self.get_team_size(),
            "collaboration_type": self.collaboration_type.value,
            "objective": self.team_objective,
            "cohesion": self.cohesion_score,
            "avg_contribution": self.calculate_team_contribution(),
            "members": {k: v.to_dict() for k, v in self.members.items()}
        }


@dataclass
class Collaboration:
    """Manages a collaborative task"""
    collaboration_id: str
    team: Team
    task_description: str = ""
    status: str = "pending"  # pending, in_progress, completed
    completion_percentage: float = 0.0
    quality_score: float = 0.0

    def start_collaboration(self) -> bool:
        """Start the collaborative task"""
        if self.status != "pending":
            return False
        self.status = "in_progress"
        return True

    def update_progress(self, percentage: float) -> bool:
        """Update task completion percentage"""
        if not (0.0 <= percentage <= 1.0):
            return False
        self.completion_percentage = percentage
        if percentage >= 1.0:
            self.status = "completed"
        return True

    def evaluate_quality(self, score: float) -> bool:
        """Evaluate collaboration quality (0.0-1.0)"""
        if not (0.0 <= score <= 1.0):
            return False
        self.quality_score = score
        return True

    def to_dict(self) -> Dict:
        return {
            "collaboration_id": self.collaboration_id,
            "task": self.task_description,
            "status": self.status,
            "progress": self.completion_percentage,
            "quality": self.quality_score,
            "team": self.team.to_dict()
        }


class MultiAgentSociety:
    """Manages multiple agents and teams"""

    def __init__(self):
        self.agents: Dict[str, TeamMember] = {}
        self.teams: Dict[str, Team] = {}
        self.collaborations: Dict[str, Collaboration] = {}
        self.message_log: List[Message] = []

    def register_agent(self, agent_id: str, skill_level: float = 0.5) -> TeamMember:
        """Register an agent in the society"""
        member = TeamMember(
            agent_id=agent_id,
            role=TeamRole.LEARNER,
            skill_level=skill_level
        )
        self.agents[agent_id] = member
        return member

    def create_team(self, team_id: str, collab_type: CollaborationType = CollaborationType.PARALLEL) -> Team:
        """Create a new team"""
        team = Team(team_id=team_id, collaboration_type=collab_type)
        self.teams[team_id] = team
        return team

    def form_team(self, team_id: str, agent_ids: List[str], roles: Dict[str, TeamRole]) -> bool:
        """Form a team with specific agents and roles"""
        if team_id not in self.teams:
            return False
        team = self.teams[team_id]
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                return False
            member = self.agents[agent_id]
            member.role = roles.get(agent_id, TeamRole.LEARNER)
            if not team.add_member(member):
                return False
        return True

    def send_message(self, sender_id: str, receiver_id: str, content: str, msg_type: str = "info") -> bool:
        """Send message between agents"""
        if sender_id not in self.agents or receiver_id not in self.agents:
            return False
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=msg_type
        )
        self.agents[sender_id].send_message()
        self.agents[receiver_id].receive_message()
        self.message_log.append(message)
        return True

    def create_collaboration(self, collab_id: str, team_id: str, task: str) -> Optional[Collaboration]:
        """Create a collaborative task for a team"""
        if team_id not in self.teams:
            return None
        team = self.teams[team_id]
        collab = Collaboration(
            collaboration_id=collab_id,
            team=team,
            task_description=task
        )
        self.collaborations[collab_id] = collab
        return collab

    def get_society_health(self) -> Dict:
        """Get overall society health metrics"""
        if not self.agents:
            return {"health_score": 0.0}
        avg_contribution = sum(a.contribution_score for a in self.agents.values()) / len(self.agents)
        avg_cohesion = sum(t.cohesion_score for t in self.teams.values()) / max(1, len(self.teams))
        health_score = (avg_contribution * 0.6) + (avg_cohesion * 0.4)
        return {
            "health_score": health_score,
            "total_agents": len(self.agents),
            "total_teams": len(self.teams),
            "total_collaborations": len(self.collaborations),
            "total_messages": len(self.message_log)
        }


# ===== Tests =====

def test_message_creation():
    """Test message creation"""
    msg = Message(
        sender_id="agent_001",
        receiver_id="agent_002",
        content="Let's work together"
    )
    assert msg.sender_id == "agent_001"
    assert msg.receiver_id == "agent_002"


def test_team_member_creation():
    """Test team member creation"""
    member = TeamMember(
        agent_id="agent_001",
        role=TeamRole.SPECIALIST,
        skill_level=0.8
    )
    assert member.agent_id == "agent_001"
    assert member.skill_level == 0.8


def test_team_member_message_tracking():
    """Test tracking member messages"""
    member = TeamMember(agent_id="agent_001", role=TeamRole.LEADER)
    assert member.send_message() is True
    assert member.messages_sent == 1
    assert member.receive_message() is True
    assert member.messages_received == 1


def test_team_member_contribution():
    """Test member contribution tracking"""
    member = TeamMember(agent_id="agent_001", role=TeamRole.SUPPORT)
    assert member.contribute_to_task(0.2) is True
    assert member.contribution_score == 0.2
    assert member.contribute_to_task(0.3) is True
    assert member.contribution_score == 0.5


def test_team_creation():
    """Test team creation"""
    team = Team(
        team_id="team_001",
        collaboration_type=CollaborationType.PARALLEL
    )
    assert team.team_id == "team_001"
    assert team.get_team_size() == 0


def test_team_add_remove_members():
    """Test adding and removing members"""
    team = Team(team_id="team_001")
    member = TeamMember(agent_id="agent_001", role=TeamRole.LEADER)
    assert team.add_member(member) is True
    assert team.get_team_size() == 1
    assert team.remove_member("agent_001") is True
    assert team.get_team_size() == 0


def test_team_objective():
    """Test setting team objective"""
    team = Team(team_id="team_001")
    assert team.set_objective("Solve puzzle together") is True
    assert team.team_objective == "Solve puzzle together"


def test_team_cohesion():
    """Test team cohesion tracking"""
    team = Team(team_id="team_001", cohesion_score=0.5)
    assert team.update_cohesion(0.1) is True
    assert team.cohesion_score == 0.6
    assert team.update_cohesion(0.5) is True
    assert team.cohesion_score == 1.0


def test_team_shared_memory():
    """Test shared team memory"""
    team = Team(team_id="team_001")
    assert team.store_shared_knowledge("strategy", "divide_and_conquer") is True
    assert team.shared_memory["strategy"] == "divide_and_conquer"


def test_team_contribution_calculation():
    """Test calculating team contribution"""
    team = Team(team_id="team_001")
    for i in range(3):
        member = TeamMember(agent_id=f"agent_{i:03d}", role=TeamRole.SPECIALIST)
        member.contribution_score = 0.6
        team.add_member(member)
    assert team.calculate_team_contribution() == 0.6


def test_collaboration_creation():
    """Test collaboration creation"""
    team = Team(team_id="team_001")
    collab = Collaboration(
        collaboration_id="collab_001",
        team=team,
        task_description="Build a solution"
    )
    assert collab.status == "pending"


def test_collaboration_workflow():
    """Test collaboration workflow"""
    team = Team(team_id="team_001")
    collab = Collaboration(collaboration_id="collab_001", team=team)
    
    assert collab.start_collaboration() is True
    assert collab.status == "in_progress"
    
    assert collab.update_progress(0.5) is True
    assert collab.completion_percentage == 0.5
    
    assert collab.evaluate_quality(0.85) is True
    assert collab.quality_score == 0.85
    
    assert collab.update_progress(1.0) is True
    assert collab.status == "completed"


def test_multi_agent_society_creation():
    """Test society creation"""
    society = MultiAgentSociety()
    assert len(society.agents) == 0


def test_agent_registration():
    """Test registering agents"""
    society = MultiAgentSociety()
    agent = society.register_agent("agent_001", skill_level=0.7)
    assert "agent_001" in society.agents
    assert agent.skill_level == 0.7


def test_team_creation_and_formation():
    """Test creating and forming teams"""
    society = MultiAgentSociety()
    society.register_agent("agent_001")
    society.register_agent("agent_002")
    
    team = society.create_team("team_001")
    assert "team_001" in society.teams
    
    roles = {"agent_001": TeamRole.LEADER, "agent_002": TeamRole.SPECIALIST}
    assert society.form_team("team_001", ["agent_001", "agent_002"], roles) is True
    assert team.get_team_size() == 2


def test_inter_agent_messaging():
    """Test messaging between agents"""
    society = MultiAgentSociety()
    society.register_agent("agent_001")
    society.register_agent("agent_002")
    
    assert society.send_message("agent_001", "agent_002", "Hello!", "info") is True
    assert len(society.message_log) == 1
    assert society.agents["agent_001"].messages_sent == 1
    assert society.agents["agent_002"].messages_received == 1


def test_collaboration_task_creation():
    """Test creating collaboration tasks"""
    society = MultiAgentSociety()
    society.register_agent("agent_001")
    society.register_agent("agent_002")
    team = society.create_team("team_001")
    society.form_team("team_001", ["agent_001", "agent_002"], {})
    
    collab = society.create_collaboration("collab_001", "team_001", "Write report")
    assert collab is not None
    assert collab.task_description == "Write report"


def test_society_health_metrics():
    """Test calculating society health"""
    society = MultiAgentSociety()
    society.register_agent("agent_001")
    society.register_agent("agent_002")
    
    health = society.get_society_health()
    assert "health_score" in health
    assert health["total_agents"] == 2


def test_complex_collaboration_workflow():
    """Test complete collaboration workflow"""
    society = MultiAgentSociety()
    
    # Register agents
    agents = [society.register_agent(f"agent_{i:03d}", skill_level=0.5 + i*0.1) for i in range(3)]
    
    # Create team
    team = society.create_team("team_001", CollaborationType.HIERARCHICAL)
    roles = {
        "agent_000": TeamRole.LEADER,
        "agent_001": TeamRole.SPECIALIST,
        "agent_002": TeamRole.SUPPORT
    }
    society.form_team("team_001", list(roles.keys()), roles)
    
    # Create collaboration
    collab = society.create_collaboration("collab_001", "team_001", "Complex task")
    collab.start_collaboration()
    
    # Simulate team work
    team.update_cohesion(0.1)
    team.store_shared_knowledge("progress", "50%")
    
    for member in team.members.values():
        member.contribute_to_task(0.1)
    
    # Complete collaboration
    collab.update_progress(1.0)
    collab.evaluate_quality(0.9)
    
    # Verify results
    health = society.get_society_health()
    assert health["total_agents"] == 3
    assert health["total_teams"] == 1
    assert health["total_collaborations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
