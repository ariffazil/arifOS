"""
arifOS Adapter Pack — Layer 3: Thin Adapters
============================================
Machine-agnostic adapters for Bash, Hermes config, Claude Desktop, Cursor, VPS.

Usage:
  Bash      → source /workspace/arifOS/adapters/bash_adapter.sh
  Hermes    → add mcp_servers entry in config.yaml
  Claude    → add to ~/.claude.json or CLAUDE_DESKTOP_MCP_URLS
  Cursor    → add to ~/.cursor/mcp.json
  VPS local → docker compose + ARIFOS_TRANSPORT=http ARIFOS_MCP_HTTP_PORT=8080
"""

import json, os, sys
from pathlib import Path

ARIFOS_VERSION   = "0.1.0-prototype"
CONTRACT_VERSION = "2026-05-23"
ARIFOS_DIR       = Path("/workspace/arifOS")

# ── 1. Hermes MCP config entry ──────────────────────────────────────────────
def hermes_config_entry(transport: str = "stdio") -> dict:
    """Returns the mcp_servers entry to add to ~/.hermes/config.yaml."""
    if transport == "stdio":
        return {
            "arifos": {
                "command": "python3",
                "args": [str(ARIFOS_DIR / "arifOS_mcp_runtime.py"), "stdio"],
                "env": {
                    "ARIFOS_PLAN_URI_BASE":     "file:///workspace/plans",
                    "ARIFOS_ARTIFACT_URI_BASE": "file:///workspace/artifacts",
                    "ARIFOS_SEAL_URI_BASE":     "file:///workspace/artifacts/vault999",
                    "ARIFOS_SCRIPT_URI_BASE":   "file:///workspace/scripts",
                    "ARIFOS_CONFIG_URI_BASE":   "file:///workspace/configs",
                }
            }
        }
    elif transport == "http":
        return {
            "arifos_http": {
                "url": os.environ.get(
                    "ARIFOS_MCP_HTTP_URL",
                    "http://localhost:8080/mcp/message"
                ),
                "headers": {}
            }
        }

# ── 2. Claude Desktop MCP config ────────────────────────────────────────────
def claude_desktop_config(transport: str = "stdio") -> dict:
    """Returns Claude Desktop mcpServers config for ~/.claude.json."""
    if transport == "stdio":
        return {
            "mcpServers": {
                "arifOS": {
                    "command": "python3",
                    "args": [str(ARIFOS_DIR / "arifOS_mcp_runtime.py"), "stdio"],
                    "env": {
                        "ARIFOS_PLAN_URI_BASE":     "file:///home/arif/arifOS/plans",
                        "ARIFOS_ARTIFACT_URI_BASE": "file:///home/arif/arifOS/artifacts",
                        "ARIFOS_SEAL_URI_BASE":     "file:///home/arif/arifOS/artifacts/vault999",
                    }
                }
            }
        }
    elif transport == "http":
        return {
            "mcpServers": {
                "arifOS": {
                    "url": os.environ.get(
                        "ARIFOS_MCP_HTTP_URL",
                        "http://localhost:8080/mcp/message"
                    )
                }
            }
        }

# ── 3. Cursor MCP config ───────────────────────────────────────────────────────
def cursor_config(transport: str = "stdio") -> dict:
    """Returns Cursor mcp.json config."""
    return claude_desktop_config(transport)

# ── 4. VPS Docker Compose overlay ────────────────────────────────────────────
def vps_docker_compose() -> str:
    """Returns a docker-compose snippet for VPS deployment."""
    return """
  arifos-mcp:
    image: arifos/mcp-runtime:0.1
    container_name: arifos-mcp
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - ARIFOS_MCP_TRANSPORT=http
      - ARIFOS_MCP_HTTP_PORT=8080
      - ARIFOS_PLAN_URI_BASE=file:///app/plans
      - ARIFOS_ARTIFACT_URI_BASE=file:///app/artifacts
      - ARIFOS_SEAL_URI_BASE=file:///app/artifacts/vault999
      - ARIFOS_MCP_REMOTE_ENDPOINT=https://mcp.arif-fazil.com/mcp
    volumes:
      - arifos-plans:/app/plans
      - arifos-artifacts:/app/artifacts
    volumes:
      arifos-plans:
      arifos-artifacts:
"""

