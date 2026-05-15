import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.analytics.kpi_engine import KPIEngine
import pandas as pd

def test_connection():
    print("Testing Database Connection...")
    try:
        engine = KPIEngine()
        kpis = engine.summary_kpis()
        print(f"Connection Successful!")
        print(f"Total Records: {kpis.get('total_records', 0):,}")
        print(f"Unique Users: {kpis.get('unique_users', 0):,}")
        print(f"Total Revenue: ${kpis.get('revenue', 0):,.2f}")
        
        if kpis.get('total_records', 0) == 0:
            print("WARNING: Database is connected but table 'web_logs' appears empty.")
        else:
            print("SUCCESS: Data is flowing correctly.")
            
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")

if __name__ == "__main__":
    test_connection()
