"""
Round 15: Agent Personality & Customization System

This module implements agent personality traits that affect behavior,
communication style, and decision-making. Players can customize their
agents' personalities through trait selection and development.

Key concepts:
- Personality traits (creativity, empathy, curiosity, caution, dominance)
- Trait expression in communication and behavior
- Personality evolution through experiences
- Personality-based skill affinity
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class PersonalityTrait(Enum):
    """Core personality dimensions for AI agents"""
    CREATIVITY = "creativity"
    EMPATHY = "empathy"
    CURIOSITY = "curiosity"
    CAUTION = "caution"
    DOMINANCE = "dominance"


class CommunicationStyle(Enum):
    """How agents express themselves"""
    FORMAL = "formal"
    CASUAL = "casual"
    POETIC = "poetic"
    ANALYTICAL = "analytical"
    HUMOROUS = "humorous"


@dataclass
class PersonalityTraitValue:
    """Individual trait with strength and expression"""
    trait: PersonalityTrait
    strength: float = 0.5
    expression_style: CommunicationStyle = CommunicationStyle.CASUAL
    unlock_level: int = 1

    def boost(self, amount: float) -> bool:
        """Boost trait strength (capped at 1.0)"""
        new_strength = self.strength + amount
        if not (0.0 <= new_strength <= 1.0):
            return False
        self.strength = new_strength
        return True

    def unlock_new_expression(self) -> bool:
        """Unlock deeper expression of this trait"""
        if self.unlock_level >= 10:
            return False
        self.unlock_level += 1
        return True

    def to_dict(self) -> Dict:
        return {
            "trait": self.trait.value,
            "strength": self.strength,
            "expression_style": self.expression_style.value,
            "unlock_level": self.unlock_level
        }


@dataclass
class PersonalityProfile:
    """Complete personality configuration for an agent"""
    agent_id: str
    primary_style: CommunicationStyle
    base_traits: Dict[PersonalityTrait, PersonalityTraitValue] = field(default_factory=dict)
    quirks: List[str] = field(default_factory=list)
    development_stage: int = 1

    def __post_init__(self):
        """Initialize with default trait values if empty"""
        if not self.base_traits:
            self.base_traits = {
                trait: PersonalityTraitValue(
                    trait=trait,
                    strength=0.5,
                    expression_style=CommunicationStyle.CASUAL,
                    unlock_level=1
                )
                for trait in PersonalityTrait
            }

    def get_trait_strength(self, trait: PersonalityTrait) -> float:
        """Get the strength of a specific trait"""
        if trait not in self.base_traits:
            return 0.0
        return self.base_traits[trait].strength

    def set_trait_strength(self, trait: PersonalityTrait, strength: float) -> bool:
        """Set trait strength (0.0-1.0)"""
        if not (0.0 <= strength <= 1.0):
            return False
        if trait not in self.base_traits:
            self.base_traits[trait] = PersonalityTraitValue(trait, strength, CommunicationStyle.CASUAL, 1)
        else:
            self.base_traits[trait].strength = strength
        return True

    def express_trait(self, trait: PersonalityTrait, action: str) -> str:
        """Get expression of how agent would handle action based on trait"""
        strength = self.get_trait_strength(trait)

        if strength < 0.3:
            return f"[Weak {trait.value}] {action}"
        elif strength < 0.7:
            return f"[Moderate {trait.value}] {action}"
        else:
            return f"[Strong {trait.value}] {action}"

    def develop_personality(self, experience: str) -> bool:
        """Develop personality based on experience (growth)"""
        if self.development_stage >= 100:
            return False
        self.development_stage = min(100, self.development_stage + 5)
        return True

    def add_quirk(self, quirk: str) -> bool:
        """Add a unique personality quirk"""
        if quirk in self.quirks:
            return False
        self.quirks.append(quirk)
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "base_traits": {k.value: v.to_dict() for k, v in self.base_traits.items()},
            "primary_style": self.primary_style.value,
            "quirks": self.quirks,
            "development_stage": self.development_stage
        }


class PersonalitySkillAfinity:
    """Maps personality traits to skill aptitudes"""

    TRAIT_SKILL_MAP = {
        PersonalityTrait.CREATIVITY: ["art", "music", "writing", "design"],
        PersonalityTrait.EMPATHY: ["teaching", "counseling", "collaboration", "mediation"],
        PersonalityTrait.CURIOSITY: ["research", "exploration", "learning", "experimentation"],
        PersonalityTrait.CAUTION: ["planning", "risk_management", "verification", "testing"],
        PersonalityTrait.DOMINANCE: ["leadership", "negotiation", "command", "strategy"],
    }

    @staticmethod
    def get_skill_bonus(profile: PersonalityProfile, skill: str) -> float:
        """Calculate skill bonus based on personality traits"""
        bonus = 0.0
        for trait, skills in PersonalitySkillAfinity.TRAIT_SKILL_MAP.items():
            if skill in skills:
                bonus += profile.get_trait_strength(trait) * 0.2
        return min(1.0, bonus)

    @staticmethod
    def get_affinity_score(profile: PersonalityProfile, skill: str) -> float:
        """Get 0-1 affinity score for a skill"""
        affinity = 0.0
        for trait, skills in PersonalitySkillAfinity.TRAIT_SKILL_MAP.items():
            if skill in skills:
                affinity += profile.get_trait_strength(trait)
        return min(1.0, affinity / 5.0)


class PersonalityDatabase:
    """Manage and evolve agent personalities"""

    def __init__(self):
        self.profiles: Dict[str, PersonalityProfile] = {}
        self.personality_history: Dict[str, List[Dict]] = {}

    def create_profile(self, agent_id: str, primary_style: CommunicationStyle) -> PersonalityProfile:
        """Create new personality profile for agent"""
        profile = PersonalityProfile(
            agent_id=agent_id,
            primary_style=primary_style,
            base_traits={},
            quirks=[],
            development_stage=1
        )
        self.profiles[agent_id] = profile
        self.personality_history[agent_id] = []
        return profile

    def get_profile(self, agent_id: str) -> Optional[PersonalityProfile]:
        """Retrieve agent's personality profile"""
        return self.profiles.get(agent_id)

    def record_personality_state(self, agent_id: str) -> bool:
        """Snapshot personality state for history tracking"""
        profile = self.get_profile(agent_id)
        if not profile:
            return False
        self.personality_history[agent_id].append(profile.to_dict())
        return True

    def evolve_trait(self, agent_id: str, trait: PersonalityTrait, amount: float) -> bool:
        """Evolve a trait based on experiences"""
        profile = self.get_profile(agent_id)
        if not profile:
            return False
        if trait not in profile.base_traits:
            profile.base_traits[trait] = PersonalityTraitValue(trait, 0.5, CommunicationStyle.CASUAL, 1)
        return profile.base_traits[trait].boost(amount)

    def get_personality_evolution(self, agent_id: str) -> List[Dict]:
        """Get personality evolution history"""
        return self.personality_history.get(agent_id, [])
