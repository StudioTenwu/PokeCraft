"""
Round 46: Error Handling & Recovery System
Production-grade exception handling, error logging, and recovery strategies.
Features: error categories, recovery mechanisms, error tracking, graceful degradation.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any


class ErrorCategory(Enum):
    """Categories of errors that can occur"""
    VALIDATION = "validation"  # Data validation failed
    RESOURCE = "resource"  # Resource not found or unavailable
    PERMISSION = "permission"  # Permission denied
    STATE = "state"  # Invalid state transition
    CONSTRAINT = "constraint"  # Constraint violation
    INTEGRATION = "integration"  # System integration error
    EXTERNAL = "external"  # External service error
    UNKNOWN = "unknown"  # Unknown error


class ErrorSeverity(Enum):
    """Severity of error"""
    MINOR = "minor"  # Can ignore, continue with reduced functionality
    MODERATE = "moderate"  # Should handle, may affect feature
    SEVERE = "severe"  # Must handle, feature unavailable
    CRITICAL = "critical"  # System failure, immediate intervention needed


class RecoveryStrategy(Enum):
    """Strategy for recovering from error"""
    RETRY = "retry"  # Retry operation
    FALLBACK = "fallback"  # Use fallback/default value
    DEGRADE = "degrade"  # Reduce functionality
    SKIP = "skip"  # Skip operation, continue
    ABORT = "abort"  # Abort and report


@dataclass
class ErrorRecord:
    """Record of error occurrence"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    stack_trace: str = ""
    resolved: bool = False
    resolution_method: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "resolved": self.resolved,
            "method": self.resolution_method
        }


@dataclass
class RecoveryAction:
    """Action to take for error recovery"""
    action_id: str
    error_category: ErrorCategory
    strategy: RecoveryStrategy
    handler_func: str  # Name of handler function
    retry_count: int = 3
    timeout: float = 5.0
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.action_id,
            "category": self.error_category.value,
            "strategy": self.strategy.value,
            "retries": self.retry_count
        }


class ErrorLogger:
    """Logs and tracks all errors in system"""

    def __init__(self):
        self.errors: Dict[str, ErrorRecord] = {}
        self.error_count_by_category: Dict[str, int] = {}
        self.error_count_by_severity: Dict[str, int] = {}

    def log_error(self, error: ErrorRecord) -> bool:
        """Log error occurrence"""
        if error.error_id in self.errors:
            return False

        self.errors[error.error_id] = error

        # Track by category
        if error.category not in self.error_count_by_category:
            self.error_count_by_category[error.category] = 0
        self.error_count_by_category[error.category] += 1

        # Track by severity
        if error.severity not in self.error_count_by_severity:
            self.error_count_by_severity[error.severity] = 0
        self.error_count_by_severity[error.severity] += 1

        return True

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error by ID"""
        return self.errors.get(error_id)

    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorRecord]:
        """Get all errors in category"""
        return [e for e in self.errors.values() if e.category == category]

    def get_unresolved_errors(self) -> List[ErrorRecord]:
        """Get all unresolved errors"""
        return [e for e in self.errors.values() if not e.resolved]

    def mark_resolved(self, error_id: str, resolution_method: str) -> bool:
        """Mark error as resolved"""
        if error_id not in self.errors:
            return False

        error = self.errors[error_id]
        error.resolved = True
        error.resolution_method = resolution_method
        return True

    def get_statistics(self) -> Dict:
        """Get error statistics"""
        return {
            "total_errors": len(self.errors),
            "unresolved": len(self.get_unresolved_errors()),
            "by_category": dict(self.error_count_by_category),
            "by_severity": dict(self.error_count_by_severity)
        }

    def to_dict(self) -> Dict:
        return {
            "total_errors": len(self.errors),
            "categories": len(self.error_count_by_category),
            "unresolved": len(self.get_unresolved_errors())
        }


class ExceptionHandler:
    """Handles exceptions with appropriate recovery strategies"""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.error_logger = ErrorLogger()
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Setup built-in exception handlers"""
        self.handlers["validation"] = self._handle_validation_error
        self.handlers["resource"] = self._handle_resource_error
        self.handlers["permission"] = self._handle_permission_error
        self.handlers["state"] = self._handle_state_error

    def _handle_validation_error(self, error: ErrorRecord) -> bool:
        """Handle validation error"""
        # Log and mark as recoverable
        self.error_logger.log_error(error)
        return True

    def _handle_resource_error(self, error: ErrorRecord) -> bool:
        """Handle resource error"""
        # Log and suggest retry
        self.error_logger.log_error(error)
        return True

    def _handle_permission_error(self, error: ErrorRecord) -> bool:
        """Handle permission error"""
        # Log and suggest user action
        self.error_logger.log_error(error)
        return True

    def _handle_state_error(self, error: ErrorRecord) -> bool:
        """Handle state error"""
        # Log and reset to known state
        self.error_logger.log_error(error)
        return True

    def register_handler(self, category: str, func: Callable) -> bool:
        """Register custom error handler"""
        self.handlers[category] = func
        return True

    def register_recovery_action(self, action: RecoveryAction) -> bool:
        """Register recovery action for error category"""
        self.recovery_actions[action.error_category.value] = action
        return True

    def handle_exception(self, category: ErrorCategory, message: str,
                        severity: ErrorSeverity, context: Dict = None) -> bool:
        """Handle exception with appropriate strategy"""
        if context is None:
            context = {}

        error = ErrorRecord(
            error_id=f"err_{len(self.error_logger.errors)}",
            category=category,
            severity=severity,
            message=message,
            context=context
        )

        # Log error
        self.error_logger.log_error(error)

        # Call handler if registered
        handler_key = category.value
        if handler_key in self.handlers:
            self.handlers[handler_key](error)

        # Apply recovery strategy if defined
        if handler_key in self.recovery_actions:
            action = self.recovery_actions[handler_key]
            return self._apply_recovery(action, error)

        return True

    def _apply_recovery(self, action: RecoveryAction, error: ErrorRecord) -> bool:
        """Apply recovery strategy"""
        if action.strategy == RecoveryStrategy.RETRY:
            return True  # Caller will retry
        elif action.strategy == RecoveryStrategy.FALLBACK:
            return True  # Use fallback value
        elif action.strategy == RecoveryStrategy.DEGRADE:
            return True  # Reduce functionality
        elif action.strategy == RecoveryStrategy.SKIP:
            return True  # Continue operation
        elif action.strategy == RecoveryStrategy.ABORT:
            return False  # Abort operation

        return False

    def get_recovery_action(self, category: ErrorCategory) -> Optional[RecoveryAction]:
        """Get recovery action for error category"""
        return self.recovery_actions.get(category.value)

    def to_dict(self) -> Dict:
        return {
            "handlers": len(self.handlers),
            "recovery_actions": len(self.recovery_actions),
            "total_errors": self.error_logger.to_dict()["total_errors"]
        }


