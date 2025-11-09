"""
Round 56: Agent Personality System
Agents have unique personalities that affect their reasoning, communication, and behavior.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


class PersonalityTrait(Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class ReasoningStyle(Enum):
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    BALANCED = "balanced"


class CommunicationStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    POETIC = "poetic"


class DecisionStrategy(Enum):
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    COLLABORATIVE = "collaborative"


@dataclass
class TraitScore:
    trait: PersonalityTrait
    value: float = 0.5
    expression: str = ""

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))

    def to_dict(self) -> Dict:
        return {"trait": self.trait.value, "value": self.value}


@dataclass
class PersonalityProfile:
    profile_id: str
    agent_id: str
    traits: Dict[PersonalityTrait, TraitScore] = field(default_factory=dict)
    reasoning_style: ReasoningStyle = ReasoningStyle.BALANCED
    communication_style: CommunicationStyle = CommunicationStyle.CASUAL
    decision_strategy: DecisionStrategy = DecisionStrategy.BALANCED
    archetype: str = "neutral"

    def set_trait(self, trait: PersonalityTrait, value: float) -> bool:
        if 0.0 <= value <= 1.0:
            self.traits[trait] = TraitScore(trait, value)
            return True
        return False

    def get_trait(self, trait: PersonalityTrait) -> Optional[float]:
        return self.traits.get(trait).value if trait in self.traits else None

    def calculate_consistency(self) -> float:
        if not self.traits:
            return 0.0
        values = [t.value for t in self.traits.values()]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return max(0.0, min(1.0, 1.0 - (variance * 0.5)))

    def to_dict(self) -> Dict:
        return {
            "profile_id": self.profile_id,
            "archetype": self.archetype,
            "consistency": self.calculate_consistency()
        }


class PersonalityModifier:
    @staticmethod
    def modify_confidence(base: float, trait: float) -> float:
        modified = base + (trait - 0.5) * 0.2
        return max(0.0, min(1.0, modified))

    @staticmethod
    def modify_risk(base: float, aggression: float) -> float:
        modified = base + (aggression - 0.5) * 0.3
        return max(0.0, min(1.0, modified))


class PersonalityArchetypes:
    CURIOUS = {"name": "Curious", PersonalityTrait.OPENNESS: 0.9}
    LOGICAL = {"name": "Logical", PersonalityTrait.CONSCIENTIOUSNESS: 0.9}
    FRIENDLY = {"name": "Friendly", PersonalityTrait.AGREEABLENESS: 0.95}

    @staticmethod
    def apply(profile: PersonalityProfile, arch: Dict) -> bool:
        for k, v in arch.items():
            if isinstance(k, PersonalityTrait):
                profile.set_trait(k, v)
            elif k == "name":
                profile.archetype = v
        return True


class PersonalityEngine:
    def __init__(self):
        self.profiles: Dict[str, PersonalityProfile] = {}

    def create_profile(self, agent_id: str) -> PersonalityProfile:
        pid = f"p_{len(self.profiles)}"
        p = PersonalityProfile(pid, agent_id)
        self.profiles[pid] = p
        return p

    def apply_archetype(self, pid: str, arch: Dict) -> bool:
        if pid in self.profiles:
            return PersonalityArchetypes.apply(self.profiles[pid], arch)
        return False

    def customize_trait(self, pid: str, trait: PersonalityTrait, value: float) -> bool:
        if pid in self.profiles:
            return self.profiles[pid].set_trait(trait, value)
        return False


# Tests
def test_trait_score():
    s = TraitScore(PersonalityTrait.OPENNESS, 0.8)
    assert s.value == 0.8

def test_trait_bounds():
    s = TraitScore(PersonalityTrait.OPENNESS, 1.5)
    assert s.value == 1.0

def test_profile_creation():
    p = PersonalityProfile("p1", "a1")
    assert p.profile_id == "p1"

def test_set_trait():
    p = PersonalityProfile("p1", "a1")
    assert p.set_trait(PersonalityTrait.OPENNESS, 0.8) is True

def test_get_trait():
    p = PersonalityProfile("p1", "a1")
    p.set_trait(PersonalityTrait.OPENNESS, 0.8)
    assert p.get_trait(PersonalityTrait.OPENNESS) == 0.8

def test_consistency():
    p = PersonalityProfile("p1", "a1")
    p.set_trait(PersonalityTrait.OPENNESS, 0.5)
    p.set_trait(PersonalityTrait.CONSCIENTIOUSNESS, 0.5)
    assert p.calculate_consistency() == 1.0

def test_modifier_confidence():
    assert PersonalityModifier.modify_confidence(0.5, 0.8) > 0.5

def test_modifier_risk():
    assert PersonalityModifier.modify_risk(0.5, 0.8) > 0.5

def test_archetype_curious():
    p = PersonalityProfile("p1", "a1")
    PersonalityArchetypes.apply(p, PersonalityArchetypes.CURIOUS)
    assert p.archetype == "Curious"

def test_engine_create():
    e = PersonalityEngine()
    p = e.create_profile("a1")
    assert p is not None

def test_engine_archetype():
    e = PersonalityEngine()
    p = e.create_profile("a1")
    assert e.apply_archetype(p.profile_id, PersonalityArchetypes.CURIOUS) is True

def test_engine_customize():
    e = PersonalityEngine()
    p = e.create_profile("a1")
    assert e.customize_trait(p.profile_id, PersonalityTrait.OPENNESS, 0.9) is True

def test_complete_workflow():
    e = PersonalityEngine()
    p = e.create_profile("curious_bot")
    assert e.apply_archetype(p.profile_id, PersonalityArchetypes.CURIOUS) is True
    assert e.customize_trait(p.profile_id, PersonalityTrait.OPENNESS, 0.95) is True
    pdict = p.to_dict()
    assert pdict["archetype"] == "Curious"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
