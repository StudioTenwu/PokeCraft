"""
Round 43: System Integration Layer

Connect all 42 existing systems so learning environments, custom tools,
mentorship, and empathy affect agent development meaningfully. This is the
critical integration layer that makes the microworld coherent.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class IntegrationEventType(Enum):
    """Types of events flowing between systems"""
    CHALLENGE_COMPLETED = "challenge_completed"
    TOOL_CREATED = "tool_created"
    TOOL_USED = "tool_used"
    MENTORSHIP_GOAL_REACHED = "mentorship_goal_reached"
    EMPATHY_INSIGHT_GAINED = "empathy_insight_gained"
    SKILL_UNLOCKED = "skill_unlocked"
    KNOWLEDGE_ACQUIRED = "knowledge_acquired"


@dataclass
class IntegrationEvent:
    """Event representing cross-system interaction"""
    event_id: str
    event_type: IntegrationEventType
    agent_id: str
    source_system: str  # e.g., "learning_env", "custom_tools"
    target_system: str  # e.g., "agent_core", "personality"
    data: Dict = field(default_factory=dict)
    processed: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.event_id,
            "type": self.event_type.value,
            "agent_id": self.agent_id,
            "processed": self.processed
        }


@dataclass
class IntegrationMapping:
    """Defines how events from one system affect another"""
    source_system: str
    target_system: str
    event_type: IntegrationEventType
    processor_func: str  # Name of function to call
    multiplier: float = 1.0  # How much impact (0.0-2.0)

    def to_dict(self) -> Dict:
        return {
            "from": self.source_system,
            "to": self.target_system,
            "event": self.event_type.value,
            "multiplier": self.multiplier
        }


class IntegrationBridge:
    """
    Central system connecting all subsystems.
    When learning_env completes a challenge, this system:
    1. Creates integration event
    2. Finds relevant mappings
    3. Calls appropriate handler functions
    4. Updates agent development
    """

    def __init__(self):
        self.events: Dict[str, IntegrationEvent] = {}
        self.mappings: List[IntegrationMapping] = []
        self.event_handlers: Dict[str, callable] = {}
        self.agent_effects: Dict[str, Dict] = {}  # agent_id -> effects log

    def register_mapping(self, mapping: IntegrationMapping) -> bool:
        """Register how one system affects another"""
        self.mappings.append(mapping)
        return True

    def register_handler(self, event_key: str, handler: callable) -> bool:
        """Register function to handle specific event type"""
        self.event_handlers[event_key] = handler
        return True

    def process_event(self, event: IntegrationEvent) -> bool:
        """Process integration event and apply effects"""
        self.events[event.event_id] = event

        # Find all mappings for this event type
        relevant_mappings = [
            m for m in self.mappings
            if m.source_system == event.source_system
            and m.event_type == event.event_type
        ]

        # Apply effects from each mapping
        for mapping in relevant_mappings:
            handler_key = f"{mapping.source_system}_{mapping.event_type.value}"
            if handler_key in self.event_handlers:
                effect = self.event_handlers[handler_key](event, mapping)
                if effect:
                    self._record_effect(event.agent_id, mapping.target_system, effect)

        event.processed = True
        return True

    def _record_effect(self, agent_id: str, target_system: str, effect: Dict) -> None:
        """Record the effect on an agent"""
        if agent_id not in self.agent_effects:
            self.agent_effects[agent_id] = {}

        if target_system not in self.agent_effects[agent_id]:
            self.agent_effects[agent_id][target_system] = []

        self.agent_effects[agent_id][target_system].append(effect)

    def get_agent_effects(self, agent_id: str) -> Dict:
        """Get all effects applied to agent"""
        return self.agent_effects.get(agent_id, {})

    def to_dict(self) -> Dict:
        return {
            "total_events": len(self.events),
            "processed_events": sum(1 for e in self.events.values() if e.processed),
            "mappings": len(self.mappings),
            "agents_affected": len(self.agent_effects)
        }


class LearningToAgentIntegration:
    """Specific integration: Learning environment → Agent development"""

    @staticmethod
    def challenge_affects_expertise(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Challenge completion increases agent expertise in skill domain"""
        skill_name = event.data.get("skill", "general")
        performance = event.data.get("performance", 0.5)

        # Effect multiplied by performance quality
        expertise_gain = 0.1 * performance * mapping.multiplier

        return {
            "system": "knowledge_base",
            "effect": "expertise_increased",
            "skill": skill_name,
            "amount": expertise_gain,
            "source": "challenge_completion"
        }

    @staticmethod
    def challenge_affects_confidence(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Challenge completion affects agent confidence"""
        performance = event.data.get("performance", 0.5)

        # Higher performance = higher confidence boost
        confidence_boost = 0.15 * performance * mapping.multiplier

        return {
            "system": "personality",
            "effect": "confidence_increased",
            "amount": confidence_boost,
            "source": "challenge_success"
        }

    @staticmethod
    def challenge_affects_emotion(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Challenge completion triggers positive emotion"""
        performance = event.data.get("performance", 0.5)

        if performance > 0.7:
            emotion = "JOY"
            intensity = 0.8 * mapping.multiplier
        elif performance > 0.4:
            emotion = "SATISFACTION"
            intensity = 0.5 * mapping.multiplier
        else:
            emotion = "FRUSTRATION"
            intensity = 0.6 * mapping.multiplier

        return {
            "system": "emotion_system",
            "effect": "emotion_triggered",
            "emotion": emotion,
            "intensity": intensity,
            "source": "challenge_outcome"
        }


class ToolToAgentIntegration:
    """Specific integration: Custom tools → Agent capabilities"""

    @staticmethod
    def tool_creation_unlocks_capability(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Custom tool creation unlocks new agent capability"""
        tool_reliability = event.data.get("reliability", 0.5)
        tool_inputs = event.data.get("inputs", [])

        return {
            "system": "agent_toolkit",
            "effect": "tool_added",
            "tool_count": len(tool_inputs),
            "reliability": tool_reliability,
            "source": "tool_creation"
        }

    @staticmethod
    def tool_usage_improves_skill(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Using custom tool improves related skill"""
        tool_domain = event.data.get("domain", "general")
        success = event.data.get("success", False)

        if not success:
            return {"system": "knowledge_base", "effect": "no_improvement"}

        skill_improvement = 0.05 * mapping.multiplier

        return {
            "system": "knowledge_base",
            "effect": "skill_improved",
            "skill": tool_domain,
            "amount": skill_improvement,
            "source": "tool_usage"
        }


class MentorshipToAgentIntegration:
    """Specific integration: Mentorship goals → Agent personality growth"""

    @staticmethod
    def mentorship_goal_affects_personality(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """Completing mentorship goal shapes agent personality"""
        goal_type = event.data.get("goal_type", "learning")
        xp_earned = event.data.get("xp", 0)

        personality_growth = xp_earned / 100.0 * mapping.multiplier

        return {
            "system": "personality",
            "effect": "personality_shaped",
            "growth": personality_growth,
            "goal_type": goal_type,
            "source": "mentorship_achievement"
        }


class EmpathyToRelationshipIntegration:
    """Specific integration: Empathy experiences → Relationship deepening"""

    @staticmethod
    def empathy_deepens_bond(event: IntegrationEvent, mapping: IntegrationMapping) -> Dict:
        """First-person experience deepens relationship understanding"""
        confusion_level = event.data.get("confusion", 0.5)
        duration = event.data.get("duration", 1.0)

        # Less confusion + longer duration = stronger bond
        bond_strength = (1.0 - confusion_level) * (duration / 10.0) * mapping.multiplier

        return {
            "system": "relationships",
            "effect": "bond_deepened",
            "bond_increase": bond_strength,
            "source": "empathy_experience"
        }


class SystemIntegrationManager:
    """High-level manager coordinating all system integrations"""

    def __init__(self):
        self.bridge = IntegrationBridge()
        self._setup_default_mappings()
        self._setup_handlers()

    def _setup_default_mappings(self) -> None:
        """Register all default system mappings"""
        # Learning environment → Agent development
        self.bridge.register_mapping(IntegrationMapping(
            "learning_env", "knowledge_base",
            IntegrationEventType.CHALLENGE_COMPLETED,
            "challenge_affects_expertise", 1.0
        ))
        self.bridge.register_mapping(IntegrationMapping(
            "learning_env", "personality",
            IntegrationEventType.CHALLENGE_COMPLETED,
            "challenge_affects_confidence", 0.8
        ))
        self.bridge.register_mapping(IntegrationMapping(
            "learning_env", "emotion_system",
            IntegrationEventType.CHALLENGE_COMPLETED,
            "challenge_affects_emotion", 1.0
        ))

        # Custom tools → Agent toolkit
        self.bridge.register_mapping(IntegrationMapping(
            "custom_tools", "agent_toolkit",
            IntegrationEventType.TOOL_CREATED,
            "tool_creation_unlocks_capability", 1.0
        ))
        self.bridge.register_mapping(IntegrationMapping(
            "custom_tools", "knowledge_base",
            IntegrationEventType.TOOL_USED,
            "tool_usage_improves_skill", 0.7
        ))

        # Mentorship → Personality
        self.bridge.register_mapping(IntegrationMapping(
            "mentorship", "personality",
            IntegrationEventType.MENTORSHIP_GOAL_REACHED,
            "mentorship_goal_affects_personality", 1.2
        ))

        # Empathy → Relationships
        self.bridge.register_mapping(IntegrationMapping(
            "empathy", "relationships",
            IntegrationEventType.EMPATHY_INSIGHT_GAINED,
            "empathy_deepens_bond", 0.9
        ))

    def _setup_handlers(self) -> None:
        """Register event handlers"""
        self.bridge.register_handler(
            "learning_env_challenge_completed",
            LearningToAgentIntegration.challenge_affects_expertise
        )
        self.bridge.register_handler(
            "custom_tools_tool_created",
            ToolToAgentIntegration.tool_creation_unlocks_capability
        )
        self.bridge.register_handler(
            "mentorship_mentorship_goal_reached",
            MentorshipToAgentIntegration.mentorship_goal_affects_personality
        )
        self.bridge.register_handler(
            "empathy_empathy_insight_gained",
            EmpathyToRelationshipIntegration.empathy_deepens_bond
        )

    def process_challenge_completion(self, agent_id: str, skill: str, performance: float) -> bool:
        """Process learning environment challenge completion"""
        event = IntegrationEvent(
            f"event_challenge_{agent_id}_{skill}",
            IntegrationEventType.CHALLENGE_COMPLETED,
            agent_id,
            "learning_env",
            "agent_core",
            {"skill": skill, "performance": performance}
        )
        return self.bridge.process_event(event)

    def process_tool_creation(self, agent_id: str, tool_reliability: float, inputs_count: int) -> bool:
        """Process custom tool creation"""
        event = IntegrationEvent(
            f"event_tool_{agent_id}",
            IntegrationEventType.TOOL_CREATED,
            agent_id,
            "custom_tools",
            "agent_toolkit",
            {"reliability": tool_reliability, "inputs": list(range(inputs_count))}
        )
        return self.bridge.process_event(event)

    def process_mentorship_goal(self, agent_id: str, goal_type: str, xp_earned: float) -> bool:
        """Process mentorship goal completion"""
        event = IntegrationEvent(
            f"event_mentor_{agent_id}_{goal_type}",
            IntegrationEventType.MENTORSHIP_GOAL_REACHED,
            agent_id,
            "mentorship",
            "personality",
            {"goal_type": goal_type, "xp": xp_earned}
        )
        return self.bridge.process_event(event)

    def process_empathy_experience(self, agent_id: str, confusion: float, duration: float) -> bool:
        """Process empathy experience insight"""
        event = IntegrationEvent(
            f"event_empathy_{agent_id}",
            IntegrationEventType.EMPATHY_INSIGHT_GAINED,
            agent_id,
            "empathy",
            "relationships",
            {"confusion": confusion, "duration": duration}
        )
        return self.bridge.process_event(event)

    def get_agent_development_summary(self, agent_id: str) -> Dict:
        """Get how all systems have affected agent development"""
        effects = self.bridge.get_agent_effects(agent_id)

        summary = {
            "agent_id": agent_id,
            "total_effects": sum(len(v) for v in effects.values()),
            "systems_affected": list(effects.keys()),
            "effects_by_system": {k: len(v) for k, v in effects.items()},
            "expertise_growth": sum(1 for v in effects.get("knowledge_base", [])
                                  if v.get("effect") == "expertise_increased"),
            "personality_growth": sum(1 for v in effects.get("personality", [])
                                    if v.get("effect") in ["confidence_increased", "personality_shaped"]),
            "relationship_growth": sum(1 for v in effects.get("relationships", [])
                                     if v.get("effect") == "bond_deepened")
        }
        return summary

    def to_dict(self) -> Dict:
        return {
            "bridge_status": self.bridge.to_dict(),
            "total_mappings": len(self.bridge.mappings),
            "handlers_registered": len(self.bridge.event_handlers)
        }


# ===== Tests =====

def test_integration_event_creation():
    """Test creating integration event"""
    event = IntegrationEvent(
        "ev1",
        IntegrationEventType.CHALLENGE_COMPLETED,
        "a1",
        "learning_env",
        "agent_core"
    )
    assert event.event_id == "ev1"
    assert not event.processed


def test_integration_mapping():
    """Test integration mapping"""
    mapping = IntegrationMapping(
        "learning_env",
        "knowledge_base",
        IntegrationEventType.CHALLENGE_COMPLETED,
        "handler_func"
    )
    assert mapping.source_system == "learning_env"


def test_integration_bridge():
    """Test integration bridge creation"""
    bridge = IntegrationBridge()
    assert len(bridge.mappings) == 0


def test_register_mapping():
    """Test registering mapping"""
    bridge = IntegrationBridge()
    mapping = IntegrationMapping(
        "sys1", "sys2",
        IntegrationEventType.CHALLENGE_COMPLETED,
        "func"
    )
    assert bridge.register_mapping(mapping) is True


def test_learning_to_agent_integration():
    """Test learning environment affects agent expertise"""
    event = IntegrationEvent(
        "ev1", IntegrationEventType.CHALLENGE_COMPLETED, "a1",
        "learning_env", "knowledge_base",
        {"skill": "reasoning", "performance": 0.8}
    )
    mapping = IntegrationMapping(
        "learning_env", "knowledge_base",
        IntegrationEventType.CHALLENGE_COMPLETED, "func", 1.0
    )

    effect = LearningToAgentIntegration.challenge_affects_expertise(event, mapping)
    assert effect["effect"] == "expertise_increased"
    assert effect["skill"] == "reasoning"


def test_challenge_affects_emotion():
    """Test challenge completion affects emotion"""
    event = IntegrationEvent(
        "ev1", IntegrationEventType.CHALLENGE_COMPLETED, "a1",
        "learning_env", "emotion_system",
        {"performance": 0.8}
    )
    mapping = IntegrationMapping(
        "learning_env", "emotion_system",
        IntegrationEventType.CHALLENGE_COMPLETED, "func", 1.0
    )

    effect = LearningToAgentIntegration.challenge_affects_emotion(event, mapping)
    assert effect["emotion"] == "JOY"


def test_tool_creation_affects_agent():
    """Test custom tool creation unlocks capability"""
    event = IntegrationEvent(
        "ev1", IntegrationEventType.TOOL_CREATED, "a1",
        "custom_tools", "agent_toolkit",
        {"reliability": 0.9, "inputs": ["text", "data"]}
    )
    mapping = IntegrationMapping(
        "custom_tools", "agent_toolkit",
        IntegrationEventType.TOOL_CREATED, "func", 1.0
    )

    effect = ToolToAgentIntegration.tool_creation_unlocks_capability(event, mapping)
    assert effect["effect"] == "tool_added"


def test_mentorship_affects_personality():
    """Test mentorship goal shapes personality"""
    event = IntegrationEvent(
        "ev1", IntegrationEventType.MENTORSHIP_GOAL_REACHED, "a1",
        "mentorship", "personality",
        {"goal_type": "learning", "xp": 100}
    )
    mapping = IntegrationMapping(
        "mentorship", "personality",
        IntegrationEventType.MENTORSHIP_GOAL_REACHED, "func", 1.2
    )

    effect = MentorshipToAgentIntegration.mentorship_goal_affects_personality(event, mapping)
    assert effect["effect"] == "personality_shaped"
    assert effect["growth"] > 0


def test_empathy_deepens_bond():
    """Test empathy experience deepens relationship"""
    event = IntegrationEvent(
        "ev1", IntegrationEventType.EMPATHY_INSIGHT_GAINED, "a1",
        "empathy", "relationships",
        {"confusion": 0.2, "duration": 5.0}
    )
    mapping = IntegrationMapping(
        "empathy", "relationships",
        IntegrationEventType.EMPATHY_INSIGHT_GAINED, "func", 0.9
    )

    effect = EmpathyToRelationshipIntegration.empathy_deepens_bond(event, mapping)
    assert effect["effect"] == "bond_deepened"


def test_system_integration_manager():
    """Test system integration manager"""
    manager = SystemIntegrationManager()
    assert len(manager.bridge.mappings) > 0


def test_process_challenge_completion():
    """Test processing challenge completion through manager"""
    manager = SystemIntegrationManager()
    assert manager.process_challenge_completion("a1", "logic", 0.85) is True


def test_process_tool_creation():
    """Test processing tool creation"""
    manager = SystemIntegrationManager()
    assert manager.process_tool_creation("a1", 0.9, 3) is True


def test_process_mentorship_goal():
    """Test processing mentorship goal"""
    manager = SystemIntegrationManager()
    assert manager.process_mentorship_goal("a1", "learning", 100.0) is True


def test_process_empathy_experience():
    """Test processing empathy experience"""
    manager = SystemIntegrationManager()
    assert manager.process_empathy_experience("a1", 0.3, 10.0) is True


def test_get_agent_development_summary():
    """Test getting agent development summary"""
    manager = SystemIntegrationManager()

    # Process multiple events
    manager.process_challenge_completion("a1", "math", 0.8)
    manager.process_tool_creation("a1", 0.85, 2)
    manager.process_mentorship_goal("a1", "learning", 75.0)

    summary = manager.get_agent_development_summary("a1")
    assert summary["agent_id"] == "a1"
    assert summary["total_effects"] > 0
    assert "knowledge_base" in summary["systems_affected"]


def test_complete_integration_workflow():
    """Test complete system integration workflow"""
    manager = SystemIntegrationManager()

    agent_id = "explorer_ai"

    # Agent completes learning challenge
    manager.process_challenge_completion(agent_id, "reasoning", 0.9)

    # Agent creates custom tool
    manager.process_tool_creation(agent_id, 0.95, 3)

    # Agent reaches mentorship goal
    manager.process_mentorship_goal(agent_id, "exploration", 150.0)

    # Agent has empathy experience
    manager.process_empathy_experience(agent_id, 0.2, 15.0)

    # Verify all systems have recorded effects
    summary = manager.get_agent_development_summary(agent_id)

    assert summary["total_effects"] >= 4
    assert summary["expertise_growth"] >= 1
    assert summary["personality_growth"] >= 1
    assert summary["relationship_growth"] >= 1

    # Verify bridge processed events
    assert manager.bridge.to_dict()["processed_events"] >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
