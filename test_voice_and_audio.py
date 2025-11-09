"""
Round 37: Audio and Voice Design

Enable agents to express themselves through voice that reflects personality,
emotion, speech patterns, and emotional states. Audio brings agents to life.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class VoiceType(Enum):
    """Base voice archetypes"""
    CHILD = "child"  # Young, innocent, curious
    ADULT = "adult"  # Mature, thoughtful
    DIGITAL = "digital"  # Electronic, synthetic
    ETHEREAL = "ethereal"  # Floating, dreamy
    GRUFF = "gruff"  # Deep, rough
    BRIGHT = "bright"  # Clear, cheerful


class SpeechPaceModulation(Enum):
    """How speech speed changes with emotion"""
    NORMAL = 1.0
    SLOW = 0.7  # Sad, thoughtful, careful
    FAST = 1.4  # Excited, anxious, impulsive
    MEASURED = 0.9  # Formal, analytical
    RAPID = 1.6  # Angry, panicked


class PitchModulation(Enum):
    """How pitch changes with emotion"""
    DEEP = 0.7  # Sad, angry, authoritative
    NORMAL = 1.0
    HIGH = 1.4  # Happy, excited, fearful
    RISING = "rising"  # Questioning, uncertain
    FALLING = "falling"  # Confident, concluding


class VoiceQuirk(Enum):
    """Distinctive voice characteristics"""
    STUTTERING = "stuttering"  # Hesitant speech
    MELODIC = "melodic"  # Singing quality
    ROBOTIC = "robotic"  # Electronic artifacts
    BREATHY = "breathy"  # Soft, intimate
    RASPY = "raspy"  # Rough edges
    FLOWING = "flowing"  # Smooth, natural


@dataclass
class VoiceProfile:
    """Agent voice characteristics"""
    agent_id: str
    voice_type: VoiceType
    base_pitch: float = 1.0  # 0.5-2.0
    base_pace: float = 1.0  # 0.5-2.0 (words per second ratio)
    volume: float = 1.0  # 0.0-1.0
    clarity: float = 0.9  # 0.0-1.0, enunciation quality
    quirks: List[VoiceQuirk] = field(default_factory=list)

    def get_characteristic_pitch(self) -> float:
        """Base pitch for this voice type"""
        pitch_by_type = {
            VoiceType.CHILD: 1.5,
            VoiceType.ADULT: 1.0,
            VoiceType.DIGITAL: 1.2,
            VoiceType.ETHEREAL: 1.3,
            VoiceType.GRUFF: 0.6,
            VoiceType.BRIGHT: 1.4
        }
        return pitch_by_type.get(self.voice_type, 1.0) * self.base_pitch

    def get_characteristic_pace(self) -> float:
        """Base speaking pace for this voice type"""
        pace_by_type = {
            VoiceType.CHILD: 1.1,
            VoiceType.ADULT: 1.0,
            VoiceType.DIGITAL: 0.95,
            VoiceType.ETHEREAL: 0.8,
            VoiceType.GRUFF: 0.9,
            VoiceType.BRIGHT: 1.2
        }
        return pace_by_type.get(self.voice_type, 1.0) * self.base_pace

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "voice_type": self.voice_type.value,
            "pitch": self.get_characteristic_pitch(),
            "pace": self.get_characteristic_pace(),
            "volume": self.volume,
            "clarity": self.clarity,
            "quirks": [q.value for q in self.quirks]
        }


@dataclass
class EmotionalVoiceModulation:
    """How voice characteristics change with emotion"""
    emotion: str  # JOY, SADNESS, ANGER, FEAR, SURPRISE, DISGUST, TRUST, ANTICIPATION
    pitch_shift: float  # -2.0 to 2.0, multiplicative
    pace_shift: float  # 0.5 to 2.0, multiplicative
    volume_shift: float  # -1.0 to 1.0, additive
    brightness: float  # 0.0-1.0, how bright/clear the voice is

    def apply_to_voice(self, voice_profile: VoiceProfile) -> 'ModulatedVoice':
        """Apply emotional modulation to voice"""
        final_pitch = voice_profile.get_characteristic_pitch() * self.pitch_shift
        final_pace = voice_profile.get_characteristic_pace() * self.pace_shift
        final_volume = max(0.0, min(1.0, voice_profile.volume + self.volume_shift))

        return ModulatedVoice(
            emotion=self.emotion,
            pitch=final_pitch,
            pace=final_pace,
            volume=final_volume,
            brightness=self.brightness,
            clarity=voice_profile.clarity * self.brightness
        )

    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion,
            "pitch_shift": self.pitch_shift,
            "pace_shift": self.pace_shift,
            "volume_shift": self.volume_shift
        }


@dataclass
class ModulatedVoice:
    """Voice after applying emotional and context modulation"""
    emotion: str
    pitch: float  # 0.5-2.0
    pace: float  # 0.5-2.0
    volume: float  # 0.0-1.0
    brightness: float  # 0.0-1.0
    clarity: float  # 0.0-1.0

    def get_audio_description(self) -> str:
        """Human-readable audio description"""
        pace_desc = "rapid" if self.pace > 1.3 else "measured" if self.pace > 0.8 else "slow"
        pitch_desc = "high-pitched" if self.pitch > 1.3 else "deep" if self.pitch < 0.7 else "natural"
        brightness_desc = "bright" if self.brightness > 0.7 else "warm" if self.brightness > 0.3 else "dark"

        return f"{brightness_desc} {pitch_desc} voice speaking {pace_desc}"

    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion,
            "pitch": self.pitch,
            "pace": self.pace,
            "volume": self.volume,
            "brightness": self.brightness,
            "clarity": self.clarity,
            "description": self.get_audio_description()
        }


@dataclass
class SpeechPattern:
    """Communication style from personality"""
    pattern: str  # FORMAL, CASUAL, POETIC, TECHNICAL, CHILDLIKE, VERBOSE, TERSE
    pace_modifier: float  # How this pattern affects pace
    pitch_modifier: float  # How this pattern affects pitch
    clarity_boost: float  # How clear this pattern is
    emphasis_pattern: str  # e.g., "pause_between_clauses", "rising_inflection"

    def apply_to_voice(self, modulated_voice: ModulatedVoice) -> 'VoiceWithPattern':
        """Apply speech pattern to modulated voice"""
        pattern_descriptions = {
            "FORMAL": "formal, measured, professional",
            "CASUAL": "relaxed, conversational, natural",
            "POETIC": "lyrical, flowing, artistic",
            "TECHNICAL": "precise, emphatic on keywords",
            "CHILDLIKE": "playful, expressive, simple",
            "VERBOSE": "elaborate, detailed explanations",
            "TERSE": "concise, clipped delivery"
        }

        return VoiceWithPattern(
            base_voice=modulated_voice,
            pattern=self.pattern,
            pace_adjusted=modulated_voice.pace * self.pace_modifier,
            pitch_adjusted=modulated_voice.pitch * self.pitch_modifier,
            clarity_adjusted=modulated_voice.clarity + self.clarity_boost,
            style_description=pattern_descriptions.get(self.pattern, "neutral"),
            emphasis_pattern=self.emphasis_pattern
        )

    def to_dict(self) -> Dict:
        return {
            "pattern": self.pattern,
            "pace_modifier": self.pace_modifier,
            "pitch_modifier": self.pitch_modifier,
            "emphasis": self.emphasis_pattern
        }


@dataclass
class VoiceWithPattern:
    """Final voice rendering with all modulations applied"""
    base_voice: ModulatedVoice
    pattern: str
    pace_adjusted: float
    pitch_adjusted: float
    clarity_adjusted: float
    style_description: str
    emphasis_pattern: str

    def get_final_characteristics(self) -> Dict:
        """Get final audio characteristics for synthesis"""
        return {
            "pitch": max(0.3, min(3.0, self.pitch_adjusted)),  # Clamp reasonable range
            "pace": max(0.4, min(2.5, self.pace_adjusted)),  # Clamp reasonable range
            "volume": self.base_voice.volume,
            "clarity": max(0.0, min(1.0, self.clarity_adjusted)),
            "emotion": self.base_voice.emotion,
            "style": self.style_description,
            "emphasis": self.emphasis_pattern
        }

    def to_dict(self) -> Dict:
        return {
            "emotion": self.base_voice.emotion,
            "pattern": self.pattern,
            "pitch": self.pitch_adjusted,
            "pace": self.pace_adjusted,
            "clarity": self.clarity_adjusted,
            "style": self.style_description,
            "characteristics": self.get_final_characteristics()
        }


class EmotionalVoiceSystem:
    """Map emotions to voice characteristics"""

    # Predefined emotional modulations
    EMOTIONAL_MODULATIONS = {
        "JOY": EmotionalVoiceModulation(
            emotion="JOY",
            pitch_shift=1.3,
            pace_shift=1.3,
            volume_shift=0.2,
            brightness=0.9
        ),
        "SADNESS": EmotionalVoiceModulation(
            emotion="SADNESS",
            pitch_shift=0.7,
            pace_shift=0.6,
            volume_shift=-0.2,
            brightness=0.4
        ),
        "ANGER": EmotionalVoiceModulation(
            emotion="ANGER",
            pitch_shift=1.2,
            pace_shift=1.5,
            volume_shift=0.3,
            brightness=0.6
        ),
        "FEAR": EmotionalVoiceModulation(
            emotion="FEAR",
            pitch_shift=1.4,
            pace_shift=1.6,
            volume_shift=-0.1,
            brightness=0.5
        ),
        "SURPRISE": EmotionalVoiceModulation(
            emotion="SURPRISE",
            pitch_shift=1.5,
            pace_shift=1.2,
            volume_shift=0.2,
            brightness=0.85
        ),
        "DISGUST": EmotionalVoiceModulation(
            emotion="DISGUST",
            pitch_shift=0.8,
            pace_shift=0.8,
            volume_shift=0.1,
            brightness=0.45
        ),
        "TRUST": EmotionalVoiceModulation(
            emotion="TRUST",
            pitch_shift=0.95,
            pace_shift=0.9,
            volume_shift=0.05,
            brightness=0.75
        ),
        "ANTICIPATION": EmotionalVoiceModulation(
            emotion="ANTICIPATION",
            pitch_shift=1.2,
            pace_shift=1.4,
            volume_shift=0.1,
            brightness=0.8
        )
    }

    def get_emotional_modulation(self, emotion: str) -> Optional[EmotionalVoiceModulation]:
        """Get voice modulation for emotion"""
        return self.EMOTIONAL_MODULATIONS.get(emotion)

    def render_dialogue(
        self,
        voice_profile: VoiceProfile,
        emotion: str,
        speech_pattern: SpeechPattern
    ) -> VoiceWithPattern:
        """Render dialogue with full modulation"""
        modulation = self.get_emotional_modulation(emotion)
        if not modulation:
            modulation = self.EMOTIONAL_MODULATIONS["TRUST"]  # Default

        modulated = modulation.apply_to_voice(voice_profile)
        final_voice = speech_pattern.apply_to_voice(modulated)

        return final_voice

    def to_dict(self) -> Dict:
        return {
            "emotional_modulations": len(self.EMOTIONAL_MODULATIONS),
            "emotions": list(self.EMOTIONAL_MODULATIONS.keys())
        }


@dataclass
class DialogueAudio:
    """Audio rendering of dialogue with personality"""
    text: str
    voice_with_pattern: VoiceWithPattern
    duration: float = 0.0  # Estimated duration in seconds

    def estimate_duration(self, text_length: int) -> float:
        """Estimate speech duration based on text and pace"""
        # Rough calculation: 130 words/minute average
        # Adjusted for speech pattern pace
        base_wpm = 130
        adjusted_wpm = base_wpm * self.voice_with_pattern.pace_adjusted
        words = len(self.text.split())
        duration = (words / adjusted_wpm) * 60
        return duration

    def get_synthesis_params(self) -> Dict:
        """Parameters for speech synthesis engine"""
        params = self.voice_with_pattern.get_final_characteristics()
        params["text"] = self.text
        params["duration_estimate"] = self.duration
        return params

    def to_dict(self) -> Dict:
        return {
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "duration": self.duration,
            "audio_params": self.voice_with_pattern.to_dict()
        }


class AudioSystem:
    """Complete audio system for agent speech"""

    def __init__(self):
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.emotional_system = EmotionalVoiceSystem()
        self.speech_patterns: Dict[str, SpeechPattern] = self._init_speech_patterns()

    def _init_speech_patterns(self) -> Dict[str, SpeechPattern]:
        """Initialize speech patterns"""
        return {
            "FORMAL": SpeechPattern("FORMAL", 0.9, 0.95, 0.1, "pause_between_clauses"),
            "CASUAL": SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow"),
            "POETIC": SpeechPattern("POETIC", 0.85, 1.2, 0.15, "melodic_phrasing"),
            "TECHNICAL": SpeechPattern("TECHNICAL", 0.95, 1.05, 0.2, "emphasis_keywords"),
            "CHILDLIKE": SpeechPattern("CHILDLIKE", 1.15, 1.1, 0.1, "playful_inflection"),
            "VERBOSE": SpeechPattern("VERBOSE", 0.9, 1.0, 0.05, "detailed_pacing"),
            "TERSE": SpeechPattern("TERSE", 1.2, 0.95, 0.0, "clipped_delivery")
        }

    def register_agent_voice(self, voice_profile: VoiceProfile) -> bool:
        """Register agent voice"""
        if voice_profile.agent_id in self.voice_profiles:
            return False
        self.voice_profiles[voice_profile.agent_id] = voice_profile
        return True

    def render_agent_speech(
        self,
        agent_id: str,
        text: str,
        emotion: str = "TRUST",
        speech_pattern_name: str = "CASUAL"
    ) -> Optional[DialogueAudio]:
        """Render agent speech with emotion and style"""
        if agent_id not in self.voice_profiles:
            return None

        voice_profile = self.voice_profiles[agent_id]
        speech_pattern = self.speech_patterns.get(speech_pattern_name)

        if not speech_pattern:
            speech_pattern = self.speech_patterns["CASUAL"]

        voice_with_pattern = self.emotional_system.render_dialogue(
            voice_profile,
            emotion,
            speech_pattern
        )

        dialogue = DialogueAudio(
            text=text,
            voice_with_pattern=voice_with_pattern
        )
        dialogue.duration = dialogue.estimate_duration(len(text))

        return dialogue

    def get_voice_profile(self, agent_id: str) -> Optional[VoiceProfile]:
        """Get agent's voice profile"""
        return self.voice_profiles.get(agent_id)

    def to_dict(self) -> Dict:
        return {
            "agents": len(self.voice_profiles),
            "speech_patterns": len(self.speech_patterns),
            "emotions_available": list(self.emotional_system.EMOTIONAL_MODULATIONS.keys())
        }


