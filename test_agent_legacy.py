"""
Round 26: Agent Legacy & Inheritance System

Enable agents to become mentors and pass down knowledge to successor agents.
Create lineage trees where agents can inherit capabilities and memories
from their predecessors, forming a chain of intelligent development.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class LegacyType(Enum):
    """Types of knowledge/capabilities that can be inherited"""
    SKILL = "skill"  # Direct skill transfer
    MEMORY = "memory"  # Experience/episodic memory
    PERSONALITY = "personality"  # Traits and quirks
    TECHNIQUE = "technique"  # Learned problem-solving approaches
    WISDOM = "wisdom"  # Abstract insights


class GenerationStatus(Enum):
    """Status of an agent in generational chain"""
    FOUNDER = "founder"  # First generation
    SUCCESSOR = "successor"  # Inherits from predecessor
    MENTOR = "mentor"  # Can mentor next generation
    RETIRED = "retired"  # No longer active
    LEGENDARY = "legendary"  # Historic figure in lineage


@dataclass
class Lineage:
    """Tracks agent family tree"""
    agent_id: str
    generation: int = 0  # 0=founder, 1=first successor, etc.
    predecessor_id: Optional[str] = None
    successors: List[str] = field(default_factory=list)
    status: GenerationStatus = GenerationStatus.FOUNDER
    founding_age: int = 0  # When created
    retirement_age: Optional[int] = None

    def add_successor(self, successor_id: str) -> bool:
        """Register a successor agent"""
        if successor_id in self.successors:
            return False
        self.successors.append(successor_id)
        if self.status in [GenerationStatus.FOUNDER, GenerationStatus.SUCCESSOR]:
            self.status = GenerationStatus.MENTOR
        return True

    def retire(self, age: int) -> bool:
        """Retire this agent from active development"""
        if self.status == GenerationStatus.RETIRED:
            return False
        self.status = GenerationStatus.RETIRED
        self.retirement_age = age
        return True

    def mark_legendary(self) -> bool:
        """Mark agent as legendary (historically significant)"""
        if len(self.successors) >= 3:  # Must have raised multiple successors
            self.status = GenerationStatus.LEGENDARY
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "generation": self.generation,
            "status": self.status.value,
            "successors_count": len(self.successors)
        }


@dataclass
class InheritedCapability:
    """A capability passed down through generations"""
    capability_id: str
    legacy_type: LegacyType
    name: str
    strength: float = 0.5  # 0.0-1.0, inherited strength
    origin_agent: str = ""  # Original creator
    generations_old: int = 0  # How many generations back it originated
    uses: int = 0  # Times used by current holder

    def use_capability(self) -> bool:
        """Use this inherited capability"""
        self.uses += 1
        return True

    def enhance(self, amount: float = 0.1) -> bool:
        """Enhance inherited capability through use"""
        if self.strength >= 1.0:
            return False
        self.strength = min(1.0, self.strength + amount)
        return True

    def to_dict(self) -> Dict:
        return {
            "capability_id": self.capability_id,
            "legacy_type": self.legacy_type.value,
            "name": self.name,
            "strength": self.strength,
            "generations_old": self.generations_old,
            "uses": self.uses
        }


@dataclass
class SuccessorAgent:
    """A new agent created as successor to existing agent"""
    agent_id: str
    predecessor_id: str
    creation_time: int = 0  # When created
    inherited_capabilities: Dict[str, InheritedCapability] = field(default_factory=dict)
    original_capabilities: Dict[str, str] = field(default_factory=dict)  # New capabilities learned
    capability_fusion_score: float = 0.0  # 0.0-1.0, how well inherited+new blend
    mentor_satisfaction: float = 0.5  # 0.0-1.0, predecessor's rating of successor

    def gain_inherited_capability(self, capability: InheritedCapability) -> bool:
        """Inherit a capability from predecessor"""
        if capability.capability_id in self.inherited_capabilities:
            return False
        # Reduce strength slightly when inheriting (lossy transmission)
        capability.strength = max(0.3, capability.strength * 0.8)
        capability.generations_old += 1
        self.inherited_capabilities[capability.capability_id] = capability
        return True

    def learn_original_capability(self, capability_id: str, name: str) -> bool:
        """Learn a new capability not from predecessor"""
        if capability_id in self.original_capabilities:
            return False
        self.original_capabilities[capability_id] = name
        return True

    def update_fusion_score(self) -> float:
        """Calculate how well inherited and original capabilities blend"""
        if not self.inherited_capabilities and not self.original_capabilities:
            return 0.0

        total_inherited_strength = sum(
            c.strength for c in self.inherited_capabilities.values()
        )
        inherited_avg = (
            total_inherited_strength / len(self.inherited_capabilities)
            if self.inherited_capabilities
            else 0.0
        )
        original_count = len(self.original_capabilities)

        # Good balance = inherited used as foundation, then enhanced with new
        balance = original_count / max(1, len(self.inherited_capabilities) + original_count)
        self.capability_fusion_score = (inherited_avg * 0.6) + (balance * 0.4)
        return self.capability_fusion_score

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "predecessor_id": self.predecessor_id,
            "inherited_count": len(self.inherited_capabilities),
            "original_count": len(self.original_capabilities),
            "fusion_score": self.capability_fusion_score
        }


class LegacySystem:
    """Manage agent lineages, inheritance, and knowledge transmission"""

    def __init__(self):
        self.lineages: Dict[str, Lineage] = {}
        self.agents: Dict[str, SuccessorAgent] = {}
        self.knowledge_vault: Dict[str, InheritedCapability] = {}
        self.legendary_agents: Set[str] = set()
        self.total_generations_created: int = 0

    def register_founder(self, agent_id: str) -> bool:
        """Register a founder agent (generation 0)"""
        if agent_id in self.lineages:
            return False
        lineage = Lineage(agent_id=agent_id, generation=0, status=GenerationStatus.FOUNDER)
        self.lineages[agent_id] = lineage
        return True

    def create_successor(self, predecessor_id: str, successor_id: str) -> Optional[SuccessorAgent]:
        """Create a successor agent from a predecessor"""
        if predecessor_id not in self.lineages:
            return None

        predecessor_lineage = self.lineages[predecessor_id]

        # Create successor
        successor_agent = SuccessorAgent(
            agent_id=successor_id,
            predecessor_id=predecessor_id,
            creation_time=self.total_generations_created
        )

        # Register successor lineage
        successor_lineage = Lineage(
            agent_id=successor_id,
            generation=predecessor_lineage.generation + 1,
            predecessor_id=predecessor_id,
            status=GenerationStatus.SUCCESSOR
        )

        # Update predecessor
        predecessor_lineage.add_successor(successor_id)

        # Store both
        self.agents[successor_id] = successor_agent
        self.lineages[successor_id] = successor_lineage
        self.total_generations_created += 1

        return successor_agent

    def transfer_capability(
        self, predecessor_id: str, successor_id: str, capability: InheritedCapability
    ) -> bool:
        """Transfer a capability from predecessor to successor"""
        if (
            predecessor_id not in self.lineages
            or successor_id not in self.agents
            or self.agents[successor_id].predecessor_id != predecessor_id
        ):
            return False

        successor = self.agents[successor_id]
        return successor.gain_inherited_capability(capability)

    def teach_successor(self, predecessor_id: str, successor_id: str) -> bool:
        """Predecessor teaches successor multiple capabilities"""
        if predecessor_id not in self.lineages or successor_id not in self.agents:
            return False

        successor = self.agents[successor_id]

        # Create teaching event - transfer generic capabilities
        base_capability = InheritedCapability(
            capability_id=f"legacy_{predecessor_id}_{successor_id}",
            legacy_type=LegacyType.WISDOM,
            name=f"Wisdom from {predecessor_id}",
            strength=0.7,
            origin_agent=predecessor_id
        )

        return self.transfer_capability(predecessor_id, successor_id, base_capability)

    def successor_innovates(self, successor_id: str, new_capability_id: str, name: str) -> bool:
        """Successor creates a new capability unique to them"""
        if successor_id not in self.agents:
            return False

        successor = self.agents[successor_id]
        return successor.learn_original_capability(new_capability_id, name)

    def get_lineage_health(self, agent_id: str) -> Dict:
        """Get metrics about an agent's lineage"""
        if agent_id not in self.lineages:
            return {}

        lineage = self.lineages[agent_id]
        agent_data = self.agents.get(agent_id)

        health = {
            "generation": lineage.generation,
            "status": lineage.status.value,
            "successors_raised": len(lineage.successors),
        }

        if agent_data:
            health["inherited_capabilities"] = len(agent_data.inherited_capabilities)
            health["original_capabilities"] = len(agent_data.original_capabilities)
            health["fusion_score"] = agent_data.update_fusion_score()

        return health

    def get_lineage_tree(self, founder_id: str) -> Dict:
        """Get complete family tree for a founder and descendants"""
        if founder_id not in self.lineages:
            return {}

        def build_tree(agent_id: str) -> Dict:
            lineage = self.lineages[agent_id]
            node = {
                "agent_id": agent_id,
                "generation": lineage.generation,
                "status": lineage.status.value,
                "children": []
            }

            for successor_id in lineage.successors:
                node["children"].append(build_tree(successor_id))

            return node

        return build_tree(founder_id)

    def promote_to_legendary(self, agent_id: str) -> bool:
        """Attempt to promote agent to legendary status"""
        if agent_id not in self.lineages:
            return False

        lineage = self.lineages[agent_id]
        if lineage.mark_legendary():
            self.legendary_agents.add(agent_id)
            return True
        return False

    def get_system_statistics(self) -> Dict:
        """Get overall system legacy statistics"""
        return {
            "total_lineages": len(self.lineages),
            "total_successors": len(self.agents),
            "generations_created": self.total_generations_created,
            "legendary_agents": len(self.legendary_agents),
            "avg_generation": (
                sum(l.generation for l in self.lineages.values()) / max(1, len(self.lineages))
            ),
        }


