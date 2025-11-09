"""
Real-World Integration & Export for AICraft (Round 14).
Enables agents to be deployed to and execute real-world tasks.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
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


@dataclass
class RealWorldTask:
    """A task executed in the real world."""
    task_id: str
    environment: RealWorldEnvironment
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent_id: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    success_metrics: Dict[str, float] = field(default_factory=dict)
    started_at: Optional[datetime] = None

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
        total = len(self.active_tasks) + len(self.completed_tasks)
        return {
            "total_agents": len(self.agent_deployments),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "total_tasks": total,
            "overall_completion_rate": len(self.completed_tasks) / max(1, total)
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
        format_counts = {}
        for export in self.exports.values():
            fmt = export.export_format.value
            format_counts[fmt] = format_counts.get(fmt, 0) + 1

        return {
            "total_exports": len(self.exports),
            "formats": format_counts,
            "storage_directory": self.storage_dir
        }
