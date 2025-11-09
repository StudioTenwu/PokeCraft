"""Round 21: Tool & Skill Unlocking System"""
import pytest
from enum import Enum
from dataclasses import dataclass

class ToolCategory(Enum):
    TEXT = "text"
    CALCULATION = "calculation"
    DRAWING = "drawing"
    CODE = "code"
    CUSTOM = "custom"

@dataclass
class Tool:
    tool_id: str
    category: ToolCategory
    name: str
    power_level: float = 0.0
    unlocked: bool = False
    usage_count: int = 0
    
    def unlock_tool(self) -> bool:
        if self.unlocked:
            return False
        self.unlocked = True
        return True
    
    def use_tool(self) -> bool:
        if not self.unlocked:
            return False
        self.usage_count += 1
        return True
    
    def upgrade_power(self, amount: float) -> bool:
        self.power_level = min(1.0, self.power_level + amount)
        return True

class ToolManager:
    def __init__(self):
        self.tools = {}
        self.unlocked_tools = set()
    
    def register_tool(self, tool: Tool) -> bool:
        if tool.tool_id in self.tools:
            return False
        self.tools[tool.tool_id] = tool
        return True
    
    def unlock_tool(self, tool_id: str) -> bool:
        if tool_id not in self.tools:
            return False
        if self.tools[tool_id].unlock_tool():
            self.unlocked_tools.add(tool_id)
            return True
        return False
    
    def get_unlocked_count(self) -> int:
        return len(self.unlocked_tools)

def test_tool_creation():
    tool = Tool(tool_id="t1", category=ToolCategory.TEXT, name="Writer")
    assert tool.unlocked is False

def test_tool_unlock():
    tool = Tool(tool_id="t1", category=ToolCategory.TEXT, name="Writer")
    assert tool.unlock_tool() is True
    assert tool.unlocked is True

def test_tool_usage():
    tool = Tool(tool_id="t1", category=ToolCategory.TEXT, name="Writer")
    tool.unlock_tool()
    assert tool.use_tool() is True
    assert tool.usage_count == 1

def test_tool_power():
    tool = Tool(tool_id="t1", category=ToolCategory.CODE, name="Coder")
    assert tool.upgrade_power(0.5) is True
    assert tool.power_level == 0.5

def test_manager():
    mgr = ToolManager()
    tool = Tool(tool_id="t1", category=ToolCategory.TEXT, name="Writer")
    assert mgr.register_tool(tool) is True
    assert mgr.unlock_tool("t1") is True
    assert mgr.get_unlocked_count() == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
