"""
Round 35: Agent Visual Representation

Enable agents to have distinct visual appearances that reflect their personality,
emotions, and capabilities. Visual representation makes agents feel alive and
helps players intuitively understand agent state.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CharacterType(Enum):
    """Base character types for agent avatars"""
    CYBERLING = "cyberling"  # Digital creature
    LIGHTBEING = "lightbeing"  # Ethereal entity
    ANDROID = "android"  # Mechanical being
    CREATURE = "creature"  # Organic-style creature


class ColorPalette(Enum):
    """Personality-driven color palettes"""
    WARM = "warm"  # Gold, orange, warm pink
    COOL = "cool"  # Gray-blue, indigo
    HOT = "hot"  # Red, orange-red, burgundy
    CALM = "calm"  # Sage, soft gray, muted teal
    BRIGHT = "bright"  # Bright primary colors
    NEUTRAL = "neutral"  # Balanced natural tones


class EyeState(Enum):
    """Emotional expression through eyes"""
    HAPPY = "happy"  # Wide, smiling eyes
    SAD = "sad"  # Drooping eyes, tear-like
    ANGRY = "angry"  # Narrowed, sharp eyes
    SURPRISED = "surprised"  # Wide, round eyes
    NEUTRAL = "neutral"  # Standard eyes
    CLOSED = "closed"  # Eyes closed (sleeping/resting)
    CONFUSED = "confused"  # Crossed or uncertain eyes


class PostureState(Enum):
    """Physical posture indicators"""
    CONFIDENT = "confident"  # Chest out, upright
    SLOUCHED = "slouched"  # Curved, dejected
    DEFENSIVE = "defensive"  # Guarded, withdrawn
    FORWARD_LEAN = "forward_lean"  # Interested, curious
    BACKWARD_LEAN = "backward_lean"  # Cautious, hesitant
    NEUTRAL = "neutral"  # Balanced, at ease


class StatusBadge(Enum):
    """Achievement and capability indicators"""
    TOOL_UNLOCKED = "tool_unlocked"
    EXPERTISE_BADGE = "expertise_badge"
    QUEST_COMPLETED = "quest_completed"
    BOND_MILESTONE = "bond_milestone"
    KNOWLEDGE_TIER = "knowledge_tier"


@dataclass
class ColorProfile:
    """Agent color palette based on personality"""
    primary: str  # Main color (hex)
    secondary: str  # Accent color (hex)
    tertiary: str  # Highlight color (hex)
    emotional_shift: Dict[str, str] = field(default_factory=dict)  # emotion -> color override

    def get_emotion_color(self, emotion: str) -> str:
        """Get color for specific emotion"""
        return self.emotional_shift.get(emotion, self.primary)

    def to_dict(self) -> Dict:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "tertiary": self.tertiary
        }


@dataclass
class EyeExpression:
    """Eye appearance and emotion"""
    state: EyeState
    brightness: float = 1.0  # 0.0-1.0, how bright/alert
    moisture: float = 0.0  # 0.0-1.0, teariness/brightness

    def get_visual_description(self) -> str:
        """Human-readable eye appearance"""
        descriptions = {
            EyeState.HAPPY: "bright, happy eyes with smile lines",
            EyeState.SAD: "drooping eyes with tear streaks",
            EyeState.ANGRY: "narrowed, sharp eyes glaring",
            EyeState.SURPRISED: "wide, round eyes",
            EyeState.NEUTRAL: "calm, steady eyes",
            EyeState.CLOSED: "eyes gently closed",
            EyeState.CONFUSED: "crossed or uncertain eyes"
        }
        return descriptions.get(self.state, "eyes")

    def to_dict(self) -> Dict:
        return {
            "state": self.state.value,
            "brightness": self.brightness,
            "moisture": self.moisture
        }


@dataclass
class PostureExpression:
    """Body posture and stance"""
    state: PostureState
    tension: float = 0.5  # 0.0-1.0, muscle tension
    alignment: float = 0.5  # 0.0-1.0, vertical alignment (0=forward, 1=backward)

    def get_visual_description(self) -> str:
        """Human-readable posture"""
        descriptions = {
            PostureState.CONFIDENT: "chest out, confident stance",
            PostureState.SLOUCHED: "curved, dejected posture",
            PostureState.DEFENSIVE: "guarded, protective stance",
            PostureState.FORWARD_LEAN: "leaning forward, interested",
            PostureState.BACKWARD_LEAN: "leaning back, hesitant",
            PostureState.NEUTRAL: "balanced, relaxed stance"
        }
        return descriptions.get(self.state, "standing")

    def to_dict(self) -> Dict:
        return {
            "state": self.state.value,
            "tension": self.tension,
            "alignment": self.alignment
        }


@dataclass
class StatusIndicator:
    """Visual status badge or indicator"""
    badge_type: StatusBadge
    label: str
    intensity: float = 1.0  # 0.0-1.0, how prominent

    def to_dict(self) -> Dict:
        return {
            "badge": self.badge_type.value,
            "label": self.label,
            "intensity": self.intensity
        }


@dataclass
class AgentAvatar:
    """Complete visual representation of an agent"""
    agent_id: str
    character_type: CharacterType
    color_palette: ColorPalette
    color_profile: ColorProfile
    name: str

    # Emotional expression
    eye_expression: EyeExpression = field(default_factory=lambda: EyeExpression(EyeState.NEUTRAL))
    posture_expression: PostureExpression = field(default_factory=lambda: PostureExpression(PostureState.NEUTRAL))

    # Status
    health: float = 1.0  # 0.0-1.0
    energy: float = 1.0  # 0.0-1.0
    happiness: float = 0.5  # 0.0-1.0

    # Visual customization
    size: float = 1.0  # 0.5-2.0, relative size
    glow_intensity: float = 0.5  # 0.0-1.0, emotional glow
    aura_color: Optional[str] = None  # Override aura color

    # Status badges
    status_badges: List[StatusIndicator] = field(default_factory=list)

    def get_aura_color(self) -> str:
        """Determine aura color from current state"""
        if self.aura_color:
            return self.aura_color

        # Derive from happiness/emotional state
        if self.happiness > 0.7:
            return "#FFD700"  # Gold (happy)
        elif self.happiness > 0.4:
            return "#87CEEB"  # Sky blue (neutral)
        else:
            return "#4B0082"  # Indigo (sad)

    def set_emotional_state(self, eye_state: EyeState, posture_state: PostureState) -> bool:
        """Update emotional expression"""
        self.eye_expression.state = eye_state
        self.posture_expression.state = posture_state

        # Auto-adjust happiness based on emotional state
        if eye_state == EyeState.HAPPY:
            self.happiness = min(1.0, self.happiness + 0.2)
        elif eye_state == EyeState.SAD:
            self.happiness = max(0.0, self.happiness - 0.2)
        elif eye_state == EyeState.ANGRY:
            self.happiness = max(0.0, self.happiness - 0.3)

        return True

    def update_health(self, amount: float) -> bool:
        """Update health (0.0-1.0)"""
        if not (-1.0 <= amount <= 1.0):
            return False
        self.health = max(0.0, min(1.0, self.health + amount))
        return True

    def update_energy(self, amount: float) -> bool:
        """Update energy (0.0-1.0)"""
        if not (-1.0 <= amount <= 1.0):
            return False
        self.energy = max(0.0, min(1.0, self.energy + amount))
        return True

    def add_status_badge(self, badge: StatusIndicator) -> bool:
        """Add achievement or status badge"""
        self.status_badges.append(badge)
        return True

    def get_visual_summary(self) -> Dict:
        """Get complete visual state summary"""
        return {
            "agent_id": self.agent_id,
            "character": self.character_type.value,
            "colors": self.color_palette.value,
            "eyes": self.eye_expression.get_visual_description(),
            "posture": self.posture_expression.get_visual_description(),
            "aura": self.get_aura_color(),
            "health": self.health,
            "energy": self.energy,
            "happiness": self.happiness,
            "badges": len(self.status_badges)
        }

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "character_type": self.character_type.value,
            "color_palette": self.color_palette.value,
            "name": self.name,
            "health": self.health,
            "energy": self.energy,
            "happiness": self.happiness,
            "eye_state": self.eye_expression.state.value,
            "posture_state": self.posture_expression.state.value,
            "aura_color": self.get_aura_color()
        }


@dataclass
class PersonalityVisuals:
    """Visual traits derived from personality"""
    personality_quirks: List[str]  # CURIOUS, CAUTIOUS, etc.
    speech_patterns: List[str]  # FORMAL, CASUAL, POETIC, etc.

    def get_base_color_palette(self) -> ColorPalette:
        """Determine color palette from personality"""
        # CURIOUS/BOLD → WARM, CAUTIOUS → COOL, ANALYTICAL → NEUTRAL
        if "CURIOUS" in self.personality_quirks or "BOLD" in self.personality_quirks:
            return ColorPalette.WARM
        elif "CAUTIOUS" in self.personality_quirks:
            return ColorPalette.COOL
        elif "ANALYTICAL" in self.personality_quirks:
            return ColorPalette.NEUTRAL
        else:
            return ColorPalette.CALM

    def get_characteristic_eye_state(self) -> EyeState:
        """Default eye state based on personality"""
        if "CURIOUS" in self.personality_quirks:
            return EyeState.SURPRISED
        elif "ANALYTICAL" in self.personality_quirks:
            return EyeState.NEUTRAL
        elif "BOLD" in self.personality_quirks:
            return EyeState.ANGRY  # Fierce/confident
        else:
            return EyeState.NEUTRAL

    def get_characteristic_posture(self) -> PostureState:
        """Default posture based on personality"""
        if "CURIOUS" in self.personality_quirks:
            return PostureState.FORWARD_LEAN
        elif "CAUTIOUS" in self.personality_quirks:
            return PostureState.BACKWARD_LEAN
        elif "BOLD" in self.personality_quirks:
            return PostureState.CONFIDENT
        else:
            return PostureState.NEUTRAL

    def get_size_modifier(self) -> float:
        """Size based on personality (0.7-1.3)"""
        if "BOLD" in self.personality_quirks:
            return 1.2  # Larger, takes up space
        elif "CAUTIOUS" in self.personality_quirks:
            return 0.8  # Smaller, less imposing
        else:
            return 1.0

    def to_dict(self) -> Dict:
        return {
            "quirks": self.personality_quirks,
            "speech_patterns": self.speech_patterns
        }


class AvatarFactory:
    """Create avatars based on personality and preferences"""

    def create_avatar(
        self,
        agent_id: str,
        name: str,
        character_type: CharacterType,
        personality_visuals: PersonalityVisuals,
        custom_colors: Optional[ColorProfile] = None
    ) -> AgentAvatar:
        """Create avatar from personality blueprint"""

        # Determine color palette from personality
        palette = personality_visuals.get_base_color_palette()

        # Use custom colors or create from palette
        if not custom_colors:
            custom_colors = self._palette_to_colors(palette)

        avatar = AgentAvatar(
            agent_id=agent_id,
            character_type=character_type,
            color_palette=palette,
            color_profile=custom_colors,
            name=name,
            size=personality_visuals.get_size_modifier()
        )

        # Set characteristic expression from personality
        eye_state = personality_visuals.get_characteristic_eye_state()
        posture_state = personality_visuals.get_characteristic_posture()
        avatar.set_emotional_state(eye_state, posture_state)

        return avatar

    def _palette_to_colors(self, palette: ColorPalette) -> ColorProfile:
        """Convert palette enum to actual colors"""
        palettes = {
            ColorPalette.WARM: ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
            ColorPalette.COOL: ColorProfile("#4682B4", "#6A5ACD", "#708090"),
            ColorPalette.HOT: ColorProfile("#FF0000", "#DC143C", "#8B0000"),
            ColorPalette.CALM: ColorProfile("#90EE90", "#708090", "#5F9EA0"),
            ColorPalette.BRIGHT: ColorProfile("#FF00FF", "#FFFF00", "#00CED1"),
            ColorPalette.NEUTRAL: ColorProfile("#A9A9A9", "#D3D3D3", "#BEBEBE")
        }
        return palettes.get(palette, ColorProfile("#808080", "#A9A9A9", "#D3D3D3"))


# ===== Tests =====

def test_avatar_creation():
    """Test creating basic avatar"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    assert avatar.agent_id == "a1"
    assert avatar.name == "Spark"
    assert avatar.health == 1.0


