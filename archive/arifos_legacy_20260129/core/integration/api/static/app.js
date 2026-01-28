// arifOS Monitoring Dashboard (v52.5.1) - Serena-style live monitoring

const CONFIG = {
    metrics_url: '/metrics/json',
    poll_interval: 2000  // Poll every 2 seconds
};

// Floor definitions
const FLOORS = [
    { id: 'F1', name: 'Amanah', key: 'F1_amanah' },
    { id: 'F2', name: 'Truth', key: 'F2_truth' },
    { id: 'F3', name: 'Tri-Witness', key: 'F3_tri_witness' },
    { id: 'F4', name: 'Clarity', key: 'F4_clarity' },
    { id: 'F5', name: 'Peace', key: 'F5_peace' },
    { id: 'F6', name: 'Empathy', key: 'F6_empathy' },
    { id: 'F7', name: 'Humility', key: 'F7_humility' },
    { id: 'F8', name: 'Genius', key: 'F8_genius' },
    { id: 'F9', name: 'C_dark', key: 'F9_dark' },
    { id: 'F10', name: 'Ontology', key: 'F10_ontology' },
    { id: 'F11', name: 'Auth', key: 'F11_auth' },
    { id: 'F12', name: 'Injection', key: 'F12_injection' },
    { id: 'F13', name: 'Curiosity', key: 'F13_curiosity' }
];

// Tool names for display
const TOOL_NAMES = ['init_000', 'agi_genius', 'asi_act', 'apex_judge', 'vault_999'];

// Initialize dashboard
function init() {
    initFloors();
    updateDashboard();
    setInterval(updateDashboard, CONFIG.poll_interval);
}

// Initialize floor LED grid
function initFloors() {
    const grid = document.getElementById('floors-grid');
    if (!grid) return;

    grid.innerHTML = '';
    FLOORS.forEach(floor => {
        const div = document.createElement('div');
        div.className = 'floor-led';
        div.innerHTML = `
            <div class="led green" id="led-${floor.id}"></div>
            <span>${floor.id} ${floor.name}</span>
        `;
        grid.appendChild(div);
    });
}

