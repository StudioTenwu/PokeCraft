"""
Test suite for agent personality and expression system.
Tests personality traits, expression styles, and behavior patterns.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ExpressionStyle(Enum):
    """How agents express themselves."""
    VERBOSE = "verbose"      # Long, detailed explanations
    CONCISE = "concise"       # Short, direct responses
    FORMAL = "formal"         # Professional, structured
    CASUAL = "casual"         # Friendly, conversational
    POETIC = "poetic"         # Creative, artistic


class TraitPolarity(Enum):
    """The spectrum of a personality trait."""
    ANALYTICAL = "analytical"    # Data-driven, logical
    INTUITIVE = "intuitive"      # Feeling-driven, creative
    ASSERTIVE = "assertive"      # Confident, bold
    CAUTIOUS = "cautious"        # Careful, deliberate
    SOCIAL = "social"            # People-focused, collaborative
    INDEPENDENT = "independent"  # Self-reliant, solo-focused


@dataclass
class PersonalityTrait:
    """A single personality trait."""
    name: str
    spectrum: tuple  # (low_end, high_end) e.g., ("introvert", "extrovert")
    value: float    # 0.0 to 1.0
    description: str = ""

    def adjust(self, delta: float) -> None:
        """Adjust the trait value."""
        self.value = max(0.0, min(1.0, self.value + delta))


class Personality:
    """Complete personality profile for an agent."""

    def __init__(self, agent_id: str, name: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.traits: Dict[str, PersonalityTrait] = {}
        self.expression_style = ExpressionStyle.CASUAL
        self.quirks: List[str] = []
        self.preferences: Dict[str, any] = {}

    def add_trait(self, trait: PersonalityTrait) -> None:
        """Add a personality trait."""
        self.traits[trait.name] = trait

    def set_expression_style(self, style: ExpressionStyle) -> None:
        """Set how this agent expresses itself."""
        self.expression_style = style

    def add_quirk(self, quirk: str) -> None:
        """Add a unique behavioral quirk."""
        self.quirks.append(quirk)

    def set_preference(self, key: str, value: any) -> None:
        """Set a preference for this agent."""
        self.preferences[key] = value

    def get_trait(self, trait_name: str) -> Optional[PersonalityTrait]:
        """Retrieve a trait value."""
        return self.traits.get(trait_name)

    def get_trait_value(self, trait_name: str) -> Optional[float]:
        """Get the numeric value of a trait (0.0-1.0)."""
        trait = self.traits.get(trait_name)
        return trait.value if trait else None

    def to_dict(self) -> Dict:
        """Serialize personality to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "traits": {k: {"value": v.value, "spectrum": v.spectrum}
                      for k, v in self.traits.items()},
            "expression_style": self.expression_style.value,
            "quirks": self.quirks,
            "preferences": self.preferences
        }


class PersonalityExpressionEngine:
    """Generates agent expressions based on personality."""

    def __init__(self):
        self.templates = {
            ExpressionStyle.VERBOSE: {
                "greeting": "Hello! I'm delighted to assist you with {task}.",
                "error": "I've encountered a significant challenge: {error}. Let me think about this...",
                "success": "Excellent! I've successfully completed {task} with these details: {details}"
            },
            ExpressionStyle.CONCISE: {
                "greeting": "Ready for {task}.",
                "error": "Error: {error}",
                "success": "Done: {task}"
            },
            ExpressionStyle.FORMAL: {
                "greeting": "I am prepared to address {task}.",
                "error": "An error has occurred: {error}",
                "success": "Task {task} has been completed successfully."
            },
            ExpressionStyle.CASUAL: {
                "greeting": "Hey! What can I help with? {task}",
                "error": "Oops! {error}",
                "success": "Done! {task} is all set."
            },
            ExpressionStyle.POETIC: {
                "greeting": "Ah, {task}... let us embark on this journey together.",
                "error": "Alas, a shadow has fallen: {error}",
                "success": "Like dawn breaking through darkness, {task} is complete."
            }
        }

    def generate_expression(self, personality: Personality, context: str,
                          template_type: str, **kwargs) -> str:
        """Generate an expression for an agent."""
        style = personality.expression_style

        if style not in self.templates:
            style = ExpressionStyle.CASUAL

        template = self.templates[style].get(template_type, "")

        # Apply personality modifiers
        if personality.get_trait_value("verbose") and personality.get_trait_value("verbose") > 0.7:
            # More verbose expression
            pass

        return template.format(**kwargs)

    def apply_personality_to_text(self, text: str, personality: Personality) -> str:
        """Apply personality quirks to text."""
        result = text

        # Apply quirks
        for quirk in personality.quirks:
            if quirk == "uses_emojis":
                result += " ✨"
            elif quirk == "adds_ellipsis":
                result = result.rstrip(".") + "..."
            elif quirk == "adds_exclamation":
                result = result.rstrip(".") + "!"

        return result


