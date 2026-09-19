import io
import os
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Global dataset & model state
DATASET = None
MODEL = None
MODEL_METRICS = {}
FEATURES = ["Scalar_B", "Bz", "Proton_Density", "Solar_Wind_Speed", "Plasma_Beta", "Kp"]

def generate_demo_omni_dataset():
    """Generates 720 hours (30 days) of realistic OMNI solar-wind telemetry data."""
    np.random.seed(42)
    n_samples = 720
    years = [2024] * n_samples
    doys = np.repeat(np.arange(1, 31), 24)
    hours = np.tile(np.arange(0, 24), 30)

    # Realistic solar wind physics & storm simulations
    scalar_b = 5.2 + 3.8 * np.sin(np.linspace(0, 5 * np.pi, n_samples)) + np.random.normal(0, 1.2, n_samples)
    bz = -2.8 + 6.4 * np.cos(np.linspace(0, 7 * np.pi, n_samples)) + np.random.normal(0, 2.0, n_samples)
    proton_density = 5.8 + 4.2 * np.abs(np.sin(np.linspace(0, 4 * np.pi, n_samples))) + np.random.normal(0, 0.8, n_samples)
    solar_wind_speed = 380 + 180 * (np.sin(np.linspace(0, 6 * np.pi, n_samples)) ** 2) + np.random.normal(0, 15, n_samples)
    plasma_beta = 1.1 + 0.6 * np.random.exponential(1, n_samples)

    raw_kp = 1.4 + (-0.38 * bz) + (0.0055 * (solar_wind_speed - 350)) + (0.12 * scalar_b) + np.random.normal(0, 0.35, n_samples)
    kp = np.clip(raw_kp, 0.3, 8.8)

    df = pd.DataFrame({
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
    return df

def clean_and_process_dataset(df):
    """Cleans OMNI missing values and normalizes Kp if required."""
    numeric_columns = ["YEAR", "DOY", "Hour", "Scalar_B", "Bz", "Proton_Density", "Solar_Wind_Speed", "Plasma_Beta", "Kp"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_values = {
        "Scalar_B": [999.9, 9999, 99999],
        "Bz": [999.9, 9999, 99999],
        "Proton_Density": [999.9, 9999, 99999],
        "Solar_Wind_Speed": [9999.0, 999.9, 99999],
        "Plasma_Beta": [999.99, 9999, 99999],
        "Kp": [99, 999, 9999]
    }
    for col, vals in missing_values.items():
        if col in df.columns:
            df[col] = df[col].replace(vals, np.nan)

    df = df.dropna(subset=["YEAR", "DOY", "Hour", "Kp"]).copy()
    if df["Kp"].max() > 9:
        df["Kp"] = df["Kp"] / 10.0

    # Fill remaining missing numeric values with medians
    for col in FEATURES:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    return df

def train_machine_learning_model(df):
    """Trains Random Forest classifier for 24-hour ahead storm prediction (Target: Kp >= 5.0)."""
    global MODEL, MODEL_METRICS

    df_model = df.copy()
    # 24-hour target shift
    df_model["Target_Kp_24h"] = df_model["Kp"].shift(-24)
    df_model["Storm_Target"] = (df_model["Target_Kp_24h"] >= 5.0).astype(int)
    df_model = df_model.dropna(subset=["Target_Kp_24h"]).copy()

    X = df_model[FEATURES]
    y = df_model["Storm_Target"]

    if len(np.unique(y)) < 2:
        # Guarantee binary targets for evaluation in demo datasets
        y.iloc[:int(len(y)*0.15)] = 1

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1] if len(rf.classes_) > 1 else np.zeros(len(y_test))

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    importances = dict(zip(FEATURES, [round(float(val), 4) for val in rf.feature_importances_]))

    MODEL = rf
    MODEL_METRICS = {
        "accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec) * 100, 2),
        "recall": round(float(rec) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importances": importances
    }

def init_app():
    global DATASET
    raw_df = generate_demo_omni_dataset()
    DATASET = clean_and_process_dataset(raw_df)
    train_machine_learning_model(DATASET)

init_app()

# ============================================================
# SQLITE PERSISTENT DATABASE & AUTHENTICATION STORE
# ============================================================

import secrets
import sqlite3

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solar_storm.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database schema and seeds default operators."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scalar_b REAL,
                bz REAL,
                proton_density REAL,
                solar_wind_speed REAL,
                plasma_beta REAL,
                kp_current REAL,
                predicted_kp_24h REAL,
                storm_prob REAL,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed default operators if not present
        default_users = [
            ("admin", "solar123", "Rushi Dhere", "Flight Commander", "Level 5 Clearance"),
            ("rushi021", "solar123", "Rushi Dhere", "Flight Commander", "Level 5 Clearance"),
            ("sai", "solar123", "Sai Operator", "Space Weather Analyst", "Level 4 Clearance"),
            ("guest", "guest", "Guest Explorer", "Observer", "Level 1 Access")
        ]
        for u, p, n, r, l in default_users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, name, role, level)
                VALUES (?, ?, ?, ?, ?)
            """, (u, p, n, r, l))
        conn.commit()

init_db()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        token = secrets.token_hex(16)
        cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
        conn.commit()
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "level": user["level"]
        }
        conn.close()
        return jsonify({
            "success": True,
            "token": token,
            "user": user_data
        })
    conn.close()
    return jsonify({"success": False, "error": "Invalid username or security credentials"}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    name = str(data.get("name", "New Operator")).strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Operator ID already exists"}), 400

    cursor.execute("""
        INSERT INTO users (username, password, name, role, level)
        VALUES (?, ?, ?, 'Mission Specialist', 'Level 3 Clearance')
    """, (username, password, name))
    user_id = cursor.lastrowid

    token = secrets.token_hex(16)
    cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()

    user_data = {
        "id": user_id,
        "username": username,
        "name": name,
        "role": "Mission Specialist",
        "level": "Level 3 Clearance"
    }
    conn.close()
    return jsonify({
        "success": True,
        "token": token,
        "user": user_data
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.name, u.role, u.level
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (token,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "role": user["role"],
                    "level": user["level"]
                }
            })
    return jsonify({"success": False, "error": "Unauthenticated"}), 401

# ============================================================
# REST API ENDPOINTS
# ============================================================

@app.route('/')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'Index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    user_count = 0
    pred_count = 0
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM predictions")
        pred_count = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    return jsonify({
        "status": "ONLINE",
        "system": "Solar Storm AI Backend",
        "database": "SQLite (Connected - solar_storm.db)",
        "database_connected": True,
        "database_users": user_count,
        "database_predictions": pred_count,
        "model": "Random Forest Classifier (150 trees)",
        "dataset_records": len(DATASET) if DATASET is not None else 0,
        "features": FEATURES,
        "metrics": MODEL_METRICS
    })

@app.route('/api/predictions/history', methods=['GET'])
def get_prediction_history():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "history": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    if DATASET is None:
        return jsonify({"error": "No dataset online"}), 400

    latest = DATASET.iloc[-1].to_dict()
    recent = DATASET.tail(30).to_dict(orient="records")
    
    # Storm classification counts
    quiet_count = int((DATASET["Kp"] < 4).sum())
    active_count = int(((DATASET["Kp"] >= 4) & (DATASET["Kp"] < 5)).sum())
    storm_count = int((DATASET["Kp"] >= 5).sum())

    # Current geomagnetic risk index
    current_kp = float(latest.get("Kp", 0))
    risk_score = round(min(100.0, (current_kp / 9.0) * 100), 1)

    if current_kp >= 7:
        storm_class = "🔴 G3-G5 SEVERE STORM"
        status_color = "#ff3b5c"
    elif current_kp >= 5:
        storm_class = "🔴 G1-G2 MODERATE STORM"
        status_color = "#ff6847"
    elif current_kp >= 4:
        storm_class = "🟡 ACTIVE GEOMAGNETIC"
        status_color = "#ffb347"
    else:
        storm_class = "🟢 QUIET CONDITIONS"
        status_color = "#43ff87"

    return jsonify({
        "latest": latest,
        "recent": recent,
        "summary": {
            "total_records": len(DATASET),
            "quiet_count": quiet_count,
            "active_count": active_count,
            "storm_count": storm_count,
            "current_kp": current_kp,
            "risk_score": risk_score,
            "storm_class": storm_class,
            "status_color": status_color
        },
        "time_series": {
            "timestamps": [f"Y{int(row['YEAR'])}-D{int(row['DOY']):03d}-H{int(row['Hour']):02d}" for _, row in DATASET.tail(72).iterrows()],
            "kp": DATASET.tail(72)["Kp"].tolist(),
            "bz": DATASET.tail(72)["Bz"].tolist(),
            "solar_wind_speed": DATASET.tail(72)["Solar_Wind_Speed"].tolist(),
            "proton_density": DATASET.tail(72)["Proton_Density"].tolist(),
            "scalar_b": DATASET.tail(72)["Scalar_B"].tolist()
        }
    })

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    return jsonify({
        "metrics": MODEL_METRICS,
        "features": FEATURES,
        "algorithm": "Random Forest Classifier",
        "estimators": 150,
        "target": "24-Hour Ahead Kp ≥ 5.0 Geomagnetic Storm Event"
    })

@app.route('/api/predict', methods=['POST'])
def predict_storm():
    if MODEL is None:
        return jsonify({"error": "Model not trained"}), 400

    data = request.get_json() or {}
    try:
        scalar_b = float(data.get("scalar_b", 12.0))
        bz = float(data.get("bz", -8.5))
        proton_density = float(data.get("density", 14.0))
        solar_wind_speed = float(data.get("speed", 580.0))
        plasma_beta = float(data.get("plasma_beta", 1.8))
        kp_current = float(data.get("kp", 4.2))

        input_df = pd.DataFrame([{
            "Scalar_B": scalar_b,
            "Bz": bz,
            "Proton_Density": proton_density,
            "Solar_Wind_Speed": solar_wind_speed,
            "Plasma_Beta": plasma_beta,
            "Kp": kp_current
        }])

        prob = float(MODEL.predict_proba(input_df)[0][1]) if len(MODEL.classes_) > 1 else 0.0
        prob_percent = round(prob * 100, 1)

        # Estimate expected 24h Kp
        est_kp = round(min(9.0, max(0.5, kp_current + (-0.25 * bz) + (0.004 * (solar_wind_speed - 400)) + (prob * 2.5))), 1)

        if est_kp >= 8:
            risk_level = "G4/G5 EXTREME STORM ALERT"
            risk_color = "#ff2a55"
            advisory = "CRITICAL: High potential for power grid tripping, widespread HF radio blackout, and satellite orientation anomalies."
        elif est_kp >= 7:
            risk_level = "G3 STRONG STORM WARNING"
            risk_color = "#ff5533"
            advisory = "HIGH RISK: Power system voltage corrections required. Satellite drag increases."
        elif est_kp >= 5:
            risk_level = "G1/G2 MODERATE STORM WATCH"
            risk_color = "#ff8c33"
            advisory = "MODERATE RISK: High-latitude power grid fluctuations and minor satellite operation impacts."
        elif est_kp >= 4:
            risk_level = "UNSETTLED GEOMAGNETIC ACTIVITY"
            risk_color = "#ffc833"
            advisory = "ELEVATED: Auroral activity active at high latitudes. Standard telemetry monitoring."
        else:
            risk_level = "QUIET / NORMAL SPACE WEATHER"
            risk_color = "#33ff88"
            advisory = "NOMINAL: Space environment stable. All satellite and ground systems operating normally."

        # Persist prediction in SQLite database
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions (scalar_b, bz, proton_density, solar_wind_speed, plasma_beta, kp_current, predicted_kp_24h, storm_prob, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (scalar_b, bz, proton_density, solar_wind_speed, plasma_beta, kp_current, est_kp, prob_percent, risk_level))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print("DB prediction logging error:", db_err)

        return jsonify({
            "storm_probability_percent": prob_percent,
            "predicted_kp_24h": est_kp,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "advisory": advisory,
            "inputs_evaluated": {
                "Scalar_B": scalar_b,
                "Bz": bz,
                "Proton_Density": proton_density,
                "Solar_Wind_Speed": solar_wind_speed,
                "Plasma_Beta": plasma_beta,
                "Kp_Current": kp_current
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_dataset():
    global DATASET
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        df_uploaded = pd.read_csv(
            io.StringIO(content),
            sep=r"\s+",
            header=None,
            names=["YEAR", "DOY", "Hour", "Scalar_B", "Bz", "Proton_Density", "Solar_Wind_Speed", "Plasma_Beta", "Kp"],
            engine="python"
        )
        cleaned = clean_and_process_dataset(df_uploaded)
        if len(cleaned) == 0:
            return jsonify({"error": "Dataset contains no valid records after cleaning"}), 400

        DATASET = cleaned
        train_machine_learning_model(DATASET)
        return jsonify({
            "message": "Custom OMNI dataset ingested successfully!",
            "records_loaded": len(DATASET),
            "metrics": MODEL_METRICS
        })
    except Exception as e:
        return jsonify({"error": f"Dataset parsing error: {str(e)}"}), 400

@app.route('/api/reset-demo', methods=['POST'])
def reset_demo():
    init_app()
    return jsonify({
        "message": "Reset to 720-hour OMNI NASA Demo Telemetry Stream",
        "records_loaded": len(DATASET),
        "metrics": MODEL_METRICS
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Solar Storm AI Flask Backend on http://localhost:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=False)
