// Main Frontend Application Script
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initCopilotDrawer();
    loadDashboardStats();
    loadAgentCollaboration();
    initCvStudio();
    initAnalytics();
    initEntitiesExplorer();
    loadReport();
});

// 1. Navigation Tab Switching
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            
            navItems.forEach(n => n.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            item.classList.add('active');
            const targetPanel = document.getElementById(targetTab);
            if (targetPanel) targetPanel.classList.add('active');
        });
    });
}

// 2. Executive Dashboard Stats & Radar Chart
let radarChartInstance = null;
let equipChartInstance = null;

async function loadDashboardStats() {
    try {
        const res = await fetch('/api/dashboard/stats');
        const data = await res.json();

        document.getElementById('header-risk-score').innerText = `${data.composite_risk_score} | ${data.overall_risk_level}`;
        document.getElementById('dash-risk-score').innerText = data.composite_risk_score;
        document.getElementById('dash-risk-level').innerText = `Status: ${data.overall_risk_level} RISK`;
        document.getElementById('dash-ppe-pct').innerText = `${data.ppe_compliance_pct}%`;
        document.getElementById('dash-worker-count').innerText = `Active Workers Logged: ${data.active_workers_count}`;
        document.getElementById('dash-weather-rain').innerText = `${data.weather_summary.rainfall_mm || 38.0} mm`;
        document.getElementById('dash-weather-condition').innerText = data.weather_summary.condition || "Thunderstorm Forecast";

        // Render Alerts
        const alertContainer = document.getElementById('dash-alert-feed');
        if (alertContainer && data.recent_alerts) {
            alertContainer.innerHTML = data.recent_alerts.map(a => `
                <div class="alert-item">
                    <div class="alert-item-header">
                        <span>🚨 ${a.severity}</span>
                        <span>${a.source_agent}</span>
                    </div>
                    <div class="alert-title">${a.title}</div>
                    <div class="alert-msg">${a.message}</div>
                </div>
            `).join('');
        }

        renderRiskRadarChart(data.composite_risk_score, data.ppe_compliance_pct);
    } catch (e) {
        console.error("Dashboard stats error:", e);
    }
}

function renderRiskRadarChart(riskScore, ppePct) {
    const ctx = document.getElementById('chart-risk-radar');
    if (!ctx) return;

    if (radarChartInstance) radarChartInstance.destroy();

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Safety & PPE', 'Weather Risk', 'Schedule Delay', 'Cost Variance', 'Equipment Failure', 'Structural Quality'],
            datasets: [{
                label: 'Domain Risk Index',
                data: [100 - ppePct, 75, 55, 42, 68, 25],
                backgroundColor: 'rgba(6, 182, 212, 0.2)',
                borderColor: '#06b6d4',
                pointBackgroundColor: '#06b6d4'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255,255,255,0.1)' },
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    pointLabels: { color: '#94a3b8', font: { size: 11 } },
                    ticks: { display: false, max: 100 }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// 3. Computer Vision Safety Studio
function initCvStudio() {
    const dropZone = document.getElementById('cv-drop-zone');
    const fileInput = document.getElementById('cv-file-input');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) processCvFile(e.target.files[0]);
        });
    }

    const btn1 = document.getElementById('btn-preset-1');
    const btn2 = document.getElementById('btn-preset-2');
    if (btn1) btn1.addEventListener('click', () => runPresetCv("preset_feed_shearwall.jpg"));
    if (btn2) btn2.addEventListener('click', () => runPresetCv("preset_feed_crane.jpg"));
}

async function processCvFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const placeholder = document.getElementById('cv-placeholder');
    if (placeholder) placeholder.innerHTML = `<div class="spinner-icon">⏳</div><p>Running Computer Vision PPE Detector...</p>`;

    try {
        const res = await fetch('/api/safety/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        renderCvResults(data);
    } catch (e) {
        console.error("CV error:", e);
    }
}

function runPresetCv(filename) {
    // Generate dummy image file for preset trigger
    const canvas = document.createElement('canvas');
    canvas.width = 640; canvas.height = 480;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = "#1e293b"; ctx.fillRect(0,0,640,480);
    ctx.fillStyle = "#06b6d4"; ctx.font = "20px Inter"; ctx.fillText("Preset Construction Feed: Shear Wall Zone", 80, 240);
    
    canvas.toBlob(blob => {
        const file = new File([blob], filename, { type: 'image/jpeg' });
        processCvFile(file);
    });
}

