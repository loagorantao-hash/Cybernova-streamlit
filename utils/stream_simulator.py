import random
from datetime import datetime
import pandas as pd

def generate_synthetic_event() -> dict:
    """Generates a synthetic web log event for live testing."""
    return {
        "timestamp": datetime.now(),
        "user_id": random.randint(1000, 5000),
        "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
        "uri": random.choice(["/api/v1/auth", "/checkout", "/dashboard", "/products"]),
        "status_code": random.choices([200, 201, 400, 401, 403, 404, 500], weights=[70, 10, 5, 2, 2, 5, 1])[0],
        "bytes_sent": random.randint(500, 50000),
        "user_agent": "Mozilla/5.0 StreamSimulator",
        "response_time_ms": random.randint(20, 1500),
        "session_id": f"sess_{random.randint(10000, 99999)}",
        "country": random.choice(["USA", "UK", "Canada", "Germany", "France"]),
        "service_name": random.choice(["AuthService", "PaymentGate", "WebFrontend"]),
        "activity_type": "web_request",
        "conversion_flag": random.choices([0, 1], weights=[95, 5])[0],
        "revenue_value": float(random.randint(10, 500)) if random.random() < 0.05 else 0.0
    }

def simulate_burst(count: int = 10) -> pd.DataFrame:
    """Returns a dataframe of recent synthetic events."""
    events = [generate_synthetic_event() for _ in range(count)]
    return pd.DataFrame(events)
