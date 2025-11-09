"""
Round 40: Custom Tool Builder

Enable players to design and create custom tools for their agents.
Tools can be built from basic primitives and tested in challenges.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any


class ToolPrimitive(Enum):
    """Basic tool building blocks"""
    INPUT = "input"  # Take input from user/agent
    PROCESS = "process"  # Apply processing/transformation
    OUTPUT = "output"  # Generate output
    MEMORY = "memory"  # Access/store memory
    COMMUNICATE = "communicate"  # Send to other agents
    REASON = "reason"  # Apply reasoning
    CREATE = "create"  # Generate content


class ToolValidation(Enum):
    """Validation status of custom tool"""
    UNTESTED = "untested"
    VALID = "valid"
    INVALID = "invalid"
    UNSAFE = "unsafe"


@dataclass
class ToolComponent:
    """Component in a tool blueprint"""
    component_id: str
    primitive: ToolPrimitive
    parameters: Dict[str, Any] = field(default_factory=dict)
    validation_status: ToolValidation = ToolValidation.UNTESTED

    def to_dict(self) -> Dict:
        return {
            "id": self.component_id,
            "primitive": self.primitive.value,
            "parameters": self.parameters,
            "status": self.validation_status.value
        }


@dataclass
class ToolBlueprint:
    """Designer's plan for a custom tool"""
    blueprint_id: str
    name: str
    description: str
    components: List[ToolComponent] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)  # Expected inputs
    outputs: List[str] = field(default_factory=list)  # Expected outputs
    test_cases: List[Dict] = field(default_factory=list)
    reliability: float = 0.5  # 0.0-1.0, estimated reliability
    author_id: str = ""
    is_public: bool = False  # Can be shared with other players

    def add_component(self, component: ToolComponent) -> bool:
        """Add component to blueprint"""
        self.components.append(component)
        return True

    def add_input(self, input_name: str) -> bool:
        """Define input parameter"""
        if input_name not in self.inputs:
            self.inputs.append(input_name)
        return True

    def add_output(self, output_name: str) -> bool:
        """Define output parameter"""
        if output_name not in self.outputs:
            self.outputs.append(output_name)
        return True

    def add_test_case(self, input_data: Dict, expected_output: Dict) -> bool:
        """Add test case for tool"""
        self.test_cases.append({
            "input": input_data,
            "expected": expected_output
        })
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.blueprint_id,
            "name": self.name,
            "description": self.description,
            "components": len(self.components),
            "inputs": len(self.inputs),
            "outputs": len(self.outputs),
            "tests": len(self.test_cases),
            "reliability": self.reliability
        }


@dataclass
class CustomTool:
    """Compiled and tested custom tool ready for use"""
    tool_id: str
    blueprint_id: str
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    reliability: float  # 0.0-1.0, based on tests
    test_pass_rate: float  # 0.0-1.0
    usage_count: int = 0
    success_count: int = 0
    failures: List[str] = field(default_factory=list)

    def execute(self, input_data: Dict) -> Optional[Dict]:
        """Simulate tool execution"""
        self.usage_count += 1
        # In real system, this would actually execute the tool
        if all(key in input_data for key in self.inputs):
            self.success_count += 1
            return {"status": "success", "data": input_data}
        else:
            error = f"Missing inputs: {set(self.inputs) - set(input_data.keys())}"
            self.failures.append(error)
            return None

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.usage_count == 0:
            return self.reliability
        return self.success_count / self.usage_count

    def to_dict(self) -> Dict:
        return {
            "id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "reliability": self.reliability,
            "usage": self.usage_count,
            "success_rate": self.get_success_rate()
        }


