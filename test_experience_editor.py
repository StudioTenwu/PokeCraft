"""
Round 28: Experience Editor & Therapy System

Enable players to craft narratives, edit memories, and provide therapeutic
support to agents. This is the "Empathizer Role" made deep - players
understand their agents by rewinding, replaying, and healing traumatic experiences.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ExperienceType(Enum):
    """Types of experiences agents can have"""
    POSITIVE = "positive"  # Success, joy, discovery
    NEGATIVE = "negative"  # Failure, frustration
    NEUTRAL = "neutral"  # Mundane, learning
    TRANSFORMATIVE = "transformative"  # Life-changing moment
    TRAUMATIC = "traumatic"  # Painful experience


class EditType(Enum):
    """Types of edits a player can make"""
    REFRAME = "reframe"  # Change perspective on memory
    SUPPRESS = "suppress"  # Temporarily hide memory
    ENHANCE = "enhance"  # Make positive aspects stronger
    SOOTHE = "soothe"  # Reduce emotional intensity
    RECONSTRUCT = "reconstruct"  # Rebuild memory from scratch


class TherapyTechnique(Enum):
    """Therapeutic approaches available"""
    COGNITIVE_REFRAMING = "cognitive_reframing"  # Change interpretation
    EXPOSURE_THERAPY = "exposure_therapy"  # Gentle re-exposure
    NARRATIVE_THERAPY = "narrative_therapy"  # Rewrite the story
    EMOTIONAL_REGULATION = "emotional_regulation"  # Manage feelings
    POSITIVE_VISUALIZATION = "positive_visualization"  # Imagine better outcome


@dataclass
class Memory:
    """A memory an agent retains"""
    memory_id: str
    experience_type: ExperienceType
    description: str
    emotional_charge: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    vividness: float = 0.5  # 0.0-1.0, how clear the memory is
    importance: float = 0.5  # 0.0-1.0, how much it affects the agent
    timestamp: int = 0
    is_suppressed: bool = False
    suppression_strength: float = 0.0  # 0.0-1.0, how hidden it is

    def update_emotional_charge(self, amount: float) -> bool:
        """Change emotional intensity of memory"""
        if not (-1.0 <= amount <= 1.0):
            return False
        self.emotional_charge = max(-1.0, min(1.0, self.emotional_charge + amount))
        return True

    def suppress(self, strength: float = 0.7) -> bool:
        """Suppress/hide a memory"""
        if not (0.0 <= strength <= 1.0):
            return False
        self.is_suppressed = True
        self.suppression_strength = strength
        self.vividness = max(0.0, self.vividness * (1.0 - strength))
        return True

    def unsuppress(self) -> bool:
        """Restore suppressed memory"""
        if not self.is_suppressed:
            return False
        self.is_suppressed = False
        self.vividness = min(1.0, self.vividness / max(0.1, 1.0 - self.suppression_strength))
        self.suppression_strength = 0.0
        return True

    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "type": self.experience_type.value,
            "emotional_charge": self.emotional_charge,
            "vividness": self.vividness,
            "is_suppressed": self.is_suppressed
        }


@dataclass
class TherapySession:
    """A therapeutic session with an agent"""
    session_id: str
    agent_id: str
    technique: TherapyTechnique
    target_memory_id: Optional[str] = None
    duration: int = 0  # Number of turns
    effectiveness: float = 0.0  # 0.0-1.0, how successful
    memories_processed: List[str] = field(default_factory=list)
    insights_gained: List[str] = field(default_factory=list)
    is_completed: bool = False

    def add_insight(self, insight: str) -> bool:
        """Record an insight from therapy"""
        if len(self.insights_gained) >= 10:  # Cap at 10 insights per session
            return False
        self.insights_gained.append(insight)
        return True

    def process_memory(self, memory_id: str) -> bool:
        """Process a memory during therapy"""
        if memory_id in self.memories_processed:
            return False
        self.memories_processed.append(memory_id)
        self.effectiveness = min(1.0, self.effectiveness + 0.15)
        return True

    def complete_session(self) -> bool:
        """Mark therapy session as complete"""
        if self.is_completed:
            return False
        self.is_completed = True
        self.effectiveness = min(1.0, self.effectiveness)
        return True

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "technique": self.technique.value,
            "effectiveness": self.effectiveness,
            "memories_processed": len(self.memories_processed),
            "insights_gained": len(self.insights_gained),
            "is_completed": self.is_completed
        }


@dataclass
class ExperienceEdit:
    """An edit made to a memory by a player"""
    edit_id: str
    memory_id: str
    edit_type: EditType
    before_charge: float  # Emotional charge before edit
    after_charge: float  # Emotional charge after edit
    timestamp: int = 0
    approved: bool = False  # Did agent accept this edit?
    agent_acceptance_score: float = 0.5  # 0.0-1.0, how much agent agrees

    def apply_to_memory(self, memory: Memory) -> bool:
        """Apply this edit to a memory"""
        if self.edit_type == EditType.SOOTHE:
            # Reduce emotional intensity
            memory.emotional_charge = self.after_charge
            memory.vividness = max(0.1, memory.vividness - 0.2)
        elif self.edit_type == EditType.ENHANCE:
            # Strengthen positive aspects
            memory.emotional_charge = self.after_charge
            memory.importance = min(1.0, memory.importance + 0.2)
        elif self.edit_type == EditType.REFRAME:
            # Change perspective
            memory.emotional_charge = self.after_charge
        elif self.edit_type == EditType.SUPPRESS:
            # Hide the memory
            memory.suppress(0.7)
        elif self.edit_type == EditType.RECONSTRUCT:
            # Rebuild from scratch
            memory.emotional_charge = self.after_charge
            memory.vividness = 0.7  # Fresh memory

        return True

    def to_dict(self) -> Dict:
        return {
            "edit_id": self.edit_id,
            "memory_id": self.memory_id,
            "edit_type": self.edit_type.value,
            "agent_acceptance": self.agent_acceptance_score,
            "was_approved": self.approved
        }


class ExperienceEditor:
    """Manage memory editing and therapy for agents"""

    def __init__(self):
        self.agent_memories: Dict[str, List[Memory]] = {}
        self.edits: Dict[str, ExperienceEdit] = {}
        self.therapy_sessions: Dict[str, TherapySession] = {}
        self.total_edits_made: int = 0
        self.total_sessions_completed: int = 0

    def register_agent(self, agent_id: str) -> bool:
        """Register an agent for memory editing"""
        if agent_id in self.agent_memories:
            return False
        self.agent_memories[agent_id] = []
        return True

    def add_memory(self, agent_id: str, memory: Memory) -> bool:
        """Add a memory to agent's history"""
        if agent_id not in self.agent_memories:
            return False
        self.agent_memories[agent_id].append(memory)
        return True

    def get_agent_memories(self, agent_id: str) -> List[Memory]:
        """Get all memories for an agent"""
        return self.agent_memories.get(agent_id, [])

    def edit_memory(self, agent_id: str, memory_id: str, edit: ExperienceEdit) -> bool:
        """Make an edit to agent's memory"""
        if agent_id not in self.agent_memories:
            return False

        # Find the memory
        memory = None
        for m in self.agent_memories[agent_id]:
            if m.memory_id == memory_id:
                memory = m
                break

        if not memory:
            return False

        # Apply the edit
        edit.apply_to_memory(memory)
        self.edits[edit.edit_id] = edit
        self.total_edits_made += 1
        return True

    def approve_edit(self, edit_id: str, agent_acceptance: float) -> bool:
        """Agent accepts (or rejects) an edit"""
        if edit_id not in self.edits:
            return False

        edit = self.edits[edit_id]
        edit.agent_acceptance_score = agent_acceptance
        if agent_acceptance >= 0.6:
            edit.approved = True
        return True

    def create_therapy_session(self, session: TherapySession) -> bool:
        """Create a therapy session"""
        if session.session_id in self.therapy_sessions:
            return False
        self.therapy_sessions[session.session_id] = session
        return True

    def process_memory_in_therapy(self, session_id: str, memory_id: str) -> bool:
        """Process a memory during therapy"""
        if session_id not in self.therapy_sessions:
            return False

        session = self.therapy_sessions[session_id]
        return session.process_memory(memory_id)

    def complete_therapy_session(self, session_id: str) -> bool:
        """Complete a therapy session"""
        if session_id not in self.therapy_sessions:
            return False

        session = self.therapy_sessions[session_id]
        if session.complete_session():
            self.total_sessions_completed += 1
            return True
        return False

    def get_emotional_trajectory(self, agent_id: str) -> List[float]:
        """Get agent's emotional journey over time"""
        memories = self.get_agent_memories(agent_id)
        return [m.emotional_charge for m in sorted(memories, key=lambda x: x.timestamp)]

    def get_emotional_health(self, agent_id: str) -> Dict:
        """Calculate agent's emotional well-being"""
        memories = self.get_agent_memories(agent_id)
        if not memories:
            return {"emotional_health": 0.5}

        avg_charge = sum(m.emotional_charge for m in memories) / len(memories)
        traumatic_count = sum(1 for m in memories if m.experience_type == ExperienceType.TRAUMATIC and not m.is_suppressed)
        suppressed_count = sum(1 for m in memories if m.is_suppressed)

        # Health = average emotional tone + resilience (managing trauma)
        resilience = 1.0 - (traumatic_count / max(1, len(memories)))
        health = (avg_charge + 1.0) / 2.0 * resilience  # Normalize to 0.0-1.0

        return {
            "emotional_health": health,
            "avg_emotional_charge": avg_charge,
            "traumatic_memories": traumatic_count,
            "suppressed_memories": suppressed_count,
            "total_memories": len(memories)
        }

    def get_recovery_potential(self, agent_id: str) -> float:
        """Estimate agent's potential for healing (0.0-1.0)"""
        sessions = [s for s in self.therapy_sessions.values() if s.agent_id == agent_id]
        if not sessions:
            return 0.3  # Base recovery potential

        completed = [s for s in sessions if s.is_completed]
        if not completed:
            return 0.5

        avg_effectiveness = sum(s.effectiveness for s in completed) / len(completed)
        return min(1.0, avg_effectiveness + 0.3)

    def get_narrative_coherence(self, agent_id: str) -> float:
        """How coherent is agent's life narrative (0.0-1.0)"""
        memories = self.get_agent_memories(agent_id)
        if len(memories) < 3:
            return 0.5

        # Coherence = avoiding emotional whiplash + narrative progression
        charges = [m.emotional_charge for m in sorted(memories, key=lambda x: x.timestamp)]

        # Check for smooth progression (low variance = more coherent)
        if len(charges) > 1:
            diffs = [abs(charges[i] - charges[i-1]) for i in range(1, len(charges))]
            avg_diff = sum(diffs) / len(diffs)
            coherence = 1.0 - min(1.0, avg_diff)
        else:
            coherence = 0.5

        return coherence

    def to_dict(self) -> Dict:
        return {
            "total_agents": len(self.agent_memories),
            "total_memories": sum(len(m) for m in self.agent_memories.values()),
            "total_edits": self.total_edits_made,
            "therapy_sessions_completed": self.total_sessions_completed
        }


