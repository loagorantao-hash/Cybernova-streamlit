import pandas as pd
import io
from pathlib import Path
from datetime import datetime
from config import EXPORTS_DIR


def export_csv(df: pd.DataFrame) -> bytes:
    """FR16: Export DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def export_excel(df: pd.DataFrame, sheet_name: str = "Web Logs") -> bytes:
    """FR16: Export DataFrame to Excel bytes."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def save_export(df: pd.DataFrame, filename: str, fmt: str = "csv") -> Path:
    """Save export to the exports directory."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{ts}_{filename}"
    if fmt == "csv":
        path = EXPORTS_DIR / f"{safe_name}.csv"
        df.to_csv(path, index=False)
    else:
        path = EXPORTS_DIR / f"{safe_name}.xlsx"
        df.to_excel(path, index=False, engine="openpyxl")
    return path


def get_export_filename(prefix: str = "cybernova_export") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"
