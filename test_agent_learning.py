"""
Round 57: Agent Learning & Adaptation
Agents learn from experiences, update confidence, refine strategies, and evolve over time.
Enables long-term agent development and improvement through interaction with environment.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class LearningType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CORRECTED = "corrected"


@dataclass
class Experience:
    exp_id: str
    action: str
    outcome: LearningType
    confidence_before: float = 0.5
    confidence_after: float = 0.5
    lesson: str = ""

    def to_dict(self) -> Dict:
        return {
            "exp_id": self.exp_id,
            "action": self.action,
            "outcome": self.outcome.value,
            "confidence_delta": self.confidence_after - self.confidence_before
        }


@dataclass
class LearningRule:
    rule_id: str
    condition: str
    action: str
    success_rate: float = 0.5  # 0.0-1.0
    usage_count: int = 0
    effectiveness: float = 0.5  # 0.0-1.0

    def apply_success(self):
        self.usage_count += 1
        self.success_rate = (self.success_rate * 0.8) + (1.0 * 0.2)
        self.effectiveness = self.success_rate

    def apply_failure(self):
        self.usage_count += 1
        self.success_rate = (self.success_rate * 0.8) + (0.0 * 0.2)
        self.effectiveness = self.success_rate

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count
        }


@dataclass
class ConfidenceUpdate:
    reason: str
    delta: float = 0.0  # Can be negative
    timestamp: float = 0.0

    def to_dict(self) -> Dict:
        return {"reason": self.reason, "delta": self.delta}


class ConfidenceTracker:
    def __init__(self, initial: float = 0.5):
        self.current: float = max(0.0, min(1.0, initial))
        self.history: List[ConfidenceUpdate] = []
        self.total_updates: int = 0

    def update(self, delta: float, reason: str) -> bool:
        old = self.current
        self.current = max(0.0, min(1.0, self.current + delta))
        self.history.append(ConfidenceUpdate(reason, delta))
        self.total_updates += 1
        return True

    def boost_from_success(self) -> bool:
        return self.update(0.1, "success")

    def decrease_from_failure(self) -> bool:
        return self.update(-0.15, "failure")

    def to_dict(self) -> Dict:
        return {
            "current_confidence": self.current,
            "total_updates": self.total_updates,
            "history_length": len(self.history)
        }


class StrategyAdaptation:
    def __init__(self):
        self.strategies: Dict[str, float] = {}  # strategy -> effectiveness
        self.current_strategy: str = "default"

    def register_strategy(self, name: str, effectiveness: float = 0.5) -> bool:
        if name not in self.strategies:
            self.strategies[name] = max(0.0, min(1.0, effectiveness))
            return True
        return False

    def update_strategy_effectiveness(self, name: str, delta: float) -> bool:
        if name in self.strategies:
            self.strategies[name] = max(0.0, min(1.0, self.strategies[name] + delta))
            return True
        return False

    def select_best_strategy(self) -> Optional[str]:
        if not self.strategies:
            return None
        best = max(self.strategies, key=self.strategies.get)
        self.current_strategy = best
        return best

    def to_dict(self) -> Dict:
        return {
            "strategies": len(self.strategies),
            "current": self.current_strategy,
            "best_effectiveness": max(self.strategies.values()) if self.strategies else 0.0
        }


class AgentLearner:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.experiences: List[Experience] = []
        self.learning_rules: Dict[str, LearningRule] = {}
        self.confidence_tracker = ConfidenceTracker()
        self.strategy_adaptation = StrategyAdaptation()
        self.total_successes: int = 0
        self.total_failures: int = 0

    def record_experience(self, action: str, outcome: LearningType) -> Experience:
        exp = Experience(
            exp_id=f"exp_{len(self.experiences)}",
            action=action,
            outcome=outcome,
            confidence_before=self.confidence_tracker.current
        )

        if outcome == LearningType.SUCCESS:
            self.total_successes += 1
            self.confidence_tracker.boost_from_success()
            exp.confidence_after = self.confidence_tracker.current
        elif outcome == LearningType.FAILURE:
            self.total_failures += 1
            self.confidence_tracker.decrease_from_failure()
            exp.confidence_after = self.confidence_tracker.current
        else:
            exp.confidence_after = self.confidence_tracker.current

        self.experiences.append(exp)
        return exp

    def add_learning_rule(self, condition: str, action: str) -> LearningRule:
        rule_id = f"rule_{len(self.learning_rules)}"
        rule = LearningRule(rule_id, condition, action)
        self.learning_rules[rule_id] = rule
        return rule

    def reinforce_rule(self, rule_id: str, success: bool) -> bool:
        if rule_id in self.learning_rules:
            if success:
                self.learning_rules[rule_id].apply_success()
            else:
                self.learning_rules[rule_id].apply_failure()
            return True
        return False

    def get_success_rate(self) -> float:
        total = self.total_successes + self.total_failures
        if total == 0:
            return 0.0
        return self.total_successes / total

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "experiences": len(self.experiences),
            "learning_rules": len(self.learning_rules),
            "confidence": self.confidence_tracker.current,
            "success_rate": self.get_success_rate()
        }


# Tests
def test_experience_creation():
    e = Experience("e1", "test_action", LearningType.SUCCESS)
    assert e.exp_id == "e1"

def test_experience_outcome():
    e = Experience("e1", "test", LearningType.SUCCESS)
    assert e.outcome == LearningType.SUCCESS

def test_learning_rule_creation():
    r = LearningRule("r1", "condition", "action")
    assert r.rule_id == "r1"

def test_learning_rule_success():
    r = LearningRule("r1", "cond", "act")
    r.apply_success()
    assert r.usage_count == 1
    assert r.success_rate > 0.5

def test_learning_rule_failure():
    r = LearningRule("r1", "cond", "act")
    r.apply_failure()
    assert r.usage_count == 1
    assert r.success_rate < 0.5

def test_confidence_tracker_creation():
    ct = ConfidenceTracker()
    assert ct.current == 0.5

def test_confidence_update():
    ct = ConfidenceTracker(0.5)
    assert ct.update(0.1, "test") is True
    assert ct.current == 0.6

def test_confidence_bounds():
    ct = ConfidenceTracker(0.9)
    ct.update(0.2, "test")
    assert ct.current == 1.0

def test_confidence_boost():
    ct = ConfidenceTracker()
    ct.boost_from_success()
    assert ct.current > 0.5

def test_confidence_decrease():
    ct = ConfidenceTracker()
    ct.decrease_from_failure()
    assert ct.current < 0.5

def test_strategy_adaptation_register():
    sa = StrategyAdaptation()
    assert sa.register_strategy("strategy1") is True

def test_strategy_adaptation_update():
    sa = StrategyAdaptation()
    sa.register_strategy("strategy1", 0.5)
    assert sa.update_strategy_effectiveness("strategy1", 0.2) is True

def test_strategy_selection():
    sa = StrategyAdaptation()
    sa.register_strategy("s1", 0.5)
    sa.register_strategy("s2", 0.8)
    best = sa.select_best_strategy()
    assert best == "s2"

def test_agent_learner_creation():
    al = AgentLearner("agent1")
    assert al.agent_id == "agent1"

def test_agent_record_success():
    al = AgentLearner("agent1")
    exp = al.record_experience("test_action", LearningType.SUCCESS)
    assert exp.outcome == LearningType.SUCCESS
    assert al.total_successes == 1

def test_agent_record_failure():
    al = AgentLearner("agent1")
    exp = al.record_experience("test_action", LearningType.FAILURE)
    assert al.total_failures == 1

def test_agent_add_rule():
    al = AgentLearner("agent1")
    rule = al.add_learning_rule("condition", "action")
    assert rule is not None

def test_agent_reinforce_rule():
    al = AgentLearner("agent1")
    rule = al.add_learning_rule("cond", "act")
    assert al.reinforce_rule(rule.rule_id, True) is True

def test_agent_success_rate():
    al = AgentLearner("agent1")
    al.record_experience("a1", LearningType.SUCCESS)
    al.record_experience("a2", LearningType.SUCCESS)
    al.record_experience("a3", LearningType.FAILURE)
    rate = al.get_success_rate()
    assert rate == 2.0 / 3.0

def test_complete_learning_workflow():
    al = AgentLearner("learner1")

    # Record experiences
    al.record_experience("action1", LearningType.SUCCESS)
    al.record_experience("action2", LearningType.FAILURE)
    al.record_experience("action3", LearningType.SUCCESS)

    # Add rules
    rule = al.add_learning_rule("condition1", "action1")
    al.reinforce_rule(rule.rule_id, True)

    # Verify learning
    assert len(al.experiences) == 3
    assert len(al.learning_rules) == 1
    assert al.get_success_rate() > 0.5

    # Check final state
    state = al.to_dict()
    assert state["experiences"] == 3
    assert state["success_rate"] > 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
