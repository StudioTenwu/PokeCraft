"""
Agent-to-agent communication system for AICraft.

Provides:
- Typed message passing between agents
- Shared context/memory for collaboration
- Coordination primitives for multi-agent collaboration
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import uuid


class MessageType(Enum):
    """Types of messages agents can send."""
    TASK = "task"
    REQUEST = "request"
    RESPONSE = "response"
    OBSERVATION = "observation"
    ACKNOWLEDGMENT = "acknowledgment"
    ERROR = "error"


@dataclass
class Message:
    """Represents a message between agents."""
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher = more important
    context_id: Optional[str] = None  # Shared context reference
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "context_id": self.context_id
        }


class SharedContext:
    """Shared memory context for multi-agent collaboration."""

    def __init__(self, context_id: str):
        self.context_id = context_id
        self.data: Dict[str, Any] = {}
        self.history: List[tuple] = []
        self.participants: Set[str] = set()
        self.created_at = datetime.now()

    def add_participant(self, agent_id: str) -> None:
        """Add an agent as a participant in this context."""
        self.participants.add(agent_id)

    def set(self, key: str, value: Any, agent_id: Optional[str] = None) -> None:
        """Set a value in shared context with optional agent attribution."""
        self.history.append(("set", key, value, agent_id, datetime.now()))
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared context."""
        return self.data.get(key, default)

    def update(self, updates: Dict[str, Any], agent_id: Optional[str] = None) -> None:
        """Batch update shared context."""
        for key, value in updates.items():
            self.set(key, value, agent_id)

    def get_history(self, key: Optional[str] = None) -> List[tuple]:
        """Get update history, optionally filtered by key."""
        if key:
            return [(op, k, v, aid, ts) for op, k, v, aid, ts in self.history if k == key]
        return self.history

    def get_by_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get all data set by a specific agent."""
        result = {}
        for op, key, value, aid, ts in self.history:
            if aid == agent_id and op == "set":
                result[key] = value
        return result


class AgentCommunicationBus:
    """Central message bus for agent-to-agent communication."""

    def __init__(self):
        self.messages: Dict[str, List[Message]] = {}
        self.agents: Dict[str, Any] = {}
        self.contexts: Dict[str, SharedContext] = {}
        self.message_archive: List[Message] = []

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """Register an agent with the bus."""
        self.agents[agent_id] = agent
        self.messages[agent_id] = []

    def deregister_agent(self, agent_id: str) -> None:
        """Deregister an agent from the bus."""
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.messages:
            del self.messages[agent_id]

    def create_context(self, context_id: str) -> SharedContext:
        """Create a new shared context."""
        ctx = SharedContext(context_id)
        self.contexts[context_id] = ctx
        return ctx

    def get_context(self, context_id: str) -> Optional[SharedContext]:
        """Retrieve a shared context."""
        return self.contexts.get(context_id)

    def send_message(self, message: Message) -> bool:
        """Send a message from one agent to another."""
        if message.recipient_id not in self.agents:
            return False

        self.messages[message.recipient_id].append(message)
        self.message_archive.append(message)

        # Add to context if specified
        if message.context_id and message.context_id in self.contexts:
            ctx = self.contexts[message.context_id]
            ctx.add_participant(message.sender_id)
            ctx.add_participant(message.recipient_id)

        return True

    def get_messages(self, agent_id: str) -> List[Message]:
        """Retrieve all messages for an agent."""
        return self.messages.get(agent_id, [])

    def get_messages_sorted(self, agent_id: str) -> List[Message]:
        """Retrieve messages sorted by priority (highest first)."""
        messages = self.get_messages(agent_id)
        return sorted(messages, key=lambda m: m.priority, reverse=True)

    def clear_messages(self, agent_id: str) -> None:
        """Clear all messages for an agent."""
        if agent_id in self.messages:
            self.messages[agent_id] = []

    def get_message_history(self, agent_id: Optional[str] = None) -> List[Message]:
        """Get message archive, optionally filtered by agent."""
        if agent_id:
            return [m for m in self.message_archive
                    if m.sender_id == agent_id or m.recipient_id == agent_id]
        return self.message_archive

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the communication bus."""
        return {
            "registered_agents": len(self.agents),
            "active_contexts": len(self.contexts),
            "total_messages_sent": len(self.message_archive),
            "pending_messages": sum(len(msgs) for msgs in self.messages.values())
        }


class AgentCollaborationCoordinator:
    """Coordinates multi-agent collaboration patterns."""

    def __init__(self, bus: AgentCommunicationBus):
        self.bus = bus
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, List[str]] = {}

    def create_task(self, task_id: str, task_def: Dict[str, Any]) -> None:
        """Create a new task in the workflow."""
        self.tasks[task_id] = {
            "definition": task_def,
            "status": "pending",
            "created_at": datetime.now(),
            "completed_at": None,
            "assigned_to": None
        }

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        if task_id not in self.tasks:
            return False

        self.tasks[task_id]["assigned_to"] = agent_id
        self.tasks[task_id]["status"] = "assigned"

        # Send task message
        msg = Message(
            sender_id="coordinator",
            recipient_id=agent_id,
            message_type=MessageType.TASK,
            content={
                "task_id": task_id,
                "definition": self.tasks[task_id]["definition"]
            },
            priority=5
        )

        return self.bus.send_message(msg)

    def complete_task(self, task_id: str) -> None:
        """Mark a task as complete."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["completed_at"] = datetime.now()

    def create_workflow(self, workflow_id: str, task_sequence: List[str]) -> None:
        """Create a workflow (sequence of tasks)."""
        self.workflows[workflow_id] = task_sequence

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task."""
        if task_id in self.tasks:
            return self.tasks[task_id]["status"]
        return None


# Example usage and convenience functions
def create_agent_network(num_agents: int) -> AgentCommunicationBus:
    """Create a communication network with N agents."""
    from test_agent_communication import MockAgent

    bus = AgentCommunicationBus()
    for i in range(num_agents):
        agent_id = f"agent_{i}"
        agent = MockAgent(agent_id)
        bus.register_agent(agent_id, agent)

    return bus
