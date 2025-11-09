"""
Agent toolkit and skills system for AICraft.

Provides:
- Tool definitions and schemas
- Tool mastery and proficiency tracking
- Toolkit management for agents
- Skill composition from tools
- Custom tool creation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import json


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
    required_level: float = 0.0  # Minimum proficiency required
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate_input(self, inputs: Dict[str, Any]) -> bool:
        """Check if inputs match expected schema."""
        for key in self.input_schema.keys():
            if key not in inputs:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tool definition."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "required_level": self.required_level,
            "examples": self.examples,
            "tags": self.tags
        }


class ToolMastery:
    """Tracks an agent's proficiency with a tool."""

    def __init__(self, tool_id: str, initial_level: float = 0.0):
        self.tool_id = tool_id
        self.proficiency = max(0.0, min(1.0, initial_level))  # 0.0 to 1.0
        self.times_used = 0
        self.successes = 0
        self.failures = 0
        self.discovered_at = datetime.now()
        self.last_used = None
        self.usage_history: List[tuple] = []

    def use_tool(self, success: bool, timestamp: Optional[datetime] = None) -> float:
        """Record tool usage and return new proficiency."""
        self.times_used += 1
        self.last_used = timestamp or datetime.now()
        self.usage_history.append((self.last_used, success))

        if success:
            self.successes += 1
            # Increase proficiency on success
            self.proficiency = min(1.0, self.proficiency + 0.02)
        else:
            self.failures += 1
            # Slight decrease on failure but still learn
            self.proficiency = max(0.0, self.proficiency - 0.01)

        return self.proficiency

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.times_used == 0:
            return 0.0
        return self.successes / self.times_used

    def is_mastered(self, threshold: float = 0.8) -> bool:
        """Check if tool is mastered."""
        return self.proficiency >= threshold

    def get_proficiency_level(self) -> str:
        """Get human-readable proficiency level."""
        if self.proficiency < 0.2:
            return "novice"
        elif self.proficiency < 0.4:
            return "apprentice"
        elif self.proficiency < 0.6:
            return "intermediate"
        elif self.proficiency < 0.8:
            return "advanced"
        else:
            return "master"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize mastery to dictionary."""
        return {
            "tool_id": self.tool_id,
            "proficiency": self.proficiency,
            "level": self.get_proficiency_level(),
            "times_used": self.times_used,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": self.get_success_rate(),
            "discovered_at": self.discovered_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }


class Toolkit:
    """Collection of tools available to an agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.available_tools: Dict[str, ToolDefinition] = {}
        self.tool_mastery: Dict[str, ToolMastery] = {}
        self.custom_tools: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()

    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a tool as available."""
        self.available_tools[tool_def.tool_id] = tool_def
        self.tool_mastery[tool_def.tool_id] = ToolMastery(
            tool_def.tool_id,
            initial_level=0.0
        )

    def register_tools(self, tools: List[ToolDefinition]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.register_tool(tool)

    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Retrieve a tool definition."""
        return self.available_tools.get(tool_id)

    def can_use_tool(self, tool_id: str) -> bool:
        """Check if agent has access to tool."""
        if tool_id not in self.available_tools:
            return False

        tool = self.available_tools[tool_id]
        mastery = self.tool_mastery.get(tool_id)

        if tool.required_level == 0:
            return True  # No level requirement

        return mastery and mastery.proficiency >= tool.required_level

    def use_tool(self, tool_id: str, inputs: Dict[str, Any],
                success: bool = True, timestamp: Optional[datetime] = None) -> None:
        """Record tool usage and update mastery."""
        if tool_id in self.tool_mastery:
            self.tool_mastery[tool_id].use_tool(success, timestamp)

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a category."""
        return [
            tool for tool in self.available_tools.values()
            if tool.category == category
        ]

    def get_available_tools(self) -> List[ToolDefinition]:
        """Get all available tools."""
        return list(self.available_tools.values())

    def get_mastered_tools(self, threshold: float = 0.8) -> List[str]:
        """Get list of mastered tool IDs."""
        return [
            tool_id for tool_id, mastery in self.tool_mastery.items()
            if mastery.is_mastered(threshold)
        ]

    def get_tools_by_proficiency(self, min_proficiency: float) -> List[str]:
        """Get tools with minimum proficiency level."""
        return [
            tool_id for tool_id, mastery in self.tool_mastery.items()
            if mastery.proficiency >= min_proficiency
        ]

    def add_custom_tool(self, tool_name: str, implementation: Dict[str, Any]) -> None:
        """Add a custom tool defined by the agent."""
        self.custom_tools[tool_name] = {
            "created_at": datetime.now().isoformat(),
            "implementation": implementation,
            "usage_count": 0
        }

    def discover_tool(self, tool_def: ToolDefinition) -> None:
        """Agent discovers a new tool."""
        self.register_tool(tool_def)

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        mastery_values = list(self.tool_mastery.values())

        return {
            "total_tools_registered": len(self.available_tools),
            "tools_ever_used": sum(1 for m in mastery_values if m.times_used > 0),
            "mastered_tools": len(self.get_mastered_tools()),
            "custom_tools": len(self.custom_tools),
            "avg_proficiency": (
                sum(m.proficiency for m in mastery_values) / len(mastery_values)
                if mastery_values else 0.0
            ),
            "total_tool_uses": sum(m.times_used for m in mastery_values),
            "tools_by_category": {
                cat.value: len(self.get_tools_by_category(cat))
                for cat in ToolCategory
            }
        }

    def export_toolkit(self) -> Dict[str, Any]:
        """Export toolkit configuration."""
        return {
            "agent_id": self.agent_id,
            "tools": {
                tool_id: tool.to_dict()
                for tool_id, tool in self.available_tools.items()
            },
            "mastery": {
                tool_id: mastery.to_dict()
                for tool_id, mastery in self.tool_mastery.items()
            },
            "custom_tools": self.custom_tools,
            "created_at": self.created_at.isoformat()
        }

    def get_toolkit_report(self) -> str:
        """Generate a human-readable toolkit report."""
        stats = self.get_tool_stats()
        report = f"\n**Toolkit Report for Agent {self.agent_id}:**\n"
        report += f"- Total tools registered: {stats['total_tools_registered']}\n"
        report += f"- Tools used: {stats['tools_ever_used']}\n"
        report += f"- Mastered tools: {stats['mastered_tools']}\n"
        report += f"- Custom tools created: {stats['custom_tools']}\n"
        report += f"- Average proficiency: {stats['avg_proficiency']:.0%}\n"
        report += f"- Total uses: {stats['total_tool_uses']}\n"

        if self.get_mastered_tools():
            report += f"\nMastered tools:\n"
            for tool_id in self.get_mastered_tools():
                tool = self.get_tool(tool_id)
                if tool:
                    report += f"  - {tool.name}\n"

        return report


class SkillComposer:
    """Combines tools into higher-level skills."""

    def __init__(self):
        self.skill_definitions: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()

    def define_skill(self, skill_name: str, required_tools: List[str],
                    procedure: List[str], description: str = "") -> None:
        """Define a skill that uses multiple tools."""
        self.skill_definitions[skill_name] = {
            "required_tools": required_tools,
            "procedure": procedure,
            "complexity": len(required_tools),
            "description": description,
            "created_at": datetime.now().isoformat()
        }

    def can_perform_skill(self, skill_name: str, toolkit: Toolkit) -> bool:
        """Check if agent can perform a skill with their tools."""
        if skill_name not in self.skill_definitions:
            return False

        skill = self.skill_definitions[skill_name]
        required_tools = skill["required_tools"]

        # Check if all required tools are available and accessible
        return all(toolkit.can_use_tool(tool_id) for tool_id in required_tools)

    def get_skill_complexity(self, skill_name: str) -> int:
        """Get complexity of a skill (based on tools required)."""
        if skill_name in self.skill_definitions:
            return self.skill_definitions[skill_name]["complexity"]
        return 0

    def learn_skill_from_examples(self, skill_name: str,
                                 examples: List[Dict[str, Any]]) -> None:
        """Learn a skill by example."""
        self.skill_definitions[skill_name] = {
            "learned_from_examples": True,
            "examples": examples,
            "procedure": [],  # Would be generated by ML
            "created_at": datetime.now().isoformat()
        }

    def compose_skills(self, skill_sequence: List[str]) -> Optional[Dict[str, Any]]:
        """Compose multiple skills into a complex procedure."""
        composite_tools = set()
        composite_procedure = []

        for skill_name in skill_sequence:
            if skill_name not in self.skill_definitions:
                return None

            skill = self.skill_definitions[skill_name]
            composite_tools.update(skill["required_tools"])
            composite_procedure.extend(skill["procedure"])

        return {
            "composite_skill": True,
            "component_skills": skill_sequence,
            "required_tools": list(composite_tools),
            "procedure": composite_procedure,
            "total_complexity": len(composite_tools)
        }

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get details about a skill."""
        return self.skill_definitions.get(skill_name)

    def get_all_skills(self) -> List[str]:
        """Get list of all defined skills."""
        return list(self.skill_definitions.keys())

    def get_skills_by_complexity(self, max_complexity: int) -> List[str]:
        """Get skills with complexity at or below threshold."""
        return [
            name for name, skill in self.skill_definitions.items()
            if skill.get("complexity", 0) <= max_complexity
        ]

    def export_skills(self) -> Dict[str, Any]:
        """Export skill definitions."""
        return {
            "skills": self.skill_definitions,
            "created_at": self.created_at.isoformat()
        }


