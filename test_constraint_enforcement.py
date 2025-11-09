"""
Round 45: Constraint Enforcement System
Validates and enforces constraints on learning challenges.
Features: constraint definitions, validation, penalties, compliance tracking.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any


class ConstraintType(Enum):
    """Types of constraints"""
    TIME_LIMIT = "time_limit"  # Must complete within time
    ACCURACY = "accuracy"  # Must meet accuracy threshold
    EFFICIENCY = "efficiency"  # Must use resources efficiently
    CREATIVITY = "creativity"  # Must demonstrate creativity
    COLLABORATION = "collaboration"  # Must work with others
    PERSISTENCE = "persistence"  # Must not give up
    SAFETY = "safety"  # Must follow safety rules
    COMPLETENESS = "completeness"  # Must complete all parts


class ConstraintSeverity(Enum):
    """Severity of constraint violation"""
    SOFT = "soft"  # Penalty but goal achievable
    HARD = "hard"  # Failure if violated
    CRITICAL = "critical"  # Immediate failure


class ConstraintStatus(Enum):
    """Status of constraint during session"""
    PENDING = "pending"
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    WARNING = "warning"


@dataclass
class ConstraintDefinition:
    """Definition of a constraint"""
    constraint_id: str
    constraint_type: ConstraintType
    description: str
    severity: ConstraintSeverity
    target_value: float  # 0.0-1.0 threshold
    penalty_factor: float = 1.0  # Multiplier for penalty (0.0-1.0)
    warning_threshold: float = 0.8  # When to warn player
    check_function: Optional[str] = None  # Name of validation function

    def to_dict(self) -> Dict:
        return {
            "id": self.constraint_id,
            "type": self.constraint_type.value,
            "description": self.description,
            "severity": self.severity.value,
            "target": self.target_value,
            "penalty": self.penalty_factor
        }


@dataclass
class ConstraintViolation:
    """Record of constraint violation"""
    violation_id: str
    constraint_id: str
    constraint_type: ConstraintType
    agent_id: str
    severity: ConstraintSeverity
    actual_value: float  # What agent actually achieved
    target_value: float  # What was required
    penalty: float = 0.0  # Penalty applied
    timestamp: float = 0.0
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.violation_id,
            "constraint": self.constraint_id,
            "type": self.constraint_type.value,
            "agent": self.agent_id,
            "severity": self.severity.value,
            "actual": self.actual_value,
            "target": self.target_value,
            "penalty": self.penalty
        }


@dataclass
class ConstraintStatus:
    """Status of constraint in session"""
    constraint_id: str
    status: ConstraintStatus
    current_value: float = 0.0
    progress: float = 0.0  # 0.0-1.0, how close to target
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "constraint": self.constraint_id,
            "status": self.status.value,
            "current": self.current_value,
            "progress": self.progress
        }


class ConstraintValidator:
    """Validates if constraints are satisfied"""

    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self._setup_default_validators()

    def _setup_default_validators(self):
        """Setup built-in validators"""
        self.validators["time_limit"] = self._validate_time
        self.validators["accuracy"] = self._validate_accuracy
        self.validators["efficiency"] = self._validate_efficiency
        self.validators["creativity"] = self._validate_creativity
        self.validators["collaboration"] = self._validate_collaboration

    def _validate_time(self, actual: float, target: float) -> bool:
        """Validate time constraint (actual <= target)"""
        return actual <= target

    def _validate_accuracy(self, actual: float, target: float) -> bool:
        """Validate accuracy constraint (actual >= target)"""
        return actual >= target

    def _validate_efficiency(self, actual: float, target: float) -> bool:
        """Validate efficiency constraint (actual >= target)"""
        return actual >= target

    def _validate_creativity(self, actual: float, target: float) -> bool:
        """Validate creativity constraint (actual >= target)"""
        return actual >= target

    def _validate_collaboration(self, actual: float, target: float) -> bool:
        """Validate collaboration constraint (actual >= target)"""
        return actual >= target

    def register_validator(self, constraint_type: str, func: Callable) -> bool:
        """Register custom validator"""
        self.validators[constraint_type] = func
        return True

    def validate(self, constraint: ConstraintDefinition, actual_value: float) -> bool:
        """Validate constraint"""
        constraint_key = constraint.constraint_type.value

        if constraint_key in self.validators:
            return self.validators[constraint_key](actual_value, constraint.target_value)

        return False


class PenaltyCalculator:
    """Calculates penalties for constraint violations"""

    def __init__(self):
        self.base_penalty = 0.1  # 10% base penalty per violation
        self.max_penalty = 0.5  # Maximum 50% penalty total

    def calculate_penalty(self, violation: ConstraintViolation) -> float:
        """Calculate penalty for violation"""
        penalty = 0.0

        # Base penalty by severity
        if violation.severity == ConstraintSeverity.SOFT:
            penalty = self.base_penalty * 0.3
        elif violation.severity == ConstraintSeverity.HARD:
            penalty = self.base_penalty
        elif violation.severity == ConstraintSeverity.CRITICAL:
            penalty = self.base_penalty * 2.0

        # Adjust by how far from target
        deviation = abs(violation.actual_value - violation.target_value)
        deviation = min(deviation, 1.0)  # Cap deviation at 1.0
        penalty *= (1.0 + deviation * 0.5)  # Gentler scaling

        # Cap at max
        return min(penalty, self.max_penalty)

    def to_dict(self) -> Dict:
        return {
            "base_penalty": self.base_penalty,
            "max_penalty": self.max_penalty
        }


class ConstraintEnforcer:
    """Applies constraints to challenge sessions"""

    def __init__(self):
        self.validator = ConstraintValidator()
        self.penalty_calculator = PenaltyCalculator()
        self.violations: Dict[str, ConstraintViolation] = {}
        self.session_violations: Dict[str, List[str]] = {}  # session_id -> violation_ids

    def check_constraints(
        self, session_id: str, agent_id: str,
        constraints: List[ConstraintDefinition],
        actual_values: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check all constraints for session"""
        results = {
            "session_id": session_id,
            "agent_id": agent_id,
            "satisfied": 0,
            "violated": 0,
            "violations": [],
            "total_penalty": 0.0,
            "can_complete": True
        }

        if session_id not in self.session_violations:
            self.session_violations[session_id] = []

        for constraint in constraints:
            constraint_key = constraint.constraint_type.value

            if constraint_key not in actual_values:
                continue

            actual = actual_values[constraint_key]

            # Check if satisfied
            if self.validator.validate(constraint, actual):
                results["satisfied"] += 1
            else:
                # Create violation
                violation = ConstraintViolation(
                    violation_id=f"{session_id}_{constraint.constraint_id}",
                    constraint_id=constraint.constraint_id,
                    constraint_type=constraint.constraint_type,
                    agent_id=agent_id,
                    severity=constraint.severity,
                    actual_value=actual,
                    target_value=constraint.target_value,
                    description=constraint.description
                )

                # Calculate penalty
                penalty = self.penalty_calculator.calculate_penalty(violation)
                violation.penalty = penalty

                self.violations[violation.violation_id] = violation
                self.session_violations[session_id].append(violation.violation_id)

                results["violated"] += 1
                results["violations"].append(violation.to_dict())
                results["total_penalty"] += penalty

                # Check severity
                if constraint.severity == ConstraintSeverity.CRITICAL:
                    results["can_complete"] = False

        return results

    def get_session_violations(self, session_id: str) -> List[ConstraintViolation]:
        """Get all violations for session"""
        if session_id not in self.session_violations:
            return []

        violation_ids = self.session_violations[session_id]
        return [self.violations[vid] for vid in violation_ids if vid in self.violations]

    def apply_penalty_to_score(self, base_score: float, total_penalty: float) -> float:
        """Apply penalty to score"""
        return max(0.0, base_score * (1.0 - total_penalty))

    def to_dict(self) -> Dict:
        return {
            "total_violations": len(self.violations),
            "sessions_checked": len(self.session_violations)
        }


