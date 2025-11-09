"""
Test suite for Perception System & Sensory Input (Round 11).
Tests agent perception capabilities, sensory input, and awareness mechanisms.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
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


class PerceptionEvent:
    """A single sensory event perceived by an agent."""

    def __init__(self, event_type: PerceptionModality, content: Any, quality: PerceptionQuality = PerceptionQuality.BASIC):
        self.event_id = f"perc_{datetime.now().timestamp()}"
        self.timestamp = datetime.now()
        self.modality = event_type
        self.content = content
        self.quality = quality
        self.processed = False
        self.interpreted_as: Optional[str] = None
        self.emotional_response: Optional[float] = None  # -1.0 to 1.0
        self.attention_level: float = 0.5  # How much attention this gets

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
            "emotional_response": self.emotional_response
        }


class SensorySuite:
    """Collection of sensory capabilities an agent has."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.active_modalities: Dict[PerceptionModality, PerceptionQuality] = {
            PerceptionModality.TEXT: PerceptionQuality.DETAILED  # All agents start with text
        }
        self.perception_history: List[PerceptionEvent] = []
        self.sensory_acuity: Dict[PerceptionModality, float] = {}  # 0.0-1.0

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

    def get_recent_perceptions(self, limit: int = 10, modality: Optional[PerceptionModality] = None) -> List[PerceptionEvent]:
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
            "processed_count": sum(1 for p in self.perception_history if p.processed)
        }


class AwarenessModel:
    """Agent's understanding of self and surroundings."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.self_awareness: float = 0.2  # How much agent understands itself
        self.environmental_awareness: float = 0.3  # Understanding of world
        self.social_awareness: float = 0.2  # Understanding of others
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


# ===== TESTS =====

def test_perception_modalities():
    """Test basic perception modalities."""
    assert PerceptionModality.TEXT.value == "text"
    assert PerceptionModality.VISION.value == "vision"
    assert len(PerceptionModality) == 6  # All 6 modalities


def test_perception_event_creation():
    """Test creating perception events."""
    event = PerceptionEvent(PerceptionModality.TEXT, "Hello world")
    assert event.modality == PerceptionModality.TEXT
    assert event.content == "Hello world"
    assert not event.processed


def test_perception_event_processing():
    """Test processing perception into understanding."""
    event = PerceptionEvent(PerceptionModality.TEXT, "The sun rises")
    assert not event.processed

    assert event.process("Natural phenomenon")
    assert event.processed
    assert event.interpreted_as == "Natural phenomenon"


def test_perception_emotional_response():
    """Test emotional response to perception."""
    event = PerceptionEvent(PerceptionModality.TEXT, "Great news!")

    assert event.set_emotional_response(0.8)
    assert event.emotional_response == 0.8

    assert not event.set_emotional_response(1.5)  # Out of bounds


def test_sensory_suite_initialization():
    """Test sensory suite starts with text perception."""
    suite = SensorySuite("agent_1")

    assert PerceptionModality.TEXT in suite.active_modalities
    assert suite.active_modalities[PerceptionModality.TEXT] == PerceptionQuality.DETAILED


def test_sensory_suite_unlock_modality():
    """Test unlocking new sensory modalities."""
    suite = SensorySuite("agent_1")

    assert suite.unlock_modality(PerceptionModality.VISION, PerceptionQuality.BASIC)
    assert PerceptionModality.VISION in suite.active_modalities

    # Can't unlock twice
    assert not suite.unlock_modality(PerceptionModality.VISION)


def test_sensory_suite_upgrade_modality():
    """Test upgrading sensory modality quality."""
    suite = SensorySuite("agent_1")
    suite.unlock_modality(PerceptionModality.VISION, PerceptionQuality.BASIC)

    assert suite.upgrade_modality(PerceptionModality.VISION)
    assert suite.active_modalities[PerceptionModality.VISION] == PerceptionQuality.DETAILED


def test_sensory_suite_perceive():
    """Test perceiving sensory events."""
    suite = SensorySuite("agent_1")
    event = PerceptionEvent(PerceptionModality.TEXT, "Test content")

    assert suite.perceive(event)
    assert len(suite.perception_history) == 1

    # Can't perceive with locked modality
    vision_event = PerceptionEvent(PerceptionModality.VISION, "Image")
    assert not suite.perceive(vision_event)


def test_perception_acuity_improvement():
    """Test improving sensory acuity."""
    suite = SensorySuite("agent_1")
    suite.unlock_modality(PerceptionModality.VISION)

    initial_acuity = suite.sensory_acuity[PerceptionModality.VISION]
    assert suite.improve_acuity(PerceptionModality.VISION, 0.2)
    assert suite.sensory_acuity[PerceptionModality.VISION] > initial_acuity


def test_awareness_model_self_awareness():
    """Test building self-awareness."""
    awareness = AwarenessModel("agent_1")
    initial = awareness.self_awareness

    assert awareness.learn_about_self("I can process language", 0.8)
    assert awareness.self_awareness > initial


def test_awareness_model_environmental_awareness():
    """Test building environmental awareness."""
    awareness = AwarenessModel("agent_1")

    assert awareness.learn_about_environment("The world has rules", 0.7)
    assert awareness.environmental_awareness > 0.3


def test_awareness_model_social_awareness():
    """Test building social awareness."""
    awareness = AwarenessModel("agent_1")

    assert awareness.learn_about_others("Others have perspectives", 0.9)
    assert awareness.social_awareness > 0.2


def test_total_awareness_calculation():
    """Test calculating total awareness."""
    awareness = AwarenessModel("agent_1")

    awareness.learn_about_self("insight", 0.5)
    awareness.learn_about_environment("observation", 0.5)
    awareness.learn_about_others("social", 0.5)

    total = awareness.get_total_awareness()
    assert 0.0 <= total <= 1.0
    assert total > 0.3  # Should be higher than initial


def test_perception_filter_focus():
    """Test perception filter with focus areas."""
    filter = PerceptionFilter()
    filter.add_focus_area("danger")

    event = PerceptionEvent(PerceptionModality.TEXT, "Warning")
    event.process("danger alert")

    assert filter.should_attend_to(event)


def test_perception_filter_ignore():
    """Test perception filter with ignore patterns."""
    filter = PerceptionFilter()
    filter.add_ignore_pattern("noise")

    event = PerceptionEvent(PerceptionModality.TEXT, "Background noise")
    event.process("noise background")

    assert not filter.should_attend_to(event)


def test_perception_filter_attention_threshold():
    """Test attention threshold filtering."""
    filter = PerceptionFilter()
    filter.attention_threshold = 0.7

    low_attention_event = PerceptionEvent(PerceptionModality.TEXT, "content")
    low_attention_event.attention_level = 0.5

    assert not filter.should_attend_to(low_attention_event)

    high_attention_event = PerceptionEvent(PerceptionModality.TEXT, "content")
    high_attention_event.attention_level = 0.8

    assert filter.should_attend_to(high_attention_event)


def test_perception_profile():
    """Test getting perception profile."""
    suite = SensorySuite("agent_1")
    suite.unlock_modality(PerceptionModality.VISION)

    event = PerceptionEvent(PerceptionModality.TEXT, "content")
    event.process("interpretation")
    suite.perceive(event)

    profile = suite.get_perception_profile()
    assert profile["agent_id"] == "agent_1"
    assert profile["perception_count"] == 1
    assert profile["processed_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
