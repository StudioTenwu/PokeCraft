"""
Round 15: Agent Personality & Customization System - Tests

Comprehensive test suite for agent personality traits that affect behavior,
communication style, and decision-making.
"""

import pytest
from personality_system import (
    PersonalityTrait,
    CommunicationStyle,
    PersonalityTraitValue,
    PersonalityProfile,
    PersonalitySkillAfinity,
    PersonalityDatabase
)


def test_personality_trait_value_creation():
    """Test individual trait creation and management"""
    trait = PersonalityTraitValue(
        trait=PersonalityTrait.CREATIVITY,
        strength=0.6,
        expression_style=CommunicationStyle.POETIC,
        unlock_level=2
    )
    assert trait.trait == PersonalityTrait.CREATIVITY
    assert trait.strength == 0.6
    assert trait.unlock_level == 2


def test_personality_trait_boost():
    """Test trait strength boosting"""
    trait = PersonalityTraitValue(
        trait=PersonalityTrait.EMPATHY,
        strength=0.5,
        expression_style=CommunicationStyle.CASUAL,
        unlock_level=1
    )
    assert trait.boost(0.2) is True
    assert trait.strength == 0.7
    assert trait.boost(0.5) is False


def test_personality_trait_unlock_expression():
    """Test unlocking deeper trait expression"""
    trait = PersonalityTraitValue(
        trait=PersonalityTrait.CURIOSITY,
        strength=0.8,
        expression_style=CommunicationStyle.ANALYTICAL,
        unlock_level=3
    )
    assert trait.unlock_new_expression() is True
    assert trait.unlock_level == 4

    for _ in range(20):
        trait.unlock_new_expression()
    assert trait.unlock_level == 10


def test_personality_profile_initialization():
    """Test personality profile default initialization"""
    profile = PersonalityProfile(
        agent_id="agent_001",
        primary_style=CommunicationStyle.CASUAL,
    )
    assert profile.agent_id == "agent_001"
    assert len(profile.base_traits) == 5
    assert all(t.strength == 0.5 for t in profile.base_traits.values())


def test_personality_profile_trait_management():
    """Test trait strength management in profile"""
    profile = PersonalityProfile(
        agent_id="agent_002",
        primary_style=CommunicationStyle.ANALYTICAL,
    )

    assert profile.set_trait_strength(PersonalityTrait.CREATIVITY, 0.9) is True
    assert profile.get_trait_strength(PersonalityTrait.CREATIVITY) == 0.9

    assert profile.set_trait_strength(PersonalityTrait.EMPATHY, 1.5) is False


def test_personality_trait_expression():
    """Test how traits express in communication"""
    profile = PersonalityProfile(
        agent_id="agent_003",
        primary_style=CommunicationStyle.POETIC,
    )

    profile.set_trait_strength(PersonalityTrait.CREATIVITY, 0.8)
    expression = profile.express_trait(PersonalityTrait.CREATIVITY, "Write a poem")
    assert "Strong creativity" in expression

    profile.set_trait_strength(PersonalityTrait.CAUTION, 0.2)
    expression = profile.express_trait(PersonalityTrait.CAUTION, "Take a risk")
    assert "Weak caution" in expression


def test_personality_development():
    """Test personality maturation over time"""
    profile = PersonalityProfile(
        agent_id="agent_004",
        primary_style=CommunicationStyle.CASUAL,
    )

    assert profile.development_stage == 1
    assert profile.develop_personality("first_conversation") is True
    assert profile.development_stage == 6

    for _ in range(100):
        profile.develop_personality("experience")
    assert profile.development_stage == 100


def test_personality_quirks():
    """Test adding personality quirks"""
    profile = PersonalityProfile(
        agent_id="agent_005",
        primary_style=CommunicationStyle.HUMOROUS,
    )

    assert profile.add_quirk("speaks in rhymes") is True
    assert profile.add_quirk("loves puns") is True
    assert profile.add_quirk("speaks in rhymes") is False
    assert len(profile.quirks) == 2


def test_skill_affinity_calculation():
    """Test personality-based skill affinity"""
    profile = PersonalityProfile(
        agent_id="agent_006",
        primary_style=CommunicationStyle.POETIC,
    )

    profile.set_trait_strength(PersonalityTrait.CREATIVITY, 0.9)
    profile.set_trait_strength(PersonalityTrait.CURIOSITY, 0.8)

    art_affinity = PersonalitySkillAfinity.get_affinity_score(profile, "art")
    assert art_affinity > 0.15

    profile.set_trait_strength(PersonalityTrait.DOMINANCE, 0.7)
    leadership_affinity = PersonalitySkillAfinity.get_affinity_score(profile, "leadership")
    assert leadership_affinity > 0.1


def test_skill_bonus_calculation():
    """Test skill bonus from personality traits"""
    profile = PersonalityProfile(
        agent_id="agent_007",
        primary_style=CommunicationStyle.ANALYTICAL,
    )

    profile.set_trait_strength(PersonalityTrait.CAUTION, 0.8)
    bonus = PersonalitySkillAfinity.get_skill_bonus(profile, "verification")
    assert bonus > 0.1
    assert bonus <= 1.0


def test_personality_database_creation():
    """Test personality database management"""
    db = PersonalityDatabase()
    profile = db.create_profile("agent_008", CommunicationStyle.CASUAL)

    assert profile.agent_id == "agent_008"
    assert db.get_profile("agent_008") is not None
    assert db.get_profile("nonexistent") is None


def test_personality_evolution_tracking():
    """Test tracking personality changes over time"""
    db = PersonalityDatabase()
    profile = db.create_profile("agent_009", CommunicationStyle.ANALYTICAL)

    assert db.record_personality_state("agent_009") is True

    assert db.evolve_trait("agent_009", PersonalityTrait.CREATIVITY, 0.1) is True

    assert db.record_personality_state("agent_009") is True

    history = db.get_personality_evolution("agent_009")
    assert len(history) == 2
    assert history[0]["base_traits"][PersonalityTrait.CREATIVITY.value]["strength"] < history[1]["base_traits"][PersonalityTrait.CREATIVITY.value]["strength"]


def test_personality_profile_serialization():
    """Test personality profile to_dict conversion"""
    profile = PersonalityProfile(
        agent_id="agent_010",
        primary_style=CommunicationStyle.POETIC,
    )
    profile.quirks = ["speaks in metaphors"]
    profile.development_stage = 25

    profile.set_trait_strength(PersonalityTrait.CREATIVITY, 0.9)

    data = profile.to_dict()
    assert data["agent_id"] == "agent_010"
    assert data["primary_style"] == "poetic"
    assert "speaks in metaphors" in data["quirks"]
    assert data["base_traits"][PersonalityTrait.CREATIVITY.value]["strength"] == 0.9


def test_complete_personality_customization_workflow():
    """Test complete personality creation and customization workflow"""
    db = PersonalityDatabase()

    profile = db.create_profile("creative_agent", CommunicationStyle.POETIC)

    profile.set_trait_strength(PersonalityTrait.CREATIVITY, 0.95)
    profile.set_trait_strength(PersonalityTrait.CURIOSITY, 0.8)
    profile.set_trait_strength(PersonalityTrait.CAUTION, 0.2)

    profile.add_quirk("always uses metaphors")
    profile.add_quirk("asks questions about everything")

    for _ in range(5):
        profile.develop_personality("creative_experience")

    db.record_personality_state("creative_agent")

    assert profile.get_trait_strength(PersonalityTrait.CREATIVITY) == 0.95
    assert len(profile.quirks) == 2
    assert profile.development_stage > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
