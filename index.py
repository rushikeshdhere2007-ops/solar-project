import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Solar Storm AI",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# NASA / SPACE STYLE CSS
# ============================================================

st.markdown("""<style>
/* ==========================================================
   GOOGLE FONTS
   ========================================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ==========================================================
   GLOBAL
   ========================================================== */
.stApp {
    background:
        radial-gradient(
            ellipse at 10% 10%,
            rgba(255, 100, 40, 0.14),
            transparent 35%
        ),
        radial-gradient(
            ellipse at 90% 15%,
            rgba(60, 70, 255, 0.16),
            transparent 35%
        ),
        radial-gradient(
            ellipse at 50% 50%,
            rgba(100, 40, 255, 0.06),
            transparent 45%
        ),
        radial-gradient(
            ellipse at 20% 80%,
            rgba(0, 200, 255, 0.08),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #020310 0%,
            #060a1a 40%,
            #030516 70%,
            #020310 100%
        );
    color: #ffffff;
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Animated stars */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 25% 60%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1.5px 1.5px at 40% 15%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 55% 80%, rgba(255,255,255,0.25), transparent),
        radial-gradient(1px 1px at 70% 35%, rgba(255,255,255,0.35), transparent),
        radial-gradient(1.5px 1.5px at 85% 70%, rgba(255,255,255,0.45), transparent),
        radial-gradient(1px 1px at 15% 90%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 60% 45%, rgba(255,255,255,0.2), transparent),
        radial-gradient(1.5px 1.5px at 90% 10%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 35% 40%, rgba(255,255,255,0.35), transparent),
        radial-gradient(1px 1px at 80% 55%, rgba(255,255,255,0.2), transparent),
        radial-gradient(1px 1px at 5% 50%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1.5px 1.5px at 48% 95%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 72% 88%, rgba(255,255,255,0.3), transparent);
    pointer-events: none;
    z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
}

@keyframes twinkle {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.7; }
}

/* ==========================================================
   MAIN CONTAINER
   ========================================================== */
.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 4rem;
    position: relative;
    z-index: 1;
}

/* ==========================================================
   SIDEBAR
   ========================================================== */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(3, 4, 16, 0.98),
            rgba(8, 12, 35, 0.98),
            rgba(3, 4, 16, 0.98)
        );
    border-right:
        1px solid
        rgba(100, 130, 255, 0.15);
    backdrop-filter: blur(20px);
}

section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(
        180deg,
        transparent,
        rgba(255, 120, 60, 0.4),
        rgba(100, 130, 255, 0.3),
        transparent
    );
}

/* ==========================================================
   TITLE
   ========================================================== */
h1 {
    text-align: center;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 52px !important;
    font-weight: 800 !important;
    letter-spacing: 2px;
    margin-bottom: 4px;
    background:
        linear-gradient(
            90deg,
            #ffffff 0%,
            #ffb347 30%,
            #ff6847 50%,
            #ffb347 70%,
            #ffffff 100%
        );
    background-size: 200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: titleShimmer 6s ease-in-out infinite;
}

@keyframes titleShimmer {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

h2 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px;
    font-size: 22px !important;
    position: relative;
    padding-bottom: 12px;
}

h2::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #ff6847, #ffb347);
    border-radius: 3px;
}

h3 {
    font-family: 'Inter', sans-serif !important;
    color: #dbe3ff !important;
    font-weight: 600 !important;
}

/* ==========================================================
   HERO
   ========================================================== */
.hero {
    background:
        linear-gradient(
            135deg,
            rgba(20, 24, 60, 0.85),
            rgba(8, 10, 28, 0.92)
        );
    border: 1px solid rgba(255, 140, 70, 0.18);
    border-radius: 28px;
    padding: 40px 36px;
    margin: 10px 0 28px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 25px 80px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Animated aurora overlay */
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
        conic-gradient(
            from 0deg at 50% 50%,
            transparent 0deg,
            rgba(255, 100, 50, 0.04) 60deg,
            transparent 120deg,
            rgba(80, 100, 255, 0.04) 200deg,
            transparent 260deg,
            rgba(255, 80, 120, 0.03) 320deg,
            transparent 360deg
        );
    animation: auroraRotate 20s linear infinite;
    pointer-events: none;
}

@keyframes auroraRotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 10px;
    letter-spacing: 1px;
    position: relative;
    z-index: 1;
}

.hero-text {
    font-size: 16px;
    color: #b8c4e8;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

/* ==========================================================
   STATUS BAR
   ========================================================== */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 14px 24px;
    border-radius: 16px;
    background:
        linear-gradient(
            135deg,
            rgba(10, 15, 40, 0.92),
            rgba(5, 8, 25, 0.95)
        );
    border: 1px solid rgba(80, 110, 255, 0.2);
    color: #c0ccff;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

/* Animated scan line */
.status-bar::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(100, 140, 255, 0.06),
        transparent
    );
    animation: scanLine 4s ease-in-out infinite;
}

@keyframes scanLine {
    0% { left: -60%; }
    100% { left: 160%; }
}

.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #43ff87;
    box-shadow:
        0 0 10px #43ff87,
        0 0 25px rgba(67, 255, 135, 0.4);
    animation: statusPulse 2s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes statusPulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px #43ff87, 0 0 25px rgba(67, 255, 135, 0.4); }
    50% { opacity: 0.65; box-shadow: 0 0 5px #43ff87, 0 0 12px rgba(67, 255, 135, 0.2); }
}

/* ==========================================================
   CARDS — GLASSMORPHISM
   ========================================================== */
.dashboard-card {
    background:
        linear-gradient(
            160deg,
            rgba(15, 20, 50, 0.88),
            rgba(6, 9, 24, 0.94)
        );
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(90, 115, 255, 0.18);
    border-radius: 24px;
    padding: 28px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.04);
    transition: border-color 0.4s ease, box-shadow 0.4s ease;
}

.dashboard-card:hover {
    border-color: rgba(255, 130, 60, 0.3);
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.35),
        0 0 40px rgba(255, 100, 50, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* Animated top accent line */
.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 120, 50, 0.6) 20%,
        rgba(100, 130, 255, 0.5) 50%,
        rgba(200, 80, 255, 0.4) 80%,
        transparent 100%
    );
    background-size: 200% 100%;
    animation: borderFlow 4s linear infinite;
}

@keyframes borderFlow {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ==========================================================
   METRICS — GLOWING CARDS
   ========================================================== */
[data-testid="stMetric"] {
    background:
        linear-gradient(
            155deg,
            rgba(20, 28, 65, 0.95),
            rgba(8, 12, 32, 0.98)
        );
    border: 1px solid rgba(90, 120, 255, 0.2);
    border-radius: 20px;
    padding: 20px;
    min-height: 110px;
    position: relative;
    overflow: hidden;
    transition: all 0.35s ease;
    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.25);
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 130, 60, 0.3);
    box-shadow:
        0 16px 50px rgba(0, 0, 0, 0.3),
        0 0 30px rgba(255, 100, 50, 0.06);
}

/* Colored accent bar on metric cards */
[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 15%;
    right: 15%;
    height: 2px;
    background: linear-gradient(90deg, #ff6847, #ffb347, #ff6847);
    border-radius: 2px;
    opacity: 0.5;
}

[data-testid="stMetricLabel"] {
    color: #8e9cc8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

/* ==========================================================
   BUTTON — ANIMATED GRADIENT
   ========================================================== */
.stButton > button {
    width: 100%;
    min-height: 56px;
    border: none;
    border-radius: 16px;
    background:
        linear-gradient(
            135deg,
            #ff5a36,
            #ff8b35,
            #ff4e67,
            #ff5a36
        );
    background-size: 300% 100%;
    color: white;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    box-shadow:
        0 10px 35px rgba(255, 90, 50, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
    transition: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    animation: btnGradient 3s ease infinite;
    position: relative;
    overflow: hidden;
}

@keyframes btnGradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle,
        rgba(255, 255, 255, 0.1) 0%,
        transparent 60%
    );
    opacity: 0;
    transition: opacity 0.4s ease;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow:
        0 18px 50px rgba(255, 90, 50, 0.45),
        0 0 30px rgba(255, 90, 50, 0.15);
}

.stButton > button:hover::after {
    opacity: 1;
}

/* ==========================================================
   FILE UPLOADER — NASA MISSION CONTROL DROPZONE
   ========================================================== */
[data-testid="stFileUploader"] {
    background: transparent !important;
    padding: 0 !important;
}

[data-testid="stFileUploaderDropzone"] {
    background:
        linear-gradient(
            145deg,
            rgba(12, 18, 48, 0.95),
            rgba(5, 8, 25, 0.98)
        ) !important;
    border: 2px dashed rgba(255, 130, 70, 0.4) !important;
    border-radius: 20px !important;
    padding: 32px 24px !important;
    box-shadow:
        0 15px 45px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

[data-testid="stFileUploaderDropzone"]::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%, rgba(255, 100, 50, 0.08), transparent 70%);
    pointer-events: none;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #ff8b35 !important;
    box-shadow:
        0 0 35px rgba(255, 120, 50, 0.25),
        0 20px 50px rgba(0, 0, 0, 0.5) !important;
    transform: translateY(-2px);
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #b8c4e8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(135deg, #ff5a36, #ff8b35) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 10px 22px !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 6px 20px rgba(255, 90, 50, 0.3) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 10px 28px rgba(255, 90, 50, 0.5) !important;
}

/* ==========================================================
   INPUTS
   ========================================================== */
.stNumberInput input {
    background:
        rgba(4, 8, 24, 0.95) !important;
    color:
        #ffffff !important;
    border:
        1px solid
        rgba(90, 120, 255, 0.3) !important;
    border-radius:
        12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stNumberInput input:focus {
    border-color:
        rgba(255, 120, 60, 0.6) !important;
    box-shadow:
        0 0 20px rgba(255, 100, 60, 0.15),
        0 0 40px rgba(255, 100, 60, 0.05) !important;
}

/* ==========================================================
   PROGRESS BAR
   ========================================================== */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ff5a36, #ffb347, #ff4e67) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 15px rgba(255, 90, 50, 0.3);
}

.stProgress > div > div {
    background: rgba(15, 20, 45, 0.8) !important;
    border-radius: 8px !important;
}

/* ==========================================================
   ALERTS — SCI-FI TELEMETRY BANNERS
   ========================================================== */
[data-testid="stAlert"] {
    background:
        linear-gradient(
            135deg,
            rgba(14, 22, 54, 0.95),
            rgba(7, 10, 28, 0.98)
        ) !important;
    border: 1px solid rgba(100, 140, 255, 0.25) !important;
    border-left: 5px solid #ff6847 !important;
    border-radius: 18px !important;
    padding: 18px 24px !important;
    color: #e2e9ff !important;
    backdrop-filter: blur(16px) !important;
    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAlert"] p {
    color: #d2dcff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* ==========================================================
   DATAFRAME
   ========================================================== */
[data-testid="stDataFrame"] {
    border:
        1px solid
        rgba(90, 115, 255, 0.18);
    border-radius:
        18px;
    overflow: hidden;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
}

/* ==========================================================
   TEXT
   ========================================================== */
p {
    color: #bfc9e6;
    font-family: 'Inter', sans-serif;
}

label {
    color: #cdd6f4 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
}

/* ==========================================================
   DIVIDER
   ========================================================== */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(100, 130, 255, 0.25),
        rgba(255, 120, 60, 0.2),
        transparent
    ) !important;
    margin: 20px 0 !important;
}

/* ==========================================================
   FOOTER
   ========================================================== */
.footer {
    text-align: center;
    color: #5c6890;
    font-size: 13px;
    padding: 30px;
    margin-top: 40px;
    border-top: 1px solid rgba(80, 100, 160, 0.12);
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.5px;
}

/* ==========================================================
   SCROLLBAR
   ========================================================== */
::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #020310;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff6847, #ff9547, #ff5a36);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #ff8060, #ffb060, #ff7050);
}

/* ==========================================================
   SELECTION
   ========================================================== */
::selection {
    background: rgba(255, 100, 50, 0.25);
    color: #ffffff;
}

/* ==========================================================
   TABS
   ========================================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}

/* ==========================================================
   SPINNER
   ========================================================== */
.stSpinner > div {
    border-top-color: #ff6847 !important;
}

/* ==========================================================
   MOBILE
   ========================================================== */
@media (max-width: 768px) {
    h1 {
        font-size: 32px !important;
        letter-spacing: 1px;
    }
    h2 {
        font-size: 18px !important;
    }
    .hero {
        padding: 24px 18px;
        border-radius: 20px;
    }
    .hero-title {
        font-size: 22px;
    }
    .dashboard-card {
        padding: 18px;
        border-radius: 18px;
    }
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
    }
    [data-testid="stMetric"] {
        padding: 14px;
        border-radius: 14px;
    }
}
</style>
    """, unsafe_allow_html=True)


