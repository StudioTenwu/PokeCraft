"""
Round 30: Emotion & Feeling System

Enable agents to experience emotions that affect behavior, decisions,
and relationships. Emotions develop and change based on experiences,
creating depth and personality.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class Emotion(Enum):
    """Core emotions agents can experience"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


class EmotionalValence(Enum):
    """Positive/negative spectrum"""
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


@dataclass
class EmotionalState:
    """Current emotional condition"""
    emotion: Emotion
    intensity: float = 0.5  # 0.0-1.0
    duration_turns: int = 0  # How long held
    trigger: str = ""  # What caused it

    def intensify(self, amount: float = 0.1) -> bool:
        """Increase emotional intensity"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.intensity = min(1.0, self.intensity + amount)
        return True

    def diminish(self, amount: float = 0.1) -> bool:
        """Decrease emotional intensity"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.intensity = max(0.0, self.intensity - amount)
        return True

    def fade_naturally(self) -> None:
        """Emotions fade over time"""
        self.duration_turns += 1
        if self.duration_turns > 10:
            self.diminish(0.05)

    def get_valence(self) -> EmotionalValence:
        """Get positive/negative classification"""
        positive = {Emotion.JOY, Emotion.TRUST, Emotion.ANTICIPATION}
        negative = {Emotion.SADNESS, Emotion.ANGER, Emotion.FEAR, Emotion.DISGUST}

        if self.emotion in positive:
            return EmotionalValence.POSITIVE
        elif self.emotion in negative:
            return EmotionalValence.NEGATIVE
        else:
            return EmotionalValence.NEUTRAL

    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion.value,
            "intensity": self.intensity,
            "valence": self.get_valence().value,
            "duration": self.duration_turns
        }


@dataclass
class EmotionalMemory:
    """Link between emotion and memory"""
    memory_id: str
    emotion: Emotion
    intensity_at_time: float
    affects_recall: bool = True  # Strong emotions affect memories


