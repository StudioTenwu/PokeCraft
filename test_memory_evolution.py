"""
Round 16: Memory Evolution & Growth Tracking

This module enables agents to evolve their memory systems through experiences.
Memory capacity grows, retention improves, and learning curves develop as agents
interact with their world and develop relationships.

Key concepts:
- Memory capacity progression (short-term → long-term)
- Memory retention and recall quality improvements
- Experience integration driving growth
- Learning curves and skill acquisition tracking
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


class MemoryType(Enum):
    """Types of memories agents can store"""
    SHORT_TERM = "short_term"  # Immediate context (0-1 hour)
    EPISODIC = "episodic"  # Specific events and experiences
    SEMANTIC = "semantic"  # Knowledge and facts
    PROCEDURAL = "procedural"  # Skills and how-to knowledge
    EMOTIONAL = "emotional"  # Feelings tied to experiences


class MemoryCapacity(Enum):
    """Memory storage capacity levels"""
    MINIMAL = 5  # Can remember 5 items
    SMALL = 15
    MEDIUM = 50
    LARGE = 200
    VAST = 1000


@dataclass
class Memory:
    """Individual memory unit with metadata"""
    memory_id: str
    memory_type: MemoryType
    content: str
    created_at: float = 0.0
    importance: float = 0.5  # 0.0-1.0
    access_count: int = 0
    retention: float = 1.0  # 0.0-1.0, decays over time

    def decay(self, time_factor: float) -> bool:
        """Decay memory retention over time"""
        self.retention = max(0.0, self.retention - time_factor)
        return self.retention > 0.0

    def access(self) -> float:
        """Access memory and strengthen retention"""
        self.access_count += 1
        self.retention = min(1.0, self.retention + 0.05)
        return self.retention

    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "importance": self.importance,
            "access_count": self.access_count,
            "retention": self.retention
        }


@dataclass
class MemorySystem:
    """Agent's memory system with capacity and evolution"""
    agent_id: str
    current_capacity: MemoryCapacity = MemoryCapacity.SMALL
    memories: Dict[str, Memory] = field(default_factory=dict)
    capacity_level: int = 1  # 1-5 progression
    learning_rate: float = 1.0  # Multiplier for memory improvement
    total_experiences: int = 0

    def add_memory(self, memory: Memory) -> bool:
        """Add memory to system (respects capacity)"""
        if len(self.memories) >= self.current_capacity.value:
            return False
        self.memories[memory.memory_id] = memory
        return True

    def recall_memory(self, memory_id: str) -> Optional[Memory]:
        """Recall a memory and strengthen it"""
        if memory_id not in self.memories:
            return None
        memory = self.memories[memory_id]
        memory.access()
        return memory

    def upgrade_capacity(self) -> bool:
        """Upgrade memory capacity level"""
        if self.capacity_level >= 5:
            return False
        self.capacity_level += 1
        # Map levels to capacities
        capacities = [
            MemoryCapacity.MINIMAL,
            MemoryCapacity.SMALL,
            MemoryCapacity.MEDIUM,
            MemoryCapacity.LARGE,
            MemoryCapacity.VAST
        ]
        self.current_capacity = capacities[self.capacity_level - 1]
        return True

    def forget_oldest(self) -> bool:
        """Forget least important/least accessed memory"""
        if not self.memories:
            return False
        worst_memory = min(
            self.memories.values(),
            key=lambda m: (m.importance, m.access_count)
        )
        del self.memories[worst_memory.memory_id]
        return True

    def improve_learning_rate(self, amount: float) -> bool:
        """Improve learning rate (capped at 2.0)"""
        self.learning_rate = min(2.0, self.learning_rate + amount)
        return True

    def integrate_experience(self, experience_data: Dict) -> bool:
        """Integrate an experience into memory"""
        if not experience_data:
            return False
        self.total_experiences += 1
        # Experience integration could trigger capacity upgrade
        if self.total_experiences > 0 and self.total_experiences % 10 == 0:
            self.upgrade_capacity()
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "current_capacity": self.current_capacity.value,
            "capacity_level": self.capacity_level,
            "learning_rate": self.learning_rate,
            "total_experiences": self.total_experiences,
            "memory_count": len(self.memories),
            "memories": {k: v.to_dict() for k, v in self.memories.items()}
        }


@dataclass
class LearningCurve:
    """Tracks agent skill acquisition and learning progression"""
    agent_id: str
    skill_name: str
    current_level: float = 0.0  # 0.0-1.0
    total_practice: int = 0
    learning_efficiency: float = 0.1  # How much each practice improves skill
    threshold_for_growth: int = 5  # Practice sessions before level up

    def practice(self) -> bool:
        """Practice the skill"""
        self.total_practice += 1
        self.current_level += self.learning_efficiency
        self.current_level = min(1.0, self.current_level)
        return True

    def accelerate_learning(self, factor: float) -> bool:
        """Increase learning efficiency"""
        self.learning_efficiency = min(0.5, self.learning_efficiency + factor)
        return True

    def reach_mastery(self) -> bool:
        """Check if skill is mastered"""
        return self.current_level >= 0.95

    def to_dict(self) -> Dict:
        return {
            "skill_name": self.skill_name,
            "current_level": self.current_level,
            "total_practice": self.total_practice,
            "learning_efficiency": self.learning_efficiency,
            "mastered": self.reach_mastery()
        }