# ============================================================
# LIVE CLOCK
# ============================================================

components.html("""
<div style="
    text-align: right;
    padding: 4px 12px;
    font-family: 'Inter', Arial, sans-serif;">
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(15, 20, 45, 0.8), rgba(8, 12, 30, 0.9));
        border: 1px solid rgba(100, 130, 255, 0.15);
        border-radius: 50px;
        padding: 6px 16px;
        color: #8e9cc8;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 0.8px;">
        <span style="
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #43ff87;
            box-shadow: 0 0 8px #43ff87;
            display: inline-block;"></span>
        <span id="clock">SYNCING...</span>
    </span>
</div>
<script>
function updateClock() {
    const now = new Date();
    const opts = {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false};
    const date = now.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'}).toUpperCase();
    document.getElementById("clock").innerHTML =
        "MISSION TIME • " + date + " • " + now.toLocaleTimeString('en-US',opts);
}
updateClock();
setInterval(updateClock, 1000);
</script>
    """, height=35)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """<div class="hero">
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            border-radius: 50%;
            border: 1px solid rgba(255, 140, 70, 0.06);
            pointer-events: none;
        "></div>
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 320px;
            height: 320px;
            border-radius: 50%;
            border: 1px solid rgba(100, 130, 255, 0.04);
            pointer-events: none;
        "></div>
        <div class="hero-title">
            ☀️ SOLAR STORM AI
        </div>
        <div style="
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 3px;
            color: #ff9547;
            margin-bottom: 12px;
            text-transform: uppercase;
            position: relative;
            z-index: 1;
        ">NEXT-GENERATION SPACE WEATHER INTELLIGENCE</div>
        <div class="hero-text">
            Artificial Intelligence System for
            24-Hour Geomagnetic Storm Prediction
            using Solar-Wind and Kp Measurements.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """<div class="status-bar">
        <span class="status-dot"></span>
        AI SYSTEM ONLINE
        &nbsp; • &nbsp;
        RANDOM FOREST
        &nbsp; • &nbsp;
        24-HOUR FORECAST
        &nbsp; • &nbsp;
        LIVE TELEMETRY
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """<div style="
            text-align: center;
            padding: 20px 0 15px;
        ">
            <div style="
                font-family: 'Space Grotesk', sans-serif;
                font-size: 28px;
                font-weight: 800;
                background: linear-gradient(90deg, #ffb347, #ff6847);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 4px;
            ">☀️ Solar Storm AI</div>
            <div style="
                font-size: 11px;
                color: #6f7ba5;
                letter-spacing: 2px;
                text-transform: uppercase;
            ">SPACE WEATHER INTELLIGENCE</div>
        </div>
        <hr style="
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,120,60,0.3), transparent);
            margin: 10px 0 20px;
        ">
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📋 Navigation")
    st.markdown(
        """<div style="
            font-size: 13px;
            color: #8e9cc8;
            line-height: 2.2;
        ">
        📡 Data Ingestion<br>
        ⏱️ Temporal Analysis<br>
        🎯 24-Hour Forecast Target<br>
        🌩️ Storm Status<br>
        🤖 AI Engine<br>
        🛰️ Live Telemetry<br>
        🔮 Storm Predictor<br>
        📈 Kp Activity Chart<br>
        🎯 Risk Index Gauge<br>
        🧠 Feature Importance
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### ⚙️ System Info")
    st.markdown(
        """<div style="
            font-size: 12px;
            color: #6f7ba5;
            line-height: 1.8;
        ">
        <b style="color:#b8c4e8">Model:</b> Random Forest<br>
        <b style="color:#b8c4e8">Trees:</b> 150 estimators<br>
        <b style="color:#b8c4e8">Forecast:</b> 24-hour ahead<br>
        <b style="color:#b8c4e8">Threshold:</b> Kp ≥ 5<br>
        <b style="color:#b8c4e8">Dataset:</b> OMNI Solar-Wind
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        """<div style="
            text-align: center;
            padding: 10px 0;
        ">
            <div style="
                font-size: 11px;
                color: #5c6890;
                letter-spacing: 1px;
            ">BUILT BY RUSHI DHERE</div>
            <div style="
                margin-top: 8px;
                display: flex;
                justify-content: center;
                gap: 15px;
            ">
                <a href="https://github.com/rushikeshdhere2007-ops" target="_blank" style="
                    color: #6f7ba5;
                    text-decoration: none;
                    font-size: 18px;
                ">⭐</a>
                <a href="https://www.linkedin.com/in/rushikesh-dhere-3637b6391" target="_blank" style="
                    color: #6f7ba5;
                    text-decoration: none;
                    font-size: 18px;
                ">💼</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DEMO DATASET GENERATOR
# ============================================================

@st.cache_data
def get_demo_omni_dataset():
    np.random.seed(42)
    n_samples = 720  # 30 days of hourly solar wind telemetry
    years = [2024] * n_samples
    doys = np.repeat(np.arange(1, 31), 24)
    hours = np.tile(np.arange(0, 24), 30)
    
    scalar_b = 5.2 + 3.8 * np.sin(np.linspace(0, 5*np.pi, n_samples)) + np.random.normal(0, 1.2, n_samples)
    bz = -2.8 + 6.4 * np.cos(np.linspace(0, 7*np.pi, n_samples)) + np.random.normal(0, 2.0, n_samples)
    proton_density = 5.8 + 4.2 * np.abs(np.sin(np.linspace(0, 4*np.pi, n_samples))) + np.random.normal(0, 0.8, n_samples)
    solar_wind_speed = 380 + 180 * (np.sin(np.linspace(0, 6*np.pi, n_samples))**2) + np.random.normal(0, 15, n_samples)
    plasma_beta = 1.1 + 0.6 * np.random.exponential(1, n_samples)
    
    raw_kp = 1.4 + (-0.38 * bz) + (0.0055 * (solar_wind_speed - 350)) + (0.12 * scalar_b) + np.random.normal(0, 0.35, n_samples)
    kp = np.clip(raw_kp, 0.3, 8.8)
    
    return pd.DataFrame({
        "YEAR": years,
        "DOY": doys,
        "Hour": hours,
        "Scalar_B": np.round(scalar_b, 2),
        "Bz": np.round(bz, 2),
        "Proton_Density": np.round(proton_density, 2),
        "Solar_Wind_Speed": np.round(solar_wind_speed, 1),
        "Plasma_Beta": np.round(plasma_beta, 2),
        "Kp": np.round(kp, 1)
    })


# ============================================================
# DATASET INGESTION
# ============================================================

st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.subheader("📡 DATA INGESTION & TELEMETRY STREAM")
with col_h2:
    st.markdown("""
    <div style="text-align: right; padding-top: 5px;">
        <span style="background: rgba(0, 230, 150, 0.15); border: 1px solid rgba(0, 230, 150, 0.4); color: #00e696; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 1px;">
            ● OMNI-2 ONLINE
        </span>
    </div>
    """, unsafe_allow_html=True)

ingestion_mode = st.radio(
    "Select Telemetry Source:",
    ["🚀 Live Demo OMNI Stream (Fast Activation)", "📁 Custom OMNI File Upload (.lst, .txt, .csv)"],
    horizontal=True
)

df = None

if "Custom" in ingestion_mode:
    uploaded_file = st.file_uploader(
        "Upload OMNI Solar-Wind Dataset File",
        type=["lst", "txt", "csv"]
    )
    if uploaded_file is not None:
        try:
            df = pd.read_csv(
                uploaded_file,
                sep=r"\s+",
                header=None,
                names=[
                    "YEAR", "DOY", "Hour", "Scalar_B", "Bz",
                    "Proton_Density", "Solar_Wind_Speed", "Plasma_Beta", "Kp"
                ],
                engine="python"
            )
            st.success(f"🟢 CUSTOM DATASET ONLINE • {len(df):,} records loaded successfully from file")
        except Exception as error:
            st.error(f"Dataset parsing error: {error}")
            st.stop()
    else:
        st.info("💡 Upload your OMNI dataset file above, or switch to 'Live Demo OMNI Stream' to launch immediately!")
        if st.button("⚡ Quick-Activate Live Demo Telemetry"):
            df = get_demo_omni_dataset()
            st.success(f"🟢 DEMO TELEMETRY STREAM ACTIVATED • {len(df):,} synthetic OMNI-2 records loaded")
        else:
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()
else:
    df = get_demo_omni_dataset()
    st.success("🟢 LIVE DEMO TELEMETRY ONLINE • 720 Hours (30 Days) of OMNI Solar-Wind Data Stream Activated")

st.markdown('</div>', unsafe_allow_html=True)


st.markdown(
    """<div style="
        text-align: center;
        padding: 8px;
        margin: 10px 0;
        color: #3d4870;
        font-size: 11px;
        letter-spacing: 4px;
    ">━━━ ◆ ━━━</div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CLEAN DATA
# ============================================================

numeric_columns = [
    "YEAR",
    "DOY",
    "Hour",
    "Scalar_B",
    "Bz",
    "Proton_Density",
    "Solar_Wind_Speed",
    "Plasma_Beta",
    "Kp"
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


missing_values = {
    "Scalar_B": [999.9, 9999, 99999],
    "Bz": [999.9, 9999, 99999],
    "Proton_Density": [999.9, 9999, 99999],
    "Solar_Wind_Speed": [9999.0, 999.9, 99999],
    "Plasma_Beta": [999.99, 9999, 99999],
    "Kp": [99, 999, 9999]
}


for column, values in missing_values.items():

    df[column] = df[column].replace(
        values,
        np.nan
    )


df = df.dropna(
    subset=[
        "YEAR",
        "DOY",
        "Hour",
        "Kp"
    ]
).copy()


# ============================================================
# KP NORMALIZATION
# ============================================================

if df["Kp"].max() > 9:

    df["Kp"] = df["Kp"] / 10


df["Kp"] = df["Kp"].clip(
    0,
    9
)


# ============================================================
# TIMESTAMP
# ============================================================

date_part = (
    df["YEAR"].astype(int).astype(str)
    +
    df["DOY"].astype(int)
    .astype(str)
    .str.zfill(3)
)


df["Timestamp"] = pd.to_datetime(
    date_part,
    format="%Y%j",
    errors="coerce"
)


df["Timestamp"] += pd.to_timedelta(
    df["Hour"],
    
    unit="h"
)


df = (
    df.dropna(subset=["Timestamp"])
    .sort_values("Timestamp")
    .reset_index(drop=True)
)


if len(df) < 100:

    st.error(
        "Not enough valid records for AI training."
    )

    st.stop()


# ============================================================
# TIME STEP
# ============================================================

st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.subheader("⏱️ TEMPORAL DATA ANALYSIS")


time_diff = df["Timestamp"].diff().dropna()


time_diff_hours = (
    time_diff.dt.total_seconds()
    / 3600
)


median_step = time_diff_hours.median()


mode_values = (
    time_diff_hours
    .round(2)
    .mode()
)


if len(mode_values) > 0:

    common_step = float(
        mode_values.iloc[0]
    )

else:

    common_step = median_step


gaps = int(
    (time_diff_hours > 1).sum()
)


c1, c2, c3 = st.columns(3)


c1.metric(
    "MEDIAN STEP",
    f"{median_step:.2f} h"
)


c2.metric(
    "COMMON STEP",
    f"{common_step:.2f} h"
)


c3.metric(
    "DATA GAPS",
    f"{gaps:,}"
)
st.markdown('</div>', unsafe_allow_html=True)


st.markdown(
    """<div style="
        text-align: center;
        padding: 8px;
        margin: 10px 0;
        color: #3d4870;
        font-size: 11px;
        letter-spacing: 4px;
    ">━━━ ◆ ━━━</div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 24 HOUR TARGET
# ============================================================

st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.subheader(
    "🎯 24-HOUR FORECAST TARGET"
)


df["Future_Kp"] = (
    df["Kp"].shift(-24)
)


df = df.dropna(
    subset=["Future_Kp"]
).copy()


df["Storm"] = (
    df["Future_Kp"] >= 5
).astype(int)

st.markdown(
    f"""<div style="
        display: flex;
        justify-content: center;
        gap: 30px;
        padding: 16px;
        margin: 10px 0;
    ">
        <div style="
            text-align: center;
            padding: 12px 24px;
            background: rgba(67, 255, 135, 0.06);
            border: 1px solid rgba(67, 255, 135, 0.15);
            border-radius: 14px;
        ">
            <div style="font-size: 11px; color: #6f7ba5; letter-spacing: 1px; text-transform: uppercase;">Quiet Hours</div>
            <div style="font-size: 24px; font-weight: 800; color: #43ff87; font-family: 'Space Grotesk', sans-serif;">{int((df['Future_Kp'] < 5).sum()):,}</div>
        </div>
        <div style="
            text-align: center;
            padding: 12px 24px;
            background: rgba(255, 90, 50, 0.06);
            border: 1px solid rgba(255, 90, 50, 0.15);
            border-radius: 14px;
        ">
            <div style="font-size: 11px; color: #6f7ba5; letter-spacing: 1px; text-transform: uppercase;">Storm Hours</div>
            <div style="font-size: 24px; font-weight: 800; color: #ff5a36; font-family: 'Space Grotesk', sans-serif;">{int((df['Future_Kp'] >= 5).sum()):,}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)


st.markdown(
    """<div style="
        text-align: center;
        padding: 8px;
        margin: 10px 0;
        color: #3d4870;
        font-size: 11px;
        letter-spacing: 4px;
    ">━━━ ◆ ━━━</div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STORM STATISTICS
# ============================================================

st.subheader(
    "🌩️ GEOMAGNETIC STORM STATUS"
)


no_storm = int(
    (df["Storm"] == 0).sum()
)


storm = int(
    (df["Storm"] == 1).sum()
)


storm_percentage = (
    (storm / len(df) * 100)
    if len(df) > 0
    else 0.0
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "TOTAL RECORDS",
    f"{len(df):,}"
)


c2.metric(
    "QUIET / NO STORM",
    f"{no_storm:,}"
)


c3.metric(
    "STORM RECORDS",
    f"{storm:,}"
)


c4.metric(
    "STORM RATE",
    f"{storm_percentage:.2f}%"
)


# ============================================================
# FEATURES
# ============================================================

features = [
    "Scalar_B",
    "Bz",
    "Proton_Density",
    "Solar_Wind_Speed",
    "Plasma_Beta",
    "Kp"
]


X = df[features].copy()


y = df["Storm"].copy()


X = X.replace(
    [np.inf, -np.inf],
    np.nan
)


# ============================================================
# TRAIN TEST
# ============================================================

split_index = int(
    len(X) * 0.80
)


gap_rows = 24


X_train = X.iloc[
    :split_index
].copy()


y_train = y.iloc[
    :split_index
].copy()


X_test = X.iloc[
    split_index + gap_rows:
].copy()


y_test = y.iloc[
    split_index + gap_rows:
].copy()


if len(X_test) == 0:

    st.error(
        "Testing dataset is empty."
    )

    st.stop()


if y_train.nunique() < 2:

    st.error(
        "Training data contains only one class "
        "(all storm or all quiet). Please upload "
        "a larger or more varied dataset."
    )

    st.stop()


# ============================================================
# MEDIAN IMPUTATION
# ============================================================

train_medians = X_train.median()


X_train = X_train.fillna(
    train_medians
)


X_test = X_test.fillna(
    train_medians
)


# ============================================================
# AI MODEL
# ============================================================

st.subheader(
    "🤖 ARTIFICIAL INTELLIGENCE ENGINE"
)


with st.spinner(
    "Training Random Forest AI model..."
):

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )


    model.fit(
        X_train,
        y_train
    )


# ============================================================
# EVALUATION
# ============================================================

y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred
)


precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)


recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)


f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "ACCURACY",
    f"{accuracy * 100:.2f}%"
)


c2.metric(
    "PRECISION",
    f"{precision:.2f}"
)


c3.metric(
    "RECALL",
    f"{recall:.2f}"
)


c4.metric(
    "F1 SCORE",
    f"{f1:.2f}"
)


# ============================================================
# NOAA
# ============================================================

st.subheader(
    "🛰️ NOAA LIVE SOLAR-WIND TELEMETRY"
)


@st.cache_data(ttl=60)
def get_live_solar_wind():

    url = (
        "https://services.swpc.noaa.gov/"
        "json/rtsw/rtsw_wind_1m.json"
    )


    response = requests.get(
        url,
        timeout=15
    )


    response.raise_for_status()


    return pd.DataFrame(
        response.json()
    )


live_df = pd.DataFrame()


try:

    live_df = get_live_solar_wind()


    if not live_df.empty:

        latest = live_df.iloc[-1]


        lc1, lc2, lc3 = st.columns(3)


        if "proton_speed" in live_df.columns:

            speed_value = pd.to_numeric(
                latest["proton_speed"],
                errors="coerce"
            )


            lc1.metric(
                "SOLAR WIND",
                f"{speed_value:.1f} km/s"
                if pd.notna(speed_value)
                else "N/A"
            )


        else:

            lc1.metric(
                "SOLAR WIND",
                "N/A"
            )


        if "proton_density" in live_df.columns:

            density_value = pd.to_numeric(
                latest["proton_density"],
                errors="coerce"
            )


            lc2.metric(
                "PROTON DENSITY",
                f"{density_value:.2f} n/cc"
                if pd.notna(density_value)
                else "N/A"
            )


        else:

            lc2.metric(
                "PROTON DENSITY",
                "N/A"
            )


        if "proton_temperature" in live_df.columns:

            temp_value = pd.to_numeric(
                latest["proton_temperature"],
                errors="coerce"
            )


            lc3.metric(
                "TEMPERATURE",
                f"{temp_value:.0f} K"
                if pd.notna(temp_value)
                else "N/A"
            )


        else:

            lc3.metric(
                "TEMPERATURE",
                "N/A"
            )


        st.success(
            "🟢 NOAA LIVE FEED CONNECTED"
        )


