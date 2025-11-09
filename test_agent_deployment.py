"""
Test suite for Agent Deployment & Lifecycle Management (Round 7).
Tests agent lifecycle transitions, deployment mechanics, and world integration.
"""

import pytest
from datetime import datetime, timedelta
from enum import Enum
from agent_core import Agent, AgentState, Task
from agent_personality import Personality
from agent_memory import Memory
from agent_toolkit import Toolkit


class DeploymentEnvironment(Enum):
    """Different deployment contexts for agents."""
    MICROWORLD = "microworld"
    HOMEWORK = "homework"
    MULTI_AGENT = "multi_agent"
    EMBODIED = "embodied"
    CUSTOM = "custom"


class DeploymentConfig:
    """Configuration for deploying an agent to an environment."""

    def __init__(self, environment: DeploymentEnvironment, constraints: dict = None):
        self.environment = environment
        self.constraints = constraints or {}
        self.isolation_level = "sandboxed"  # sandboxed, isolated, full
        self.resource_limits = {
            "max_tokens": 10000,
            "max_memory": 100,  # MB
            "timeout": 300  # seconds
        }
        self.created_at = datetime.now()


class AgentDeployment:
    """Manages agent deployment lifecycle and world integration."""

    def __init__(self, agent: Agent, config: DeploymentConfig):
        self.agent = agent
        self.config = config
        self.deployment_id = f"dep_{agent.agent_id}_{datetime.now().timestamp()}"
        self.status = "ready"  # ready, active, paused, completed
        self.started_at = None
        self.ended_at = None
        self.execution_log = []
        self.resource_usage = {
            "tokens_used": 0,
            "memory_used": 0,
            "execution_time": 0
        }

    def launch(self) -> bool:
        """Launch the agent in the deployment environment."""
        if self.agent.state != AgentState.CAPABLE and self.agent.state != AgentState.EVOLVED:
            return False

        self.status = "active"
        self.started_at = datetime.now()
        self.agent.state = AgentState.DEPLOYED
        return True

    def pause(self) -> bool:
        """Pause deployment without terminating."""
        if self.status != "active":
            return False

        self.status = "paused"
        return True

    def resume(self) -> bool:
        """Resume paused deployment."""
        if self.status != "paused":
            return False

        self.status = "active"
        return True

    def terminate(self) -> bool:
        """End deployment."""
        if self.status not in ["active", "paused"]:
            return False

        self.status = "completed"
        self.ended_at = datetime.now()
        self.agent.state = AgentState.RESTING
        return True

    def check_resource_limits(self) -> bool:
        """Check if resource limits are exceeded."""
        for resource, limit in self.config.resource_limits.items():
            if self.resource_usage.get(resource, 0) >= limit:
                return False
        return True

    def log_execution(self, task_id: str, result: dict):
        """Log a task execution."""
        self.execution_log.append({
            "timestamp": datetime.now(),
            "task_id": task_id,
            "result": result
        })

    def export_snapshot(self) -> dict:
        """Export agent state at deployment time for external use."""
        return {
            "agent_id": self.agent.agent_id,
            "deployment_id": self.deployment_id,
            "personality": self.agent.personality.to_dict() if self.agent.personality else None,
            "memory": self.agent.memory.to_dict() if self.agent.memory else None,
            "toolkit": self.agent.toolkit.to_dict() if self.agent.toolkit else None,
            "environment": self.config.environment.value,
            "snapshot_time": datetime.now().isoformat()
        }


class LifecycleManagerTest:
    """Test version - use the real one from agent_deployment module."""
    pass


# ===== TESTS =====

def test_deployment_config_creation():
    """Test creating a deployment configuration."""
    config = DeploymentConfig(DeploymentEnvironment.HOMEWORK)
    assert config.environment == DeploymentEnvironment.HOMEWORK
    assert config.isolation_level == "sandboxed"
    assert config.resource_limits["timeout"] == 300