class ConstraintCompliance:
    """Tracks agent compliance with constraints"""

    def __init__(self):
        self.agent_compliance: Dict[str, Dict] = {}  # agent_id -> compliance_data

    def record_compliance(self, agent_id: str, session_id: str, violations: List[ConstraintViolation]) -> bool:
        """Record compliance for agent in session"""
        if agent_id not in self.agent_compliance:
            self.agent_compliance[agent_id] = {
                "total_sessions": 0,
                "fully_compliant": 0,
                "violations_total": 0,
                "penalty_total": 0.0,
                "compliance_score": 1.0  # 0.0-1.0
            }

        data = self.agent_compliance[agent_id]
        data["total_sessions"] += 1

        if not violations:
            data["fully_compliant"] += 1
        else:
            data["violations_total"] += len(violations)
            data["penalty_total"] += sum(v.penalty for v in violations)

        # Calculate compliance score
        if data["total_sessions"] > 0:
            compliant_rate = data["fully_compliant"] / data["total_sessions"]
            penalty_rate = data["penalty_total"]
            data["compliance_score"] = compliant_rate * (1.0 - min(penalty_rate, 1.0))

        return True

    def get_agent_compliance(self, agent_id: str) -> Optional[Dict]:
        """Get agent's compliance record"""
        return self.agent_compliance.get(agent_id)

    def get_top_compliant_agents(self, limit: int = 10) -> List[str]:
        """Get most compliant agents"""
        agents = sorted(
            self.agent_compliance.items(),
            key=lambda x: x[1]["compliance_score"],
            reverse=True
        )
        return [aid for aid, _ in agents[:limit]]

    def to_dict(self) -> Dict:
        return {
            "agents_tracked": len(self.agent_compliance),
            "avg_compliance": (
                sum(d["compliance_score"] for d in self.agent_compliance.values()) /
                len(self.agent_compliance)
                if self.agent_compliance else 0.0
            )
        }


