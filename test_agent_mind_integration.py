"""
Round 55: Agent Mind Integration Layer
Integrate Rounds 51-54 cognitive systems (reasoning, perception, communication, collaboration)
into the core Agent framework. The AgentMind unifies these capabilities.

Integration connects:
- Perception (Round 52) → Reasoning (Round 51) → Tools → Communication (Round 53)
- Collaboration (Round 54) enables multi-agent deployment
- Memory (Rounds 10-15) stores reasoning chains, percepts, communications
- Goals align cognitive systems toward agent's purpose
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


class CognitiveMode(Enum):
    """Mode of agent cognition"""
    PERCEPTION = "perception"  # Processing inputs
    REASONING = "reasoning"     # Thinking about problem
    PLANNING = "planning"       # Planning action sequence
    EXECUTION = "execution"     # Executing tools
    COMMUNICATION = "communication"  # Messaging other agents
    REFLECTION = "reflection"   # Learning from outcomes


class MindState(Enum):
    """State of the agent mind"""
    IDLE = "idle"
    ACTIVE = "active"
    THINKING = "thinking"
    WAITING = "waiting"
    COMPLETE = "complete"


@dataclass
class CognitiveStep:
    """Single step in agent's cognitive process"""
    step_id: str
    mode: CognitiveMode
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5  # 0.0-1.0
    duration: float = 0.0
    timestamp: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "mode": self.mode.value,
            "confidence": self.confidence,
            "duration": self.duration
        }


@dataclass
class CognitiveTrace:
    """Complete trace of agent's thinking process"""
    trace_id: str
    goal: str = ""
    steps: List[CognitiveStep] = field(default_factory=list)
    final_action: str = ""
    success: bool = False
    total_confidence: float = 0.0

    def add_step(self, step: CognitiveStep) -> bool:
        self.steps.append(step)
        self._update_confidence()
        return True

    def _update_confidence(self):
        if not self.steps:
            self.total_confidence = 0.0
        else:
            self.total_confidence = sum(s.confidence for s in self.steps) / len(self.steps)

    def to_dict(self) -> Dict:
        return {
            "trace_id": self.trace_id,
            "goal": self.goal,
            "steps": len(self.steps),
            "success": self.success,
            "confidence": self.total_confidence
        }


