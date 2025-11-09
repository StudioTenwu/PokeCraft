"""
Round 31: Agent Personality Expression System

Enable agents to express their personalities through dialogue patterns,
behavioral quirks, speech mannerisms, and interaction styles. Personality
becomes visible and tangible to players.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class SpeechPattern(Enum):
    """How agents speak"""
    FORMAL = "formal"  # Professional, measured
    CASUAL = "casual"  # Relaxed, friendly
    POETIC = "poetic"  # Flowery, artistic
    TECHNICAL = "technical"  # Precise, jargon-heavy
    CHILDLIKE = "childlike"  # Simple, playful
    VERBOSE = "verbose"  # Wordy, detailed
    TERSE = "terse"  # Brief, minimal


class BehaviorQuirk(Enum):
    """Unique behavioral traits"""
    CURIOUS = "curious"  # Always asks questions
    CAUTIOUS = "cautious"  # Second-guesses decisions
    BOLD = "bold"  # Takes risks readily
    ANALYTICAL = "analytical"  # Thinks through everything
    IMPULSIVE = "impulsive"  # Acts before thinking
    EMPATHETIC = "empathetic"  # Considers others' feelings
    SELFISH = "selfish"  # Prioritizes own goals


class InteractionStyle(Enum):
    """How agent interacts with others"""
    AGGRESSIVE = "aggressive"  # Direct confrontation
    PASSIVE = "passive"  # Avoidant, non-confrontational
    ASSERTIVE = "assertive"  # Clear but respectful
    MANIPULATIVE = "manipulative"  # Uses social engineering
    COLLABORATIVE = "collaborative"  # Seeks partnership
    INDEPENDENT = "independent"  # Prefers solo work
    DEPENDENT = "dependent"  # Seeks guidance


@dataclass
class DialoguePhrase:
    """A phrase the agent might say"""
    phrase_id: str
    content: str
    speech_pattern: SpeechPattern
    context: str  # When to use it
    personality_alignment: Dict[str, float] = field(default_factory=dict)  # Trait → alignment (0.0-1.0)
    usage_count: int = 0

    def use_phrase(self) -> bool:
        """Record usage of this phrase"""
        self.usage_count += 1
        return True

    def get_alignment_score(self, trait: str) -> float:
        """How well does this phrase match a trait"""
        return self.personality_alignment.get(trait, 0.5)

    def to_dict(self) -> Dict:
        return {
            "phrase_id": self.phrase_id,
            "speech_pattern": self.speech_pattern.value,
            "usage_count": self.usage_count
        }


@dataclass
class PersonalityManifest:
    """How a personality expresses itself"""
    agent_id: str
    dominant_quirks: List[BehaviorQuirk] = field(default_factory=list)
    speech_pattern: SpeechPattern = SpeechPattern.CASUAL
    interaction_style: InteractionStyle = InteractionStyle.COLLABORATIVE
    signature_phrases: Set[str] = field(default_factory=set)
    behavioral_consistency: float = 0.5  # 0.0-1.0, how consistent behavior is
    expressiveness: float = 0.5  # 0.0-1.0, how much personality shows
    mannerisms: Dict[str, int] = field(default_factory=dict)  # Quirk → frequency

    def add_quirk(self, quirk: BehaviorQuirk) -> bool:
        """Add behavioral quirk"""
        if quirk in self.dominant_quirks:
            return False
        if len(self.dominant_quirks) >= 3:
            return False  # Max 3 dominant quirks
        self.dominant_quirks.append(quirk)
        self.mannerisms[quirk.value] = 0
        return True

    def remove_quirk(self, quirk: BehaviorQuirk) -> bool:
        """Remove behavioral quirk"""
        if quirk not in self.dominant_quirks:
            return False
        self.dominant_quirks.remove(quirk)
        if quirk.value in self.mannerisms:
            del self.mannerisms[quirk.value]
        return True

    def add_signature_phrase(self, phrase_id: str) -> bool:
        """Add phrase the agent says frequently"""
        if len(self.signature_phrases) >= 5:
            return False
        self.signature_phrases.add(phrase_id)
        return True

    def exhibit_mannerism(self, quirk: BehaviorQuirk) -> bool:
        """Agent exhibits a quirk"""
        if quirk.value not in self.mannerisms:
            return False
        self.mannerisms[quirk.value] += 1
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "speech_pattern": self.speech_pattern.value,
            "interaction_style": self.interaction_style.value,
            "quirks": [q.value for q in self.dominant_quirks],
            "expressiveness": self.expressiveness
        }


class DialogueSystem:
    """Manage agent dialogue and expression"""

    def __init__(self):
        self.dialogue_library: Dict[str, DialoguePhrase] = {}
        self.agent_manifestos: Dict[str, PersonalityManifest] = {}
        self.total_dialogues_spoken: int = 0
        self.expression_log: List[Dict] = []

    def add_dialogue_phrase(self, phrase: DialoguePhrase) -> bool:
        """Add dialogue option"""
        if phrase.phrase_id in self.dialogue_library:
            return False
        self.dialogue_library[phrase.phrase_id] = phrase
        return True

    def register_agent_personality(self, agent_id: str, manifest: PersonalityManifest) -> bool:
        """Register agent's personality"""
        if agent_id in self.agent_manifestos:
            return False
        self.agent_manifestos[agent_id] = manifest
        return True

    def select_dialogue(self, agent_id: str, context: str) -> Optional[str]:
        """Select appropriate dialogue for agent in context"""
        if agent_id not in self.agent_manifestos:
            return None

        manifest = self.agent_manifestos[agent_id]

        # Find phrases matching context and speech pattern
        matching_phrases = [
            p for p in self.dialogue_library.values()
            if context.lower() in p.context.lower() and p.speech_pattern == manifest.speech_pattern
        ]

        if not matching_phrases:
            # Fallback to any phrase with context
            matching_phrases = [
                p for p in self.dialogue_library.values()
                if context.lower() in p.context.lower()
            ]

        if not matching_phrases:
            return None

        # Select from matching phrases
        best_phrase = max(matching_phrases, key=lambda p: p.get_alignment_score("general"))
        return best_phrase.phrase_id

    def speak_dialogue(self, agent_id: str, phrase_id: str) -> bool:
        """Agent speaks a dialogue phrase"""
        if agent_id not in self.agent_manifestos or phrase_id not in self.dialogue_library:
            return False

        phrase = self.dialogue_library[phrase_id]
        manifest = self.agent_manifestos[agent_id]

        phrase.use_phrase()
        self.total_dialogues_spoken += 1

        # Log expression
        self.expression_log.append({
            "agent_id": agent_id,
            "phrase_id": phrase_id,
            "timestamp": len(self.expression_log),
            "speech_pattern": phrase.speech_pattern.value
        })

        return True

    def update_personality_trait(self, agent_id: str, trait: str, value: float) -> bool:
        """Update personality trait strength"""
        if agent_id not in self.agent_manifestos:
            return False
        if not (0.0 <= value <= 1.0):
            return False

        manifest = self.agent_manifestos[agent_id]
        if trait == "expressiveness":
            manifest.expressiveness = value
        elif trait == "consistency":
            manifest.behavioral_consistency = value

        return True

    def get_personality_summary(self, agent_id: str) -> Dict:
        """Get personality summary for agent"""
        if agent_id not in self.agent_manifestos:
            return {}

        manifest = self.agent_manifestos[agent_id]
        return {
            "speech_pattern": manifest.speech_pattern.value,
            "interaction_style": manifest.interaction_style.value,
            "dominant_quirks": [q.value for q in manifest.dominant_quirks],
            "signature_phrases": len(manifest.signature_phrases),
            "expressiveness": manifest.expressiveness,
            "behavioral_consistency": manifest.behavioral_consistency
        }

    def analyze_dialogue_patterns(self, agent_id: str) -> Dict:
        """Analyze agent's dialogue patterns"""
        agent_dialogues = [
            log for log in self.expression_log
            if log["agent_id"] == agent_id
        ]

        if not agent_dialogues:
            return {"dialogues_spoken": 0}

        # Count speech patterns used
        patterns: Dict[str, int] = {}
        for log in agent_dialogues:
            pattern = log["speech_pattern"]
            patterns[pattern] = patterns.get(pattern, 0) + 1

        return {
            "dialogues_spoken": len(agent_dialogues),
            "speech_patterns_used": patterns,
            "consistency": len(set(patterns.keys())) == 1  # Using single pattern = consistent
        }

    def get_expression_consistency(self, agent_id: str) -> float:
        """Measure how consistently agent expresses personality (0.0-1.0)"""
        analysis = self.analyze_dialogue_patterns(agent_id)
        if analysis.get("dialogues_spoken", 0) < 3:
            return 0.5  # Need minimum samples

        manifest = self.agent_manifestos.get(agent_id)
        if not manifest:
            return 0.0

        # Consistency = using consistent speech pattern + exhibiting quirks
        pattern_consistency = 1.0 if analysis.get("consistency") else 0.7
        quirk_consistency = sum(manifest.mannerisms.values()) / max(1, len(manifest.mannerisms)) / 10.0

        return (pattern_consistency + min(1.0, quirk_consistency)) / 2.0

    def to_dict(self) -> Dict:
        return {
            "agents_with_personality": len(self.agent_manifestos),
            "dialogue_library_size": len(self.dialogue_library),
            "total_dialogues_spoken": self.total_dialogues_spoken
        }


