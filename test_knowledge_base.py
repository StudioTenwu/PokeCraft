"""
Round 33: Knowledge Base & Learning Optimization

Enable agents to accumulate knowledge, optimize learning strategies,
retrieve relevant information efficiently, and improve over time.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class KnowledgeType(Enum):
    """Types of knowledge agents can learn"""
    FACTUAL = "factual"  # Facts and data
    PROCEDURAL = "procedural"  # How-to knowledge
    CONCEPTUAL = "conceptual"  # Understanding concepts
    STRATEGIC = "strategic"  # When and how to apply
    METACOGNITIVE = "metacognitive"  # Knowing how to learn


class KnowledgeTier(Enum):
    """Levels of knowledge depth"""
    SURFACE = "surface"  # Basic awareness
    INTERMEDIATE = "intermediate"  # Working understanding
    DEEP = "deep"  # Mastery-level knowledge
    EXPERT = "expert"  # Can teach others


@dataclass
class KnowledgeUnit:
    """A piece of knowledge"""
    unit_id: str
    knowledge_type: KnowledgeType
    topic: str
    content: str
    tier: KnowledgeTier = KnowledgeTier.SURFACE
    reliability: float = 0.5  # 0.0-1.0, how confident
    usage_count: int = 0
    prerequisite_units: Set[str] = field(default_factory=set)

    def use_knowledge(self) -> bool:
        """Record using this knowledge"""
        self.usage_count += 1
        return True

    def deepen_understanding(self) -> bool:
        """Deepen tier of knowledge"""
        tier_progression = [KnowledgeTier.SURFACE, KnowledgeTier.INTERMEDIATE, KnowledgeTier.DEEP, KnowledgeTier.EXPERT]
        current_idx = tier_progression.index(self.tier)
        if current_idx < len(tier_progression) - 1:
            self.tier = tier_progression[current_idx + 1]
            self.reliability = min(1.0, self.reliability + 0.2)
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "unit_id": self.unit_id,
            "topic": self.topic,
            "tier": self.tier.value,
            "reliability": self.reliability,
            "usage_count": self.usage_count
        }


@dataclass
class LearningStrategy:
    """How an agent learns effectively"""
    strategy_id: str
    agent_id: str
    name: str
    description: str
    effectiveness: float = 0.5  # 0.0-1.0
    time_required: float = 1.0  # Relative time cost
    retention: float = 0.5  # 0.0-1.0, how well knowledge sticks
    usage_count: int = 0

    def apply_strategy(self) -> bool:
        """Use this learning strategy"""
        self.usage_count += 1
        return True

    def improve_effectiveness(self, amount: float = 0.1) -> bool:
        """Strategy becomes more effective"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.effectiveness = min(1.0, self.effectiveness + amount)
        return True

    def to_dict(self) -> Dict:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "effectiveness": self.effectiveness,
            "retention": self.retention
        }