except Exception as error:

    st.warning(
        f"NOAA feed unavailable: {error}"
    )


# ============================================================
# PREDICTION
# ============================================================

left, right = st.columns(
    [1, 1.8]
)


# ============================================================
# PREDICTION PANEL
# ============================================================

with left:

    st.markdown(
        '<div class="dashboard-card">',
        unsafe_allow_html=True
    )


    st.subheader(
        "🔮 AI STORM PREDICTOR"
    )


    bz = st.number_input(
        "Bz (nT)",
        value=-2.0,
        step=0.1
    )


    speed = st.number_input(
        "Solar Wind Speed (km/s)",
        value=450.0,
        step=1.0
    )


    density = st.number_input(
        "Proton Density (n/cc)",
        value=5.0,
        step=0.1
    )


    beta = st.number_input(
        "Plasma Beta",
        value=1.0,
        step=0.1
    )


    current_kp = st.number_input(
        "Current Kp",
        value=3.0,
        min_value=0.0,
        max_value=9.0,
        step=0.1
    )


    if st.button(
        "⚡ RUN AI PREDICTION"
    ):


        scalar_b = float(
            train_medians.get(
                "Scalar_B",
                0
            )
        )


        input_data = pd.DataFrame({

            "Scalar_B": [
                scalar_b
            ],

            "Bz": [
                bz
            ],

            "Proton_Density": [
                density
            ],

            "Solar_Wind_Speed": [
                speed
            ],

            "Plasma_Beta": [
                beta
            ],

            "Kp": [
                current_kp
            ]

        })[features]


        probability = float(
            model.predict_proba(
                input_data
            )[0][1]
        )


        percentage = (
            probability * 100
        )


        prediction = int(
            model.predict(
                input_data
            )[0]
        )


        st.markdown("---")


        if percentage >= 70:

            st.error(
                f"🔴 HIGH RISK\n\n"
                f"{percentage:.2f}%"
            )


        elif percentage >= 40:

            st.warning(
                f"🟡 MODERATE RISK\n\n"
                f"{percentage:.2f}%"
            )


        else:

            st.success(
                f"🟢 LOW RISK\n\n"
                f"{percentage:.2f}%"
            )


        st.progress(
            probability
        )


        if prediction == 1:

            st.write(
                "🌩️ **AI Classification:** "
                "Geomagnetic Storm"
            )

        else:

            st.write(
                "🌤️ **AI Classification:** "
                "No Geomagnetic Storm"
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# KP GRAPH
# ============================================================

with right:

    st.markdown(
        '<div class="dashboard-card">',
        unsafe_allow_html=True
    )


    st.subheader(
        "📈 GEOMAGNETIC Kp ACTIVITY"
    )


    graph_data = df.tail(500)


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=graph_data["Timestamp"],
            y=graph_data["Kp"],
            mode="lines",
            name="Actual Kp",
            line=dict(
                width=2.5,
                color="#00d4ff"
            ),
            fill="tozeroy",
            fillcolor="rgba(0, 212, 255, 0.05)"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=graph_data["Timestamp"],
            y=graph_data["Future_Kp"],
            mode="lines",
            name="Future Kp (24h)",
            line=dict(
                dash="dash",
                width=2,
                color="#ff9547"
            )
        )
    )


    fig.add_hline(
        y=5,
        line_dash="dot",
        line_color="#ff4e67",
        line_width=1.5,
        annotation_text="⚠ G1 STORM THRESHOLD",
        annotation_font=dict(
            color="#ff4e67",
            size=11
        )
    )


    fig.update_layout(

        height=500,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#8e9cc8",
            family="Inter, sans-serif"
        ),

        xaxis=dict(
            title="TIME",
            gridcolor="rgba(100, 130, 255, 0.06)",
            showline=True,
            linecolor="rgba(100, 130, 255, 0.15)",
            zeroline=False,
            title_font=dict(size=11, color="#6f7ba5")
        ),

        yaxis=dict(
            title="Kp INDEX",
            gridcolor="rgba(100, 130, 255, 0.06)",
            showline=True,
            linecolor="rgba(100, 130, 255, 0.15)",
            zeroline=False,
            title_font=dict(size=11, color="#6f7ba5")
        ),

        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="rgba(10, 15, 35, 0.95)",
            bordercolor="rgba(100, 130, 255, 0.2)",
            font_color="#ffffff"
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(100, 130, 255, 0.1)",
            borderwidth=1,
            font=dict(size=12, color="#b8c4e8")
        ),

        margin=dict(l=10, r=10, t=20, b=10)
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# GAUGE + FEATURE IMPORTANCE
# ============================================================

