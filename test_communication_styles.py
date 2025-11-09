"""Round 20: Agent Communication Styles & Expression Dialects"""
import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List

class Dialect(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    POETIC = "poetic"
    TECHNICAL = "technical"
    CHILDLIKE = "childlike"

class ExpressionMode(Enum):
    DIRECT = "direct"
    METAPHORICAL = "metaphorical"
    HUMOROUS = "humorous"
    EMPATHETIC = "empathetic"

@dataclass
class CommStyle:
    agent_id: str
    primary_dialect: Dialect = Dialect.CASUAL
    expression_mode: ExpressionMode = ExpressionMode.DIRECT
    verbosity: float = 0.5  # 0.0-1.0
    formality_level: float = 0.5  # 0.0-1.0
    active_modifiers: List[str] = field(default_factory=list)
    
    def switch_dialect(self, dialect: Dialect) -> bool:
        self.primary_dialect = dialect
        return True
    
    def set_expression(self, mode: ExpressionMode) -> bool:
        self.expression_mode = mode
        return True
    
    def adjust_verbosity(self, amount: float) -> bool:
        self.verbosity = max(0.0, min(1.0, self.verbosity + amount))
        return True
    
    def add_modifier(self, modifier: str) -> bool:
        if modifier in self.active_modifiers:
            return False
        self.active_modifiers.append(modifier)
        return True

@dataclass
class CommunicationChannel:
    channel_id: str
    channel_type: str  # "text", "voice", "visual"
    active: bool = True
    messages_sent: int = 0
    
    def send_message(self) -> bool:
        if not self.active:
            return False
        self.messages_sent += 1
        return True

class CommunicationFramework:
    def __init__(self):
        self.styles: Dict[str, CommStyle] = {}
        self.channels: Dict[str, CommunicationChannel] = {}
        self.conversation_history: List[Dict] = []
    
    def register_agent_style(self, agent_id: str, style: CommStyle) -> bool:
        if agent_id in self.styles:
            return False
        self.styles[agent_id] = style
        return True
    
    def register_channel(self, channel: CommunicationChannel) -> bool:
        if channel.channel_id in self.channels:
            return False
        self.channels[channel.channel_id] = channel
        return True
    
    def send_message(self, agent_id: str, channel_id: str, content: str) -> bool:
        if agent_id not in self.styles or channel_id not in self.channels:
            return False
        if not self.channels[channel_id].send_message():
            return False
        self.conversation_history.append({
            "agent_id": agent_id,
            "channel_id": channel_id,
            "dialect": self.styles[agent_id].primary_dialect.value,
            "content": content
        })
        return True

def test_comm_style_creation():
    style = CommStyle(agent_id="a1", primary_dialect=Dialect.CASUAL)
    assert style.primary_dialect == Dialect.CASUAL
    assert style.verbosity == 0.5

def test_dialect_switching():
    style = CommStyle(agent_id="a1")
    assert style.switch_dialect(Dialect.FORMAL) is True
    assert style.primary_dialect == Dialect.FORMAL

def test_expression_modes():
    style = CommStyle(agent_id="a1")
    assert style.set_expression(ExpressionMode.METAPHORICAL) is True
    assert style.expression_mode == ExpressionMode.METAPHORICAL

def test_verbosity_adjustment():
    style = CommStyle(agent_id="a1", verbosity=0.5)
    assert style.adjust_verbosity(0.2) is True
    assert style.verbosity == 0.7

def test_modifiers():
    style = CommStyle(agent_id="a1")
    assert style.add_modifier("shy") is True
    assert style.add_modifier("confident") is True
    assert style.add_modifier("shy") is False

def test_communication_channel():
    channel = CommunicationChannel(channel_id="ch1", channel_type="text")
    assert channel.send_message() is True
    assert channel.messages_sent == 1

def test_framework_registration():
    fw = CommunicationFramework()
    style = CommStyle(agent_id="a1")
    assert fw.register_agent_style("a1", style) is True
    
    channel = CommunicationChannel(channel_id="ch1", channel_type="text")
    assert fw.register_channel(channel) is True

def test_framework_messaging():
    fw = CommunicationFramework()
    fw.register_agent_style("a1", CommStyle(agent_id="a1"))
    fw.register_channel(CommunicationChannel(channel_id="ch1", channel_type="text"))
    
    assert fw.send_message("a1", "ch1", "Hello!") is True
    assert len(fw.conversation_history) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
