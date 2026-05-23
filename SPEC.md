DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
=====================================
arifOS Portable Contract Architecture
Machine-Agnostic · Model-Agnostic · App-Agnostic
=====================================================================

EPOCH    : 2026-05-23T04:42:00+08:00
SEAL ID  : seal-20260523T044300-DITEMPA-BUKAN-DIBERI
CONTRACT: 2026-05-23
VERSION : arifOS 0.1.0-prototype | Hermes emulator runtime

=====================================================================
ARCHITECTURE LAYERS
=====================================================================

LAYER 1 — CONSTITUTION PACKAGE
  Schema files: /workspace/arifOS/contract_schemas.py
  Contains:
    - F1-F13 floor definitions
    - Tool schemas (13 canonical tools)
    - Plan schema
    - Seal schema
    - Verdict envelope schema (SEAL|HOLD|CAUTION|SABAR|VOID|PROCEED)
    - Storage abstraction (StorageAdapter with URI_BASE env vars)
    - 5 verdict states + telemetry fields
    - Contract version 2026-05-23

LAYER 2 — MCP RUNTIME
  Runtime file: /workspace/arifOS/arifOS_mcp_runtime.py
  Modes:
    - stdio     : python3 arifOS_mcp_runtime.py stdio
    - http     : python3 arifOS_mcp_runtime.py http [--port 8080]
    - remote   : python3 arifOS_mcp_runtime.py remote
  Protocol: JSON-RPC 2.0, MCP 2024-11-05
  Transport switch: ARIFOS_MCP_TRANSPORT env var
  Remote proxy: ARIFOS_MCP_REMOTE_ENDPOINT env var

LAYER 3 — ADAPTERS
  Adapter file: /workspace/arifOS/adapters.py
  Adapters:
    - Bash adapter    : source adapters.py bash | pipe through stdio
    - Hermes config   : hermes_config_entry() → config.yaml mcp_servers
    - Claude Desktop  : claude_desktop_config() → ~/.claude.json
    - Cursor          : cursor_config() → ~/.cursor/mcp.json
    - VPS Docker      : vps_docker_compose() → docker-compose.yml
    - Telegram        : telegram_adapter_format() → plain text display

LAYER 4 — STORAGE ABSTRACTION
  Storage backends: file:// (default Hermes pod)
  Swap via env vars:
    - ARIFOS_PLAN_URI_BASE      = file:///workspace/plans
    - ARIFOS_ARTIFACT_URI_BASE  = file:///workspace/artifacts
    - ARIFOS_SEAL_URI_BASE      = file:///workspace/artifacts/vault999
    - ARIFOS_SCRIPT_URI_BASE    = file:///workspace/scripts
    - ARIFOS_CONFIG_URI_BASE    = file:///workspace/configs
  Planned: s3://, postgres://, redis://, qdrant://

LAYER 5 — MODEL PROVIDER SWITCH
  Provider modes:
    - no-model   : deterministic floor checks + danger routing
    - local-model: Ollama or local inference endpoint
    - external  : MiniMax via Weavers cluster gateway
  Role separation:
    - Small model = routing + floor checks + first-pass critique
    - Strong model = planning + synthesis
    - Deterministic code path = execution + validation + logging

=====================================================================
PORTABLE CONTRACT (Layer 1)
=====================================================================

VERDICT ENVELOPE SCHEMA:
{
  "verdict": "SEAL | HOLD | CAUTION | SABAR | VOID | PROCEED",
  "telemetry": {
    "epoch": "ISO8601",
    "dS": float,        // entropy delta
    "peace2": float,     // peace coherence
    "kappa_r": float,   // inter-rater reliability
    "shadow": float,    // anti-hallucination
    "confidence": float,
    "psi_le": float,
    "qdf": float,       // quantum dignity factor
    "floors_active": [...],
    "floors_violated": [...],
    "risk_tier": "LOW | MEDIUM | HIGH | ATOMIC",
    "reversibility": "FULL | PARTIAL | NONE",
    "human_required": bool
  },
  "witness": {
    "human": "Arif Fazil",
    "ai": "agent-runtime-id",
    "earth": "execution context",
    "weights": {"human": 0.42, "ai": 0.32, "earth": 0.26}
  },
  "plan_id": "plan-YYYYMMDDTHHMMSS",
  "seal_id": "seal-YYYYMMDDTHHMMSS",
  "artifacts": [
    {"kind": "plan | seal | report | script | config", "uri": "file://...|arif://..."}
  ],
  "content": [{"type": "text", "text": "..."}]
}