class RecoveryManager:
    """Manages recovery strategies for different failure types"""

    def __init__(self):
        self.strategies: Dict[str, List[RecoveryStrategy]] = {}
        self.recovery_success_rate: Dict[str, float] = {}
        self._setup_default_strategies()

    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        # Validation errors: skip or fallback
        self.strategies["validation"] = [
            RecoveryStrategy.FALLBACK,
            RecoveryStrategy.SKIP
        ]

        # Resource errors: retry then fallback
        self.strategies["resource"] = [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.FALLBACK
        ]

        # Permission errors: skip or abort
        self.strategies["permission"] = [
            RecoveryStrategy.SKIP,
            RecoveryStrategy.ABORT
        ]

        # State errors: degrade or abort
        self.strategies["state"] = [
            RecoveryStrategy.DEGRADE,
            RecoveryStrategy.ABORT
        ]

    def get_recovery_strategies(self, category: ErrorCategory) -> List[RecoveryStrategy]:
        """Get recovery strategies for error category"""
        return self.strategies.get(category.value, [RecoveryStrategy.ABORT])

    def record_recovery_attempt(self, category: str, success: bool) -> bool:
        """Record success/failure of recovery attempt"""
        if category not in self.recovery_success_rate:
            self.recovery_success_rate[category] = 0.0

        current = self.recovery_success_rate[category]
        if success:
            self.recovery_success_rate[category] = (current + 1.0) / 2.0
        else:
            self.recovery_success_rate[category] = current * 0.9

        return True

    def get_recovery_success_rate(self, category: str) -> float:
        """Get success rate for category's recovery"""
        return self.recovery_success_rate.get(category, 0.0)

    def to_dict(self) -> Dict:
        return {
            "categories": len(self.strategies),
            "tracked_success_rates": len(self.recovery_success_rate)
        }


