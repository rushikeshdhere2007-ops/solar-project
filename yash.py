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
# LOGIN SYSTEM
# ============================================================

USERNAME = "sai"
PASSWORD = "solar123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:

    st.markdown("""
    <div style="
        max-width:500px;
        margin:100px auto 20px auto;
        padding:40px;
        text-align:center;
        background:linear-gradient(145deg,#111737,#050818);
        border:1px solid rgba(255,120,70,0.3);
        border-radius:25px;
        box-shadow:0 20px 70px rgba(0,0,0,.5);
    ">
        <div style="font-size:50px;">☀️</div>
        <h1 style="font-size:32px !important;">
            SOLAR STORM AI
        </h1>
        <p>
            Secure AI Prediction System
        </p>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input(
        "👤 Username"
    )

    password = st.text_input(
        "🔑 Password",
        type="password"
    )

    if st.button("🚀 LOGIN"):

        if username == USERNAME and password == PASSWORD:

            st.session_state.logged_in = True
            st.rerun()

        else:

            st.error("❌ Invalid username or password.")

    st.stop()


# ============================================================
# NASA / SPACE STYLE CSS
# ============================================================

st.markdown("""<style>
/* ==========================================================
   GLOBAL
   ========================================================== */
.stApp {
    background:
        radial-gradient(
            circle at 15% 15%,
            rgba(255, 110, 40, 0.16),
            transparent 22%
        ),
        radial-gradient(
            circle at 85% 20%,
            rgba(70, 80, 255, 0.18),
            transparent 25%
        ),
        radial-gradient(
            circle at 50% 80%,
            rgba(150, 40, 255, 0.10),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #02030b 0%,
            #060a19 45%,
            #02030b 100%
        );
    color: #ffffff;
}
/* ==========================================================
   MAIN CONTAINER
   ========================================================== */
.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}
/* ==========================================================
   SIDEBAR
   ========================================================== */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #03040d,
            #080c20,
            #03040d
        );
    border-right:
        1px solid
        rgba(120, 140, 255, 0.20);
}
/* ==========================================================
   TITLE
   ========================================================== */
h1 {
    text-align: center;
    font-size: 56px !important;
    font-weight: 900 !important;
    letter-spacing: 3px;
    margin-bottom: 4px;
    background:
        linear-gradient(
            90deg,
            #ffffff,
            #ffb347,
            #ff6847,
            #ffffff
        );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow:
        0 0 30px
        rgba(255, 100, 50, 0.25);
}
h2 {
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px;
}
h3 {
    color: #dbe3ff !important;
    font-weight: 700 !important;
}
/* ==========================================================
   HERO
   ========================================================== */
.hero {
    background:
        linear-gradient(
            135deg,
            rgba(25, 28, 70, 0.90),
            rgba(8, 10, 28, 0.96)
        );
    border:
        1px solid
        rgba(255, 150, 80, 0.22);
    border-radius: 25px;
    padding: 30px;
    margin: 10px 0 25px 0;
    text-align: center;
    box-shadow:
        0 20px 70px
        rgba(0, 0, 0, 0.45);
}
.hero-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 8px;
}
.hero-text {
    font-size: 16px;
    color: #b8c4e8;
    line-height: 1.6;
}
/* ==========================================================
   STATUS BAR
   ========================================================== */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 12px;
    border-radius: 14px;
    background:
        rgba(12, 18, 45, 0.90);
    border:
        1px solid
        rgba(90, 120, 255, 0.25);
    color: #cbd7ff;
    font-size: 14px;
    margin-bottom: 20px;
}
.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #43ff87;
    box-shadow:
        0 0 15px
        #43ff87;
}
/* ==========================================================
   CARDS
   ========================================================== */
.dashboard-card {
    background:
        linear-gradient(
            145deg,
            rgba(17, 23, 55, 0.96),
            rgba(5, 8, 24, 0.98)
        );
    border:
        1px solid
        rgba(100, 125, 255, 0.24);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow:
        0 15px 45px
        rgba(0, 0, 0, 0.35),
        inset 0 1px 0
        rgba(255, 255, 255, 0.04);
}
/* ==========================================================
   METRICS
   ========================================================== */
[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(24, 32, 75, 0.98),
            rgba(8, 13, 35, 0.98)
        );
    border:
        1px solid
        rgba(105, 130, 255, 0.25);
    border-radius: 18px;
    padding: 18px;
    min-height: 105px;
    box-shadow:
        0 10px 35px
        rgba(0, 0, 0, 0.25);
}
[data-testid="stMetricLabel"] {
    color: #9eabd8 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 28px !important;
    font-weight: 900 !important;
}
/* ==========================================================
   BUTTON
   ========================================================== */
