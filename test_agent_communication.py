"""
Test suite for agent-to-agent communication system.
Tests message passing, context sharing, and collaboration patterns.
"""

import pytest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Message:
    """Represents a message between agents."""
    sender_id: str
    recipient_id: str
    message_type: str  # "task", "request", "response", "observation"
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 0  # Higher = more important
    context_id: Optional[str] = None  # Shared context reference


class AgentCommunicationBus:
    """Central message bus for agent communication."""

    def __init__(self):
        self.messages: Dict[str, List[Message]] = {}
        self.agents: Dict[str, 'Agent'] = {}

    def register_agent(self, agent_id: str, agent: 'Agent') -> None:
        """Register an agent with the bus."""
        self.agents[agent_id] = agent
        self.messages[agent_id] = []

    def send_message(self, message: Message) -> bool:
        """Send a message from one agent to another."""
        if message.recipient_id not in self.agents:
            return False
        self.messages[message.recipient_id].append(message)
        return True

    def get_messages(self, agent_id: str) -> List[Message]:
        """Retrieve all messages for an agent."""
        return self.messages.get(agent_id, [])

    def clear_messages(self, agent_id: str) -> None:
        """Clear all messages for an agent."""
        if agent_id in self.messages:
            self.messages[agent_id] = []


class SharedContext:
    """Shared memory context between agents."""

    def __init__(self, context_id: str):
        self.context_id = context_id
        self.data: Dict[str, Any] = {}
        self.history: List[tuple] = []

    def set(self, key: str, value: Any) -> None:
        """Set a value in shared context."""
        self.history.append(("set", key, value, datetime.now()))
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared context."""
        return self.data.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """Batch update shared context."""
        for key, value in updates.items():
            self.set(key, value)

    def get_history(self, key: Optional[str] = None) -> List[tuple]:
        """Get update history."""
        if key:
            return [(op, k, v, ts) for op, k, v, ts in self.history if k == key]
        return self.history


class TestAgentCommunicationBus:
    """Test message passing infrastructure."""

    def test_register_agent(self):
        bus = AgentCommunicationBus()
        agent = MockAgent("agent1")
        bus.register_agent("agent1", agent)
        assert "agent1" in bus.agents
        assert "agent1" in bus.messages

    def test_send_message_between_agents(self):
        bus = AgentCommunicationBus()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        bus.register_agent("agent1", agent1)
        bus.register_agent("agent2", agent2)

        msg = Message(
            sender_id="agent1",
            recipient_id="agent2",
            message_type="task",
            content={"task": "fetch_data", "resource": "weather"},
            timestamp=datetime.now()
        )

        assert bus.send_message(msg) is True
        messages = bus.get_messages("agent2")
        assert len(messages) == 1
        assert messages[0].content["task"] == "fetch_data"

    def test_send_to_nonexistent_agent(self):
        bus = AgentCommunicationBus()
        msg = Message(
            sender_id="agent1",
            recipient_id="nonexistent",
            message_type="task",
            content={},
            timestamp=datetime.now()
        )
        assert bus.send_message(msg) is False

    def test_clear_messages(self):
        bus = AgentCommunicationBus()
        agent = MockAgent("agent1")
        bus.register_agent("agent1", agent)

        msg = Message(
            sender_id="sender",
            recipient_id="agent1",
            message_type="task",
            content={},
            timestamp=datetime.now()
        )
        bus.send_message(msg)
        assert len(bus.get_messages("agent1")) == 1

        bus.clear_messages("agent1")
        assert len(bus.get_messages("agent1")) == 0

    def test_message_priority(self):
        bus = AgentCommunicationBus()
        agent = MockAgent("agent1")
        bus.register_agent("agent1", agent)

        # Send low-priority message first
        msg1 = Message(
            sender_id="sender1",
            recipient_id="agent1",
            message_type="observation",
            content={"data": "low"},
            timestamp=datetime.now(),
            priority=0
        )

        # Send high-priority message
        msg2 = Message(
            sender_id="sender2",
            recipient_id="agent1",
            message_type="request",
            content={"data": "high"},
            timestamp=datetime.now(),
            priority=10
        )

        bus.send_message(msg1)
        bus.send_message(msg2)

        messages = bus.get_messages("agent1")
        messages_sorted = sorted(messages, key=lambda m: m.priority, reverse=True)
        assert messages_sorted[0].priority == 10


class TestSharedContext:
    """Test shared memory between agents."""

    def test_set_and_get(self):
        ctx = SharedContext("ctx1")
        ctx.set("task_status", "in_progress")
        assert ctx.get("task_status") == "in_progress"

    def test_get_with_default(self):
        ctx = SharedContext("ctx1")
        assert ctx.get("nonexistent", "default") == "default"

    def test_batch_update(self):
        ctx = SharedContext("ctx1")
        ctx.update({
            "agent1_status": "ready",
            "agent2_status": "waiting",
            "shared_resource": "data.json"
        })

        assert ctx.get("agent1_status") == "ready"
        assert ctx.get("agent2_status") == "waiting"
        assert ctx.get("shared_resource") == "data.json"

    def test_history_tracking(self):
        ctx = SharedContext("ctx1")
        ctx.set("counter", 1)
        ctx.set("counter", 2)
        ctx.set("status", "done")

        history = ctx.get_history("counter")
        assert len(history) == 2
        assert history[0][2] == 1  # First value
        assert history[1][2] == 2  # Second value

    def test_full_history(self):
        ctx = SharedContext("ctx1")
        ctx.set("key1", "value1")
        ctx.set("key2", "value2")

        history = ctx.get_history()
        assert len(history) == 2


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id


# Integration tests
class TestAgentCollaborationPatterns:
    """Test collaboration patterns between agents."""

    def test_leader_follower_pattern(self):
        """Test leader delegates tasks to followers."""
        bus = AgentCommunicationBus()
        ctx = SharedContext("task_ctx")

        leader = MockAgent("leader")
        follower1 = MockAgent("follower1")
        follower2 = MockAgent("follower2")

        bus.register_agent("leader", leader)
        bus.register_agent("follower1", follower1)
        bus.register_agent("follower2", follower2)

        # Leader delegates tasks
        task1 = Message(
            sender_id="leader",
            recipient_id="follower1",
            message_type="task",
            content={"task_id": 1, "action": "gather_data"},
            timestamp=datetime.now(),
            context_id="task_ctx",
            priority=5
        )

        task2 = Message(
            sender_id="leader",
            recipient_id="follower2",
            message_type="task",
            content={"task_id": 2, "action": "process_data"},
            timestamp=datetime.now(),
            context_id="task_ctx",
            priority=5
        )

        assert bus.send_message(task1) is True
        assert bus.send_message(task2) is True

        # Followers acknowledge
        ack1 = Message(
            sender_id="follower1",
            recipient_id="leader",
            message_type="response",
            content={"task_id": 1, "status": "in_progress"},
            timestamp=datetime.now()
        )

        bus.send_message(ack1)

        leader_msgs = bus.get_messages("leader")
        assert len(leader_msgs) == 1
        assert leader_msgs[0].content["status"] == "in_progress"

    def test_peer_to_peer_collaboration(self):
        """Test peer agents sharing context and coordinating."""
        bus = AgentCommunicationBus()
        ctx = SharedContext("collab_ctx")

        agent_a = MockAgent("agent_a")
        agent_b = MockAgent("agent_b")

        bus.register_agent("agent_a", agent_a)
        bus.register_agent("agent_b", agent_b)

        # Agent A shares findings in context
        ctx.set("discovery", "pattern_found")
        ctx.set("confidence", 0.85)

        # Agent B requests context
        request = Message(
            sender_id="agent_b",
            recipient_id="agent_a",
            message_type="request",
            content={"request": "share_findings"},
            timestamp=datetime.now(),
            context_id="collab_ctx"
        )

        bus.send_message(request)
        assert ctx.get("discovery") == "pattern_found"
        assert ctx.get("confidence") == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
