import pandas as pd
import sqlite3
import os
from pathlib import Path
import time

def migrate_data():
    base_dir = Path(r"c:\Users\WINDOWS 11 PRO\Desktop\Cybernova streamlit\data")
    db_path = base_dir / "cybernova.db"
    csv_path = base_dir / "cybernova_web_logs_500k.csv"
    
    # Remove existing malformed database files
    for ext in ["", "-shm", "-wal"]:
        f_path = Path(str(db_path) + ext)
        if f_path.exists():
            try:
                os.remove(f_path)
                print(f"Removed {f_path}")
            except Exception as e:
                print(f"Warning: could not remove {f_path} - {e}")
                
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    print("Connecting to new database...")
    conn = sqlite3.connect(db_path)
    
    # Enable WAL for performance
    conn.execute("PRAGMA journal_mode=WAL")
    
    print("Reading CSV in chunks and writing to SQLite...")
    start_time = time.time()
    
    chunksize = 50000
    rows_inserted = 0
    
    first_chunk = True
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        if first_chunk:
            chunk.to_sql("web_logs", conn, if_exists="replace", index=False)
            first_chunk = False
        else:
            chunk.to_sql("web_logs", conn, if_exists="append", index=False)
        rows_inserted += len(chunk)
        print(f"Inserted {rows_inserted} rows...")
        
    print("Creating indexes...")
    # Indexes to speed up queries
    conn.execute("CREATE INDEX idx_web_logs_user_id ON web_logs(user_id)")
    conn.execute("CREATE INDEX idx_web_logs_timestamp ON web_logs(timestamp)")
    conn.execute("CREATE INDEX idx_web_logs_activity ON web_logs(activity_type)")
    
    conn.close()
    
    end_time = time.time()
    print(f"Migration complete in {end_time - start_time:.2f} seconds!")

if __name__ == "__main__":
    migrate_data()
