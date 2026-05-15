import pandas as pd
from backend.analytics.filter_engine import get_filter_options

# Mock data where timestamp is a string
df = pd.DataFrame({
    "timestamp": ["2026-05-14 10:00:00", "2026-05-14 11:00:00"],
    "country": ["USA", "UK"],
    "service_type": ["API", "Web"],
    "status_code": [200, 404],
    "method": ["GET", "POST"],
    "campaign_id": ["C1", "C2"]
})

print("Testing get_filter_options with string timestamps...")
try:
    opts = get_filter_options(df)
    print("Success! date_min:", opts["date_min"])
    print("Success! date_max:", opts["date_max"])
except Exception as e:
    print("Failed!", e)