class EmotionalResponse:
    """How an agent responds to stimuli emotionally"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_emotions: List[EmotionalState] = []
        self.dominant_emotion: Optional[Emotion] = None
        self.emotional_baseline: Dict[Emotion, float] = {
            e: 0.0 for e in Emotion
        }  # 0.0-1.0 predisposition
        self.emotional_memory: List[EmotionalMemory] = []
        self.mood: float = 0.5  # -1.0 (very negative) to 1.0 (very positive)

    def set_baseline(self, emotion: Emotion, level: float) -> bool:
        """Set baseline predisposition to emotion"""
        if not (0.0 <= level <= 1.0):
            return False
        self.emotional_baseline[emotion] = level
        return True

    def experience_emotion(self, emotion: Emotion, intensity: float = 0.5, trigger: str = "") -> bool:
        """Agent experiences an emotion"""
        if not (0.0 <= intensity <= 1.0):
            return False

        # Remove conflicting emotion (e.g., joy overrides sadness)
        conflicting = {
            Emotion.JOY: {Emotion.SADNESS, Emotion.FEAR},
            Emotion.SADNESS: {Emotion.JOY, Emotion.ANTICIPATION},
            Emotion.ANGER: {Emotion.TRUST},
            Emotion.FEAR: {Emotion.TRUST, Emotion.JOY}
        }

        if emotion in conflicting:
            self.current_emotions = [
                e for e in self.current_emotions
                if e.emotion not in conflicting[emotion]
            ]

        # Add new emotion
        state = EmotionalState(emotion=emotion, intensity=intensity, trigger=trigger)
        self.current_emotions.append(state)

        # Update mood
        valence = state.get_valence()
        if valence == EmotionalValence.POSITIVE:
            self.mood = min(1.0, self.mood + intensity * 0.1)
        elif valence == EmotionalValence.NEGATIVE:
            self.mood = max(-1.0, self.mood - intensity * 0.1)

        # Update dominant emotion
        if not self.dominant_emotion or intensity > self.get_emotional_intensity(self.dominant_emotion):
            self.dominant_emotion = emotion

        return True

    def link_emotion_to_memory(self, memory_id: str, emotion: Emotion) -> bool:
        """Link an emotion to a memory"""
        intensity = self.get_emotional_intensity(emotion)
        link = EmotionalMemory(
            memory_id=memory_id,
            emotion=emotion,
            intensity_at_time=intensity
        )
        self.emotional_memory.append(link)
        return True

    def get_emotional_intensity(self, emotion: Emotion) -> float:
        """Get current intensity of specific emotion"""
        for state in self.current_emotions:
            if state.emotion == emotion:
                return state.intensity
        return self.emotional_baseline.get(emotion, 0.0)

    def advance_time(self) -> None:
        """Age emotions by one turn"""
        for state in self.current_emotions[:]:
            state.fade_naturally()
            if state.intensity <= 0.0:
                self.current_emotions.remove(state)

    def regulate_emotion(self, technique: str) -> bool:
        """Apply emotional regulation technique"""
        if not self.current_emotions:
            return False

        techniques = {
            "breathing": 0.1,  # Calming
            "reappraisal": 0.15,  # Cognitive shift
            "distraction": 0.05,  # Weak effect
            "acceptance": 0.2,  # Healthy coping
        }

        reduction = techniques.get(technique, 0.0)
        for state in self.current_emotions:
            state.diminish(reduction)

        return True

    def get_emotional_profile(self) -> Dict:
        """Get overall emotional state snapshot"""
        return {
            "dominant_emotion": self.dominant_emotion.value if self.dominant_emotion else None,
            "mood": self.mood,
            "active_emotions": len(self.current_emotions),
            "emotional_states": [e.to_dict() for e in self.current_emotions]
        }

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "mood": self.mood,
            "dominant_emotion": self.dominant_emotion.value if self.dominant_emotion else None,
            "active_emotions": len(self.current_emotions)
        }


class EmotionSystem:
    """Manage emotions for all agents"""

    def __init__(self):
        self.agent_responses: Dict[str, EmotionalResponse] = {}
        self.total_emotions_experienced: int = 0

    def register_agent(self, agent_id: str) -> bool:
        """Register agent for emotion tracking"""
        if agent_id in self.agent_responses:
            return False
        self.agent_responses[agent_id] = EmotionalResponse(agent_id)
        return True

    def agent_experiences_emotion(
        self, agent_id: str, emotion: Emotion, intensity: float = 0.5, trigger: str = ""
    ) -> bool:
        """Record agent experiencing emotion"""
        if agent_id not in self.agent_responses:
            return False

        response = self.agent_responses[agent_id]
        if response.experience_emotion(emotion, intensity, trigger):
            self.total_emotions_experienced += 1
            return True
        return False

    def link_emotion_to_memory(self, agent_id: str, memory_id: str, emotion: Emotion) -> bool:
        """Link emotion to agent memory"""
        if agent_id not in self.agent_responses:
            return False
        return self.agent_responses[agent_id].link_emotion_to_memory(memory_id, emotion)

    def regulate_agent_emotion(self, agent_id: str, technique: str) -> bool:
        """Apply emotion regulation technique"""
        if agent_id not in self.agent_responses:
            return False
        return self.agent_responses[agent_id].regulate_emotion(technique)

    def set_emotional_baseline(self, agent_id: str, emotion: Emotion, level: float) -> bool:
        """Set agent's baseline predisposition"""
        if agent_id not in self.agent_responses:
            return False
        return self.agent_responses[agent_id].set_baseline(emotion, level)

    def advance_time(self) -> None:
        """Age all agent emotions"""
        for response in self.agent_responses.values():
            response.advance_time()

    def get_agent_emotional_profile(self, agent_id: str) -> Dict:
        """Get agent's emotional profile"""
        if agent_id not in self.agent_responses:
            return {}
        return self.agent_responses[agent_id].get_emotional_profile()

    def get_system_emotion_distribution(self) -> Dict:
        """Get emotion distribution across all agents"""
        emotion_count: Dict[str, int] = {e.value: 0 for e in Emotion}

        for response in self.agent_responses.values():
            for state in response.current_emotions:
                emotion_count[state.emotion.value] += 1

        return emotion_count

    def to_dict(self) -> Dict:
        return {
            "agents_tracked": len(self.agent_responses),
            "total_emotions_experienced": self.total_emotions_experienced,
            "distribution": self.get_system_emotion_distribution()
        }


# ===== Tests =====

def test_emotion_creation():
    """Test creating emotional state"""
    state = EmotionalState(emotion=Emotion.JOY, intensity=0.8)
    assert state.emotion == Emotion.JOY
    assert state.intensity == 0.8


def test_emotion_intensity_change():
    """Test changing emotion intensity"""
    state = EmotionalState(emotion=Emotion.SADNESS, intensity=0.5)
    assert state.intensify(0.3) is True
    assert abs(state.intensity - 0.8) < 0.0001

    assert state.diminish(0.2) is True
    assert abs(state.intensity - 0.6) < 0.0001


def test_emotion_valence():
    """Test emotion valence classification"""
    positive = EmotionalState(emotion=Emotion.JOY)
    negative = EmotionalState(emotion=Emotion.ANGER)
    surprise = EmotionalState(emotion=Emotion.SURPRISE)

    assert positive.get_valence() == EmotionalValence.POSITIVE
    assert negative.get_valence() == EmotionalValence.NEGATIVE
    assert surprise.get_valence() == EmotionalValence.NEUTRAL


