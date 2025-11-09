"""
Round 27: Multi-Agent Societies System

Enable multiple agents to form collaborative societies with governance structures,
social hierarchies, and collective decision-making. Agents develop relationships,
negotiate resources, and work toward shared goals.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


class GovernanceType(Enum):
    """Types of governance structures for societies"""
    FLAT = "flat"  # All agents equal
    HIERARCHICAL = "hierarchical"  # Clear leadership chain
    CONSENSUS = "consensus"  # Votes on decisions
    MERITOCRATIC = "meritocratic"  # Power based on skill/contribution
    COOPERATIVE = "cooperative"  # Collective ownership


class SocialRole(Enum):
    """Social roles agents can hold in society"""
    LEADER = "leader"  # Decision maker
    SPECIALIST = "specialist"  # Expert in specific domain
    SUPPORT = "support"  # Helper role
    SCOUT = "scout"  # Explorer/information gatherer
    DIPLOMAT = "diplomat"  # Mediator between groups
    ELDER = "elder"  # Experienced guide
    LEARNER = "learner"  # Growing/developing agent


class RelationshipStatus(Enum):
    """Status of relationships between agents"""
    NEUTRAL = "neutral"
    ALLY = "ally"
    RIVAL = "rival"
    TEAMMATE = "teammate"
    MENTOR_MENTEE = "mentor_mentee"


@dataclass
class SocialRelationship:
    """Relationship between two agents"""
    agent_a_id: str
    agent_b_id: str
    status: RelationshipStatus = RelationshipStatus.NEUTRAL
    trust: float = 0.5  # 0.0-1.0
    cooperation_level: float = 0.5  # 0.0-1.0 how well they work together
    shared_goals: int = 0  # Number of goals they're working toward together
    conflicts: int = 0  # Number of conflicts that arose

    def increase_trust(self, amount: float = 0.1) -> bool:
        """Increase trust between agents"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.trust = min(1.0, self.trust + amount)
        return True

    def decrease_trust(self, amount: float = 0.1) -> bool:
        """Decrease trust between agents"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.trust = max(0.0, self.trust - amount)
        return True

    def set_status(self, status: RelationshipStatus) -> bool:
        """Update relationship status"""
        self.status = status
        # Automatically adjust cooperation based on status
        status_cooperation = {
            RelationshipStatus.NEUTRAL: 0.5,
            RelationshipStatus.ALLY: 0.8,
            RelationshipStatus.RIVAL: 0.3,
            RelationshipStatus.TEAMMATE: 0.9,
            RelationshipStatus.MENTOR_MENTEE: 0.7,
        }
        self.cooperation_level = status_cooperation.get(status, 0.5)
        return True

    def add_shared_goal(self) -> bool:
        """Record agents working on goal together"""
        self.shared_goals += 1
        return True

    def record_conflict(self) -> bool:
        """Record conflict between agents"""
        self.conflicts += 1
        # Conflicts reduce cooperation
        self.cooperation_level = max(0.1, self.cooperation_level - 0.05)
        return True

    def get_health(self) -> float:
        """Overall relationship health (0.0-1.0)"""
        # Average of trust and cooperation
        return (self.trust + self.cooperation_level) / 2.0

    def to_dict(self) -> Dict:
        return {
            "agent_a_id": self.agent_a_id,
            "agent_b_id": self.agent_b_id,
            "status": self.status.value,
            "trust": self.trust,
            "cooperation_level": self.cooperation_level,
            "shared_goals": self.shared_goals,
            "conflicts": self.conflicts
        }


@dataclass
class SocietyMember:
    """An agent as member of society"""
    agent_id: str
    role: SocialRole = SocialRole.LEARNER
    contribution_score: float = 0.0  # 0.0-1.0, amount of work done
    reputation: float = 0.5  # 0.0-1.0, what others think
    joined_at: int = 0  # Turn/time joined

    def change_role(self, new_role: SocialRole) -> bool:
        """Change agent's social role"""
        self.role = new_role
        return True

    def increase_contribution(self, amount: float = 0.1) -> bool:
        """Record agent contribution"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.contribution_score = min(1.0, self.contribution_score + amount)
        return True

    def update_reputation(self, amount: float) -> bool:
        """Update agent reputation"""
        if not (-0.5 <= amount <= 0.5):
            return False
        self.reputation = max(0.0, min(1.0, self.reputation + amount))
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "contribution_score": self.contribution_score,
            "reputation": self.reputation
        }


@dataclass
class CollectiveGoal:
    """A goal the society works toward together"""
    goal_id: str
    description: str
    priority: int = 1  # 1-10
    contributors: Set[str] = field(default_factory=set)  # Agent IDs working on it
    progress: float = 0.0  # 0.0-1.0
    deadline: Optional[int] = None  # Turn limit
    reward_pool: float = 0.0  # Shared reward when complete

    def add_contributor(self, agent_id: str) -> bool:
        """Add agent working on goal"""
        if agent_id in self.contributors:
            return False
        self.contributors.add(agent_id)
        return True

    def advance_progress(self, amount: float = 0.1) -> bool:
        """Advance goal progress"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.progress = min(1.0, self.progress + amount)
        return True

    def is_complete(self) -> bool:
        """Check if goal is complete"""
        return self.progress >= 1.0

    def to_dict(self) -> Dict:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "progress": self.progress,
            "contributors": len(self.contributors),
            "is_complete": self.is_complete()
        }


