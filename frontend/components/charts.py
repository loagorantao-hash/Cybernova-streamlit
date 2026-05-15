import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from config import CHART_COLORS, PLOTLY_LAYOUT
import copy


def _base_layout(**overrides) -> dict:
    layout = copy.deepcopy(PLOTLY_LAYOUT)
    layout.update(overrides)
    return layout


# ── Line / Area Chart ─────────────────────────────────────────────────────────
def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
               color: str = "#2563eb", fill: bool = True) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5, color=color),
        fill="tozeroy" if fill else "none",
        fillcolor=color.replace(")", ", 0.1)").replace("rgb", "rgba") if "rgb" in color else f"rgba(37,99,235,0.08)",
        name=y.replace("_", " ").title(),
        hovertemplate=f"<b>%{{x}}</b><br>{y}: %{{y:,.0f}}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))))
    return fig


# ── Bar Chart ─────────────────────────────────────────────────────────────────
def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
              color: str = "#2563eb", horizontal: bool = False,
              color_sequence: list = None) -> go.Figure:
    colors = color_sequence or [color]
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", color_discrete_sequence=colors)
    else:
        fig = px.bar(df, x=x, y=y, color_discrete_sequence=colors)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1")),
                                     bargap=0.3))
    return fig


# ── Multi-Bar Chart ───────────────────────────────────────────────────────────
def grouped_bar_chart(df: pd.DataFrame, x: str, y_cols: list,
                      title: str = "") -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Bar(
            x=df[x], y=df[col], name=col.replace("_", " ").title(),
            marker_color=color, marker_line_width=0,
        ))
    fig.update_layout(**_base_layout(
        title=dict(text=title, font=dict(size=14, color="#cbd5e1")),
        barmode="group", bargap=0.2,
    ))
    return fig


# ── Pie / Donut Chart ─────────────────────────────────────────────────────────
def donut_chart(df: pd.DataFrame, values: str, names: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Pie(
        values=df[values], labels=df[names],
        hole=0.55,
        marker=dict(colors=CHART_COLORS, line=dict(color="#0f172a", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#cbd5e1"),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text=title, font=dict(size=14, color="#cbd5e1")),
        showlegend=True,
        legend=dict(orientation="v", x=1, y=0.5),
    ))
    return fig


# ── Funnel Chart ──────────────────────────────────────────────────────────────
def funnel_chart(df: pd.DataFrame, stage_col: str, value_col: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Funnel(
        y=df[stage_col], x=df[value_col],
        textposition="inside",
        textinfo="value+percent previous",
        marker=dict(color=CHART_COLORS[:len(df)]),
        connector=dict(line=dict(color="#1e293b", width=2)),
    ))
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))))
    return fig


# ── Choropleth Map ────────────────────────────────────────────────────────────
def choropleth_map(df: pd.DataFrame, country_col: str, iso_col: str,
                   value_col: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Choropleth(
        locations=df[iso_col],
        z=df[value_col],
        text=df[country_col],
        colorscale=[[0, "#0f172a"], [0.3, "#1e3a5f"], [0.6, "#2563eb"], [1.0, "#06b6d4"]],
        marker_line_color="#0f172a",
        marker_line_width=0.5,
        colorbar=dict(bgcolor="rgba(0,0,0,0)", tickfont=dict(color="#94a3b8")),
        hovertemplate="<b>%{text}</b><br>" + value_col.replace("_", " ").title() + ": %{z:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))),
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.1)",
            landcolor="#1e293b", oceancolor="#0f172a",
            showocean=True, bgcolor="rgba(0,0,0,0)",
            projection_type="natural earth",
        ),
    )
    return fig


# ── Scatter Chart ─────────────────────────────────────────────────────────────
def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
                  title: str = "", size: str = None) -> go.Figure:
    kwargs = dict(x=x, y=y, color_discrete_sequence=CHART_COLORS)
    if color and color in df.columns:
        kwargs["color"] = color
    if size and size in df.columns:
        kwargs["size"] = size
    fig = px.scatter(df, **kwargs)
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))))
    return fig


# ── Heatmap ───────────────────────────────────────────────────────────────────
def heatmap(z_data, x_labels, y_labels, title: str = "") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=z_data, x=x_labels, y=y_labels,
        colorscale=[[0, "#0f172a"], [0.5, "#2563eb"], [1.0, "#06b6d4"]],
        hovertemplate="x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))))
    return fig


# ── Histogram ──────────────────────────────────────────────────────────────────
def histogram(df: pd.DataFrame, x: str, title: str = "", color: str = "#2563eb", 
              nbins: int = 30) -> go.Figure:
    fig = px.histogram(df, x=x, nbins=nbins, color_discrete_sequence=[color])
    fig.update_layout(**_base_layout(title=dict(text=title, font=dict(size=14, color="#cbd5e1"))))
    fig.update_traces(marker_line_width=0)
    return fig


# ── Chart Renderer ────────────────────────────────────────────────────────────
def show(fig: go.Figure, height: int = 380, key: str = None):
    """Render a Plotly figure in Streamlit."""
    st.plotly_chart(
        fig, use_container_width=True,
        config={"displayModeBar": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d", "toImage"]},
        key=key,
    )