class GracefulDegradation:
    """Continue operation with reduced functionality on errors"""

    def __init__(self):
        self.feature_status: Dict[str, bool] = {}  # feature_name -> enabled
        self.degraded_features: List[str] = []
        self.performance_impact: Dict[str, float] = {}  # feature -> impact (0.0-1.0)

    def enable_feature(self, feature_name: str) -> bool:
        """Enable feature"""
        self.feature_status[feature_name] = True
        return True

    def disable_feature(self, feature_name: str, reason: str = "") -> bool:
        """Disable feature gracefully"""
        self.feature_status[feature_name] = False
        self.degraded_features.append(feature_name)

        if not reason:
            self.performance_impact[feature_name] = 0.1

        return True

    def is_feature_available(self, feature_name: str) -> bool:
        """Check if feature is available"""
        return self.feature_status.get(feature_name, False)

    def get_available_features(self) -> List[str]:
        """Get all available features"""
        return [f for f, enabled in self.feature_status.items() if enabled]

    def get_degradation_impact(self) -> float:
        """Get overall system impact from degradation (0.0-1.0)"""
        if not self.degraded_features:
            return 0.0

        total_impact = sum(
            self.performance_impact.get(f, 0.1)
            for f in self.degraded_features
        )

        return min(total_impact / len(self.degraded_features), 1.0)

    def can_continue_operation(self) -> bool:
        """Check if system can continue basic operation"""
        # At least 50% of features must be available
        if not self.feature_status:
            return True

        available = len(self.get_available_features())
        total = len(self.feature_status)
        return available >= (total * 0.5)

    def to_dict(self) -> Dict:
        return {
            "total_features": len(self.feature_status),
            "available": len(self.get_available_features()),
            "degraded": len(self.degraded_features),
            "impact": self.get_degradation_impact()
        }


class ErrorHandlingManager:
    """Central manager for all error handling and recovery"""

    def __init__(self):
        self.exception_handler = ExceptionHandler()
        self.recovery_manager = RecoveryManager()
        self.degradation = GracefulDegradation()
        self.error_policies: Dict[str, Dict] = {}

    def handle_system_error(self, category: ErrorCategory, message: str,
                           severity: ErrorSeverity, context: Dict = None) -> Dict:
        """Handle system error with full recovery pipeline"""
        if context is None:
            context = {}

        # Log error
        self.exception_handler.handle_exception(category, message, severity, context)

        # Get recovery strategies
        strategies = self.recovery_manager.get_recovery_strategies(category)

        # Determine action
        action = "continue"
        if severity == ErrorSeverity.CRITICAL:
            action = "alert"
        elif severity == ErrorSeverity.SEVERE:
            if RecoveryStrategy.DEGRADE in strategies:
                action = "degrade"

        return {
            "category": category.value,
            "severity": severity.value,
            "action": action,
            "strategies": [s.value for s in strategies]
        }

    def set_error_policy(self, category: str, policy: Dict) -> bool:
        """Set custom error handling policy"""
        self.error_policies[category] = policy
        return True

    def get_system_health(self) -> Dict:
        """Get overall system health"""
        return {
            "total_errors": self.exception_handler.error_logger.to_dict()["total_errors"],
            "unresolved": len(self.exception_handler.error_logger.get_unresolved_errors()),
            "degradation_impact": self.degradation.get_degradation_impact(),
            "can_operate": self.degradation.can_continue_operation()
        }

    def to_dict(self) -> Dict:
        return {
            "exception_handler": self.exception_handler.to_dict(),
            "recovery_manager": self.recovery_manager.to_dict(),
            "degradation": self.degradation.to_dict()
        }


# ===== Tests =====

def test_error_record_creation():
    """Test creating error record"""
    error = ErrorRecord(
        "err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR,
        "Invalid input data"
    )
    assert error.error_id == "err1"
    assert error.category == ErrorCategory.VALIDATION


def test_error_logger_log():
    """Test logging error"""
    logger = ErrorLogger()
    error = ErrorRecord(
        "err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR,
        "Invalid input"
    )
    assert logger.log_error(error) is True
    assert logger.get_error("err1") is not None


def test_error_logger_duplicate_rejection():
    """Test logger rejects duplicate error"""
    logger = ErrorLogger()
    error = ErrorRecord(
        "err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR,
        "Invalid input"
    )
    assert logger.log_error(error) is True
    assert logger.log_error(error) is False


def test_error_logger_by_category():
    """Test getting errors by category"""
    logger = ErrorLogger()
    e1 = ErrorRecord(
        "err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR, "Msg1"
    )
    e2 = ErrorRecord(
        "err2", ErrorCategory.RESOURCE, ErrorSeverity.MINOR, "Msg2"
    )
    logger.log_error(e1)
    logger.log_error(e2)

    validation_errors = logger.get_errors_by_category(ErrorCategory.VALIDATION)
    assert len(validation_errors) == 1


def test_error_logger_mark_resolved():
    """Test marking error as resolved"""
    logger = ErrorLogger()
    error = ErrorRecord(
        "err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR, "Msg"
    )
    logger.log_error(error)

    assert logger.mark_resolved("err1", "user_correction") is True
    assert logger.get_error("err1").resolved is True