class Society:
    """A society of collaborating agents"""

    def __init__(self, society_id: str, governance: GovernanceType = GovernanceType.FLAT):
        self.society_id = society_id
        self.governance = governance
        self.members: Dict[str, SocietyMember] = {}
        self.relationships: List[SocialRelationship] = []
        self.collective_goals: Dict[str, CollectiveGoal] = {}
        self.leader_id: Optional[str] = None
        self.treasury: float = 0.0  # Shared resources
        self.age: int = 0  # Turns existed

    def add_member(self, agent: SocietyMember) -> bool:
        """Add agent to society"""
        if agent.agent_id in self.members:
            return False
        agent.joined_at = self.age
        self.members[agent.agent_id] = agent

        # If first member in hierarchical society, make them leader
        if self.governance == GovernanceType.HIERARCHICAL and self.leader_id is None:
            self.leader_id = agent.agent_id
            agent.role = SocialRole.LEADER

        return True

    def create_relationship(self, agent_a_id: str, agent_b_id: str) -> Optional[SocialRelationship]:
        """Create or get relationship between two agents"""
        if agent_a_id not in self.members or agent_b_id not in self.members:
            return None

        # Check if relationship exists
        for rel in self.relationships:
            if (rel.agent_a_id == agent_a_id and rel.agent_b_id == agent_b_id) or \
               (rel.agent_a_id == agent_b_id and rel.agent_b_id == agent_a_id):
                return rel

        # Create new relationship
        relationship = SocialRelationship(agent_a_id, agent_b_id)
        self.relationships.append(relationship)
        return relationship

    def get_relationship(self, agent_a_id: str, agent_b_id: str) -> Optional[SocialRelationship]:
        """Get relationship between two agents"""
        for rel in self.relationships:
            if (rel.agent_a_id == agent_a_id and rel.agent_b_id == agent_b_id) or \
               (rel.agent_a_id == agent_b_id and rel.agent_b_id == agent_a_id):
                return rel
        return None

    def create_collective_goal(self, goal: CollectiveGoal) -> bool:
        """Create a collective goal for the society"""
        if goal.goal_id in self.collective_goals:
            return False
        self.collective_goals[goal.goal_id] = goal
        return True

    def add_contributor_to_goal(self, goal_id: str, agent_id: str) -> bool:
        """Add agent as contributor to goal"""
        if goal_id not in self.collective_goals:
            return False
        if agent_id not in self.members:
            return False

        goal = self.collective_goals[goal_id]
        if goal.add_contributor(agent_id):
            # Record shared goal in relationship
            rel = self.create_relationship(agent_id, next(iter(goal.contributors)) if goal.contributors else agent_id)
            if rel:
                rel.add_shared_goal()
            return True
        return False

    def contribute_to_treasury(self, agent_id: str, amount: float) -> bool:
        """Agent contributes resources to shared treasury"""
        if agent_id not in self.members:
            return False
        if amount < 0:
            return False

        self.treasury += amount
        self.members[agent_id].increase_contribution(min(1.0, amount / 10.0))
        return True

    def distribute_from_treasury(self, agent_id: str, amount: float) -> bool:
        """Distribute from treasury to agent"""
        if agent_id not in self.members or amount > self.treasury:
            return False

        self.treasury -= amount
        return True

    def change_agent_role(self, agent_id: str, new_role: SocialRole) -> bool:
        """Change agent's role in society"""
        if agent_id not in self.members:
            return False

        self.members[agent_id].change_role(new_role)

        # If hierarchical, only leader can be leader
        if self.governance == GovernanceType.HIERARCHICAL and new_role == SocialRole.LEADER:
            self.leader_id = agent_id

        return True

    def resolve_conflict(self, agent_a_id: str, agent_b_id: str) -> bool:
        """Attempt to resolve conflict between agents"""
        rel = self.get_relationship(agent_a_id, agent_b_id)
        if not rel:
            return False

        # Conflict resolution depends on governance type
        if self.governance == GovernanceType.CONSENSUS:
            # Consensus reduces conflict impact
            rel.conflicts = max(0, rel.conflicts - 1)
        elif self.governance == GovernanceType.COOPERATIVE:
            # Cooperative increases trust
            rel.increase_trust(0.1)

        return True

    def advance_time(self) -> None:
        """Advance society by one turn"""
        self.age += 1

    def get_society_health(self) -> Dict:
        """Get overall health metrics for society"""
        if not self.members:
            return {"members": 0}

        avg_reputation = sum(m.reputation for m in self.members.values()) / len(self.members)
        avg_contribution = sum(m.contribution_score for m in self.members.values()) / len(self.members)

        relationships_count = len(self.relationships)
        avg_trust = (
            sum(r.trust for r in self.relationships) / relationships_count
            if relationships_count > 0
            else 0.5
        )

        completed_goals = sum(1 for g in self.collective_goals.values() if g.is_complete())

        return {
            "members": len(self.members),
            "avg_reputation": avg_reputation,
            "avg_contribution": avg_contribution,
            "avg_trust": avg_trust,
            "treasury": self.treasury,
            "collective_goals_completed": completed_goals,
            "total_goals": len(self.collective_goals),
            "age": self.age
        }

    def get_social_graph(self) -> Dict:
        """Get network of relationships"""
        return {
            "members": [m.agent_id for m in self.members.values()],
            "relationships": len(self.relationships),
            "avg_trust": sum(r.trust for r in self.relationships) / max(1, len(self.relationships))
        }

    def to_dict(self) -> Dict:
        return {
            "society_id": self.society_id,
            "governance": self.governance.value,
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "goals": {k: v.to_dict() for k, v in self.collective_goals.items()},
            "health": self.get_society_health()
        }