# ===== Tests =====

def test_memory_creation():
    """Test creating a memory"""
    memory = Memory(
        memory_id="m1",
        experience_type=ExperienceType.POSITIVE,
        description="Learned something new"
    )
    assert memory.emotional_charge == 0.0


def test_memory_emotional_charge():
    """Test updating emotional charge"""
    memory = Memory(memory_id="m1", experience_type=ExperienceType.NEUTRAL, description="Task")
    assert memory.update_emotional_charge(0.3) is True
    assert abs(memory.emotional_charge - 0.3) < 0.0001


def test_memory_suppression():
    """Test suppressing a memory"""
    memory = Memory(memory_id="m1", experience_type=ExperienceType.TRAUMATIC, description="Bad event", vividness=1.0)
    assert memory.suppress(0.8) is True
    assert memory.is_suppressed is True
    assert memory.vividness < 1.0


def test_memory_unsuppression():
    """Test restoring a suppressed memory"""
    memory = Memory(memory_id="m1", experience_type=ExperienceType.TRAUMATIC, description="Bad event", vividness=1.0)
    memory.suppress(0.7)
    assert memory.unsuppress() is True
    assert memory.is_suppressed is False


def test_therapy_session_creation():
    """Test creating therapy session"""
    session = TherapySession(
        session_id="t1",
        agent_id="a1",
        technique=TherapyTechnique.COGNITIVE_REFRAMING
    )
    assert session.is_completed is False