def test_emotional_expression():
    """Test updating emotional state"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    assert avatar.set_emotional_state(EyeState.HAPPY, PostureState.CONFIDENT) is True
    assert avatar.eye_expression.state == EyeState.HAPPY


def test_happiness_changes_with_emotion():
    """Test that happiness updates with emotional state"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark",
        happiness=0.5
    )
    avatar.set_emotional_state(EyeState.HAPPY, PostureState.CONFIDENT)
    assert avatar.happiness > 0.5


def test_aura_color_reflects_happiness():
    """Test that aura color changes with happiness"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark",
        happiness=0.8
    )
    aura = avatar.get_aura_color()
    assert aura == "#FFD700"  # Gold (happy)


def test_health_update():
    """Test updating health"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    assert avatar.update_health(-0.3) is True
    assert avatar.health == 0.7


def test_energy_update():
    """Test updating energy"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark",
        energy=1.0
    )
    assert avatar.update_energy(-0.5) is True
    assert avatar.energy == 0.5


def test_health_bounds():
    """Test health stays within bounds"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark",
        health=0.2
    )
    avatar.update_health(-1.0)
    assert avatar.health == 0.0


def test_status_badge_addition():
    """Test adding status badges"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    badge = StatusIndicator(StatusBadge.TOOL_UNLOCKED, "Vision Tool")
    assert avatar.add_status_badge(badge) is True
    assert len(avatar.status_badges) == 1


def test_eye_expression_description():
    """Test eye expression text descriptions"""
    expr = EyeExpression(EyeState.HAPPY)
    desc = expr.get_visual_description()
    assert "happy" in desc.lower()


def test_posture_expression_description():
    """Test posture expression text descriptions"""
    expr = PostureExpression(PostureState.CONFIDENT)
    desc = expr.get_visual_description()
    assert "confident" in desc.lower()


def test_personality_visuals_color_palette():
    """Test color palette derivation from personality"""
    pv = PersonalityVisuals(
        personality_quirks=["CURIOUS"],
        speech_patterns=["CASUAL"]
    )
    palette = pv.get_base_color_palette()
    assert palette == ColorPalette.WARM


def test_personality_visuals_eye_state():
    """Test eye state from personality"""
    pv = PersonalityVisuals(
        personality_quirks=["CURIOUS"],
        speech_patterns=["CASUAL"]
    )
    eye = pv.get_characteristic_eye_state()
    assert eye == EyeState.SURPRISED


def test_personality_visuals_posture():
    """Test posture from personality"""
    pv = PersonalityVisuals(
        personality_quirks=["BOLD"],
        speech_patterns=["FORMAL"]
    )
    posture = pv.get_characteristic_posture()
    assert posture == PostureState.CONFIDENT


def test_personality_visuals_size():
    """Test size modifier from personality"""
    pv_bold = PersonalityVisuals(
        personality_quirks=["BOLD"],
        speech_patterns=[]
    )
    assert pv_bold.get_size_modifier() == 1.2

    pv_cautious = PersonalityVisuals(
        personality_quirks=["CAUTIOUS"],
        speech_patterns=[]
    )
    assert pv_cautious.get_size_modifier() == 0.8


def test_avatar_factory_creation():
    """Test creating avatar from factory"""
    factory = AvatarFactory()
    pv = PersonalityVisuals(
        personality_quirks=["CURIOUS"],
        speech_patterns=["CASUAL"]
    )
    avatar = factory.create_avatar(
        agent_id="a1",
        name="Spark",
        character_type=CharacterType.CYBERLING,
        personality_visuals=pv
    )
    assert avatar.agent_id == "a1"
    assert avatar.name == "Spark"


def test_visual_summary():
    """Test getting complete visual summary"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    summary = avatar.get_visual_summary()
    assert "character" in summary
    assert "eyes" in summary
    assert "posture" in summary
    assert "aura" in summary


