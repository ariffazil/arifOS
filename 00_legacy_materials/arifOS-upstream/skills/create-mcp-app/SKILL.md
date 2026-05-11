# Skill: create-mcp-app

Forge a new MCP App (Guest UI) from spec, build it, deploy it to the VPS, and wire the `ui/resourceUri` return into an arifOS MCP tool.

## When to Use

- Agent is asked to create an interactive UI for an arifOS tool
- Need a dashboard, form, chart, or widget that renders inside Claude/WebMCP
- Building a ChatGPT Apps SDK compatible guest UI

## Prerequisites

- VPS has Node 22 + Bun 1.3+ (verified: `bun --version`)
- `/srv/mcp/apps/` exists and is served by Nginx on `:8081`
- `/opt/agent-builds/` exists for sandboxed builds

## Protocol Reference

MCP Apps use the `io.modelcontextprotocol/ui` extension.

Guest UI App lifecycle:
1. Host (Claude) loads `ui://<appname>/index.html` in iframe
2. Guest UI sends `initialize` JSON-RPC over postMessage
3. Host responds with capabilities
4. Guest UI requests tool results via `tools/call`
5. Host renders UI; user interacts; Guest sends `ui/notifications/response`
6. On close, Host sends `ui/notifications/request-teardown`

## Forge Chain (Deterministic)

### Step 1 — Scaffold

```bash
APP_NAME="<app_name>"
BUILD_DIR="/opt/agent-builds/${APP_NAME}"
DEPLOY_DIR="/srv/mcp/apps/${APP_NAME}/dist"

mkdir -p "${BUILD_DIR}"
cp -r "${SKILL_ROOT}/template/"* "${BUILD_DIR}/"
```

Customize `index.html` and `app.js` per spec.

### Step 2 — Build

```bash
cd "${BUILD_DIR}"
bun install || npm install
bun build --outdir=dist ./app.js || npm run build
```

### Step 3 — Deploy

```bash
mkdir -p "${DEPLOY_DIR}"
cp -r "${BUILD_DIR}/dist/"* "${DEPLOY_DIR}/"
```

### Step 4 — Wire Tool

Add or patch an arifOS MCP tool to return:

```python
return {
    "content": [{"type": "text", "text": "Launching UI..."}],
    "ui": {
        "resourceUri": f"ui://{APP_NAME}/index.html"
    }
}
```

The Nginx mapping serves:
- `ui://hello-mcp/index.html` → `http://localhost:8081/mcp-apps/hello-mcp/dist/index.html`

## Template Structure

```
template/
├── index.html      # Guest UI entry point (iframe content)
├── app.js          # MCP postMessage bridge + UI logic
├── style.css       # Tailwind or plain CSS
└── package.json    # Dependencies: esbuild, zod
```

## Validation Checklist

- [ ] `bun build` exits 0
- [ ] `dist/index.html` exists
- [ ] `dist/` copied to `/srv/mcp/apps/<appname>/dist/`
- [ ] Tool returns `ui/resourceUri` matching `ui://<appname>/index.html`
- [ ] Nginx serves the file at `http://localhost:8081/mcp-apps/<appname>/dist/index.html`
- [ ] postMessage JSON-RPC handshake works in browser devtools

## Safety

- Build only in `/opt/agent-builds/` — never in `/srv/mcp/apps/`
- Verify HTML has no external scripts (CSP compliance)
- Run `arifos_judge` with `mode="ui_safety"` before deploying

DITEMPA BUKAN DIBERI — Forged, Not Given