# ===== Tests =====

def test_lineage_creation():
    """Test creating founder lineage"""
    lineage = Lineage(agent_id="founder_1")
    assert lineage.generation == 0
    assert lineage.status == GenerationStatus.FOUNDER


def test_successor_lineage():
    """Test creating successor in lineage"""
    founder = Lineage(agent_id="founder_1", generation=0)
    successor = Lineage(agent_id="successor_1", generation=1, predecessor_id="founder_1")
    assert successor.generation == 1
    assert successor.predecessor_id == "founder_1"


def test_inherited_capability():
    """Test inherited capability"""
    capability = InheritedCapability(
        capability_id="cap1",
        legacy_type=LegacyType.SKILL,
        name="Problem Solving",
        strength=0.8
    )
    assert capability.strength == 0.8


def test_capability_enhancement():
    """Test enhancing inherited capability"""
    capability = InheritedCapability(
        capability_id="cap1",
        legacy_type=LegacyType.TECHNIQUE,
        name="Strategy",
        strength=0.5
    )
    assert capability.enhance(0.2) is True
    assert capability.strength == 0.7


def test_successor_agent_creation():
    """Test creating successor agent"""
    successor = SuccessorAgent(agent_id="succ1", predecessor_id="founder1")
    assert successor.predecessor_id == "founder1"
    assert len(successor.inherited_capabilities) == 0


