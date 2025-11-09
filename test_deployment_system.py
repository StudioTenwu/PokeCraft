"""
Round 49: Real-World Deployment System
Agents can be deployed to perform real-world tasks and integrate with external systems.
Features: deployment configurations, task execution, performance monitoring, result tracking.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class DeploymentTarget(Enum):
    """Where agent can be deployed"""
    HOMEWORK = "homework"  # Real homework/assignment APIs
    GAME = "game"  # Game environments
    ROBOT = "robot"  # Robotic systems
    API = "api"  # REST API services
    PLUGIN = "plugin"  # Browser extensions
    WORKFLOW = "workflow"  # Business workflow systems
    COMMUNITY = "community"  # Community shared tasks
    CUSTOM = "custom"  # Custom user-defined


class TaskStatus(Enum):
    """Status of deployed task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PerformanceRating(Enum):
    """Rating of agent performance"""
    POOR = 0.2
    FAIR = 0.4
    GOOD = 0.6
    EXCELLENT = 0.8
    OUTSTANDING = 1.0


@dataclass
class DeploymentConfig:
    """Configuration for deploying agent"""
    config_id: str
    agent_id: str
    target: DeploymentTarget
    target_url: str
    timeout: float = 30.0
    retry_count: int = 3
    auto_retry: bool = True
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    allowed_operations: List[str] = field(default_factory=list)
    sandboxed: bool = True
    enabled: bool = True

    def to_dict(self) -> Dict:
        return {
            "id": self.config_id,
            "agent": self.agent_id,
            "target": self.target.value,
            "timeout": self.timeout,
            "sandboxed": self.sandboxed
        }


