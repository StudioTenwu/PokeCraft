"""
Round 29: Tool Capability Unlocking System

Enable progressive unlocking of tools and capabilities through quests,
challenges, and learning milestones. Agents start simple (text-only)
and unlock vision, web access, robotics, code execution, etc.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class ToolType(Enum):
    """Types of tools agents can use"""
    TEXT = "text"  # Basic text input/output
    VISION = "vision"  # Image analysis
    WEB = "web"  # Internet access
    CODE = "code"  # Code execution
    ROBOTICS = "robotics"  # Robot control
    DRAWING = "drawing"  # Image generation
    AUDIO = "audio"  # Sound synthesis
    MATH = "math"  # Advanced calculation
    FILE = "file"  # File system access


class UnlockConditionType(Enum):
    """Ways to unlock tools"""
    QUEST_COMPLETION = "quest_completion"  # Complete specific quest
    SKILL_THRESHOLD = "skill_threshold"  # Reach skill level
    EXPERIENCE_LEVEL = "experience_level"  # Agent level milestone
    CHALLENGE_WIN = "challenge_win"  # Win a challenge
    TIME_UNLOCK = "time_unlock"  # Unlock after time/turns
    MENTOR_GRANT = "mentor_grant"  # Mentor unlocks for agent
    ACHIEVEMENT = "achievement"  # Unlock achievement


@dataclass
class UnlockCondition:
    """Condition required to unlock a tool"""
    condition_type: UnlockConditionType
    requirement: str  # Quest ID, skill name, etc.
    progress: float = 0.0  # 0.0-1.0, how close to completion
    is_met: bool = False

    def advance_progress(self, amount: float = 0.1) -> bool:
        """Advance toward meeting condition"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.progress = min(1.0, self.progress + amount)
        if self.progress >= 1.0:
            self.is_met = True
        return True

    def check_condition(self) -> bool:
        """Check if condition is currently met"""
        return self.progress >= 1.0

    def to_dict(self) -> Dict:
        return {
            "type": self.condition_type.value,
            "requirement": self.requirement,
            "progress": self.progress,
            "is_met": self.is_met
        }


@dataclass
class Tool:
    """A tool that agents can use"""
    tool_id: str
    tool_type: ToolType
    name: str
    description: str
    power_level: float = 0.5  # 0.0-1.0, capability strength
    is_unlocked: bool = False
    unlock_conditions: List[UnlockCondition] = field(default_factory=list)
    unlock_cost: float = 0.0  # XP or resource cost to unlock
    difficulty_to_use: float = 0.5  # 0.0-1.0, how hard to master

    def add_unlock_condition(self, condition: UnlockCondition) -> bool:
        """Add a condition for unlocking this tool"""
        if condition.requirement in [c.requirement for c in self.unlock_conditions]:
            return False
        self.unlock_conditions.append(condition)
        return True

    def all_conditions_met(self) -> bool:
        """Check if all unlock conditions are satisfied"""
        if not self.unlock_conditions:
            return False  # Need at least one condition
        return all(c.is_met for c in self.unlock_conditions)

    def unlock(self) -> bool:
        """Unlock this tool"""
        if self.all_conditions_met() or not self.unlock_conditions:
            self.is_unlocked = True
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "tool_id": self.tool_id,
            "type": self.tool_type.value,
            "name": self.name,
            "is_unlocked": self.is_unlocked,
            "power_level": self.power_level,
            "conditions_met": sum(1 for c in self.unlock_conditions if c.is_met)
        }


@dataclass
class ToolTier:
    """A progression tier of tools"""
    tier_level: int  # 1, 2, 3, etc.
    required_agent_level: int  # Agent level needed to access
    tools: List[str] = field(default_factory=list)  # Tool IDs in this tier
    description: str = ""

    def add_tool(self, tool_id: str) -> bool:
        """Add tool to this tier"""
        if tool_id in self.tools:
            return False
        self.tools.append(tool_id)
        return True

    def to_dict(self) -> Dict:
        return {
            "tier_level": self.tier_level,
            "required_agent_level": self.required_agent_level,
            "tools_count": len(self.tools)
        }


