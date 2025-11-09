"""
Test suite for agent toolkit and skills system.
Tests tool definitions, tool mastery, and skill composition.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class ToolCategory(Enum):
    """Categories of tools agents can use."""
    PERCEPTION = "perception"      # Sensing/input (text, vision, files)
    COMPUTATION = "computation"    # Math, logic, data processing
    CREATION = "creation"          # Drawing, music, writing, code
    COMMUNICATION = "communication"  # Messaging, API calls
    MEMORY = "memory"              # Storage and retrieval
    CUSTOM = "custom"              # User-defined tools


@dataclass
class ToolDefinition:
    """Defines a tool that agents can use."""
    tool_id: str
    name: str
    category: ToolCategory
    description: str
    input_schema: Dict[str, Any]  # What inputs it expects
    output_schema: Dict[str, Any]  # What it produces
    required_level: int = 0  # Minimum agent level to use
    examples: List[Dict[str, Any]] = None

    def __post_init__(self):
        self.examples = self.examples or []

    def validate_input(self, inputs: Dict[str, Any]) -> bool:
        """Check if inputs match expected schema."""
        for key in self.input_schema.keys():
            if key not in inputs:
                return False
        return True


class ToolMastery:
    """Tracks an agent's proficiency with a tool."""

    def __init__(self, tool_id: str, initial_level: float = 0.0):
        self.tool_id = tool_id
        self.proficiency = initial_level  # 0.0 to 1.0
        self.times_used = 0
        self.successes = 0
        self.failures = 0

    def use_tool(self, success: bool) -> None:
        """Record tool usage."""
        self.times_used += 1

        if success:
            self.successes += 1
            # Increase proficiency on success
            self.proficiency = min(1.0, self.proficiency + 0.02)
        else:
            self.failures += 1
            # Slight decrease on failure but still learn
            self.proficiency = max(0.0, self.proficiency - 0.01)

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.times_used == 0:
            return 0.0
        return self.successes / self.times_used

    def is_mastered(self) -> bool:
        """Check if tool is mastered (proficiency > 0.8)."""
        return self.proficiency > 0.8


class Toolkit:
    """Collection of tools available to an agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.available_tools: Dict[str, ToolDefinition] = {}
        self.tool_mastery: Dict[str, ToolMastery] = {}
        self.custom_tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a tool as available."""
        self.available_tools[tool_def.tool_id] = tool_def
        self.tool_mastery[tool_def.tool_id] = ToolMastery(tool_def.tool_id)

    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Retrieve a tool definition."""
        return self.available_tools.get(tool_id)

    def can_use_tool(self, tool_id: str) -> bool:
        """Check if agent has access to tool."""
        if tool_id not in self.available_tools:
            return False

        tool = self.available_tools[tool_id]
        # Check if agent's proficiency is high enough
        mastery = self.tool_mastery.get(tool_id)

        if tool.required_level == 0:
            return True  # No level requirement

        return mastery and mastery.proficiency >= tool.required_level

    def use_tool(self, tool_id: str, inputs: Dict[str, Any], success: bool = True) -> None:
        """Record tool usage and update mastery."""
        if tool_id in self.tool_mastery:
            self.tool_mastery[tool_id].use_tool(success)

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a category."""
        return [
            tool for tool in self.available_tools.values()
            if tool.category == category
        ]

    def get_mastered_tools(self) -> List[str]:
        """Get list of mastered tool IDs."""
        return [
            tool_id for tool_id, mastery in self.tool_mastery.items()
            if mastery.is_mastered()
        ]

    def add_custom_tool(self, tool_name: str, implementation: Dict[str, Any]) -> None:
        """Add a custom tool defined by the agent."""
        self.custom_tools[tool_name] = {
            "created_at": "now",
            "implementation": implementation
        }

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        stats = {
            "total_tools": len(self.available_tools),
            "tools_used": sum(1 for m in self.tool_mastery.values() if m.times_used > 0),
            "mastered_tools": len(self.get_mastered_tools()),
            "custom_tools": len(self.custom_tools),
            "avg_proficiency": (
                sum(m.proficiency for m in self.tool_mastery.values()) / len(self.tool_mastery)
                if self.tool_mastery else 0.0
            )
        }
        return stats