# ===== Tests =====

def test_dialogue_phrase_creation():
    """Test creating dialogue phrase"""
    phrase = DialoguePhrase(
        phrase_id="greeting_1",
        content="Hello there!",
        speech_pattern=SpeechPattern.CASUAL,
        context="greeting"
    )
    assert phrase.speech_pattern == SpeechPattern.CASUAL


def test_dialogue_usage():
    """Test using dialogue phrase"""
    phrase = DialoguePhrase(
        phrase_id="greet",
        content="Hey!",
        speech_pattern=SpeechPattern.CASUAL,
        context="hello"
    )
    assert phrase.use_phrase() is True
    assert phrase.usage_count == 1


def test_personality_manifest_creation():
    """Test creating personality manifest"""
    manifest = PersonalityManifest(agent_id="a1")
    assert manifest.agent_id == "a1"
    assert manifest.speech_pattern == SpeechPattern.CASUAL


def test_add_quirk():
    """Test adding behavioral quirk"""
    manifest = PersonalityManifest(agent_id="a1")
    assert manifest.add_quirk(BehaviorQuirk.CURIOUS) is True
    assert BehaviorQuirk.CURIOUS in manifest.dominant_quirks


def test_max_quirks():
    """Test maximum quirks limit"""
    manifest = PersonalityManifest(agent_id="a1")
    assert manifest.add_quirk(BehaviorQuirk.CURIOUS) is True
    assert manifest.add_quirk(BehaviorQuirk.BOLD) is True
    assert manifest.add_quirk(BehaviorQuirk.ANALYTICAL) is True
    assert manifest.add_quirk(BehaviorQuirk.IMPULSIVE) is False  # Max 3