# ===== Tests =====

def test_voice_profile_creation():
    """Test creating voice profile"""
    vp = VoiceProfile(
        agent_id="a1",
        voice_type=VoiceType.CHILD
    )
    assert vp.agent_id == "a1"
    assert vp.volume == 1.0


def test_voice_type_pitch():
    """Test pitch varies by voice type"""
    child_voice = VoiceProfile("a1", VoiceType.CHILD)
    gruff_voice = VoiceProfile("a2", VoiceType.GRUFF)

    assert child_voice.get_characteristic_pitch() > gruff_voice.get_characteristic_pitch()


def test_voice_type_pace():
    """Test pace varies by voice type"""
    bright_voice = VoiceProfile("a1", VoiceType.BRIGHT)
    ethereal_voice = VoiceProfile("a2", VoiceType.ETHEREAL)

    assert bright_voice.get_characteristic_pace() > ethereal_voice.get_characteristic_pace()


def test_emotional_modulation_joy():
    """Test joy increases pitch and pace"""
    joy_mod = EmotionalVoiceModulation(
        emotion="JOY",
        pitch_shift=1.3,
        pace_shift=1.3,
        volume_shift=0.2,
        brightness=0.9
    )
    assert joy_mod.pitch_shift > 1.0
    assert joy_mod.pace_shift > 1.0