def test_successor_inherits_capability():
    """Test successor inheriting capability"""
    successor = SuccessorAgent(agent_id="succ1", predecessor_id="founder1")
    capability = InheritedCapability(
        capability_id="cap1",
        legacy_type=LegacyType.SKILL,
        name="Logic",
        strength=0.8,
        origin_agent="founder1"
    )

    assert successor.gain_inherited_capability(capability) is True
    assert len(successor.inherited_capabilities) == 1
    assert successor.inherited_capabilities["cap1"].strength < 0.8  # Reduced by inheritance


def test_successor_learns_original():
    """Test successor learning new capability"""
    successor = SuccessorAgent(agent_id="succ1", predecessor_id="founder1")
    assert successor.learn_original_capability("new_cap1", "Innovation") is True
    assert len(successor.original_capabilities) == 1


def test_fusion_score_calculation():
    """Test capability fusion score"""
    successor = SuccessorAgent(agent_id="succ1", predecessor_id="founder1")

    # Add inherited
    cap1 = InheritedCapability(
        capability_id="cap1",
        legacy_type=LegacyType.SKILL,
        name="Skill1",
        strength=0.8,
        origin_agent="founder1"
    )
    successor.gain_inherited_capability(cap1)

    # Add original
    successor.learn_original_capability("new_cap1", "NewSkill")

    fusion = successor.update_fusion_score()
    assert 0.0 <= fusion <= 1.0


def test_lineage_mentor_status():
    """Test lineage becomes mentor after raising successor"""
    founder = Lineage(agent_id="founder1", status=GenerationStatus.FOUNDER)
    assert founder.add_successor("succ1") is True
    assert founder.status == GenerationStatus.MENTOR


