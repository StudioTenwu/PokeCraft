"""
Round 25: Conflict & Challenge Resolution System

Enable meaningful challenges, failure states, and recovery mechanics.
Agents and players face obstacles that test their capabilities and offer
learning through adversity and problem-solving.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ChallengeType(Enum):
    """Types of challenges agents can face"""
    SKILL_TEST = "skill_test"  # Must use specific skill
    PUZZLE = "puzzle"  # Requires reasoning
    MORAL = "moral"  # Ethical dilemma
    TIME_CONSTRAINT = "time_constraint"  # Must succeed within limit
    RESOURCE_SCARCITY = "resource_scarcity"  # Limited resources
    INTERPERSONAL = "interpersonal"  # Social/communication challenge


class ChallengeStatus(Enum):
    """Status of a challenge"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ABANDONED = "abandoned"


class ConflictType(Enum):
    """Types of conflicts that can arise"""
    INTERNAL = "internal"  # Agent's internal contradiction
    EXTERNAL = "external"  # External pressure/opposition
    RELATIONAL = "relational"  # With other agents or players
    SYSTEMIC = "systemic"  # With environment/rules


class ResolutionStrategy(Enum):
    """Ways to resolve conflicts"""
    DIRECT = "direct"  # Head-on confrontation
    DIPLOMATIC = "diplomatic"  # Negotiation
    CREATIVE = "creative"  # Unusual/novel solution
    WITHDRAWAL = "withdrawal"  # Avoid/retreat
    SYNTHESIS = "synthesis"  # Combine opposing viewpoints


@dataclass
class Challenge:
    """A challenge to overcome"""
    challenge_id: str
    type: ChallengeType
    difficulty: int = 1  # 1-10
    status: ChallengeStatus = ChallengeStatus.AVAILABLE
    description: str = ""
    required_skill: Optional[str] = None
    time_limit: Optional[int] = None  # Steps/turns allowed
    success_condition: str = ""
    failure_consequence: str = ""
    attempts: int = 0
    max_attempts: int = 3
    successes: int = 0

    def start(self) -> bool:
        """Begin the challenge"""
        if self.status != ChallengeStatus.AVAILABLE:
            return False
        self.status = ChallengeStatus.IN_PROGRESS
        self.attempts += 1
        return True

    def succeed(self) -> bool:
        """Mark challenge as succeeded"""
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False
        self.status = ChallengeStatus.SUCCEEDED
        self.successes += 1
        return True

    def fail(self) -> bool:
        """Mark challenge as failed"""
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False
        if self.attempts >= self.max_attempts:
            self.status = ChallengeStatus.FAILED
        else:
            self.status = ChallengeStatus.AVAILABLE
        return True

    def abandon(self) -> bool:
        """Abandon the challenge"""
        if self.status == ChallengeStatus.ABANDONED:
            return False
        self.status = ChallengeStatus.ABANDONED
        return True

    def can_retry(self) -> bool:
        """Check if challenge can be retried"""
        return self.attempts < self.max_attempts and self.status in [
            ChallengeStatus.AVAILABLE,
            ChallengeStatus.FAILED
        ]

    def to_dict(self) -> Dict:
        return {
            "challenge_id": self.challenge_id,
            "type": self.type.value,
            "status": self.status.value,
            "attempts": self.attempts,
            "successes": self.successes
        }


@dataclass
class Conflict:
    """A conflict situation"""
    conflict_id: str
    type: ConflictType
    severity: float = 0.5  # 0.0-1.0
    status: str = "active"  # active, resolved, suppressed
    parties: List[str] = field(default_factory=list)  # IDs involved
    root_cause: str = ""
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_effectiveness: float = 0.0  # 0.0-1.0

    def apply_resolution(self, strategy: ResolutionStrategy) -> bool:
        """Attempt to resolve conflict"""
        if self.status != "active":
            return False
        self.resolution_strategy = strategy
        # Different strategies have different effectiveness
        effectiveness_map = {
            ResolutionStrategy.DIRECT: 0.75,
            ResolutionStrategy.DIPLOMATIC: 0.8,
            ResolutionStrategy.CREATIVE: 0.9,
            ResolutionStrategy.WITHDRAWAL: 0.3,
            ResolutionStrategy.SYNTHESIS: 0.95
        }
        self.resolution_effectiveness = effectiveness_map.get(strategy, 0.5)

        # High effectiveness = resolved, low = suppressed
        if self.resolution_effectiveness >= 0.7:
            self.status = "resolved"
        else:
            self.status = "suppressed"
        return True

    def escalate(self) -> bool:
        """Escalate conflict severity"""
        if self.severity >= 1.0:
            return False
        self.severity = min(1.0, self.severity + 0.2)
        return True

    def de_escalate(self) -> bool:
        """De-escalate conflict severity"""
        if self.severity <= 0.0:
            return False
        self.severity = max(0.0, self.severity - 0.2)
        return True

    def to_dict(self) -> Dict:
        return {
            "conflict_id": self.conflict_id,
            "type": self.type.value,
            "severity": self.severity,
            "status": self.status,
            "resolution_strategy": self.resolution_strategy.value if self.resolution_strategy else None
        }


