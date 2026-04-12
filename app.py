"""
RehabAI v2.0 – Real-time Recovery Intelligence System
Upgraded: Realistic body visualization, exercise modes, dynamic joint highlights,
improved UI polish, and cleaner code structure.
"""

import streamlit as st
import numpy as np
import math
import time
from datetime import datetime
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RehabAI · Recovery Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
EXERCISE_CONFIG = {
    "Shoulder Flexion": {
        "description": "Raise arm forward from resting position",
        "target_angle": 90,
        "correct_min": 80,
        "almost_min": 60,
        "joint_label": "Shoulder",
        "mediapipe_joints": ("RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_HIP"),
        "icon": "💪",
    },
    "Elbow Flexion": {
        "description": "Bend elbow bringing hand toward shoulder",
        "target_angle": 90,
        "correct_min": 75,
        "almost_min": 55,
        "joint_label": "Elbow",
        "mediapipe_joints": ("RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"),
        "icon": "🦾",
    },
    "Knee Extension": {
        "description": "Straighten knee from seated position",
        "target_angle": 150,
        "correct_min": 140,
        "almost_min": 120,
        "joint_label": "Knee",
        "mediapipe_joints": ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"),
        "icon": "🦵",
    },
    "Hip Abduction": {
        "description": "Move leg outward away from body",
        "target_angle": 30,
        "correct_min": 25,
        "almost_min": 15,
        "joint_label": "Hip",
        "mediapipe_joints": ("RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE"),
        "icon": "🏃",
    },
}

STATUS_COLORS = {
    "Correct":   {"hex": "#16a34a", "bg": "#f0fdf4", "border": "#22c55e", "text": "#14532d"},
    "Almost":    {"hex": "#ea580c", "bg": "#fff7ed", "border": "#f97316", "text": "#7c2d12"},
    "Incorrect": {"hex": "#dc2626", "bg": "#fff1f2", "border": "#f43f5e", "text": "#881337"},
}

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@400;600;700;800&display=swap');

