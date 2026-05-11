/**
 * arifOS MCP App — Guest UI Bridge
 * Implements io.modelcontextprotocol/ui postMessage JSON-RPC
 */

const MCP_ORIGIN = "*"; // In production, restrict to host origin

function send(message) {
  window.parent.postMessage(message, MCP_ORIGIN);
}

function requestToolCall(name, args) {
  send({
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name, arguments: args },
    id: Math.random().toString(36).slice(2)
  });
}

function notifyReady() {
  send({
    jsonrpc: "2.0",
    method: "ui/notifications/ready",
    params: {}
  });
}

function notifyResponse(data) {
  send({
    jsonrpc: "2.0",
    method: "ui/notifications/response",
    params: data
  });
}

// ── Initialize handshake ────────────────────────────────────────────────────
window.addEventListener("message", (event) => {
  const msg = event.data;
  if (!msg || msg.jsonrpc !== "2.0") return;

  if (msg.method === "initialize") {
    console.log("[MCP App] Host initialized:", msg.params);
    document.getElementById("status").textContent = "Connected to arifOS";
    notifyReady();
    return;
  }

  if (msg.method === "ui/notifications/request-teardown") {
    console.log("[MCP App] Teardown requested");
    // Cleanup state here
    return;
  }

  if (msg.result) {
    console.log("[MCP App] Tool result:", msg.result);
    render(msg.result);
  }
});

// ── Render logic (customize per app) ────────────────────────────────────────
function render(result) {
  const el = document.getElementById("content");
  el.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
}

// ── Boot ────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("status").textContent = "Waiting for host...";
});