def test_emotional_modulation_sadness():
    """Test sadness decreases pitch and pace"""
    sadness_mod = EmotionalVoiceModulation(
        emotion="SADNESS",
        pitch_shift=0.7,
        pace_shift=0.6,
        volume_shift=-0.2,
        brightness=0.4
    )
    assert sadness_mod.pitch_shift < 1.0
    assert sadness_mod.pace_shift < 1.0


def test_apply_emotional_modulation():
    """Test applying emotion to voice"""
    vp = VoiceProfile("a1", VoiceType.ADULT)
    modulation = EmotionalVoiceModulation(
        emotion="JOY",
        pitch_shift=1.3,
        pace_shift=1.3,
        volume_shift=0.2,
        brightness=0.9
    )
    modulated = modulation.apply_to_voice(vp)
    assert modulated.emotion == "JOY"
    assert modulated.pitch > vp.get_characteristic_pitch()


def test_modulated_voice_description():
    """Test audio description of modulated voice"""
    modulated = ModulatedVoice(
        emotion="JOY",
        pitch=1.5,
        pace=1.4,
        volume=1.0,
        brightness=0.9,
        clarity=0.95
    )
    desc = modulated.get_audio_description()
    assert "bright" in desc.lower()


def test_speech_pattern_formal():
    """Test formal speech pattern"""
    formal = SpeechPattern("FORMAL", 0.9, 0.95, 0.1, "pause_between_clauses")
    assert formal.pace_modifier < 1.0
    assert formal.clarity_boost > 0


