"""
Generate 500,000 synthetic IIS-style web log records and save as Parquet.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from config import PARQUET_FILE

def generate_web_logs(n_records=500_000):
    print(f"Generating {n_records:,} synthetic web log records...")
    start_time = time.time()
    
    rng = np.random.default_rng(42)
    
    # Base configuration
    base_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 5, 15)
    total_seconds = int((end_date - base_date).total_seconds())
    
    # Dimensions
    countries = ["United States", "United Kingdom", "Germany", "France", "Canada",
                 "Australia", "Japan", "Brazil", "India", "South Africa", "Nigeria", "Kenya"]
    country_weights = [0.35, 0.15, 0.10, 0.08, 0.07, 0.05, 0.05, 0.04, 0.04, 0.03, 0.02, 0.02]
    
    services = ["Product Demo", "Support Portal", "Documentation", "Pricing Page",
                "Blog", "Case Studies", "Webinar", "Free Trial", "API Docs", "Dashboard"]
    service_weights = [0.15, 0.15, 0.12, 0.10, 0.10, 0.08, 0.08, 0.07, 0.05, 0.10]
    
    campaigns = ["CAMP_SPRING", "CAMP_SUMMER", "CAMP_FALL", "CAMP_WINTER", "ORGANIC", "DIRECT", "REFERRAL"]
    campaign_weights = [0.1, 0.1, 0.1, 0.1, 0.3, 0.2, 0.1]
    
    methods = ["GET", "POST", "PUT", "DELETE"]
    method_weights = [0.75, 0.15, 0.08, 0.02]
    
    statuses = [200, 201, 301, 302, 400, 401, 403, 404, 500, 502, 503]
    status_weights = [0.70, 0.05, 0.05, 0.05, 0.03, 0.02, 0.02, 0.05, 0.01, 0.01, 0.01]

    # Generate arrays
    print("  Generating timestamps...")
    # Exponential distribution to simulate varying traffic patterns, then mapped to our time range
    random_seconds = rng.integers(0, total_seconds, size=n_records)
    random_seconds.sort() # Sort to simulate chronological log file
    timestamps = [base_date + timedelta(seconds=int(s)) for s in random_seconds]
    
    print("  Generating IPs and Users...")
    ip_blocks = rng.integers(1, 255, size=(n_records, 4))
    ips = [f"{row[0]}.{row[1]}.{row[2]}.{row[3]}" for row in ip_blocks]
    
    # Introduce some repeat users (session IDs)
    num_sessions = n_records // 5
    base_sessions = [f"sess_{rng.integers(1000000, 9999999)}" for _ in range(num_sessions)]
    sessions = rng.choice(base_sessions, size=n_records)
    
    print("  Generating categorical data...")
    df = pd.DataFrame({
        "timestamp": timestamps,
        "ip_address": ips,
        "method": rng.choice(methods, n_records, p=method_weights),
        "uri": rng.choice(["/home", "/product", "/demo", "/pricing", "/support", "/blog", "/api/v1/data"], n_records),
        "status_code": rng.choice(statuses, n_records, p=status_weights),
        "bytes_sent": rng.integers(500, 100000, n_records).astype(float),
        "country": rng.choice(countries, n_records, p=country_weights),
        "service_type": rng.choice(services, n_records, p=service_weights),
        "session_id": sessions,
        "campaign_id": rng.choice(campaigns, n_records, p=campaign_weights),
    })
    
    # Logic for conversions and revenue based on service and campaign
    print("  Generating conversions and revenue...")
    
    # Base probability of conversion
    base_conv_prob = 0.05
    
    # Adjust prob based on service
    service_conv_multiplier = {
        "Product Demo": 3.0,
        "Free Trial": 4.0,
        "Pricing Page": 2.0,
        "Support Portal": 0.1,
        "Documentation": 0.1
    }
    
    df["conv_prob"] = base_conv_prob * df["service_type"].map(service_conv_multiplier).fillna(1.0)
    
    # Adjust prob based on campaign
    campaign_conv_multiplier = {
        "ORGANIC": 1.5,
        "DIRECT": 1.2,
        "REFERRAL": 2.0
    }
    df["conv_prob"] = df["conv_prob"] * df["campaign_id"].map(campaign_conv_multiplier).fillna(1.0)
    
    # Cap probability
    df["conv_prob"] = df["conv_prob"].clip(upper=0.9)
    
    # Roll for conversion
    random_rolls = rng.random(n_records)
    df["conversion_flag"] = (random_rolls < df["conv_prob"]).astype(int)
    
    # Generate revenue only for converted records
    df["revenue"] = 0.0
    converted_mask = df["conversion_flag"] == 1
    
    # Base revenue $50 - $1000, influenced by country
    country_rev_multiplier = {
        "United States": 1.5,
        "United Kingdom": 1.3,
        "Germany": 1.2,
        "India": 0.5,
        "Nigeria": 0.4
    }
    
    base_rev = rng.uniform(50, 1000, size=converted_mask.sum())
    country_mult = df.loc[converted_mask, "country"].map(country_rev_multiplier).fillna(1.0).values
    df.loc[converted_mask, "revenue"] = (base_rev * country_mult).round(2)
    
    # Drop temporary columns
    df = df.drop(columns=["conv_prob"])
    
    print(f"  Generation complete in {time.time() - start_time:.2f} seconds.")
    
    print(f"Saving to {PARQUET_FILE}...")
    PARQUET_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_FILE, index=False)
    
    file_size_mb = PARQUET_FILE.stat().st_size / (1024 * 1024)
    print(f"Done! Saved {n_records:,} records. File size: {file_size_mb:.2f} MB")
    
    # Quick sanity check
    print("\nDataset Summary:")
    print(f"  Total Records: {len(df):,}")
    print(f"  Total Conversions: {df['conversion_flag'].sum():,}")
    print(f"  Total Revenue: ${df['revenue'].sum():,.2f}")

if __name__ == "__main__":
    generate_web_logs()