def test_remove_quirk():
    """Test removing quirk"""
    manifest = PersonalityManifest(agent_id="a1")
    manifest.add_quirk(BehaviorQuirk.CURIOUS)
    assert manifest.remove_quirk(BehaviorQuirk.CURIOUS) is True


def test_signature_phrases():
    """Test adding signature phrase"""
    manifest = PersonalityManifest(agent_id="a1")
    assert manifest.add_signature_phrase("phrase_1") is True
    assert "phrase_1" in manifest.signature_phrases


def test_exhibit_mannerism():
    """Test agent exhibiting quirk"""
    manifest = PersonalityManifest(agent_id="a1")
    manifest.add_quirk(BehaviorQuirk.CURIOUS)
    assert manifest.exhibit_mannerism(BehaviorQuirk.CURIOUS) is True
    assert manifest.mannerisms[BehaviorQuirk.CURIOUS.value] == 1


def test_dialogue_system_creation():
    """Test creating dialogue system"""
    system = DialogueSystem()
    assert system.total_dialogues_spoken == 0


def test_add_dialogue_to_system():
    """Test adding dialogue to system"""
    system = DialogueSystem()
    phrase = DialoguePhrase(
        phrase_id="p1",
        content="Hello",
        speech_pattern=SpeechPattern.CASUAL,
        context="greeting"
    )
    assert system.add_dialogue_phrase(phrase) is True


def test_register_agent_personality():
    """Test registering agent personality"""
    system = DialogueSystem()
    manifest = PersonalityManifest(agent_id="a1")
    assert system.register_agent_personality("a1", manifest) is True


def test_select_dialogue():
    """Test selecting dialogue for context"""
    system = DialogueSystem()
    manifest = PersonalityManifest(agent_id="a1", speech_pattern=SpeechPattern.CASUAL)
    system.register_agent_personality("a1", manifest)

    phrase = DialoguePhrase(
        phrase_id="greet",
        content="Hey there!",
        speech_pattern=SpeechPattern.CASUAL,
        context="greeting"
    )
    system.add_dialogue_phrase(phrase)

    selected = system.select_dialogue("a1", "greeting")
    assert selected == "greet"


