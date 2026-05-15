import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LiveEngine:
    """
    Smart auto-refresh engine for CyberNova dashboards
    """
    
    def __init__(self, dataset: pd.DataFrame, refresh_interval: int = 5):
        self.dataset = dataset # Fallback/Initial dataset
        self.refresh_interval = refresh_interval
        self.last_refresh = datetime.now()
        self.refresh_count = 0
        self.performance_metrics = []
        
    def _get_live_df(self, query: str) -> pd.DataFrame:
        try:
            from backend.database.connection import get_engine
            engine = get_engine()
            df = pd.read_sql(query, con=engine)
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            return df
        except Exception as e:
            logger.error(f"Failed to fetch live data: {e}")
            return pd.DataFrame()
        
    def should_refresh(self) -> bool:
        if not st.session_state.get('live_mode', False):
            return False
        elapsed = (datetime.now() - self.last_refresh).total_seconds()
        return elapsed >= self.refresh_interval
    
    def refresh_kpis(self, role: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            if role == 'website_user':
                kpis = self._refresh_user_kpis(user_id)
            elif role == 'analyst':
                kpis = self._refresh_analyst_kpis()
            elif role == 'admin':
                kpis = self._refresh_admin_kpis()
            else:
                kpis = {}
            
            kpis['_meta'] = {
                'timestamp': datetime.now().isoformat(),
                'refresh_count': self.refresh_count,
                'elapsed_ms': int((time.time() - start_time) * 1000)
            }
            
            self.last_refresh = datetime.now()
            self.refresh_count += 1
            
            self.performance_metrics.append({
                'timestamp': datetime.now(),
                'duration_ms': kpis['_meta']['elapsed_ms'],
                'role': role
            })
            return kpis
        except Exception as e:
            logger.error(f"[LiveEngine] Refresh failed: {e}")
            return {'error': str(e)}
    
    def _refresh_user_kpis(self, user_id: int) -> Dict[str, Any]:
        if user_id is None:
            return {}
        
        # We don't have user_id in web_logs natively, so we map by ip_address or just return 0 if no clear link
        # For now, we'll return zeroes or gracefully handle it to avoid KeyError
        return {
            'sessions_today': 0,
            'total_sessions': 0,
            'conversions_today': 0,
            'revenue_today': 0,
            'last_activity': None,
            'active_now': False
        }
    
    def _refresh_analyst_kpis(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime('%Y-%m-%d 00:00:00')
        hour_ago_str = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Fetch today's data from SQLite for live accuracy
        today_data = self._get_live_df(f"SELECT * FROM web_logs WHERE timestamp >= '{today_str}'")
        
        if today_data.empty:
            return {
                'visits_today': 0, 'visits_last_hour': 0, 'conversions_today': 0,
                'revenue_today': 0, 'conversion_rate': 0, 'avg_response_time': 0,
                'error_rate': 0, 'active_users': 0, 'top_service': None
            }
            
        recent_data = today_data[today_data['timestamp'] >= pd.to_datetime(hour_ago_str)]
        
        return {
            'visits_today': len(today_data),
            'visits_last_hour': len(recent_data),
            'conversions_today': today_data['conversion_flag'].sum() if 'conversion_flag' in today_data.columns else 0,
            'revenue_today': today_data['revenue'].sum() if 'revenue' in today_data.columns else (today_data['revenue_value'].sum() if 'revenue_value' in today_data.columns else 0),
            'conversion_rate': (
                today_data['conversion_flag'].sum() / len(today_data) * 100
                if len(today_data) > 0 and 'conversion_flag' in today_data.columns else 0
            ),
            'avg_response_time': today_data['bytes_sent'].mean() if 'bytes_sent' in today_data.columns else 0,
            'error_rate': (
                (today_data['status_code'].isin([400, 404, 500])).sum() / len(today_data) * 100
                if len(today_data) > 0 and 'status_code' in today_data.columns else 0
            ),
            'active_users': self._count_active_users_live(),
            'top_service': today_data['service_type'].mode()[0] if len(today_data) > 0 and 'service_type' in today_data.columns else None
        }
    
    def _refresh_admin_kpis(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime('%Y-%m-%d 00:00:00')
        today_data = self._get_live_df(f"SELECT status_code, bytes_sent FROM web_logs WHERE timestamp >= '{today_str}'")
        
        # Get total records quickly
        total_records_df = self._get_live_df("SELECT COUNT(*) as total FROM web_logs")
        total_records = total_records_df['total'].iloc[0] if not total_records_df.empty else 0
        
        return {
            'total_records': total_records,
            'records_today': len(today_data),
            'active_users_now': self._count_active_users_live(),
            'failed_logins': self._count_failed_logins(),
            'error_count': (today_data['status_code'].isin([400, 404, 500])).sum() if 'status_code' in today_data.columns else 0,
            'avg_response_time': today_data['bytes_sent'].mean() if 'bytes_sent' in today_data.columns else 0,
            'uploads_today': 0, 
            'system_health': self._get_system_health()
        }
    
    def _is_user_active(self, user_id: int) -> bool:
        cutoff = datetime.now() - timedelta(minutes=5)
        recent = self.dataset[
            (self.dataset['user_id'] == user_id) &
            (self.dataset['timestamp'] >= cutoff)
        ]
        return len(recent) > 0
    
    def _count_active_users_live(self) -> int:
        five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        df = self._get_live_df(f"SELECT COUNT(DISTINCT ip_address) as active FROM web_logs WHERE timestamp >= '{five_mins_ago}'")
        return df['active'].iloc[0] if not df.empty else 0
        
    def _count_active_users(self) -> int:
        return self._count_active_users_live()
    
    def _count_failed_logins(self) -> int:
        return 0
    
    def _get_system_health(self) -> Dict[str, Any]:
        from backend.analytics.performance_monitor import get_system_metrics
        return get_system_metrics()
    
    def refresh_charts(self, chart_type: str, filters: Dict[str, Any] = None) -> pd.DataFrame:
        filtered_data = self.dataset.copy()
        if filters:
            if 'date_from' in filters:
                filtered_data = filtered_data[filtered_data['timestamp'] >= pd.to_datetime(filters['date_from'])]
            if 'date_to' in filters:
                filtered_data = filtered_data[filtered_data['timestamp'] <= pd.to_datetime(filters['date_to'])]
            if 'countries' in filters:
                filtered_data = filtered_data[filtered_data['country'].isin(filters['countries'])]
        
        if chart_type == 'revenue_trend' and 'revenue_value' in filtered_data:
            return filtered_data.groupby(filtered_data['timestamp'].dt.date)['revenue_value'].sum().reset_index()
        elif chart_type == 'traffic':
            return filtered_data.groupby(filtered_data['timestamp'].dt.date).size().reset_index(name='visits')
        elif chart_type == 'geographic':
            return filtered_data['country'].value_counts().reset_index()
        else:
            return filtered_data
    
    def refresh_system_health(self) -> Dict[str, Any]:
        return self._get_system_health()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        if not self.performance_metrics:
            return {}
        recent = [m['duration_ms'] for m in self.performance_metrics[-10:]]
        return {
            'total_refreshes': self.refresh_count,
            'avg_refresh_time_ms': sum(recent) / len(recent) if recent else 0,
            'max_refresh_time_ms': max(recent) if recent else 0,
            'min_refresh_time_ms': min(recent) if recent else 0
        }

def enable_auto_refresh(interval_seconds: int = 5):
    if st.session_state.get('live_mode', False):
        time.sleep(interval_seconds)
        st.rerun()