class PerceptionInterface:
    """Abstraction of perception system for agent mind"""

    def perceive(self, stimuli: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensory input and return percepts"""
        # Simulates Rounds 52: Multi-Modal Perception
        percepts = {
            "text": stimuli.get("text", ""),
            "visual_features": [],
            "attention_focus": 0.5,
            "emotional_response": 0.0
        }
        return percepts


class ReasoningInterface:
    """Abstraction of reasoning system for agent mind"""

    def reason(self, percepts: Dict[str, Any], goal: str) -> Tuple[str, float]:
        """Reason about percepts and goal, return action and confidence"""
        # Simulates Round 51: AI Agent Reasoning Engine
        # Returns action to take and confidence in reasoning
        action = f"action_for_{goal}"
        confidence = 0.7
        return action, confidence


class CommunicationInterface:
    """Abstraction of communication system for agent mind"""

    def compose_message(self, content: str, recipient: str) -> str:
        """Compose message to another agent"""
        # Simulates Round 53: Agent Communication Protocol
        return f"Message to {recipient}: {content}"

    def handle_message(self, message: str, sender: str) -> str:
        """Process incoming message"""
        return f"Received from {sender}: {message}"


class CollaborationInterface:
    """Abstraction of collaboration system for agent mind"""

    def join_collaboration(self, session_id: str, shared_goal: str) -> bool:
        """Join collaborative session"""
        # Simulates Round 54: Real-Time Collaboration System
        return True

    def sync_state(self, session_id: str, state: Dict) -> bool:
        """Synchronize state with collaborators"""
        return True


class MemoryInterface:
    """Abstraction of memory system for agent mind"""

    def store_experience(self, experience: Dict) -> bool:
        """Store cognitive experience in memory"""
        return True

    def retrieve_similar_experiences(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve similar past experiences"""
        return []


class AgentMind:
    """
    Unified agent mind integrating all cognitive systems.
    Routes: Perception → Reasoning → Tools → Communication
    Stores traces in Memory. Enables Collaboration.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = MindState.IDLE
        self.perception = PerceptionInterface()
        self.reasoning = ReasoningInterface()
        self.communication = CommunicationInterface()
        self.collaboration = CollaborationInterface()
        self.memory = MemoryInterface()
        self.current_goal: str = ""
        self.cognitive_traces: List[CognitiveTrace] = []
        self.active_collaborations: List[str] = []

    def set_goal(self, goal: str) -> bool:
        """Set agent's current goal"""
        self.current_goal = goal
        self.state = MindState.ACTIVE
        return True

    def perceive(self, stimuli: Dict[str, Any]) -> CognitiveStep:
        """Execute perception step"""
        step = CognitiveStep(
            step_id=f"percept_{len(self.cognitive_traces)}",
            mode=CognitiveMode.PERCEPTION,
            input_data=stimuli
        )
        percepts = self.perception.perceive(stimuli)
        step.output_data = percepts
        step.confidence = 0.9
        return step

    def reason(self, percepts: Dict[str, Any]) -> CognitiveStep:
        """Execute reasoning step"""
        step = CognitiveStep(
            step_id=f"reason_{len(self.cognitive_traces)}",
            mode=CognitiveMode.REASONING,
            input_data=percepts
        )
        action, confidence = self.reasoning.reason(percepts, self.current_goal)
        step.output_data = {"action": action}
        step.confidence = confidence
        return step

    def plan(self, reasoning_output: Dict[str, Any]) -> CognitiveStep:
        """Execute planning step"""
        step = CognitiveStep(
            step_id=f"plan_{len(self.cognitive_traces)}",
            mode=CognitiveMode.PLANNING,
            input_data=reasoning_output
        )
        # Plan sequence of actions
        step.output_data = {"action_sequence": [reasoning_output.get("action")]}
        step.confidence = 0.8
        return step

    def execute(self, plan: Dict[str, Any]) -> CognitiveStep:
        """Execute tool/action step"""
        step = CognitiveStep(
            step_id=f"exec_{len(self.cognitive_traces)}",
            mode=CognitiveMode.EXECUTION,
            input_data=plan
        )
        # Execute actions
        step.output_data = {"result": "execution_complete"}
        step.confidence = 0.8
        return step

    def communicate(self, message_content: str, recipient: str) -> CognitiveStep:
        """Execute communication step"""
        step = CognitiveStep(
            step_id=f"comm_{len(self.cognitive_traces)}",
            mode=CognitiveMode.COMMUNICATION,
            input_data={"content": message_content, "recipient": recipient}
        )
        message = self.communication.compose_message(message_content, recipient)
        step.output_data = {"message": message}
        step.confidence = 0.9
        return step

    def reflect(self, outcome: Dict[str, Any]) -> CognitiveStep:
        """Execute reflection step - learn from outcomes"""
        step = CognitiveStep(
            step_id=f"reflect_{len(self.cognitive_traces)}",
            mode=CognitiveMode.REFLECTION,
            input_data=outcome
        )
        # Update confidence based on outcome
        success = outcome.get("success", False)
        step.output_data = {"lesson": "outcome_processed"}
        step.confidence = 0.9 if success else 0.5
        return step

    def run_cognitive_cycle(self, stimuli: Dict[str, Any]) -> CognitiveTrace:
        """Execute full cognitive cycle: perceive → reason → plan → execute"""
        trace = CognitiveTrace(
            trace_id=f"trace_{len(self.cognitive_traces)}",
            goal=self.current_goal
        )

        # Perception
        percept_step = self.perceive(stimuli)
        trace.add_step(percept_step)

        # Reasoning
        reason_step = self.reason(percept_step.output_data)
        trace.add_step(reason_step)

        # Planning
        plan_step = self.plan(reason_step.output_data)
        trace.add_step(plan_step)

        # Execution
        exec_step = self.execute(plan_step.output_data)
        trace.add_step(exec_step)

        # Store in cognitive traces
        self.cognitive_traces.append(trace)

        # Store in memory
        self.memory.store_experience({
            "trace_id": trace.trace_id,
            "goal": trace.goal,
            "outcome": exec_step.output_data
        })

        return trace

    def collaborate(self, session_id: str, shared_goal: str, shared_state: Dict) -> bool:
        """Join and participate in collaboration"""
        if not self.collaboration.join_collaboration(session_id, shared_goal):
            return False

        self.active_collaborations.append(session_id)

        # Synchronize state with collaborators
        agent_state = {
            "agent_id": self.agent_id,
            "goal": self.current_goal,
            "state": shared_state
        }
        return self.collaboration.sync_state(session_id, agent_state)

    def get_mind_state(self) -> Dict:
        """Get current state of agent mind"""
        return {
            "agent_id": self.agent_id,
            "goal": self.current_goal,
            "state": self.state.value,
            "traces": len(self.cognitive_traces),
            "collaborations": len(self.active_collaborations),
            "avg_confidence": self._calculate_avg_confidence()
        }

    def _calculate_avg_confidence(self) -> float:
        if not self.cognitive_traces:
            return 0.0
        return sum(t.total_confidence for t in self.cognitive_traces) / len(self.cognitive_traces)

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "goal": self.current_goal,
            "traces": len(self.cognitive_traces),
            "collaborations": len(self.active_collaborations),
            "avg_confidence": self._calculate_avg_confidence()
        }


