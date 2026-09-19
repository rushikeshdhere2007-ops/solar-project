// ============================================================
// SOLAR STORM AI 3D — FRONTEND ENGINE & THREE.JS 3D CANVAS
// ============================================================

const API_BASE = '/api';
let CURRENT_USER = null;

document.addEventListener('DOMContentLoaded', () => {
    init3DSpaceScene();
    init3DTiltEffect();
    initClock();

    checkAuthSession();
    checkBackendHealth();
    loadDashboardData();

    setupAuthModal();
    setupPredictorForm();
    setupDropzone();
    setupResetDemoButton();
});

// ============================================================
// THREE.JS 3D MAGNETOSPHERE & SOLAR WIND ENGINE
// ============================================================
function init3DSpaceScene() {
    const canvas = document.getElementById('bg-canvas-3d');
    if (!canvas || typeof THREE === 'undefined') return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 25;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 1. Earth Wireframe Sphere
    const earthGeo = new THREE.IcosahedronGeometry(6, 3);
    const earthMat = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        wireframe: true,
        transparent: true,
        opacity: 0.28
    });
    const earthMesh = new THREE.Mesh(earthGeo, earthMat);
    scene.add(earthMesh);

    // 2. Inner Glowing Core
    const coreGeo = new THREE.SphereGeometry(4.2, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
        color: 0x051238,
        transparent: true,
        opacity: 0.85
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);

    // 3. Atmosphere Halo Ring
    const haloGeo = new THREE.RingGeometry(6.4, 7.8, 64);
    const haloMat = new THREE.MeshBasicMaterial({
        color: 0xff6847,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.18
    });
    const haloMesh = new THREE.Mesh(haloGeo, haloMat);
    haloMesh.rotation.x = Math.PI / 2.5;
    scene.add(haloMesh);

    // 4. Solar Wind Stream Particles
    const particleCount = 700;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const speeds = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 80;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 50;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 40;
        speeds[i] = 0.1 + Math.random() * 0.25;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.35,
        transparent: true,
        opacity: 0.7
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // Parallax mouse tracking
    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.0008;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.0008;
    });

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);

        earthMesh.rotation.y += 0.003;
        haloMesh.rotation.z -= 0.002;

        camera.position.x += (mouseX * 15 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 15 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);

        // Move solar wind particles
        const posArr = particleSystem.geometry.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {
            posArr[i * 3] += speeds[i];
            if (posArr[i * 3] > 40) {
                posArr[i * 3] = -40;
            }
        }
        particleSystem.geometry.attributes.position.needsUpdate = true;

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ============================================================
// 3D TILT EFFECT FOR CARDS
// ============================================================
function init3DTiltEffect() {
    const cards = document.querySelectorAll('.tilt-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.01, 1.01, 1.01)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
    });
}

// ============================================================
// AUTHENTICATION MODAL ENGINE
// ============================================================
function setupAuthModal() {
    const modal = document.getElementById('auth-modal');
    const triggerBtn = document.getElementById('btn-auth-trigger');
    const closeBtn = document.getElementById('auth-close-btn');
    const guestBtn = document.getElementById('btn-guest-access');

    const tabLogin = document.getElementById('tab-login-btn');
    const tabRegister = document.getElementById('tab-register-btn');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const msgBox = document.getElementById('auth-msg');

    if (!modal) return;

    triggerBtn.addEventListener('click', () => {
        if (CURRENT_USER && CURRENT_USER.username !== 'guest') {
            // Log out
            localStorage.removeItem('solar_auth_token');
            CURRENT_USER = null;
            updateUserBadge(null);
            showAuthMsg('Logged out successfully.', 'success');
        }
        modal.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    guestBtn.addEventListener('click', () => modal.classList.add('hidden'));

    tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        msgBox.classList.add('hidden');
    });

    tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        msgBox.classList.add('hidden');
    });

    // Handle Login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        const btn = document.getElementById('btn-login-submit');
        btn.disabled = true;
        btn.innerText = 'VERIFYING CLEARANCE...';

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            if (data.success) {
                localStorage.setItem('solar_auth_token', data.token);
                CURRENT_USER = data.user;
                updateUserBadge(data.user);
                showAuthMsg(`AUTHENTICATED: Welcome ${data.user.name}`, 'success');
                setTimeout(() => modal.classList.add('hidden'), 1000);
            } else {
                showAuthMsg(`ERROR: ${data.error}`, 'error');
            }
        } catch (err) {
            showAuthMsg('Authentication API network error.', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> AUTHENTICATE COMMANDER';
        }
    });

    // Handle Registration
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('reg-name').value;
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;

        const btn = document.getElementById('btn-reg-submit');
        btn.disabled = true;
        btn.innerText = 'REGISTERING OPERATOR...';

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, username, password })
            });

            const data = await res.json();
            if (data.success) {
                localStorage.setItem('solar_auth_token', data.token);
                CURRENT_USER = data.user;
                updateUserBadge(data.user);
                showAuthMsg(`REGISTERED: Welcome ${data.user.name}`, 'success');
                setTimeout(() => modal.classList.add('hidden'), 1000);
            } else {
                showAuthMsg(`ERROR: ${data.error}`, 'error');
            }
        } catch (err) {
            showAuthMsg('Registration API network error.', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-user-plus"></i> REGISTER & ACCESS SYSTEM';
        }
    });
}

