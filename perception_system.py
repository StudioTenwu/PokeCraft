"""
Perception System & Sensory Input for AICraft (Round 11).
Provides agents with sensory modalities, awareness, and perception filtering.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class PerceptionModality(Enum):
    """Types of sensory input an agent can perceive."""
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    PROPRIOCEPTIVE = "proprioceptive"  # Self-awareness
    TACTILE = "tactile"
    CHEMICAL = "chemical"  # Smell/taste


class PerceptionQuality(Enum):
    """Quality/resolution of perception."""
    RAW = 1
    BASIC = 2
    DETAILED = 3
    EXPERT = 4


@dataclass
class PerceptionEvent:
    """A single sensory event perceived by an agent."""
    event_id: str
    timestamp: datetime
    modality: PerceptionModality
    content: Any
    quality: PerceptionQuality = PerceptionQuality.BASIC
    processed: bool = False
    interpreted_as: Optional[str] = None
    emotional_response: Optional[float] = None
    attention_level: float = 0.5

    @staticmethod
    def create(event_type: PerceptionModality, content: Any, quality: PerceptionQuality = PerceptionQuality.BASIC) -> 'PerceptionEvent':
        """Factory method to create perception events."""
        return PerceptionEvent(
            event_id=f"perc_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            modality=event_type,
            content=content,
            quality=quality
        )

    def process(self, interpretation: str) -> bool:
        """Process the sensory event into an understanding."""
        if self.processed:
            return False
        self.processed = True
        self.interpreted_as = interpretation
        return True

    def set_emotional_response(self, response: float) -> bool:
        """Set emotional response to perception (-1.0 to 1.0)."""
        if not -1.0 <= response <= 1.0:
            return False
        self.emotional_response = response
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize perception event."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "modality": self.modality.name,
            "quality": self.quality.name,
            "processed": self.processed,
            "interpreted_as": self.interpreted_as,
            "emotional_response": self.emotional_response,
            "attention_level": self.attention_level
        }


class SensorySuite:
    """Collection of sensory capabilities an agent has."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.active_modalities: Dict[PerceptionModality, PerceptionQuality] = {
            PerceptionModality.TEXT: PerceptionQuality.DETAILED  # All agents start with text
        }
        self.perception_history: List[PerceptionEvent] = []
        self.sensory_acuity: Dict[PerceptionModality, float] = {
            PerceptionModality.TEXT: 0.8  # Start competent with text
        }
        self.created_at = datetime.now()

    def unlock_modality(self, modality: PerceptionModality, quality: PerceptionQuality = PerceptionQuality.BASIC) -> bool:
        """Unlock a new sensory modality."""
        if modality in self.active_modalities:
            return False

        self.active_modalities[modality] = quality
        self.sensory_acuity[modality] = 0.5  # Start at baseline
        return True

    def upgrade_modality(self, modality: PerceptionModality) -> bool:
        """Upgrade quality of existing modality."""
        if modality not in self.active_modalities:
            return False

        current_quality = self.active_modalities[modality]
        if current_quality == PerceptionQuality.EXPERT:
            return False

        next_quality = PerceptionQuality(current_quality.value + 1)
        self.active_modalities[modality] = next_quality
        return True

    def perceive(self, event: PerceptionEvent) -> bool:
        """Record a perception event."""
        if event.modality not in self.active_modalities:
            return False

        # Adjust quality based on acuity
        acuity = self.sensory_acuity.get(event.modality, 0.5)
        event.quality = PerceptionQuality(int(1 + acuity * 3))

        self.perception_history.append(event)
        return True

    def get_recent_perceptions(
        self, limit: int = 10,
        modality: Optional[PerceptionModality] = None
    ) -> List[PerceptionEvent]:
        """Get recent perceptions, optionally filtered by modality."""
        perceptions = self.perception_history
        if modality:
            perceptions = [p for p in perceptions if p.modality == modality]
        return perceptions[-limit:]

    def improve_acuity(self, modality: PerceptionModality, improvement: float) -> bool:
        """Improve sensory acuity through practice."""
        if modality not in self.active_modalities:
            return False

        current = self.sensory_acuity.get(modality, 0.5)
        new_acuity = min(1.0, current + improvement)
        self.sensory_acuity[modality] = new_acuity
        return True

    def get_perception_profile(self) -> Dict[str, Any]:
        """Get summary of perceptual capabilities."""
        return {
            "agent_id": self.agent_id,
            "active_modalities": {m.name: q.name for m, q in self.active_modalities.items()},
            "sensory_acuity": {m.name: a for m, a in self.sensory_acuity.items()},
            "perception_count": len(self.perception_history),
            "processed_count": sum(1 for p in self.perception_history if p.processed),
            "modality_count": len(self.active_modalities)
        }


