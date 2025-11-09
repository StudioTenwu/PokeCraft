"""
Test suite for Real-World Integration & Export (Round 14).
Tests agent export, real-world task execution, and integration.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class RealWorldEnvironment(Enum):
    """Real-world contexts where agents operate."""
    HOMEWORK = "homework"
    CREATIVE = "creative"  # Art, music, writing
    ROBOTICS = "robotics"
    RESEARCH = "research"
    SOCIAL = "social"  # Multi-agent interaction


class ExportFormat(Enum):
    """Formats to export agents in."""
    JSON = "json"
    PYTHON = "python"
    BINARY = "binary"
    API = "api"


class RealWorldTask:
    """A task executed in the real world."""

    def __init__(self, task_id: str, environment: RealWorldEnvironment, description: str):
        self.task_id = task_id
        self.environment = environment
        self.description = description
        self.created_at = datetime.now()
        self.assigned_agent_id: Optional[str] = None
        self.status = "pending"  # pending, assigned, in_progress, completed, failed
        self.result: Optional[Dict[str, Any]] = None
        self.execution_time: float = 0.0
        self.success_metrics: Dict[str, float] = {}

    def assign_agent(self, agent_id: str) -> bool:
        """Assign an agent to the task."""
        if self.assigned_agent_id is not None:
            return False
        self.assigned_agent_id = agent_id
        self.status = "assigned"
        return True

    def start_execution(self) -> bool:
        """Mark task execution as started."""
        if self.status != "assigned":
            return False
        self.status = "in_progress"
        self.started_at = datetime.now()
        return True

    def complete(self, result: Dict[str, Any], metrics: Dict[str, float] = None) -> bool:
        """Mark task as completed."""
        if self.status != "in_progress":
            return False

        self.status = "completed"
        self.result = result
        self.execution_time = (datetime.now() - self.started_at).total_seconds()
        if metrics:
            self.success_metrics = metrics
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task."""
        return {
            "task_id": self.task_id,
            "environment": self.environment.value,
            "description": self.description,
            "status": self.status,
            "assigned_agent": self.assigned_agent_id,
            "execution_time": self.execution_time,
            "success_metrics": self.success_metrics
        }


class AgentExport:
    """Exports an agent for external use."""

    def __init__(self, agent_id: str, export_format: ExportFormat = ExportFormat.JSON):
        self.agent_id = agent_id
        self.export_format = export_format
        self.export_time = datetime.now()
        self.exported_state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "version": "1.0",
            "created_at": self.export_time.isoformat()
        }
        self.compatible_environments: List[str] = []

    def add_state(self, key: str, value: Any) -> bool:
        """Add state to export."""
        self.exported_state[key] = value
        return True

    def mark_compatible_environment(self, environment: RealWorldEnvironment) -> bool:
        """Mark environment as compatible."""
        env_str = environment.value
        if env_str not in self.compatible_environments:
            self.compatible_environments.append(env_str)
            return True
        return False

    def get_export_package(self) -> Dict[str, Any]:
        """Get complete export package."""
        return {
            "agent_id": self.agent_id,
            "format": self.export_format.value,
            "metadata": self.metadata,
            "state": self.exported_state,
            "compatible_environments": self.compatible_environments
        }

    def export_to_file(self, filepath: str) -> bool:
        """Export to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.get_export_package(), f, indent=2)
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize export."""
        return self.get_export_package()