.stButton > button {
    width: 100%;
    min-height: 54px;
    border: none;
    border-radius: 14px;
    background:
        linear-gradient(
            90deg,
            #ff5a36,
            #ff8b35,
            #ff4e67
        );
    color: white;
    font-size: 17px;
    font-weight: 900;
    letter-spacing: 0.7px;
    box-shadow:
        0 10px 30px
        rgba(255, 90, 50, 0.28);
    transition:
        0.25s ease;
}
.stButton > button:hover {
    transform:
        translateY(-2px);
    box-shadow:
        0 15px 40px
        rgba(255, 90, 50, 0.45);
}
/* ==========================================================
   FILE UPLOADER
   ========================================================== */
[data-testid="stFileUploader"] {
    background:
        rgba(8, 13, 35, 0.90);
    border:
        1px dashed
        rgba(255, 140, 80, 0.50);
    border-radius: 18px;
    padding: 16px;
}
/* ==========================================================
   INPUTS
   ========================================================== */
.stNumberInput input {
    background:
        rgba(3, 7, 22, 0.95) !important;
    color:
        #ffffff !important;
    border:
        1px solid
        rgba(100, 130, 255, 0.35) !important;
    border-radius:
        10px !important;
}
.stNumberInput input:focus {
    border:
        1px solid
        #ff7547 !important;
    box-shadow:
        0 0 15px
        rgba(255, 100, 60, 0.25) !important;
}
/* ==========================================================
   ALERTS
   ========================================================== */
[data-testid="stAlert"] {
    border-radius:
        15px !important;
    border:
        1px solid
        rgba(120, 140, 255, 0.22);
}
/* ==========================================================
   DATAFRAME
   ========================================================== */
[data-testid="stDataFrame"] {
    border:
        1px solid
        rgba(100, 125, 255, 0.20);
    border-radius:
        15px;
    overflow:
        hidden;
}
/* ==========================================================
   TEXT
   ========================================================== */
p {
    color:
        #c1cbe8;
}
label {
    color:
        #d4dcf8 !important;
    font-weight:
        600 !important;
}
/* ==========================================================
   FOOTER
   ========================================================== */
.footer {
    text-align: center;
    color: #6f7ba5;
    font-size: 13px;
    padding: 25px;
    margin-top: 30px;
    border-top:
        1px solid
        rgba(100, 120, 180, 0.15);
}
/* ==========================================================
   SCROLLBAR
   ========================================================== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #02030b;
}
::-webkit-scrollbar-thumb {
    background: #ff663f;
    border-radius: 10px;
}
/* ==========================================================
   MOBILE
   ========================================================== */
@media (max-width: 768px) {
    h1 {
        font-size: 36px !important;
        letter-spacing: 1px;
    }
    .hero {
        padding: 20px;
    }
    .hero-title {
        font-size: 22px;
    }
    .dashboard-card {
        padding: 16px;
        border-radius: 16px;
    }
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
    }
}
</style>
    """, unsafe_allow_html=True)


# ============================================================
# LIVE CLOCK
# ============================================================

components.html("""
<div style="
    text-align:right;
    color:#9da9d3;
    font-family:Arial;
    font-size:13px;">
    <span id="clock">Connecting...</span>
</div>
<script>
function updateClock() {
    const now = new Date();
    document.getElementById("clock").innerHTML =
        "🕐 SYSTEM TIME • " +
        now.toLocaleString();
}
updateClock();
setInterval(updateClock, 1000);
</script>
    """, height=30)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """<div class="hero">
        <div class="hero-title">
            ☀️ SOLAR STORM AI
        </div>
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
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATASET
# ============================================================

st.subheader("📡 DATA INGESTION")

uploaded_file = st.file_uploader(
    "Upload OMNI Solar-Wind Dataset",
    type=["lst", "txt", "csv"]
)


if uploaded_file is None:

    st.info(
        "Upload your OMNI dataset to activate "
        "the Solar Storm AI prediction system."
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = pd.read_csv(
        uploaded_file,
        sep=r"\s+",
        header=None,
        names=[
            "YEAR",
            "DOY",
            "Hour",
            "Scalar_B",
            "Bz",
            "Proton_Density",
            "Solar_Wind_Speed",
            "Plasma_Beta",
            "Kp"
        ],
        engine="python"
    )

except Exception as error:

    st.error(
        f"Dataset loading error: {error}"
    )

    st.stop()


st.success(
    f"🟢 DATASET ONLINE • "
    f"{len(df):,} records loaded"
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


# ============================================================
# 24 HOUR TARGET
# ============================================================

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
                width=2
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=graph_data["Timestamp"],
            y=graph_data["Future_Kp"],
            mode="lines",
            name="Future Kp",
            line=dict(
                dash="dash",
                width=2
            )
        )
    )


    fig.add_hline(
        y=5,
        line_dash="dot",
        annotation_text="G1 STORM THRESHOLD"
    )


    fig.update_layout(

        height=500,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="white"
        ),

        xaxis_title="TIME",

        yaxis_title="Kp INDEX",

        hovermode="x unified"
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

        height=330,

        paper_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="white"
        )

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
                f"{x:.2f}"
                for x
                in importance["Importance"]
            ],

            textposition="outside"

        )

    )


    fig2.update_layout(

        height=330,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="white"
        ),

        xaxis_title="IMPORTANCE"

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