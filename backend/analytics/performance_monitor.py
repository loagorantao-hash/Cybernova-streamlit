import time
import psutil
import platform
import streamlit as st
from datetime import datetime
from config import DB_PATH
from backend.database.connection import get_engine
from sqlalchemy import text


_start_time = datetime.now()


def get_system_metrics() -> dict:
    """FR22: System health KPIs."""
    uptime = datetime.now() - _start_time
    uptime_str = str(uptime).split(".")[0]  # Remove microseconds

    try:
        cpu_pct = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        mem_used_gb = round(mem.used / 1024 ** 3, 2)
        mem_total_gb = round(mem.total / 1024 ** 3, 2)
        mem_pct = mem.percent
    except Exception:
        cpu_pct = 0.0
        mem_used_gb = mem_total_gb = mem_pct = 0.0

    db_size_mb = round(DB_PATH.stat().st_size / 1024 / 1024, 3) if DB_PATH.exists() else 0.0
    
    # Database Health Checks
    db_health = "Offline"
    wal_status = "Unknown"
    row_count = 0
    query_latency_ms = 0.0
    
    try:
        engine = get_engine()
        t0 = time.perf_counter()
        with engine.connect() as conn:
            # Check connection and latency
            conn.execute(text("SELECT 1")).fetchone()
            query_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            
            # Check WAL status
            res = conn.execute(text("PRAGMA journal_mode;")).fetchone()
            if res:
                wal_status = res[0].upper()
            
            # Table row counts
            res = conn.execute(text("SELECT COUNT(*) FROM web_logs;")).fetchone()
            if res:
                row_count = res[0]
                
            db_health = "Online"
    except Exception as e:
        db_health = f"Error: {str(e)}"

    return {
        "uptime": uptime_str,
        "cpu_percent": cpu_pct,
        "memory_used_gb": mem_used_gb,
        "memory_total_gb": mem_total_gb,
        "memory_percent": mem_pct,
        "db_size_mb": db_size_mb,
        "db_health": db_health,
        "wal_status": wal_status,
        "row_count": row_count,
        "query_latency_ms": query_latency_ms,
        "python_version": platform.python_version(),
        "os": platform.system(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def time_query(func, *args, **kwargs):
    """Wrap a function call and return (result, elapsed_ms)."""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    return result, elapsed