// Main update loop
async function updateDashboard() {
    try {
        const response = await fetch(CONFIG.metrics_url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Update header
        updateHeader(data);

        // Update top metrics
        updateTopMetrics(data);

        // Update tool usage
        updateToolUsage(data.tool_usage || {});

        // Update verdict distribution
        updateVerdictDistribution(data.verdict_distribution || {});

        // Update recent executions
        updateRecentExecutions(data.recent_executions || []);

        // Update floor health
        updateFloorHealth(data.floor_health || {});

        // Update trinity scores
        updateTrinityScores(data.trinity || {});

        // Update last update time
        document.getElementById('last-update').innerText =
            `Last update: ${new Date().toLocaleTimeString()}`;

    } catch (err) {
        console.error('Dashboard update failed:', err);
        document.getElementById('status-badge').innerText = 'Disconnected';
        document.getElementById('status-badge').style.color = '#f85149';
        document.getElementById('status-badge').style.borderColor = '#f85149';
    }
}

function updateHeader(data) {
    document.getElementById('version').innerText = data.version || 'v52.5.1-SEAL';
    document.getElementById('uptime').innerText = `Uptime: ${data.uptime_hours || 0}h`;

    // Show calibration mode indicator if in calibration
    const calIndicator = document.getElementById('calibration-indicator');
    if (data.calibration_mode) {
        calIndicator.style.display = 'block';
        console.warn('Dashboard in calibration mode - synthetic data');
    } else {
        calIndicator.style.display = 'none';
    }

    const badge = document.getElementById('status-badge');
    if (data.status === 'active') {
        badge.innerText = 'Active';
        badge.style.color = '#3fb950';
        badge.style.borderColor = '#3fb950';
    } else if (data.status === 'error') {
        badge.innerText = 'Error';
        badge.style.color = '#f85149';
        badge.style.borderColor = '#f85149';
    }
}

function updateTopMetrics(data) {
    document.getElementById('total-calls').innerText = data.total_tool_calls || 0;
    document.getElementById('active-sessions').innerText = data.active_sessions || 0;
    document.getElementById('seal-rate').innerText =
        `${Math.round((data.seal_rate || 0) * 100)}%`;
    document.getElementById('avg-latency').innerText =
        `${Math.round(data.latency_ms?.avg || 0)}ms`;
}

function updateToolUsage(toolUsage) {
    const container = document.getElementById('tool-usage');
    if (!container) return;

    container.innerHTML = '';
    TOOL_NAMES.forEach(tool => {
        const count = toolUsage[tool] || 0;
        const div = document.createElement('div');
        div.className = 'tool-row';
        div.innerHTML = `
            <span class="tool-name">${tool}</span>
            <span class="tool-count">${count}</span>
        `;
        container.appendChild(div);
    });
}

function updateVerdictDistribution(verdictDist) {
    const container = document.getElementById('verdict-dist');
    if (!container) return;

    const verdicts = [
        { key: 'SEAL', css: 'seal' },
        { key: 'VOID', css: 'void' },
        { key: 'PARTIAL', css: 'partial' },
        { key: '888_HOLD', css: 'hold' }
    ];

    container.innerHTML = '';
    verdicts.forEach(v => {
        const count = verdictDist[v.key] || 0;
        const div = document.createElement('div');
        div.className = `verdict-row ${v.css}`;
        div.innerHTML = `
            <span class="verdict-name">${v.key}</span>
            <span class="verdict-count">${count}</span>
        `;
        container.appendChild(div);
    });
}

function updateRecentExecutions(executions) {
    const container = document.getElementById('recent-executions');
    if (!container) return;

    if (!executions || executions.length === 0) {
        container.innerHTML = '<div class="execution-empty">No executions yet...</div>';
        return;
    }

    container.innerHTML = '';
    executions.forEach(exec => {
        const verdictClass = getVerdictClass(exec.verdict);
        const div = document.createElement('div');
        div.className = `execution-item ${verdictClass}`;

        // Format timestamp
        const time = exec.timestamp ? formatTime(exec.timestamp) : '--';

        div.innerHTML = `
            <div class="execution-left">
                <span class="execution-tool">${exec.tool || 'unknown'}</span>
                <span class="execution-time">${time}</span>
            </div>
            <div class="execution-right">
                <span class="execution-verdict ${verdictClass}">${exec.verdict || 'UNKNOWN'}</span>
                <span class="execution-duration">${Math.round(exec.duration_ms || 0)}ms</span>
            </div>
        `;
        container.appendChild(div);
    });
}

function updateFloorHealth(floorHealth) {
    FLOORS.forEach(floor => {
        const led = document.getElementById(`led-${floor.id}`);
        if (!led) return;

        const isHealthy = floorHealth[floor.key] !== false;
        led.className = `led ${isHealthy ? 'green' : 'red'}`;
    });
}

function updateTrinityScores(data) {
    // Use live metrics - NO FALLBACKS (fail transparently)
    const tau = data.tau;  // τ: Truth accuracy
    const kappa_r = data.kappa_r;  // κᵣ: Empathy
    const psi = data.psi;  // Ψ: Vitality

    // Update with live values (will show undefined if API fails)
    document.getElementById('agi-score').innerText = tau?.toFixed(3) || '—';
    document.getElementById('asi-score').innerText = kappa_r?.toFixed(3) || '—';
    document.getElementById('apex-score').innerText = psi?.toFixed(3) || '—';

    // Log if values are missing (for debugging)
    if (tau === undefined) console.warn('τ (truth) missing from metrics');
    if (kappa_r === undefined) console.warn('κᵣ (empathy) missing from metrics');
    if (psi === undefined) console.warn('Ψ (vitality) missing from metrics');
}

// Helper: Get verdict CSS class
function getVerdictClass(verdict) {
    switch (verdict?.toUpperCase()) {
        case 'SEAL': return 'seal';
        case 'VOID': return 'void';
        case 'PARTIAL': return 'partial';
        case '888_HOLD': return 'hold';
        default: return '';
    }
}

// Helper: Format ISO timestamp to readable time
function formatTime(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString();
    } catch {
        return isoString;
    }
}

// Start on DOM ready
document.addEventListener('DOMContentLoaded', init);