def test_agent_deployment_launch():
    """Test launching an agent deployment."""
    agent = Agent("TestAgent")
    agent.state = AgentState.CAPABLE

    config = DeploymentConfig(DeploymentEnvironment.MICROWORLD)
    deployment = AgentDeployment(agent, config)

    assert deployment.status == "ready"
    assert deployment.launch()
    assert deployment.status == "active"
    assert deployment.started_at is not None


def test_agent_deployment_requires_capability():
    """Test that only capable agents can be deployed."""
    agent = Agent("NewbieAgent")
    agent.state = AgentState.DEVELOPING  # Not ready yet

    config = DeploymentConfig(DeploymentEnvironment.HOMEWORK)
    deployment = AgentDeployment(agent, config)

    # Should fail to launch
    assert not deployment.launch()
    assert deployment.status == "ready"


def test_deployment_lifecycle():
    """Test full deployment lifecycle: launch -> pause -> resume -> terminate."""
    agent = Agent("LifecycleAgent")
    agent.state = AgentState.CAPABLE

    config = DeploymentConfig(DeploymentEnvironment.MULTI_AGENT)
    deployment = AgentDeployment(agent, config)

    # Launch
    assert deployment.launch()
    assert deployment.status == "active"

    # Pause
    assert deployment.pause()
    assert deployment.status == "paused"

    # Resume
    assert deployment.resume()
    assert deployment.status == "active"

    # Terminate
    assert deployment.terminate()
    assert deployment.status == "completed"
    assert deployment.ended_at is not None


def test_deployment_resource_tracking():
    """Test resource usage tracking during deployment."""
    agent = Agent("ResourceAgent")
    agent.state = AgentState.CAPABLE

    config = DeploymentConfig(DeploymentEnvironment.HOMEWORK)
    # Keys in resource_limits must match keys in resource_usage
    config.resource_limits["tokens_used"] = 10000
    config.resource_limits["memory_used"] = 100  # 100 MB

    deployment = AgentDeployment(agent, config)
    deployment.launch()

    # Update resource usage within limits
    deployment.resource_usage["tokens_used"] = 5000
    deployment.resource_usage["memory_used"] = 50

    # Should still be within limits
    assert deployment.check_resource_limits()

    # Exceed memory limit
    deployment.resource_usage["memory_used"] = 101
    assert not deployment.check_resource_limits()


def test_deployment_execution_logging():
    """Test logging executions during deployment."""
    agent = Agent("LoggingAgent")
    agent.state = AgentState.CAPABLE

    config = DeploymentConfig(DeploymentEnvironment.HOMEWORK)
    deployment = AgentDeployment(agent, config)
    deployment.launch()

    # Log some executions
    deployment.log_execution("task_1", {"output": "result_1"})
    deployment.log_execution("task_2", {"output": "result_2"})

    assert len(deployment.execution_log) == 2
    assert deployment.execution_log[0]["task_id"] == "task_1"


def test_deployment_snapshot_export():
    """Test exporting agent snapshot for external deployment."""
    from agent_personality import PersonalityTrait

    agent = Agent("ExportAgent")
    agent.state = AgentState.CAPABLE
    agent.personality = Personality("ExportAgent")
    agent.personality.add_trait(PersonalityTrait(
        name="helpful",
        spectrum=("unhelpful", "helpful"),
        value=0.8
    ))

    config = DeploymentConfig(DeploymentEnvironment.EMBODIED)
    deployment = AgentDeployment(agent, config)
    deployment.launch()

    snapshot = deployment.export_snapshot()
    assert snapshot["agent_id"] == agent.agent_id
    assert snapshot["deployment_id"] == deployment.deployment_id
    assert snapshot["environment"] == "embodied"
    assert snapshot["personality"] is not None


def test_lifecycle_manager_agent_registration():
    """Test registering agents with lifecycle manager."""
    from agent_deployment import LifecycleManager

    manager = LifecycleManager()
    agent = Agent("ManagedAgent")

    assert manager.register_agent(agent)
    assert agent.agent_id in manager.agents


