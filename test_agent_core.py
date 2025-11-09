"""
Test suite for integrated Agent class.
Tests agent creation, state management, and system integration.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class AgentState(Enum):
    """Agent lifecycle states."""
    CREATED = "created"        # Just hatched
    DEVELOPING = "developing"  # Growing and learning
    CAPABLE = "capable"        # Ready for deployment
    DEPLOYED = "deployed"      # In active use
    RESTING = "resting"        # Idle/sleeping
    EVOLVED = "evolved"        # Matured/mastered


class Agent:
    """Integrated agent with all 4 primitives."""

    def __init__(self, agent_id: str, name: str = ""):
        self.agent_id = agent_id
        self.name = name or f"Agent-{agent_id[:8]}"
        self.state = AgentState.CREATED
        self.created_at = datetime.now()

        # Import systems (simplified for testing)
        self.personality = None  # PersonalityModule would be injected
        self.memory = None       # MemoryStore would be injected
        self.toolkit = None      # Toolkit would be injected
        self.communication_bus = None  # AgentCommunicationBus would be injected

        # Stats
        self.experience_points = 0
        self.lifetime_tasks_completed = 0
        self.lifetime_collaborations = 0
        self.current_task = None
        self.collaborators: List[str] = []

    def set_personality(self, personality) -> None:
        """Inject personality module."""
        self.personality = personality

    def set_memory(self, memory) -> None:
        """Inject memory module."""
        self.memory = memory

    def set_toolkit(self, toolkit) -> None:
        """Inject toolkit module."""
        self.toolkit = toolkit

    def set_communication_bus(self, bus) -> None:
        """Inject communication bus."""
        self.communication_bus = bus

    def transition_to_state(self, new_state: AgentState) -> bool:
        """Transition agent to a new state."""
        valid_transitions = {
            AgentState.CREATED: [AgentState.DEVELOPING],
            AgentState.DEVELOPING: [AgentState.CAPABLE, AgentState.RESTING],
            AgentState.CAPABLE: [AgentState.DEPLOYED, AgentState.RESTING],
            AgentState.DEPLOYED: [AgentState.RESTING, AgentState.EVOLVED],
            AgentState.RESTING: [AgentState.DEVELOPING, AgentState.DEPLOYED],
            AgentState.EVOLVED: [AgentState.DEPLOYED, AgentState.RESTING]
        }

        if new_state in valid_transitions.get(self.state, []):
            self.state = new_state
            return True
        return False

    def start_task(self, task_id: str, task_description: str) -> bool:
        """Begin working on a task."""
        if self.state not in [AgentState.CAPABLE, AgentState.DEPLOYED, AgentState.EVOLVED]:
            return False

        self.current_task = {
            "task_id": task_id,
            "description": task_description,
            "started_at": datetime.now(),
            "status": "in_progress"
        }
        return True

    def complete_task(self, success: bool, reward: int = 10) -> None:
        """Mark current task as complete."""
        if not self.current_task:
            return

        self.current_task["status"] = "completed" if success else "failed"
        self.current_task["completed_at"] = datetime.now()

        if success:
            self.lifetime_tasks_completed += 1
            self.experience_points += reward

            # Update personality
            if self.personality:
                self.personality.gain_experience(reward)

        self.current_task = None

    def collaborate_with(self, other_agent_id: str) -> None:
        """Record collaboration with another agent."""
        if other_agent_id not in self.collaborators:
            self.collaborators.append(other_agent_id)
            self.lifetime_collaborations += 1

    def can_perform_action(self, action: str) -> bool:
        """Check if agent can perform an action based on state and capabilities."""
        if self.state in [AgentState.CREATED, AgentState.RESTING]:
            return False

        # Could check toolkit, memory, etc.
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get complete agent status snapshot."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "experience_points": self.experience_points,
            "tasks_completed": self.lifetime_tasks_completed,
            "collaborations": self.lifetime_collaborations,
            "current_task": self.current_task,
            "collaborators": self.collaborators,
            "personality": self.personality.to_dict() if self.personality else None,
            "memory_stats": self.memory.get_memory_stats() if self.memory else None,
            "toolkit_stats": self.toolkit.get_tool_stats() if self.toolkit else None
        }

    def get_profile(self) -> str:
        """Generate human-readable agent profile."""
        profile = f"\n**{self.name}'s Profile**\n"
        profile += f"- Agent ID: {self.agent_id}\n"
        profile += f"- State: {self.state.value.upper()}\n"
        profile += f"- Experience: {self.experience_points} pts\n"
        profile += f"- Tasks Completed: {self.lifetime_tasks_completed}\n"
        profile += f"- Collaborations: {self.lifetime_collaborations}\n"

        if self.personality:
            profile += f"- Personality Style: {self.personality.expression_style.value}\n"

        if self.toolkit:
            stats = self.toolkit.get_tool_stats()
            profile += f"- Tools Mastered: {stats['mastered_tools']}/{stats['total_tools_registered']}\n"

        return profile


class TestAgentCreation:
    """Test agent initialization and basic operations."""

    def test_create_agent(self):
        agent = Agent("agent_1", "Alice")
        assert agent.agent_id == "agent_1"
        assert agent.name == "Alice"
        assert agent.state == AgentState.CREATED

    def test_agent_starts_with_zero_experience(self):
        agent = Agent("agent_1")
        assert agent.experience_points == 0
        assert agent.lifetime_tasks_completed == 0

    def test_agent_default_name(self):
        agent = Agent("xyz789abc")
        assert "Agent-" in agent.name
        assert "xyz789ab" in agent.name


class TestAgentStateTransition:
    """Test agent lifecycle state transitions."""

    def test_valid_transition_created_to_developing(self):
        agent = Agent("agent_1")
        assert agent.transition_to_state(AgentState.DEVELOPING) is True
        assert agent.state == AgentState.DEVELOPING

    def test_invalid_transition(self):
        agent = Agent("agent_1")
        # Can't jump directly from CREATED to DEPLOYED
        assert agent.transition_to_state(AgentState.DEPLOYED) is False
        assert agent.state == AgentState.CREATED

    def test_state_path_to_deployment(self):
        agent = Agent("agent_1")

        # Valid progression
        assert agent.transition_to_state(AgentState.DEVELOPING) is True
        assert agent.transition_to_state(AgentState.CAPABLE) is True
        assert agent.transition_to_state(AgentState.DEPLOYED) is True

        assert agent.state == AgentState.DEPLOYED

    def test_rest_from_deployed(self):
        agent = Agent("agent_1")
        agent.transition_to_state(AgentState.DEVELOPING)
        agent.transition_to_state(AgentState.CAPABLE)
        agent.transition_to_state(AgentState.DEPLOYED)

        assert agent.transition_to_state(AgentState.RESTING) is True
        assert agent.state == AgentState.RESTING


class TestAgentTaskManagement:
    """Test task execution and completion."""

    def test_start_task_in_developing_state(self):
        agent = Agent("agent_1")
        agent.state = AgentState.DEVELOPING

        # Can't start task in developing state
        assert agent.start_task("task_1", "Do something") is False

    def test_start_task_in_capable_state(self):
        agent = Agent("agent_1")
        agent.state = AgentState.CAPABLE

        assert agent.start_task("task_1", "Learn new skill") is True
        assert agent.current_task is not None
        assert agent.current_task["task_id"] == "task_1"

    def test_complete_task_with_success(self):
        agent = Agent("agent_1")
        agent.state = AgentState.CAPABLE
        agent.start_task("task_1", "Test task")

        assert agent.lifetime_tasks_completed == 0
        assert agent.experience_points == 0

        agent.complete_task(success=True, reward=25)

        assert agent.lifetime_tasks_completed == 1
        assert agent.experience_points == 25
        assert agent.current_task is None

    def test_complete_task_with_failure(self):
        agent = Agent("agent_1")
        agent.state = AgentState.DEPLOYED
        agent.start_task("task_1", "Risky task")

        agent.complete_task(success=False, reward=10)

        # Failure doesn't award experience
        assert agent.experience_points == 0
        assert agent.lifetime_tasks_completed == 0


class TestAgentCollaboration:
    """Test multi-agent collaboration tracking."""

    def test_collaborate_with_agent(self):
        agent = Agent("agent_1", "Alice")

        agent.collaborate_with("agent_2")

        assert "agent_2" in agent.collaborators
        assert agent.lifetime_collaborations == 1

    def test_multiple_collaborations(self):
        agent = Agent("agent_1")

        agent.collaborate_with("agent_2")
        agent.collaborate_with("agent_3")
        agent.collaborate_with("agent_4")

        assert len(agent.collaborators) == 3
        assert agent.lifetime_collaborations == 3

    def test_duplicate_collaboration(self):
        agent = Agent("agent_1")

        agent.collaborate_with("agent_2")
        agent.collaborate_with("agent_2")  # Collaborate again

        # Should only count unique collaborators once
        assert len(agent.collaborators) == 1
        assert agent.lifetime_collaborations == 1


class TestAgentModuleInjection:
    """Test dependency injection of agent modules."""

    def test_inject_personality(self):
        agent = Agent("agent_1")

        class MockPersonality:
            def to_dict(self):
                return {"style": "casual"}
            def gain_experience(self, pts):
                pass

        personality = MockPersonality()
        agent.set_personality(personality)

        assert agent.personality is not None

    def test_inject_all_modules(self):
        agent = Agent("agent_1")

        class Mock:
            def to_dict(self):
                return {}
            def get_memory_stats(self):
                return {}
            def get_tool_stats(self):
                return {}
            def gain_experience(self, pts):
                pass

        mock = Mock()
        agent.set_personality(mock)
        agent.set_memory(mock)
        agent.set_toolkit(mock)

        assert agent.personality is not None
        assert agent.memory is not None
        assert agent.toolkit is not None


class TestAgentActions:
    """Test agent action capabilities based on state."""

    def test_can_act_when_capable(self):
        agent = Agent("agent_1")
        agent.state = AgentState.CAPABLE

        assert agent.can_perform_action("read") is True
        assert agent.can_perform_action("think") is True

    def test_cannot_act_when_created(self):
        agent = Agent("agent_1")
        assert agent.state == AgentState.CREATED

        assert agent.can_perform_action("read") is False

    def test_cannot_act_when_resting(self):
        agent = Agent("agent_1")
        agent.state = AgentState.RESTING

        assert agent.can_perform_action("read") is False


class TestAgentStatus:
    """Test agent status reporting."""

    def test_get_status_snapshot(self):
        agent = Agent("agent_1", "TestAgent")
        status = agent.get_status()

        assert status["agent_id"] == "agent_1"
        assert status["name"] == "TestAgent"
        assert status["state"] == "created"
        assert status["experience_points"] == 0

    def test_status_with_task(self):
        agent = Agent("agent_1")
        agent.state = AgentState.DEPLOYED
        agent.start_task("task_1", "Important task")

        status = agent.get_status()
        assert status["current_task"] is not None
        assert status["current_task"]["task_id"] == "task_1"

    def test_get_profile(self):
        agent = Agent("agent_1", "CharlieBot")
        profile = agent.get_profile()

        assert "CharlieBot" in profile
        assert "agent_1" in profile
        assert "Experience" in profile


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