/* ── Root & Layout ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Sora', sans-serif;
    background: #eef2f7;
}
[data-testid="stSidebar"]   { background: #06101f; border-right: 1px solid #0f2040; }
[data-testid="stSidebar"] * { color: #c9d8ee !important; }
[data-testid="stSidebar"] .stButton button {
    width: 100%; border-radius: 10px;
    font-weight: 700; letter-spacing: .04em;
    font-family: 'Sora', sans-serif;
}
#MainMenu, header, footer { visibility: hidden; }

/* ── Top Header Bar ── */
.top-bar {
    background: linear-gradient(120deg, #1347b0 0%, #0284c7 100%);
    border-radius: 18px; padding: 18px 28px;
    color: white; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 24px rgba(19,71,176,.22);
}
.top-bar-title { font-size: 22px; font-weight: 800; letter-spacing: -.02em; }
.top-bar-sub   { font-size: 13px; opacity: .75; margin-top: 3px; font-weight: 400; }
.top-bar-badge {
    background: rgba(255,255,255,.18); border-radius: 20px;
    padding: 5px 16px; font-size: 12px; font-weight: 700;
    letter-spacing: .04em; backdrop-filter: blur(4px);
}
.top-bar-time  { font-family: 'IBM Plex Mono', monospace; font-size: 12px; opacity:.6; margin-top:5px; }

/* ── KPI Cards ── */
.kpi-card {
    background: white; border-radius: 16px;
    padding: 18px 20px; text-align: center;
    box-shadow: 0 2px 14px rgba(6,16,31,.08);
    border: 1px solid #dde5f0;
    height: 115px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    transition: box-shadow .2s;
}
.kpi-card:hover { box-shadow: 0 4px 20px rgba(6,16,31,.13); }
.kpi-label { font-size: 10px; font-weight: 700; letter-spacing: .1em;
             text-transform: uppercase; color: #6b7a99; margin-bottom: 6px; }
.kpi-value { font-size: 34px; font-weight: 800; line-height: 1; font-family: 'Sora', sans-serif; }
.kpi-sub   { font-size: 11px; color: #94a3b8; margin-top: 4px; }

/* ── Status Colors ── */
.c-green  { color: #15803d; } .c-orange { color: #c2570a; }
.c-red    { color: #b91c1c; } .c-blue   { color: #1d4ed8; }

/* ── Section Cards ── */
.section-card {
    background: white; border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(6,16,31,.06);
    border: 1px solid #dde5f0; margin-bottom: 16px;
}
.section-label {
    font-size: 10px; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #1d4ed8;
    border-bottom: 2px solid #bfdbfe;
    padding-bottom: 8px; margin-bottom: 16px;
}

/* ── Recommendation Box ── */
.rec-box {
    border-radius: 12px; padding: 16px 20px;
    font-size: 14px; line-height: 1.7; font-weight: 500;
    border-left: 5px solid;
}
.rec-green  { background:#f0fdf4; border-color:#22c55e; color:#14532d; }
.rec-orange { background:#fff7ed; border-color:#f97316; color:#7c2d12; }
.rec-red    { background:#fff1f2; border-color:#f43f5e; color:#881337; }

/* ── Insight Rows ── */
.insight-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px;
}
.insight-key   { color: #64748b; font-weight: 500; }
.insight-value { font-weight: 800; font-size: 15px; }

/* ── Session Tiles ── */
.sess-tile {
    background: #f8fafc; border-radius: 12px; padding: 14px;
    text-align: center; border: 1px solid #e2e8f0;
}
.sess-num { font-size: 28px; font-weight: 800; }
.sess-lbl { font-size: 10px; color: #64748b; text-transform: uppercase;
            letter-spacing: .08em; margin-top: 3px; font-weight: 600; }

/* ── Exercise badge ── */
.exercise-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 10px; padding: 8px 14px;
    font-size: 13px; font-weight: 700; color: #1d4ed8;
    margin-bottom: 14px;
}
.exercise-desc { font-size: 12px; color: #64748b; margin-bottom: 16px; font-weight: 400; }

/* ── Angle display ── */
.angle-display {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 72px; font-weight: 700; line-height: 1;
    letter-spacing: -.04em;
}
.angle-target-label {
    font-size: 11px; color: #94a3b8; font-weight: 600;
    text-transform: uppercase; letter-spacing: .08em;
    margin-top: 6px;
}

/* ── Joint highlight pulse ── */
@keyframes joint-pulse {
    0%   { r: 7; opacity: 1; }
    50%  { r: 11; opacity: .6; }
    100% { r: 7; opacity: 1; }
}
.active-joint { animation: joint-pulse 1.2s ease-in-out infinite; }

/* ── Skeleton wrap ── */
.skeleton-wrap {
    display: flex; align-items: center; justify-content: center;
    background: #f8fafc; border-radius: 12px;
    min-height: 260px; border: 1.5px dashed #cbd5e1;
}

/* ── Progress bar ── */
.stProgress > div > div { border-radius: 8px !important; }

/* ── Slider label fix ── */
[data-testid="stSlider"] label { color: #c9d8ee !important; }

/* ── Monospace numbers ── */
.mono { font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = dict(
    running=False,
    score_history=[],
    angle_history=[],
    correct_reps=0,
    incorrect_reps=0,
    last_stage="idle",
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, list) else []

# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION & SCORING HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def classify_angle(angle: float, exercise: str) -> dict:
    cfg = EXERCISE_CONFIG[exercise]
    if angle >= cfg["correct_min"]:
        return dict(
            status="Correct", risk="LOW", score_delta=+3,
            icon="✅", rec_cls="rec-green",
            rec=f"Excellent form! Hold at {angle:.0f}° — you've hit the target zone for {exercise}.",
        )
    elif angle >= cfg["almost_min"]:
        return dict(
            status="Almost", risk="MEDIUM", score_delta=+1,
            icon="⚠️", rec_cls="rec-orange",
            rec=f"Almost there — push a little further. Target is {cfg['target_angle']}°.",
        )
    else:
        return dict(
            status="Incorrect", risk="HIGH", score_delta=-2,
            icon="❌", rec_cls="rec-red",
            rec=f"Incorrect range detected. Slow down and increase your {cfg['joint_label']} angle.",
        )

def update_score(delta: int) -> int:
    hist = st.session_state.score_history
    prev = hist[-1] if hist else 50
    return max(0, min(100, prev + delta))

def score_color(s: int) -> str:
    if s >= 70: return "#15803d"
    if s >= 40: return "#c2570a"
    return "#b91c1c"

def kpi_color_class(status: str) -> str:
    return {"Correct": "c-green", "Almost": "c-orange", "Incorrect": "c-red"}.get(status, "c-blue")

def risk_color_class(risk: str) -> str:
    return {"LOW": "c-green", "MEDIUM": "c-orange", "HIGH": "c-red"}.get(risk, "c-blue")

# ─────────────────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def build_score_chart(history: list) -> go.Figure:
    data = history[-30:]
    x = list(range(len(data)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=data, mode="lines",
        line=dict(color="#3b82f6", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
    ))
    fig.update_layout(
        height=140, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 100], gridcolor="#f1f5f9",
                   tickfont=dict(size=10, color="#94a3b8", family="IBM Plex Mono"),
                   zeroline=False),
        showlegend=False,
    )
    return fig

def build_angle_chart(history: list, exercise: str) -> go.Figure:
    data = history[-30:]
    x = list(range(len(data)))
    target = EXERCISE_CONFIG[exercise]["correct_min"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=data, mode="lines+markers",
        line=dict(color="#8b5cf6", width=2, shape="spline"),
        marker=dict(size=4, color="#8b5cf6"),
    ))
    fig.add_hline(
        y=target, line=dict(color="#22c55e", dash="dot", width=1.5),
        annotation_text="Target", annotation_position="right",
        annotation_font=dict(size=10, color="#22c55e"),
    )
    fig.update_layout(
        height=120, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(gridcolor="#f1f5f9",
                   tickfont=dict(size=10, color="#94a3b8", family="IBM Plex Mono"),
                   zeroline=False),
        showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# REALISTIC BODY SVG  (v2.0 — exercise-aware, joint highlights)
# ─────────────────────────────────────────────────────────────────────────────
def body_svg(angle: float, posture: dict, exercise: str) -> str:
    """
    Renders a more realistic medical-illustration-style body figure.
    The active joint is highlighted and animated; limb positions respond
    to the exercise type and current angle.
    """
    status = posture["status"]
    c      = STATUS_COLORS[status]["hex"]
    pulse  = f'class="active-joint"' if st.session_state.running else ""

    # ── Base body geometry (standing figure, 280×400 viewBox) ──
    # Torso, head, base arms/legs are always the same.
    # We override the relevant limb segment per exercise.

    head_cx, head_cy, head_r = 140, 42, 26

    # Spine
    spine_top = (140, 68)
    spine_bot = (140, 195)

    # Shoulder bar
    sh_l = (85, 90); sh_r = (195, 90)

    # Hip bar
    hip_l = (100, 195); hip_r = (180, 195)

    # Default arm positions (resting)
    l_elbow = (70, 145); l_wrist = (65, 195)
    r_elbow = (210, 145); r_wrist = (215, 195)

    # Default leg positions
    l_knee = (95, 260);  l_ankle = (92, 320)
    r_knee = (185, 260); r_ankle = (188, 320)

    # Joint to highlight
    active_joint = None
    active_r = 9

    rad = math.radians(angle)

    # ── Exercise-specific overrides ──
    if exercise == "Shoulder Flexion":
        # Right arm swings forward: shoulder stays fixed, elbow rises
        lift = math.radians(angle)
        r_elbow  = (int(195 + 55 * math.cos(math.radians(270 + angle))),
                    int(90  + 55 * math.sin(math.radians(270 + angle))))
        r_wrist  = (int(r_elbow[0] + 45 * math.cos(math.radians(270 + angle))),
                    int(r_elbow[1] + 45 * math.sin(math.radians(270 + angle))))
        active_joint = sh_r

    elif exercise == "Elbow Flexion":
        # Upper arm fixed downward, forearm bends at elbow
        r_elbow  = (208, 150)
        r_wrist  = (int(208 + 50 * math.cos(math.radians(180 - angle))),
                    int(150 + 50 * math.sin(math.radians(180 - angle))))
        active_joint = r_elbow

    elif exercise == "Knee Extension":
        # Seated position: thigh is horizontal, shin extends
        # Map angle: 0° = fully bent, 150° = fully extended
        r_knee   = (183, 230)
        r_ankle  = (int(183 + 70 * math.cos(math.radians(angle - 90))),
                    int(230 + 70 * math.sin(math.radians(angle - 90))))
        # Tilt hip slightly for seated look
        hip_r    = (178, 200)
        active_joint = r_knee

    elif exercise == "Hip Abduction":
        # Right leg swings outward
        abduct_offset = int(angle * 1.2)
        r_knee   = (185 + abduct_offset // 2, 262)
        r_ankle  = (188 + abduct_offset,      322)
        active_joint = hip_r

    # ── Colour palette ──
    body_stroke  = "#94a3b8"   # inactive joints / lines
    active_color = c           # the exercise limb colour

    # Helper to draw a segment
    def seg(x1, y1, x2, y2, color=body_stroke, width=3, dashed=False):
        dash = 'stroke-dasharray="6 3"' if dashed else ""
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" {dash}/>')

    def joint(cx, cy, r=6, fill="white", stroke=body_stroke, sw=2.5, extra=""):
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def active_jt(cx, cy):
        return (
            f'<circle cx="{cx}" cy="{cy}" r="14" fill="{c}" opacity=".15"/>'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{c}" stroke="white" stroke-width="2.5" {pulse}/>'
        )

    lines = []
    joints = []

    # ── Skeleton body (inactive color) ──
    # Spine
    lines.append(seg(*spine_top, *spine_bot, body_stroke, 3))
    # Shoulder bar
    lines.append(seg(*sh_l, *sh_r, body_stroke, 3))
    # Hip bar
    lines.append(seg(*hip_l, *hip_r, body_stroke, 3))

    # Left arm (always inactive)
    lines.append(seg(*sh_l,    *l_elbow, body_stroke, 2.5))
    lines.append(seg(*l_elbow, *l_wrist, body_stroke, 2.5))

    # Left leg (always inactive)
    lines.append(seg(*hip_l,  *l_knee,  body_stroke, 2.5))
    lines.append(seg(*l_knee, *l_ankle, body_stroke, 2.5))

    # Right leg — active color if knee extension / hip abduction
    leg_color = active_color if exercise in ("Knee Extension", "Hip Abduction") else body_stroke
    lines.append(seg(*hip_r,  *r_knee,  leg_color, 3 if leg_color != body_stroke else 2.5))
    lines.append(seg(*r_knee, *r_ankle, leg_color, 3 if leg_color != body_stroke else 2.5))

    # Right arm — active color if shoulder / elbow flexion
    arm_color = active_color if exercise in ("Shoulder Flexion", "Elbow Flexion") else body_stroke
    upper_arm_end = r_elbow
    lines.append(seg(*sh_r, *upper_arm_end, arm_color, 3 if arm_color != body_stroke else 2.5))
    lines.append(seg(*r_elbow, *r_wrist,   arm_color, 3 if arm_color != body_stroke else 2.5))

    # ── Joints ──
    for pt in [sh_l, sh_r, hip_l, hip_r]:
        joints.append(joint(*pt, r=6))
    for pt in [l_elbow, l_wrist, r_elbow, r_wrist]:
        joints.append(joint(*pt, r=5))
    for pt in [l_knee, l_ankle, r_knee, r_ankle]:
        joints.append(joint(*pt, r=5))

    # Active joint highlight (on top)
    if active_joint:
        joints.append(active_jt(*active_joint))

    # Angle arc annotation near active joint
    angle_ann = ""
    if active_joint:
        ax, ay = active_joint
        angle_ann = (
            f'<rect x="{ax+14}" y="{ay-14}" width="52" height="22" rx="6" '
            f'fill="{c}" opacity=".12"/>'
            f'<text x="{ax+40}" y="{ay+3}" text-anchor="middle" font-size="13" '
            f'fill="{c}" font-weight="700" font-family="IBM Plex Mono, monospace">'
            f'{angle:.0f}°</text>'
        )

    # Status pill
    pill_c = STATUS_COLORS[status]
    status_pill = (
        f'<rect x="70" y="348" width="100" height="24" rx="12" '
        f'fill="{pill_c["hex"]}" opacity=".15"/>'
        f'<text x="120" y="365" text-anchor="middle" font-size="11" '
        f'fill="{pill_c["hex"]}" font-weight="700" font-family="Sora, sans-serif">'
        f'{posture["icon"]} {status}</text>'
    )

    # Exercise label at top
    exercise_label = (
        f'<text x="120" y="386" text-anchor="middle" font-size="10" '
        f'fill="#94a3b8" font-family="Sora, sans-serif" font-weight="600" '
        f'letter-spacing="1">{exercise.upper()}</text>'
    )

    svg_body = "\n".join(lines + joints)

    return f"""
    <svg viewBox="0 0 240 400" width="100%" style="max-height:360px;display:block;margin:0 auto;">
      <!-- Drop shadow filter -->
      <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#00000018"/>
        </filter>
        <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#f8fafc"/>
          <stop offset="100%" stop-color="#f1f5f9"/>
        </linearGradient>
      </defs>

      <!-- Background -->
      <rect width="240" height="400" fill="url(#bodyGrad)" rx="14"/>
      <rect width="240" height="400" fill="none" stroke="#e2e8f0" stroke-width="1.5" rx="14"/>

      <!-- Head (face) -->
      <circle cx="{head_cx}" cy="{head_cy}" r="{head_r}"
              fill="white" stroke="{body_stroke}" stroke-width="2.5" filter="url(#shadow)"/>
      <!-- Simple face dots -->
      <circle cx="133" cy="39" r="2.5" fill="#94a3b8"/>
      <circle cx="147" cy="39" r="2.5" fill="#94a3b8"/>
      <path d="M134 49 Q140 54 146 49" stroke="#94a3b8" stroke-width="1.5"
            fill="none" stroke-linecap="round"/>

      <!-- Body -->
      {svg_body}

      {angle_ann}
      {status_pill}
      {exercise_label}
    </svg>"""

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 RehabAI v2.0")
    st.markdown("---")

    st.markdown("**Patient Profile**")
    patient_name = st.text_input("Name", "Sarah Mitchell",
                                 label_visibility="collapsed", placeholder="Patient name")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", 10, 100, 34, label_visibility="collapsed")
    with col_b:
        st.markdown(f"<div style='padding-top:8px;font-size:13px;'>Age: {age}</div>",
                    unsafe_allow_html=True)
    condition = st.selectbox("Condition", [
        "ACL Recovery", "Shoulder Rehab", "Hip Replacement", "Stroke Recovery", "Custom"
    ])
    st.markdown("---")

    st.markdown("**Exercise Type**")
    exercise = st.selectbox(
        "Exercise",
        list(EXERCISE_CONFIG.keys()),
        format_func=lambda x: f"{EXERCISE_CONFIG[x]['icon']} {x}",
        label_visibility="collapsed",
    )
    st.markdown("---")

    st.markdown("**Monitoring Mode**")
    mode = st.radio("", ["Demo", "Camera"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if mode == "Demo":
        st.markdown("**Simulate Angle**")
        cfg = EXERCISE_CONFIG[exercise]
        demo_angle = st.slider(
            "Joint Angle (°)", 0, 170,
            cfg["almost_min"],
            label_visibility="collapsed",
        )

    target_reps = st.number_input("Target Reps", 5, 50, 15)
    st.markdown("---")

    b1, b2 = st.columns(2)
    with b1:
        start = st.button("▶ Start", type="primary", use_container_width=True)
    with b2:
        stop = st.button("⏹ Stop", use_container_width=True)
    reset = st.button("↺ Reset Session", use_container_width=True)

    if start: st.session_state.running = True
    if stop:  st.session_state.running = False
    if reset:
        for k, v in DEFAULTS.items():
            st.session_state[k] = v if not isinstance(v, list) else []
        st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:11px;color:#475569;text-align:center;line-height:1.9;">
        RehabAI v2.0 · {mode} Mode<br>
        <span style="font-family:'IBM Plex Mono',monospace;">{datetime.now().strftime('%H:%M · %b %d, %Y')}</span>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DETERMINE CURRENT ANGLE & POSTURE
# ─────────────────────────────────────────────────────────────────────────────
if mode == "Demo":
    angle = float(demo_angle)
else:
    angle = st.session_state.angle_history[-1] if st.session_state.angle_history else 0.0

posture = classify_angle(angle, exercise)

# Update histories when running in Demo mode
if st.session_state.running and mode == "Demo":
    new_score = update_score(posture["score_delta"])
    st.session_state.score_history.append(new_score)
    st.session_state.angle_history.append(angle)
    stage = posture["status"].lower()
    if st.session_state.last_stage != stage:
        if stage == "correct" and st.session_state.last_stage in ("almost", "incorrect", "idle"):
            st.session_state.correct_reps += 1
        elif stage == "incorrect":
            st.session_state.incorrect_reps += 1
        st.session_state.last_stage = stage
    if len(st.session_state.score_history) > 200:
        st.session_state.score_history = st.session_state.score_history[-200:]
        st.session_state.angle_history = st.session_state.angle_history[-200:]

current_score = st.session_state.score_history[-1] if st.session_state.score_history else 50

# ─────────────────────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────────────────────
mode_dot = "🟢" if st.session_state.running else "⚪"
ex_cfg   = EXERCISE_CONFIG[exercise]
st.markdown(f"""
<div class="top-bar">
  <div>
    <div class="top-bar-title">RehabAI · Recovery Intelligence System</div>
    <div class="top-bar-sub">{patient_name} · {condition} · {age} yrs
      &nbsp;·&nbsp; {ex_cfg['icon']} {exercise}</div>
  </div>
  <div style="text-align:right;">
    <div class="top-bar-badge">{mode_dot} {mode} Mode</div>
    <div class="top-bar-time">{datetime.now().strftime('%H:%M:%S')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPI BAR  (4 cards)
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

def kpi_card(label, value, sub, cls):
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {cls}">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

with k1:
    st.markdown(kpi_card(
        "Posture Status",
        f'{posture["icon"]} {posture["status"]}',
        "Real-time detection",
        kpi_color_class(posture["status"]),
    ), unsafe_allow_html=True)

with k2:
    sc = score_color(current_score)
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Recovery Score</div>
      <div class="kpi-value mono" style="color:{sc};">{current_score}</div>
      <div class="kpi-sub">out of 100</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(kpi_card(
        "Risk Level", posture["risk"],
        "Injury probability",
        risk_color_class(posture["risk"]),
    ), unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Joint Angle</div>
      <div class="kpi-value mono c-blue">{angle:.1f}°</div>
      <div class="kpi-sub">{ex_cfg['joint_label']} flexion · target {ex_cfg['target_angle']}°</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT ROW
# ─────────────────────────────────────────────────────────────────────────────
main_col, right_col = st.columns([1.55, 1], gap="medium")

# ╔══════════════════════════════════════════════╗
# ║  CENTER PANEL                                ║
# ╚══════════════════════════════════════════════╝
with main_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    if mode == "Demo":
        # ── DEMO PANEL ──
        st.markdown('<div class="section-label">📡 Simulated Monitoring Panel</div>',
                    unsafe_allow_html=True)

        # Exercise badge + description
        st.markdown(f"""
        <div class="exercise-badge">
          {ex_cfg['icon']} {exercise}
          <span style="font-weight:400;color:#3b82f6;font-size:12px;">
            · {ex_cfg['joint_label']} joint
          </span>
        </div>
        <div class="exercise-desc">{ex_cfg['description']}</div>
        """, unsafe_allow_html=True)

        angle_col, skel_col = st.columns([1, 1.2])

        with angle_col:
            c_hex = STATUS_COLORS[posture["status"]]["hex"]
            c_bg  = STATUS_COLORS[posture["status"]]["bg"]
            c_txt = STATUS_COLORS[posture["status"]]["text"]
            target_pct = min(angle / ex_cfg["target_angle"], 1.0)

            st.markdown(f"""
            <div style="text-align:center; padding: 16px 0 8px 0;">
              <div style="font-size:11px;font-weight:700;letter-spacing:.1em;
                          text-transform:uppercase;color:#6b7a99;margin-bottom:10px;">
                {ex_cfg['joint_label']} Angle
              </div>
              <div class="angle-display" style="color:{c_hex};">{angle:.0f}°</div>
              <div class="angle-target-label">Target: {ex_cfg['target_angle']}°</div>

              <!-- Range bar -->
              <div style="margin:14px auto 0;max-width:160px;">
                <div style="background:#e2e8f0;border-radius:6px;height:8px;overflow:hidden;">
                  <div style="width:{int(target_pct*100)}%;background:{c_hex};height:100%;
                              border-radius:6px;transition:width .3s;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;
                            font-size:10px;color:#94a3b8;margin-top:3px;">
                  <span>0°</span><span>{ex_cfg['target_angle']}°</span>
                </div>
              </div>

              <div style="margin-top:16px;">
                <span style="background:{c_bg};color:{c_txt};border-radius:20px;
                             padding:5px 18px;font-size:14px;font-weight:700;
                             border:1px solid {c_hex}33;">
                  {posture['icon']} {posture['status']}
                </span>
              </div>
              <div style="margin-top:16px;color:#94a3b8;font-size:12px;line-height:1.5;">
                Move the sidebar slider<br>to simulate movement.
              </div>
            </div>
            """, unsafe_allow_html=True)

        with skel_col:
            st.markdown(body_svg(angle, posture, exercise), unsafe_allow_html=True)

    else:
        # ── CAMERA PANEL ──
        st.markdown('<div class="section-label">📷 Live Camera Feed · MediaPipe Pose</div>',
                    unsafe_allow_html=True)

        try:
            import cv2
            import mediapipe as mp
            CAM_LIBS = True
        except ImportError:
            CAM_LIBS = False

        if not CAM_LIBS:
            st.markdown("""
            <div style="background:#fff7ed;border:1.5px solid #fed7aa;border-radius:14px;
                        padding:28px;text-align:center;">
              <div style="font-size:36px;">⚠️</div>
              <div style="font-size:17px;font-weight:700;color:#9a3412;margin-top:10px;">
                Camera libraries not installed
              </div>
              <div style="color:#c2570a;font-size:14px;margin-top:8px;">
                Run: <code>pip install mediapipe opencv-python-headless</code><br>
                or switch to <strong>Demo Mode</strong> in the sidebar.
              </div>
            </div>""", unsafe_allow_html=True)

        elif not st.session_state.running:
            st.markdown("""
            <div class="skeleton-wrap" style="min-height:280px;">
              <div style="text-align:center;color:#94a3b8;">
                <div style="font-size:40px;">📷</div>
                <div style="font-size:14px;margin-top:10px;">
                  Press <strong>▶ Start</strong> in the sidebar to activate camera.
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        else:
            mp_pose   = mp.solutions.pose
            mp_draw   = mp.solutions.drawing_utils
            mp_styles = mp.solutions.drawing_styles

            joints_map = {
                "RIGHT_SHOULDER": mp_pose.PoseLandmark.RIGHT_SHOULDER,
                "RIGHT_ELBOW":    mp_pose.PoseLandmark.RIGHT_ELBOW,
                "RIGHT_WRIST":    mp_pose.PoseLandmark.RIGHT_WRIST,
                "RIGHT_HIP":      mp_pose.PoseLandmark.RIGHT_HIP,
                "RIGHT_KNEE":     mp_pose.PoseLandmark.RIGHT_KNEE,
                "RIGHT_ANKLE":    mp_pose.PoseLandmark.RIGHT_ANKLE,
            }

            def angle_from_landmarks(lm, h, w, j_names):
                def c(name):
                    l = lm[joints_map[name]]
                    return np.array([l.x * w, l.y * h])
                a, b, cc = c(j_names[0]), c(j_names[1]), c(j_names[2])
                ba, bc = a - b, cc - b
                cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-9)
                return math.degrees(math.acos(np.clip(cos, -1, 1)))

            frame_slot = st.empty()
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                st.markdown("""
                <div style="background:#fff1f2;border:1.5px solid #fecdd3;border-radius:14px;
                            padding:28px;text-align:center;">
                  <div style="font-size:36px;">🚫</div>
                  <div style="font-size:17px;font-weight:700;color:#9f1239;margin-top:10px;">
                    Camera not available
                  </div>
                  <div style="color:#be123c;font-size:14px;margin-top:8px;">
                    No webcam detected. Please switch to <strong>Demo Mode</strong>.
                  </div>
                </div>""", unsafe_allow_html=True)
                st.session_state.running = False
            else:
                with mp_pose.Pose(
                    model_complexity=1,
                    smooth_landmarks=True,
                    min_detection_confidence=0.55,
                    min_tracking_confidence=0.55,
                ) as pose:
                    ret, frame = cap.read()
                    if ret:
                        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = pose.process(rgb)
                        cam_angle = 0.0
                        if results.pose_landmarks:
                            h, w = frame.shape[:2]
                            j_names = ex_cfg["mediapipe_joints"]
                            cam_angle   = angle_from_landmarks(
                                results.pose_landmarks.landmark, h, w, j_names)
                            cam_posture = classify_angle(cam_angle, exercise)
                            mp_draw.draw_landmarks(
                                frame, results.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS,
                                mp_styles.get_default_pose_landmarks_style(),
                            )
                            color_bgr = {
                                "Correct":   (22, 163, 74),
                                "Almost":    (234, 88, 12),
                                "Incorrect": (220, 38, 38),
                            }.get(cam_posture["status"], (59, 130, 246))
                            cv2.rectangle(frame, (8, 8), (290, 65), (255, 255, 255), -1)
                            cv2.rectangle(frame, (8, 8), (290, 65), color_bgr, 2)
                            cv2.putText(frame, f"{exercise}: {cam_angle:.1f}°",
                                        (16, 34), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.65, (30, 30, 30), 2)
                            cv2.putText(frame, cam_posture["status"],
                                        (16, 57), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.62, color_bgr, 2)
                            # Update state
                            new_score = update_score(cam_posture["score_delta"])
                            st.session_state.score_history.append(new_score)
                            st.session_state.angle_history.append(cam_angle)
                            if len(st.session_state.score_history) > 200:
                                st.session_state.score_history = st.session_state.score_history[-200:]
                                st.session_state.angle_history = st.session_state.angle_history[-200:]
                            stage = cam_posture["status"].lower()
                            if st.session_state.last_stage != stage:
                                if stage == "correct" and st.session_state.last_stage in (
                                        "almost", "incorrect", "idle"):
                                    st.session_state.correct_reps += 1
                                elif stage == "incorrect":
                                    st.session_state.incorrect_reps += 1
                                st.session_state.last_stage = stage
                            angle   = cam_angle
                            posture = cam_posture
                            current_score = new_score

                        frame_slot.image(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                            channels="RGB", use_column_width=True,
                        )
                cap.release()

    st.markdown('</div>', unsafe_allow_html=True)  # end section-card

    # ── Angle history chart ──
    if len(st.session_state.angle_history) > 1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📐 Joint Angle History</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            build_angle_chart(st.session_state.angle_history, exercise),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown('</div>', unsafe_allow_html=True)

# ╔══════════════════════════════════════════════╗
# ║  RIGHT PANEL – AI INSIGHTS                   ║
# ╚══════════════════════════════════════════════╝
with right_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">🤖 AI Insights</div>', unsafe_allow_html=True)

    risk_hex   = {"LOW": "#15803d", "MEDIUM": "#c2570a", "HIGH": "#b91c1c"}.get(posture["risk"], "#1d4ed8")
    status_hex = STATUS_COLORS.get(posture["status"], {}).get("hex", "#1d4ed8")

    rows = [
        ("Posture Status",
         f'<span style="color:{status_hex};font-weight:800;">{posture["icon"]} {posture["status"]}</span>'),
        ("Recovery Score",
         f'<span class="mono" style="color:{score_color(current_score)};font-weight:800;">{current_score} / 100</span>'),
        ("Risk Level",
         f'<span style="color:{risk_hex};font-weight:800;">{posture["risk"]}</span>'),
        ("Joint Angle",
         f'<span class="mono" style="color:#1d4ed8;font-weight:800;">{angle:.1f}°</span>'),
        ("Exercise",
         f'<span style="color:#6b21a8;font-weight:700;">{ex_cfg["icon"]} {exercise}</span>'),
        ("Target Angle",
         f'<span class="mono" style="color:#0369a1;font-weight:700;">{ex_cfg["target_angle"]}°</span>'),
    ]
    for key, val in rows:
        st.markdown(f"""
        <div class="insight-item">
          <span class="insight-key">{key}</span>
          <span class="insight-value">{val}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                color:#6b7a99;margin-bottom:8px;">AI Recommendation</div>
    <div class="rec-box {posture['rec_cls']}">
      🧠 {posture['rec']}
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Recovery score trend ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📈 Recovery Score Trend</div>',
                unsafe_allow_html=True)
    if len(st.session_state.score_history) > 1:
        st.plotly_chart(
            build_score_chart(st.session_state.score_history),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        st.markdown("""
        <div style="height:80px;display:flex;align-items:center;justify-content:center;
                    color:#94a3b8;font-size:13px;">
          Press Start to begin recording…
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Session summary ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📋 Session Summary</div>',
                unsafe_allow_html=True)

    total_reps    = st.session_state.correct_reps + st.session_state.incorrect_reps
    progress_pct  = min(total_reps / max(target_reps, 1), 1.0)
    accuracy_pct  = int(st.session_state.correct_reps / max(total_reps, 1) * 100)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="sess-tile">
          <div class="sess-num" style="color:#15803d;">{st.session_state.correct_reps}</div>
          <div class="sess-lbl">Correct</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="sess-tile">
          <div class="sess-num" style="color:#b91c1c;">{st.session_state.incorrect_reps}</div>
          <div class="sess-lbl">Incorrect</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="sess-tile">
          <div class="sess-num" style="color:#1d4ed8;">{target_reps}</div>
          <div class="sess-lbl">Target</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.progress(progress_pct)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;
                font-size:12px;color:#94a3b8;margin-top:4px;">
      <span>0</span>
      <span style="font-weight:700;color:#1d4ed8;">{total_reps} / {target_reps} reps</span>
      <span>{target_reps}</span>
    </div>
    <div style="margin-top:12px;padding:10px 14px;background:#f8fafc;
                border-radius:10px;border:1px solid #e2e8f0;">
      <div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;
                  letter-spacing:.07em;margin-bottom:4px;">Session Accuracy</div>
      <div style="font-size:22px;font-weight:800;
                  color:{'#15803d' if accuracy_pct>=70 else '#c2570a' if accuracy_pct>=40 else '#b91c1c'};">
        {accuracy_pct}%
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-REFRESH
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.running and mode == "Demo":
    time.sleep(0.8)
    st.rerun()
elif st.session_state.running and mode == "Camera":
    time.sleep(0.05)
    st.rerun()