class ToolProgressionSystem:
    """Manage tool unlocking and capability progression"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tiers: Dict[int, ToolTier] = {}
        self.agent_unlocked_tools: Dict[str, Set[str]] = {}  # agent_id → tool_ids
        self.agent_levels: Dict[str, int] = {}  # agent_id → level
        self.total_tools_unlocked: int = 0

    def create_tool(self, tool: Tool) -> bool:
        """Create a new tool"""
        if tool.tool_id in self.tools:
            return False
        self.tools[tool.tool_id] = tool
        return True

    def create_tier(self, tier: ToolTier) -> bool:
        """Create a tool tier"""
        if tier.tier_level in self.tiers:
            return False
        self.tiers[tier.tier_level] = tier
        return True

    def register_agent(self, agent_id: str, starting_level: int = 1) -> bool:
        """Register agent for tool progression"""
        if agent_id in self.agent_levels:
            return False
        self.agent_levels[agent_id] = starting_level
        self.agent_unlocked_tools[agent_id] = set()

        # Give starter tools to new agents (text tools with no conditions)
        starter_tools = [t for t in self.tools.values() if t.tool_type == ToolType.TEXT and not t.unlock_conditions]
        for tool in starter_tools:
            tool.is_unlocked = True
            self.agent_unlocked_tools[agent_id].add(tool.tool_id)
            self.total_tools_unlocked += 1

        return True

    def unlock_condition_progress(
        self, tool_id: str, requirement: str, progress: float
    ) -> bool:
        """Advance progress on an unlock condition"""
        if tool_id not in self.tools:
            return False

        tool = self.tools[tool_id]
        for condition in tool.unlock_conditions:
            if condition.requirement == requirement:
                return condition.advance_progress(progress)

        return False

    def check_tool_unlock(self, agent_id: str, tool_id: str) -> bool:
        """Check if tool can be unlocked for agent"""
        if tool_id not in self.tools or agent_id not in self.agent_levels:
            return False

        tool = self.tools[tool_id]

        # Check agent level requirement
        for tier in self.tiers.values():
            if tool_id in tier.tools:
                if self.agent_levels[agent_id] < tier.required_agent_level:
                    return False
                break

        # Check unlock conditions
        return tool.all_conditions_met()

    def unlock_tool_for_agent(self, agent_id: str, tool_id: str) -> bool:
        """Unlock a tool for an agent"""
        if not self.check_tool_unlock(agent_id, tool_id):
            return False

        if tool_id in self.agent_unlocked_tools[agent_id]:
            return False  # Already unlocked

        tool = self.tools[tool_id]
        if tool.unlock():
            self.agent_unlocked_tools[agent_id].add(tool_id)
            self.total_tools_unlocked += 1
            return True

        return False

    def get_agent_toolkit(self, agent_id: str) -> List[str]:
        """Get all tools unlocked for agent"""
        return list(self.agent_unlocked_tools.get(agent_id, []))

    def get_available_tools(self, agent_id: str) -> List[str]:
        """Get tools agent can potentially unlock next"""
        if agent_id not in self.agent_levels:
            return []

        agent_level = self.agent_levels[agent_id]
        available = []

        for tool in self.tools.values():
            # Already unlocked
            if tool.tool_id in self.agent_unlocked_tools[agent_id]:
                continue

            # Check tier requirement
            tier_found = False
            for tier in self.tiers.values():
                if tool.tool_id in tier.tools:
                    if agent_level >= tier.required_agent_level:
                        tier_found = True
                    break

            if tier_found or not any(tier.tools == [tool.tool_id] for tier in self.tiers.values()):
                available.append(tool.tool_id)

        return available

    def advance_agent_level(self, agent_id: str) -> bool:
        """Level up an agent"""
        if agent_id not in self.agent_levels:
            return False
        self.agent_levels[agent_id] += 1
        return True

    def get_progression_stats(self, agent_id: str) -> Dict:
        """Get tool progression stats for agent"""
        if agent_id not in self.agent_levels:
            return {}

        unlocked = len(self.agent_unlocked_tools.get(agent_id, []))
        available = len(self.get_available_tools(agent_id))
        total_tools = len(self.tools)

        return {
            "agent_level": self.agent_levels[agent_id],
            "tools_unlocked": unlocked,
            "tools_available": available,
            "total_tools": total_tools,
            "unlock_percentage": (unlocked / max(1, total_tools)) * 100
        }

    def to_dict(self) -> Dict:
        return {
            "total_tools": len(self.tools),
            "total_tiers": len(self.tiers),
            "total_tools_unlocked": self.total_tools_unlocked,
            "agents_registered": len(self.agent_levels)
        }


# ===== Tests =====

def test_unlock_condition_creation():
    """Test creating unlock condition"""
    condition = UnlockCondition(
        condition_type=UnlockConditionType.QUEST_COMPLETION,
        requirement="tutorial_quest_1"
    )
    assert condition.is_met is False


def test_unlock_condition_progress():
    """Test advancing condition progress"""
    condition = UnlockCondition(
        condition_type=UnlockConditionType.SKILL_THRESHOLD,
        requirement="reasoning"
    )
    assert condition.advance_progress(0.5) is True
    assert condition.advance_progress(0.5) is True
    assert condition.is_met is True


def test_tool_creation():
    """Test creating a tool"""
    tool = Tool(
        tool_id="vision_tool",
        tool_type=ToolType.VISION,
        name="Vision Module",
        description="Analyze images"
    )
    assert tool.is_unlocked is False


def test_tool_with_conditions():
    """Test tool with unlock conditions"""
    tool = Tool(
        tool_id="web_access",
        tool_type=ToolType.WEB,
        name="Internet Access",
        description="Browse the web"
    )
    condition = UnlockCondition(
        condition_type=UnlockConditionType.EXPERIENCE_LEVEL,
        requirement="level_3"
    )
    assert tool.add_unlock_condition(condition) is True


def test_tool_unlock():
    """Test unlocking a tool"""
    tool = Tool(tool_id="code_tool", tool_type=ToolType.CODE, name="Code Execution", description="Run code")
    condition = UnlockCondition(
        condition_type=UnlockConditionType.EXPERIENCE_LEVEL,
        requirement="level_5"
    )
    condition.is_met = True
    tool.add_unlock_condition(condition)

    assert tool.all_conditions_met() is True
    assert tool.unlock() is True
    assert tool.is_unlocked is True


def test_tool_tier_creation():
    """Test creating tool tier"""
    tier = ToolTier(tier_level=1, required_agent_level=1, description="Beginner tools")
    assert tier.tier_level == 1


def test_add_tool_to_tier():
    """Test adding tool to tier"""
    tier = ToolTier(tier_level=2, required_agent_level=5)
    assert tier.add_tool("vision_001") is True
    assert "vision_001" in tier.tools


def test_progression_system_creation():
    """Test creating progression system"""
    system = ToolProgressionSystem()
    tool = Tool(tool_id="t1", tool_type=ToolType.TEXT, name="Text", description="Basic")
    assert system.create_tool(tool) is True


def test_register_agent():
    """Test registering agent in progression system"""
    system = ToolProgressionSystem()
    tool = Tool(tool_id="text", tool_type=ToolType.TEXT, name="Text", description="Basic")
    system.create_tool(tool)

    assert system.register_agent("agent_1") is True
    assert "agent_1" in system.agent_levels


def test_agent_starts_with_text_tools():
    """Test agent starts with text tools"""
    system = ToolProgressionSystem()

    text_tool = Tool(tool_id="text", tool_type=ToolType.TEXT, name="Text I/O", description="Text")
    system.create_tool(text_tool)
    system.register_agent("agent_1")

    toolkit = system.get_agent_toolkit("agent_1")
    assert "text" in toolkit


def test_agent_level_up():
    """Test agent leveling up"""
    system = ToolProgressionSystem()
    system.register_agent("agent_1")

    initial_level = system.agent_levels["agent_1"]
    assert system.advance_agent_level("agent_1") is True
    assert system.agent_levels["agent_1"] == initial_level + 1


def test_tool_unlock_progression():
    """Test unlocking tools as agent progresses"""
    system = ToolProgressionSystem()

    # Create tools
    text_tool = Tool(tool_id="text", tool_type=ToolType.TEXT, name="Text", description="Basic")
    vision_tool = Tool(tool_id="vision", tool_type=ToolType.VISION, name="Vision", description="Images")

    system.create_tool(text_tool)
    system.create_tool(vision_tool)

    # Create tiers
    tier1 = ToolTier(tier_level=1, required_agent_level=1)
    tier2 = ToolTier(tier_level=2, required_agent_level=3)

    tier1.add_tool("text")
    tier2.add_tool("vision")

    system.create_tier(tier1)
    system.create_tier(tier2)

    # Register agent
    system.register_agent("agent_1", starting_level=1)
    assert "text" in system.get_agent_toolkit("agent_1")

    # Level up
    system.advance_agent_level("agent_1")
    system.advance_agent_level("agent_1")

    # Now vision should be available
    available = system.get_available_tools("agent_1")
    assert "vision" in available


def test_progression_stats():
    """Test getting progression statistics"""
    system = ToolProgressionSystem()
    tool = Tool(tool_id="t1", tool_type=ToolType.TEXT, name="Text", description="Basic")
    system.create_tool(tool)
    system.register_agent("agent_1")

    stats = system.get_progression_stats("agent_1")
    assert "agent_level" in stats
    assert "tools_unlocked" in stats


def test_complete_tool_unlock_workflow():
    """Test complete workflow of unlocking tools"""
    system = ToolProgressionSystem()

    # Create tools with different unlock paths
    starter_tool = Tool(
        tool_id="text_io",
        tool_type=ToolType.TEXT,
        name="Text I/O",
        description="Basic text"
    )

    vision_tool = Tool(
        tool_id="vision_v1",
        tool_type=ToolType.VISION,
        name="Vision v1",
        description="Image analysis"
    )

    web_tool = Tool(
        tool_id="web_v1",
        tool_type=ToolType.WEB,
        name="Web Access",
        description="Internet"
    )

    # Add conditions
    vision_condition = UnlockCondition(
        condition_type=UnlockConditionType.EXPERIENCE_LEVEL,
        requirement="level_5"
    )
    vision_tool.add_unlock_condition(vision_condition)

    web_condition = UnlockCondition(
        condition_type=UnlockConditionType.QUEST_COMPLETION,
        requirement="internet_safety_quest"
    )
    web_tool.add_unlock_condition(web_condition)

    system.create_tool(starter_tool)
    system.create_tool(vision_tool)
    system.create_tool(web_tool)

    # Create tiers
    tier1 = ToolTier(tier_level=1, required_agent_level=1)
    tier2 = ToolTier(tier_level=2, required_agent_level=5)

    tier1.add_tool("text_io")
    tier2.add_tool("vision_v1")
    tier2.add_tool("web_v1")

    system.create_tier(tier1)
    system.create_tier(tier2)

    # Register agent
    system.register_agent("agent_sparkle", starting_level=1)
    assert system.get_agent_toolkit("agent_sparkle") == ["text_io"]

    # Progress toward vision unlock
    for _ in range(4):
        system.advance_agent_level("agent_sparkle")

    # Meet vision condition
    system.unlock_condition_progress("vision_v1", "level_5", 1.0)
    assert system.unlock_tool_for_agent("agent_sparkle", "vision_v1") is True

    # Verify vision is now in toolkit
    assert "vision_v1" in system.get_agent_toolkit("agent_sparkle")

    # Complete web access quest
    system.unlock_condition_progress("web_v1", "internet_safety_quest", 1.0)
    assert system.unlock_tool_for_agent("agent_sparkle", "web_v1") is True

    # Check final stats
    stats = system.get_progression_stats("agent_sparkle")
    assert stats["tools_unlocked"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