class ToolBuilder:
    """System for designing and building custom tools"""

    def __init__(self):
        self.blueprints: Dict[str, ToolBlueprint] = {}
        self.tools: Dict[str, CustomTool] = {}
        self.tool_library: Dict[str, CustomTool] = {}  # Public tools

    def create_blueprint(self, blueprint_id: str, name: str, description: str, author_id: str) -> ToolBlueprint:
        """Create new tool blueprint"""
        blueprint = ToolBlueprint(blueprint_id, name, description, author_id=author_id)
        self.blueprints[blueprint_id] = blueprint
        return blueprint

    def get_blueprint(self, blueprint_id: str) -> Optional[ToolBlueprint]:
        """Get blueprint"""
        return self.blueprints.get(blueprint_id)

    def validate_blueprint(self, blueprint_id: str) -> bool:
        """Validate blueprint for compilation"""
        blueprint = self.get_blueprint(blueprint_id)
        if not blueprint:
            return False

        # Must have at least one component
        if len(blueprint.components) == 0:
            return False

        # Must have inputs and outputs defined
        if len(blueprint.inputs) == 0 or len(blueprint.outputs) == 0:
            return False

        # Must have test cases
        if len(blueprint.test_cases) == 0:
            return False

        return True

    def compile_tool(self, blueprint_id: str) -> Optional[CustomTool]:
        """Compile blueprint into executable tool"""
        blueprint = self.get_blueprint(blueprint_id)
        if not blueprint:
            return None

        if not self.validate_blueprint(blueprint_id):
            return None

        # Run test cases to determine reliability
        pass_count = len(blueprint.test_cases)  # Simplified
        test_pass_rate = 1.0  # In real system, actually run tests

        tool = CustomTool(
            tool_id=f"tool_{blueprint_id}",
            blueprint_id=blueprint_id,
            name=blueprint.name,
            description=blueprint.description,
            inputs=blueprint.inputs,
            outputs=blueprint.outputs,
            reliability=blueprint.reliability * test_pass_rate,
            test_pass_rate=test_pass_rate
        )

        self.tools[tool.tool_id] = tool
        return tool

    def publish_tool(self, tool_id: str) -> bool:
        """Publish tool to library for other players"""
        if tool_id not in self.tools:
            return False

        tool = self.tools[tool_id]
        # Only publish if reliable enough
        if tool.reliability < 0.7:
            return False

        self.tool_library[tool_id] = tool
        return True

    def get_library_tools(self) -> List[CustomTool]:
        """Get all published tools in library"""
        return list(self.tool_library.values())

    def get_tool_by_inputs(self, required_inputs: List[str]) -> List[CustomTool]:
        """Find tools that accept given inputs"""
        matching = []
        for tool in self.get_library_tools():
            if all(inp in tool.inputs for inp in required_inputs):
                matching.append(tool)
        return matching

    def to_dict(self) -> Dict:
        return {
            "blueprints": len(self.blueprints),
            "custom_tools": len(self.tools),
            "library_tools": len(self.tool_library)
        }


# ===== Tests =====

def test_tool_primitive():
    """Test tool primitives"""
    assert ToolPrimitive.INPUT.value == "input"
    assert ToolPrimitive.PROCESS.value == "process"


def test_tool_component():
    """Test tool component"""
    component = ToolComponent("c1", ToolPrimitive.INPUT)
    assert component.component_id == "c1"
    assert component.primitive == ToolPrimitive.INPUT


def test_tool_blueprint_creation():
    """Test creating tool blueprint"""
    blueprint = ToolBlueprint("bp1", "My Tool", "Description")
    assert blueprint.blueprint_id == "bp1"
    assert blueprint.name == "My Tool"


def test_add_component():
    """Test adding component to blueprint"""
    blueprint = ToolBlueprint("bp1", "Tool", "Desc")
    component = ToolComponent("c1", ToolPrimitive.INPUT)
    assert blueprint.add_component(component) is True


def test_add_input_output():
    """Test adding inputs and outputs"""
    blueprint = ToolBlueprint("bp1", "Tool", "Desc")
    assert blueprint.add_input("text") is True
    assert blueprint.add_output("result") is True


def test_add_test_case():
    """Test adding test case"""
    blueprint = ToolBlueprint("bp1", "Tool", "Desc")
    assert blueprint.add_test_case({"input": "hello"}, {"output": "HELLO"}) is True


def test_custom_tool_creation():
    """Test creating custom tool"""
    tool = CustomTool(
        "t1",
        "bp1",
        "My Tool",
        "Description",
        ["text"],
        ["result"],
        0.9,
        0.95
    )
    assert tool.tool_id == "t1"
    assert tool.reliability == 0.9


def test_tool_execution():
    """Test executing tool"""
    tool = CustomTool("t1", "bp1", "Tool", "Desc", ["text"], ["result"], 0.9, 0.95)
    result = tool.execute({"text": "hello"})
    assert result is not None
    assert tool.usage_count == 1
    assert tool.success_count == 1


def test_tool_execution_failure():
    """Test tool execution with missing input"""
    tool = CustomTool("t1", "bp1", "Tool", "Desc", ["text"], ["result"], 0.9, 0.95)
    result = tool.execute({"other": "data"})
    assert result is None
    assert tool.usage_count == 1
    assert tool.success_count == 0


