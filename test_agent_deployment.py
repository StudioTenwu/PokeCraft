"""
Round 34: Agent Deployment to External Systems
"""

import pytest
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional


class DeploymentTarget(Enum):
    ROBOTICS = "robotics"
    GAME = "game"
    API = "api"
    FILESYSTEM = "filesystem"
    DISCORD = "discord"
    SLACK = "slack"
    DATABASE = "database"
    CUSTOM = "custom"


class ExecutionEnvironment(Enum):
    CLOUD = "cloud"
    LOCAL = "local"
    EMBEDDED = "embedded"
    WEB = "web"


@dataclass
class DeploymentConfig:
    config_id: str
    agent_id: str
    target: DeploymentTarget
    environment: ExecutionEnvironment
    enabled: bool = False

    def enable_deployment(self) -> bool:
        if self.enabled:
            return False
        self.enabled = True
        return True


@dataclass
class DeploymentMetrics:
    deployment_id: str
    requests: int = 0
    successes: int = 0
    errors: int = 0
    avg_response_time: float = 0.0
    uptime: float = 99.9

    def record_request(self) -> bool:
        self.requests += 1
        return True

    def record_success(self, response_time: float) -> bool:
        if response_time < 0:
            return False
        self.successes += 1
        self.avg_response_time = ((self.avg_response_time * (self.successes - 1) + response_time) / self.successes)
        return True

    def record_error(self, error_msg: str) -> bool:
        self.errors += 1
        return True

    def get_success_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.successes / self.requests

    def get_health_score(self) -> float:
        success = self.get_success_rate()
        uptime = self.uptime / 100.0
        return (success * 0.6) + (uptime * 0.4)


@dataclass
class DeployedAgent:
    deployment_id: str
    agent_id: str
    target: DeploymentTarget
    version: str = "1.0"
    previous_version: Optional[str] = None

    def update_deployment(self, new_version: str) -> bool:
        self.previous_version = self.version
        self.version = new_version
        return True

    def rollback(self) -> bool:
        if not self.previous_version:
            return False
        self.version = self.previous_version
        self.previous_version = None
        return True


class AgentDeploymentSystem:
    def __init__(self):
        self.configs: Dict = {}
        self.deployments: Dict = {}
        self.metrics: Dict = {}
        self.active_deployments: int = 0

    def create_deployment_config(self, config: DeploymentConfig) -> bool:
        if config.config_id in self.configs:
            return False
        self.configs[config.config_id] = config
        return True

    def deploy_agent(self, config_id: str, agent_id: str) -> Optional[str]:
        if config_id not in self.configs or not self.configs[config_id].enabled:
            return None
        deployment_id = f"deploy_{len(self.deployments)}"
        self.deployments[deployment_id] = DeployedAgent(deployment_id, agent_id, self.configs[config_id].target)
        self.metrics[deployment_id] = DeploymentMetrics(deployment_id)
        self.active_deployments += 1
        return deployment_id

    def query_deployment(self, deployment_id: str, query_time: float = 50.0) -> bool:
        if deployment_id not in self.metrics:
            return False
        self.metrics[deployment_id].record_request()
        if query_time > 0:
            self.metrics[deployment_id].record_success(query_time)
            return True
        return False

    def get_deployment_health(self, deployment_id: str) -> Dict:
        if deployment_id not in self.metrics:
            return {}
        m = self.metrics[deployment_id]
        return {
            "requests": m.requests,
            "success_rate": m.get_success_rate(),
            "health_score": m.get_health_score(),
            "avg_response_time": m.avg_response_time
        }

    def update_agent_version(self, deployment_id: str, new_version: str) -> bool:
        if deployment_id not in self.deployments:
            return False
        return self.deployments[deployment_id].update_deployment(new_version)

    def get_system_status(self) -> Dict:
        total_requests = sum(m.requests for m in self.metrics.values())
        total_successes = sum(m.successes for m in self.metrics.values())
        avg_health = sum(m.get_health_score() for m in self.metrics.values()) / max(1, len(self.metrics))
        return {
            "active_deployments": self.active_deployments,
            "total_requests": total_requests,
            "success_rate": total_successes / max(1, total_requests),
            "avg_health": avg_health
        }


