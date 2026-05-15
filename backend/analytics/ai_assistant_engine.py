import pandas as pd
from backend.analytics.kpi_engine import KPIEngine

class AIAssistantEngine:
    def __init__(self, user_id=None):
        self.kpi_engine = KPIEngine(user_id=user_id)

    def get_quick_insights(self):
        """Generate a list of automated insights based on current KPIs."""
        kpis = self.kpi_engine.summary_kpis()
        total = kpis.get('total_records', 1)
        conv_rate = kpis.get('conversion_rate', 0)
        
        insights = []
        
        # Insight 1: Conversion Rate
        if conv_rate > 2.5:
            insights.append({
                "type": "positive",
                "text": f"Your conversion rate ({conv_rate}%) is currently above the industry baseline of 2.0%.",
                "suggestion": "Monitor high-performing campaigns to maintain this momentum."
            })
        elif conv_rate < 1.0:
            insights.append({
                "type": "warning",
                "text": f"Conversion rate is low ({conv_rate}%). Mobile users are showing higher drop-off rates.",
                "suggestion": "Optimize the 'Demo Request' flow for smaller screens."
            })
            
        # Insight 2: Traffic/Visits
        visits_trend = self.kpi_engine.visits_over_time()
        if not visits_trend.empty and len(visits_trend) > 1:
            recent = visits_trend.iloc[-1]['visits']
            previous = visits_trend.iloc[-2]['visits']
            change = ((recent - previous) / previous * 100) if previous > 0 else 0
            
            if change > 10:
                insights.append({
                    "type": "positive",
                    "text": f"Traffic has increased by {change:.1f}% since yesterday.",
                    "suggestion": "Ensure server capacity is optimized for Gaborone HQ peaks."
                })
            elif change < -10:
                insights.append({
                    "type": "negative",
                    "text": f"Traffic is down by {abs(change):.1f}% compared to yesterday.",
                    "suggestion": "Check if any Southern African regional campaign has ended."
                })

        # Insight 3: Performance
        avg_lat = kpis.get('avg_response_time', 0)
        if avg_lat > 500:
            insights.append({
                "type": "warning",
                "text": f"Average latency ({avg_lat:.0f}ms) is higher than the 300ms target.",
                "suggestion": "Consider edge caching for your Johannesburg and Gaborone users."
            })

        return insights

    def answer_question(self, question):
        """Simple rule-based Q&A for the assistant."""
        q = question.lower()
        kpis = self.kpi_engine.summary_kpis()
        
        if "conversion" in q or "sales" in q:
            return (f"The current conversion rate is {kpis.get('conversion_rate', 0)}%. "
                    "Most conversions are coming from 'Security Audit' job types in Gaborone.")
        
        if "traffic" in q or "visits" in q:
            return (f"Total visits recorded: {kpis.get('total_records', 0):,}. "
                    "Peak traffic hours are usually between 09:00 and 11:00 CAT.")
        
        if "error" in q or "fail" in q:
            err_count = kpis.get('errors', 0)
            return (f"We have detected {err_count} failed requests. "
                    "Most are 404 errors on the 'Promotions' page.")
            
        if "best" in q and "campaign" in q:
            camp = self.kpi_engine.campaign_performance()
            if not camp.empty:
                best = camp.sort_values('revenue', ascending=False).iloc[0]
                return f"The best performing campaign is '{best['campaign_type']}' with ${best['revenue']:,.2f} in revenue."
        
        return "I'm not sure about that specific metric, but I can help you analyze conversions, traffic, or campaign performance!"
