from backend.analytics.performance_monitor import get_system_metrics

class MonitoringService:
    """
    Service for monitoring system health.
    Wraps the underlying performance_monitor for the Live Real-Time Upgrade v8.0.
    """
    @staticmethod
    def get_health() -> dict:
        return get_system_metrics()