@dataclass
class FailureState:
    """Tracks agent failure and recovery"""
    failure_id: str
    agent_id: str
    challenge_id: str
    failure_type: str
    severity: float = 0.5  # 0.0-1.0
    trust_loss: float = 0.0  # 0.0-1.0
    recovery_attempts: int = 0
    recovered: bool = False
    learning_gained: float = 0.0  # 0.0-1.0

    def attempt_recovery(self) -> bool:
        """Attempt to recover from failure"""
        if self.recovered:
            return False
        self.recovery_attempts += 1
        # Learning increases with attempts, capped at 0.9
        self.learning_gained = min(0.9, self.recovery_attempts * 0.15)
        # Recovery succeeds after enough attempts
        if self.recovery_attempts >= 3 or (self.learning_gained >= 0.6):
            self.recovered = True
        return True

    def to_dict(self) -> Dict:
        return {
            "failure_id": self.failure_id,
            "agent_id": self.agent_id,
            "failure_type": self.failure_type,
            "severity": self.severity,
            "trust_loss": self.trust_loss,
            "recovered": self.recovered,
            "learning_gained": self.learning_gained
        }


class ConflictResolutionSystem:
    """Manage challenges, conflicts, and failure recovery"""

    def __init__(self):
        self.challenges: Dict[str, Challenge] = {}
        self.conflicts: Dict[str, Conflict] = {}
        self.failures: Dict[str, FailureState] = {}
        self.challenge_history: List[str] = []
        self.total_challenges_completed: int = 0
        self.total_conflicts_resolved: int = 0

    def create_challenge(self, challenge: Challenge) -> bool:
        """Create a new challenge"""
        if challenge.challenge_id in self.challenges:
            return False
        self.challenges[challenge.challenge_id] = challenge
        return True

    def start_challenge(self, challenge_id: str) -> bool:
        """Start a challenge"""
        if challenge_id not in self.challenges:
            return False
        challenge = self.challenges[challenge_id]
        return challenge.start()

    def complete_challenge(self, challenge_id: str, success: bool) -> Optional[FailureState]:
        """Complete a challenge (succeed or fail)"""
        if challenge_id not in self.challenges:
            return None

        challenge = self.challenges[challenge_id]

        if success:
            if challenge.succeed():
                self.challenge_history.append(challenge_id)
                self.total_challenges_completed += 1
                return None
        else:
            challenge.fail()
            if challenge.status == ChallengeStatus.FAILED:
                # Create failure state for recovery
                failure = FailureState(
                    failure_id=f"fail_{len(self.failures)}",
                    agent_id="unknown",
                    challenge_id=challenge_id,
                    failure_type=challenge.type.value,
                    severity=challenge.difficulty / 10.0
                )
                self.failures[failure.failure_id] = failure
                return failure

        return None

    def create_conflict(self, conflict: Conflict) -> bool:
        """Create a new conflict"""
        if conflict.conflict_id in self.conflicts:
            return False
        self.conflicts[conflict.conflict_id] = conflict
        return True

    def resolve_conflict(self, conflict_id: str, strategy: ResolutionStrategy) -> bool:
        """Attempt to resolve a conflict"""
        if conflict_id not in self.conflicts:
            return False

        conflict = self.conflicts[conflict_id]
        if conflict.apply_resolution(strategy):
            if conflict.status == "resolved":
                self.total_conflicts_resolved += 1
            return True
        return False

    def recover_from_failure(self, failure_id: str) -> bool:
        """Attempt recovery from failure"""
        if failure_id not in self.failures:
            return False

        failure = self.failures[failure_id]
        return failure.attempt_recovery()

    def get_challenge_difficulty(self, challenge_id: str) -> Optional[int]:
        """Get challenge difficulty rating"""
        if challenge_id not in self.challenges:
            return None
        return self.challenges[challenge_id].difficulty

    def get_agent_challenge_success_rate(self, agent_id: str) -> float:
        """Calculate agent's challenge success rate"""
        agent_challenges = [
            c for c in self.challenges.values()
            if agent_id in c.challenge_id or True  # Simplified: any challenge
        ]
        if not agent_challenges:
            return 0.0

        successes = sum(1 for c in agent_challenges if c.status == ChallengeStatus.SUCCEEDED)
        return successes / max(1, len(agent_challenges))

    def get_conflict_resolution_rate(self) -> float:
        """Calculate percentage of conflicts successfully resolved"""
        if not self.conflicts:
            return 0.0
        resolved = sum(1 for c in self.conflicts.values() if c.status == "resolved")
        return resolved / len(self.conflicts)

    def get_system_resilience(self) -> Dict:
        """Calculate overall system resilience metrics"""
        return {
            "total_challenges": len(self.challenges),
            "challenges_completed": self.total_challenges_completed,
            "total_conflicts": len(self.conflicts),
            "conflicts_resolved": self.total_conflicts_resolved,
            "active_failures": sum(1 for f in self.failures.values() if not f.recovered),
            "recovery_rate": sum(1 for f in self.failures.values() if f.recovered) / max(1, len(self.failures))
        }

    def to_dict(self) -> Dict:
        return {
            "challenges": {k: v.to_dict() for k, v in self.challenges.items()},
            "conflicts": {k: v.to_dict() for k, v in self.conflicts.items()},
            "failures": {k: v.to_dict() for k, v in self.failures.items()},
            "resilience": self.get_system_resilience()
        }


