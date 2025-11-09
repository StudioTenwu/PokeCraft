"""
Round 50: Admin Dashboard & Monitoring
System administration, monitoring, analytics, and management capabilities.
Features: analytics, alerts, logs, system health, performance monitoring, user management.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class AlertLevel(Enum):
    """Severity of system alert"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Type of metric being tracked"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERROR = "error"
    DEPLOYMENT = "deployment"
    AGENT = "agent"
    SYSTEM = "system"


@dataclass
class SystemAlert:
    """Alert for system administrators"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    affected_component: str
    timestamp: float = 0.0
    resolved: bool = False
    resolution_time: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "component": self.affected_component,
            "resolved": self.resolved
        }


@dataclass
class SystemMetric:
    """System performance metric"""
    metric_id: str
    metric_type: MetricType
    metric_name: str
    value: float  # 0.0-1.0 normalized
    timestamp: float = 0.0
    threshold_warning: float = 0.7
    threshold_critical: float = 0.9
    dimension: str = ""  # e.g., agent_id, component_name

    def get_alert_level(self) -> Optional[AlertLevel]:
        """Get alert level based on metric value"""
        if self.value >= self.threshold_critical:
            return AlertLevel.CRITICAL
        elif self.value >= self.threshold_warning:
            return AlertLevel.WARNING
        return None

    def to_dict(self) -> Dict:
        return {
            "id": self.metric_id,
            "type": self.metric_type.value,
            "name": self.metric_name,
            "value": round(self.value, 3),
            "alert": self.get_alert_level().value if self.get_alert_level() else None
        }


@dataclass
class SystemLog:
    """System activity log entry"""
    log_id: str
    timestamp: float
    log_level: AlertLevel
    component: str
    message: str
    user_id: str = ""
    action: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.log_id,
            "timestamp": self.timestamp,
            "level": self.log_level.value,
            "component": self.component,
            "message": self.message,
            "action": self.action
        }


@dataclass
class SystemHealth:
    """Overall system health status"""
    health_score: float = 1.0  # 0.0-1.0
    component_health: Dict[str, float] = field(default_factory=dict)  # component -> health
    active_alerts: int = 0
    critical_alerts: int = 0
    uptime_percent: float = 100.0
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    memory_usage_percent: float = 0.0
    last_update: float = 0.0

    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.health_score >= 0.7 and self.critical_alerts == 0

    def to_dict(self) -> Dict:
        return {
            "health_score": round(self.health_score, 2),
            "is_healthy": self.is_healthy(),
            "active_alerts": self.active_alerts,
            "critical": self.critical_alerts,
            "uptime": round(self.uptime_percent, 1),
            "error_rate": round(self.error_rate, 3)
        }


class AlertManager:
    """Manages system alerts"""

    def __init__(self):
        self.alerts: Dict[str, SystemAlert] = {}
        self.active_alerts: List[str] = []

    def create_alert(self, alert: SystemAlert) -> bool:
        """Create new alert"""
        if alert.alert_id in self.alerts:
            return False

        self.alerts[alert.alert_id] = alert
        self.active_alerts.append(alert.alert_id)
        return True

    def resolve_alert(self, alert_id: str, resolution_time: float = 0.0) -> bool:
        """Mark alert as resolved"""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.resolved = True
        alert.resolution_time = resolution_time

        if alert_id in self.active_alerts:
            self.active_alerts.remove(alert_id)

        return True

    def get_active_alerts(self) -> List[SystemAlert]:
        """Get all active (unresolved) alerts"""
        return [self.alerts[aid] for aid in self.active_alerts if aid in self.alerts]

    def get_alerts_by_level(self, level: AlertLevel) -> List[SystemAlert]:
        """Get alerts by severity level"""
        return [a for a in self.alerts.values() if a.level == level]

    def get_alert_count(self) -> int:
        """Get total unresolved alert count"""
        return len(self.active_alerts)

    def get_critical_alert_count(self) -> int:
        """Get critical unresolved alert count"""
        return len([a for a in self.get_active_alerts() if a.level == AlertLevel.CRITICAL])

    def to_dict(self) -> Dict:
        return {
            "total_alerts": len(self.alerts),
            "active": len(self.active_alerts),
            "critical": self.get_critical_alert_count()
        }


class MetricsCollector:
    """Collects and aggregates system metrics"""

    def __init__(self):
        self.metrics: Dict[str, SystemMetric] = {}
        self.metric_history: Dict[str, List[float]] = {}  # metric_name -> values

    def record_metric(self, metric: SystemMetric) -> bool:
        """Record system metric"""
        if metric.metric_id in self.metrics:
            return False

        self.metrics[metric.metric_id] = metric

        if metric.metric_name not in self.metric_history:
            self.metric_history[metric.metric_name] = []
        self.metric_history[metric.metric_name].append(metric.value)

        # Keep last 100 readings
        if len(self.metric_history[metric.metric_name]) > 100:
            self.metric_history[metric.metric_name] = self.metric_history[metric.metric_name][-100:]

        return True

    def get_metric(self, metric_id: str) -> Optional[SystemMetric]:
        """Get metric by ID"""
        return self.metrics.get(metric_id)

    def get_latest_metrics(self, metric_type: MetricType) -> List[SystemMetric]:
        """Get latest metrics of type"""
        return sorted(
            [m for m in self.metrics.values() if m.metric_type == metric_type],
            key=lambda m: m.timestamp,
            reverse=True
        )

    def get_metric_average(self, metric_name: str) -> float:
        """Get average value of metric"""
        if metric_name not in self.metric_history:
            return 0.0

        values = self.metric_history[metric_name]
        if not values:
            return 0.0

        return sum(values) / len(values)

    def get_metric_stats(self, metric_name: str) -> Dict:
        """Get statistics for metric"""
        if metric_name not in self.metric_history:
            return {}

        values = self.metric_history[metric_name]
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1]
        }

    def to_dict(self) -> Dict:
        return {
            "total_metrics": len(self.metrics),
            "unique_metrics": len(self.metric_history),
            "measurements": sum(len(v) for v in self.metric_history.values())
        }


class SystemLogger:
    """Logs system activities"""

    def __init__(self):
        self.logs: Dict[str, SystemLog] = {}
        self.logs_by_component: Dict[str, List[str]] = {}  # component -> log_ids

    def log_activity(self, log: SystemLog) -> bool:
        """Log activity"""
        if log.log_id in self.logs:
            return False

        self.logs[log.log_id] = log

        if log.component not in self.logs_by_component:
            self.logs_by_component[log.component] = []
        self.logs_by_component[log.component].append(log.log_id)

        return True

    def get_logs(self, component: Optional[str] = None, limit: int = 100) -> List[SystemLog]:
        """Get logs, optionally filtered by component"""
        if component:
            if component not in self.logs_by_component:
                return []
            log_ids = self.logs_by_component[component][-limit:]
            return [self.logs[lid] for lid in log_ids if lid in self.logs]

        # Get all logs sorted by timestamp
        all_logs = sorted(self.logs.values(), key=lambda l: l.timestamp, reverse=True)
        return all_logs[:limit]

    def get_logs_by_level(self, level: AlertLevel) -> List[SystemLog]:
        """Get logs by level"""
        return [l for l in self.logs.values() if l.log_level == level]

    def to_dict(self) -> Dict:
        return {
            "total_logs": len(self.logs),
            "components": len(self.logs_by_component),
            "critical_logs": len(self.get_logs_by_level(AlertLevel.CRITICAL))
        }


class AdminDashboard:
    """Central admin dashboard for system monitoring"""

    def __init__(self):
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector()
        self.system_logger = SystemLogger()
        self.system_health = SystemHealth()

    def update_system_health(self) -> SystemHealth:
        """Update overall system health status"""
        # Aggregate component health from metrics
        component_health = {}
        for metric in self.metrics_collector.metrics.values():
            if metric.dimension:
                avg = self.metrics_collector.get_metric_average(metric.metric_name)
                component_health[metric.dimension] = 1.0 - avg  # Invert so high is good

        self.system_health.component_health = component_health

        # Calculate overall health score
        if component_health:
            self.system_health.health_score = sum(component_health.values()) / len(component_health)
        else:
            self.system_health.health_score = 1.0

        # Factor in alerts
        self.system_health.active_alerts = self.alert_manager.get_alert_count()
        self.system_health.critical_alerts = self.alert_manager.get_critical_alert_count()

        if self.system_health.critical_alerts > 0:
            self.system_health.health_score *= 0.5

        return self.system_health

    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        self.update_system_health()

        return {
            "health": self.system_health.to_dict(),
            "alerts": {
                "active": len(self.alert_manager.active_alerts),
                "critical": self.alert_manager.get_critical_alert_count(),
                "recent": [a.to_dict() for a in self.alert_manager.get_active_alerts()[:5]]
            },
            "metrics": {
                "total_recorded": len(self.metrics_collector.metrics),
                "latest": [m.to_dict() for m in self.metrics_collector.metrics.values()][:10]
            },
            "logs": {
                "total": len(self.system_logger.logs),
                "recent": [l.to_dict() for l in self.system_logger.get_logs(limit=10)]
            },
            "components": self.system_health.component_health
        }

    def record_alert(self, alert: SystemAlert) -> bool:
        """Record system alert"""
        return self.alert_manager.create_alert(alert)

    def record_metric(self, metric: SystemMetric) -> bool:
        """Record system metric"""
        return self.metrics_collector.record_metric(metric)

    def record_log(self, log: SystemLog) -> bool:
        """Record activity log"""
        return self.system_logger.log_activity(log)

    def to_dict(self) -> Dict:
        return {
            "alerts": self.alert_manager.to_dict(),
            "metrics": self.metrics_collector.to_dict(),
            "logs": self.system_logger.to_dict(),
            "health": self.system_health.to_dict()
        }


# ===== Tests =====

def test_system_alert_creation():
    """Test creating system alert"""
    alert = SystemAlert(
        "alr1", AlertLevel.WARNING, "High Memory Usage",
        "Memory usage exceeds 80%", "memory_system"
    )
    assert alert.alert_id == "alr1"
    assert alert.resolved is False


def test_system_metric_creation():
    """Test creating system metric"""
    metric = SystemMetric(
        "met1", MetricType.PERFORMANCE, "cpu_usage",
        0.75, dimension="agent1"
    )
    assert metric.metric_id == "met1"
    assert metric.value == 0.75


def test_metric_alert_level():
    """Test metric alert level"""
    metric = SystemMetric(
        "met1", MetricType.PERFORMANCE, "cpu_usage",
        0.95  # Above critical threshold
    )
    assert metric.get_alert_level() == AlertLevel.CRITICAL

    metric.value = 0.75  # Above warning
    assert metric.get_alert_level() == AlertLevel.WARNING

    metric.value = 0.5  # Below warning
    assert metric.get_alert_level() is None


def test_alert_manager_create():
    """Test alert manager"""
    manager = AlertManager()
    alert = SystemAlert(
        "alr1", AlertLevel.ERROR, "API Down",
        "API server is not responding", "api_service"
    )
    assert manager.create_alert(alert) is True


def test_alert_manager_resolve():
    """Test resolving alert"""
    manager = AlertManager()
    alert = SystemAlert(
        "alr1", AlertLevel.WARNING, "Test", "Test alert", "test"
    )
    manager.create_alert(alert)

    assert manager.resolve_alert("alr1", 300.0) is True
    assert manager.get_alert_count() == 0


def test_alert_manager_active():
    """Test getting active alerts"""
    manager = AlertManager()

    a1 = SystemAlert("alr1", AlertLevel.WARNING, "Alert 1", "Msg", "comp1")
    a2 = SystemAlert("alr2", AlertLevel.ERROR, "Alert 2", "Msg", "comp2")

    manager.create_alert(a1)
    manager.create_alert(a2)

    active = manager.get_active_alerts()
    assert len(active) == 2

    manager.resolve_alert("alr1")
    active = manager.get_active_alerts()
    assert len(active) == 1


def test_metrics_collector_record():
    """Test metrics collector"""
    collector = MetricsCollector()
    metric = SystemMetric(
        "met1", MetricType.PERFORMANCE, "cpu_usage",
        0.65
    )
    assert collector.record_metric(metric) is True


def test_metrics_collector_average():
    """Test metric averaging"""
    collector = MetricsCollector()

    m1 = SystemMetric("m1", MetricType.PERFORMANCE, "cpu", 0.5)
    m2 = SystemMetric("m2", MetricType.PERFORMANCE, "cpu", 0.6)
    m3 = SystemMetric("m3", MetricType.PERFORMANCE, "cpu", 0.7)

    collector.record_metric(m1)
    collector.record_metric(m2)
    collector.record_metric(m3)

    avg = collector.get_metric_average("cpu")
    assert avg == 0.6


def test_metrics_collector_stats():
    """Test metric statistics"""
    collector = MetricsCollector()

    for i in range(5):
        m = SystemMetric(
            f"m{i}", MetricType.PERFORMANCE, "cpu",
            0.5 + (i * 0.1)
        )
        collector.record_metric(m)

    stats = collector.get_metric_stats("cpu")
    assert stats["count"] == 5
    assert stats["min"] == 0.5
    assert stats["max"] == 0.9


def test_system_log_creation():
    """Test creating system log"""
    log = SystemLog(
        "log1", 1000.0, AlertLevel.INFO,
        "agent_system", "Agent deployed successfully"
    )
    assert log.log_id == "log1"


def test_system_logger():
    """Test system logger"""
    logger = SystemLogger()
    log = SystemLog(
        "log1", 1000.0, AlertLevel.INFO,
        "test", "Test log message"
    )
    assert logger.log_activity(log) is True


def test_system_logger_by_component():
    """Test filtering logs by component"""
    logger = SystemLogger()

    l1 = SystemLog("log1", 1000.0, AlertLevel.INFO, "comp1", "Msg1")
    l2 = SystemLog("log2", 1001.0, AlertLevel.INFO, "comp2", "Msg2")
    l3 = SystemLog("log3", 1002.0, AlertLevel.INFO, "comp1", "Msg3")

    logger.log_activity(l1)
    logger.log_activity(l2)
    logger.log_activity(l3)

    comp1_logs = logger.get_logs("comp1")
    assert len(comp1_logs) == 2


def test_system_health():
    """Test system health"""
    health = SystemHealth()
    assert health.is_healthy() is True

    health.critical_alerts = 1
    assert health.is_healthy() is False


def test_admin_dashboard_record():
    """Test admin dashboard"""
    dashboard = AdminDashboard()

    alert = SystemAlert(
        "alr1", AlertLevel.WARNING, "Test", "Test alert", "test"
    )
    assert dashboard.record_alert(alert) is True

    metric = SystemMetric(
        "met1", MetricType.PERFORMANCE, "cpu", 0.75
    )
    assert dashboard.record_metric(metric) is True

    log = SystemLog(
        "log1", 1000.0, AlertLevel.INFO, "test", "Test log"
    )
    assert dashboard.record_log(log) is True


def test_admin_dashboard_health():
    """Test dashboard health update"""
    dashboard = AdminDashboard()

    m1 = SystemMetric("m1", MetricType.PERFORMANCE, "cpu", 0.6, dimension="comp1")
    m2 = SystemMetric("m2", MetricType.PERFORMANCE, "cpu", 0.7, dimension="comp2")

    dashboard.record_metric(m1)
    dashboard.record_metric(m2)

    health = dashboard.update_system_health()
    assert health.health_score > 0.0
    assert health.health_score <= 1.0


def test_admin_dashboard_data():
    """Test getting dashboard data"""
    dashboard = AdminDashboard()

    # Add some data
    alert = SystemAlert("alr1", AlertLevel.WARNING, "Test", "Alert", "test")
    dashboard.record_alert(alert)

    metric = SystemMetric("m1", MetricType.PERFORMANCE, "cpu", 0.75)
    dashboard.record_metric(metric)

    log = SystemLog("log1", 1000.0, AlertLevel.INFO, "test", "Log")
    dashboard.record_log(log)

    data = dashboard.get_dashboard_data()
    assert "health" in data
    assert "alerts" in data
    assert "metrics" in data
    assert "logs" in data


def test_complete_admin_workflow():
    """Test complete admin dashboard workflow"""
    dashboard = AdminDashboard()

    # System starts healthy
    health = dashboard.update_system_health()
    assert health.is_healthy() is True

    # High CPU alert
    alert1 = SystemAlert(
        "alr1", AlertLevel.WARNING, "High CPU",
        "CPU usage is 85%", "cpu"
    )
    dashboard.record_alert(alert1)

    # Record CPU metric
    metric = SystemMetric(
        "m1", MetricType.PERFORMANCE, "cpu_usage",
        0.85, dimension="cpu"
    )
    dashboard.record_metric(metric)

    # Log the issue
    log = SystemLog(
        "log1", 1000.0, AlertLevel.WARNING,
        "cpu", "High CPU detected", action="auto_scale"
    )
    dashboard.record_log(log)

    # Check dashboard
    data = dashboard.get_dashboard_data()
    assert data["alerts"]["active"] >= 1
    assert len(data["logs"]["recent"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