class RealWorldIntegration:
    """Manages agent deployment to real world."""

    def __init__(self):
        self.active_tasks: Dict[str, RealWorldTask] = {}
        self.completed_tasks: List[RealWorldTask] = []
        self.agent_deployments: Dict[str, List[str]] = {}  # agent_id -> [task_ids]
        self.performance_metrics: Dict[str, Dict[str, float]] = {}

    def create_task(self, task: RealWorldTask) -> bool:
        """Create a real-world task."""
        if task.task_id in self.active_tasks:
            return False
        self.active_tasks[task.task_id] = task
        return True

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign an agent to a task."""
        if task_id not in self.active_tasks:
            return False

        task = self.active_tasks[task_id]
        if not task.assign_agent(agent_id):
            return False

        if agent_id not in self.agent_deployments:
            self.agent_deployments[agent_id] = []
        self.agent_deployments[agent_id].append(task_id)

        return True

    def execute_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Execute and complete a task."""
        if task_id not in self.active_tasks:
            return False

        task = self.active_tasks[task_id]
        if not task.start_execution():
            return False

        if task.complete(result):
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            return True

        return False

    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get agent performance metrics."""
        if agent_id not in self.agent_deployments:
            return {"agent_id": agent_id, "tasks": 0, "success_rate": 0.0}

        task_ids = self.agent_deployments[agent_id]
        completed = [t for t in self.completed_tasks if t.task_id in task_ids]

        if not completed:
            return {
                "agent_id": agent_id,
                "tasks_assigned": len(task_ids),
                "tasks_completed": 0,
                "success_rate": 0.0
            }

        successful = sum(1 for t in completed if t.status == "completed")
        return {
            "agent_id": agent_id,
            "tasks_assigned": len(task_ids),
            "tasks_completed": len(completed),
            "success_rate": successful / len(completed),
            "avg_execution_time": sum(t.execution_time for t in completed) / len(completed)
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        return None

    def get_system_summary(self) -> Dict[str, Any]:
        """Get summary of real-world integration."""
        return {
            "total_agents": len(self.agent_deployments),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "total_tasks": len(self.active_tasks) + len(self.completed_tasks),
            "overall_completion_rate": len(self.completed_tasks) / max(1, len(self.active_tasks) + len(self.completed_tasks))
        }


class ExportManager:
    """Manages agent exports to different formats."""

    def __init__(self, storage_dir: str = "./agent_exports"):
        self.storage_dir = storage_dir
        self.exports: Dict[str, AgentExport] = {}
        os.makedirs(storage_dir, exist_ok=True)

    def export_agent(self, agent_id: str, export_format: ExportFormat = ExportFormat.JSON) -> AgentExport:
        """Export an agent."""
        export = AgentExport(agent_id, export_format)
        self.exports[agent_id] = export
        return export

    def save_export(self, agent_id: str) -> bool:
        """Save export to disk."""
        if agent_id not in self.exports:
            return False

        export = self.exports[agent_id]
        filepath = os.path.join(self.storage_dir, f"{agent_id}_export.json")

        return export.export_to_file(filepath)

    def load_export(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load export from file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def get_export_list(self) -> List[str]:
        """Get list of exported agent IDs."""
        return list(self.exports.keys())

    def get_export_summary(self) -> Dict[str, Any]:
        """Get summary of exports."""
        return {
            "total_exports": len(self.exports),
            "formats": {fmt.value: sum(1 for e in self.exports.values() if e.export_format == fmt) for fmt in ExportFormat},
            "storage_directory": self.storage_dir
        }


# ===== TESTS =====

def test_real_world_task_creation():
    """Test creating real-world tasks."""
    task = RealWorldTask("task_1", RealWorldEnvironment.HOMEWORK, "Write essay")
    assert task.task_id == "task_1"
    assert task.environment == RealWorldEnvironment.HOMEWORK
    assert task.status == "pending"


def test_task_assignment():
    """Test assigning tasks to agents."""
    task = RealWorldTask("task_1", RealWorldEnvironment.CREATIVE, "Create art")
    assert task.assign_agent("agent_1")
    assert task.assigned_agent_id == "agent_1"
    assert task.status == "assigned"


def test_task_execution():
    """Test executing a task."""
    task = RealWorldTask("task_1", RealWorldEnvironment.HOMEWORK, "Task")
    task.assign_agent("agent_1")

    assert task.start_execution()
    assert task.status == "in_progress"

    result = {"score": 95, "feedback": "Excellent work"}
    assert task.complete(result, {"quality": 0.95})
    assert task.status == "completed"


def test_agent_export_creation():
    """Test creating agent exports."""
    export = AgentExport("agent_1", ExportFormat.JSON)
    assert export.agent_id == "agent_1"
    assert export.export_format == ExportFormat.JSON


def test_agent_export_state():
    """Test adding state to export."""
    export = AgentExport("agent_1")
    assert export.add_state("personality", {"helpful": 0.8})
    assert export.add_state("memory_size", 100)
    assert len(export.exported_state) == 2


def test_agent_export_compatibility():
    """Test marking compatible environments."""
    export = AgentExport("agent_1")
    assert export.mark_compatible_environment(RealWorldEnvironment.HOMEWORK)
    assert export.mark_compatible_environment(RealWorldEnvironment.ROBOTICS)
    assert len(export.compatible_environments) == 2


def test_agent_export_package():
    """Test generating export package."""
    export = AgentExport("agent_1", ExportFormat.PYTHON)
    export.add_state("version", "2.0")
    export.mark_compatible_environment(RealWorldEnvironment.SOCIAL)

    package = export.get_export_package()
    assert package["agent_id"] == "agent_1"
    assert package["format"] == "python"
    assert "version" in package["state"]


def test_agent_export_to_file():
    """Test exporting agent to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        export = AgentExport("agent_1")
        export.add_state("test", "data")

        filepath = os.path.join(tmpdir, "agent_export.json")
        assert export.export_to_file(filepath)
        assert os.path.exists(filepath)


