// arifOS Sovereign Dashboard - Controller (v52.0)

const CONFIG = {
    metrics_url: '/metrics/json',
    poll_interval: 3000
};

// State
let dashboardData = {
    seal_rate: 0,
    void_rate: 0,
    active_sessions: 0,
    entropy_history: []
};

// Initialize Floors
const floorNames = [
    "F1 Amanah", "F2 Truth", "F3 Stability", "F4 Empathy",
    "F5 Humility", "F6 Clarity", "F7 Care", "F8 Witnesses",
    "F9 No Faking", "F10 Reality", "F11 Authority", "F12 Security",
    "F13 Curiosity"
];

function initFloors() {
    const grid = document.getElementById('floors-grid');
    floorNames.forEach((name, i) => {
        const id = `F${i + 1}`;
        const div = document.createElement('div');
        div.className = 'floor-led';
        div.innerHTML = `
            <div class="led active-green" id="led-${id}"></div>
            <span>${name}</span>
        `;
        grid.appendChild(div);
    });
}

// Update Loop
async function updateDashboard() {
    try {
        const response = await fetch(CONFIG.metrics_url);
        const data = await response.json();

        // Update Stats
        document.getElementById('val-seal-rate').innerText = `${Math.round(data.seal_rate * 100)}%`;
        document.getElementById('val-delta-s').innerText = `${data.entropy_delta || -0.05} bits`;
        document.getElementById('equilibrium-pct').innerText = `${Math.round((1 - data.void_rate) * 100)}%`;

        // Update Trinity
        document.getElementById('score-truth').innerText = `τ: ${data.truth_score?.p50 || 0.95}`;
        document.getElementById('score-empathy').innerText = `κᵣ: ${data.empathy_score || 0.96}`;

        // Randomly flicker some floors for effect (mocking live checks)
        updateFloorsUI();

        // Append ledger log
        if (Math.random() > 0.7) {
            addLedgerMessage(`[SEAL] session_${Math.floor(Math.random() * 1000)} validated.`);
        }

    } catch (err) {
        console.error("Dashboard update failed:", err);
    }
}

function updateFloorsUI() {
    // In a live system, we'd pull actual floor failures from /metrics
    // For now, keep them mostly green
}

function addLedgerMessage(text) {
    const container = document.getElementById('ledger-messages');
    const msg = document.createElement('div');
    msg.className = 'msg';
    msg.innerText = text;
    container.prepend(msg);

    // Keep it clean
    if (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

// Startup
document.addEventListener('DOMContentLoaded', () => {
    initFloors();
    setInterval(updateDashboard, CONFIG.poll_interval);
    updateDashboard(); // Initial call

    // Set random session id for display
    document.getElementById('session-id').innerText = `SID: ${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
});