def test_lifecycle_state_transitions():
    """Test valid state transitions."""
    from agent_deployment import LifecycleManager

    manager = LifecycleManager()
    agent = Agent("TransitionAgent")
    agent.state = AgentState.CREATED
    manager.register_agent(agent)

    # CREATED -> DEVELOPING
    assert manager.advance_agent_state(agent.agent_id, AgentState.DEVELOPING)
    assert agent.state == AgentState.DEVELOPING

    # DEVELOPING -> CAPABLE
    assert manager.advance_agent_state(agent.agent_id, AgentState.CAPABLE)
    assert agent.state == AgentState.CAPABLE

    # Invalid transition (CAPABLE -> CREATING)
    assert not manager.advance_agent_state(agent.agent_id, AgentState.CREATED)


def test_lifecycle_deployment_readiness():
    """Test checking if agent is ready for deployment."""
    from agent_toolkit import ToolDefinition, ToolCategory
    from agent_deployment import LifecycleManager

    manager = LifecycleManager()
    agent = Agent("DeployReadyAgent")
    agent.state = AgentState.DEVELOPING
    manager.register_agent(agent)

    # Not ready (not CAPABLE/EVOLVED)
    assert not manager.can_deploy(agent.agent_id)

    # Advance to CAPABLE
    manager.advance_agent_state(agent.agent_id, AgentState.CAPABLE)

    # Still not ready (no tools)
    assert not manager.can_deploy(agent.agent_id)

    # Add toolkit
    agent.toolkit = Toolkit(agent.agent_id)
    tool_def = ToolDefinition(
        tool_id="test_tool",
        name="Test Tool",
        description="A test tool",
        category=ToolCategory.COMMUNICATION,
        input_schema={},
        output_schema={}
    )
    agent.toolkit.register_tool(tool_def)

    # Now ready
    assert manager.can_deploy(agent.agent_id)


def test_lifecycle_deploy_agent():
    """Test deploying agent through lifecycle manager."""
    from agent_toolkit import ToolDefinition, ToolCategory
    from agent_deployment import LifecycleManager

    manager = LifecycleManager()
    agent = Agent("LifecycleDeployAgent")
    agent.state = AgentState.CAPABLE
    agent.toolkit = Toolkit(agent.agent_id)

    tool_def = ToolDefinition(
        tool_id="test",
        name="Test Tool",
        description="test",
        category=ToolCategory.COMMUNICATION,
        input_schema={},
        output_schema={}
    )
    agent.toolkit.register_tool(tool_def)

    manager.register_agent(agent)

    config = DeploymentConfig(DeploymentEnvironment.HOMEWORK)
    deployment = manager.deploy_agent(agent.agent_id, config)

    assert deployment is not None
    assert deployment.status == "active"
    assert agent.state == AgentState.DEPLOYED


def test_maturity_score_calculation():
    """Test calculating agent maturity score."""
    from agent_toolkit import ToolDefinition, ToolCategory
    from agent_personality import PersonalityTrait
    from agent_deployment import LifecycleManager

    manager = LifecycleManager()

    # New agent
    agent = Agent("MaturityAgent")
    agent.state = AgentState.CREATED
    manager.register_agent(agent)

    score = manager.get_maturity_score(agent.agent_id)
    assert 0.0 <= score <= 1.0
    assert score == 0.0  # Just created

    # Developing agent
    manager.advance_agent_state(agent.agent_id, AgentState.DEVELOPING)
    agent.toolkit = Toolkit(agent.agent_id)
    for i in range(3):
        tool_def = ToolDefinition(
            tool_id=f"tool_{i}",
            name=f"Tool {i}",
            description=f"tool {i}",
            category=ToolCategory.COMMUNICATION,
            input_schema={},
            output_schema={}
        )
        agent.toolkit.register_tool(tool_def)

    score = manager.get_maturity_score(agent.agent_id)
    assert score > 0.0

    # Evolved agent with full capabilities
    agent.state = AgentState.EVOLVED
    agent.personality = Personality("MaturityAgent")
    for i in range(8):
        agent.personality.add_trait(PersonalityTrait(
            name=f"trait_{i}",
            spectrum=("low", "high"),
            value=0.5 + i * 0.05
        ))

    score = manager.get_maturity_score(agent.agent_id)
    assert score > 0.5  # Should be fairly mature


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