def test_avatar_serialization():
    """Test converting avatar to dict"""
    avatar = AgentAvatar(
        agent_id="a1",
        character_type=CharacterType.CYBERLING,
        color_palette=ColorPalette.WARM,
        color_profile=ColorProfile("#FFD700", "#FF8C00", "#FFB6C1"),
        name="Spark"
    )
    data = avatar.to_dict()
    assert data["agent_id"] == "a1"
    assert data["name"] == "Spark"


def test_complete_avatar_customization_workflow():
    """Test complete avatar creation and customization"""
    factory = AvatarFactory()

    # Create personality-driven avatar
    pv = PersonalityVisuals(
        personality_quirks=["CURIOUS", "EMPATHETIC"],
        speech_patterns=["POETIC", "CASUAL"]
    )
    avatar = factory.create_avatar(
        agent_id="explorer_ai",
        name="Luna",
        character_type=CharacterType.LIGHTBEING,
        personality_visuals=pv
    )

    # Customize appearance
    avatar.update_health(0.1)
    avatar.update_energy(0.2)
    avatar.set_emotional_state(EyeState.HAPPY, PostureState.FORWARD_LEAN)

    # Add achievements
    badge1 = StatusIndicator(StatusBadge.QUEST_COMPLETED, "First Discovery")
    badge2 = StatusIndicator(StatusBadge.EXPERTISE_BADGE, "Mathematics Expert")
    avatar.add_status_badge(badge1)
    avatar.add_status_badge(badge2)

    # Verify complete state
    summary = avatar.get_visual_summary()
    assert summary["agent_id"] == "explorer_ai"
    assert summary["badges"] == 2
    assert avatar.health == 1.0
    assert avatar.energy == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