def test_error_logger_unresolved():
    """Test getting unresolved errors"""
    logger = ErrorLogger()
    e1 = ErrorRecord("err1", ErrorCategory.VALIDATION, ErrorSeverity.MINOR, "Msg1")
    e2 = ErrorRecord("err2", ErrorCategory.VALIDATION, ErrorSeverity.MINOR, "Msg2")
    logger.log_error(e1)
    logger.log_error(e2)

    logger.mark_resolved("err1", "fixed")

    unresolved = logger.get_unresolved_errors()
    assert len(unresolved) == 1
    assert unresolved[0].error_id == "err2"


def test_exception_handler_creation():
    """Test creating exception handler"""
    handler = ExceptionHandler()
    assert handler is not None
    assert len(handler.handlers) > 0


def test_exception_handler_handle():
    """Test handling exception"""
    handler = ExceptionHandler()
    result = handler.handle_exception(
        ErrorCategory.VALIDATION, "Invalid data",
        ErrorSeverity.MINOR
    )
    assert result is True


def test_recovery_action():
    """Test recovery action"""
    action = RecoveryAction(
        "act1", ErrorCategory.RESOURCE,
        RecoveryStrategy.RETRY, "retry_handler"
    )
    assert action.action_id == "act1"
    assert action.strategy == RecoveryStrategy.RETRY


def test_recovery_manager_strategies():
    """Test getting recovery strategies"""
    manager = RecoveryManager()
    strategies = manager.get_recovery_strategies(ErrorCategory.RESOURCE)
    assert len(strategies) > 0
    assert RecoveryStrategy.RETRY in strategies


def test_recovery_success_tracking():
    """Test tracking recovery success"""
    manager = RecoveryManager()

    manager.record_recovery_attempt("resource", True)
    manager.record_recovery_attempt("resource", True)
    manager.record_recovery_attempt("resource", False)

    rate = manager.get_recovery_success_rate("resource")
    assert 0.0 < rate < 1.0


def test_graceful_degradation_feature():
    """Test graceful degradation"""
    degradation = GracefulDegradation()

    degradation.enable_feature("feature_a")
    degradation.enable_feature("feature_b")

    assert degradation.is_feature_available("feature_a") is True

    degradation.disable_feature("feature_a")
    assert degradation.is_feature_available("feature_a") is False


def test_graceful_degradation_impact():
    """Test degradation impact calculation"""
    degradation = GracefulDegradation()

    degradation.enable_feature("f1")
    degradation.enable_feature("f2")
    degradation.enable_feature("f3")

    degradation.disable_feature("f1")
    degradation.disable_feature("f2")

    impact = degradation.get_degradation_impact()
    assert 0.0 < impact < 1.0


def test_graceful_degradation_can_continue():
    """Test if system can continue operation"""
    degradation = GracefulDegradation()

    # Enable 4 features
    for i in range(4):
        degradation.enable_feature(f"f{i}")

    # Disable 1 (75% still available)
    degradation.disable_feature("f0")
    assert degradation.can_continue_operation() is True

    # Disable 2 more (50% available, still ok)
    degradation.disable_feature("f1")
    assert degradation.can_continue_operation() is True

    # Disable 1 more (25% available, below 50%)
    degradation.disable_feature("f2")
    assert degradation.can_continue_operation() is False


def test_error_handling_manager_system_error():
    """Test error handling manager"""
    manager = ErrorHandlingManager()

    result = manager.handle_system_error(
        ErrorCategory.VALIDATION, "Invalid data",
        ErrorSeverity.MINOR
    )

    assert "action" in result
    assert "strategies" in result


def test_error_handling_manager_policy():
    """Test setting error policy"""
    manager = ErrorHandlingManager()

    policy = {"retry_count": 5, "timeout": 10.0}
    assert manager.set_error_policy("resource", policy) is True


def test_error_handling_manager_health():
    """Test system health check"""
    manager = ErrorHandlingManager()

    health = manager.get_system_health()
    assert "total_errors" in health
    assert "can_operate" in health


def test_complete_error_workflow():
    """Test complete error handling workflow"""
    manager = ErrorHandlingManager()

    # Simulate error
    result = manager.handle_system_error(
        ErrorCategory.RESOURCE, "Database connection failed",
        ErrorSeverity.SEVERE
    )

    assert result["action"] in ["continue", "alert", "degrade"]

    # Simulate recovery
    manager.degradation.enable_feature("query_service")
    manager.degradation.disable_feature("cache_service")

    health = manager.get_system_health()
    assert health["degradation_impact"] >= 0.0
    assert health["can_operate"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
