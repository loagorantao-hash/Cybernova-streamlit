import streamlit as st
import pandas as pd
from typing import Optional
from backend.services.export_service import export_csv, export_excel, get_export_filename


def render_data_table(
    df: pd.DataFrame,
    title: str = "",
    height: int = 400,
    enable_export: bool = True,
    key: str = "table",
    max_rows: int = 10_000,
):
    """Render an interactive data table with export buttons."""
    if title:
        st.html(f'<div class="section-header">{title}</div>')

    display_df = df.head(max_rows) if len(df) > max_rows else df

    if len(display_df) == 0:
        st.info("No data matches the current filters.")
        return

    st.dataframe(
        display_df,
        use_container_width=True,
        height=height,
        hide_index=True,
    )

    if enable_export and len(df) > 0:
        st.html("<div style='margin-top:8px'></div>")
        col1, col2, col3 = st.columns([1, 1, 5])
        fname = get_export_filename("cybernova_logs")
        with col1:
            st.download_button(
                label="Export CSV",
                data=export_csv(df),
                file_name=f"{fname}.csv",
                mime="text/csv",
                key=f"{key}_csv",
            )
        with col2:
            st.download_button(
                label="Export Excel",
                data=export_excel(df),
                file_name=f"{fname}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key}_xlsx",
            )


def render_summary_table(df: pd.DataFrame, title: str = "", key: str = "summary"):
    """Compact read-only summary table without export."""
    if title:
        st.html(f'<div class="section-header">{title}</div>')
    st.dataframe(df, use_container_width=True, hide_index=True, key=key)