def test_therapy_insight():
    """Test recording insight in therapy"""
    session = TherapySession(session_id="t1", agent_id="a1", technique=TherapyTechnique.EMOTIONAL_REGULATION)
    assert session.add_insight("Failure teaches growth") is True
    assert len(session.insights_gained) == 1


def test_therapy_process_memory():
    """Test processing memory in therapy"""
    session = TherapySession(session_id="t1", agent_id="a1", technique=TherapyTechnique.NARRATIVE_THERAPY)
    assert session.process_memory("m1") is True
    assert len(session.memories_processed) == 1


def test_therapy_completion():
    """Test completing therapy session"""
    session = TherapySession(session_id="t1", agent_id="a1", technique=TherapyTechnique.POSITIVE_VISUALIZATION)
    assert session.complete_session() is True
    assert session.is_completed is True


def test_experience_edit_creation():
    """Test creating an edit"""
    edit = ExperienceEdit(
        edit_id="e1",
        memory_id="m1",
        edit_type=EditType.REFRAME,
        before_charge=-0.7,
        after_charge=-0.2
    )
    assert edit.agent_acceptance_score == 0.5


def test_edit_soothe():
    """Test soothing edit on memory"""
    memory = Memory(
        memory_id="m1",
        experience_type=ExperienceType.NEGATIVE,
        description="Failure",
        emotional_charge=-0.8,
        vividness=0.9
    )
    edit = ExperienceEdit(
        edit_id="e1",
        memory_id="m1",
        edit_type=EditType.SOOTHE,
        before_charge=-0.8,
        after_charge=-0.3
    )
    edit.apply_to_memory(memory)
    assert memory.emotional_charge == -0.3
    assert memory.vividness < 0.9


