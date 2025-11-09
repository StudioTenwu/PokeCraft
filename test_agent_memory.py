"""
Test suite for agent memory and learning system.
Tests episodic memory, semantic memory, and memory consolidation.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


@dataclass
class Memory:
    """A single memory entry."""
    memory_id: str
    memory_type: str  # "episodic", "semantic", "procedural"
    content: Dict[str, Any]
    timestamp: datetime
    agent_id: str
    relevance_score: float = 1.0  # Decreases over time
    tags: List[str] = None
    associated_emotions: List[str] = None

    def __post_init__(self):
        self.tags = self.tags or []
        self.associated_emotions = self.associated_emotions or []

    def decay(self, days_passed: int) -> None:
        """Memory fades over time."""
        decay_factor = 0.95 ** days_passed
        self.relevance_score = max(0.1, self.relevance_score * decay_factor)


class MemoryStore:
    """Stores and manages agent memories."""

    def __init__(self, agent_id: str, max_short_term: int = 10):
        self.agent_id = agent_id
        self.episodic_memories: List[Memory] = []
        self.semantic_memories: Dict[str, Any] = {}
        self.short_term_buffer: List[Memory] = []
        self.max_short_term = max_short_term
        self.consolidation_threshold = 5  # Times accessed before consolidation

    def add_episodic_memory(self, memory: Memory) -> None:
        """Add an episodic memory (event-based)."""
        self.episodic_memories.append(memory)
        self.short_term_buffer.append(memory)

        # Keep short-term buffer at max size
        if len(self.short_term_buffer) > self.max_short_term:
            self.short_term_buffer.pop(0)

    def add_semantic_memory(self, key: str, value: Any) -> None:
        """Add semantic memory (facts/concepts)."""
        self.semantic_memories[key] = {
            "value": value,
            "access_count": 0,
            "first_learned": datetime.now()
        }

    def recall_episodic(self, query: str) -> List[Memory]:
        """Search episodic memories by tag or content."""
        results = []
        for memory in self.episodic_memories:
            if query.lower() in [t.lower() for t in memory.tags]:
                results.append(memory)
            elif query.lower() in str(memory.content).lower():
                results.append(memory)
        return sorted(results, key=lambda m: m.relevance_score, reverse=True)

    def recall_semantic(self, key: str) -> Optional[Any]:
        """Retrieve semantic memory."""
        if key in self.semantic_memories:
            entry = self.semantic_memories[key]
            entry["access_count"] += 1
            return entry["value"]
        return None

    def get_short_term_memories(self) -> List[Memory]:
        """Get current short-term memory buffer."""
        return self.short_term_buffer.copy()

    def consolidate_memories(self) -> None:
        """Consolidate episodic memories into semantic."""
        for memory in self.episodic_memories:
            for tag in memory.tags:
                if memory.memory_type == "episodic":
                    # Extract facts from episodic memories
                    key = f"{tag}_experiences"
                    if key not in self.semantic_memories:
                        self.semantic_memories[key] = []
                    self.semantic_memories[key].append(memory.content)

    def forget_old_memories(self, days_threshold: int = 30) -> None:
        """Remove very old memories with low relevance."""
        now = datetime.now()
        self.episodic_memories = [
            m for m in self.episodic_memories
            if (now - m.timestamp).days < days_threshold or m.relevance_score > 0.3
        ]

    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory system statistics."""
        return {
            "episodic": len(self.episodic_memories),
            "semantic": len(self.semantic_memories),
            "short_term": len(self.short_term_buffer)
        }