# Tests

def test_config_creation():
    config = DeploymentConfig("cfg1", "a1", DeploymentTarget.API, ExecutionEnvironment.CLOUD)
    assert config.target == DeploymentTarget.API

def test_enable_deployment():
    config = DeploymentConfig("cfg1", "a1", DeploymentTarget.ROBOTICS, ExecutionEnvironment.EMBEDDED)
    assert config.enable_deployment() is True
    assert config.enabled is True

def test_metrics_creation():
    metrics = DeploymentMetrics("m1")
    assert metrics.requests == 0

def test_record_request():
    metrics = DeploymentMetrics("m1")
    assert metrics.record_request() is True
    assert metrics.requests == 1

def test_record_success():
    metrics = DeploymentMetrics("m1")
    assert metrics.record_success(45.0) is True
    assert metrics.successes == 1

def test_success_rate():
    metrics = DeploymentMetrics("m1")
    metrics.record_request()
    metrics.record_success(50.0)
    metrics.record_request()
    metrics.record_error("Failed")
    assert metrics.get_success_rate() == 0.5

def test_deployed_agent():
    agent = DeployedAgent("d1", "a1", DeploymentTarget.GAME)
    assert agent.version == "1.0"

def test_update_version():
    agent = DeployedAgent("d1", "a1", DeploymentTarget.API)
    assert agent.update_deployment("2.0") is True
    assert agent.version == "2.0"

def test_rollback():
    agent = DeployedAgent("d1", "a1", DeploymentTarget.DATABASE)
    agent.update_deployment("2.0")
    assert agent.rollback() is True
    assert agent.version == "1.0"

def test_system_creation():
    system = AgentDeploymentSystem()
    assert system.active_deployments == 0

def test_deploy():
    system = AgentDeploymentSystem()
    config = DeploymentConfig("cfg1", "a1", DeploymentTarget.DISCORD, ExecutionEnvironment.CLOUD)
    config.enable_deployment()
    system.create_deployment_config(config)
    deployment_id = system.deploy_agent("cfg1", "a1")
    assert deployment_id is not None
    assert system.active_deployments == 1

def test_query():
    system = AgentDeploymentSystem()
    config = DeploymentConfig("cfg1", "a1", DeploymentTarget.API, ExecutionEnvironment.CLOUD)
    config.enable_deployment()
    system.create_deployment_config(config)
    deployment_id = system.deploy_agent("cfg1", "a1")
    assert system.query_deployment(deployment_id, 35.0) is True

def test_health():
    system = AgentDeploymentSystem()
    config = DeploymentConfig("cfg1", "a1", DeploymentTarget.ROBOTICS, ExecutionEnvironment.EMBEDDED)
    config.enable_deployment()
    system.create_deployment_config(config)
    deployment_id = system.deploy_agent("cfg1", "a1")
    system.query_deployment(deployment_id, 55.0)
    health = system.get_deployment_health(deployment_id)
    assert "health_score" in health

def test_complete_workflow():
    system = AgentDeploymentSystem()
    configs = [
        DeploymentConfig("cfg_api", "a1", DeploymentTarget.API, ExecutionEnvironment.CLOUD),
        DeploymentConfig("cfg_bot", "a2", DeploymentTarget.DISCORD, ExecutionEnvironment.CLOUD),
        DeploymentConfig("cfg_robot", "a3", DeploymentTarget.ROBOTICS, ExecutionEnvironment.EMBEDDED),
    ]
    for cfg in configs:
        cfg.enable_deployment()
        system.create_deployment_config(cfg)
    api_deployment = system.deploy_agent("cfg_api", "a1")
    bot_deployment = system.deploy_agent("cfg_bot", "a2")
    robot_deployment = system.deploy_agent("cfg_robot", "a3")
    assert system.active_deployments == 3
    system.query_deployment(api_deployment, 42.0)
    system.query_deployment(api_deployment, 48.0)
    system.query_deployment(bot_deployment, 95.0)
    system.query_deployment(robot_deployment, 150.0)
    status = system.get_system_status()
    assert status["active_deployments"] == 3
    assert status["total_requests"] == 4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