def test_real_world_integration_task_creation():
    """Test creating tasks in integration."""
    integration = RealWorldIntegration()
    task = RealWorldTask("t1", RealWorldEnvironment.HOMEWORK, "Write")

    assert integration.create_task(task)
    assert "t1" in integration.active_tasks


def test_real_world_integration_assignment():
    """Test task assignment in integration."""
    integration = RealWorldIntegration()
    task = RealWorldTask("t1", RealWorldEnvironment.HOMEWORK, "Task")
    integration.create_task(task)

    assert integration.assign_task("t1", "agent_1")
    assert "agent_1" in integration.agent_deployments


def test_real_world_integration_execution():
    """Test executing tasks."""
    integration = RealWorldIntegration()
    task = RealWorldTask("t1", RealWorldEnvironment.CREATIVE, "Create")
    integration.create_task(task)
    integration.assign_task("t1", "agent_1")

    result = {"output": "creative work"}
    assert integration.execute_task("t1", result)
    assert len(integration.completed_tasks) == 1


def test_agent_performance_metrics():
    """Test getting agent performance."""
    integration = RealWorldIntegration()

    task1 = RealWorldTask("t1", RealWorldEnvironment.HOMEWORK, "Task 1")
    task2 = RealWorldTask("t2", RealWorldEnvironment.HOMEWORK, "Task 2")

    integration.create_task(task1)
    integration.create_task(task2)

    integration.assign_task("t1", "agent_1")
    integration.assign_task("t2", "agent_1")

    integration.execute_task("t1", {"result": "success"})

    perf = integration.get_agent_performance("agent_1")
    assert perf["tasks_assigned"] == 2
    assert perf["tasks_completed"] == 1


def test_export_manager_creation():
    """Test export manager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportManager(tmpdir)
        export = manager.export_agent("agent_1")

        assert "agent_1" in manager.exports
        assert len(manager.get_export_list()) == 1


def test_export_manager_save_load():
    """Test saving and loading exports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportManager(tmpdir)
        export = manager.export_agent("agent_1")
        export.add_state("data", "value")

        assert manager.save_export("agent_1")

        filepath = os.path.join(tmpdir, "agent_1_export.json")
        loaded = manager.load_export(filepath)

        assert loaded is not None
        assert loaded["agent_id"] == "agent_1"


def test_export_summary():
    """Test export summary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportManager(tmpdir)
        manager.export_agent("agent_1", ExportFormat.JSON)
        manager.export_agent("agent_2", ExportFormat.PYTHON)

        summary = manager.get_export_summary()
        assert summary["total_exports"] == 2


def test_system_summary():
    """Test getting system summary."""
    integration = RealWorldIntegration()

    task = RealWorldTask("t1", RealWorldEnvironment.ROBOTICS, "Control robot")
    integration.create_task(task)

    summary = integration.get_system_summary()
    assert summary["active_tasks"] == 1
    assert summary["completed_tasks"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