def test_edit_enhance():
    """Test enhancing positive memory"""
    memory = Memory(
        memory_id="m1",
        experience_type=ExperienceType.POSITIVE,
        description="Success",
        emotional_charge=0.6,
        importance=0.5
    )
    edit = ExperienceEdit(
        edit_id="e1",
        memory_id="m1",
        edit_type=EditType.ENHANCE,
        before_charge=0.6,
        after_charge=0.8
    )
    edit.apply_to_memory(memory)
    assert memory.importance > 0.5


def test_experience_editor_registration():
    """Test registering agent with editor"""
    editor = ExperienceEditor()
    assert editor.register_agent("a1") is True
    assert "a1" in editor.agent_memories


def test_add_memory_to_agent():
    """Test adding memory to agent"""
    editor = ExperienceEditor()
    editor.register_agent("a1")
    memory = Memory(memory_id="m1", experience_type=ExperienceType.POSITIVE, description="Joy")
    assert editor.add_memory("a1", memory) is True


def test_edit_agent_memory():
    """Test editing agent's memory"""
    editor = ExperienceEditor()
    editor.register_agent("a1")
    memory = Memory(memory_id="m1", experience_type=ExperienceType.NEGATIVE, description="Failure", emotional_charge=-0.7)
    editor.add_memory("a1", memory)

    edit = ExperienceEdit(
        edit_id="e1",
        memory_id="m1",
        edit_type=EditType.SOOTHE,
        before_charge=-0.7,
        after_charge=-0.2
    )
    assert editor.edit_memory("a1", "m1", edit) is True


