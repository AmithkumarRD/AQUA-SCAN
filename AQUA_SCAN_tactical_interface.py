import streamlit as st
import plotly.graph_objects as go
import math
import random
import csv
import io
import os
from datetime import datetime
import cv2
import numpy as np

# ============================================================
# AQUA-SCAN | UNDERWATER DAM DIGITAL TWIN
# Curved dam, canyon terrain, water, ROV, sonar and defects
# ============================================================

st.set_page_config(
    page_title="AQUA-SCAN | Underwater Dam Digital Twin",
    page_icon="🌊",
    layout="wide"
)

# ------------------------- TACTICAL INTERFACE THEME -------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --ops-bg: #080e0c;
    --ops-panel: #101a15;
    --ops-panel-2: #14221a;
    --ops-line: #304638;
    --ops-green: #a6ff4d;
    --ops-muted: #8da394;
    --ops-amber: #ffbd4a;
    --ops-red: #ff5b58;
}
.stApp {
    background:
      radial-gradient(ellipse at 12% 0%, rgba(73,125,68,.16), transparent 35%),
      linear-gradient(145deg, #080e0c 0%, #0b1510 55%, #080d0b 100%);
    color: #e7f0e8;
}
[data-testid="stHeader"] { background: rgba(8,14,12,.88); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111d16, #0a110d);
    border-right: 1px solid #304638;
}
[data-testid="stSidebar"] * { color: #dce9dd; }
h1, h2, h3, h4 {
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: 1.4px;
    text-transform: uppercase;
}
h1 { color: var(--ops-green) !important; font-size: 3.1rem !important; }
h2 { color: #d7e9d8 !important; border-bottom: 1px solid #304638; padding-bottom: .35rem; }
h3 { color: var(--ops-green) !important; }
p, label, [data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #14221a, #0d1711);
    border: 1px solid #38533e;
    border-left: 3px solid var(--ops-green);
    border-radius: 7px;
    padding: 13px 16px;
    min-height: 104px;
    box-shadow: 0 8px 24px rgba(0,0,0,.18);
}
[data-testid="stMetricLabel"] { color: #91aa98 !important; font-size: .72rem !important; }
[data-testid="stMetricValue"] {
    color: #d9ffad !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2rem !important;
}
.stButton > button, .stDownloadButton > button {
    border: 1px solid #6e9b58;
    background: linear-gradient(110deg, #253d29, #17291c);
    color: #dfffca;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: .7px;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #b6ff75;
    color: #fff;
    background: #304d31;
}
[data-testid="stProgressBar"] > div > div { background: #a6ff4d; }
[data-testid="stExpander"] {
    border: 1px solid #304638;
    border-radius: 5px;
    background: rgba(16,26,21,.72);
}
hr { border-color: #304638 !important; }
.ops-banner {
    border: 1px solid #426044;
    background: linear-gradient(100deg, rgba(35,62,39,.92), rgba(12,24,17,.94));
    padding: 17px 20px;
    border-radius: 6px;
    margin: 0 0 18px 0;
    position: relative;
}
.ops-kicker {
    color: #a6ff4d; font: 600 11px 'IBM Plex Mono', monospace;
    letter-spacing: 2px; margin-bottom: 5px;
}
.ops-title {
    color: #f0f7ee; font: 800 30px 'Barlow Condensed', sans-serif;
    letter-spacing: 2px; text-transform: uppercase;
}
.ops-sub {
    color: #9fb4a2; font: 11px 'IBM Plex Mono', monospace;
    margin-top: 4px; letter-spacing: .7px;
}
.ops-status {
    display: inline-block; border: 1px solid #64834e; color: #caff9d;
    padding: 5px 9px; border-radius: 3px; font: 600 10px 'IBM Plex Mono', monospace;
    letter-spacing: 1px; margin-top: 10px;
}
.target-card {
    background: linear-gradient(135deg, #17251c, #0d1711 75%);
    border: 1px solid #405a43; border-left: 4px solid var(--target-color);
    border-radius: 6px; padding: 15px 16px; margin: 8px 0 12px 0;
    box-shadow: 0 8px 22px rgba(0,0,0,.2);
}
.target-top { display:flex; justify-content:space-between; gap:10px; align-items:center; }
.target-id { color:#9ab09d; font: 600 10px 'IBM Plex Mono',monospace; letter-spacing:1.5px; }
.target-kind { color:#f0f6ee; font:700 21px 'Barlow Condensed',sans-serif; letter-spacing:1px; text-transform:uppercase; margin:5px 0 9px; }
.target-chip { color:var(--target-color); border:1px solid var(--target-color); padding:4px 7px; font:600 10px 'IBM Plex Mono',monospace; border-radius:3px; }
.target-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; border-top:1px solid #344a38; padding-top:10px; }
.target-label { color:#819887; font:9px 'IBM Plex Mono',monospace; letter-spacing:1px; }
.target-value { color:#e0f0df; font:600 14px 'IBM Plex Mono',monospace; margin-top:4px; }
.target-foot { color:#a9b9aa; font:10px 'IBM Plex Mono',monospace; margin-top:11px; line-height:1.5; }
.target-meter { height:5px; background:#26372b; border-radius:5px; margin-top:7px; overflow:hidden; }
.target-meter-fill { height:100%; background:var(--target-color); box-shadow:0 0 10px var(--target-color); }
.section-tag {
    color:#a6ff4d; font:600 10px 'IBM Plex Mono',monospace; letter-spacing:2px;
    border:1px solid #38533e; display:inline-block; padding:4px 8px; margin-bottom:8px;
}
div[data-testid="stAlert"] { border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ops-banner">
  <div class="ops-kicker">AQUA-SCAN // AUTONOMOUS INSPECTION COMMAND</div>
  <div class="ops-title">Underwater Structural Intelligence System</div>
  <div class="ops-sub">SECTOR: DAM-01 &nbsp;|&nbsp; PLATFORM: REMOTE OPERATED VEHICLE &nbsp;|&nbsp; SENSOR SUITE: SONAR / OPTICAL</div>
  <div class="ops-status">● SIMULATION ENVIRONMENT &nbsp; // &nbsp; SYSTEM READY</div>
</div>
""", unsafe_allow_html=True)

# ------------------------- CONSTANTS -------------------------

DAM_WIDTH = 24.0
DAM_HEIGHT = 16.0
DAM_THICKNESS = 1.2
WATER_LEVEL = 11.0
ROV_OFFSET = 4.0

# Route waypoints are (X, Z); Y is calculated from the curved dam.
ROUTE = [
    (2.0, 3.0), (4.0, 4.0), (6.0, 5.0),
    (8.0, 6.0), (10.0, 7.0), (12.0, 8.0),
    (14.0, 8.0), (16.0, 7.0), (18.0, 6.0),
    (20.0, 5.0), (22.0, 4.0)
]

DEFECTS = [
    {"x": 5.2, "z": 12.1, "kind": "Crack", "severity": "High"},
    {"x": 10.4, "z": 7.0, "kind": "Surface erosion", "severity": "Medium"},
    {"x": 17.6, "z": 4.0, "kind": "Spalling", "severity": "High"},
    {"x": 20.0, "z": 9.2, "kind": "Seepage indicator", "severity": "Medium"},
]

# ------------------------- SESSION STATE -------------------------

defaults = {
    "running": False,
    "step": 0,
    "battery": 100.0,
    "depth": 25.0,
    "heading": 90,
    "sonar_angle": 0,
    "target_depth": 25,
    "water_turbidity": 150,
    "detected_defects": [],
    "route_points": list(ROUTE),
    "obstacle_avoided": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------- SIDEBAR -------------------------

st.sidebar.title("◈ MISSION CONTROL")
st.sidebar.markdown("### OPERATION PARAMETERS")

st.session_state.target_depth = st.sidebar.slider(
    "Target depth (m)", 5, 100, 25, key="depth_control"
)
st.session_state.water_turbidity = st.sidebar.slider(
    "Water turbidity (NTU)", 5, 500, 150, key="turbidity_control"
)

st.sidebar.divider()
if st.sidebar.button("▶ START MISSION", width="stretch"):
    st.session_state.running = True
if st.sidebar.button("⏸ PAUSE MISSION", width="stretch"):
    st.session_state.running = False
if st.sidebar.button("↻ RESET MISSION", width="stretch"):
    st.session_state.running = False
    st.session_state.step = 0
    st.session_state.battery = 100.0
    st.session_state.depth = 25.0
    st.session_state.heading = 90
    st.session_state.sonar_angle = 0
    st.session_state.detected_defects = []
    st.session_state.route_points = list(ROUTE)
    st.session_state.obstacle_avoided = False

st.sidebar.divider()
st.sidebar.markdown("### TACTICAL DISPLAY LAYERS")
st.sidebar.caption("Curved reinforced-concrete dam")
st.sidebar.caption("Canyon rock and reservoir water")
st.sidebar.caption("Simulated ROV, sonar and defect locations")
st.sidebar.warning("SIMULATION ONLY // Sensor values and defect detections are not live field measurements.")

# ------------------------- GEOMETRY HELPERS -------------------------

def dam_curve(x):
    """Curved dam plan profile; downstream face is toward lower Y."""
    return 5.0 + 0.018 * (x - DAM_WIDTH / 2) ** 2

def dam_front_y(x):
    return dam_curve(x) - DAM_THICKNESS / 2

def rov_y(x):
    return dam_front_y(x) - ROV_OFFSET

def add_box(fig, cx, cy, cz, sx, sy, sz, color, name,
            opacity=1.0, showlegend=True):
    """Add a rectangular 3D solid using Mesh3d."""
    vertices = [
        (cx-sx/2, cy-sy/2, cz-sz/2),
        (cx+sx/2, cy-sy/2, cz-sz/2),
        (cx+sx/2, cy+sy/2, cz-sz/2),
        (cx-sx/2, cy+sy/2, cz-sz/2),
        (cx-sx/2, cy-sy/2, cz+sz/2),
        (cx+sx/2, cy-sy/2, cz+sz/2),
        (cx+sx/2, cy+sy/2, cz+sz/2),
        (cx-sx/2, cy+sy/2, cz+sz/2),
    ]
    i = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
    j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
    k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]
    fig.add_trace(go.Mesh3d(
        x=[v[0] for v in vertices],
        y=[v[1] for v in vertices],
        z=[v[2] for v in vertices],
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        flatshading=True,
        name=name,
        showlegend=showlegend,
        hoverinfo="name"
    ))

def add_rock_bank(fig, x_start, x_end, side_name):
    """Rough stepped canyon bank on either side of the dam."""
    xs = [x_start + (x_end-x_start)*i/12 for i in range(13)]
    ys = [-3 + 0.35*math.sin(i*1.7) for i in range(13)]
    zs = [2 + 0.8*math.sin(i*1.2) for i in range(13)]
    # A sloping rock mass behind the dam ends
    top_y = [y + (2.5 if side_name == "left" else -2.5) for y in ys]
    top_z = [z + 5 + 1.1*math.cos(i*0.8) for i, z in enumerate(zs)]
    xx = xs + xs
    yy = ys + top_y
    zz = zs + top_z
    n = len(xs)
    ii, jj, kk = [], [], []
    for q in range(n-1):
        ii.extend([q, q])
        jj.extend([q+1, q+1])
        kk.extend([q+n, q+n+1])
    fig.add_trace(go.Mesh3d(
        x=xx, y=yy, z=zz, i=ii, j=jj, k=kk,
        color="#625f58", opacity=0.92,
        flatshading=True, name=f"{side_name.title()} canyon rock",
        showlegend=False, hoverinfo="skip"
    ))

# ------------------------- 3D SCENE -------------------------

def create_scene(rov_x, rov_z, sonar_angle, turbidity, route_points=None):
    fig = go.Figure()
    route_points = route_points or ROUTE

    # Canyon floor / reservoir bed
    floor_x = [-5, 29, 29, -5]
    floor_y = [-12, -12, 13, 13]
    floor_z = [0, 0, 0, 0]
    fig.add_trace(go.Mesh3d(
        x=floor_x, y=floor_y, z=floor_z,
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#4a4c4a", opacity=0.95,
        name="Reservoir bed", showlegend=True
    ))

    # Rocky canyon walls / banks framing the dam
    add_rock_bank(fig, -5, 1, "left")
    add_rock_bank(fig, 23, 29, "right")

    # Dam concrete body: curved front and rear faces
    xs = [i * DAM_WIDTH / 48 for i in range(49)]
    zs = [i * DAM_HEIGHT / 32 for i in range(33)]
    front_x, front_y, front_z = [], [], []
    rear_x, rear_y, rear_z = [], [], []

    for z in zs:
        fx, fy, fz = [], [], []
        rx, ry, rz = [], [], []
        for x in xs:
            curve = dam_curve(x)
            fx.append(x); fy.append(curve - DAM_THICKNESS/2); fz.append(z)
            rx.append(x); ry.append(curve + DAM_THICKNESS/2); rz.append(z)
        front_x.append(fx); front_y.append(fy); front_z.append(fz)
        rear_x.append(rx); rear_y.append(ry); rear_z.append(rz)

    # Subtle mottled concrete color texture
    concrete_texture = []
    for z in zs:
        row = []
        for x in xs:
            v = 0.52 + 0.12*math.sin(x*1.8)*math.cos(z*1.3) + 0.06*math.sin(x*z)
            row.append(v)
        concrete_texture.append(row)

    fig.add_trace(go.Surface(
        x=front_x, y=front_y, z=front_z,
        surfacecolor=concrete_texture,
        colorscale=[
            [0.0, "#555d62"], [0.25, "#747d82"],
            [0.55, "#92999b"], [0.8, "#a7adae"], [1.0, "#737c81"]
        ],
        cmin=0.25, cmax=0.8, showscale=False,
        opacity=1, name="Curved concrete dam",
        hovertemplate="Concrete dam<br>X: %{x:.1f} m<br>Z: %{z:.1f} m<extra></extra>"
    ))

    # Rear surface to give the dam real thickness
    fig.add_trace(go.Surface(
        x=rear_x, y=rear_y, z=rear_z,
        colorscale=[[0, "#59636a"], [1, "#879198"]],
        showscale=False, opacity=0.96,
        name="Dam rear face", showlegend=False, hoverinfo="skip"
    ))

    # Top curved crest surface joining front and rear faces
    crest_y_front = [dam_curve(x)-DAM_THICKNESS/2 for x in xs]
    crest_y_back = [dam_curve(x)+DAM_THICKNESS/2 for x in xs]
    fig.add_trace(go.Mesh3d(
        x=xs+xs,
        y=crest_y_front+crest_y_back,
        z=[DAM_HEIGHT]*len(xs)*2,
        i=list(range(len(xs)-1))+list(range(len(xs), 2*len(xs)-1)),
        j=list(range(1, len(xs)))+list(range(len(xs)+1, 2*len(xs))),
        k=list(range(len(xs), 2*len(xs)))+list(range(1, len(xs))),
        color="#aeb5b7", opacity=1,
        name="Dam crest", showlegend=False
    ))

    # Vertical structural contraction joints on the front face
    for px in [4, 8, 12, 16, 20]:
        py = dam_front_y(px) - 0.035
        fig.add_trace(go.Scatter3d(
            x=[px, px], y=[py, py], z=[0, DAM_HEIGHT],
            mode="lines",
            line=dict(color="#414b50", width=3),
            showlegend=False, hoverinfo="skip"
        ))

    # Horizontal construction joints
    for pz in [4, 8, 12]:
        line_x = [i*0.25 for i in range(97)]
        line_y = [dam_front_y(x)-0.04 for x in line_x]
        fig.add_trace(go.Scatter3d(
            x=line_x, y=line_y, z=[pz]*len(line_x),
            mode="lines",
            line=dict(color="#69747a", width=2),
            showlegend=False, hoverinfo="skip"
        ))

    # Water surface across reservoir
    water_x = [-4, 28, 28, -4]
    water_y = [-11, -11, 12, 12]
    water_z = [WATER_LEVEL]*4
    fig.add_trace(go.Mesh3d(
        x=water_x, y=water_y, z=water_z,
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#087fa5", opacity=0.20,
        name="Reservoir water surface"
    ))

    # Water level line
    fig.add_trace(go.Scatter3d(
        x=[-4, 28], y=[-1, -1], z=[WATER_LEVEL]*2,
        mode="lines",
        line=dict(color="#43c9e8", width=4, dash="dash"),
        name="Water level"
    ))

    # Defects positioned on curved front face
    # Crack: jagged line
    crack_x = [5.0, 5.25, 5.05, 5.45, 5.3, 5.65, 5.55]
    crack_z = [13.2, 12.8, 12.3, 11.9, 11.4, 11.0, 10.6]
    crack_y = [dam_front_y(v)-0.09 for v in crack_x]
    fig.add_trace(go.Scatter3d(
        x=crack_x, y=crack_y, z=crack_z,
        mode="lines",
        line=dict(color="#ff392e", width=7),
        name="Crack defect"
    ))

    # Erosion patch, irregular cluster
    erosion_points = [
        (10.0, 7.0), (10.4, 7.4), (10.9, 7.2),
        (11.1, 6.8), (10.7, 6.4), (10.2, 6.5),
        (9.9, 6.8), (10.5, 6.9)
    ]
    fig.add_trace(go.Scatter3d(
        x=[p[0] for p in erosion_points],
        y=[dam_front_y(p[0])-0.1 for p in erosion_points],
        z=[p[1] for p in erosion_points],
        mode="markers",
        marker=dict(color="#f39a32", size=7, symbol="circle"),
        name="Erosion region"
    ))

    # Spalling patch
    fig.add_trace(go.Scatter3d(
        x=[17.3, 17.7, 18.0, 17.6, 17.2],
        y=[dam_front_y(v)-0.11 for v in [17.3,17.7,18.0,17.6,17.2]],
        z=[4.0, 4.4, 4.0, 3.6, 3.7],
        mode="markers",
        marker=dict(color="#ff5b4d", size=9, symbol="circle"),
        name="Spalling"
    ))

    # Seepage indicator
    seep_x = [20.0, 20.2, 20.1, 20.4]
    fig.add_trace(go.Scatter3d(
        x=seep_x,
        y=[dam_front_y(v)-0.1 for v in seep_x],
        z=[9.5, 9.0, 8.5, 8.0],
        mode="lines+markers",
        line=dict(color="#48d9ed", width=5, dash="dot"),
        marker=dict(size=4, color="#48d9ed"),
        name="Suspected seepage"
    ))

    # Planned and completed route
    route_x = [p[0] for p in route_points]
    route_z = [p[1] for p in route_points]
    route_y = [rov_y(p[0]) for p in ROUTE]
    fig.add_trace(go.Scatter3d(
        x=route_x, y=route_y, z=route_z,
        mode="lines",
        line=dict(color="#e7f2f5", width=4, dash="dot"),
        name="Planned ROV route"
    ))

    done = route_points[:st.session_state.step+1]
    fig.add_trace(go.Scatter3d(
        x=[p[0] for p in done],
        y=[rov_y(p[0]) for p in done],
        z=[p[1] for p in done],
        mode="lines+markers",
        line=dict(color="#55ff88", width=7),
        marker=dict(size=3, color="#55ff88"),
        name="Completed route"
    ))

    # Obstacle rock in the water near route
    ox, oy, oz = 13.0, rov_y(13.0)+1.0, 7.0
    fig.add_trace(go.Mesh3d(
        x=[ox-0.8, ox+0.8, ox, ox, ox-0.6, ox+0.6],
        y=[oy-0.5, oy-0.5, oy+0.7, oy, oy+0.4, oy+0.4],
        z=[oz-0.5, oz-0.5, oz, oz+1.0, oz+0.3, oz+0.3],
        i=[0,0,1,1,2,3,4,5],
        j=[1,2,2,3,3,4,5,0],
        k=[2,3,3,4,4,5,0,1],
        color="#b47b42", opacity=0.95,
        name="Submerged obstacle"
    ))

    # ROV position
    ry = rov_y(rov_x)
    rz = rov_z

    # Main ROV body: yellow industrial submersible
    add_box(fig, rov_x, ry, rz, 1.65, 0.85, 0.65,
            "#e6b82f", "AQUA-SCAN ROV body")

    # Top equipment pod
    add_box(fig, rov_x, ry, rz+0.43, 0.75, 0.55, 0.22,
            "#303d48", "ROV electronics pod", showlegend=False)

    # Front camera housing and lens
    add_box(fig, rov_x, ry-0.49, rz+0.02, 0.38, 0.16, 0.32,
            "#26343e", "ROV camera housing", showlegend=False)
    fig.add_trace(go.Scatter3d(
        x=[rov_x], y=[ry-0.59], z=[rz+0.02],
        mode="markers",
        marker=dict(color="#62eaff", size=7, symbol="circle"),
        name="Inspection camera"
    ))

    # Four thruster pods
    for dx in [-0.62, 0.62]:
        for dz in [-0.22, 0.22]:
            add_box(fig, rov_x+dx, ry+0.38, rz+dz,
                    0.28, 0.5, 0.22, "#202a33",
                    "ROV thruster", showlegend=False)

    # Front lights
    for dx in [-0.42, 0.42]:
        fig.add_trace(go.Scatter3d(
            x=[rov_x+dx], y=[ry-0.61], z=[rz+0.2],
            mode="markers",
            marker=dict(color="#fff4b0", size=7),
            showlegend=False, hoverinfo="skip"
        ))

    # Sonar scan beam directed from ROV toward the dam
    beam_angle = math.radians(sonar_angle)
    beam_end_x = max(0, min(DAM_WIDTH, rov_x + 2.0*math.sin(beam_angle)))
    beam_end_z = max(0, min(DAM_HEIGHT, rov_z + 1.5*math.cos(beam_angle)))
    fig.add_trace(go.Scatter3d(
        x=[rov_x, beam_end_x],
        y=[ry-0.65, dam_front_y(beam_end_x)-0.12],
        z=[rov_z, beam_end_z],
        mode="lines",
        line=dict(color="#39eaff", width=6),
        name="Sonar beam"
    ))

    # A soft sonar cone-like triangular fan
    fig.add_trace(go.Mesh3d(
        x=[rov_x, beam_end_x-0.8, beam_end_x+0.8],
        y=[ry-0.62, dam_front_y(beam_end_x)-0.10,
           dam_front_y(beam_end_x)-0.10],
        z=[rov_z, beam_end_z-0.8, beam_end_z+0.8],
        i=[0], j=[1], k=[2],
        color="#22d9f2", opacity=0.12,
        name="Sonar coverage"
    ))

    # Scene layout
    fig.update_layout(
        template="plotly_dark",
        height=760,
        title=dict(
            text="AQUA-SCAN | Curved Dam & Underwater Inspection Zone",
            x=0.02, font=dict(size=20)
        ),
        scene=dict(
            xaxis=dict(title="Dam span (m)", range=[-4, 28],
                       backgroundcolor="#102637", gridcolor="#355064"),
            yaxis=dict(title="Reservoir depth / stand-off (m)", range=[-13, 14],
                       backgroundcolor="#0b3047", gridcolor="#355064"),
            zaxis=dict(title="Elevation (m)", range=[0, 18],
                       backgroundcolor="#102637", gridcolor="#355064"),
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=1.15, z=1.0),
            camera=dict(eye=dict(x=1.75, y=-2.25, z=1.35),
                        center=dict(x=0, y=0, z=0)),
            bgcolor="#092033"
        ),
        paper_bgcolor="#081722",
        plot_bgcolor="#081722",
        margin=dict(l=0, r=0, t=65, b=5),
        legend=dict(orientation="h", y=-0.08, x=0.01),
        uirevision="aquascan-scene"
    )

    return fig

# ------------------------- SONAR RADAR -------------------------

def create_sonar(angle):
    sonar = go.Figure()
    sonar.add_trace(go.Scatterpolar(
        r=[0, 10], theta=[angle, angle],
        mode="lines",
        line=dict(color="#35eaff", width=5),
        name="Sonar sweep"
    ))
    sonar.add_trace(go.Scatterpolar(
        r=[6], theta=[45],
        mode="markers",
        marker=dict(color="#ff9e35", size=13),
        name="Obstacle return"
    ))
    sonar.add_trace(go.Scatterpolar(
        r=[4.5], theta=[125],
        mode="markers",
        marker=dict(color="#ff4545", size=11),
        name="Wall return"
    ))
    sonar.update_layout(
        template="plotly_dark",
        height=360,
        title="Acoustic sonar scanner (simulated)",
        polar=dict(
            bgcolor="#09283b",
            radialaxis=dict(range=[0, 10], gridcolor="#31566b"),
            angularaxis=dict(gridcolor="#31566b")
        ),
        paper_bgcolor="#081722",
        margin=dict(l=25, r=25, t=55, b=20)
    )
    return sonar

# ------------------------- LIVE SIMULATION -------------------------

@st.fragment(run_every=0.8)
def live_simulation():

    target_depth = st.session_state.target_depth
    turbidity = st.session_state.water_turbidity

    # Simulated sonar obstacle detection and automatic route replanning.
    # The obstacle is a configured demonstration target, not a live sensor reading.
    if st.session_state.running:
        if st.session_state.step < len(st.session_state.route_points) - 1:
            st.session_state.step += 1
            st.session_state.battery = max(
                0, st.session_state.battery - 0.10
            )
        else:
            st.session_state.running = False

        st.session_state.depth += (
            target_depth - st.session_state.depth
        ) * 0.15
        st.session_state.heading = random.randint(85, 100)
        st.session_state.sonar_angle = (
            st.session_state.sonar_angle + 18
        ) % 360

    # When the ROV reaches the obstacle approach zone, insert two detour
    # waypoints above the obstacle and then rejoin the planned route.
    if (st.session_state.running
            and st.session_state.step >= 5
            and not st.session_state.obstacle_avoided):
        st.session_state.route_points = (
            list(ROUTE[:5]) + [(12.0, 10.0), (14.0, 10.0)] + list(ROUTE[6:])
        )
        st.session_state.obstacle_avoided = True

    active_route = st.session_state.route_points
    x, z = active_route[min(st.session_state.step, len(active_route) - 1)]

    # Demonstration proximity-based defect flags
    if st.session_state.running:
        for index, defect in enumerate(DEFECTS):
            distance = math.sqrt(
                (x-defect["x"])**2 + (z-defect["z"])**2
            )
            if distance <= 3.2 and index not in st.session_state.detected_defects:
                st.session_state.detected_defects.append(index)

    st.markdown('<div class="section-tag">01 // VEHICLE TELEMETRY</div>', unsafe_allow_html=True)
    st.markdown("## LIVE PLATFORM STATUS")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Depth", f"{st.session_state.depth:.1f} m")
    c2.metric("Heading", f"{st.session_state.heading}°")
    c3.metric("Turbidity", f"{turbidity} NTU")
    c4.metric("Battery", f"{st.session_state.battery:.1f}%")

    progress = st.session_state.step / (len(active_route)-1)
    st.progress(progress, text=f"Inspection progress: {progress*100:.0f}%")

    st.divider()
    st.markdown('<div class="section-tag">02 // TACTICAL DIGITAL TWIN</div>', unsafe_allow_html=True)
    st.markdown("## 3D INSPECTION THEATRE")
    st.caption("TACTICAL VIEW // Drag to rotate • Scroll to zoom • Right-click and drag to pan")
    fig = create_scene(
        x, z, st.session_state.sonar_angle, turbidity, active_route
    )
    st.plotly_chart(fig, width="stretch", key="aquascan_3d_scene")

    st.divider()
    st.markdown('<div class="section-tag">03 // ACOUSTIC SENSOR ARRAY</div>', unsafe_allow_html=True)
    st.markdown("## SONAR CONTACT MONITOR")
    sonar_col, info_col = st.columns([2, 1])
    with sonar_col:
        st.plotly_chart(
            create_sonar(st.session_state.sonar_angle),
            width="stretch",
            key="aquascan_sonar"
        )
    with info_col:
        st.markdown("### Sonar readings")
        st.metric("Scan angle", f"{st.session_state.sonar_angle}°")
        st.metric("Simulated obstacle range", "6.0 m")
        st.metric(
            "Scanner status",
            "Active" if st.session_state.running else "Standby"
        )
        st.info(
            "Cyan beam represents the simulated sonar scan. "
            "Orange and red returns are demonstration targets."
        )

    st.markdown("### NAVIGATION / THREAT DECONFLICTION")
    if st.session_state.obstacle_avoided:
        st.success(
            "Simulated sonar obstacle alert: obstacle detected near the "
            "planned path. Two detour waypoints were inserted and the ROV "
            "has rejoined the inspection route."
        )
        st.metric("Navigation mode", "Detour / rejoin")
    else:
        st.info(
            "Obstacle avoidance is armed. The demonstration obstacle is "
            "ahead of the ROV; the route will be replanned when the ROV "
            "reaches the configured detection zone."
        )
        st.metric("Navigation mode", "Planned route")
    st.caption(
        "This is a scripted navigation demonstration using a predefined "
        "obstacle location. It is not live sonar-based autonomous navigation."
    )

    # ============================================================
    # AI DEFECT INTELLIGENCE & RISK ASSESSMENT
    # Rule-based demonstration layer (not a trained AI model)
    # ============================================================
    st.divider()
    st.markdown('<div class="section-tag">04 // STRUCTURAL ANOMALY INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown("## DETECTED TARGETS & RISK CLASSIFICATION")
    detected = st.session_state.detected_defects

    risk_values = {
        "Crack": 90,
        "Surface erosion": 65,
        "Spalling": 85,
        "Seepage indicator": 70,
    }

    recommendations = {
        "Crack": "Perform detailed crack inspection and structural assessment.",
        "Surface erosion": "Inspect the concrete surface for material loss and progression.",
        "Spalling": "Prioritise concrete condition assessment and repair planning.",
        "Seepage indicator": "Verify suspected seepage using flow or pressure measurements.",
    }

    if detected:
        report_rows = []
        for index in detected:
            defect = DEFECTS[index]
            risk = risk_values.get(defect["kind"], 50)
            if risk >= 80:
                priority = "HIGH"
            elif risk >= 60:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            report_rows.append({
                "Defect": defect["kind"],
                "Severity": defect["severity"],
                "Risk Score (demonstration)": risk,
                "Priority": priority,
                "X Coordinate (m)": defect["x"],
                "Z Coordinate (m)": defect["z"],
                "Recommended Action": recommendations[defect["kind"]],
            })

        high = sum(row["Priority"] == "HIGH" for row in report_rows)
        medium = sum(row["Priority"] == "MEDIUM" for row in report_rows)
        low = sum(row["Priority"] == "LOW" for row in report_rows)

        a, b, c, d = st.columns(4)
        a.metric("Contacts acquired", len(report_rows))
        b.metric("Priority-1 / High", high)
        c.metric("Priority-2 / Medium", medium)
        d.metric("Priority-3 / Low", low)

        st.markdown("### TARGET ACQUISITION REGISTER")
        st.caption("Each contact is assigned a unique target ID, coordinate lock and demonstration risk index.")
        for card_index, row in enumerate(report_rows, start=1):
            risk = row["Risk Score (demonstration)"]
            priority = row["Priority"]
            color = "#ff5b58" if priority == "HIGH" else ("#ffbd4a" if priority == "MEDIUM" else "#a6ff4d")
            st.markdown(f"""
            <div class="target-card" style="--target-color:{color}">
              <div class="target-top">
                <span class="target-id">CONTACT // AS-{card_index:03d} &nbsp; • &nbsp; STRUCTURAL ANOMALY</span>
                <span class="target-chip">{priority} PRIORITY</span>
              </div>
              <div class="target-kind">{row['Defect']}</div>
              <div class="target-grid">
                <div><div class="target-label">RISK INDEX</div><div class="target-value">{risk:02d} / 100</div></div>
                <div><div class="target-label">X COORDINATE</div><div class="target-value">{row['X Coordinate (m)']:.1f} M</div></div>
                <div><div class="target-label">Z COORDINATE</div><div class="target-value">{row['Z Coordinate (m)']:.1f} M</div></div>
              </div>
              <div class="target-meter"><div class="target-meter-fill" style="width:{risk}%;"></div></div>
              <div class="target-foot">RECORDED SEVERITY: {row['Severity'].upper()} &nbsp; // &nbsp; CLASSIFICATION: RULE-BASED DEMONSTRATION</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"OPEN TARGET FILE // AS-{card_index:03d}"):
                st.write(f"**Recommended inspection action:** {row['Recommended Action']}")
                st.write("**Verification state:** Pending qualified inspector review")

        # Create a downloadable CSV inspection report
        report_buffer = io.StringIO()
        writer = csv.DictWriter(report_buffer, fieldnames=list(report_rows[0].keys()))
        writer.writeheader()
        writer.writerows(report_rows)

        st.download_button(
            label="EXPORT STRUCTURAL INTELLIGENCE REPORT",
            data=report_buffer.getvalue(),
            file_name="AQUA_SCAN_Inspection_Report.csv",
            mime="text/csv",
            key="aquascan_download_report",
        )
    else:
        st.info("No defects scanned yet. Start the ROV inspection mission.")

    st.metric("Defects flagged in simulation", len(detected))
    st.caption(
        "Note: detections are simulated from predefined defect locations. "
        "Risk scores are illustrative rule-based values, not trained AI predictions."
    )

    # ============================================================
    # UNDERWATER CAMERA IMAGE ANALYSIS
    # OpenCV visibility enhancement and crack-candidate detection
    # ============================================================
    st.divider()
    st.markdown('<div class="section-tag">05 // OPTICAL RECONNAISSANCE</div>', unsafe_allow_html=True)
    st.markdown("## CAMERA-BASED SURFACE ANALYSIS")
    st.caption(
        "Upload an underwater concrete inspection image. AQUA-SCAN "
        "enhances local contrast and highlights possible crack-like regions."
    )

    uploaded_image = st.file_uploader(
        "Upload underwater inspection image",
        type=["jpg", "jpeg", "png"],
        key="aquascan_camera_upload"
    )

    if uploaded_image is not None:
        try:
            image_bytes = np.frombuffer(uploaded_image.getvalue(), dtype=np.uint8)
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

            if image is None:
                st.error("Unable to read this image. Please upload another JPG or PNG.")
            else:
                original = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Local contrast enhancement; useful for uneven illumination.
                clahe = cv2.createCLAHE(
                    clipLimit=2.5,
                    tileGridSize=(8, 8)
                )
                enhanced = clahe.apply(gray)

                # Morphological black-hat response highlights dark thin features.
                kernel_horizontal = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (17, 3)
                )
                kernel_vertical = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (3, 17)
                )
                blackhat_h = cv2.morphologyEx(
                    enhanced, cv2.MORPH_BLACKHAT, kernel_horizontal
                )
                blackhat_v = cv2.morphologyEx(
                    enhanced, cv2.MORPH_BLACKHAT, kernel_vertical
                )
                crack_response = cv2.max(blackhat_h, blackhat_v)

                _, binary = cv2.threshold(
                    crack_response,
                    0,
                    255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                clean_kernel = np.ones((3, 3), np.uint8)
                cleaned = cv2.morphologyEx(
                    binary, cv2.MORPH_OPEN, clean_kernel
                )

                contours, _ = cv2.findContours(
                    cleaned,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                result = original.copy()
                candidate_count = 0
                image_area = gray.shape[0] * gray.shape[1]

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < 8:
                        continue

                    x_box, y_box, box_w, box_h = cv2.boundingRect(contour)
                    if box_w * box_h > image_area * 0.15:
                        continue

                    candidate_count += 1
                    cv2.rectangle(
                        result,
                        (x_box, y_box),
                        (x_box + box_w, y_box + box_h),
                        (255, 40, 40),
                        2
                    )
                    cv2.putText(
                        result,
                        "Crack candidate",
                        (x_box, max(20, y_box - 7)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 40, 40),
                        1
                    )

                st.markdown("### Image processing results")
                img_col1, img_col2 = st.columns(2)
                with img_col1:
                    st.image(
                        original,
                        caption="Original underwater image",
                        width="stretch"
                    )
                with img_col2:
                    st.image(
                        enhanced,
                        caption="CLAHE contrast-enhanced grayscale image",
                        width="stretch"
                    )

                st.markdown("### ANOMALY OVERLAY / CANDIDATE REGIONS")
                st.image(
                    result,
                    caption="Red boxes show possible crack-like image regions",
                    width="stretch"
                )

                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric("Potential regions", candidate_count)
                metric_col2.metric(
                    "Image resolution",
                    f"{gray.shape[1]} × {gray.shape[0]}"
                )

                if candidate_count:
                    st.warning(
                        f"{candidate_count} possible crack-like region(s) found. "
                        "A qualified inspector must verify them."
                    )
                else:
                    st.info(
                        "No crack-like regions were found with the current "
                        "image-processing settings. This does not prove the "
                        "surface is defect-free."
                    )

                st.caption(
                    "Technical limitation: this is classical OpenCV image "
                    "processing (CLAHE, morphology and thresholding), not a "
                    "trained AI model. It may produce false positives or miss "
                    "real defects, especially in highly turbid images."
                )

                # Save images and an inspection record only when requested.
                st.markdown("### EVIDENCE ARCHIVE / SAVE INSPECTION RECORD")
                st.caption(
                    "Save the uploaded original image, the processed image "
                    "with highlighted candidates, and a CSV record locally."
                )

                if st.button(
                    "ARCHIVE IMAGES + INSPECTION RECORD",
                    key="aquascan_save_inspection"
                ):
                    try:
                        base_folder = "inspection_images"
                        original_folder = os.path.join(base_folder, "original")
                        processed_folder = os.path.join(base_folder, "processed")
                        os.makedirs(original_folder, exist_ok=True)
                        os.makedirs(processed_folder, exist_ok=True)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_stem = os.path.splitext(uploaded_image.name)[0]
                        safe_stem = "".join(
                            ch if ch.isalnum() or ch in "-_" else "_"
                            for ch in safe_stem
                        )[:40] or "inspection"
                        file_stem = f"{safe_stem}_{timestamp}"

                        original_path = os.path.join(
                            original_folder, f"{file_stem}.jpg"
                        )
                        processed_path = os.path.join(
                            processed_folder, f"{file_stem}_processed.jpg"
                        )

                        # Store original image bytes without altering them.
                        with open(original_path, "wb") as image_file:
                            image_file.write(uploaded_image.getvalue())

                        # Store processed result as a JPEG image.
                        processed_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
                        if not cv2.imwrite(processed_path, processed_bgr):
                            raise OSError("Could not write the processed image.")

                        log_path = os.path.join(base_folder, "inspection_log.csv")
                        log_exists = os.path.exists(log_path)
                        with open(log_path, "a", newline="", encoding="utf-8") as log_file:
                            fieldnames = [
                                "inspection_datetime", "source_filename",
                                "saved_original", "saved_processed",
                                "potential_crack_like_regions", "image_width_px",
                                "image_height_px", "analysis_method", "verification_status"
                            ]
                            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
                            if not log_exists:
                                writer.writeheader()
                            writer.writerow({
                                "inspection_datetime": datetime.now().isoformat(timespec="seconds"),
                                "source_filename": uploaded_image.name,
                                "saved_original": original_path,
                                "saved_processed": processed_path,
                                "potential_crack_like_regions": candidate_count,
                                "image_width_px": gray.shape[1],
                                "image_height_px": gray.shape[0],
                                "analysis_method": "OpenCV CLAHE + blackhat morphology + Otsu threshold",
                                "verification_status": "Pending manual verification"
                            })

                        st.success("Inspection images and record saved successfully!")
                        st.write(f"**Original:** `{original_path}`")
                        st.write(f"**Processed:** `{processed_path}`")
                        st.write(f"**Inspection log:** `{log_path}`")
                    except Exception as save_error:
                        st.error(f"Could not save inspection: {save_error}")

        except Exception as e:
            st.error(f"Image analysis error: {e}")
    else:
        st.info(
            "Upload a JPG or PNG underwater concrete image to run the "
            "camera image-processing demonstration."
        )

    st.divider()
    st.markdown('<div class="section-tag">06 // MISSION SUMMARY</div>', unsafe_allow_html=True)
    st.markdown("## OPERATIONAL STATUS")
    if st.session_state.running:
        st.success("ROV is actively following the inspection route.")
    elif progress >= 1:
        st.success("Inspection route completed.")
    else:
        st.info("ROV is waiting for the start command.")

    st.caption(
        "AQUA-SCAN | Curved dam digital twin with simulated navigation, "
        "sonar, scripted obstacle avoidance and preconfigured defect locations."
    )

live_simulation()
