import pandas as pd
import numpy as np
from scipy import stats


def descriptive_stats(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """FR19: Mean, std dev, median, min, max, percentiles for numeric columns."""
    if columns is None:
        columns = ["bytes_sent", "revenue", "status_code"]
    cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not cols:
        return pd.DataFrame()

    rows = []
    for col in cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        rows.append({
            "Metric": col.replace("_", " ").title(),
            "Count": len(series),
            "Mean": round(float(series.mean()), 4),
            "Std Dev": round(float(series.std()), 4),
            "Min": round(float(series.min()), 4),
            "25th %ile": round(float(series.quantile(0.25)), 4),
            "Median": round(float(series.median()), 4),
            "75th %ile": round(float(series.quantile(0.75)), 4),
            "Max": round(float(series.max()), 4),
            "Skewness": round(float(series.skew()), 4),
        })
    return pd.DataFrame(rows)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation matrix for numeric columns."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].corr().round(3)


def outlier_detection(df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.DataFrame:
    """Return rows where column value is beyond threshold z-scores."""
    if column not in df.columns:
        return pd.DataFrame()
    series = df[column].dropna()
    z_scores = np.abs(stats.zscore(series))
    outlier_idx = series.index[z_scores > threshold]
    return df.loc[outlier_idx]


def revenue_statistics(df: pd.DataFrame) -> dict:
    """Revenue-specific statistics."""
    if "revenue" not in df.columns:
        return {}
    rev = df[df["revenue"] > 0]["revenue"]
    if len(rev) == 0:
        return {}
    return {
        "total_revenue": round(float(rev.sum()), 2),
        "mean_revenue": round(float(rev.mean()), 2),
        "median_revenue": round(float(rev.median()), 2),
        "std_revenue": round(float(rev.std()), 2),
        "max_revenue": round(float(rev.max()), 2),
        "min_revenue": round(float(rev.min()), 2),
        "revenue_transactions": len(rev),
    }
