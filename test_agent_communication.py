"""
Round 53: Agent Communication Protocol
Enable agents to communicate with each other using structured messages.
Features: message formats, conversation protocols, knowledge sharing, conflict resolution.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class MessageType(Enum):
    """Type of message between agents"""
    REQUEST = "request"
    RESPONSE = "response"
    INFORM = "inform"
    QUERY = "query"
    COMMIT = "commit"
    REFUSE = "refuse"


class ConversationPhase(Enum):
    """Phase of agent conversation"""
    INITIATION = "initiation"
    NEGOTIATION = "negotiation"
    AGREEMENT = "agreement"
    EXECUTION = "execution"
    COMPLETION = "completion"
    DISPUTE = "dispute"


@dataclass
class Message:
    """Message from one agent to another"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    priority: float = 0.5
    requires_response: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.message_id,
            "sender": self.sender_id,
            "recipient": self.recipient_id,
            "type": self.message_type.value,
            "priority": self.priority
        }


@dataclass
class Conversation:
    """Exchange of messages between agents"""
    conversation_id: str
    agent_ids: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    phase: ConversationPhase = ConversationPhase.INITIATION
    shared_goal: str = ""
    agreement_confidence: float = 0.0

    def add_message(self, message: Message) -> bool:
        self.messages.append(message)
        return True

    def get_message_count(self) -> int:
        return len(self.messages)

    def advance_phase(self, new_phase: ConversationPhase) -> bool:
        self.phase = new_phase
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.conversation_id,
            "participants": len(self.agent_ids),
            "messages": len(self.messages),
            "phase": self.phase.value
        }


class CommunicationManager:
    """Central manager for agent communication"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.message_history: List[Message] = []

    def initiate_conversation(self, agent_ids: List[str], goal: str = "") -> Conversation:
        """Start new conversation"""
        conversation = Conversation(
            conversation_id=f"conv_{len(self.conversations)}",
            agent_ids=agent_ids,
            shared_goal=goal
        )
        self.conversations[conversation.conversation_id] = conversation
        return conversation

    def send_message(self, sender_id: str, recipient_id: str, msg_type: MessageType, content: Dict) -> Message:
        """Send message"""
        message = Message(
            message_id=f"msg_{len(self.message_history)}",
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=msg_type,
            content=content
        )
        self.message_history.append(message)
        return message

    def reach_agreement(self, conversation_id: str, confidence: float = 0.8) -> bool:
        """Record agreement"""
        if conversation_id not in self.conversations:
            return False
        conv = self.conversations[conversation_id]
        conv.agreement_confidence = confidence
        conv.advance_phase(ConversationPhase.AGREEMENT)
        return True

    def to_dict(self) -> Dict:
        return {
            "conversations": len(self.conversations),
            "messages": len(self.message_history)
        }


# ===== Tests =====

def test_message_creation():
    msg = Message("msg1", "agent1", "agent2", MessageType.REQUEST)
    assert msg.message_id == "msg1"

def test_conversation_creation():
    conv = Conversation("conv1", agent_ids=["agent1", "agent2"])
    assert len(conv.agent_ids) == 2

def test_conversation_messages():
    conv = Conversation("conv1")
    msg = Message("msg1", "agent1", "agent2", MessageType.REQUEST)
    assert conv.add_message(msg) is True
    assert conv.get_message_count() == 1

def test_conversation_phase():
    conv = Conversation("conv1")
    assert conv.advance_phase(ConversationPhase.NEGOTIATION) is True
    assert conv.phase == ConversationPhase.NEGOTIATION

def test_communication_manager_conversation():
    manager = CommunicationManager()
    conv = manager.initiate_conversation(["agent1", "agent2"], "task")
    assert conv is not None

def test_communication_manager_send():
    manager = CommunicationManager()
    msg = manager.send_message("agent1", "agent2", MessageType.REQUEST, {"task": "help"})
    assert msg is not None

def test_communication_manager_agreement():
    manager = CommunicationManager()
    conv = manager.initiate_conversation(["agent1", "agent2"])
    assert manager.reach_agreement(conv.conversation_id, 0.9) is True

def test_complete_communication_workflow():
    manager = CommunicationManager()
    conv = manager.initiate_conversation(["agent1", "agent2"], "task")
    msg1 = manager.send_message("agent1", "agent2", MessageType.REQUEST, {"task": "analyze"})
    msg2 = manager.send_message("agent2", "agent1", MessageType.RESPONSE, {"status": "ok"})
    assert manager.reach_agreement(conv.conversation_id, 0.95) is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