# ===== Tests =====

def test_constraint_definition():
    """Test creating constraint definition"""
    constraint = ConstraintDefinition(
        "c1", ConstraintType.TIME_LIMIT, "Complete within 10 minutes",
        ConstraintSeverity.HARD, 10.0
    )
    assert constraint.constraint_id == "c1"
    assert constraint.constraint_type == ConstraintType.TIME_LIMIT


def test_constraint_violation():
    """Test creating constraint violation"""
    violation = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent1", ConstraintSeverity.HARD, 15.0, 10.0
    )
    assert violation.violation_id == "v1"
    assert violation.actual_value == 15.0


def test_constraint_validator_time():
    """Test time constraint validation"""
    validator = ConstraintValidator()
    constraint = ConstraintDefinition(
        "c1", ConstraintType.TIME_LIMIT, "Desc",
        ConstraintSeverity.HARD, 10.0
    )

    # Within time: pass
    assert validator.validate(constraint, 8.0) is True

    # Over time: fail
    assert validator.validate(constraint, 12.0) is False


def test_constraint_validator_accuracy():
    """Test accuracy constraint validation"""
    validator = ConstraintValidator()
    constraint = ConstraintDefinition(
        "c1", ConstraintType.ACCURACY, "Desc",
        ConstraintSeverity.HARD, 0.8  # Need 80% accuracy
    )

    # Good accuracy: pass
    assert validator.validate(constraint, 0.9) is True

    # Low accuracy: fail
    assert validator.validate(constraint, 0.7) is False


def test_penalty_calculator_soft():
    """Test penalty for soft violation"""
    calc = PenaltyCalculator()
    violation = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent1", ConstraintSeverity.SOFT, 12.0, 10.0
    )

    penalty = calc.calculate_penalty(violation)
    assert 0.0 < penalty < 0.15  # Soft penalty is 30% of base


def test_penalty_calculator_hard():
    """Test penalty for hard violation"""
    calc = PenaltyCalculator()
    violation = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent1", ConstraintSeverity.HARD, 15.0, 10.0
    )

    penalty = calc.calculate_penalty(violation)
    assert 0.0 < penalty <= 0.5


def test_constraint_enforcer_check():
    """Test constraint enforcer"""
    enforcer = ConstraintEnforcer()

    constraints = [
        ConstraintDefinition(
            "c1", ConstraintType.TIME_LIMIT, "Time limit",
            ConstraintSeverity.HARD, 10.0
        ),
        ConstraintDefinition(
            "c2", ConstraintType.ACCURACY, "Accuracy",
            ConstraintSeverity.HARD, 0.8
        )
    ]

    actual_values = {
        "time_limit": 8.0,  # Good
        "accuracy": 0.9  # Good
    }

    results = enforcer.check_constraints("session1", "agent1", constraints, actual_values)
    assert results["satisfied"] == 2
    assert results["violated"] == 0


