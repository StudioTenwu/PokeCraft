"""
Test suite for agent execution engine.
Tests tool execution, task delegation, and operation results.
"""

import pytest
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecutionResult:
    """Result from executing a tool or operation."""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_id: Optional[str] = None


class ExecutionEngine:
    """Executes agent operations using tools."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.execution_history: List[ExecutionResult] = []
        self.tool_implementations: Dict[str, Callable] = {}
        self.max_retries = 3

    def register_tool_implementation(self, tool_id: str, implementation: Callable) -> None:
        """Register a tool implementation (the actual logic)."""
        self.tool_implementations[tool_id] = implementation

    def execute_tool(self, tool_id: str, inputs: Dict[str, Any],
                    timeout: float = 30.0) -> ExecutionResult:
        """Execute a tool and return the result."""
        if tool_id not in self.tool_implementations:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Tool not registered: {tool_id}"
            )

        try:
            start_time = datetime.now()
            impl = self.tool_implementations[tool_id]
            output = impl(**inputs)
            elapsed = (datetime.now() - start_time).total_seconds()

            result = ExecutionResult(
                success=True,
                output=output,
                execution_time=elapsed,
                tool_id=tool_id
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            result = ExecutionResult(
                success=False,
                output=None,
                error=str(e),
                tool_id=tool_id
            )
            self.execution_history.append(result)
            return result

    def execute_with_retry(self, tool_id: str, inputs: Dict[str, Any],
                          max_retries: Optional[int] = None) -> ExecutionResult:
        """Execute a tool with automatic retry on failure."""
        retries = max_retries or self.max_retries

        for attempt in range(retries):
            result = self.execute_tool(tool_id, inputs)
            if result.success:
                return result

        return result  # Return last failure

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool executions."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0
            }

        successful = sum(1 for r in self.execution_history if r.success)
        total = len(self.execution_history)

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_execution_time": (
                sum(r.execution_time for r in self.execution_history) / total
                if total > 0 else 0.0
            )
        }

    def get_execution_history(self, limit: int = 10) -> List[ExecutionResult]:
        """Get recent execution history."""
        return self.execution_history[-limit:]


class ToolLibrary:
    """Standard library of tool implementations."""

    @staticmethod
    def text_read(text: str, max_chars: int = 100) -> Dict[str, Any]:
        """Read and process text."""
        return {
            "text": text[:max_chars],
            "length": len(text),
            "truncated": len(text) > max_chars
        }

    @staticmethod
    def text_write(content: str, style: str = "plain") -> Dict[str, Any]:
        """Write and format text."""
        if style == "uppercase":
            output = content.upper()
        elif style == "bold":
            output = f"**{content}**"
        else:
            output = content

        return {"output": output, "style": style}

    @staticmethod
    def math_add(a: float, b: float) -> Dict[str, Any]:
        """Add two numbers."""
        return {"result": a + b, "operands": [a, b]}

    @staticmethod
    def math_multiply(a: float, b: float) -> Dict[str, Any]:
        """Multiply two numbers."""
        return {"result": a * b, "operands": [a, b]}


class TestExecutionEngine:
    """Test the execution engine."""

    def test_register_tool(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)

        assert "add" in engine.tool_implementations

    def test_execute_registered_tool(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)

        result = engine.execute_tool("add", {"a": 5, "b": 3})

        assert result.success is True
        assert result.output["result"] == 8
        assert result.tool_id == "add"

    def test_execute_unregistered_tool(self):
        engine = ExecutionEngine("agent_1")

        result = engine.execute_tool("unknown_tool", {})

        assert result.success is False
        assert "not registered" in result.error

    def test_tool_with_error(self):
        engine = ExecutionEngine("agent_1")

        def bad_tool(**kwargs):
            raise ValueError("Intentional error")

        engine.register_tool_implementation("bad", bad_tool)

        result = engine.execute_tool("bad", {})

        assert result.success is False
        assert result.error is not None

    def test_execution_history(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)

        engine.execute_tool("add", {"a": 1, "b": 2})
        engine.execute_tool("add", {"a": 10, "b": 20})

        history = engine.get_execution_history()
        assert len(history) == 2

    def test_execution_stats(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)
        engine.register_tool_implementation("multiply", ToolLibrary.math_multiply)

        # Successful executions
        engine.execute_tool("add", {"a": 1, "b": 1})
        engine.execute_tool("multiply", {"a": 2, "b": 3})

        stats = engine.get_execution_stats()
        assert stats["total_executions"] == 2
        assert stats["successful"] == 2
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0

    def test_execution_with_retry(self):
        engine = ExecutionEngine("agent_1")
        call_count = 0

        def flaky_tool():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"success": True}

        engine.register_tool_implementation("flaky", flaky_tool)

        result = engine.execute_with_retry("flaky", {}, max_retries=5)

        assert result.success is True
        assert call_count == 3

    def test_execution_time_tracking(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)

        result = engine.execute_tool("add", {"a": 5, "b": 3})

        assert result.execution_time >= 0.0
        # Should be very fast for simple operation
        assert result.execution_time < 1.0


class TestToolLibrary:
    """Test standard tool implementations."""

    def test_text_read(self):
        result = ToolLibrary.text_read("Hello world", max_chars=5)
        assert result["text"] == "Hello"
        assert result["truncated"] is True

    def test_text_write_plain(self):
        result = ToolLibrary.text_write("Test", style="plain")
        assert result["output"] == "Test"

    def test_text_write_uppercase(self):
        result = ToolLibrary.text_write("hello", style="uppercase")
        assert result["output"] == "HELLO"

    def test_text_write_bold(self):
        result = ToolLibrary.text_write("important", style="bold")
        assert "**important**" in result["output"]

    def test_math_operations(self):
        add_result = ToolLibrary.math_add(10, 5)
        assert add_result["result"] == 15

        mul_result = ToolLibrary.math_multiply(10, 5)
        assert mul_result["result"] == 50


class TestExecutionPipeline:
    """Test executing sequences of operations."""

    def test_execute_sequence(self):
        engine = ExecutionEngine("agent_1")
        engine.register_tool_implementation("add", ToolLibrary.math_add)
        engine.register_tool_implementation("multiply", ToolLibrary.math_multiply)

        # Chain: (5 + 3) * 2
        result1 = engine.execute_tool("add", {"a": 5, "b": 3})
        assert result1.success is True
        intermediate = result1.output["result"]

        result2 = engine.execute_tool("multiply", {"a": intermediate, "b": 2})
        assert result2.success is True
        assert result2.output["result"] == 16

        assert len(engine.execution_history) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