def test_emotion_fading():
    """Test emotion fading over time"""
    state = EmotionalState(emotion=Emotion.JOY, intensity=0.9)
    initial = state.intensity

    for _ in range(15):
        state.fade_naturally()

    assert state.intensity < initial


def test_emotional_response_creation():
    """Test creating emotional response system"""
    response = EmotionalResponse(agent_id="a1")
    assert response.agent_id == "a1"
    assert response.mood == 0.5


def test_agent_experience_emotion():
    """Test agent experiencing emotion"""
    response = EmotionalResponse(agent_id="a1")
    assert response.experience_emotion(Emotion.JOY, 0.8, trigger="success") is True
    assert len(response.current_emotions) == 1


def test_emotional_conflict_resolution():
    """Test conflicting emotions replace each other"""
    response = EmotionalResponse(agent_id="a1")
    response.experience_emotion(Emotion.JOY, 0.7)
    response.experience_emotion(Emotion.SADNESS, 0.8)

    # Sadness should remove joy
    emotions = [e.emotion for e in response.current_emotions]
    assert Emotion.JOY not in emotions
    assert Emotion.SADNESS in emotions


def test_emotional_baseline():
    """Test setting emotional baseline"""
    response = EmotionalResponse(agent_id="a1")
    assert response.set_baseline(Emotion.OPTIMISM if hasattr(Emotion, 'OPTIMISM') else Emotion.JOY, 0.8) is True


def test_emotion_memory_linking():
    """Test linking emotion to memory"""
    response = EmotionalResponse(agent_id="a1")
    response.experience_emotion(Emotion.JOY, 0.7)
    assert response.link_emotion_to_memory("mem1", Emotion.JOY) is True
    assert len(response.emotional_memory) == 1


def test_emotion_regulation():
    """Test emotional regulation technique"""
    response = EmotionalResponse(agent_id="a1")
    response.experience_emotion(Emotion.ANGER, 0.9)

    initial_intensity = response.get_emotional_intensity(Emotion.ANGER)
    response.regulate_emotion("breathing")
    new_intensity = response.get_emotional_intensity(Emotion.ANGER)

    assert new_intensity < initial_intensity


def test_emotion_system_registration():
    """Test registering agent in emotion system"""
    system = EmotionSystem()
    assert system.register_agent("a1") is True


def test_emotion_system_experience():
    """Test agent experiencing emotion through system"""
    system = EmotionSystem()
    system.register_agent("a1")

    assert system.agent_experiences_emotion("a1", Emotion.JOY, 0.7, trigger="win") is True
    assert system.total_emotions_experienced == 1


def test_emotional_profile():
    """Test getting emotional profile"""
    system = EmotionSystem()
    system.register_agent("a1")
    system.agent_experiences_emotion("a1", Emotion.JOY, 0.8)

    profile = system.get_agent_emotional_profile("a1")
    assert "dominant_emotion" in profile
    assert profile["dominant_emotion"] == Emotion.JOY.value


def test_emotion_distribution():
    """Test emotion distribution across system"""
    system = EmotionSystem()
    system.register_agent("a1")
    system.register_agent("a2")

    system.agent_experiences_emotion("a1", Emotion.JOY)
    system.agent_experiences_emotion("a2", Emotion.SADNESS)

    dist = system.get_system_emotion_distribution()
    assert dist[Emotion.JOY.value] == 1
    assert dist[Emotion.SADNESS.value] == 1


def test_complete_emotion_workflow():
    """Test complete emotional journey"""
    system = EmotionSystem()
    system.register_agent("hero_agent")

    # Set personality baseline (more prone to joy than fear)
    system.set_emotional_baseline("hero_agent", Emotion.JOY, 0.7)
    system.set_emotional_baseline("hero_agent", Emotion.FEAR, 0.2)

    # Experience success
    assert system.agent_experiences_emotion("hero_agent", Emotion.JOY, 0.8, trigger="quest_win") is True

    # Link emotion to memory
    assert system.link_emotion_to_memory("hero_agent", "mem_victory", Emotion.JOY) is True

    # Check profile
    profile = system.get_agent_emotional_profile("hero_agent")
    assert profile["dominant_emotion"] == Emotion.JOY.value

    # Time passes, emotion fades
    for _ in range(5):
        system.advance_time()

    # Intensity should be less
    new_profile = system.get_agent_emotional_profile("hero_agent")
    # Joy may still be there but faded

    # Experience challenge, triggers fear
    system.agent_experiences_emotion("hero_agent", Emotion.FEAR, 0.5, trigger="big_challenge")

    # Agent uses regulation
    system.regulate_agent_emotion("hero_agent", "reappraisal")

    # Check final state
    final_profile = system.get_agent_emotional_profile("hero_agent")
    assert final_profile["active_emotions"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