def test_speech_pattern_casual():
    """Test casual speech pattern"""
    casual = SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow")
    assert casual.pace_modifier > 1.0


def test_apply_speech_pattern():
    """Test applying speech pattern to voice"""
    modulated = ModulatedVoice(
        emotion="TRUST",
        pitch=1.0,
        pace=1.0,
        volume=1.0,
        brightness=0.75,
        clarity=0.9
    )
    formal = SpeechPattern("FORMAL", 0.9, 0.95, 0.1, "pause_between_clauses")
    voiced = formal.apply_to_voice(modulated)
    assert voiced.pattern == "FORMAL"
    assert voiced.pace_adjusted < modulated.pace


def test_voice_with_pattern_characteristics():
    """Test getting final voice characteristics"""
    modulated = ModulatedVoice(
        emotion="JOY",
        pitch=1.5,
        pace=1.4,
        volume=1.0,
        brightness=0.9,
        clarity=0.95
    )
    pattern = SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow")
    voiced = pattern.apply_to_voice(modulated)

    chars = voiced.get_final_characteristics()
    assert "pitch" in chars
    assert "pace" in chars
    assert "emotion" in chars


def test_emotional_voice_system():
    """Test emotional voice system"""
    evs = EmotionalVoiceSystem()
    joy_mod = evs.get_emotional_modulation("JOY")
    assert joy_mod is not None
    assert joy_mod.emotion == "JOY"