class SkillComposer:
    """Combines tools into higher-level skills."""

    def __init__(self):
        self.skill_definitions: Dict[str, Dict[str, Any]] = {}

    def define_skill(self, skill_name: str, required_tools: List[str],
                    procedure: List[str]) -> None:
        """Define a skill that uses multiple tools."""
        self.skill_definitions[skill_name] = {
            "required_tools": required_tools,
            "procedure": procedure,
            "complexity": len(required_tools)
        }

    def can_perform_skill(self, skill_name: str, toolkit: Toolkit) -> bool:
        """Check if agent can perform a skill with their tools."""
        if skill_name not in self.skill_definitions:
            return False

        skill = self.skill_definitions[skill_name]
        required_tools = skill["required_tools"]

        # Check if all required tools are available
        return all(toolkit.can_use_tool(tool_id) for tool_id in required_tools)

    def learn_skill_from_examples(self, skill_name: str, examples: List[Dict[str, Any]]) -> None:
        """Learn a skill by example."""
        # In a real system, this would use ML
        self.skill_definitions[skill_name] = {
            "learned_from_examples": True,
            "examples": examples,
            "procedure": []  # Would be generated
        }

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get details about a skill."""
        return self.skill_definitions.get(skill_name)


class TestToolDefinition:
    """Test tool definitions."""

    def test_create_tool(self):
        tool = ToolDefinition(
            tool_id="write_text",
            name="Write Text",
            category=ToolCategory.CREATION,
            description="Write and format text",
            input_schema={"text": "string", "format": "string"},
            output_schema={"output": "string"}
        )

        assert tool.tool_id == "write_text"
        assert tool.category == ToolCategory.CREATION

    def test_validate_input(self):
        tool = ToolDefinition(
            tool_id="math_add",
            name="Add Numbers",
            category=ToolCategory.COMPUTATION,
            input_schema={"a": "number", "b": "number"},
            output_schema={"result": "number"},
            description="Add two numbers"
        )

        assert tool.validate_input({"a": 1, "b": 2}) is True
        assert tool.validate_input({"a": 1}) is False

    def test_tool_examples(self):
        examples = [
            {"inputs": {"a": 2, "b": 3}, "output": {"result": 5}},
            {"inputs": {"a": 10, "b": 20}, "output": {"result": 30}}
        ]

        tool = ToolDefinition(
            tool_id="math_add",
            name="Add Numbers",
            category=ToolCategory.COMPUTATION,
            input_schema={"a": "number", "b": "number"},
            output_schema={"result": "number"},
            description="Add numbers",
            examples=examples
        )

        assert len(tool.examples) == 2


class TestToolMastery:
    """Test tool proficiency tracking."""

    def test_initial_mastery(self):
        mastery = ToolMastery("tool_1")
        assert mastery.proficiency == 0.0
        assert mastery.times_used == 0

    def test_proficiency_increase(self):
        mastery = ToolMastery("tool_1")
        mastery.use_tool(success=True)
        mastery.use_tool(success=True)

        assert mastery.proficiency > 0.0
        assert mastery.times_used == 2
        assert mastery.successes == 2

    def test_proficiency_decrease(self):
        mastery = ToolMastery("tool_1", initial_level=0.5)
        mastery.use_tool(success=False)

        assert mastery.proficiency < 0.5

    def test_mastery_threshold(self):
        mastery = ToolMastery("tool_1", initial_level=0.9)
        assert mastery.is_mastered() is True

    def test_success_rate(self):
        mastery = ToolMastery("tool_1")
        mastery.use_tool(success=True)
        mastery.use_tool(success=True)
        mastery.use_tool(success=False)

        assert mastery.get_success_rate() == pytest.approx(2/3, 0.01)


class TestToolkit:
    """Test toolkit management."""

    def test_register_tool(self):
        toolkit = Toolkit("agent_1")
        tool = ToolDefinition(
            tool_id="write", name="Write", category=ToolCategory.CREATION,
            description="Write text", input_schema={}, output_schema={}
        )

        toolkit.register_tool(tool)
        assert "write" in toolkit.available_tools

    def test_get_tool_by_category(self):
        toolkit = Toolkit("agent_1")

        tool1 = ToolDefinition(
            tool_id="write", name="Write", category=ToolCategory.CREATION,
            description="Write", input_schema={}, output_schema={}
        )
        tool2 = ToolDefinition(
            tool_id="paint", name="Paint", category=ToolCategory.CREATION,
            description="Paint", input_schema={}, output_schema={}
        )
        tool3 = ToolDefinition(
            tool_id="listen", name="Listen", category=ToolCategory.PERCEPTION,
            description="Listen", input_schema={}, output_schema={}
        )

        toolkit.register_tool(tool1)
        toolkit.register_tool(tool2)
        toolkit.register_tool(tool3)

        creation_tools = toolkit.get_tools_by_category(ToolCategory.CREATION)
        assert len(creation_tools) == 2

    def test_can_use_tool(self):
        toolkit = Toolkit("agent_1")

        tool = ToolDefinition(
            tool_id="advanced_calc", name="Advanced Calc",
            category=ToolCategory.COMPUTATION,
            description="Complex calculations",
            input_schema={}, output_schema={},
            required_level=0  # No requirement
        )

        toolkit.register_tool(tool)
        assert toolkit.can_use_tool("advanced_calc") is True

    def test_tool_mastery_tracking(self):
        toolkit = Toolkit("agent_1")

        tool = ToolDefinition(
            tool_id="draw", name="Draw", category=ToolCategory.CREATION,
            description="Draw shapes", input_schema={}, output_schema={}
        )

        toolkit.register_tool(tool)
        toolkit.use_tool("draw", {}, success=True)
        toolkit.use_tool("draw", {}, success=True)

        mastery = toolkit.tool_mastery["draw"]
        assert mastery.times_used == 2
        assert mastery.successes == 2

    def test_custom_tools(self):
        toolkit = Toolkit("agent_1")
        custom = {"logic": "if x > 5 then output y"}
        toolkit.add_custom_tool("special_check", custom)

        assert "special_check" in toolkit.custom_tools

    def test_toolkit_stats(self):
        toolkit = Toolkit("agent_1")

        for i in range(3):
            tool = ToolDefinition(
                tool_id=f"tool_{i}", name=f"Tool {i}",
                category=ToolCategory.CREATION,
                description="Test tool", input_schema={}, output_schema={}
            )
            toolkit.register_tool(tool)

        stats = toolkit.get_tool_stats()
        assert stats["total_tools"] == 3


class TestSkillComposer:
    """Test skill composition from tools."""

    def test_define_skill(self):
        composer = SkillComposer()
        composer.define_skill(
            "write_story",
            required_tools=["write", "edit", "format"],
            procedure=["brainstorm", "draft", "edit", "format"]
        )

        skill = composer.get_skill_info("write_story")
        assert "write" in skill["required_tools"]

    def test_can_perform_skill(self):
        composer = SkillComposer()
        toolkit = Toolkit("agent_1")

        # Define skill
        composer.define_skill("draw_art", ["draw", "color"], [])

        # Register required tools
        for tool_name in ["draw", "color"]:
            tool = ToolDefinition(
                tool_id=tool_name, name=tool_name.title(),
                category=ToolCategory.CREATION,
                description="Tool", input_schema={}, output_schema={}
            )
            toolkit.register_tool(tool)

        assert composer.can_perform_skill("draw_art", toolkit) is True

    def test_skill_from_examples(self):
        composer = SkillComposer()

        examples = [
            {"input": "x", "output": "processed_x"},
            {"input": "y", "output": "processed_y"}
        ]

        composer.learn_skill_from_examples("process_data", examples)

        skill = composer.get_skill_info("process_data")
        assert "learned_from_examples" in skill


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