class MindFactory:
    """Factory for creating and configuring agent minds"""

    def __init__(self):
        self.minds: Dict[str, AgentMind] = {}

    def create_mind(self, agent_id: str) -> AgentMind:
        """Create new agent mind"""
        mind = AgentMind(agent_id)
        self.minds[agent_id] = mind
        return mind

    def get_mind(self, agent_id: str) -> Optional[AgentMind]:
        """Retrieve existing mind"""
        return self.minds.get(agent_id)

    def configure_mind(self, agent_id: str, goal: str) -> bool:
        """Configure mind with goal"""
        mind = self.get_mind(agent_id)
        if mind:
            return mind.set_goal(goal)
        return False

    def to_dict(self) -> Dict:
        return {
            "total_minds": len(self.minds),
            "minds": {mid: m.to_dict() for mid, m in self.minds.items()}
        }


# ===== Tests =====

def test_cognitive_step_creation():
    step = CognitiveStep("step1", CognitiveMode.PERCEPTION)
    assert step.step_id == "step1"
    assert step.mode == CognitiveMode.PERCEPTION


def test_cognitive_trace_creation():
    trace = CognitiveTrace("trace1", "test_goal")
    assert trace.trace_id == "trace1"
    assert trace.goal == "test_goal"
    assert len(trace.steps) == 0


def test_cognitive_trace_add_step():
    trace = CognitiveTrace("trace1")
    step = CognitiveStep("step1", CognitiveMode.PERCEPTION, confidence=0.8)
    assert trace.add_step(step) is True
    assert len(trace.steps) == 1


def test_cognitive_trace_confidence_update():
    trace = CognitiveTrace("trace1")
    step1 = CognitiveStep("s1", CognitiveMode.PERCEPTION, confidence=0.8)
    step2 = CognitiveStep("s2", CognitiveMode.REASONING, confidence=0.6)
    trace.add_step(step1)
    trace.add_step(step2)
    assert trace.total_confidence == 0.7  # (0.8 + 0.6) / 2


def test_perception_interface():
    perc = PerceptionInterface()
    stimuli = {"text": "hello"}
    percepts = perc.perceive(stimuli)
    assert "text" in percepts
    assert percepts["text"] == "hello"


def test_reasoning_interface():
    reason = ReasoningInterface()
    percepts = {"text": "problem statement"}
    action, confidence = reason.reason(percepts, "solve_problem")
    assert action is not None
    assert 0.0 <= confidence <= 1.0