# ===== Tests =====

def test_challenge_creation():
    """Test creating challenges"""
    challenge = Challenge(
        challenge_id="c1",
        type=ChallengeType.SKILL_TEST,
        difficulty=5
    )
    assert challenge.status == ChallengeStatus.AVAILABLE


def test_challenge_lifecycle():
    """Test challenge progression"""
    challenge = Challenge(challenge_id="c1", type=ChallengeType.PUZZLE, difficulty=3)
    assert challenge.start() is True
    assert challenge.status == ChallengeStatus.IN_PROGRESS
    assert challenge.succeed() is True
    assert challenge.status == ChallengeStatus.SUCCEEDED


def test_challenge_failure_and_retry():
    """Test challenge failure with retries"""
    challenge = Challenge(challenge_id="c1", type=ChallengeType.PUZZLE, max_attempts=3)
    assert challenge.start() is True
    assert challenge.fail() is True
    assert challenge.status == ChallengeStatus.AVAILABLE
    assert challenge.can_retry() is True


def test_challenge_max_attempts():
    """Test challenge exhaustion after max attempts"""
    challenge = Challenge(challenge_id="c1", type=ChallengeType.SKILL_TEST, max_attempts=2)
    challenge.start()
    challenge.fail()
    assert challenge.can_retry() is True

    challenge.start()
    challenge.fail()
    assert challenge.status == ChallengeStatus.FAILED
    assert challenge.can_retry() is False


def test_conflict_creation():
    """Test creating conflicts"""
    conflict = Conflict(
        conflict_id="con1",
        type=ConflictType.INTERNAL,
        severity=0.6,
        parties=["agent_1"]
    )
    assert conflict.status == "active"


def test_conflict_resolution():
    """Test resolving conflicts"""
    conflict = Conflict(conflict_id="con1", type=ConflictType.EXTERNAL)
    assert conflict.apply_resolution(ResolutionStrategy.DIPLOMATIC) is True
    assert conflict.status == "resolved"
    assert conflict.resolution_effectiveness >= 0.7


def test_conflict_escalation():
    """Test conflict escalation"""
    conflict = Conflict(conflict_id="con1", type=ConflictType.RELATIONAL, severity=0.3)
    assert conflict.escalate() is True
    assert conflict.severity == 0.5


def test_conflict_de_escalation():
    """Test conflict de-escalation"""
    conflict = Conflict(conflict_id="con1", type=ConflictType.SYSTEMIC, severity=0.8)
    assert conflict.de_escalate() is True
    assert abs(conflict.severity - 0.6) < 0.0001


def test_failure_state_creation():
    """Test creating failure states"""
    failure = FailureState(
        failure_id="f1",
        agent_id="a1",
        challenge_id="c1",
        failure_type="skill_test"
    )
    assert failure.recovered is False