def test_tool_success_rate():
    """Test calculating success rate"""
    tool = CustomTool("t1", "bp1", "Tool", "Desc", ["text"], ["result"], 0.9, 0.95)
    tool.execute({"text": "hello"})
    tool.execute({"other": "data"})
    tool.execute({"text": "world"})

    success_rate = tool.get_success_rate()
    assert abs(success_rate - 0.666) < 0.01  # 2 out of 3


def test_tool_builder():
    """Test tool builder"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "Tool", "Desc", "author1")
    assert blueprint is not None


def test_create_blueprint():
    """Test creating blueprint with builder"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "MyTool", "Does something", "author1")
    assert builder.get_blueprint("bp1") is not None


def test_validate_blueprint():
    """Test blueprint validation"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "Tool", "Desc", "author1")

    # Invalid without components
    assert builder.validate_blueprint("bp1") is False

    # Add components and IO
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.INPUT))
    blueprint.add_input("text")
    blueprint.add_output("result")

    # Still invalid without tests
    assert builder.validate_blueprint("bp1") is False

    # Add test case
    blueprint.add_test_case({"text": "hello"}, {"result": "HELLO"})

    # Now valid
    assert builder.validate_blueprint("bp1") is True


def test_compile_tool():
    """Test compiling blueprint to tool"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "Tool", "Desc", "author1")
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.PROCESS))
    blueprint.add_input("data")
    blueprint.add_output("processed")
    blueprint.add_test_case({"data": "test"}, {"processed": "TEST"})

    tool = builder.compile_tool("bp1")
    assert tool is not None
    assert tool.tool_id == "tool_bp1"


def test_publish_tool():
    """Test publishing tool to library"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "Tool", "Desc", "author1")
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.PROCESS))
    blueprint.add_input("data")
    blueprint.add_output("processed")
    blueprint.add_test_case({"data": "test"}, {"processed": "TEST"})
    blueprint.reliability = 0.8  # Good reliability

    tool = builder.compile_tool("bp1")
    assert builder.publish_tool(tool.tool_id) is True


def test_get_library_tools():
    """Test getting tools from library"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "Tool1", "Desc", "author1")
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.PROCESS))
    blueprint.add_input("data")
    blueprint.add_output("processed")
    blueprint.add_test_case({"data": "test"}, {"processed": "TEST"})
    blueprint.reliability = 0.8

    tool = builder.compile_tool("bp1")
    builder.publish_tool(tool.tool_id)

    library = builder.get_library_tools()
    assert len(library) == 1


def test_find_tools_by_input():
    """Test finding tools by required inputs"""
    builder = ToolBuilder()
    blueprint = builder.create_blueprint("bp1", "TextProcessor", "Processes text", "author1")
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.PROCESS))
    blueprint.add_input("text")
    blueprint.add_output("processed")
    blueprint.add_test_case({"text": "hello"}, {"processed": "HELLO"})
    blueprint.reliability = 0.8

    tool = builder.compile_tool("bp1")
    builder.publish_tool(tool.tool_id)

    # Find tools that accept "text" input
    matching = builder.get_tool_by_inputs(["text"])
    assert len(matching) == 1


def test_complete_tool_creation_workflow():
    """Test complete tool creation and sharing workflow"""
    builder = ToolBuilder()

    # Player 1 designs a text transformation tool
    blueprint = builder.create_blueprint("bp_upper", "UpperCase", "Convert to uppercase", "player1")
    blueprint.add_component(ToolComponent("c1", ToolPrimitive.PROCESS))
    blueprint.add_component(ToolComponent("c2", ToolPrimitive.OUTPUT))
    blueprint.add_input("text")
    blueprint.add_output("uppercase_text")
    blueprint.add_test_case({"text": "hello"}, {"uppercase_text": "HELLO"})
    blueprint.add_test_case({"text": "world"}, {"uppercase_text": "WORLD"})
    blueprint.reliability = 0.95

    # Compile and test
    tool = builder.compile_tool("bp_upper")
    assert tool is not None
    assert tool.reliability >= 0.9

    # Publish for others to use
    assert builder.publish_tool(tool.tool_id) is True

    # Player 2 discovers and uses the tool
    available = builder.get_tool_by_inputs(["text"])
    assert len(available) >= 1
    assert available[0].name == "UpperCase"

    # Player 2's agent uses the tool
    result = available[0].execute({"text": "test"})
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