class KnowledgeBase:
    """Manage agent knowledge and learning"""

    def __init__(self):
        self.knowledge_units: Dict[str, KnowledgeUnit] = {}
        self.agent_knowledge: Dict[str, Set[str]] = {}  # agent_id → knowledge unit ids
        self.learning_strategies: Dict[str, LearningStrategy] = {}
        self.agent_strategies: Dict[str, List[str]] = {}  # agent_id → strategy ids
        self.knowledge_graph: Dict[str, List[str]] = {}  # topic → related topics
        self.total_knowledge_acquired: int = 0

    def create_knowledge_unit(self, unit: KnowledgeUnit) -> bool:
        """Create knowledge unit"""
        if unit.unit_id in self.knowledge_units:
            return False
        self.knowledge_units[unit.unit_id] = unit
        if unit.topic not in self.knowledge_graph:
            self.knowledge_graph[unit.topic] = []
        return True

    def register_agent(self, agent_id: str) -> bool:
        """Register agent for knowledge tracking"""
        if agent_id in self.agent_knowledge:
            return False
        self.agent_knowledge[agent_id] = set()
        self.agent_strategies[agent_id] = []
        return True

    def teach_agent(self, agent_id: str, unit_id: str) -> bool:
        """Teach agent a knowledge unit"""
        if agent_id not in self.agent_knowledge or unit_id not in self.knowledge_units:
            return False

        if unit_id in self.agent_knowledge[agent_id]:
            return False  # Already knows

        self.agent_knowledge[agent_id].add(unit_id)
        self.total_knowledge_acquired += 1
        return True

    def agent_uses_knowledge(self, agent_id: str, unit_id: str) -> bool:
        """Agent applies knowledge"""
        if agent_id not in self.agent_knowledge or unit_id not in self.knowledge_units:
            return False

        if unit_id not in self.agent_knowledge[agent_id]:
            return False

        unit = self.knowledge_units[unit_id]
        unit.use_knowledge()
        return True

    def deepen_knowledge(self, agent_id: str, unit_id: str) -> bool:
        """Deepen agent's understanding"""
        if unit_id not in self.knowledge_units or unit_id not in self.agent_knowledge.get(agent_id, set()):
            return False

        unit = self.knowledge_units[unit_id]
        return unit.deepen_understanding()

    def create_learning_strategy(self, strategy: LearningStrategy) -> bool:
        """Create learning strategy"""
        if strategy.strategy_id in self.learning_strategies:
            return False
        self.learning_strategies[strategy.strategy_id] = strategy
        return True

    def teach_agent_strategy(self, agent_id: str, strategy_id: str) -> bool:
        """Teach agent a learning strategy"""
        if agent_id not in self.agent_strategies or strategy_id not in self.learning_strategies:
            return False

        if strategy_id in self.agent_strategies[agent_id]:
            return False

        self.agent_strategies[agent_id].append(strategy_id)
        return True

    def apply_strategy(self, agent_id: str, strategy_id: str) -> bool:
        """Agent applies learning strategy"""
        if strategy_id not in self.learning_strategies or strategy_id not in self.agent_strategies.get(agent_id, []):
            return False

        strategy = self.learning_strategies[strategy_id]
        strategy.apply_strategy()
        return True

    def get_agent_knowledge(self, agent_id: str) -> List[str]:
        """Get all knowledge units agent knows"""
        return list(self.agent_knowledge.get(agent_id, []))

    def get_knowledge_by_topic(self, topic: str) -> List[str]:
        """Get knowledge units on topic"""
        return [
            unit_id for unit_id, unit in self.knowledge_units.items()
            if unit.topic == topic
        ]

    def get_related_topics(self, topic: str) -> List[str]:
        """Get topics related to given topic"""
        return self.knowledge_graph.get(topic, [])

    def get_agent_expertise(self, agent_id: str) -> Dict:
        """Get agent's expertise summary"""
        if agent_id not in self.agent_knowledge:
            return {}

        knowledge_ids = self.agent_knowledge[agent_id]
        topics: Dict[str, float] = {}

        for unit_id in knowledge_ids:
            unit = self.knowledge_units.get(unit_id)
            if unit:
                topic = unit.topic
                tier_value = {
                    KnowledgeTier.SURFACE: 0.25,
                    KnowledgeTier.INTERMEDIATE: 0.5,
                    KnowledgeTier.DEEP: 0.75,
                    KnowledgeTier.EXPERT: 1.0
                }.get(unit.tier, 0.0)

                if topic not in topics:
                    topics[topic] = 0.0
                topics[topic] = max(topics[topic], tier_value)

        return {
            "total_knowledge_units": len(knowledge_ids),
            "expertise_by_topic": topics,
            "learning_strategies": len(self.agent_strategies.get(agent_id, []))
        }

    def get_recommended_learning_path(self, agent_id: str, target_topic: str) -> List[str]:
        """Recommend learning path to reach target topic"""
        # Simplified: recommend all related knowledge units
        return self.get_knowledge_by_topic(target_topic)

    def to_dict(self) -> Dict:
        return {
            "total_knowledge_units": len(self.knowledge_units),
            "agents": len(self.agent_knowledge),
            "total_knowledge_acquired": self.total_knowledge_acquired
        }


# ===== Tests =====

def test_knowledge_unit_creation():
    """Test creating knowledge unit"""
    unit = KnowledgeUnit(
        unit_id="k1",
        knowledge_type=KnowledgeType.FACTUAL,
        topic="mathematics",
        content="2+2=4"
    )
    assert unit.tier == KnowledgeTier.SURFACE


def test_deepen_knowledge():
    """Test deepening knowledge"""
    unit = KnowledgeUnit(
        unit_id="k1",
        knowledge_type=KnowledgeType.CONCEPTUAL,
        topic="physics",
        content="Energy conservation"
    )
    assert unit.deepen_understanding() is True
    assert unit.tier == KnowledgeTier.INTERMEDIATE


def test_knowledge_usage():
    """Test using knowledge"""
    unit = KnowledgeUnit(unit_id="k1", knowledge_type=KnowledgeType.PROCEDURAL, topic="coding", content="Python")
    assert unit.use_knowledge() is True
    assert unit.usage_count == 1


def test_learning_strategy_creation():
    """Test creating learning strategy"""
    strategy = LearningStrategy(
        strategy_id="s1",
        agent_id="a1",
        name="Spaced Repetition",
        description="Review material at increasing intervals"
    )
    assert strategy.effectiveness == 0.5


def test_improve_strategy_effectiveness():
    """Test improving strategy"""
    strategy = LearningStrategy(
        strategy_id="s1",
        agent_id="a1",
        name="Practice",
        description="Hands-on practice"
    )
    assert strategy.improve_effectiveness(0.3) is True
    assert strategy.effectiveness == 0.8