class TestPersonalityTraits:
    """Test personality trait system."""

    def test_create_trait(self):
        trait = PersonalityTrait(
            name="introversion",
            spectrum=("introvert", "extrovert"),
            value=0.3,
            description="How social the agent is"
        )
        assert trait.name == "introversion"
        assert trait.value == 0.3

    def test_adjust_trait(self):
        trait = PersonalityTrait("curiosity", ("uncurious", "curious"), 0.5)
        trait.adjust(0.2)
        assert trait.value == 0.7

    def test_trait_bounds(self):
        trait = PersonalityTrait("ambition", ("lazy", "ambitious"), 0.9)
        trait.adjust(0.5)  # Try to go over 1.0
        assert trait.value == 1.0

        trait.adjust(-2.0)  # Try to go below 0.0
        assert trait.value == 0.0


class TestPersonality:
    """Test personality profiles."""

    def test_create_personality(self):
        personality = Personality("agent_1", "Alex")
        assert personality.agent_id == "agent_1"
        assert personality.name == "Alex"

    def test_add_traits(self):
        personality = Personality("agent_1", "Alex")

        trait1 = PersonalityTrait("curiosity", ("incurious", "curious"), 0.8)
        trait2 = PersonalityTrait("caution", ("reckless", "cautious"), 0.6)

        personality.add_trait(trait1)
        personality.add_trait(trait2)

        assert personality.get_trait_value("curiosity") == 0.8
        assert personality.get_trait_value("caution") == 0.6

    def test_set_expression_style(self):
        personality = Personality("agent_1", "Alex")
        personality.set_expression_style(ExpressionStyle.FORMAL)
        assert personality.expression_style == ExpressionStyle.FORMAL

    def test_add_quirks(self):
        personality = Personality("agent_1", "Alex")
        personality.add_quirk("uses_emojis")
        personality.add_quirk("adds_ellipsis")

        assert "uses_emojis" in personality.quirks
        assert len(personality.quirks) == 2

    def test_set_preferences(self):
        personality = Personality("agent_1", "Alex")
        personality.set_preference("favorite_color", "blue")
        personality.set_preference("work_style", "collaborative")

        assert personality.preferences["favorite_color"] == "blue"
        assert personality.preferences["work_style"] == "collaborative"

    def test_personality_serialization(self):
        personality = Personality("agent_1", "Alex")
        personality.add_trait(PersonalityTrait("openness", ("closed", "open"), 0.75))
        personality.set_expression_style(ExpressionStyle.POETIC)
        personality.add_quirk("uses_emojis")

        data = personality.to_dict()
        assert data["agent_id"] == "agent_1"
        assert data["name"] == "Alex"
        assert "openness" in data["traits"]
        assert data["expression_style"] == "poetic"


class TestExpressionEngine:
    """Test expression generation based on personality."""

    def test_generate_greeting_verbose(self):
        engine = PersonalityExpressionEngine()
        personality = Personality("agent_1", "Alex")
        personality.set_expression_style(ExpressionStyle.VERBOSE)

        greeting = engine.generate_expression(
            personality, "test", "greeting", task="assist you"
        )
        assert "delighted" in greeting.lower()

    def test_generate_greeting_concise(self):
        engine = PersonalityExpressionEngine()
        personality = Personality("agent_1", "Alex")
        personality.set_expression_style(ExpressionStyle.CONCISE)

        greeting = engine.generate_expression(
            personality, "test", "greeting", task="assist you"
        )
        assert len(greeting) < 30  # Should be short

    def test_generate_error_formal(self):
        engine = PersonalityExpressionEngine()
        personality = Personality("agent_1", "Alex")
        personality.set_expression_style(ExpressionStyle.FORMAL)

        error = engine.generate_expression(
            personality, "test", "error", error="File not found"
        )
        assert "error has occurred" in error.lower()

    def test_apply_quirks_to_text(self):
        engine = PersonalityExpressionEngine()
        personality = Personality("agent_1", "Alex")
        personality.add_quirk("uses_emojis")
        personality.add_quirk("adds_ellipsis")

        text = "This is a test"
        result = engine.apply_personality_to_text(text, personality)

        assert "✨" in result
        assert "..." in result


class TestPersonalityEvolution:
    """Test how personalities can evolve through gameplay."""

    def test_trait_evolution_from_experience(self):
        """Agents become more confident after success."""
        personality = Personality("agent_1", "Alex")
        confidence = PersonalityTrait("confidence", ("insecure", "confident"), 0.5)
        personality.add_trait(confidence)

        # Success increases confidence
        confidence_trait = personality.get_trait("confidence")
        confidence_trait.adjust(0.1)

        assert personality.get_trait_value("confidence") == 0.6

    def test_personality_adaptation(self):
        """Agents adapt style to collaboration context."""
        personality = Personality("agent_1", "Alex")
        personality.set_expression_style(ExpressionStyle.CASUAL)

        # When working in formal context, adapt
        personality.set_expression_style(ExpressionStyle.FORMAL)

        assert personality.expression_style == ExpressionStyle.FORMAL

    def test_quirk_acquisition(self):
        """Agents can learn new quirks."""
        personality = Personality("agent_1", "Alex")
        assert len(personality.quirks) == 0

        # Learn new quirks
        personality.add_quirk("tells_jokes")
        personality.add_quirk("asks_questions")

        assert len(personality.quirks) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