@dataclass
class GrowthTracker:
    """Track overall agent growth across multiple dimensions"""
    agent_id: str
    memory_system: MemorySystem = field(default_factory=lambda: MemorySystem("unknown"))
    learning_curves: Dict[str, LearningCurve] = field(default_factory=dict)
    growth_score: float = 0.0  # 0.0-1.0 overall growth
    milestones_reached: List[str] = field(default_factory=list)

    def add_learning_curve(self, skill_name: str, curve: LearningCurve) -> bool:
        """Add skill learning curve"""
        if skill_name in self.learning_curves:
            return False
        self.learning_curves[skill_name] = curve
        return True

    def update_growth_score(self) -> float:
        """Calculate overall growth from memory and learning"""
        if not self.learning_curves:
            return 0.0
        avg_skill_level = sum(
            curve.current_level for curve in self.learning_curves.values()
        ) / len(self.learning_curves)
        memory_growth = (self.memory_system.capacity_level / 5.0)
        self.growth_score = (avg_skill_level * 0.6) + (memory_growth * 0.4)
        return self.growth_score

    def reach_milestone(self, milestone: str) -> bool:
        """Record reaching a growth milestone"""
        if milestone in self.milestones_reached:
            return False
        self.milestones_reached.append(milestone)
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "growth_score": self.growth_score,
            "memory_level": self.memory_system.capacity_level,
            "skills_learned": len(self.learning_curves),
            "milestones": self.milestones_reached,
            "learning_curves": {k: v.to_dict() for k, v in self.learning_curves.items()}
        }


# ===== Tests =====

def test_memory_creation():
    """Test individual memory creation"""
    memory = Memory(
        memory_id="mem_001",
        memory_type=MemoryType.EPISODIC,
        content="Met a friend at the park",
        importance=0.8
    )
    assert memory.memory_id == "mem_001"
    assert memory.retention == 1.0


def test_memory_decay():
    """Test memory retention decay over time"""
    memory = Memory(
        memory_id="mem_002",
        memory_type=MemoryType.SHORT_TERM,
        content="temporary info",
        retention=1.0
    )
    assert memory.decay(0.2) is True
    assert memory.retention == 0.8
    # Decay again to near-zero
    result = memory.decay(0.79)
    assert result is True
    assert abs(memory.retention - 0.01) < 0.0001


def test_memory_access_strengthens_retention():
    """Test accessing memory strengthens it"""
    memory = Memory(
        memory_id="mem_003",
        memory_type=MemoryType.SEMANTIC,
        content="fact to remember",
        retention=0.5
    )
    memory.access()
    assert memory.access_count == 1
    assert memory.retention > 0.5


def test_memory_system_initialization():
    """Test memory system creation"""
    system = MemorySystem(agent_id="agent_001")
    assert system.agent_id == "agent_001"
    assert system.capacity_level == 1
    assert system.current_capacity == MemoryCapacity.SMALL


def test_memory_system_add_memory():
    """Test adding memories to system"""
    system = MemorySystem(agent_id="agent_002")
    memory = Memory(
        memory_id="mem_004",
        memory_type=MemoryType.EPISODIC,
        content="first memory"
    )
    assert system.add_memory(memory) is True
    assert len(system.memories) == 1


def test_memory_capacity_overflow():
    """Test memory system respects capacity limits"""
    system = MemorySystem(agent_id="agent_003", current_capacity=MemoryCapacity.MINIMAL)
    for i in range(6):
        memory = Memory(
            memory_id=f"mem_{i:03d}",
            memory_type=MemoryType.SHORT_TERM,
            content=f"memory {i}"
        )
        if i < 5:
            assert system.add_memory(memory) is True
        else:
            assert system.add_memory(memory) is False


def test_memory_recall():
    """Test recalling memory strengthens it"""
    system = MemorySystem(agent_id="agent_004")
    memory = Memory(
        memory_id="mem_005",
        memory_type=MemoryType.EPISODIC,
        content="important event"
    )
    system.add_memory(memory)
    recalled = system.recall_memory(memory.memory_id)
    assert recalled is not None
    assert recalled.access_count == 1


def test_capacity_upgrade():
    """Test upgrading memory capacity"""
    system = MemorySystem(agent_id="agent_005")
    assert system.capacity_level == 1
    assert system.upgrade_capacity() is True
    assert system.capacity_level == 2
    # Level 2 maps to second capacity (index 1)
    expected_capacity = [
        MemoryCapacity.MINIMAL,
        MemoryCapacity.SMALL,
        MemoryCapacity.MEDIUM,
        MemoryCapacity.LARGE,
        MemoryCapacity.VAST
    ][system.capacity_level - 1]
    assert system.current_capacity == expected_capacity