def test_knowledge_base_creation():
    """Test creating knowledge base"""
    kb = KnowledgeBase()
    assert kb.register_agent("a1") is True


def test_teach_agent_knowledge():
    """Test teaching agent knowledge"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    unit = KnowledgeUnit(
        unit_id="k1",
        knowledge_type=KnowledgeType.FACTUAL,
        topic="history",
        content="1776 American Independence"
    )
    kb.create_knowledge_unit(unit)

    assert kb.teach_agent("a1", "k1") is True
    assert "k1" in kb.agent_knowledge["a1"]


def test_agent_uses_knowledge():
    """Test agent applying knowledge"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    unit = KnowledgeUnit(unit_id="k1", knowledge_type=KnowledgeType.PROCEDURAL, topic="cooking", content="Recipe")
    kb.create_knowledge_unit(unit)
    kb.teach_agent("a1", "k1")

    assert kb.agent_uses_knowledge("a1", "k1") is True


def test_deepen_agent_knowledge():
    """Test deepening agent's understanding"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    unit = KnowledgeUnit(unit_id="k1", knowledge_type=KnowledgeType.CONCEPTUAL, topic="science", content="Gravity")
    kb.create_knowledge_unit(unit)
    kb.teach_agent("a1", "k1")

    assert kb.deepen_knowledge("a1", "k1") is True
    assert unit.tier == KnowledgeTier.INTERMEDIATE


def test_learning_strategy_assignment():
    """Test teaching agent strategy"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    strategy = LearningStrategy(
        strategy_id="s1",
        agent_id="a1",
        name="SQ3R",
        description="Survey, Question, Read, Recite, Review"
    )
    kb.create_learning_strategy(strategy)

    assert kb.teach_agent_strategy("a1", "s1") is True


def test_apply_learning_strategy():
    """Test agent using strategy"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    strategy = LearningStrategy(strategy_id="s1", agent_id="a1", name="Interleaving", description="Mix topics")
    kb.create_learning_strategy(strategy)
    kb.teach_agent_strategy("a1", "s1")

    assert kb.apply_strategy("a1", "s1") is True


def test_get_agent_expertise():
    """Test getting agent expertise"""
    kb = KnowledgeBase()
    kb.register_agent("a1")

    unit = KnowledgeUnit(unit_id="k1", knowledge_type=KnowledgeType.STRATEGIC, topic="ai", content="Deep Learning")
    unit.tier = KnowledgeTier.DEEP
    kb.create_knowledge_unit(unit)
    kb.teach_agent("a1", "k1")

    expertise = kb.get_agent_expertise("a1")
    assert expertise["total_knowledge_units"] == 1


def test_knowledge_by_topic():
    """Test getting knowledge by topic"""
    kb = KnowledgeBase()

    unit1 = KnowledgeUnit(unit_id="k1", knowledge_type=KnowledgeType.FACTUAL, topic="math", content="Addition")
    unit2 = KnowledgeUnit(unit_id="k2", knowledge_type=KnowledgeType.FACTUAL, topic="math", content="Multiplication")
    kb.create_knowledge_unit(unit1)
    kb.create_knowledge_unit(unit2)

    math_knowledge = kb.get_knowledge_by_topic("math")
    assert len(math_knowledge) == 2


def test_complete_learning_workflow():
    """Test complete learning journey"""
    kb = KnowledgeBase()
    kb.register_agent("student_ai")

    # Create knowledge units for Python
    units = [
        KnowledgeUnit("py_1", KnowledgeType.FACTUAL, "python", "Python syntax basics"),
        KnowledgeUnit("py_2", KnowledgeType.PROCEDURAL, "python", "How to write a function"),
        KnowledgeUnit("py_3", KnowledgeType.CONCEPTUAL, "python", "Object-oriented programming"),
    ]

    for unit in units:
        kb.create_knowledge_unit(unit)

    # Agent learns the units
    for unit in units:
        kb.teach_agent("student_ai", unit.unit_id)

    # Agent practices and deepens knowledge
    kb.agent_uses_knowledge("student_ai", "py_1")
    kb.deepen_knowledge("student_ai", "py_1")
    kb.agent_uses_knowledge("student_ai", "py_2")
    kb.deepen_knowledge("student_ai", "py_2")
    kb.deepen_knowledge("student_ai", "py_2")  # Deep understanding

    # Teach learning strategies
    spaced_rep = LearningStrategy("strat_1", "student_ai", "Spaced Repetition", "Review at intervals")
    spaced_rep.effectiveness = 0.85
    kb.create_learning_strategy(spaced_rep)
    kb.teach_agent_strategy("student_ai", "strat_1")

    # Agent uses strategy
    kb.apply_strategy("student_ai", "strat_1")

    # Check expertise
    expertise = kb.get_agent_expertise("student_ai")
    assert expertise["total_knowledge_units"] == 3
    assert "python" in expertise["expertise_by_topic"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