# ===== Tests =====

def test_society_creation():
    """Test creating a society"""
    society = Society(society_id="soc1", governance=GovernanceType.FLAT)
    assert society.society_id == "soc1"
    assert society.governance == GovernanceType.FLAT


def test_add_member_to_society():
    """Test adding agent to society"""
    society = Society(society_id="soc1")
    member = SocietyMember(agent_id="a1")
    assert society.add_member(member) is True
    assert "a1" in society.members


def test_hierarchical_leadership():
    """Test leadership in hierarchical society"""
    society = Society(society_id="soc1", governance=GovernanceType.HIERARCHICAL)
    leader = SocietyMember(agent_id="leader1")
    society.add_member(leader)
    assert society.leader_id == "leader1"
    assert society.members["leader1"].role == SocialRole.LEADER


def test_create_relationship():
    """Test creating relationship between agents"""
    society = Society(society_id="soc1")
    m1 = SocietyMember(agent_id="a1")
    m2 = SocietyMember(agent_id="a2")
    society.add_member(m1)
    society.add_member(m2)

    rel = society.create_relationship("a1", "a2")
    assert rel is not None
    assert rel.status == RelationshipStatus.NEUTRAL


def test_relationship_trust():
    """Test trust changes in relationships"""
    rel = SocialRelationship("a1", "a2")
    assert rel.increase_trust(0.2) is True
    assert abs(rel.trust - 0.7) < 0.0001

    assert rel.decrease_trust(0.3) is True
    assert abs(rel.trust - 0.4) < 0.0001


def test_relationship_status_change():
    """Test changing relationship status"""
    rel = SocialRelationship("a1", "a2")
    assert rel.set_status(RelationshipStatus.ALLY) is True
    assert rel.status == RelationshipStatus.ALLY
    assert rel.cooperation_level == 0.8


def test_collective_goal():
    """Test collective goal creation"""
    goal = CollectiveGoal(goal_id="g1", description="Build something together")
    assert goal.progress == 0.0
    assert goal.is_complete() is False


def test_goal_progress():
    """Test advancing goal progress"""
    goal = CollectiveGoal(goal_id="g1", description="Task")
    assert goal.advance_progress(0.5) is True
    assert goal.advance_progress(0.5) is True
    assert goal.is_complete() is True


def test_add_goal_to_society():
    """Test adding collective goal to society"""
    society = Society(society_id="soc1")
    goal = CollectiveGoal(goal_id="g1", description="Build")
    assert society.create_collective_goal(goal) is True


