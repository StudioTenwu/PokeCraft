"""
Agent memory and learning system for AICraft.

Provides:
- Episodic memory (event-based experiences)
- Semantic memory (facts and concepts)
- Memory consolidation and decay
- Integration with agent learning and personality
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid


class MemoryType(Enum):
    """Classification of memory types."""
    EPISODIC = "episodic"      # Event-based, time-stamped
    SEMANTIC = "semantic"       # Facts, concepts, knowledge
    PROCEDURAL = "procedural"   # Skills, how-to knowledge


@dataclass
class Memory:
    """A single memory entry."""
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    agent_id: str
    relevance_score: float = 1.0  # Decreases over time
    tags: List[str] = field(default_factory=list)
    associated_emotions: List[str] = field(default_factory=list)
    access_count: int = 0

    def __post_init__(self):
        """Validate relevance score."""
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))

    def decay(self, days_passed: int) -> None:
        """Memory fades over time with exponential decay."""
        decay_factor = 0.95 ** days_passed
        self.relevance_score = max(0.1, self.relevance_score * decay_factor)

    def access(self) -> None:
        """Record a memory access and boost relevance."""
        self.access_count += 1
        # Frequently accessed memories remain vivid
        self.relevance_score = min(1.0, self.relevance_score + 0.05)

    def add_emotion(self, emotion: str) -> None:
        """Associate an emotion with this memory."""
        if emotion not in self.associated_emotions:
            self.associated_emotions.append(emotion)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dictionary."""
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "relevance_score": self.relevance_score,
            "tags": self.tags,
            "associated_emotions": self.associated_emotions,
            "access_count": self.access_count
        }