def test_render_dialogue_basic():
    """Test basic dialogue rendering"""
    evs = EmotionalVoiceSystem()
    vp = VoiceProfile("a1", VoiceType.ADULT)
    pattern = SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow")

    voiced = evs.render_dialogue(vp, "JOY", pattern)
    assert voiced.base_voice.emotion == "JOY"


def test_dialogue_audio_creation():
    """Test creating dialogue audio"""
    modulated = ModulatedVoice(
        emotion="JOY",
        pitch=1.5,
        pace=1.4,
        volume=1.0,
        brightness=0.9,
        clarity=0.95
    )
    pattern = SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow")
    voiced = pattern.apply_to_voice(modulated)

    dialogue = DialogueAudio(
        text="Hello, I'm very happy to meet you!",
        voice_with_pattern=voiced
    )
    assert dialogue.text == "Hello, I'm very happy to meet you!"


def test_estimate_duration():
    """Test estimating speech duration"""
    modulated = ModulatedVoice(
        emotion="TRUST",
        pitch=1.0,
        pace=1.0,
        volume=1.0,
        brightness=0.75,
        clarity=0.9
    )
    pattern = SpeechPattern("CASUAL", 1.1, 1.0, 0.05, "natural_flow")
    voiced = pattern.apply_to_voice(modulated)

    dialogue = DialogueAudio(
        text="This is a test sentence with several words.",
        voice_with_pattern=voiced
    )
    duration = dialogue.estimate_duration(len(dialogue.text))
    assert duration > 0


def test_audio_system_creation():
    """Test creating audio system"""
    audio_system = AudioSystem()
    assert audio_system is not None
    assert len(audio_system.speech_patterns) == 7


def test_register_agent_voice():
    """Test registering agent voice"""
    audio_system = AudioSystem()
    vp = VoiceProfile("a1", VoiceType.CHILD)
    assert audio_system.register_agent_voice(vp) is True


def test_render_agent_speech():
    """Test rendering agent speech"""
    audio_system = AudioSystem()
    vp = VoiceProfile("a1", VoiceType.BRIGHT)
    audio_system.register_agent_voice(vp)

    dialogue = audio_system.render_agent_speech(
        agent_id="a1",
        text="I'm so excited!",
        emotion="JOY",
        speech_pattern_name="CASUAL"
    )
    assert dialogue is not None
    assert dialogue.voice_with_pattern.base_voice.emotion == "JOY"


def test_complete_voice_workflow():
    """Test complete voice rendering workflow"""
    audio_system = AudioSystem()

    # Create agents with different voices
    curious_voice = VoiceProfile("explorer", VoiceType.BRIGHT, quirks=[VoiceQuirk.MELODIC])
    cautious_voice = VoiceProfile("helper", VoiceType.ETHEREAL, quirks=[VoiceQuirk.BREATHY])

    audio_system.register_agent_voice(curious_voice)
    audio_system.register_agent_voice(cautious_voice)

    # Render dialogue
    explorer_speech = audio_system.render_agent_speech(
        agent_id="explorer",
        text="Let's explore this amazing place!",
        emotion="ANTICIPATION",
        speech_pattern_name="CHILDLIKE"
    )

    helper_speech = audio_system.render_agent_speech(
        agent_id="helper",
        text="I'm... a little nervous...",
        emotion="FEAR",
        speech_pattern_name="FORMAL"
    )

    assert explorer_speech is not None
    assert helper_speech is not None
    assert explorer_speech.voice_with_pattern.pitch_adjusted > helper_speech.voice_with_pattern.pitch_adjusted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