left2, right2 = st.columns(2)


# ============================================================
# GAUGE
# ============================================================

with left2:

    st.markdown(
        '<div class="dashboard-card">',
        unsafe_allow_html=True
    )


    st.subheader(
        "🎯 STORM RISK INDEX"
    )


    avg_probability = (
        model.predict_proba(
            X_test
        )[:, 1].mean()
        * 100
    )


    gauge = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=avg_probability,

            title={
                "text":
                "AI STORM PROBABILITY"
            },

            gauge={

                "axis": {
                    "range": [0, 100]
                },

                "bar": {
                    "color": "#ff5c3d"
                },

                "steps": [

                    {
                        "range": [0, 30],
                        "color": "#143d2a"
                    },

                    {
                        "range": [30, 60],
                        "color": "#4b3d16"
                    },

                    {
                        "range": [60, 100],
                        "color": "#4d1d22"
                    }

                ]

            }

        )

    )


    gauge.update_layout(

        height=350,

        paper_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#b8c4e8",
            family="Inter, sans-serif"
        ),

        margin=dict(l=20, r=20, t=30, b=10)

    )


    st.plotly_chart(
        gauge,
        use_container_width=True
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

with right2:

    st.markdown(
        '<div class="dashboard-card">',
        unsafe_allow_html=True
    )


    st.subheader(
        "🧠 AI FEATURE IMPORTANCE"
    )


    importance = pd.DataFrame({

        "Feature": features,

        "Importance":
            model.feature_importances_

    }).sort_values(
        "Importance",
        ascending=True
    )


    fig2 = go.Figure(

        go.Bar(

            x=importance["Importance"],

            y=importance["Feature"],

            orientation="h",

            text=[
                f"{x:.3f}"
                for x
                in importance["Importance"]
            ],

            textposition="outside",

            textfont=dict(
                color="#b8c4e8",
                size=11
            ),

            marker=dict(
                color=importance["Importance"],
                colorscale=[
                    [0, "#1a1040"],
                    [0.5, "#ff6847"],
                    [1, "#ffb347"]
                ],
                line=dict(
                    color="rgba(255, 150, 80, 0.3)",
                    width=1
                ),
                cornerradius=6
            )

        )

    )


    fig2.update_layout(

        height=350,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#8e9cc8",
            family="Inter, sans-serif"
        ),

        xaxis=dict(
            title="IMPORTANCE",
            gridcolor="rgba(100, 130, 255, 0.06)",
            showline=True,
            linecolor="rgba(100, 130, 255, 0.15)",
            zeroline=False,
            title_font=dict(size=11, color="#6f7ba5")
        ),

        yaxis=dict(
            gridcolor="rgba(100, 130, 255, 0.06)",
            showline=False,
            tickfont=dict(size=12, color="#b8c4e8")
        ),

        margin=dict(l=10, r=30, t=20, b=10)

    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# RECENT DATA
# ============================================================

st.markdown(
    '<div class="dashboard-card">',
    unsafe_allow_html=True
)


st.subheader(
    "📋 RECENT SOLAR-WIND OBSERVATIONS"
)


recent = df.tail(10).copy()


recent["Storm Class"] = np.where(

    recent["Kp"] >= 5,

    "🔴 G2+ STORM",

    np.where(

        recent["Kp"] >= 4,

        "🟡 ACTIVE",

        "🟢 QUIET"

    )

)


st.dataframe(

    recent[
        [
            "YEAR",
            "DOY",
            "Hour",
            "Bz",
            "Proton_Density",
            "Solar_Wind_Speed",
            "Plasma_Beta",
            "Kp",
            "Storm Class"
        ]
    ]

)


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """<div class="footer">
        ☀️ SOLAR STORM AI
        <br><br>
        Machine Learning • Random Forest •
        OMNI Solar-Wind Dataset •
        24-Hour Geomagnetic Storm Prediction
        <br><br>
        Kp ≥ 5 → Geomagnetic Storm
    </div>
    """,
    unsafe_allow_html=True
)