class AwarenessModel:
    """Agent's understanding of self and surroundings."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.self_awareness: float = 0.2
        self.environmental_awareness: float = 0.3
        self.social_awareness: float = 0.2
        self.created_at = datetime.now()
        self.awareness_events: List[Dict[str, Any]] = []

    def learn_about_self(self, insight: str, importance: float = 0.5) -> bool:
        """Gain self-understanding."""
        if not 0.0 <= importance <= 1.0:
            return False

        self.self_awareness = min(1.0, self.self_awareness + importance * 0.1)
        self.awareness_events.append({
            "timestamp": datetime.now().isoformat(),
            "type": "self_insight",
            "insight": insight,
            "importance": importance
        })
        return True

    def learn_about_environment(self, observation: str, importance: float = 0.5) -> bool:
        """Develop environmental awareness."""
        if not 0.0 <= importance <= 1.0:
            return False

        self.environmental_awareness = min(1.0, self.environmental_awareness + importance * 0.15)
        self.awareness_events.append({
            "timestamp": datetime.now().isoformat(),
            "type": "environmental_observation",
            "observation": observation,
            "importance": importance
        })
        return True

    def learn_about_others(self, observation: str, importance: float = 0.5) -> bool:
        """Develop social awareness."""
        if not 0.0 <= importance <= 1.0:
            return False

        self.social_awareness = min(1.0, self.social_awareness + importance * 0.2)
        self.awareness_events.append({
            "timestamp": datetime.now().isoformat(),
            "type": "social_observation",
            "observation": observation,
            "importance": importance
        })
        return True

    def get_total_awareness(self) -> float:
        """Get overall awareness level (0.0-1.0)."""
        return (self.self_awareness + self.environmental_awareness + self.social_awareness) / 3.0

    def get_awareness_profile(self) -> Dict[str, Any]:
        """Get awareness metrics."""
        return {
            "agent_id": self.agent_id,
            "self_awareness": self.self_awareness,
            "environmental_awareness": self.environmental_awareness,
            "social_awareness": self.social_awareness,
            "total_awareness": self.get_total_awareness(),
            "awareness_events": len(self.awareness_events)
        }


class PerceptionFilter:
    """Filters and prioritizes perception based on agent state."""

    def __init__(self):
        self.focus_areas: List[str] = []
        self.ignore_patterns: List[str] = []
        self.attention_threshold: float = 0.3

    def add_focus_area(self, area: str) -> bool:
        """Focus on specific type of perception."""
        if area not in self.focus_areas:
            self.focus_areas.append(area)
            return True
        return False

    def add_ignore_pattern(self, pattern: str) -> bool:
        """Ignore certain perceptions."""
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            return True
        return False

    def should_attend_to(self, perception: PerceptionEvent) -> bool:
        """Decide if agent should attend to perception."""
        # Ignore if in ignore list
        if perception.interpreted_as and any(pattern in perception.interpreted_as for pattern in self.ignore_patterns):
            return False

        # Prioritize if in focus areas
        if perception.interpreted_as and any(area in perception.interpreted_as for area in self.focus_areas):
            return True

        # Otherwise use attention level
        return perception.attention_level >= self.attention_threshold

    def get_attended_perceptions(self, events: List[PerceptionEvent]) -> List[PerceptionEvent]:
        """Filter perceptions to those agent should attend to."""
        return [e for e in events if self.should_attend_to(e)]