def test_constraint_enforcer_violation():
    """Test constraint violation detection"""
    enforcer = ConstraintEnforcer()

    constraints = [
        ConstraintDefinition(
            "c1", ConstraintType.TIME_LIMIT, "Time limit",
            ConstraintSeverity.HARD, 10.0
        )
    ]

    actual_values = {
        "time_limit": 15.0  # Over time
    }

    results = enforcer.check_constraints("session1", "agent1", constraints, actual_values)
    assert results["violated"] == 1
    assert results["total_penalty"] > 0


def test_constraint_enforcer_critical():
    """Test critical constraint"""
    enforcer = ConstraintEnforcer()

    constraints = [
        ConstraintDefinition(
            "c1", ConstraintType.SAFETY, "Safety",
            ConstraintSeverity.CRITICAL, 1.0
        )
    ]

    actual_values = {
        "safety": 0.5  # Safety violated
    }

    results = enforcer.check_constraints("session1", "agent1", constraints, actual_values)
    assert results["can_complete"] is False


def test_penalty_applied_to_score():
    """Test penalty reduces score"""
    enforcer = ConstraintEnforcer()

    base_score = 1.0
    penalty = 0.2

    final_score = enforcer.apply_penalty_to_score(base_score, penalty)
    assert final_score == 0.8


def test_constraint_compliance_tracking():
    """Test tracking agent compliance"""
    compliance = ConstraintCompliance()

    violation = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent1", ConstraintSeverity.HARD, 15.0, 10.0,
        penalty=0.1
    )

    assert compliance.record_compliance("agent1", "session1", [violation]) is True

    record = compliance.get_agent_compliance("agent1")
    assert record["total_sessions"] == 1
    assert record["violations_total"] == 1


def test_compliance_full_session():
    """Test fully compliant session"""
    compliance = ConstraintCompliance()

    # No violations = fully compliant
    assert compliance.record_compliance("agent1", "session1", []) is True

    record = compliance.get_agent_compliance("agent1")
    assert record["fully_compliant"] == 1
    assert record["compliance_score"] == 1.0


def test_compliance_multiple_sessions():
    """Test compliance across multiple sessions"""
    compliance = ConstraintCompliance()

    # Session 1: no violations
    compliance.record_compliance("agent1", "session1", [])

    # Session 2: one violation
    v = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent1", ConstraintSeverity.HARD, 15.0, 10.0,
        penalty=0.1
    )
    compliance.record_compliance("agent1", "session2", [v])

    record = compliance.get_agent_compliance("agent1")
    assert record["total_sessions"] == 2
    assert record["fully_compliant"] == 1
    assert record["compliance_score"] < 1.0


def test_top_compliant_agents():
    """Test getting top compliant agents"""
    compliance = ConstraintCompliance()

    # Agent 1: perfect compliance
    compliance.record_compliance("agent1", "s1", [])
    compliance.record_compliance("agent1", "s2", [])

    # Agent 2: one violation
    v = ConstraintViolation(
        "v1", "c1", ConstraintType.TIME_LIMIT,
        "agent2", ConstraintSeverity.HARD, 15.0, 10.0,
        penalty=0.1
    )
    compliance.record_compliance("agent2", "s1", [v])

    top = compliance.get_top_compliant_agents(2)
    assert top[0] == "agent1"  # Perfect compliance


def test_complete_constraint_workflow():
    """Test complete constraint enforcement workflow"""
    enforcer = ConstraintEnforcer()
    compliance = ConstraintCompliance()

    # Define constraints
    constraints = [
        ConstraintDefinition(
            "c1", ConstraintType.TIME_LIMIT, "Complete within 15 mins",
            ConstraintSeverity.HARD, 15.0
        ),
        ConstraintDefinition(
            "c2", ConstraintType.ACCURACY, "Achieve 85% accuracy",
            ConstraintSeverity.HARD, 0.85
        ),
        ConstraintDefinition(
            "c3", ConstraintType.CREATIVITY, "Show creativity",
            ConstraintSeverity.SOFT, 0.6
        )
    ]

    # Agent performs challenge
    actual_values = {
        "time_limit": 12.0,  # Good
        "accuracy": 0.88,  # Good
        "creativity": 0.5  # Below soft threshold
    }

    # Check constraints
    results = enforcer.check_constraints("session1", "agent1", constraints, actual_values)

    assert results["satisfied"] >= 2
    assert results["can_complete"] is True

    # Track compliance
    violations = enforcer.get_session_violations("session1")
    compliance.record_compliance("agent1", "session1", violations)

    record = compliance.get_agent_compliance("agent1")
    assert record["total_sessions"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