# Standard tool definitions that can be used to initialize agents
STANDARD_TOOLS = [
    ToolDefinition(
        tool_id="read_text",
        name="Read Text",
        category=ToolCategory.PERCEPTION,
        description="Read and process text input",
        input_schema={"text": "string"},
        output_schema={"processed": "string"},
        tags=["perception", "basic"]
    ),
    ToolDefinition(
        tool_id="write_text",
        name="Write Text",
        category=ToolCategory.CREATION,
        description="Generate and format text",
        input_schema={"content": "string", "style": "string"},
        output_schema={"output": "string"},
        tags=["creation", "basic"]
    ),
    ToolDefinition(
        tool_id="execute_code",
        name="Execute Code",
        category=ToolCategory.COMPUTATION,
        description="Execute Python code",
        input_schema={"code": "string"},
        output_schema={"result": "string"},
        required_level=0.3,
        tags=["computation", "advanced"]
    ),
    ToolDefinition(
        tool_id="send_message",
        name="Send Message",
        category=ToolCategory.COMMUNICATION,
        description="Send message to another agent or user",
        input_schema={"recipient": "string", "message": "string"},
        output_schema={"sent": "boolean"},
        tags=["communication", "basic"]
    ),
    ToolDefinition(
        tool_id="store_memory",
        name="Store Memory",
        category=ToolCategory.MEMORY,
        description="Store information in memory",
        input_schema={"key": "string", "value": "string"},
        output_schema={"stored": "boolean"},
        tags=["memory", "basic"]
    ),
]