@dataclass
class DeployedTask:
    """Task executed by deployed agent"""
    task_id: str
    config_id: str
    agent_id: str
    task_type: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    started_at: float = 0.0
    completed_at: float = 0.0
    attempts: int = 0
    last_error: str = ""

    def is_completed(self) -> bool:
        """Check if task is finished"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    def get_duration(self) -> float:
        """Get task duration in seconds"""
        if self.started_at == 0.0 or self.completed_at == 0.0:
            return 0.0
        return self.completed_at - self.started_at

    def to_dict(self) -> Dict:
        return {
            "id": self.task_id,
            "agent": self.agent_id,
            "type": self.task_type,
            "status": self.status.value,
            "attempts": self.attempts,
            "duration": self.get_duration()
        }


@dataclass
class TaskResult:
    """Result of deployed task execution"""
    result_id: str
    task_id: str
    agent_id: str
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    performance_rating: float = 0.5  # 0.0-1.0
    timestamp: float = 0.0
    execution_time_ms: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.result_id,
            "task": self.task_id,
            "agent": self.agent_id,
            "success": self.success,
            "rating": self.performance_rating,
            "exec_time": self.execution_time_ms
        }


@dataclass
class DeploymentMetrics:
    """Metrics for deployed agent"""
    agent_id: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    success_rate: float = 0.0  # 0.0-1.0
    avg_performance: float = 0.5  # 0.0-1.0
    avg_execution_time_ms: float = 0.0
    total_hours_deployed: float = 0.0
    uptime_percent: float = 1.0  # 0.0-1.0

    def calculate_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks

    def update_from_result(self, result: TaskResult) -> None:
        """Update metrics from task result"""
        self.total_tasks += 1

        if result.success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1

        # Update averages
        if self.total_tasks == 1:
            self.avg_performance = result.performance_rating
            self.avg_execution_time_ms = result.execution_time_ms
        else:
            # Exponential moving average
            alpha = 0.3
            self.avg_performance = (alpha * result.performance_rating) + ((1 - alpha) * self.avg_performance)
            self.avg_execution_time_ms = (alpha * result.execution_time_ms) + ((1 - alpha) * self.avg_execution_time_ms)

        self.success_rate = self.calculate_success_rate()

    def to_dict(self) -> Dict:
        return {
            "agent": self.agent_id,
            "total": self.total_tasks,
            "successful": self.successful_tasks,
            "success_rate": round(self.success_rate, 3),
            "avg_performance": round(self.avg_performance, 2),
            "uptime": round(self.uptime_percent, 2)
        }


class DeploymentConfigManager:
    """Manages deployment configurations"""

    def __init__(self):
        self.configs: Dict[str, DeploymentConfig] = {}
        self.agent_configs: Dict[str, List[str]] = {}  # agent_id -> config_ids

    def register_config(self, config: DeploymentConfig) -> bool:
        """Register deployment configuration"""
        if config.config_id in self.configs:
            return False

        self.configs[config.config_id] = config

        if config.agent_id not in self.agent_configs:
            self.agent_configs[config.agent_id] = []
        self.agent_configs[config.agent_id].append(config.config_id)

        return True

    def get_config(self, config_id: str) -> Optional[DeploymentConfig]:
        """Get configuration by ID"""
        return self.configs.get(config_id)

    def list_agent_configs(self, agent_id: str) -> List[DeploymentConfig]:
        """Get all configs for agent"""
        if agent_id not in self.agent_configs:
            return []

        config_ids = self.agent_configs[agent_id]
        return [self.configs[cid] for cid in config_ids if cid in self.configs]

    def enable_config(self, config_id: str) -> bool:
        """Enable configuration"""
        if config_id not in self.configs:
            return False
        self.configs[config_id].enabled = True
        return True

    def disable_config(self, config_id: str) -> bool:
        """Disable configuration"""
        if config_id not in self.configs:
            return False
        self.configs[config_id].enabled = False
        return True

    def to_dict(self) -> Dict:
        return {
            "total_configs": len(self.configs),
            "agents_deployed": len(self.agent_configs)
        }


class TaskExecutor:
    """Executes deployed tasks"""

    def __init__(self):
        self.tasks: Dict[str, DeployedTask] = {}
        self.results: Dict[str, TaskResult] = {}

    def create_task(self, task: DeployedTask) -> bool:
        """Create new task"""
        if task.task_id in self.tasks:
            return False

        self.tasks[task.task_id] = task
        return True

    def start_task(self, task_id: str, current_time: float = 0.0) -> bool:
        """Start task execution"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = current_time
        task.attempts += 1
        return True

    def complete_task(self, task_id: str, success: bool, current_time: float = 0.0) -> bool:
        """Mark task as complete"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = current_time
        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel task"""
        if task_id not in self.tasks:
            return False

        self.tasks[task_id].status = TaskStatus.CANCELLED
        return True

    def record_result(self, result: TaskResult) -> bool:
        """Record task result"""
        if result.result_id in self.results:
            return False

        self.results[result.result_id] = result
        return True

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for task"""
        for result in self.results.values():
            if result.task_id == task_id:
                return result
        return None

    def get_agent_results(self, agent_id: str) -> List[TaskResult]:
        """Get all results for agent"""
        return [r for r in self.results.values() if r.agent_id == agent_id]

    def to_dict(self) -> Dict:
        return {
            "total_tasks": len(self.tasks),
            "total_results": len(self.results),
            "pending": len([t for t in self.tasks.values() if not t.is_completed()])
        }


class DeploymentManager:
    """Central manager for agent deployment"""

    def __init__(self):
        self.config_manager = DeploymentConfigManager()
        self.task_executor = TaskExecutor()
        self.metrics: Dict[str, DeploymentMetrics] = {}

    def register_deployment(self, config: DeploymentConfig) -> bool:
        """Register agent deployment configuration"""
        return self.config_manager.register_config(config)

    def deploy_agent(self, config_id: str, task_type: str, input_data: Dict) -> Optional[DeployedTask]:
        """Deploy agent to execute task"""
        config = self.config_manager.get_config(config_id)
        if not config or not config.enabled:
            return None

        task = DeployedTask(
            task_id=f"task_{len(self.task_executor.tasks)}",
            config_id=config_id,
            agent_id=config.agent_id,
            task_type=task_type,
            input_data=input_data
        )

        if not self.task_executor.create_task(task):
            return None

        return task

    def execute_task(self, task_id: str, success: bool, performance: float = 0.5,
                    output: Dict = None, exec_time_ms: float = 0.0) -> Optional[TaskResult]:
        """Execute task and record result"""
        if output is None:
            output = {}

        if not self.task_executor.start_task(task_id, 0.0):
            return None

        if not self.task_executor.complete_task(task_id, success, 1.0):
            return None

        task = self.task_executor.tasks.get(task_id)
        if not task:
            return None

        result = TaskResult(
            result_id=f"res_{len(self.task_executor.results)}",
            task_id=task_id,
            agent_id=task.agent_id,
            success=success,
            output=output,
            performance_rating=performance,
            execution_time_ms=exec_time_ms
        )

        if not self.task_executor.record_result(result):
            return None

        # Update metrics
        if task.agent_id not in self.metrics:
            self.metrics[task.agent_id] = DeploymentMetrics(agent_id=task.agent_id)

        self.metrics[task.agent_id].update_from_result(result)

        return result

    def get_agent_metrics(self, agent_id: str) -> Optional[DeploymentMetrics]:
        """Get deployment metrics for agent"""
        return self.metrics.get(agent_id)

    def get_deployment_status(self, agent_id: str) -> Dict:
        """Get deployment status for agent"""
        configs = self.config_manager.list_agent_configs(agent_id)
        results = self.task_executor.get_agent_results(agent_id)
        metrics = self.get_agent_metrics(agent_id)

        return {
            "agent": agent_id,
            "deployments": len(configs),
            "tasks_executed": len(results),
            "active_configs": len([c for c in configs if c.enabled]),
            "metrics": metrics.to_dict() if metrics else {}
        }

    def to_dict(self) -> Dict:
        return {
            "configs": self.config_manager.to_dict(),
            "executor": self.task_executor.to_dict(),
            "agents_metrics": len(self.metrics)
        }


# ===== Tests =====

def test_deployment_config_creation():
    """Test creating deployment config"""
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://homework-api.example.com"
    )
    assert config.config_id == "cfg1"
    assert config.target == DeploymentTarget.HOMEWORK


def test_deployment_config_manager_register():
    """Test registering config"""
    manager = DeploymentConfigManager()
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://homework-api.example.com"
    )
    assert manager.register_config(config) is True
    assert manager.get_config("cfg1") is not None


def test_deployed_task_creation():
    """Test creating deployed task"""
    task = DeployedTask(
        "task1", "cfg1", "agent1", "homework_problem",
        input_data={"problem": "What is 2+2?"}
    )
    assert task.task_id == "task1"
    assert task.status == TaskStatus.PENDING


def test_deployed_task_completion():
    """Test task completion tracking"""
    task = DeployedTask(
        "task1", "cfg1", "agent1", "homework_problem"
    )
    assert task.is_completed() is False

    task.status = TaskStatus.COMPLETED
    assert task.is_completed() is True


def test_task_result_creation():
    """Test creating task result"""
    result = TaskResult(
        "res1", "task1", "agent1", True,
        output={"answer": "4"},
        performance_rating=0.95
    )
    assert result.result_id == "res1"
    assert result.success is True


def test_deployment_metrics_initial():
    """Test initial metrics"""
    metrics = DeploymentMetrics("agent1")
    assert metrics.success_rate == 0.0
    assert metrics.total_tasks == 0


def test_deployment_metrics_update():
    """Test updating metrics from result"""
    metrics = DeploymentMetrics("agent1")
    result = TaskResult(
        "res1", "task1", "agent1", True,
        performance_rating=0.8, execution_time_ms=500
    )

    metrics.update_from_result(result)

    assert metrics.total_tasks == 1
    assert metrics.successful_tasks == 1
    assert metrics.success_rate == 1.0


def test_deployment_metrics_multiple_results():
    """Test metrics with multiple results"""
    metrics = DeploymentMetrics("agent1")

    r1 = TaskResult("res1", "t1", "agent1", True, performance_rating=0.8, execution_time_ms=500)
    r2 = TaskResult("res2", "t2", "agent1", True, performance_rating=0.9, execution_time_ms=400)
    r3 = TaskResult("res3", "t3", "agent1", False, performance_rating=0.2, execution_time_ms=1000)

    metrics.update_from_result(r1)
    metrics.update_from_result(r2)
    metrics.update_from_result(r3)

    assert metrics.total_tasks == 3
    assert metrics.successful_tasks == 2
    assert metrics.failed_tasks == 1
    assert 0.6 < metrics.success_rate < 0.7


def test_task_executor_create_task():
    """Test creating task in executor"""
    executor = TaskExecutor()
    task = DeployedTask("task1", "cfg1", "agent1", "test")

    assert executor.create_task(task) is True
    assert executor.tasks["task1"] is not None


def test_task_executor_execute():
    """Test task execution"""
    executor = TaskExecutor()
    task = DeployedTask("task1", "cfg1", "agent1", "test")
    executor.create_task(task)

    assert executor.start_task("task1", 0.0) is True
    assert executor.complete_task("task1", True, 1.0) is True

    assert executor.tasks["task1"].status == TaskStatus.COMPLETED


def test_task_executor_record_result():
    """Test recording result"""
    executor = TaskExecutor()
    result = TaskResult(
        "res1", "task1", "agent1", True,
        performance_rating=0.9
    )

    assert executor.record_result(result) is True
    assert executor.get_task_result("task1") is not None


def test_deployment_manager_register():
    """Test deployment manager"""
    manager = DeploymentManager()
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://api.example.com"
    )

    assert manager.register_deployment(config) is True


def test_deployment_manager_deploy():
    """Test deploying agent"""
    manager = DeploymentManager()
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://api.example.com", enabled=True
    )
    manager.register_deployment(config)

    task = manager.deploy_agent("cfg1", "homework", {"problem": "test"})
    assert task is not None
    assert task.status == TaskStatus.PENDING


def test_deployment_manager_execute():
    """Test executing deployed task"""
    manager = DeploymentManager()
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://api.example.com", enabled=True
    )
    manager.register_deployment(config)

    task = manager.deploy_agent("cfg1", "homework", {"problem": "2+2"})
    assert task is not None

    result = manager.execute_task(
        task.task_id, True, 0.95,
        {"answer": "4"}, 250.0
    )

    assert result is not None
    assert result.success is True


def test_deployment_manager_metrics():
    """Test deployment metrics"""
    manager = DeploymentManager()
    config = DeploymentConfig(
        "cfg1", "agent1", DeploymentTarget.HOMEWORK,
        "https://api.example.com", enabled=True
    )
    manager.register_deployment(config)

    for i in range(3):
        task = manager.deploy_agent("cfg1", "test", {})
        manager.execute_task(task.task_id, i < 2, 0.8 if i < 2 else 0.2)

    metrics = manager.get_agent_metrics("agent1")
    assert metrics.total_tasks == 3
    assert metrics.successful_tasks == 2


def test_complete_deployment_workflow():
    """Test complete deployment workflow"""
    manager = DeploymentManager()

    # Register deployment
    config = DeploymentConfig(
        "homework_cfg", "student_agent", DeploymentTarget.HOMEWORK,
        "https://homework-api.school.edu",
        timeout=60.0, retry_count=3
    )
    assert manager.register_deployment(config) is True

    # Deploy agent to homework
    task = manager.deploy_agent(
        "homework_cfg", "solve_problem",
        {"problem": "Calculate: 5 + 3"}
    )
    assert task is not None

    # Execute task
    result = manager.execute_task(
        task.task_id, True, 0.92,
        {"answer": "8", "steps": ["5+3", "8"]},
        350.0
    )
    assert result is not None
    assert result.success is True

    # Check metrics
    status = manager.get_deployment_status("student_agent")
    assert status["deployments"] >= 1
    assert status["tasks_executed"] >= 1
    assert "metrics" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