function showAuthMsg(msg, type) {
    const msgBox = document.getElementById('auth-msg');
    msgBox.classList.remove('hidden', 'error', 'success');
    msgBox.classList.add(type);
    msgBox.innerText = msg;
}

async function checkAuthSession() {
    const token = localStorage.getItem('solar_auth_token');
    if (!token) {
        updateUserBadge(null);
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            const data = await res.json();
            if (data.success) {
                CURRENT_USER = data.user;
                updateUserBadge(data.user);
            }
        } else {
            localStorage.removeItem('solar_auth_token');
            updateUserBadge(null);
        }
    } catch (e) {
        updateUserBadge(null);
    }
}

function updateUserBadge(user) {
    const nameEl = document.getElementById('user-name');
    const levelEl = document.getElementById('user-level');
    const labelEl = document.getElementById('auth-btn-label');
    const lockIcon = document.getElementById('auth-lock-icon');

    if (user && user.username !== 'guest') {
        nameEl.innerText = `OPERATOR: ${user.name.toUpperCase()}`;
        levelEl.innerText = `${user.role.toUpperCase()} • ${user.level.toUpperCase()}`;
        labelEl.innerText = 'LOGOUT';
        lockIcon.className = 'fa-solid fa-unlock text-cyan';
    } else {
        nameEl.innerText = 'OPERATOR: GUEST';
        levelEl.innerText = 'LEVEL 1 PUBLIC ACCESS';
        labelEl.innerText = 'LOGIN';
        lockIcon.className = 'fa-solid fa-lock';
    }
}

// ============================================================
// LIVE MISSION CLOCK
// ============================================================
function initClock() {
    const clockEl = document.getElementById('mission-clock-text');
    function update() {
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase();
        const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
        if (clockEl) {
            clockEl.innerHTML = `MISSION TIME • ${dateStr} • ${timeStr} UTC`;
        }
    }
    update();
    setInterval(update, 1000);
}

// ============================================================
// BACKEND HEALTH CHECK
// ============================================================
async function checkBackendHealth() {
    const statusPill = document.getElementById('backend-status');
    const statusText = document.getElementById('backend-text');
    try {
        const res = await fetch(`${API_BASE}/status`);
        if (res.ok) {
            const data = await res.json();
            statusPill.querySelector('.status-dot').className = 'status-dot green';
            statusText.innerText = `REST API ONLINE • ${data.dataset_records} OMNI RECORDS`;
        } else {
            throw new Error('API Response Error');
        }
    } catch (err) {
        statusPill.querySelector('.status-dot').className = 'status-dot red';
        statusText.innerText = 'BACKEND API DISCONNECTED';
    }
}

// ============================================================
// FETCH & RENDER DASHBOARD DATA
// ============================================================
async function loadDashboardData() {
    try {
        const [telemetryRes, modelRes] = await Promise.all([
            fetch(`${API_BASE}/telemetry`),
            fetch(`${API_BASE}/model-info`)
        ]);

        if (telemetryRes.ok) {
            const tData = await telemetryRes.json();
            updateMetricCards(tData.summary, tData.latest);
            renderKpChart(tData.time_series);
            renderRiskGauge(tData.summary.risk_score);
            renderSolarWindChart(tData.time_series);
            renderTelemetryTable(tData.recent);
        }

        if (modelRes.ok) {
            const mData = await modelRes.json();
            document.getElementById('val-accuracy').innerText = `${mData.metrics.accuracy}`;
            renderFeatureImportanceChart(mData.metrics.feature_importances);
        }
    } catch (err) {
        console.error('Error fetching dashboard telemetry:', err);
    }
}

