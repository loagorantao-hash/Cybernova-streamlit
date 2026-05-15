import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    TRAFFIC_DROP = "traffic_drop"
    ERROR_SPIKE = "error_spike"
    FAILED_LOGINS = "failed_logins"
    REVENUE_DROP = "revenue_drop"
    SLOW_RESPONSE = "slow_response"
    DATA_QUALITY = "data_quality"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    metric_value: float
    threshold: float
    acknowledged: bool = False

class AlertEngine:
    """
    Real-time alert engine for CyberNova
    """
    
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        
        self.thresholds = {
            'traffic_drop_percent': 20,
            'error_rate_percent': 5,
            'failed_login_count': 10,
            'revenue_drop_percent': 15,
            'response_time_ms': 500,
            'missing_values_percent': 10,
        }
    
    def run_all_checks(self) -> List[Alert]:
        self.alerts = []
        try:
            self.check_traffic_drop()
            self.check_error_spike()
            self.check_failed_logins()
            self.check_revenue_drop()
            self.check_slow_response()
            self.check_data_quality()
            logger.info(f"[AlertEngine] Checked all metrics, found {len(self.alerts)} alerts")
        except Exception as e:
            logger.error(f"[AlertEngine] Error running checks: {e}")
        return self.alerts
    
    def check_traffic_drop(self):
        today = datetime.now().date()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        today_data = self.dataset[self.dataset['timestamp'].dt.date == today]
        yesterday_data = self.dataset[self.dataset['timestamp'].dt.date == yesterday]
        today_visits = len(today_data)
        yesterday_visits = len(yesterday_data)
        
        if yesterday_visits > 0:
            drop_percent = ((yesterday_visits - today_visits) / yesterday_visits) * 100
            if drop_percent > self.thresholds['traffic_drop_percent']:
                alert = Alert(
                    id=f"traffic_drop_{datetime.now().timestamp()}",
                    type=AlertType.TRAFFIC_DROP,
                    severity=AlertSeverity.WARNING,
                    title="Traffic Drop Detected",
                    message=f"Traffic dropped {drop_percent:.1f}% compared to yesterday ({today_visits:,} vs {yesterday_visits:,} visits)",
                    timestamp=datetime.now(),
                    metric_value=drop_percent,
                    threshold=self.thresholds['traffic_drop_percent']
                )
                self.alerts.append(alert)
    
    def check_error_spike(self):
        today = datetime.now().date()
        today_data = self.dataset[self.dataset['timestamp'].dt.date == today]
        if len(today_data) > 0 and 'status_code' in today_data:
            error_count = (today_data['status_code'].isin([400, 404, 500])).sum()
            error_rate = (error_count / len(today_data)) * 100
            if error_rate > self.thresholds['error_rate_percent']:
                alert = Alert(
                    id=f"error_spike_{datetime.now().timestamp()}",
                    type=AlertType.ERROR_SPIKE,
                    severity=AlertSeverity.CRITICAL,
                    title="Error Rate Spike",
                    message=f"Error rate at {error_rate:.1f}% ({error_count:,} errors out of {len(today_data):,} requests)",
                    timestamp=datetime.now(),
                    metric_value=error_rate,
                    threshold=self.thresholds['error_rate_percent']
                )
                self.alerts.append(alert)
    
    def check_failed_logins(self):
        failed_login_count = 0
        if failed_login_count > self.thresholds['failed_login_count']:
            alert = Alert(
                id=f"failed_logins_{datetime.now().timestamp()}",
                type=AlertType.FAILED_LOGINS,
                severity=AlertSeverity.CRITICAL,
                title="Security Alert: Failed Logins",
                message=f"{failed_login_count} failed login attempts detected in last hour",
                timestamp=datetime.now(),
                metric_value=failed_login_count,
                threshold=self.thresholds['failed_login_count']
            )
            self.alerts.append(alert)
    
    def check_revenue_drop(self):
        today = datetime.now().date()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        today_data = self.dataset[self.dataset['timestamp'].dt.date == today]
        yesterday_data = self.dataset[self.dataset['timestamp'].dt.date == yesterday]
        if 'revenue_value' in self.dataset:
            today_revenue = today_data['revenue_value'].sum()
            yesterday_revenue = yesterday_data['revenue_value'].sum()
            if yesterday_revenue > 0:
                drop_percent = ((yesterday_revenue - today_revenue) / yesterday_revenue) * 100
                if drop_percent > self.thresholds['revenue_drop_percent']:
                    alert = Alert(
                        id=f"revenue_drop_{datetime.now().timestamp()}",
                        type=AlertType.REVENUE_DROP,
                        severity=AlertSeverity.WARNING,
                        title="Revenue Drop Detected",
                        message=f"Revenue dropped {drop_percent:.1f}% compared to yesterday (${today_revenue:,.2f} vs ${yesterday_revenue:,.2f})",
                        timestamp=datetime.now(),
                        metric_value=drop_percent,
                        threshold=self.thresholds['revenue_drop_percent']
                    )
                    self.alerts.append(alert)
    
    def check_slow_response(self):
        today = datetime.now().date()
        today_data = self.dataset[self.dataset['timestamp'].dt.date == today]
        if len(today_data) > 0 and 'response_time_ms' in today_data:
            avg_response = today_data['response_time_ms'].mean()
            if avg_response > self.thresholds['response_time_ms']:
                alert = Alert(
                    id=f"slow_response_{datetime.now().timestamp()}",
                    type=AlertType.SLOW_RESPONSE,
                    severity=AlertSeverity.WARNING,
                    title="Slow Response Times",
                    message=f"Average response time is {avg_response:.0f}ms (threshold: {self.thresholds['response_time_ms']}ms)",
                    timestamp=datetime.now(),
                    metric_value=avg_response,
                    threshold=self.thresholds['response_time_ms']
                )
                self.alerts.append(alert)
    
    def check_data_quality(self):
        missing_percent = (self.dataset.isna().sum().sum() / (len(self.dataset) * len(self.dataset.columns))) * 100
        if missing_percent > self.thresholds['missing_values_percent']:
            alert = Alert(
                id=f"data_quality_{datetime.now().timestamp()}",
                type=AlertType.DATA_QUALITY,
                severity=AlertSeverity.INFO,
                title="Data Quality Issue",
                message=f"{missing_percent:.1f}% of data contains missing values",
                timestamp=datetime.now(),
                metric_value=missing_percent,
                threshold=self.thresholds['missing_values_percent']
            )
            self.alerts.append(alert)
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts
    
    def acknowledge_alert(self, alert_id: str):
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self.alert_history.append(alert)
                self.alerts.remove(alert)
                break
    
    def get_alert_summary(self) -> Dict[str, int]:
        return {
            'critical': len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]),
            'warning': len([a for a in self.alerts if a.severity == AlertSeverity.WARNING]),
            'info': len([a for a in self.alerts if a.severity == AlertSeverity.INFO]),
            'total': len(self.alerts)
        }
