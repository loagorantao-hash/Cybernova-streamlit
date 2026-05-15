import time
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.connection import get_engine
from backend.analytics.performance_monitor import get_system_metrics

def benchmark():
    print("--- CyberNova Enterprise Performance Audit ---")
    
    # 1. System Health Audit
    metrics = get_system_metrics()
    print(f"DB Health: {metrics.get('db_health')}")
    print(f"Row Count: {metrics.get('row_count'):,}")
    print(f"DB Size: {metrics.get('db_size_mb'):.2f} MB")
    print(f"WAL Mode: {metrics.get('wal_status')}")
    
    # 2. Raw Query Performance (Full Scan)
    engine = get_engine()
    print("\nMeasuring Load Time (500k rows)...")
    start = time.perf_counter()
    df = pd.read_sql("SELECT * FROM web_logs", con=engine)
    end = time.perf_counter()
    load_time = end - start
    print(f"Full table load: {load_time:.2f}s")
    
    # 3. Aggregation Performance (Using Indexes)
    print("\nMeasuring Aggregation Time (with SQL indexes)...")
    start = time.perf_counter()
    agg_df = pd.read_sql("""
        SELECT country, COUNT(*) as visits, SUM(revenue) as total_rev 
        FROM web_logs 
        GROUP BY country 
        ORDER BY visits DESC 
        LIMIT 10
    """, con=engine)
    end = time.perf_counter()
    agg_time = end - start
    print(f"Top 10 Countries Agg: {agg_time*1000:.2f}ms")
    
    # 4. Live Query Simulation (Last 5 mins)
    start = time.perf_counter()
    live_df = pd.read_sql("SELECT COUNT(*) FROM web_logs WHERE timestamp >= datetime('now', '-5 minutes')", con=engine)
    end = time.perf_counter()
    live_time = end - start
    print(f"Live User Count (Last 5m): {live_time*1000:.2f}ms")

    print("\n--- Summary ---")
    if load_time < 3:
        print("SCORE: EXCELLENT (Sub-3s load for 500k rows)")
    elif load_time < 7:
        print("SCORE: GOOD (Acceptable for enterprise scale)")
    else:
        print("SCORE: NEEDS OPTIMIZATION (Load time exceeds 7s)")

if __name__ == "__main__":
    benchmark()
