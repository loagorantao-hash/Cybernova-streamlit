import textwrap
"""
FR9, FR10, FR14-FR16, FR22 — System Administrator Dashboard
User management, dataset upload, data cleaning, export, system health.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from frontend.components.layout import set_page_config, load_css, page_header, section_header
from frontend.components.sidebar import render_sidebar
from frontend.components.kpi_cards import kpi_grid
from backend.auth.auth_manager import AuthManager
from backend.data_ingestion.dataset_loader import load_dataset, get_dataset_info
from backend.data_ingestion.cleaner import clean_pipeline, validate_data_types
from backend.services.user_service import UserService
from backend.services.export_service import export_csv, export_excel, get_export_filename
from backend.analytics.performance_monitor import get_system_metrics
from config import PARQUET_FILE, ROLES

@st.fragment(run_every=10 if st.session_state.get("live_mode") else None)
def render_system_health():
    metrics = get_system_metrics()
    perf_cols = st.columns(4)
    perf_cols[0].metric("Uptime", metrics["uptime"])
    perf_cols[1].metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
    perf_cols[2].metric("Memory Used", f"{metrics['memory_used_gb']:.2f} GB")
    perf_cols[3].metric("Memory Total", f"{metrics['memory_total_gb']:.2f} GB")

    perf_cols2 = st.columns(4)
    perf_cols2[0].metric("DB Size", f"{metrics['db_size_mb']:.2f} MB")
    perf_cols2[1].metric("Dataset Size", f"{metrics['parquet_size_mb']:.1f} MB")
    perf_cols2[2].metric("Python", metrics["python_version"])
    perf_cols2[3].metric("Dataset Loaded", "Yes" if metrics["dataset_loaded"] else "No")

    # Memory bar
    mem_pct = metrics["memory_percent"]
    mem_color = "#10b981" if mem_pct < 60 else "#f59e0b" if mem_pct < 85 else "#ef4444"
    st.html(textwrap.dedent(f"""
    <div class="glass-card">
        <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;">Memory Usage</div>
        <div style="background:rgba(255,255,255,0.06);border-radius:999px;height:10px;overflow:hidden;">
            <div style="width:{mem_pct}%;background:{mem_color};height:100%;
                        border-radius:999px;transition:width 0.5s ease;"></div>
        </div>
        <div style="font-size:11px;color:{mem_color};margin-top:6px;">{mem_pct:.1f}% used</div>
    </div>
    """))
    st.caption(f"Last refreshed: {metrics['timestamp']}")

set_page_config("Admin Dashboard")
load_css()

user = AuthManager.require_auth(allowed_roles=["admin"])
render_sidebar("pages/03_Admin_Dashboard.py")

page_header("Admin Dashboard", "System administration, user management, and data operations", "")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_users, tab_dataset, tab_clean, tab_export, tab_perf = st.tabs([
    "User Management", "Dataset Upload", "Data Cleaning", "Data Export", "System Health"
])

# ─── TAB 1: User Management (FR9) ────────────────────────────────────────────
with tab_users:
    section_header("Registered Users (FR9)")
    users = UserService.list_users()

    # Stats
    total_u = len(users)
    active_u = sum(1 for u in users if u.get("is_active"))
    cols = st.columns(4)
    cols[0].metric("Total Users", total_u)
    cols[1].metric("Active Users", active_u)
    cols[2].metric("Inactive", total_u - active_u)
    cols[3].metric("Roles Available", len(ROLES))

    st.html("<div style='height:8px'></div>")

    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, use_container_width=True, hide_index=True, height=300)

    # Create User
    with st.expander("Create New User", expanded=False):
        with st.form("create_user_form"):
            c1, c2 = st.columns(2)
            nu = c1.text_input("Username", key="nu_user")
            ne = c2.text_input("Email", key="nu_email")
            np_ = c1.text_input("Password", type="password", key="nu_pass")
            nr = c2.selectbox("Role", options=list(ROLES.keys()),
                               format_func=lambda r: ROLES[r], key="nu_role")
            if st.form_submit_button("Create User", use_container_width=True):
                if nu and ne and np_:
                    res = UserService.create_user(nu, ne, np_, nr)
                    if res["success"]:
                        st.success(f"User '{nu}' created.")
                        st.rerun()
                    else:
                        st.error(res["error"])
                else:
                    st.error("All fields required.")

    # Deactivate / Delete
    if users:
        with st.expander("Manage Existing User", expanded=False):
            user_opts = {f"{u['username']} ({u['email']})": u["id"] for u in users}
            selected_label = st.selectbox("Select User", list(user_opts.keys()), key="manage_sel")
            selected_id = user_opts[selected_label]
            c1, c2, c3 = st.columns(3)
            new_role = c1.selectbox("Change Role", list(ROLES.keys()),
                                     format_func=lambda r: ROLES[r], key="change_role")
            if c2.button("Update Role"):
                res = UserService.update_user(selected_id, role=new_role)
                st.success(res.get("user", {}).get("username", "") + " role updated.") if res["success"] else st.error(res["error"])
                st.rerun()
            if c3.button("Deactivate User", type="secondary"):
                res = UserService.deactivate_user(selected_id)
                st.success("User deactivated.") if res["success"] else st.error(res["error"])
                st.rerun()

    # Audit Logs
    section_header("Audit Log")
    logs = UserService.get_audit_logs(100)
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True, height=250)

# ─── TAB 2: Dataset Upload (FR10) ────────────────────────────────────────────
with tab_dataset:
    section_header("Current Dataset Info (FR10)")
    df_loaded = load_dataset()
    info = get_dataset_info(df_loaded)

    i_cols = st.columns(4)
    i_cols[0].metric("Total Records", f"{info['total_records']:,}")
    i_cols[1].metric("Countries", info["countries"])
    i_cols[2].metric("Services", info["services"])
    i_cols[3].metric("Memory (MB)", f"{info['memory_mb']:.1f}")

    st.html(textwrap.dedent(f"""
    <div class="glass-card" style="margin-top:12px;">
        <div style="font-size:12px;color:#94a3b8;line-height:2;">
            <strong style="color:#f1f5f9;">Date Range:</strong> {info['date_range'][0]} → {info['date_range'][1]}<br>
            <strong style="color:#f1f5f9;">Columns:</strong> {', '.join(info['columns'][:12])}{'...' if len(info['columns']) > 12 else ''}
        </div>
    </div>
    """))

    section_header("Upload New Dataset (FR10)")
    uploaded = st.file_uploader(
        "Upload CSV or Parquet file (max 500MB)",
        type=["csv", "parquet"],
        key="dataset_upload",
    )
    if uploaded:
        with st.spinner("Processing uploaded file..."):
            try:
                if uploaded.name.endswith(".csv"):
                    new_df = pd.read_csv(uploaded)
                else:
                    new_df = pd.read_parquet(uploaded)

                st.success(f"File loaded: **{len(new_df):,} records**, **{len(new_df.columns)} columns**")
                st.dataframe(new_df.head(5), use_container_width=True, hide_index=True)

                if st.button("Save as Active Dataset"):
                    PARQUET_FILE.parent.mkdir(parents=True, exist_ok=True)
                    new_df.to_parquet(PARQUET_FILE, index=False)
                    st.success(f"Dataset saved to {PARQUET_FILE}. Reload the app to use it.")
                    load_dataset.clear()
            except Exception as e:
                st.error(f"Error processing file: {e}")

# ─── TAB 3: Data Cleaning (FR14-FR15) ────────────────────────────────────────
with tab_clean:
    section_header("Data Quality Report (FR14)")
    df_c = load_dataset()
    report = validate_data_types(df_c)

    if report["issues"]:
        for issue in report["issues"]:
            st.warning(issue)
    else:
        st.success("No data quality issues detected.")

    null_counts = {k: int(v) for k, v in df_c.isnull().sum().items() if v > 0}
    if null_counts:
        st.dataframe(pd.DataFrame(list(null_counts.items()), columns=["Column", "Null Count"]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No null values found.")

    dupes = int(df_c.duplicated().sum())
    st.metric("Duplicate Rows", dupes)

    section_header("Run Cleaning Pipeline (FR15)")
    c1, c2 = st.columns(2)
    rm_dupes = c1.checkbox("Remove Duplicates", value=True)
    null_strat = c2.selectbox("Null Handling Strategy", ["fill", "drop"])

    if st.button("Run Cleaning Pipeline"):
        with st.spinner("Cleaning data..."):
            cleaned_df, clean_report = clean_pipeline(df_c, remove_dupes=rm_dupes,
                                                       null_strategy=null_strat)
            st.success(f"Cleaning complete!")
            st.json({
                "Original Records": clean_report["original_count"],
                "Duplicates Removed": clean_report["removed_duplicates"],
                "Final Records": clean_report["final_count"],
                "Records Removed Total": clean_report["records_removed"],
            })
            if st.button("Save Cleaned Dataset"):
                cleaned_df.to_parquet(PARQUET_FILE, index=False)
                load_dataset.clear()
                st.success("Cleaned dataset saved.")

# ─── TAB 4: Data Export (FR16) ───────────────────────────────────────────────
with tab_export:
    section_header("Export Dataset (FR16)")
    df_exp = load_dataset()

    max_rows = st.slider("Max rows to export", 1000, min(100000, len(df_exp)),
                         value=min(10000, len(df_exp)), step=1000)
    export_df = df_exp.head(max_rows)

    fname = get_export_filename("cybernova_full_export")
    col1, col2 = st.columns(2)
    col1.download_button(
        "Download CSV", export_csv(export_df),
        file_name=f"{fname}.csv", mime="text/csv", use_container_width=True,
    )
    col2.download_button(
        "Download Excel", export_excel(export_df),
        file_name=f"{fname}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.caption(f"Exporting **{len(export_df):,}** of **{len(df_exp):,}** records.")
    st.dataframe(export_df.head(10), use_container_width=True, hide_index=True)

# ─── TAB 5: System Performance (FR22) ────────────────────────────────────────
with tab_perf:
    section_header("System Health Monitor (FR22)")
    
    render_system_health()

    if st.button("Manual Refresh Metrics"):
        st.rerun()