function renderCvResults(data) {
    const imgEl = document.getElementById('cv-result-img');
    const placeholder = document.getElementById('cv-placeholder');
    const card = document.getElementById('cv-results-card');

    if (imgEl && placeholder && card) {
        placeholder.style.display = 'none';
        imgEl.style.display = 'block';
        imgEl.src = data.annotated_image_base64;
        card.style.display = 'block';

        document.getElementById('cv-res-score').innerText = `Safety Score: ${data.safety_score}%`;
        document.getElementById('cv-res-workers').innerText = `Workers Detected: ${data.worker_count}`;

        const vList = document.getElementById('cv-violations-list');
        if (data.violations && data.violations.length > 0) {
            vList.innerHTML = `<strong>Violations Flagged:</strong><ul>` + data.violations.map(v => `<li>⚠️ ${v}</li>`).join('') + `</ul>`;
        } else {
            vList.innerHTML = `<span class="text-success">✅ All detected workers compliant with mandatory PPE safety rules.</span>`;
        }
    }
}

// 4. Agent Collaboration Hub
async function loadAgentCollaboration() {
    try {
        const res = await fetch('/api/agents/collaborate');
        const data = await res.json();

        // Render Sidebar Mini Agent List
        const miniList = document.getElementById('mini-agent-list');
        if (miniList && data.agent_summaries) {
            miniList.innerHTML = data.agent_summaries.map(a => `
                <div class="mini-agent-item">
                    <span>${a.id}</span>
                    <span class="agent-dot"></span>
                </div>
            `).join('');
        }

        // Render Full Grid
        const grid = document.getElementById('agents-full-grid');
        if (grid && data.agent_summaries) {
            grid.innerHTML = data.agent_summaries.map(a => `
                <div class="agent-card">
                    <div class="agent-card-header">
                        <span>🤖 ${a.id}</span>
                        <span class="text-success">ONLINE</span>
                    </div>
                    <div class="agent-role">Autonomous Domain Agent</div>
                    <div class="agent-insight">${a.summary_insight}</div>
                </div>
            `).join('');
        }

        // Render Collaboration Messages
        const stream = document.getElementById('agent-collaboration-stream');
        if (stream && data.inter_agent_collaboration) {
            stream.innerHTML = data.inter_agent_collaboration.map(m => `
                <div class="msg-bubble">
                    <div class="msg-header">${m.sender} ➔ ${m.receiver}</div>
                    <div>"${m.message}"</div>
                </div>
            `).join('') + `
                <div class="msg-bubble" style="background: rgba(16, 185, 129, 0.1); border-color: var(--accent-emerald);">
                    <div class="msg-header" style="color: var(--accent-emerald);">🛡️ Synthesized Multi-Agent Joint Action Plan</div>
                    <div>${data.joint_mitigation_action}</div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Agent collaboration error:", e);
    }
}

// 5. Predictive Analytics Module
function initAnalytics() {
    const btnSched = document.getElementById('btn-predict-schedule');
    const btnCost = document.getElementById('btn-predict-cost');

    if (btnSched) {
        btnSched.addEventListener('click', async () => {
            const rain = parseFloat(document.getElementById('ml-rain-input').value) || 38.0;
            const workers = parseInt(document.getElementById('ml-workers-input').value) || 64;

            const res = await fetch('/api/predictive/schedule-delay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ weather_rainfall_mm: rain, active_workers: workers })
            });
            const data = await res.json();
            document.getElementById('schedule-ml-output').innerHTML = `
                <div class="alert-item" style="border-left-color: var(--accent-cyan);">
                    <strong>ML Predicted Delay: ${data.predicted_delay_days} Days</strong> (${data.delay_risk_level} RISK)<br>
                    <small>💡 Recommendation: ${data.mitigation_recommendation}</small>
                </div>
            `;
        });
    }

    if (btnCost) {
        btnCost.addEventListener('click', async () => {
            const delay = parseFloat(document.getElementById('ml-delay-input').value) || 3.5;
            const shortage = document.getElementById('ml-shortage-select').value;

            const res = await fetch('/api/predictive/cost-overrun', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ schedule_delay_days: delay, material_shortage_risk: shortage })
            });
            const data = await res.json();
            document.getElementById('cost-ml-output').innerHTML = `
                <div class="alert-item" style="border-left-color: var(--accent-amber);">
                    <strong>Predicted Budget Overrun: +${data.overrun_percentage}% (+$${data.predicted_overrun_amount.toLocaleString()})</strong><br>
                    <small>Total Projected Cost: $${data.projected_final_cost.toLocaleString()}</small>
                </div>
            `;
        });
    }

    renderEquipmentHealthChart();
}

function renderEquipmentHealthChart() {
    const ctx = document.getElementById('chart-equipment-health');
    if (!ctx) return;

    if (equipChartInstance) equipChartInstance.destroy();

    equipChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Tower Crane #2', 'CAT Excavator 330', 'Concrete Pump Truck P88'],
            datasets: [
                { label: 'Equipment Health Score (%)', data: [72.0, 94.0, 88.5], backgroundColor: '#10b981' },
                { label: 'Failure Risk (%)', data: [38.0, 5.0, 12.0], backgroundColor: '#ef4444' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' }, max: 100 }
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });
}

// 6. Project Entities Registry Viewer
function initEntitiesExplorer() {
    const selector = document.getElementById('entity-selector');
    if (selector) {
        selector.addEventListener('change', () => loadEntityTable(selector.value));
        loadEntityTable(selector.value);
    }
}

async function loadEntityTable(entityType) {
    try {
        const res = await fetch(`/api/entities/${entityType}`);
        const data = await res.json();

        const head = document.getElementById('entities-table-head');
        const body = document.getElementById('entities-table-body');

        if (!data.data || data.data.length === 0) {
            head.innerHTML = `<th>Message</th>`;
            body.innerHTML = `<tr><td>No records found for ${entityType}.</td></tr>`;
            return;
        }

        const keys = Object.keys(data.data[0]);
        head.innerHTML = keys.map(k => `<th>${k.replace('_', ' ')}</th>`).join('');

        body.innerHTML = data.data.map(row => `
            <tr>
                ${keys.map(k => `<td>${row[k] !== null ? row[k] : ''}</td>`).join('')}
            </tr>
        `).join('');
    } catch (e) {
        console.error("Entity load error:", e);
    }
}

// 7. AI Risk Assistant Chat Copilot
function initCopilotDrawer() {
    const btnOpen = document.getElementById('btn-open-assistant');
    const btnClose = document.getElementById('btn-close-assistant');
    const drawer = document.getElementById('copilot-drawer');
    const btnSend = document.getElementById('btn-send-chat');
    const input = document.getElementById('copilot-input');

    if (btnOpen && drawer) btnOpen.addEventListener('click', () => drawer.classList.add('open'));
    if (btnClose && drawer) btnClose.addEventListener('click', () => drawer.classList.remove('open'));

    if (btnSend && input) {
        const handleSend = async () => {
            const text = input.value.trim();
            if (!text) return;
            appendChatBubble(text, 'user-bubble');
            input.value = '';

            try {
                const res = await fetch('/api/assistant/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: text })
                });
                const data = await res.json();
                appendChatBubble(data.response, 'bot-bubble');
            } catch (e) {
                appendChatBubble("Sorry, AI Assistant is currently re-indexing site telemetry.", 'bot-bubble');
            }
        };

        btnSend.addEventListener('click', handleSend);
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
    }
}

function appendChatBubble(msg, className) {
    const container = document.getElementById('copilot-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = `chat-bubble ${className}`;
    div.innerHTML = msg.replace(/\n/g, '<br>');
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// 8. Executive Report Generator
async function loadReport() {
    try {
        const res = await fetch('/api/reports/generate');
        const data = await res.json();

        const container = document.getElementById('report-view-container');
        if (container) {
            container.innerHTML = `
                <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 16px;">
                    <h3>${data.title}</h3>
                    <small>Generated by: Autonomous Agent Ensemble | Time: ${data.generated_at}</small>
                </div>
                <p><strong>Executive Summary:</strong> ${data.executive_summary}</p>
                <br>
                <div class="metrics-grid">
                    <div class="metric-card glassmorphism">
                        <span class="score-label">Overall Risk Score</span>
                        <div class="score-value text-warning">${data.composite_risk_score} / 100</div>
                    </div>
                    <div class="metric-card glassmorphism">
                        <span class="score-label">Active Risk Items</span>
                        <div class="score-value">${data.active_risks_count}</div>
                    </div>
                    <div class="metric-card glassmorphism">
                        <span class="score-label">Unresolved Alerts</span>
                        <div class="score-value text-danger">${data.unresolved_alerts_count}</div>
                    </div>
                </div>
                <br>
                <h4>Targeted Mitigation Recommendations:</h4>
                <ul>
                    ${data.recommendations.map(r => `<li>📌 ${r}</li>`).join('')}
                </ul>
            `;
        }
    } catch (e) {
        console.error("Report error:", e);
    }
}
