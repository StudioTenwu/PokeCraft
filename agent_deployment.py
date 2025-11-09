"""
Agent Deployment & Lifecycle Management for AICraft (Round 7).
Manages agent deployment to different environments and lifecycle state transitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
from agent_core import Agent, AgentState, Task


class DeploymentEnvironment(Enum):
    """Different deployment contexts for agents."""
    MICROWORLD = "microworld"
    HOMEWORK = "homework"
    MULTI_AGENT = "multi_agent"
    EMBODIED = "embodied"
    CUSTOM = "custom"


@dataclass
class DeploymentConfig:
    """Configuration for deploying an agent to an environment."""
    environment: DeploymentEnvironment
    constraints: Dict[str, Any] = field(default_factory=dict)
    isolation_level: str = "sandboxed"  # sandboxed, isolated, full
    resource_limits: Dict[str, float] = field(default_factory=lambda: {
        "max_tokens": 10000,
        "max_memory": 100,  # MB
        "timeout": 300  # seconds
    })
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize deployment config."""
        return {
            "environment": self.environment.value,
            "constraints": self.constraints,
            "isolation_level": self.isolation_level,
            "resource_limits": self.resource_limits,
            "created_at": self.created_at.isoformat()
        }


class AgentDeployment:
    """Manages agent deployment lifecycle and world integration."""

    def __init__(self, agent: Agent, config: DeploymentConfig):
        self.agent = agent
        self.config = config
        self.deployment_id = f"dep_{agent.agent_id}_{datetime.now().timestamp()}"
        self.status = "ready"  # ready, active, paused, completed
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.execution_log: List[Dict[str, Any]] = []
        self.resource_usage = {
            "tokens_used": 0,
            "memory_used": 0,
            "execution_time": 0.0
        }

    def launch(self) -> bool:
        """Launch the agent in the deployment environment."""
        # Can only deploy CAPABLE or EVOLVED agents
        if self.agent.state not in [AgentState.CAPABLE, AgentState.EVOLVED]:
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

    def update_resource_usage(self, tokens: float = 0, memory: float = 0, time: float = 0):
        """Update resource usage counters."""
        self.resource_usage["tokens_used"] += tokens
        self.resource_usage["memory_used"] += memory
        self.resource_usage["execution_time"] += time

    def log_execution(self, task_id: str, result: dict):
        """Log a task execution during deployment."""
        self.execution_log.append({
            "timestamp": datetime.now(),
            "task_id": task_id,
            "result": result
        })

    def export_snapshot(self) -> Dict[str, Any]:
        """Export agent state at deployment time for external use."""
        return {
            "agent_id": self.agent.agent_id,
            "deployment_id": self.deployment_id,
            "name": self.agent.name,
            "personality": self.agent.personality.to_dict() if self.agent.personality else None,
            "memory": self.agent.memory.to_dict() if self.agent.memory else None,
            "toolkit": self.agent.toolkit.to_dict() if self.agent.toolkit else None,
            "environment": self.config.environment.value,
            "snapshot_time": datetime.now().isoformat(),
            "resource_usage": self.resource_usage
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize deployment state."""
        return {
            "deployment_id": self.deployment_id,
            "agent_id": self.agent.agent_id,
            "status": self.status,
            "environment": self.config.environment.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "execution_log_size": len(self.execution_log),
            "resource_usage": self.resource_usage
        }


class LifecycleManager:
    """Manages agent lifecycle state transitions and maturation."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.deployments: Dict[str, AgentDeployment] = {}
        self.state_transitions: Dict[AgentState, List[AgentState]] = {
            AgentState.CREATED: [AgentState.DEVELOPING],
            AgentState.DEVELOPING: [AgentState.CAPABLE],
            AgentState.CAPABLE: [AgentState.DEPLOYED, AgentState.RESTING],
            AgentState.DEPLOYED: [AgentState.RESTING, AgentState.EVOLVED],
            AgentState.RESTING: [AgentState.DEVELOPING, AgentState.DEPLOYED],
            AgentState.EVOLVED: [AgentState.DEPLOYED, AgentState.RESTING]
        }

    def register_agent(self, agent: Agent) -> bool:
        """Register an agent in the lifecycle system."""
        self.agents[agent.agent_id] = agent
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the lifecycle system."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def advance_agent_state(self, agent_id: str, target_state: AgentState) -> bool:
        """Advance agent to target lifecycle state if transition is valid."""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]

        # Check if transition is valid
        if target_state not in self.state_transitions.get(agent.state, []):
            return False

        agent.state = target_state
        return True

    def can_deploy(self, agent_id: str) -> bool:
        """Check if agent is ready for deployment."""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]

        # Must be CAPABLE or EVOLVED
        if agent.state not in [AgentState.CAPABLE, AgentState.EVOLVED]:
            return False

        # Must have minimal toolkit
        if not agent.toolkit or len(agent.toolkit.available_tools) == 0:
            return False

        return True

    def deploy_agent(self, agent_id: str, config: DeploymentConfig) -> Optional[AgentDeployment]:
        """Deploy an agent to an environment if ready."""
        if not self.can_deploy(agent_id):
            return None

        agent = self.agents[agent_id]
        deployment = AgentDeployment(agent, config)

        if deployment.launch():
            self.deployments[deployment.deployment_id] = deployment
            return deployment

        return None

    def get_deployment(self, deployment_id: str) -> Optional[AgentDeployment]:
        """Retrieve a deployment by ID."""
        return self.deployments.get(deployment_id)

    def get_agent_deployments(self, agent_id: str) -> List[AgentDeployment]:
        """Get all deployments for an agent."""
        return [d for d in self.deployments.values() if d.agent.agent_id == agent_id]

    def get_maturity_score(self, agent_id: str) -> float:
        """Calculate maturity score (0.0-1.0) based on capabilities."""
        if agent_id not in self.agents:
            return 0.0

        agent = self.agents[agent_id]
        score = 0.0

        # State progression (0.25)
        state_progress = {
            AgentState.CREATED: 0.0,
            AgentState.DEVELOPING: 0.25,
            AgentState.CAPABLE: 0.5,
            AgentState.DEPLOYED: 0.75,
            AgentState.EVOLVED: 1.0,
            AgentState.RESTING: 0.5
        }
        score += state_progress.get(agent.state, 0.0) * 0.25

        # Toolkit breadth (0.25)
        if agent.toolkit:
            tool_count = len(agent.toolkit.available_tools)
            score += min(tool_count / 5.0, 1.0) * 0.25

        # Memory capacity (0.25)
        if agent.memory:
            memory_items = len(agent.memory.get_all_memories())
            score += min(memory_items / 50.0, 1.0) * 0.25

        # Personality development (0.25)
        if agent.personality:
            personality_score = len(agent.personality.traits) / 10.0
            score += min(personality_score, 1.0) * 0.25

        return min(score, 1.0)

    def get_readiness_report(self, agent_id: str) -> Dict[str, Any]:
        """Generate a detailed readiness report for an agent."""
        if agent_id not in self.agents:
            return {}

        agent = self.agents[agent_id]

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "current_state": agent.state.value,
            "maturity_score": self.get_maturity_score(agent_id),
            "can_deploy": self.can_deploy(agent_id),
            "toolkit_size": len(agent.toolkit.available_tools) if agent.toolkit else 0,
            "memory_items": len(agent.memory.get_all_memories()) if agent.memory else 0,
            "personality_traits": len(agent.personality.traits) if agent.personality else 0,
            "total_deployments": len(self.get_agent_deployments(agent_id)),
            "deployment_history": [
                d.status for d in self.get_agent_deployments(agent_id)
            ]
        }