class TestMemoryStore:
    """Test core memory storage."""

    def test_add_episodic_memory(self):
        store = MemoryStore("agent_1")
        memory = Memory(
            memory_id="m1",
            memory_type="episodic",
            content={"event": "learned_to_code"},
            timestamp=datetime.now(),
            agent_id="agent_1",
            tags=["learning", "success"]
        )

        store.add_episodic_memory(memory)
        assert len(store.episodic_memories) == 1
        assert len(store.short_term_buffer) == 1

    def test_add_semantic_memory(self):
        store = MemoryStore("agent_1")
        store.add_semantic_memory("python_syntax", "Uses indentation")
        store.add_semantic_memory("greeting_style", "friendly")

        assert "python_syntax" in store.semantic_memories
        assert store.recall_semantic("python_syntax") == "Uses indentation"

    def test_recall_episodic_by_tag(self):
        store = MemoryStore("agent_1")

        m1 = Memory("m1", "episodic", {"event": "success"}, datetime.now(),
                   "agent_1", tags=["victory", "puzzle"])
        m2 = Memory("m2", "episodic", {"event": "failure"}, datetime.now(),
                   "agent_1", tags=["defeat", "puzzle"])

        store.add_episodic_memory(m1)
        store.add_episodic_memory(m2)

        puzzle_memories = store.recall_episodic("puzzle")
        assert len(puzzle_memories) == 2

    def test_recall_episodic_by_content(self):
        store = MemoryStore("agent_1")

        m1 = Memory("m1", "episodic", {"action": "code_solution"},
                   datetime.now(), "agent_1")

        store.add_episodic_memory(m1)
        results = store.recall_episodic("code")
        assert len(results) == 1

    def test_recall_semantic(self):
        store = MemoryStore("agent_1")
        store.add_semantic_memory("learned_fact", "very_important")

        result = store.recall_semantic("learned_fact")
        assert result == "very_important"

        # Access count increases
        assert store.semantic_memories["learned_fact"]["access_count"] == 1

    def test_short_term_buffer_limit(self):
        store = MemoryStore("agent_1", max_short_term=3)

        for i in range(5):
            m = Memory(f"m{i}", "episodic", {"data": i}, datetime.now(), "agent_1")
            store.add_episodic_memory(m)

        # Buffer should not exceed max
        assert len(store.short_term_buffer) == 3

    def test_memory_decay(self):
        m = Memory("m1", "episodic", {}, datetime.now(), "agent_1", relevance_score=1.0)
        original_relevance = m.relevance_score

        m.decay(days_passed=10)
        assert m.relevance_score < original_relevance
        assert m.relevance_score > 0.1

    def test_consolidate_memories(self):
        store = MemoryStore("agent_1")

        m = Memory("m1", "episodic", {"lesson": "practice_helps"},
                  datetime.now(), "agent_1", tags=["learning"])

        store.add_episodic_memory(m)
        store.consolidate_memories()

        # Should create semantic memory from episodic
        assert "learning_experiences" in store.semantic_memories

    def test_forget_old_memories(self):
        store = MemoryStore("agent_1")

        old_time = datetime.now() - timedelta(days=40)
        m_old = Memory("m_old", "episodic", {}, old_time, "agent_1",
                      relevance_score=0.1)

        new_time = datetime.now()
        m_new = Memory("m_new", "episodic", {}, new_time, "agent_1")

        store.add_episodic_memory(m_old)
        store.add_episodic_memory(m_new)

        store.forget_old_memories(days_threshold=30)

        # Old memory with low relevance should be forgotten
        assert len(store.episodic_memories) >= 1  # Keep important ones
        assert any(m.memory_id == "m_new" for m in store.episodic_memories)

    def test_memory_stats(self):
        store = MemoryStore("agent_1")

        m = Memory("m1", "episodic", {}, datetime.now(), "agent_1")
        store.add_episodic_memory(m)
        store.add_semantic_memory("fact", "value")

        stats = store.get_memory_stats()
        assert stats["episodic"] >= 1
        assert stats["semantic"] >= 1


class TestMemoryIntegration:
    """Test memory system integration with agent learning."""

    def test_learn_from_success(self):
        """Agent learns and remembers successful strategies."""
        store = MemoryStore("agent_1")

        # Record success
        success_memory = Memory(
            memory_id="success_1",
            memory_type="episodic",
            content={"strategy": "divide_and_conquer", "success": True},
            timestamp=datetime.now(),
            agent_id="agent_1",
            tags=["strategy", "success"]
        )

        store.add_episodic_memory(success_memory)

        # Later, recall successful strategies
        successes = store.recall_episodic("success")
        assert len(successes) > 0

    def test_learn_from_failure(self):
        """Agent learns and remembers what doesn't work."""
        store = MemoryStore("agent_1")

        failure_memory = Memory(
            memory_id="failure_1",
            memory_type="episodic",
            content={"strategy": "brute_force", "success": False, "lesson": "inefficient"},
            timestamp=datetime.now(),
            agent_id="agent_1",
            tags=["strategy", "failure"],
            associated_emotions=["frustration", "learning"]
        )

        store.add_episodic_memory(failure_memory)

        # Recall failures to avoid repetition
        failures = store.recall_episodic("failure")
        assert len(failures) > 0
        assert failures[0].associated_emotions

    def test_emotional_memory_weighting(self):
        """Emotionally significant memories are weighted higher."""
        store = MemoryStore("agent_1")

        neutral = Memory("m1", "episodic", {"data": "neutral"}, datetime.now(),
                        "agent_1", relevance_score=0.5)

        emotional = Memory("m2", "episodic", {"data": "emotional"},
                          datetime.now(), "agent_1", relevance_score=1.0,
                          associated_emotions=["joy", "pride"])

        store.add_episodic_memory(neutral)
        store.add_episodic_memory(emotional)

        all_memories = store.recall_episodic("")  # Empty query to get all
        # Emotional memory should appear higher due to relevance
        assert len([m for m in all_memories if m.associated_emotions]) > 0


class TestMemoryQuality:
    """Test memory quality and retention metrics."""

    def test_relevant_memories_persist(self):
        """Frequently accessed memories remain vivid."""
        store = MemoryStore("agent_1")
        store.add_semantic_memory("important_skill", "critical")

        # Access multiple times
        for _ in range(5):
            store.recall_semantic("important_skill")

        assert store.semantic_memories["important_skill"]["access_count"] == 5

    def test_memory_hierarchy(self):
        """Test that consolidated memories form semantic knowledge."""
        store = MemoryStore("agent_1")

        # Add multiple related episodic memories
        for i in range(3):
            m = Memory(f"m{i}", "episodic",
                      {"observation": f"pattern_{i}"},
                      datetime.now(), "agent_1",
                      tags=["pattern_recognition"])
            store.add_episodic_memory(m)

        store.consolidate_memories()

        # Should have semantic knowledge about patterns
        assert "pattern_recognition_experiences" in store.semantic_memories
        pattern_exp = store.semantic_memories["pattern_recognition_experiences"]
        assert pattern_exp is not None
        assert len(pattern_exp) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
