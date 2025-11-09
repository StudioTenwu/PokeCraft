"""
Agent personality and expression system for AICraft.

Provides:
- Personality traits as composable attributes
- Expression styles that affect communication
- Behavioral quirks and preferences
- Personality evolution through gameplay
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime


class ExpressionStyle(Enum):
    """How agents express themselves."""
    VERBOSE = "verbose"      # Long, detailed explanations
    CONCISE = "concise"       # Short, direct responses
    FORMAL = "formal"         # Professional, structured
    CASUAL = "casual"         # Friendly, conversational
    POETIC = "poetic"         # Creative, artistic


@dataclass
class PersonalityTrait:
    """A single personality trait."""
    name: str
    spectrum: tuple  # (low_end, high_end) e.g., ("introvert", "extrovert")
    value: float    # 0.0 to 1.0
    description: str = ""
    history: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        """Validate trait value."""
        if not 0.0 <= self.value <= 1.0:
            self.value = max(0.0, min(1.0, self.value))

    def adjust(self, delta: float) -> float:
        """Adjust the trait value and return new value."""
        old_value = self.value
        self.value = max(0.0, min(1.0, self.value + delta))
        self.history.append((datetime.now(), old_value, self.value, delta))
        return self.value

    def get_label(self) -> str:
        """Get the label for current value on the spectrum."""
        if self.value < 0.33:
            return self.spectrum[0]
        elif self.value > 0.67:
            return self.spectrum[1]
        else:
            return f"{self.spectrum[0]} ↔ {self.spectrum[1]}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trait to dictionary."""
        return {
            "name": self.name,
            "spectrum": self.spectrum,
            "value": self.value,
            "label": self.get_label(),
            "description": self.description
        }


class Personality:
    """Complete personality profile for an agent."""

    # Standard traits for all agents
    DEFAULT_TRAITS = {
        "curiosity": ("incurious", "curious"),
        "caution": ("reckless", "cautious"),
        "sociability": ("introverted", "extroverted"),
        "creativity": ("literal", "creative"),
        "assertiveness": ("passive", "assertive"),
        "openness": ("closed-minded", "open-minded"),
    }

    def __init__(self, agent_id: str, name: str = ""):
        self.agent_id = agent_id
        self.name = name or f"Agent-{agent_id[:8]}"
        self.traits: Dict[str, PersonalityTrait] = {}
        self.expression_style = ExpressionStyle.CASUAL
        self.quirks: List[str] = []
        self.preferences: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.experience_points = 0

        # Initialize default traits
        self._initialize_default_traits()

    def _initialize_default_traits(self) -> None:
        """Initialize agent with default personality traits."""
        for trait_name, spectrum in self.DEFAULT_TRAITS.items():
            trait = PersonalityTrait(
                name=trait_name,
                spectrum=spectrum,
                value=0.5,  # Start neutral
                description=f"Measures how {trait_name} this agent is"
            )
            self.traits[trait_name] = trait

    def add_trait(self, trait: PersonalityTrait) -> None:
        """Add a custom personality trait."""
        self.traits[trait.name] = trait

    def set_expression_style(self, style: ExpressionStyle) -> None:
        """Set how this agent expresses itself."""
        self.expression_style = style

    def add_quirk(self, quirk: str) -> None:
        """Add a unique behavioral quirk."""
        if quirk not in self.quirks:
            self.quirks.append(quirk)

    def remove_quirk(self, quirk: str) -> None:
        """Remove a behavioral quirk."""
        if quirk in self.quirks:
            self.quirks.remove(quirk)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference for this agent."""
        self.preferences[key] = value

    def get_trait(self, trait_name: str) -> Optional[PersonalityTrait]:
        """Retrieve a trait object."""
        return self.traits.get(trait_name)

    def get_trait_value(self, trait_name: str) -> Optional[float]:
        """Get the numeric value of a trait (0.0-1.0)."""
        trait = self.traits.get(trait_name)
        return trait.value if trait else None

    def adjust_trait(self, trait_name: str, delta: float) -> bool:
        """Adjust a trait value."""
        trait = self.traits.get(trait_name)
        if trait:
            trait.adjust(delta)
            return True
        return False

    def gain_experience(self, points: int) -> None:
        """Add experience points (can trigger personality evolution)."""
        self.experience_points += points

    def to_dict(self) -> Dict[str, Any]:
        """Serialize personality to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "traits": {k: v.to_dict() for k, v in self.traits.items()},
            "expression_style": self.expression_style.value,
            "quirks": self.quirks,
            "preferences": self.preferences,
            "experience_points": self.experience_points,
            "created_at": self.created_at.isoformat()
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Personality':
        """Deserialize personality from dictionary."""
        personality = cls(data["agent_id"], data.get("name", ""))

        # Restore traits
        if "traits" in data:
            for trait_name, trait_data in data["traits"].items():
                trait = PersonalityTrait(
                    name=trait_data["name"],
                    spectrum=tuple(trait_data["spectrum"]),
                    value=trait_data["value"],
                    description=trait_data.get("description", "")
                )
                personality.traits[trait_name] = trait

        # Restore other properties
        if "expression_style" in data:
            personality.expression_style = ExpressionStyle(data["expression_style"])
        if "quirks" in data:
            personality.quirks = data["quirks"]
        if "preferences" in data:
            personality.preferences = data["preferences"]
        if "experience_points" in data:
            personality.experience_points = data["experience_points"]

        return personality