# ── 5. Bash adapter script ───────────────────────────────────────────────────
BASH_ADAPTER = '''#!/usr/bin/env bash
# arifOS Bash Adapter — source this in your shell to get arifOS functions
# over any machine with bash + python3.
#
# Usage: source /workspace/arifOS/adapters/bash_adapter.sh
# Then:  arif <intent>          — judge + plan
#        arif run <cmd>          — run after 888 gate
#        arif seal <json>        — write seal
#        arif list               — list plans + seals

ARIFOS_PYTHON="${ARIFOS_PYTHON:-python3}"
ARIFOS_RUNTIME="${ARIFOS_RUNTIME:-/workspace/arifOS/arifOS_mcp_runtime.py}"
ARIFOS_PLAN_URI="${ARIFOS_PLAN_URI_BASE:-file:///workspace/plans}"
ARIFOS_SEAL_URI="${ARIFOS_SEAL_URI_BASE:-file:///workspace/artifacts/vault999}"

arif() {
  case "$1" in
    judge)
      echo "888 JUDGMENT: $2"
      echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"arif_judge_deliberate","arguments":{"intent":"'"$2"'"}}}' \
        | $ARIFOS_PYTHON "$ARIFOS_RUNTIME" stdio 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
result=json.loads(d['result']['content'][0]['text'])
print('VERDICT:', result.get('verdict','?'))
print('REASON:', result.get('reason',''))
print('PLAN_ID:', result.get('plan_id','?'))
if result.get('artifacts'):
    for a in result['artifacts']:
        print('ARTIFACT:', a['uri'])
" 2>/dev/null || echo "arifOS runtime not reachable"
      ;;
    seal)
      echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"arif_vault_seal","arguments":{"data":'"$2"'}}}' \
        | $ARIFOS_PYTHON "$ARIFOS_RUNTIME" stdio 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
result=json.loads(d['result']['content'][0]['text'])
print('SEAL_ID:', result.get('seal_id','?'))
print('SEAL_URI:', result.get('artifacts',[{}])[0].get('uri','?'))
" 2>/dev/null || echo "arifOS runtime not reachable"
      ;;
    plan)
      echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"arif_plan_write","arguments":{"intent":"'"$2"'"}}}' \
        | $ARIFOS_PYTHON "$ARIFOS_RUNTIME" stdio 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
result=json.loads(d['result']['content'][0]['text'])
print('PLAN_ID:', result.get('plan_id','?'))
for a in result.get('artifacts',[]):
    print('URI:', a['uri'])
" 2>/dev/null || echo "arifOS runtime not reachable"
      ;;
    list)
      echo "=== Plans ==="
      ls -t /workspace/plans/*.json 2>/dev/null | head -5 || echo "(none)"
      echo "=== Vault999 Seals ==="
      ls -t /workspace/artifacts/vault999/*.json 2>/dev/null | head -5 || echo "(none)"
      ;;
    init)
      echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"arif_session_init","arguments":{"intent":"'"${*:2}"'"}}}' \
        | $ARIFOS_PYTHON "$ARIFOS_RUNTIME" stdio 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
result=json.loads(d['result']['content'][0]['text'])
print('VERDICT:', result.get('verdict','?'))
print('STAGE:', result.get('stage','?'))
" 2>/dev/null || echo "arifOS runtime not reachable"
      ;;
    help|*)
      cat <<'EOF'
arifOS Bash Adapter v0.1
Usage: source bash_adapter.sh && arif <command> [args]
Commands:
  arif judge <intent>    — 888 judgment on intent
  arif seal <json>      — write vault seal (json string or file reference)
  arif plan <intent>    — write structured plan
  arif init <intent>    — 000 session init
  arif list             — list recent plans + seals
  arif help             — this help
Requires: python3, /workspace/arifOS/arifOS_mcp_runtime.py
EOF
      ;;
  esac
}
'''

# ── 6. Telegram adapter stub ──────────────────────────────────────────────────
# Telegram is the Hermes gateway — it already delivers artifacts natively.
# This adapter just formats the verdict envelope for Telegram display.
def telegram_adapter_format(envelope: dict) -> str:
    """Format arifOS verdict envelope for Telegram plain-text display."""
    verdict = envelope.get("verdict", "?")
    telemetry = envelope.get("telemetry", {})
    artifact_list = envelope.get("artifacts", [])

    lines = [
        f"[arifOS] {verdict}",
        f"Stage: {envelope.get('stage', '?')}",
        f"Tool: {envelope.get('tool', '?')}",
    ]

    if envelope.get("plan_id"):
        lines.append(f"Plan: {envelope['plan_id']}")
    if envelope.get("seal_id"):
        lines.append(f"Seal: {envelope['seal_id']}")

    if telemetry:
        risk = telemetry.get("risk_tier", "-")
        conf = telemetry.get("confidence", 0)
        lines.append(f"Risk: {risk} | Confidence: {conf:.0%}")

    if artifact_list:
        for a in artifact_list:
            lines.append(f"  → {a['uri']}")

    return "\n".join(lines)


# ── 7. Hermes config writer ──────────────────────────────────────────────────
def patch_hermes_config(mcp_entry: dict, config_path: str = os.path.expanduser("~/.hermes/config.yaml")) -> str:
    """Patch Hermes config.yaml to add an MCP server entry."""
    import yaml
    try:
        import yaml
    except ImportError:
        print("ERROR: yaml module not available, manual patch required")
        return None

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    if "mcp_servers" not in cfg:
        cfg["mcp_servers"] = {}
    cfg["mcp_servers"].update(mcp_entry)

    new_path = config_path + ".new"
    with open(new_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

    return new_path


# ── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd == "hermes-stdio":
        entry = hermes_config_entry("stdio")
        print(json.dumps(entry, indent=2))
        print("\nAdd this to ~/.hermes/config.yaml → mcp_servers:", file=sys.stderr)

    elif cmd == "hermes-http":
        entry = hermes_config_entry("http")
        print(json.dumps(entry, indent=2))

    elif cmd == "claude":
        print(json.dumps(claude_desktop_config("stdio"), indent=2))

    elif cmd == "cursor":
        print(json.dumps(cursor_config("stdio"), indent=2))

    elif cmd == "docker":
        print(vps_docker_compose())

    elif cmd == "bash":
        print(BASH_ADAPTER)

    elif cmd == "all":
        for c in ["hermes-stdio", "claude", "cursor", "docker"]:
            print(f"\n{'='*40}")
            print(f"# {c}")
            print('='*40)
            import subprocess
            subprocess.run([sys.argv[0], c])
    else:
        print("Usage: python3 adapters.py [hermes-stdio|hermes-http|claude|cursor|docker|bash|all]")