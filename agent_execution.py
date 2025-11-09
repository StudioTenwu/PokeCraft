"""
Agent execution engine for AICraft.
Enables agents to execute tools, perform tasks, and interact with the world.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import uuid
import time


class ExecutionStatus(Enum):
    """Status of an execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result from executing a tool or operation."""
    execution_id: str
    tool_id: Optional[str]
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    timestamp: datetime = None
    retry_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result."""
        return {
            "execution_id": self.execution_id,
            "tool_id": self.tool_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count
        }


class ExecutionEngine:
    """Executes agent operations using tools."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.execution_history: List[ExecutionResult] = []
        self.tool_implementations: Dict[str, Callable] = {}
        self.max_retries = 3
        self.default_timeout = 30.0
        self.created_at = datetime.now()

    def register_tool_implementation(self, tool_id: str, implementation: Callable,
                                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a tool implementation (the actual logic)."""
        self.tool_implementations[tool_id] = {
            "impl": implementation,
            "metadata": metadata or {},
            "registered_at": datetime.now(),
            "call_count": 0,
            "success_count": 0
        }

    def execute_tool(self, tool_id: str, inputs: Dict[str, Any],
                    timeout: Optional[float] = None) -> ExecutionResult:
        """Execute a tool and return the result."""
        execution_id = str(uuid.uuid4())[:8]

        if tool_id not in self.tool_implementations:
            return ExecutionResult(
                execution_id=execution_id,
                tool_id=tool_id,
                success=False,
                error=f"Tool not registered: {tool_id}",
                status=ExecutionStatus.FAILED
            )

        try:
            tool_data = self.tool_implementations[tool_id]
            impl = tool_data["impl"]

            start_time = time.time()
            execution_timeout = timeout or self.default_timeout

            # Execute the tool
            output = impl(**inputs)

            elapsed = time.time() - start_time

            # Update statistics
            tool_data["call_count"] += 1
            tool_data["success_count"] += 1

            result = ExecutionResult(
                execution_id=execution_id,
                tool_id=tool_id,
                success=True,
                output=output,
                execution_time=elapsed,
                status=ExecutionStatus.SUCCESS
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            # Update statistics
            if tool_id in self.tool_implementations:
                self.tool_implementations[tool_id]["call_count"] += 1

            result = ExecutionResult(
                execution_id=execution_id,
                tool_id=tool_id,
                success=False,
                error=str(e),
                status=ExecutionStatus.FAILED
            )
            self.execution_history.append(result)
            return result

    def execute_with_retry(self, tool_id: str, inputs: Dict[str, Any],
                          max_retries: Optional[int] = None) -> ExecutionResult:
        """Execute a tool with automatic retry on failure."""
        retries = max_retries or self.max_retries
        last_result = None

        for attempt in range(retries):
            result = self.execute_tool(tool_id, inputs)
            result.retry_count = attempt

            if result.success:
                return result

            last_result = result

        return last_result or result

    def batch_execute(self, operations: List[Dict[str, Any]]) -> List[ExecutionResult]:
        """Execute multiple operations in sequence."""
        results = []

        for op in operations:
            tool_id = op.get("tool_id")
            inputs = op.get("inputs", {})
            timeout = op.get("timeout")

            result = self.execute_tool(tool_id, inputs, timeout)
            results.append(result)

            # Stop on critical failure
            if not result.success and op.get("critical", False):
                break

        return results

    def get_tool_stats(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get execution statistics for a specific tool."""
        if tool_id not in self.tool_implementations:
            return None

        tool_data = self.tool_implementations[tool_id]

        return {
            "tool_id": tool_id,
            "total_calls": tool_data["call_count"],
            "successful_calls": tool_data["success_count"],
            "failed_calls": tool_data["call_count"] - tool_data["success_count"],
            "success_rate": (
                tool_data["success_count"] / tool_data["call_count"]
                if tool_data["call_count"] > 0 else 0.0
            ),
            "registered_at": tool_data["registered_at"].isoformat()
        }

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get overall execution statistics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "tools_used": 0
            }

        successful = sum(1 for r in self.execution_history if r.success)
        total = len(self.execution_history)
        tools_used = len(set(r.tool_id for r in self.execution_history if r.tool_id))

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "avg_execution_time": (
                sum(r.execution_time for r in self.execution_history) / total
                if total > 0 else 0.0
            ),
            "tools_used": tools_used,
            "tools_registered": len(self.tool_implementations)
        }

    def get_execution_history(self, limit: int = 10, tool_id: Optional[str] = None) \
            -> List[ExecutionResult]:
        """Get recent execution history, optionally filtered by tool."""
        history = self.execution_history

        if tool_id:
            history = [r for r in history if r.tool_id == tool_id]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []

    def get_engine_report(self) -> str:
        """Generate a report of execution engine state."""
        stats = self.get_execution_stats()
        report = f"\n**Execution Engine Report for Agent {self.agent_id}**\n"
        report += f"- Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- Total Executions: {stats['total_executions']}\n"
        report += f"- Success Rate: {stats['success_rate']:.0%}\n"
        report += f"- Avg Execution Time: {stats['avg_execution_time']:.3f}s\n"
        report += f"- Tools Registered: {stats['tools_registered']}\n"
        report += f"- Tools Used: {stats['tools_used']}\n"

        if stats['total_executions'] > 0:
            report += f"\nRecent Executions:\n"
            for result in self.get_execution_history(limit=5):
                status_icon = "✓" if result.success else "✗"
                report += f"  {status_icon} {result.tool_id}: {result.status.value}\n"

        return report


# Standard tool library
class ToolLibrary:
    """Standard library of tool implementations."""

    @staticmethod
    def text_read(text: str, max_chars: int = 100) -> Dict[str, Any]:
        """Read and process text."""
        return {
            "text": text[:max_chars],
            "length": len(text),
            "truncated": len(text) > max_chars,
            "word_count": len(text.split())
        }

    @staticmethod
    def text_write(content: str, style: str = "plain") -> Dict[str, Any]:
        """Write and format text."""
        styles = {
            "uppercase": content.upper(),
            "lowercase": content.lower(),
            "bold": f"**{content}**",
            "italic": f"*{content}*",
            "plain": content
        }

        output = styles.get(style, content)

        return {
            "output": output,
            "style": style,
            "length": len(output)
        }

    @staticmethod
    def math_add(a: float, b: float) -> Dict[str, Any]:
        """Add two numbers."""
        return {
            "result": a + b,
            "operation": "addition",
            "operands": [a, b]
        }

    @staticmethod
    def math_multiply(a: float, b: float) -> Dict[str, Any]:
        """Multiply two numbers."""
        return {
            "result": a * b,
            "operation": "multiplication",
            "operands": [a, b]
        }

    @staticmethod
    def math_power(base: float, exponent: float) -> Dict[str, Any]:
        """Raise base to exponent."""
        return {
            "result": base ** exponent,
            "operation": "exponentiation",
            "base": base,
            "exponent": exponent
        }

    @staticmethod
    def list_process(items: List[Any], operation: str = "count") -> Dict[str, Any]:
        """Process a list."""
        if operation == "count":
            return {"result": len(items), "operation": "count"}
        elif operation == "reverse":
            return {"result": list(reversed(items)), "operation": "reverse"}
        elif operation == "unique":
            return {"result": list(set(items)), "operation": "unique"}
        else:
            return {"result": items, "operation": "noop"}