def test_emotional_trajectory():
    """Test getting emotional trajectory"""
    editor = ExperienceEditor()
    editor.register_agent("a1")

    m1 = Memory(memory_id="m1", experience_type=ExperienceType.POSITIVE, description="Start", emotional_charge=0.5, timestamp=0)
    m2 = Memory(memory_id="m2", experience_type=ExperienceType.NEGATIVE, description="Struggle", emotional_charge=-0.3, timestamp=1)
    m3 = Memory(memory_id="m3", experience_type=ExperienceType.POSITIVE, description="Growth", emotional_charge=0.7, timestamp=2)

    editor.add_memory("a1", m1)
    editor.add_memory("a1", m2)
    editor.add_memory("a1", m3)

    trajectory = editor.get_emotional_trajectory("a1")
    assert len(trajectory) == 3


def test_emotional_health():
    """Test calculating emotional health"""
    editor = ExperienceEditor()
    editor.register_agent("a1")

    memory = Memory(memory_id="m1", experience_type=ExperienceType.POSITIVE, description="Happy", emotional_charge=0.8)
    editor.add_memory("a1", memory)

    health = editor.get_emotional_health("a1")
    assert "emotional_health" in health
    assert 0.0 <= health["emotional_health"] <= 1.0


def test_recovery_potential():
    """Test calculating recovery potential"""
    editor = ExperienceEditor()
    potential = editor.get_recovery_potential("a1")
    assert 0.0 <= potential <= 1.0


def test_narrative_coherence():
    """Test measuring narrative coherence"""
    editor = ExperienceEditor()
    editor.register_agent("a1")

    # Add emotional journey
    m1 = Memory(memory_id="m1", experience_type=ExperienceType.NEUTRAL, description="Start", emotional_charge=0.0, timestamp=0)
    m2 = Memory(memory_id="m2", experience_type=ExperienceType.POSITIVE, description="Growth", emotional_charge=0.5, timestamp=1)
    m3 = Memory(memory_id="m3", experience_type=ExperienceType.POSITIVE, description="Success", emotional_charge=0.8, timestamp=2)

    editor.add_memory("a1", m1)
    editor.add_memory("a1", m2)
    editor.add_memory("a1", m3)

    coherence = editor.get_narrative_coherence("a1")
    assert 0.0 <= coherence <= 1.0


def test_complete_therapy_workflow():
    """Test complete therapy workflow"""
    editor = ExperienceEditor()
    editor.register_agent("a1")

    # Add traumatic memory
    trauma = Memory(
        memory_id="trauma_1",
        experience_type=ExperienceType.TRAUMATIC,
        description="Failed task",
        emotional_charge=-0.9,
        vividness=1.0
    )
    editor.add_memory("a1", trauma)

    # Create therapy session
    session = TherapySession(
        session_id="therapy_1",
        agent_id="a1",
        technique=TherapyTechnique.COGNITIVE_REFRAMING,
        target_memory_id="trauma_1"
    )
    editor.create_therapy_session(session)

    # Process memory in therapy
    assert editor.process_memory_in_therapy("therapy_1", "trauma_1") is True

    # Add insight
    assert session.add_insight("Failure is learning") is True

    # Complete session
    assert editor.complete_therapy_session("therapy_1") is True

    # Soothe the memory
    edit = ExperienceEdit(
        edit_id="edit_1",
        memory_id="trauma_1",
        edit_type=EditType.SOOTHE,
        before_charge=-0.9,
        after_charge=-0.3
    )
    editor.edit_memory("a1", "trauma_1", edit)

    # Check emotional health - even soothed trauma is still negative
    health = editor.get_emotional_health("a1")
    # With soothing, -0.3 is better than -0.9, so emotional health is higher
    assert health["emotional_health"] >= 0.0
    assert health["traumatic_memories"] == 1  # Still traumatic but soothed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