// ============================================================
// UPDATE TOP METRIC CARDS
// ============================================================
function updateMetricCards(summary, latest) {
    document.getElementById('val-kp').innerText = latest.Kp !== undefined ? latest.Kp.toFixed(1) : '--';
    document.getElementById('val-speed').innerHTML = `${latest.Solar_Wind_Speed !== undefined ? Math.round(latest.Solar_Wind_Speed) : '--'} <span class="unit">km/s</span>`;
    document.getElementById('val-bz').innerHTML = `${latest.Bz !== undefined ? latest.Bz.toFixed(1) : '--'} <span class="unit">nT</span>`;
    document.getElementById('val-risk').innerHTML = `${summary.risk_score} <span class="unit">%</span>`;

    const badgeEl = document.getElementById('badge-kp');
    if (summary.current_kp >= 5) {
        badgeEl.innerHTML = `<span class="badge storm">${summary.storm_class}</span>`;
    } else if (summary.current_kp >= 4) {
        badgeEl.innerHTML = `<span class="badge active">${summary.storm_class}</span>`;
    } else {
        badgeEl.innerHTML = `<span class="badge quiet">${summary.storm_class}</span>`;
    }
}

// ============================================================
// PLOTLY CHARTS
// ============================================================

const chartLayoutDefaults = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#8e9cc8' },
    margin: { l: 45, r: 25, t: 25, b: 40 },
    xaxis: {
        gridcolor: 'rgba(0, 240, 255, 0.08)',
        linecolor: 'rgba(0, 240, 255, 0.25)',
        tickfont: { size: 10, color: '#6f7ba5' }
    },
    yaxis: {
        gridcolor: 'rgba(0, 240, 255, 0.08)',
        linecolor: 'rgba(0, 240, 255, 0.25)',
        tickfont: { size: 10, color: '#6f7ba5' }
    }
};

function renderKpChart(ts) {
    const traceKp = {
        x: ts.timestamps,
        y: ts.kp,
        mode: 'lines+markers',
        name: 'Kp Index',
        line: { color: '#00f0ff', width: 2.5, shape: 'spline' },
        marker: { size: 4, color: '#ff6847' },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 240, 255, 0.06)',
        hovertemplate: '<b>Timestamp</b>: %{x}<br><b>Kp Index</b>: %{y:.1f}<extra></extra>'
    };

    const thresholdLine = {
        type: 'line',
        x0: ts.timestamps[0],
        x1: ts.timestamps[ts.timestamps.length - 1],
        y0: 5.0,
        y1: 5.0,
        line: { color: '#ff3b5c', width: 2, dash: 'dash' }
    };

    const layout = {
        ...chartLayoutDefaults,
        height: 320,
        shapes: [thresholdLine],
        annotations: [{
            x: ts.timestamps[Math.floor(ts.timestamps.length / 2)],
            y: 5.2,
            text: 'STORM THRESHOLD (Kp ≥ 5.0)',
            showarrow: false,
            font: { color: '#ff3b5c', size: 10, family: 'Space Grotesk' }
        }]
    };

    Plotly.newPlot('chart-kp', [traceKp], layout, { responsive: true, displayModeBar: false });
}

function renderRiskGauge(score) {
    const data = [{
        type: "indicator",
        mode: "gauge+number",
        value: score,
        number: { suffix: "%", font: { color: "#ffffff", family: "Space Grotesk", size: 32 } },
        gauge: {
            axis: { range: [0, 100], tickwidth: 1, tickcolor: "#6f7ba5" },
            bar: { color: score >= 60 ? "#ff3b5c" : (score >= 35 ? "#ffb347" : "#00f0ff"), width: 0.28 },
            bgcolor: "rgba(10, 16, 42, 0.8)",
            bordercolor: "rgba(0, 240, 255, 0.25)",
            steps: [
                { range: [0, 30], color: "rgba(67, 255, 135, 0.15)" },
                { range: [30, 60], color: "rgba(255, 179, 71, 0.15)" },
                { range: [60, 100], color: "rgba(255, 59, 92, 0.2)" }
            ]
        }
    }];

    const layout = {
        ...chartLayoutDefaults,
        height: 320,
        margin: { l: 30, r: 30, t: 30, b: 20 }
    };

    Plotly.newPlot('chart-gauge', data, layout, { responsive: true, displayModeBar: false });
}