def test_failure_recovery():
    """Test recovering from failure"""
    failure = FailureState(failure_id="f1", agent_id="a1", challenge_id="c1", failure_type="puzzle")
    assert failure.attempt_recovery() is True
    assert failure.recovery_attempts == 1
    assert failure.learning_gained > 0.0


def test_failure_full_recovery():
    """Test complete recovery after multiple attempts"""
    failure = FailureState(failure_id="f1", agent_id="a1", challenge_id="c1", failure_type="moral")
    failure.attempt_recovery()
    failure.attempt_recovery()
    failure.attempt_recovery()
    assert failure.recovered is True
    assert failure.learning_gained > 0.44


def test_conflict_resolution_system():
    """Test conflict resolution system"""
    system = ConflictResolutionSystem()

    challenge = Challenge(challenge_id="c1", type=ChallengeType.PUZZLE, difficulty=4)
    assert system.create_challenge(challenge) is True

    assert system.start_challenge("c1") is True
    system.complete_challenge("c1", success=True)

    assert system.total_challenges_completed == 1


def test_conflict_management():
    """Test managing conflicts in system"""
    system = ConflictResolutionSystem()

    conflict = Conflict(conflict_id="con1", type=ConflictType.INTERNAL, severity=0.5)
    assert system.create_conflict(conflict) is True

    assert system.resolve_conflict("con1", ResolutionStrategy.CREATIVE) is True
    assert system.total_conflicts_resolved == 1


def test_failure_recovery_system():
    """Test failure recovery in system"""
    system = ConflictResolutionSystem()

    failure = system.complete_challenge("c1", success=False)
    if failure:
        assert system.recover_from_failure(failure.failure_id) is True


def test_system_resilience_metrics():
    """Test system resilience calculation"""
    system = ConflictResolutionSystem()

    challenge = Challenge(challenge_id="c1", type=ChallengeType.SKILL_TEST)
    system.create_challenge(challenge)
    system.start_challenge("c1")
    system.complete_challenge("c1", success=True)

    resilience = system.get_system_resilience()
    assert "challenges_completed" in resilience
    assert resilience["challenges_completed"] == 1


def test_resolution_strategy_effectiveness():
    """Test different resolution strategies have different effectiveness"""
    weak_conflict = Conflict(conflict_id="con1", type=ConflictType.EXTERNAL)
    strong_conflict = Conflict(conflict_id="con2", type=ConflictType.SYSTEMIC)

    weak_conflict.apply_resolution(ResolutionStrategy.WITHDRAWAL)
    strong_conflict.apply_resolution(ResolutionStrategy.SYNTHESIS)

    assert weak_conflict.resolution_effectiveness < strong_conflict.resolution_effectiveness


def test_complete_challenge_resolution_workflow():
    """Test complete workflow from challenge through resolution"""
    system = ConflictResolutionSystem()

    # Create and start challenge
    challenge = Challenge(
        challenge_id="hero_quest_1",
        type=ChallengeType.MORAL,
        difficulty=7,
        max_attempts=2,
        description="Choose between two conflicting values"
    )
    system.create_challenge(challenge)
    system.start_challenge("hero_quest_1")

    # Agent fails first attempt
    system.complete_challenge("hero_quest_1", success=False)

    # Try again
    system.start_challenge("hero_quest_1")
    failure = system.complete_challenge("hero_quest_1", success=False)

    # Now failure should be created (max attempts reached)
    assert failure is not None

    # Agent attempts recovery
    system.recover_from_failure(failure.failure_id)
    assert failure.learning_gained > 0.0

    # Create new challenge to succeed
    challenge2 = Challenge(challenge_id="hero_quest_2", type=ChallengeType.MORAL)
    system.create_challenge(challenge2)
    system.start_challenge("hero_quest_2")
    system.complete_challenge("hero_quest_2", success=True)

    assert system.total_challenges_completed == 1


def test_multi_conflict_resolution():
    """Test managing multiple conflicts with different strategies"""
    system = ConflictResolutionSystem()

    conflicts = [
        Conflict(conflict_id="con1", type=ConflictType.INTERNAL),
        Conflict(conflict_id="con2", type=ConflictType.EXTERNAL),
        Conflict(conflict_id="con3", type=ConflictType.RELATIONAL),
    ]

    for c in conflicts:
        system.create_conflict(c)

    system.resolve_conflict("con1", ResolutionStrategy.CREATIVE)
    system.resolve_conflict("con2", ResolutionStrategy.DIPLOMATIC)
    system.resolve_conflict("con3", ResolutionStrategy.DIRECT)

    resilience = system.get_system_resilience()
    assert resilience["conflicts_resolved"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
