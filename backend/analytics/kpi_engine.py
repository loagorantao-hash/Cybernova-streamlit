import pandas as pd
from typing import Optional
from backend.database.queries import get_dataframe, run_query

class KPIEngine:
    """Calculates KPIs directly from the SQLite database using SQL."""

    def __init__(self, user_id=None):
        """
        user_id: integer from the users table (1, 2, 3 …)
        web_logs.user_id stores strings like 'USER_1', so we cannot
        do a direct equality match. For personal dashboards we show
        all data (no per-user filter) since there is no FK link.
        """
        self.user_id = user_id
        # web_logs.user_id has no FK to users.id — no reliable filter.
        self.base_where = ""
        self.and_where = ""

    def summary_kpis(self) -> dict:
        # DB columns: http_status, revenue_value, response_time_ms, lead_flag, conversion_flag, user_id (TEXT)
        sql = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(revenue_value) as revenue,
                SUM(lead_flag) as leads,
                SUM(conversion_flag) as conversions,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN http_status >= 400 THEN 1 ELSE 0 END) as errors
            FROM web_logs
            {self.base_where}
        """
        result = run_query(sql)
        if not result or result[0]['total_records'] == 0:
            return {
                "total_records": 0, "unique_users": 0, "revenue": 0.0,
                "leads": 0, "conversions": 0, "conversion_rate": 0.0,
                "avg_response_time": 0.0, "errors": 0, "error_rate": 0.0
            }
        
        row = result[0]
        total = row['total_records'] or 0
        conversions = row['conversions'] or 0
        errors = row['errors'] or 0
        
        return {
            "total_records": total,
            "unique_users": row['unique_users'] or 0,
            "revenue": row['revenue'] or 0.0,
            "leads": row['leads'] or 0,
            "conversions": conversions,
            "conversion_rate": round((conversions / total) * 100, 2) if total > 0 else 0.0,
            "avg_response_time": round(row['avg_response_time'] or 0.0, 2),
            "errors": errors,
            "error_rate": round((errors / total) * 100, 2) if total > 0 else 0.0
        }

    # ── FR1: Product/Service Performance ─────────────────────────────────────
    def service_usage_frequency(self, top_n: int = 10) -> pd.DataFrame:
        sql = f"""
            SELECT service_name, COUNT(*) as visit_count
            FROM web_logs
            {self.base_where}
            GROUP BY service_name
            ORDER BY visit_count DESC
            LIMIT {top_n}
        """
        return get_dataframe(sql)

    def service_revenue(self, top_n: int = 10) -> pd.DataFrame:
        sql = f"""
            SELECT service_name, SUM(revenue_value) as total_revenue
            FROM web_logs
            {self.base_where}
            GROUP BY service_name
            ORDER BY total_revenue DESC
            LIMIT {top_n}
        """
        return get_dataframe(sql)

    # ── FR2: Sales Effectiveness ──────────────────────────────────────────────
    def sales_funnel(self) -> pd.DataFrame:
        # Funnel stages: Total Visits -> Leads -> Conversions
        kpis = self.summary_kpis()
        return pd.DataFrame({
            "stage": ["Total Visitors", "Leads (Expressed Interest)", "Converted"],
            "count": [kpis["total_records"], kpis["leads"], kpis["conversions"]],
        })

    def demo_conversion_ratio(self) -> dict:
        sql = f"""
            SELECT 
                COUNT(*) as total_demos,
                SUM(conversion_flag) as conversions
            FROM web_logs
            WHERE activity_type LIKE '%demo%'
            {self.and_where}
        """
        result = run_query(sql)
        row = result[0] if result else {'total_demos': 0, 'conversions': 0}
        total_demos = row['total_demos'] or 0
        conversions = row['conversions'] or 0
        return {
            "total_demos": total_demos,
            "conversions": conversions,
            "conversion_rate": round((conversions / total_demos) * 100, 2) if total_demos > 0 else 0.0
        }

    # ── FR3: Marketing Effectiveness ─────────────────────────────────────────
    def campaign_performance(self) -> pd.DataFrame:
        sql = f"""
            SELECT 
                campaign_type,
                COUNT(*) as visits,
                SUM(conversion_flag) as conversions,
                SUM(revenue_value) as revenue
            FROM web_logs
            {self.base_where}
            GROUP BY campaign_type
            ORDER BY revenue DESC
        """
        df = get_dataframe(sql)
        if not df.empty:
            df["conversion_rate"] = (df["conversions"] / df["visits"] * 100).round(2)
        return df

    # ── Time series ───────────────────────────────────────────────────────────
    def visits_over_time(self) -> pd.DataFrame:
        # Group by Date (YYYY-MM-DD)
        sql = f"""
            SELECT date(timestamp) as date, COUNT(*) as visits
            FROM web_logs
            {self.base_where}
            GROUP BY date(timestamp)
            ORDER BY date(timestamp)
        """
        return get_dataframe(sql)

    def revenue_over_time(self) -> pd.DataFrame:
        sql = f"""
            SELECT date(timestamp) as date, SUM(revenue_value) as revenue
            FROM web_logs
            {self.base_where}
            GROUP BY date(timestamp)
            ORDER BY date(timestamp)
        """
        return get_dataframe(sql)

    def hourly_distribution(self) -> pd.DataFrame:
        # SQLite extracts hour using strftime
        sql = f"""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as visits
            FROM web_logs
            {self.base_where}
            GROUP BY hour
            ORDER BY hour
        """
        return get_dataframe(sql)

    def status_code_distribution(self) -> pd.DataFrame:
        # DB column is 'http_status'
        sql = f"""
            SELECT 
                CASE 
                    WHEN http_status >= 200 AND http_status < 300 THEN '2xx Success'
                    WHEN http_status >= 300 AND http_status < 400 THEN '3xx Redirect'
                    WHEN http_status >= 400 AND http_status < 500 THEN '4xx Client Error'
                    WHEN http_status >= 500 THEN '5xx Server Error'
                    ELSE 'Unknown'
                END as status_category,
                COUNT(*) as count
            FROM web_logs
            {self.base_where}
            GROUP BY status_category
        """
        return get_dataframe(sql)

    # ── Specialized Business Case Metrics (CyberNova Gaborone) ────────────────
    
    def jobs_analysis(self) -> pd.DataFrame:
        """Report on Job Types Requested (Service Names)."""
        sql = f"""
            SELECT service_name as job_type, COUNT(*) as request_count
            FROM web_logs
            {self.base_where}
            GROUP BY service_name
            ORDER BY request_count DESC
        """
        return get_dataframe(sql)

    def cyber_assistant_metrics(self) -> dict:
        """Track usage of the AI Assistant and Demo requests."""
        sql = f"""
            SELECT 
                SUM(CASE WHEN activity_type = 'AI_ASSISTANT' THEN 1 ELSE 0 END) as assistant_uses,
                SUM(CASE WHEN activity_type = 'DEMO_REQUEST' THEN 1 ELSE 0 END) as demo_requests,
                SUM(CASE WHEN activity_type = 'EVENT_PARTICIPATION' THEN 1 ELSE 0 END) as event_participants
            FROM web_logs
            {self.base_where}
        """
        result = run_query(sql)
        return result[0] if result else {"assistant_uses": 0, "demo_requests": 0, "event_participants": 0}

    def geo_distribution(self, top_n: int = 30) -> pd.DataFrame:
        """Return visit/conversion/revenue counts by location (DB column is 'location')."""
        sql = f"""
            SELECT
                location as country,
                COUNT(*) as visits,
                SUM(conversion_flag) as conversions,
                SUM(revenue_value) as revenue
            FROM web_logs
            {self.base_where}
            GROUP BY location
            ORDER BY visits DESC
            LIMIT {top_n}
        """
        return get_dataframe(sql)