def test_contributor_to_goal():
    """Test adding contributor to goal"""
    society = Society(society_id="soc1")
    m1 = SocietyMember(agent_id="a1")
    m2 = SocietyMember(agent_id="a2")
    society.add_member(m1)
    society.add_member(m2)

    goal = CollectiveGoal(goal_id="g1", description="Build")
    society.create_collective_goal(goal)
    assert society.add_contributor_to_goal("g1", "a1") is True


def test_society_treasury():
    """Test shared treasury system"""
    society = Society(society_id="soc1")
    member = SocietyMember(agent_id="a1")
    society.add_member(member)

    assert society.contribute_to_treasury("a1", 50.0) is True
    assert society.treasury == 50.0


def test_change_agent_role():
    """Test changing agent role"""
    society = Society(society_id="soc1")
    member = SocietyMember(agent_id="a1", role=SocialRole.LEARNER)
    society.add_member(member)

    assert society.change_agent_role("a1", SocialRole.SPECIALIST) is True
    assert society.members["a1"].role == SocialRole.SPECIALIST


def test_conflict_resolution():
    """Test conflict resolution in society"""
    society = Society(society_id="soc1", governance=GovernanceType.CONSENSUS)
    m1 = SocietyMember(agent_id="a1")
    m2 = SocietyMember(agent_id="a2")
    society.add_member(m1)
    society.add_member(m2)

    rel = society.create_relationship("a1", "a2")
    rel.record_conflict()
    assert rel.conflicts == 1

    assert society.resolve_conflict("a1", "a2") is True


def test_society_health():
    """Test calculating society health"""
    society = Society(society_id="soc1")
    m1 = SocietyMember(agent_id="a1", reputation=0.8)
    m2 = SocietyMember(agent_id="a2", reputation=0.6)
    society.add_member(m1)
    society.add_member(m2)

    health = society.get_society_health()
    assert "avg_reputation" in health
    assert health["members"] == 2


def test_social_graph():
    """Test getting social network graph"""
    society = Society(society_id="soc1")
    m1 = SocietyMember(agent_id="a1")
    m2 = SocietyMember(agent_id="a2")
    society.add_member(m1)
    society.add_member(m2)
    society.create_relationship("a1", "a2")

    graph = society.get_social_graph()
    assert len(graph["members"]) == 2
    assert graph["relationships"] == 1


def test_complete_society_workflow():
    """Test complete workflow: society formation, goals, collaboration"""
    # Create society
    society = Society(society_id="minecraft_village", governance=GovernanceType.MERITOCRATIC)

    # Add members
    builder = SocietyMember(agent_id="builder_1", role=SocialRole.SPECIALIST)
    explorer = SocietyMember(agent_id="explorer_1", role=SocialRole.SCOUT)
    farmer = SocietyMember(agent_id="farmer_1", role=SocialRole.SPECIALIST)

    assert society.add_member(builder) is True
    assert society.add_member(explorer) is True
    assert society.add_member(farmer) is True

    # Create relationships
    society.create_relationship("builder_1", "explorer_1")
    society.create_relationship("explorer_1", "farmer_1")
    society.create_relationship("builder_1", "farmer_1")

    # Create collective goal
    goal = CollectiveGoal(goal_id="harvest_food", description="Gather food for winter", priority=10)
    assert society.create_collective_goal(goal) is True

    # Add contributors
    assert society.add_contributor_to_goal("harvest_food", "farmer_1") is True
    assert society.add_contributor_to_goal("harvest_food", "builder_1") is True

    # Advance goal
    goal.advance_progress(0.3)
    goal.advance_progress(0.4)
    goal.advance_progress(0.3)
    assert goal.is_complete() is True

    # Check society health
    health = society.get_society_health()
    assert health["members"] == 3
    assert health["collective_goals_completed"] == 1

    # Advance time
    society.advance_time()
    assert society.age == 1


def test_governance_types():
    """Test different governance structures affect conflict resolution"""
    # Flat governance
    flat = Society(society_id="flat", governance=GovernanceType.FLAT)
    m1 = SocietyMember(agent_id="a1")
    m2 = SocietyMember(agent_id="a2")
    flat.add_member(m1)
    flat.add_member(m2)
    flat.create_relationship("a1", "a2")

    # Consensus governance
    consensus = Society(society_id="consensus", governance=GovernanceType.CONSENSUS)
    m3 = SocietyMember(agent_id="a3")
    m4 = SocietyMember(agent_id="a4")
    consensus.add_member(m3)
    consensus.add_member(m4)
    rel = consensus.create_relationship("a3", "a4")
    rel.record_conflict()
    assert consensus.resolve_conflict("a3", "a4") is True
    assert rel.conflicts == 0  # Consensus reduced it


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