function renderSolarWindChart(ts) {
    const traceSpeed = {
        x: ts.timestamps,
        y: ts.solar_wind_speed,
        name: 'Wind Speed (km/s)',
        type: 'scatter',
        line: { color: '#ff6847', width: 2 },
        hovertemplate: '%{x}<br>Speed: %{y:.1f} km/s<extra></extra>'
    };

    const traceBz = {
        x: ts.timestamps,
        y: ts.bz,
        name: 'IMF Bz (nT)',
        yaxis: 'y2',
        type: 'scatter',
        line: { color: '#00f0ff', width: 1.8, dash: 'dot' },
        hovertemplate: '%{x}<br>Bz: %{y:.1f} nT<extra></extra>'
    };

    const layout = {
        ...chartLayoutDefaults,
        height: 320,
        yaxis: { ...chartLayoutDefaults.yaxis, title: 'Speed (km/s)' },
        yaxis2: {
            title: 'Bz (nT)',
            overlaying: 'y',
            side: 'right',
            gridcolor: 'rgba(0,0,0,0)',
            tickfont: { size: 10, color: '#00f0ff' }
        },
        legend: { orientation: 'h', x: 0, y: 1.15, font: { color: '#8e9cc8' } }
    };

    Plotly.newPlot('chart-solarwind', [traceSpeed, traceBz], layout, { responsive: true, displayModeBar: false });
}

function renderFeatureImportanceChart(importances) {
    if (!importances) return;

    const nameMap = {
        'Bz': 'IMF Bz',
        'Kp': 'Kp Index',
        'Proton_Density': 'Proton Density',
        'Solar_Wind_Speed': 'Wind Speed',
        'Scalar_B': 'Scalar B',
        'Plasma_Beta': 'Plasma Beta'
    };

    const items = Object.entries(importances).map(([k, v]) => ({
        name: nameMap[k] || k.replace(/_/g, ' '),
        val: parseFloat(v) || 0
    })).sort((a, b) => a.val - b.val);

    const yCategories = items.map(d => d.name);
    const xValues = items.map(d => d.val);
    const textLabels = items.map(d => `${(d.val * 100).toFixed(1)}%`);

    const barColors = [
        '#00d4ff',
        '#00f0ff',
        '#ffb347',
        '#ff9547',
        '#ff6847',
        '#ff3b5c'
    ];

    const trace = {
        type: 'bar',
        orientation: 'h',
        x: xValues,
        y: yCategories,
        text: textLabels,
        textposition: 'outside',
        cliponaxis: false,
        textfont: {
            color: '#ffffff',
            size: 11,
            family: 'JetBrains Mono, monospace'
        },
        marker: {
            color: barColors,
            line: {
                color: 'rgba(0, 240, 255, 0.4)',
                width: 1
            }
        },
        hoverinfo: 'text+y',
        hovertext: items.map(d => `${d.name}: ${(d.val * 100).toFixed(1)}% importance`)
    };

    const maxVal = Math.max(...xValues, 0.1);

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif', color: '#8e9cc8' },
        height: 320,
        margin: { l: 110, r: 50, t: 15, b: 35 },
        xaxis: {
            type: 'linear',
            range: [0, maxVal * 1.3],
            tickformat: '.0%',
            gridcolor: 'rgba(0, 240, 255, 0.08)',
            linecolor: 'rgba(0, 240, 255, 0.25)',
            tickfont: { size: 10, color: '#6f7ba5' },
            zeroline: false
        },
        yaxis: {
            type: 'category',
            autorange: true,
            gridcolor: 'rgba(0,0,0,0)',
            linecolor: 'rgba(0, 240, 255, 0.25)',
            tickfont: { size: 11, color: '#e2e8ff', family: 'Space Grotesk, sans-serif' }
        }
    };

    Plotly.newPlot('chart-importance', [trace], layout, { responsive: true, displayModeBar: false });
}

