# exp10_network_traffic_dashboard.py
# Data Science & Visualization Lab – Exercise 10
# Run: streamlit run exp10_network_traffic_dashboard.py
#
# Expected CSV columns:
# source_ip, destination_ip, destination_port, protocol, timestamp, bytes
#
# Example:
# 192.168.1.10,10.0.0.5,80,TCP,2026-09-21 10:00:00,1500

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

st.set_page_config(
    page_title="Network Traffic Visualization",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Network Traffic Visualization Dashboard")
st.caption("Lab Exercise 10 – NVisionIP / Time-Based Network Traffic Visualization")

# -------------------- DATA --------------------
uploaded = st.sidebar.file_uploader(
    "Upload network_traffic.csv", type=["csv"]
)

if uploaded:
    df = pd.read_csv(uploaded)
else:
    # Fallback data so the program can be tested immediately.
    df = pd.DataFrame({
        "source_ip": [
            "192.168.1.10", "192.168.1.10", "192.168.1.11",
            "192.168.1.12", "192.168.1.11", "192.168.1.12"
        ],
        "destination_ip": [
            "10.0.0.5", "10.0.0.6", "10.0.0.5",
            "10.0.0.7", "10.0.0.6", "10.0.0.5"
        ],
        "destination_port": [80, 443, 22, 53, 80, 443],
        "protocol": ["TCP", "TCP", "TCP", "UDP", "TCP", "TCP"],
        "timestamp": [
            "2026-09-21 10:00:00",
            "2026-09-21 10:01:00",
            "2026-09-21 10:02:00",
            "2026-09-21 10:03:00",
            "2026-09-21 10:04:00",
            "2026-09-21 10:05:00"
        ],
        "bytes": [1500, 5000, 2500, 900, 4000, 7000]
    })

# -------------------- CLEANING --------------------
required = [
    "source_ip",
    "destination_ip",
    "destination_port",
    "protocol",
    "timestamp",
    "bytes"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.info("Required columns: " + ", ".join(required))
    st.stop()

df["destination_port"] = pd.to_numeric(
    df["destination_port"], errors="coerce"
)
df["bytes"] = pd.to_numeric(df["bytes"], errors="coerce").fillna(0)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

df = df.dropna(
    subset=["source_ip", "destination_ip", "destination_port", "timestamp"]
)

# -------------------- FILTERS --------------------
st.sidebar.header("Interactive Filters")

selected_hosts = st.sidebar.multiselect(
    "Source Host",
    sorted(df["source_ip"].unique()),
    default=[]
)

selected_ports = st.sidebar.multiselect(
    "Destination Port",
    sorted(df["destination_port"].astype(int).unique()),
    default=[]
)

selected_protocols = st.sidebar.multiselect(
    "Protocol",
    sorted(df["protocol"].unique()),
    default=[]
)

filtered = df.copy()

if selected_hosts:
    filtered = filtered[filtered["source_ip"].isin(selected_hosts)]

if selected_ports:
    filtered = filtered[
        filtered["destination_port"].isin(selected_ports)
    ]

if selected_protocols:
    filtered = filtered[
        filtered["protocol"].isin(selected_protocols)
    ]

# -------------------- QUESTIONS 1–6 --------------------
st.header("Lab Questions")

q1, q2, q3 = st.columns(3)

q1.write("**1. Source Hosts**")
q1.write(sorted(filtered["source_ip"].unique()))

q2.write("**2. Destination Hosts**")
q2.write(sorted(filtered["destination_ip"].unique()))

q3.write("**3. Destination Ports**")
q3.write(
    sorted(filtered["destination_port"].astype(int).unique())
)

# Largest number of flows
flow_count = (
    filtered.groupby("source_ip")
    .size()
    .sort_values(ascending=False)
)

# Largest traffic volume
traffic_by_host = (
    filtered.groupby("source_ip")["bytes"]
    .sum()
    .sort_values(ascending=False)
)

# Largest service traffic
traffic_by_service = (
    filtered.groupby("destination_port")["bytes"]
    .sum()
    .sort_values(ascending=False)
)

q4, q5, q6 = st.columns(3)

if not flow_count.empty:
    q4.metric(
        "4. Host with Largest Number of Flows",
        flow_count.index[0],
        f"{flow_count.iloc[0]} flows"
    )

if not traffic_by_host.empty:
    q5.metric(
        "5. Host with Largest Traffic",
        traffic_by_host.index[0],
        f"{traffic_by_host.iloc[0]:,.0f} bytes"
    )

if not traffic_by_service.empty:
    q6.metric(
        "6. Service/Port with Largest Traffic",
        f"Port {int(traffic_by_service.index[0])}",
        f"{traffic_by_service.iloc[0]:,.0f} bytes"
    )

st.divider()

# -------------------- 1. HOST ACTIVITY VIEW --------------------
st.header("1. Host Activity View")

host_activity = (
    filtered.groupby("source_ip")
    .agg(
        flows=("source_ip", "size"),
        traffic_bytes=("bytes", "sum")
    )
    .reset_index()
)

fig1 = px.scatter(
    host_activity,
    x="flows",
    y="traffic_bytes",
    size="traffic_bytes",
    hover_name="source_ip",
    text="source_ip",
    title="Source Host Activity"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------- 2. HOST RANKING --------------------
st.header("2. Host Ranking")

ranking = (
    filtered.groupby("source_ip")["bytes"]
    .sum()
    .reset_index()
    .sort_values("bytes", ascending=False)
)

fig2 = px.bar(
    ranking,
    x="source_ip",
    y="bytes",
    text="bytes",
    title="Total Traffic Generated by Source Host",
    labels={"bytes": "Traffic (bytes)", "source_ip": "Source IP"}
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------- 3. PORT DISTRIBUTION --------------------
st.header("3. Port Distribution")

port_distribution = (
    filtered["destination_port"]
    .value_counts()
    .rename_axis("Port")
    .reset_index(name="Flows")
)

fig3 = px.bar(
    port_distribution,
    x="Port",
    y="Flows",
    text="Flows",
    title="Destination Port Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------- 4. NETWORK GRAPH --------------------
st.header("4. Network Graph – Host / Service Relationship")

edge_data = (
    filtered.groupby(
        ["source_ip", "destination_ip", "destination_port"]
    )
    .size()
    .reset_index(name="flows")
)

G = nx.DiGraph()

for _, row in edge_data.iterrows():
    G.add_edge(
        row["source_ip"],
        f'{row["destination_ip"]}:{int(row["destination_port"])}',
        weight=row["flows"]
    )

if len(G.nodes) > 0:
    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none"
    )

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        marker=dict(size=20),
        hoverinfo="text"
    )

    fig4 = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Source Host → Destination Host:Port",
            showlegend=False,
            hovermode="closest",
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            )
        )
    )

    st.plotly_chart(fig4, use_container_width=True)

# -------------------- 5. TIME-BASED TRAFFIC --------------------
st.header("5. Time-Based Traffic Visualization")

timeline = (
    filtered.set_index("timestamp")
    .resample("1min")["bytes"]
    .sum()
    .reset_index()
)

fig5 = px.line(
    timeline,
    x="timestamp",
    y="bytes",
    markers=True,
    title="Traffic Volume Over Time",
    labels={"bytes": "Traffic (bytes)", "timestamp": "Time"}
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------- 6. PROTOCOL DISTRIBUTION --------------------
st.header("6. Protocol Distribution")

protocol_count = (
    filtered["protocol"]
    .value_counts()
    .rename_axis("Protocol")
    .reset_index(name="Flows")
)

fig6 = px.pie(
    protocol_count,
    names="Protocol",
    values="Flows",
    title="Network Traffic by Protocol"
)

st.plotly_chart(fig6, use_container_width=True)

# -------------------- RAW DATA --------------------
st.header("Filtered Network Traffic")

st.dataframe(
    filtered.sort_values("timestamp"),
    use_container_width=True,
    hide_index=True
)

st.success("Network traffic dashboard generated successfully.")