def test_forget_oldest_memory():
    """Test forgetting least important memory"""
    system = MemorySystem(agent_id="agent_006")
    for i in range(3):
        memory = Memory(
            memory_id=f"mem_{i:03d}",
            memory_type=MemoryType.SHORT_TERM,
            content=f"memory {i}",
            importance=float(i) / 3.0  # increasing importance
        )
        system.add_memory(memory)
    
    assert system.forget_oldest() is True
    assert len(system.memories) == 2
    assert "mem_000" not in system.memories


def test_learning_rate_improvement():
    """Test improving learning efficiency"""
    system = MemorySystem(agent_id="agent_007")
    assert system.learning_rate == 1.0
    assert system.improve_learning_rate(0.3) is True
    assert system.learning_rate == 1.3
    
    # Test ceiling
    system.improve_learning_rate(1.5)
    assert system.learning_rate == 2.0


def test_experience_integration():
    """Test integrating experiences"""
    system = MemorySystem(agent_id="agent_008")
    for i in range(15):
        assert system.integrate_experience({"event": f"experience_{i}"}) is True
    assert system.total_experiences == 15


def test_learning_curve_creation():
    """Test learning curve initialization"""
    curve = LearningCurve(
        agent_id="agent_009",
        skill_name="painting",
        learning_efficiency=0.1
    )
    assert curve.skill_name == "painting"
    assert curve.current_level == 0.0


def test_learning_curve_practice():
    """Test skill practice and improvement"""
    curve = LearningCurve(
        agent_id="agent_010",
        skill_name="writing",
        learning_efficiency=0.1
    )
    for _ in range(5):
        curve.practice()
    assert curve.current_level == 0.5
    assert curve.total_practice == 5


def test_learning_curve_mastery():
    """Test reaching skill mastery"""
    curve = LearningCurve(
        agent_id="agent_011",
        skill_name="mathematics",
        learning_efficiency=0.3
    )
    for _ in range(4):
        curve.practice()
    assert curve.reach_mastery() is True


def test_learning_acceleration():
    """Test accelerating learning"""
    curve = LearningCurve(
        agent_id="agent_012",
        skill_name="music",
        learning_efficiency=0.1
    )
    assert curve.accelerate_learning(0.1) is True
    assert curve.learning_efficiency == 0.2


def test_growth_tracker_initialization():
    """Test growth tracker creation"""
    memory_system = MemorySystem(agent_id="agent_013")
    tracker = GrowthTracker(
        agent_id="agent_013",
        memory_system=memory_system
    )
    assert tracker.agent_id == "agent_013"
    assert tracker.growth_score == 0.0


def test_growth_tracker_add_skill():
    """Test adding learning curves to tracker"""
    memory_system = MemorySystem(agent_id="agent_014")
    tracker = GrowthTracker(
        agent_id="agent_014",
        memory_system=memory_system
    )
    curve = LearningCurve(
        agent_id="agent_014",
        skill_name="painting"
    )
    assert tracker.add_learning_curve("painting", curve) is True
    assert "painting" in tracker.learning_curves


def test_growth_score_calculation():
    """Test calculating overall growth score"""
    memory_system = MemorySystem(agent_id="agent_015")
    tracker = GrowthTracker(
        agent_id="agent_015",
        memory_system=memory_system
    )
    
    # Add multiple skills at different levels
    for skill_name, level in [("art", 0.6), ("music", 0.7), ("writing", 0.5)]:
        curve = LearningCurve(agent_id="agent_015", skill_name=skill_name)
        curve.current_level = level
        tracker.add_learning_curve(skill_name, curve)
    
    score = tracker.update_growth_score()
    assert score > 0.3
    assert score < 1.0


def test_milestone_tracking():
    """Test reaching growth milestones"""
    memory_system = MemorySystem(agent_id="agent_016")
    tracker = GrowthTracker(
        agent_id="agent_016",
        memory_system=memory_system
    )
    
    assert tracker.reach_milestone("first_skill_learned") is True
    assert tracker.reach_milestone("memory_upgraded") is True
    assert tracker.reach_milestone("first_skill_learned") is False  # Duplicate
    assert len(tracker.milestones_reached) == 2


def test_complete_growth_workflow():
    """Test complete agent growth workflow"""
    # Create agent with memory system
    memory_system = MemorySystem(agent_id="growing_agent")
    tracker = GrowthTracker(agent_id="growing_agent", memory_system=memory_system)
    
    # Add skills
    for skill in ["painting", "music", "writing"]:
        curve = LearningCurve(agent_id="growing_agent", skill_name=skill)
        tracker.add_learning_curve(skill, curve)
    
    # Practice and grow
    for _ in range(5):
        for curve in tracker.learning_curves.values():
            curve.practice()
        memory_system.integrate_experience({"type": "practice"})
    
    # Track milestones
    tracker.reach_milestone("first_practice_session")
    tracker.reach_milestone("growing_skill_mastery")
    
    # Calculate growth
    score = tracker.update_growth_score()
    
    assert score > 0.0
    assert memory_system.total_experiences == 5
    assert len(tracker.milestones_reached) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