// ============================================================
// TELEMETRY TABLE
// ============================================================
function renderTelemetryTable(records) {
    const tbody = document.getElementById('table-body');
    if (!tbody || !records || records.length === 0) return;

    tbody.innerHTML = records.reverse().slice(0, 12).map(r => {
        const kp = r.Kp !== undefined ? r.Kp.toFixed(1) : '--';
        let statusBadge = '<span class="badge quiet">🟢 QUIET</span>';
        if (r.Kp >= 5) {
            statusBadge = '<span class="badge storm">🔴 G2+ STORM</span>';
        } else if (r.Kp >= 4) {
            statusBadge = '<span class="badge active">🟡 ACTIVE</span>';
        }

        return `
            <tr>
                <td>Y${r.YEAR}-D${r.DOY}-H${r.Hour}</td>
                <td>${r.Bz !== undefined ? r.Bz.toFixed(1) : '--'}</td>
                <td>${r.Proton_Density !== undefined ? r.Proton_Density.toFixed(1) : '--'}</td>
                <td>${r.Solar_Wind_Speed !== undefined ? Math.round(r.Solar_Wind_Speed) : '--'}</td>
                <td>${r.Plasma_Beta !== undefined ? r.Plasma_Beta.toFixed(2) : '--'}</td>
                <td style="font-weight: 700; color: #ffffff;">${kp}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// PREDICTOR FORM SUBMISSION
// ============================================================
function setupPredictorForm() {
    const form = document.getElementById('predict-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            bz: parseFloat(document.getElementById('input-bz').value),
            speed: parseFloat(document.getElementById('input-speed').value),
            density: parseFloat(document.getElementById('input-density').value),
            scalar_b: parseFloat(document.getElementById('input-scalar-b').value),
            plasma_beta: parseFloat(document.getElementById('input-beta').value),
            kp: parseFloat(document.getElementById('input-kp').value)
        };

        const btn = document.getElementById('btn-predict');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> QUERYING REST API MODEL...';

        try {
            const res = await fetch(`${API_BASE}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                displayPredictionResult(data);
            }
        } catch (err) {
            console.error('Prediction API error:', err);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-bolt"></i> RUN 24-HOUR FORECAST MODEL';
        }
    });
}

function displayPredictionResult(res) {
    const outputBox = document.getElementById('prediction-output');
    outputBox.classList.remove('hidden');

    document.getElementById('res-prob').innerText = `${res.storm_probability_percent}%`;
    document.getElementById('res-kp').innerText = `Kp ${res.predicted_kp_24h}`;
    
    const badge = document.getElementById('res-risk-level');
    badge.innerText = res.risk_level;
    badge.style.borderColor = res.risk_color;
    badge.style.color = res.risk_color;

    document.getElementById('res-advisory').innerText = res.advisory;
    outputBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================================
// DROPZONE & UPLOAD
// ============================================================
function setupDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => { e.preventDefault(); dropzone.style.borderColor = '#00f0ff'; }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => { e.preventDefault(); dropzone.style.borderColor = 'var(--border-orange)'; }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) handleFileUpload(files[0]);
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) handleFileUpload(fileInput.files[0]);
    });
}

async function handleFileUpload(file) {
    const statusMsg = document.getElementById('upload-status');
    statusMsg.classList.remove('hidden');
    statusMsg.innerText = `⏳ Ingesting & training REST API on dataset "${file.name}"...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            statusMsg.innerText = `🟢 SUCCESS: ${data.message}`;
            loadDashboardData();
            checkBackendHealth();
        } else {
            const err = await res.json();
            statusMsg.innerText = `❌ ERROR: ${err.error}`;
        }
    } catch (e) {
        statusMsg.innerText = `❌ UPLOAD FAILED: Server unreachable.`;
    }
}

// ============================================================
// RESET DEMO TELEMETRY STREAM
// ============================================================
function setupResetDemoButton() {
    const btn = document.getElementById('btn-reset-demo');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> RESETTING...';
        try {
            const res = await fetch(`${API_BASE}/reset-demo`, { method: 'POST' });
            if (res.ok) {
                loadDashboardData();
                checkBackendHealth();
            }
        } catch (err) {
            console.error('Reset error:', err);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-rotate-left"></i> RESET DEMO TELEMETRY STREAM';
        }
    });
}