def test_communication_interface():
    comm = CommunicationInterface()
    message = comm.compose_message("hello", "agent2")
    assert "agent2" in message
    assert "hello" in message


def test_collaboration_interface():
    collab = CollaborationInterface()
    assert collab.join_collaboration("sess1", "goal1") is True


def test_agent_mind_creation():
    mind = AgentMind("agent1")
    assert mind.agent_id == "agent1"
    assert mind.state == MindState.IDLE


def test_agent_mind_set_goal():
    mind = AgentMind("agent1")
    assert mind.set_goal("test_goal") is True
    assert mind.current_goal == "test_goal"
    assert mind.state == MindState.ACTIVE


def test_agent_mind_perceive():
    mind = AgentMind("agent1")
    stimuli = {"text": "input"}
    step = mind.perceive(stimuli)
    assert step.mode == CognitiveMode.PERCEPTION
    assert step.confidence > 0.0


def test_agent_mind_reason():
    mind = AgentMind("agent1")
    percepts = {"text": "problem"}
    step = mind.reason(percepts)
    assert step.mode == CognitiveMode.REASONING
    assert "action" in step.output_data


def test_agent_mind_plan():
    mind = AgentMind("agent1")
    reasoning_output = {"action": "do_something"}
    step = mind.plan(reasoning_output)
    assert step.mode == CognitiveMode.PLANNING
    assert "action_sequence" in step.output_data


def test_agent_mind_execute():
    mind = AgentMind("agent1")
    plan = {"action_sequence": ["action1"]}
    step = mind.execute(plan)
    assert step.mode == CognitiveMode.EXECUTION
    assert "result" in step.output_data


def test_agent_mind_communicate():
    mind = AgentMind("agent1")
    step = mind.communicate("hello world", "agent2")
    assert step.mode == CognitiveMode.COMMUNICATION
    assert "message" in step.output_data


def test_agent_mind_reflect():
    mind = AgentMind("agent1")
    outcome = {"success": True}
    step = mind.reflect(outcome)
    assert step.mode == CognitiveMode.REFLECTION
    assert step.confidence > 0.5


def test_agent_mind_cognitive_cycle():
    mind = AgentMind("agent1")
    mind.set_goal("solve_problem")
    stimuli = {"text": "problem statement"}
    trace = mind.run_cognitive_cycle(stimuli)
    assert trace.goal == "solve_problem"
    assert len(trace.steps) == 4  # perceive, reason, plan, execute


def test_agent_mind_collaborate():
    mind = AgentMind("agent1")
    assert mind.collaborate("sess1", "shared_goal", {"state": "value"}) is True
    assert "sess1" in mind.active_collaborations


def test_agent_mind_state():
    mind = AgentMind("agent1")
    mind.set_goal("test_goal")
    state = mind.get_mind_state()
    assert state["agent_id"] == "agent1"
    assert state["goal"] == "test_goal"


def test_mind_factory_create():
    factory = MindFactory()
    mind = factory.create_mind("agent1")
    assert mind is not None
    assert factory.get_mind("agent1") == mind


def test_mind_factory_configure():
    factory = MindFactory()
    factory.create_mind("agent1")
    assert factory.configure_mind("agent1", "test_goal") is True


def test_complete_cognitive_workflow():
    """Full workflow: create mind, set goal, perceive, reason, plan, execute"""
    factory = MindFactory()
    mind = factory.create_mind("agent1")

    # Configure
    assert factory.configure_mind("agent1", "solve_puzzle") is True

    # Run cognitive cycle
    stimuli = {
        "text": "puzzle statement",
        "context": "math problem"
    }
    trace = mind.run_cognitive_cycle(stimuli)

    # Verify trace
    assert trace.goal == "solve_puzzle"
    assert len(trace.steps) == 4
    assert trace.total_confidence > 0.0

    # Verify stored in traces
    assert len(mind.cognitive_traces) == 1

    # Collaborate
    assert mind.collaborate("session1", "group_puzzle", {"difficulty": 0.5}) is True

    # Check final state
    state = mind.get_mind_state()
    assert state["traces"] == 1
    assert state["collaborations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
