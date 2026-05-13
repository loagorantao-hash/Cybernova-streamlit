import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def remove_duplicates(df: pd.DataFrame, subset: list = None) -> tuple[pd.DataFrame, int]:
    """Remove duplicate rows. Returns cleaned df and count removed."""
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    removed = before - len(df)
    logger.info(f"Removed {removed:,} duplicate rows")
    return df, removed


def handle_nulls(df: pd.DataFrame, strategy: str = "fill") -> tuple[pd.DataFrame, dict]:
    """
    Handle null values.
    strategy: 'fill' → fill with sensible defaults, 'drop' → drop rows with nulls
    Returns cleaned df and null count summary.
    """
    null_counts = df.isnull().sum().to_dict()
    null_counts = {k: v for k, v in null_counts.items() if v > 0}

    if strategy == "drop":
        before = len(df)
        df = df.dropna()
        logger.info(f"Dropped {before - len(df):,} rows with nulls")
    else:
        # Fill strings
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].fillna("Unknown")
        # Fill numerics
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(0)
        # Fill datetime
        for col in df.select_dtypes(include=["datetime64"]).columns:
            df[col] = df[col].fillna(pd.Timestamp.now())
        logger.info("Filled null values with defaults")

    return df, null_counts


def validate_data_types(df: pd.DataFrame) -> dict:
    """Return a report of column types and any detected issues."""
    report = {"issues": [], "column_types": {}}
    for col in df.columns:
        dtype = str(df[col].dtype)
        report["column_types"][col] = dtype
        null_pct = df[col].isnull().mean() * 100
        if null_pct > 20:
            report["issues"].append(f"Column '{col}' has {null_pct:.1f}% null values")
    return report


def clean_pipeline(df: pd.DataFrame, remove_dupes: bool = True,
                   null_strategy: str = "fill") -> tuple[pd.DataFrame, dict]:
    """Full cleaning pipeline. Returns cleaned df and report."""
    report = {"original_count": len(df), "removed_duplicates": 0, "null_columns": {}}

    if remove_dupes:
        df, removed = remove_duplicates(df)
        report["removed_duplicates"] = removed

    df, null_counts = handle_nulls(df, strategy=null_strategy)
    report["null_columns"] = null_counts
    report["final_count"] = len(df)
    report["records_removed"] = report["original_count"] - report["final_count"]
    return df, report