def test_legacy_system_registration():
    """Test registering founder in legacy system"""
    system = LegacySystem()
    assert system.register_founder("founder1") is True
    assert "founder1" in system.lineages


def test_legacy_system_succession():
    """Test creating successor in legacy system"""
    system = LegacySystem()
    system.register_founder("founder1")
    successor = system.create_successor("founder1", "succ1")

    assert successor is not None
    assert successor.predecessor_id == "founder1"
    assert system.lineages["founder1"].status == GenerationStatus.MENTOR


def test_capability_transfer():
    """Test transferring capability through system"""
    system = LegacySystem()
    system.register_founder("founder1")
    successor = system.create_successor("founder1", "succ1")

    capability = InheritedCapability(
        capability_id="cap1",
        legacy_type=LegacyType.SKILL,
        name="Wisdom",
        strength=0.9,
        origin_agent="founder1"
    )

    assert system.transfer_capability("founder1", "succ1", capability) is True
    assert len(successor.inherited_capabilities) == 1


def test_teaching_successor():
    """Test predecessor teaching successor"""
    system = LegacySystem()
    system.register_founder("founder1")
    successor = system.create_successor("founder1", "succ1")

    assert system.teach_successor("founder1", "succ1") is True
    assert len(successor.inherited_capabilities) >= 1


def test_successor_innovation():
    """Test successor innovating new capability"""
    system = LegacySystem()
    system.register_founder("founder1")
    successor = system.create_successor("founder1", "succ1")

    assert system.successor_innovates("succ1", "new_cap", "Innovation") is True
    assert len(successor.original_capabilities) == 1


def test_lineage_health():
    """Test getting lineage health metrics"""
    system = LegacySystem()
    system.register_founder("founder1")
    system.create_successor("founder1", "succ1")
    system.teach_successor("founder1", "succ1")

    health = system.get_lineage_health("succ1")
    assert "generation" in health
    assert "inherited_capabilities" in health


def test_lineage_tree():
    """Test getting complete lineage tree"""
    system = LegacySystem()
    system.register_founder("founder1")
    system.create_successor("founder1", "succ1")
    system.create_successor("succ1", "grand1")

    tree = system.get_lineage_tree("founder1")
    assert tree["agent_id"] == "founder1"
    assert len(tree["children"]) == 1
    assert len(tree["children"][0]["children"]) == 1


def test_legendary_promotion():
    """Test promoting agent to legendary status"""
    system = LegacySystem()
    system.register_founder("founder1")

    # Need at least 3 successors for legendary
    for i in range(3):
        system.create_successor("founder1", f"succ{i}")

    assert system.promote_to_legendary("founder1") is True
    assert "founder1" in system.legendary_agents


def test_system_statistics():
    """Test system statistics"""
    system = LegacySystem()
    system.register_founder("founder1")
    system.create_successor("founder1", "succ1")
    system.create_successor("succ1", "grand1")

    stats = system.get_system_statistics()
    assert stats["total_lineages"] == 3
    assert stats["generations_created"] == 2


def test_complete_legacy_workflow():
    """Test complete legacy workflow across generations"""
    system = LegacySystem()

    # Generation 0: Founder
    system.register_founder("sage_1")

    # Generation 1: First successor inherits wisdom
    succ1 = system.create_successor("sage_1", "sage_1_student")
    system.teach_successor("sage_1", "sage_1_student")
    system.successor_innovates("sage_1_student", "new_technique_1", "Meditation Method")

    # Generation 2: Second-generation successor
    succ2 = system.create_successor("sage_1_student", "sage_2_student")
    system.teach_successor("sage_1_student", "sage_2_student")
    system.successor_innovates("sage_2_student", "new_technique_2", "Synthesis")

    # Generation 3: Continue lineage
    system.create_successor("sage_2_student", "sage_3_student")

    # Check lineage
    tree = system.get_lineage_tree("sage_1")
    assert tree["generation"] == 0
    assert len(tree["children"]) == 1
    assert tree["children"][0]["generation"] == 1
    assert len(tree["children"][0]["children"]) == 1

    # Promote founder to legendary (has multiple successors)
    system.register_founder("sage_1")
    for i in range(3):
        system.create_successor("sage_1", f"other_succ_{i}")
    system.promote_to_legendary("sage_1")

    assert "sage_1" in system.legendary_agents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
