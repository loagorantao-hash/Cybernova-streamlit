import time
import psutil
import platform
import streamlit as st
from datetime import datetime
from config import PARQUET_FILE, DB_PATH


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
    parquet_size_mb = round(PARQUET_FILE.stat().st_size / 1024 / 1024, 1) if PARQUET_FILE.exists() else 0.0

    return {
        "uptime": uptime_str,
        "cpu_percent": cpu_pct,
        "memory_used_gb": mem_used_gb,
        "memory_total_gb": mem_total_gb,
        "memory_percent": mem_pct,
        "db_size_mb": db_size_mb,
        "parquet_size_mb": parquet_size_mb,
        "python_version": platform.python_version(),
        "os": platform.system(),
        "dataset_loaded": PARQUET_FILE.exists(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def time_query(func, *args, **kwargs):
    """Wrap a function call and return (result, elapsed_ms)."""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    return result, elapsed
