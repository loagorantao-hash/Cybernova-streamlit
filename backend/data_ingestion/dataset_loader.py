import streamlit as st
import pandas as pd
import logging
from backend.database.queries import get_dataframe

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300, show_spinner="Loading dataset from SQLite...")
def load_dataset(limit: int = 5000) -> pd.DataFrame:
    """
    Loads a sample of the dataset for UI components that strictly require a DataFrame.
    Note: Most metrics should now be calculated via direct SQL queries in KPIEngine.
    """
    try:
        query = f"SELECT * FROM web_logs ORDER BY timestamp DESC LIMIT {limit}"
        df = get_dataframe(query)
        if df.empty:
            logger.warning("Database returned empty DataFrame.")
            return pd.DataFrame()
            
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        logger.info(f"Loaded {len(df):,} records sample from SQLite")
        return df
    except Exception as e:
        logger.error(f"Dataset load error: {e}")
        st.error(f"Error loading dataset from SQLite: {e}")
        return pd.DataFrame()

def get_dataset_info() -> dict:
    from backend.database.queries import run_query
    res = run_query("SELECT COUNT(*) as cnt FROM web_logs")
    count = res[0]['cnt'] if res else 0
    return {
        "total_records": count,
        "columns": [], # Too dynamic, use schema if needed
        "date_range": ("N/A", "N/A"),
        "countries": 0,
        "services": 0,
        "memory_mb": 0.0
    }
