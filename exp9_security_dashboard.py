# exp9_security_dashboard.py
# Data Science & Visualization Lab – Exercise 9
# Run: streamlit run exp9_security_dashboard.py
#
# Expected CSV columns:
# host, port, service, vulnerability, cvss, severity, exposed, criticality, priority
#
# Example:
# 192.168.1.10,22,SSH,Weak SSH Configuration,7.5,High,Yes,High,High

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Security Vulnerability Dashboard",
                   page_icon="🛡️", layout="wide")

st.title("🛡️ Network Vulnerability & Security Dashboard")
st.caption("Lab Exercise 9 – Cartographic / Security Visualization")

# -------------------- DATA --------------------
uploaded = st.sidebar.file_uploader(
    "Upload vulnerability_scan.csv", type=["csv"]
)

if uploaded:
    df = pd.read_csv(uploaded)
else:
    # Small fallback dataset so the dashboard works immediately.
    df = pd.DataFrame({
        "host": ["192.168.1.10", "192.168.1.10", "192.168.1.11",
                 "192.168.1.11", "192.168.1.12", "192.168.1.12"],
        "port": [22, 80, 21, 443, 3306, 8080],
        "service": ["SSH", "HTTP", "FTP", "HTTPS", "MySQL", "HTTP-Proxy"],
        "vulnerability": [
            "Weak SSH Configuration", "Outdated Web Server",
            "Anonymous FTP Login", "TLS Configuration Issue",
            "Weak Database Password", "Outdated Proxy"
        ],
        "cvss": [7.5, 6.5, 9.0, 5.3, 8.1, 4.3],
        "severity": ["High", "Medium", "Critical", "Medium", "High", "Medium"],
        "exposed": ["Yes", "Yes", "Yes", "Yes", "No", "No"],
        "criticality": ["High", "Medium", "High", "Medium", "High", "Low"],
        "priority": ["High", "Medium", "Critical", "Medium", "High", "Low"]
    })

# -------------------- CLEANING --------------------
required = [
    "host", "port", "service", "vulnerability", "cvss",
    "severity", "exposed", "criticality", "priority"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.info("Required columns: " + ", ".join(required))
    st.stop()

df["port"] = pd.to_numeric(df["port"], errors="coerce")
df["cvss"] = pd.to_numeric(df["cvss"], errors="coerce").fillna(0)

# -------------------- FILTERS --------------------
st.sidebar.header("Filters")

hosts = st.sidebar.multiselect(
    "Host", sorted(df["host"].dropna().unique()), default=[]
)
severities = st.sidebar.multiselect(
    "Severity", sorted(df["severity"].dropna().unique()), default=[]
)
services = st.sidebar.multiselect(
    "Service", sorted(df["service"].dropna().unique()), default=[]
)
exposed = st.sidebar.multiselect(
    "Exposed", sorted(df["exposed"].dropna().unique()), default=[]
)

filtered = df.copy()

if hosts:
    filtered = filtered[filtered["host"].isin(hosts)]
if severities:
    filtered = filtered[filtered["severity"].isin(severities)]
if services:
    filtered = filtered[filtered["service"].isin(services)]
if exposed:
    filtered = filtered[filtered["exposed"].isin(exposed)]

# -------------------- SUMMARY --------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Vulnerabilities", len(filtered))
c2.metric("Hosts", filtered["host"].nunique())
c3.metric("Open Ports", filtered["port"].nunique())
c4.metric("Average CVSS", round(filtered["cvss"].mean(), 2) if len(filtered) else 0)

st.divider()

# -------------------- VISUALIZATION 1 --------------------
st.subheader("1. Vulnerability by Severity")

severity_count = (
    filtered["severity"]
    .value_counts()
    .rename_axis("Severity")
    .reset_index(name="Count")
)

fig1 = px.bar(
    severity_count,
    x="Severity",
    y="Count",
    text="Count",
    title="Vulnerabilities by Severity"
)
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# -------------------- VISUALIZATION 2 --------------------
st.subheader("2. Vulnerabilities by Host")

host_count = (
    filtered["host"]
    .value_counts()
    .rename_axis("Host")
    .reset_index(name="Vulnerabilities")
)

fig2 = px.bar(
    host_count,
    x="Host",
    y="Vulnerabilities",
    text="Vulnerabilities",
    title="Vulnerability Count per Host"
)
fig2.update_traces(textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

# -------------------- VISUALIZATION 3 --------------------
st.subheader("3. CVSS Distribution")

fig3 = px.histogram(
    filtered,
    x="cvss",
    nbins=10,
    title="CVSS Score Distribution",
    labels={"cvss": "CVSS Score"}
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------- VISUALIZATION 4 --------------------
st.subheader("4. Host-Port Heatmap")

heat = filtered.pivot_table(
    index="host",
    columns="port",
    values="cvss",
    aggfunc="mean",
    fill_value=0
)

if not heat.empty:
    fig4 = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        title="Host vs Port – Average CVSS"
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No data available for the heatmap.")

# -------------------- VISUALIZATION 5 --------------------
st.subheader("5. Host–Service Relationship Graph")

# Build a simple network graph using Plotly.
edges = (
    filtered[["host", "service"]]
    .drop_duplicates()
    .rename(columns={"host": "source", "service": "target"})
)

nodes = list(
    pd.unique(
        pd.concat([edges["source"], edges["target"]], ignore_index=True)
    )
)

if edges.empty:
    st.info("No relationships available.")
else:
    import networkx as nx

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges.itertuples(index=False, name=None))

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        hoverinfo="none"
    )

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        marker=dict(size=20),
        hoverinfo="text"
    )

    fig5 = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Host → Service Relationship",
            showlegend=False,
            hovermode="closest",
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )

    st.plotly_chart(fig5, use_container_width=True)

# -------------------- VISUALIZATION 6 --------------------
st.subheader("6. Interactive Vulnerability Table")

st.dataframe(
    filtered.sort_values("cvss", ascending=False),
    use_container_width=True,
    hide_index=True
)

# -------------------- VISUALIZATION 7 --------------------
st.subheader("7. Vulnerability Prioritization")

priority_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

priority_df = filtered.copy()
priority_df["priority_score"] = (
    priority_df["priority"].map(priority_order).fillna(0)
)

priority_df = priority_df.sort_values(
    ["priority_score", "cvss"], ascending=False
)

st.dataframe(
    priority_df[
        ["host", "port", "service", "vulnerability",
         "cvss", "severity", "exposed", "criticality", "priority"]
    ],
    use_container_width=True,
    hide_index=True
)

st.success("Dashboard generated successfully.")