class MemoryStore:
    """Stores and manages agent memories."""

    def __init__(self, agent_id: str, max_short_term: int = 10):
        self.agent_id = agent_id
        self.episodic_memories: List[Memory] = []
        self.semantic_memories: Dict[str, Any] = {}
        self.procedural_memories: Dict[str, Any] = {}
        self.short_term_buffer: List[Memory] = []
        self.max_short_term = max_short_term
        self.consolidation_threshold = 5  # Times accessed before consolidation
        self.created_at = datetime.now()

    def add_memory(self, memory: Memory) -> None:
        """Add a memory to the store."""
        if memory.memory_type == MemoryType.EPISODIC:
            self.add_episodic_memory(memory)
        elif memory.memory_type == MemoryType.SEMANTIC:
            self.add_semantic_memory(memory.content.get("key", ""), memory.content)
        elif memory.memory_type == MemoryType.PROCEDURAL:
            self.add_procedural_memory(memory.content.get("skill", ""), memory.content)

    def add_episodic_memory(self, memory: Memory) -> None:
        """Add an episodic memory (event-based)."""
        if memory.memory_type != MemoryType.EPISODIC:
            memory.memory_type = MemoryType.EPISODIC

        self.episodic_memories.append(memory)
        self.short_term_buffer.append(memory)

        # Keep short-term buffer at max size (FIFO)
        if len(self.short_term_buffer) > self.max_short_term:
            self.short_term_buffer.pop(0)

    def add_semantic_memory(self, key: str, value: Any) -> None:
        """Add semantic memory (facts/concepts)."""
        self.semantic_memories[key] = {
            "value": value,
            "access_count": 0,
            "first_learned": datetime.now(),
            "last_accessed": datetime.now()
        }

    def add_procedural_memory(self, skill: str, procedure: Dict[str, Any]) -> None:
        """Add procedural memory (how-to knowledge)."""
        self.procedural_memories[skill] = {
            "procedure": procedure,
            "proficiency": 0.5,  # 0.0-1.0
            "times_practiced": 0,
            "learned_at": datetime.now()
        }

    def recall_episodic(self, query: str = "", tags: Optional[List[str]] = None) -> List[Memory]:
        """Search episodic memories by query or tags."""
        results = []

        for memory in self.episodic_memories:
            match = False

            # Match by tags
            if tags:
                if any(tag.lower() in [t.lower() for t in memory.tags] for tag in tags):
                    match = True

            # Match by query in content
            if query and query.lower() in str(memory.content).lower():
                match = True

            # Match by query in tags
            if query and query.lower() in [t.lower() for t in memory.tags]:
                match = True

            if match:
                memory.access()  # Record access
                results.append(memory)

        # Sort by relevance
        return sorted(results, key=lambda m: m.relevance_score, reverse=True)

    def recall_semantic(self, key: str) -> Optional[Any]:
        """Retrieve semantic memory."""
        if key in self.semantic_memories:
            entry = self.semantic_memories[key]
            entry["access_count"] += 1
            entry["last_accessed"] = datetime.now()
            return entry["value"]
        return None

    def recall_procedural(self, skill: str) -> Optional[Dict[str, Any]]:
        """Retrieve procedural memory (skill/procedure)."""
        if skill in self.procedural_memories:
            entry = self.procedural_memories[skill]
            entry["times_practiced"] += 1
            return entry["procedure"]
        return None

    def practice_skill(self, skill: str, success: bool) -> None:
        """Update proficiency based on practice."""
        if skill in self.procedural_memories:
            entry = self.procedural_memories[skill]
            entry["times_practiced"] += 1

            # Improve proficiency on success
            if success:
                entry["proficiency"] = min(1.0, entry["proficiency"] + 0.05)

    def get_short_term_memories(self) -> List[Memory]:
        """Get current short-term memory buffer."""
        return self.short_term_buffer.copy()

    def consolidate_memories(self) -> None:
        """Consolidate episodic memories into semantic knowledge."""
        for memory in self.episodic_memories:
            for tag in memory.tags:
                # Extract semantic knowledge from episodic experiences
                key = f"{tag}_experiences"

                if key not in self.semantic_memories:
                    self.semantic_memories[key] = {
                        "value": [],
                        "access_count": 0,
                        "first_learned": datetime.now(),
                        "last_accessed": datetime.now()
                    }

                # Add to experiences list
                if isinstance(self.semantic_memories[key]["value"], list):
                    self.semantic_memories[key]["value"].append(memory.content)

    def apply_memory_decay(self) -> None:
        """Apply decay to all episodic memories."""
        now = datetime.now()
        for memory in self.episodic_memories:
            days_passed = (now - memory.timestamp).days
            if days_passed > 0:
                memory.decay(days_passed)

    def forget_old_memories(self, days_threshold: int = 30, min_relevance: float = 0.3) -> int:
        """Remove very old memories with low relevance."""
        now = datetime.now()
        original_count = len(self.episodic_memories)

        self.episodic_memories = [
            m for m in self.episodic_memories
            if (now - m.timestamp).days < days_threshold or m.relevance_score > min_relevance
        ]

        forgotten = original_count - len(self.episodic_memories)
        return forgotten

    def search_memories(self, query: str) -> Dict[str, List]:
        """Search across all memory types."""
        return {
            "episodic": self.recall_episodic(query),
            "semantic": [
                (k, v["value"]) for k, v in self.semantic_memories.items()
                if query.lower() in k.lower() or query.lower() in str(v["value"]).lower()
            ],
            "procedural": [
                (k, v["procedure"]) for k, v in self.procedural_memories.items()
                if query.lower() in k.lower()
            ]
        }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "episodic": len(self.episodic_memories),
            "semantic": len(self.semantic_memories),
            "procedural": len(self.procedural_memories),
            "short_term": len(self.short_term_buffer),
            "total_accesses": sum(m.access_count for m in self.episodic_memories),
            "average_relevance": (
                sum(m.relevance_score for m in self.episodic_memories) / len(self.episodic_memories)
                if self.episodic_memories else 0.0
            )
        }

    def get_memory_report(self) -> str:
        """Generate a report of memory state."""
        stats = self.get_memory_stats()
        report = f"\n**Memory Report for Agent {self.agent_id}:**\n"
        report += f"- Episodic memories: {stats['episodic']}\n"
        report += f"- Semantic knowledge: {stats['semantic']}\n"
        report += f"- Skills learned: {stats['procedural']}\n"
        report += f"- Current focus (short-term): {stats['short_term']}\n"
        report += f"- Avg memory strength: {stats['average_relevance']:.1%}\n"

        # Most recent memories
        if self.short_term_buffer:
            report += f"\nRecent focus:\n"
            for mem in self.short_term_buffer[-3:]:
                report += f"  - {', '.join(mem.tags) if mem.tags else 'untagged'}\n"

        return report

    def export_memories(self) -> Dict[str, Any]:
        """Export all memories for persistence."""
        return {
            "agent_id": self.agent_id,
            "episodic": [m.to_dict() for m in self.episodic_memories],
            "semantic": self.semantic_memories,
            "procedural": self.procedural_memories,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def import_memories(cls, data: Dict[str, Any]) -> 'MemoryStore':
        """Import memories from exported data."""
        store = cls(data["agent_id"])

        # Restore episodic memories
        for mem_data in data.get("episodic", []):
            mem = Memory(
                memory_id=mem_data["memory_id"],
                memory_type=MemoryType(mem_data["memory_type"]),
                content=mem_data["content"],
                timestamp=datetime.fromisoformat(mem_data["timestamp"]),
                agent_id=mem_data["agent_id"],
                relevance_score=mem_data["relevance_score"],
                tags=mem_data["tags"],
                associated_emotions=mem_data["associated_emotions"],
                access_count=mem_data["access_count"]
            )
            store.add_episodic_memory(mem)

        # Restore semantic and procedural memories
        store.semantic_memories = data.get("semantic", {})
        store.procedural_memories = data.get("procedural", {})

        return store