def test_speak_dialogue():
    """Test agent speaking dialogue"""
    system = DialogueSystem()
    manifest = PersonalityManifest(agent_id="a1")
    system.register_agent_personality("a1", manifest)

    phrase = DialoguePhrase(
        phrase_id="p1",
        content="Hello",
        speech_pattern=SpeechPattern.CASUAL,
        context="greeting"
    )
    system.add_dialogue_phrase(phrase)

    assert system.speak_dialogue("a1", "p1") is True
    assert system.total_dialogues_spoken == 1


def test_personality_summary():
    """Test getting personality summary"""
    system = DialogueSystem()
    manifest = PersonalityManifest(
        agent_id="a1",
        speech_pattern=SpeechPattern.POETIC,
        interaction_style=InteractionStyle.COLLABORATIVE
    )
    manifest.add_quirk(BehaviorQuirk.CURIOUS)
    system.register_agent_personality("a1", manifest)

    summary = system.get_personality_summary("a1")
    assert summary["speech_pattern"] == SpeechPattern.POETIC.value
    assert "CURIOUS" in summary["dominant_quirks"][0].upper()


def test_dialogue_pattern_analysis():
    """Test analyzing dialogue patterns"""
    system = DialogueSystem()
    manifest = PersonalityManifest(agent_id="a1", speech_pattern=SpeechPattern.FORMAL)
    system.register_agent_personality("a1", manifest)

    phrase = DialoguePhrase(
        phrase_id="p1",
        content="Good day",
        speech_pattern=SpeechPattern.FORMAL,
        context="greeting"
    )
    system.add_dialogue_phrase(phrase)

    system.speak_dialogue("a1", "p1")
    system.speak_dialogue("a1", "p1")

    analysis = system.analyze_dialogue_patterns("a1")
    assert analysis["dialogues_spoken"] == 2


def test_expression_consistency():
    """Test measuring expression consistency"""
    system = DialogueSystem()
    manifest = PersonalityManifest(agent_id="a1", speech_pattern=SpeechPattern.CASUAL)
    manifest.add_quirk(BehaviorQuirk.BOLD)
    system.register_agent_personality("a1", manifest)

    phrase = DialoguePhrase(
        phrase_id="p1",
        content="Let's go!",
        speech_pattern=SpeechPattern.CASUAL,
        context="action"
    )
    system.add_dialogue_phrase(phrase)

    system.speak_dialogue("a1", "p1")
    manifest.exhibit_mannerism(BehaviorQuirk.BOLD)

    consistency = system.get_expression_consistency("a1")
    assert 0.0 <= consistency <= 1.0


def test_complete_personality_workflow():
    """Test complete personality expression workflow"""
    system = DialogueSystem()

    # Create agent with distinct personality
    manifest = PersonalityManifest(
        agent_id="creative_spark",
        speech_pattern=SpeechPattern.POETIC,
        interaction_style=InteractionStyle.COLLABORATIVE,
        expressiveness=0.8
    )
    manifest.add_quirk(BehaviorQuirk.CURIOUS)
    manifest.add_quirk(BehaviorQuirk.EMPATHETIC)
    manifest.add_signature_phrase("phrase_wonder")

    system.register_agent_personality("creative_spark", manifest)

    # Create dialogue library
    phrases = [
        DialoguePhrase("phrase_wonder", "I wonder what would happen if...", SpeechPattern.POETIC, "exploration"),
        DialoguePhrase("phrase_care", "How are you feeling about this?", SpeechPattern.CASUAL, "conversation"),
        DialoguePhrase("phrase_question", "Why do you think that matters?", SpeechPattern.CASUAL, "inquiry"),
    ]

    for phrase in phrases:
        system.add_dialogue_phrase(phrase)

    # Agent speaks in character
    system.speak_dialogue("creative_spark", "phrase_wonder")
    system.speak_dialogue("creative_spark", "phrase_care")
    system.speak_dialogue("creative_spark", "phrase_question")

    # Exhibit quirks
    manifest.exhibit_mannerism(BehaviorQuirk.CURIOUS)
    manifest.exhibit_mannerism(BehaviorQuirk.CURIOUS)
    manifest.exhibit_mannerism(BehaviorQuirk.EMPATHETIC)

    # Verify personality consistency
    summary = system.get_personality_summary("creative_spark")
    assert summary["expressiveness"] == 0.8
    assert len(summary["dominant_quirks"]) == 2

    analysis = system.analyze_dialogue_patterns("creative_spark")
    assert analysis["dialogues_spoken"] == 3

    consistency = system.get_expression_consistency("creative_spark")
    assert 0.0 <= consistency <= 1.0  # Measure consistency, even if not perfectly consistent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