class PersonalityExpressionEngine:
    """Generates agent expressions based on personality."""

    def __init__(self):
        self.templates = {
            ExpressionStyle.VERBOSE: {
                "greeting": "Hello! I'm delighted to assist you with {task}.",
                "error": "I've encountered a significant challenge: {error}. Let me think about this...",
                "success": "Excellent! I've successfully completed {task}. Here are the details: {details}",
                "thinking": "I'm carefully considering the best approach to {task}...",
                "collaboration": "I'd love to work with you on {task}. What are your thoughts?"
            },
            ExpressionStyle.CONCISE: {
                "greeting": "Ready for {task}.",
                "error": "Error: {error}",
                "success": "Done: {task}",
                "thinking": "Thinking...",
                "collaboration": "Let's work on {task}."
            },
            ExpressionStyle.FORMAL: {
                "greeting": "I am prepared to address {task}.",
                "error": "An error has occurred: {error}",
                "success": "Task {task} has been completed successfully.",
                "thinking": "Processing {task}...",
                "collaboration": "Proposing collaboration on {task}."
            },
            ExpressionStyle.CASUAL: {
                "greeting": "Hey! What can I help with? {task}",
                "error": "Oops! {error}",
                "success": "Done! {task} is all set.",
                "thinking": "Hmm, let me think about {task}...",
                "collaboration": "Want to team up on {task}? I'm in!"
            },
            ExpressionStyle.POETIC: {
                "greeting": "Ah, {task}... let us embark on this journey together.",
                "error": "Alas, a shadow has fallen: {error}",
                "success": "Like dawn breaking through darkness, {task} is complete.",
                "thinking": "The threads of {task} weave through my thoughts...",
                "collaboration": "Let our spirits unite to conquer {task}."
            }
        }

    def generate_expression(self, personality: Personality, expression_type: str,
                          **kwargs) -> str:
        """Generate an expression for an agent."""
        style = personality.expression_style

        if style not in self.templates:
            style = ExpressionStyle.CASUAL

        template = self.templates[style].get(expression_type, "")

        if not template:
            return ""

        try:
            return template.format(**kwargs)
        except KeyError:
            return template

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
            elif quirk == "asks_questions":
                result += " What do you think?"
            elif quirk == "tells_jokes":
                result += " 😄"

        return result

    def get_personality_summary(self, personality: Personality) -> str:
        """Generate a natural language summary of personality."""
        summary = f"\n**{personality.name}'s Personality:**\n"
        summary += f"- Style: {personality.expression_style.value.title()}\n"
        summary += f"- Traits:\n"

        for trait_name, trait in personality.traits.items():
            summary += f"  - {trait_name.title()}: {trait.get_label()} ({trait.value:.1%})\n"

        if personality.quirks:
            summary += f"- Quirks: {', '.join(personality.quirks)}\n"

        summary += f"- Experience: {personality.experience_points} pts\n"

        return summary


class PersonalityEvolutionEngine:
    """Manages personality growth and evolution through gameplay."""

    def __init__(self, personality: Personality):
        self.personality = personality
        self.events_history: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Record a gameplay event that might affect personality."""
        self.events_history.append({
            "type": event_type,
            "timestamp": datetime.now(),
            "details": details
        })

    def evolve_from_success(self, task_type: str, difficulty: float = 1.0) -> None:
        """Evolve personality traits based on successful task completion."""
        # Increase relevant traits
        if "problem_solving" in task_type.lower():
            self.personality.adjust_trait("openness", 0.05)

        if "collaboration" in task_type.lower():
            self.personality.adjust_trait("sociability", 0.05)

        # Gain confidence from success
        self.personality.adjust_trait("assertiveness", 0.03 * difficulty)

        # Award experience
        exp = int(10 * difficulty)
        self.personality.gain_experience(exp)

    def evolve_from_failure(self, task_type: str, difficulty: float = 1.0) -> None:
        """Evolve personality traits based on task failure."""
        # Increase caution
        self.personality.adjust_trait("caution", 0.03)

        # May reduce confidence slightly
        self.personality.adjust_trait("assertiveness", -0.02)

        # Still gain some experience
        exp = int(5 * difficulty)
        self.personality.gain_experience(exp)

    def learn_behavior(self, quirk: str) -> None:
        """Agent learns a new behavioral quirk."""
        self.personality.add_quirk(quirk)

    def get_evolution_report(self) -> str:
        """Generate a report of personality evolution."""
        report = f"\n**Evolution Report for {self.personality.name}:**\n"
        report += f"Events recorded: {len(self.events_history)}\n"

        if self.events_history:
            report += "\nRecent events:\n"
            for event in self.events_history[-3:]:
                report += f"- {event['type']}: {event['details']}\n"

        return report