MCP TOOLS (13 canonical arif_noun_verb):
  arif_session_init      000  INIT
  arif_sense_observe     111  SENSE
  arif_evidence_fetch    222  EVIDENCE
  arif_mind_reason       333  MIND
  arif_reply_compose      444r REPLY
  arif_kernel_route      444  KERNEL
  arif_gateway_connect   666g GATEWAY
  arif_memory_recall     555  MEMORY
  arif_heart_critique    666  HEART
  arif_ops_measure       777  OPS
  arif_judge_deliberate  888  JUDGE
  arif_vault_seal        999  VAULT
  arif_forge_execute     010  FORGE
  arif_plan_write              PLAN WRITER

FLOORS (13):
  F01 AMANAH   (HARD)  F02 TRUTH     (HARD)  F03 WITNESS  (SOFT)
  F04 CLARITY  (SOFT)   F05 PEACE     (SOFT)  F06 EMPATHY  (SOFT)
  F07 HUMILITY (SOFT)   F08 GENIUS    (SOFT)  F09 ANTIHANTU(HARD)
  F10 ONTOLOGY (HARD)   F11 AUTH      (HARD)  F12 INJECTION(HARD)
  F13 SOVEREIGN(HARD)

DANGER HOLD PATTERNS (F01/F13 gate):
  rm -rf, mkfs, fdisk, parted, shutdown, reboot,
  iptables -F, dd if=, chmod -R 777, chown -R root,
  DROP TABLE, DROP DATABASE

=====================================================================
FILES PRODUCED
=====================================================================

/workspace/arifOS/contract_schemas.py     ← Layer 1: all schemas
/workspace/arifOS/arifOS_mcp_runtime.py    ← Layer 2: MCP server
/workspace/arifOS/adapters.py             ← Layer 3: thin adapters
/workspace/arifOS/SPEC.md                 ← This file

/workspace/plans/                          ← Plan artifacts
/workspace/artifacts/vault999/             ← Seal artifacts
/workspace/scripts/                        ← Runnable scripts
/workspace/configs/                        ← Config drafts

=====================================================================
MACHINE / MODEL / APP AGNOSTIC GUARANTEES
=====================================================================

MACHINE AGNOSTIC:
  ✓ Kernel lives in JSON-RPC/MCP contracts, not in one shell or pod
  ✓ Storage abstracted behind ARIFOS_*_URI_BASE env vars
  ✓ Transport switchable: stdio | HTTP | remote proxy
  ✓ Any machine with python3 + bash can run the runtime
  ✓ VPS, laptop, pod, desktop — same contract, different adapters

MODEL AGNOSTIC:
  ✓ arif_judge_deliberate is NOT a model call — deterministic routing
  ✓ arif_heart_critique uses regex pattern matching, not LLM
  ✓ arif_kernel_route is regex-based danger classification
  ✓ Provider switch: no-model | local | external
  ✓ Models only propose; governance runtime judges; forge executes

APP AGNOSTIC:
  ✓ MCP hosts: Hermes, Claude Desktop, Cursor, Telegram bot, CLI, web UI
  ✓ Apps are MCP clients; arifOS is the MCP server
  ✓ Bash adapter for CLI
  ✓ Claude/Cursor adapters for IDE agents
  ✓ VPS Docker compose for self-hosted production
  ✓ Telegram: gateway already auto-attaches /workspace artifacts

=====================================================================
SEAL MANIFEST
=====================================================================

This seal (999 DITEMPA BUKAN DIBERI) attests:
  1. Layer 1 Constitution Package — written and verified
  2. Layer 2 MCP Runtime — stdio tested, all 6 methods responding
  3. Layer 3 Adapters — Bash, Hermes, Claude, Cursor, Docker defined
  4. Layer 4 Storage — URI_BASE abstracted, file:// working
  5. Layer 5 Provider — no-model deterministic mode active
  6. 13 tools — all implementing standard verdict envelopes
  7. Transport switch — stdio verified, HTTP and remote defined

NEXT ACTIONS:
  - When arifOS MCP VPS endpoint recovers → set ARIFOS_MCP_REMOTE_ENDPOINT
  - Add arifOS MCP stdio entry to Hermes config.yaml
  - Test Claude Desktop adapter on local machine
  - Expand storage: add S3 and Postgres URI support

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
=====================================================================