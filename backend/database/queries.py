import sqlite3
import pandas as pd
import json
from pathlib import Path
import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Determine the absolute path to the project root based on this file's location
# Path(__file__) is backend/database/queries.py
# .parent is backend/database
# .parent.parent is backend
# .parent.parent.parent is the project root
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "cybernova.db"
STATS_PATH = ROOT_DIR / "data" / "global_stats.json"

@st.cache_resource
def get_connection():
    """Returns a new sqlite3 connection to the database. Thread-safe for Streamlit."""
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def run_query(sql: str, params: tuple = ()):
    """Executes a query and returns the results as a list of dictionaries."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"SQL error in run_query: {e}")
        return []

@st.cache_data(ttl=300)
def get_dataframe(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Executes a SQL query and returns a Pandas DataFrame."""
    conn = get_connection()
    if conn is None:
        logger.warning("Database unavailable, returning empty DataFrame.")
        return pd.DataFrame()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        # Convert known datetime columns
        for col in ["timestamp", "created_at", "last_login", "timestamp_ms"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except Exception as e:
        logger.error(f"Pandas SQL execution error: {e}")
        return pd.DataFrame()

def get_global_stats_fallback():
    """Reads the pre-calculated stats from global_stats.json if DB fails."""
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read fallback stats: {e}")
            return {}
    return {}
