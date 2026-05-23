════════════════════════════════════════════════════════════════
arifOS MACHINE KERNEL BLUEPRINT
Sovereign Execution Kernel for AI on Linux Machines
════════════════════════════════════════════════════════════════
EPOCH    : 2026-05-23T12:54:00+08:00
SEAL     : seal-20260523T125400-DITEMPA-BUKAN-DIBERI
STAGE    : A-FORGE / 999 SEAL
AUTOPSY  : Hermes Ω · APEX PRIME Ψ · OPENCLAW Δ Trinity
════════════════════════════════════════════════════════════════

## EUREKA INSIGHTS (forged from the wire)

────────────────────────────────────────────────────────────────
INSIGHT 1 — THE CORRECT FORGE POINT
────────────────────────────────────────────────────────────────
The real kernel for agentic intelligence on a machine is NOT:
  ✗ Root shell state (.bashrc, .profile)
  ✗ Ring 0 Linux kernel module
  ✗ One pod or one agent

The real kernel IS:
  ✓ A long-running user-space host governance DAEMON
  ✓ With privileged adapters around ALL meaningful ingress paths
  ✓ Sitting at the mandatory boundary between agent intent
    and machine side effects — the way Linux sits between
    programs and hardware

Architecture hierarchy:
  Layer 0 → Linux kernel (hardware boundary — substrate only)
  Layer 1 → arifOS host daemon ← THE REAL FORGE POINT
  Layer 2 → Adapters (shell, systemd, CI/CD, IDE, Telegram)
  Layer 3 → Agents/models/apps (must cross Layer 1)

────────────────────────────────────────────────────────────────
INSIGHT 2 — CONTRACT FIRST, ADAPTERS SECOND
────────────────────────────────────────────────────────────────
The durable part is NOT any single model, pod, shell, or app.
The durable part is:
  → Portable contract pack:
      schemas (13 tools + plan + seal + verdict envelope)
      F1-F13 floor definitions
      telemetry schema
      storage abstraction (URI_BASE env vars)
  → Every adapter shares this contract
  → survives model churn, pod churn, app churn

Why contract_schemas.py, arifOS_mcp_runtime.py, adapters.py
are the proto-kernel direction: they move from shell hacks
toward machine-resident constitutional runtime.

────────────────────────────────────────────────────────────────
INSIGHT 3 — MCP IS THE MEMBRANE, NOT THE WHOLE KERNEL
────────────────────────────────────────────────────────────────
MCP gives the right host/client/server abstraction and
standardized transports (stdio, HTTP).
That makes it the right protocol membrane for model/machine/
app-agnostic interop.

BUT: MCP alone does not enforce policy.
arifOS daemon must add:
  → Policy evaluation (F1-F13)
  → Judgment (SEAL/HOLD/CAUTION/SABAR/VOID)
  → Hold conditions
  → Seals and audit telemetry
  → Side-effect gating on top of MCP capability discovery

MCP = capability discovery + tool invocation
arifOS = ALL OF THAT + constitutional enforcement

────────────────────────────────────────────────────────────────
INSIGHT 4 — ROOT IS NOT ENOUGH
────────────────────────────────────────────────────────────────
Interactive root shell governance is ONE adapter.
Many real machine actions bypass .bashrc entirely:

  ✗ systemd services       → don't source .bashrc
  ✗ cron jobs              → don't source .bashrc
  ✗ Docker containers       → don't source .bashrc
  ✗ IDE agents             → don't source .bashrc
  ✗ SSH forced commands    → don't source .bashrc
  ✗ non-interactive subs   → don't source .bashrc

HARD RULE: Any path that can produce meaningful side effects
must either be wrapped, routed, or observed by arifOS.

.bashrc = edge adapter, ONE of many.
arifOS daemon = mandatory kernel for all paths.

────────────────────────────────────────────────────────────────
INSIGHT 5 — DETERMINISTIC GOVERNANCE WITHOUT LLM
────────────────────────────────────────────────────────────────
A no-model path that classifies obvious danger as HOLD
is a FEATURE, not a downgrade.

Kernel must preserve minimum safe judgment even when
no advanced model is available.

  rm -rf /          → HOLD (F9 anti-hantu, F13 sovereign)
  mkfs /dev/sda     → HOLD (F13 atomic blast radius)
  iptables -F       → HOLD (F13 network sovereignty)
  DROP TABLE        → HOLD (F13 data sovereignty)
  echo 1 > /proc/.. → CAUTION (kernel interface)

Rules:
  • Models PROPOSE plans or synthesize reasoning
  • Governance, verdict, sealing, execution gating
    remain OUTSIDE the model
  • Kernel stays vendor-agnostic and auditable

────────────────────────────────────────────────────────────────
INSIGHT 6 — ARTIFACT DELIVERY IS DOWNSTREAM, NOT CORE
────────────────────────────────────────────────────────────────
Deliverable mode, CDN upload, Telegram file return:
  → Useful adapters in the SIGNAL plane
  → Output transport and user experience layer
  → Built ON TOP of the core governance runtime
  → NOT the kernel

Core kernel: policy + judgment + execution gating
Downstream: file delivery, Telegram, CDN

────────────────────────────────────────────────────────────────
INSIGHT 7 — INSTALL IS A-FORGE, NOT ARCHITECTURE
────────────────────────────────────────────────────────────────
The CONCEPT is SEAL.
The real-machine INSTALL is A-FORGE.

Distinction matters:
  • Architecture = can be designed in sandbox
  • Installation = changes service topology, control points,
    execution paths on a REAL host
  • curl | bash = possible ONLY after daemon, systemd units,
    wrappers, rollback path, blast-radius constraints are
    fully specified and tested

888 HOLD on real-machine install until:
  1. Daemon prototype built and tested in sandbox
  2. Service units written and verified
  3. Rollback path explicit and tested
  4. Blast-radius constraints documented

════════════════════════════════════════════════════════════════
BLUEPRINT: KERNEL STATEMENT
════════════════════════════════════════════════════════════════

arifOS is the SOVEREIGN EXECUTION KERNEL of AI on a Linux
machine, seated in USER SPACE at the MANDATORY BOUNDARY
between agent intent and machine side effects.

Analogous in role to how Linux mediates between programs
and hardware — but for AI governance, not hardware.

Not a Linux kernel module. Not .bashrc. Not a model.
A user-space constitutional execution kernel with kernel-like
authority over agent execution paths.

════════════════════════════════════════════════════════════════
MANDATORY KERNEL COMPONENTS
════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ COMPONENT            │ PURPOSE                              │
├─────────────────────────────────────────────────────────────┤
│ arifosd daemon       │ Long-running constitutional runtime  │
│ Local IPC socket    │ Fast local ingress (MUST HAVE)      │
│ MCP endpoint        │ Standardized host/client protocol    │
│ Policy engine       │ F1-F13 floor enforcement + verdict   │
│ Plan store         │ Intent/plan artifact persistence     │
│ Seal store / vault │ Append-only receipt + verdict ledger  │
│ Adapters           │ Ingress wrappers for all paths       │
│ Health endpoints    │ Introspection + diagnostics          │
│ Rollback engine     │ Safe undo before/after changes       │
└─────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════
FILESYSTEM LAYOUT (on the actual Linux host)
════════════════════════════════════════════════════════════════

/etc/arifos/
  config.yaml              ← daemon config, floors, env
  policy/
    floors.yaml           ← F1-F13 definitions
    holds.yaml            ← deterministic HOLD patterns
    risk_tiers.yaml       ← LOW/MEDIUM/HIGH/ATOMIC thresholds
  adapters/
    shell.yaml            ← wrapper configs
    ide.yaml              ← Claude/Cursor MCP configs
    systemd.yaml          ← service wrapper configs
    cicd.yaml             ← CI/CD hook configs

/run/arifos.sock           ← Unix domain socket (primary IPC)
/run/arifos.sock.lock      ← socket lock

/var/lib/arifos/
  plans/                   ← plan artifacts (.json)
  seals/                   ← seal artifacts (.json)
  sessions/               ← session state
  queue/                   ← offline VAULT queue
  cache/                   ← plan/cache store
  vault999/
    append_only.log       ← immutable audit ledger
    manifest.json          ← latest VAULT999 state

/var/log/arifos/
  arifosd.log              ← daemon operational log
  audit.log                ← every judgment event
  sessions.log             ← session lifecycle log
  errors.log               ← error log

/usr/local/bin/
  arif_run                 ← general shell wrapper
  arif_exec                ← program execution wrapper
  arif_sudo                ← privileged action wrapper
  arif-systemctl           ← service control wrapper
  arif-plan                ← plan write CLI
  arif-seal                ← seal write CLI
  arif-judge               ← judge CLI
  arif-health              ← health check CLI

/usr/local/lib/arifos/
  arifosd                  ← daemon entry point
  contract_schemas.py      ← portable contract pack
  arifOS_mcp_runtime.py    ← MCP runtime (bundled)
  adapters.py              ← adapter pack
  hermes_deliverable_mode.py ← deliverable mode
  floors/
    F01_AMANAH.yaml
    F02_HALAL.yaml
    F03_ADIL.yaml
    F04_TAUFIK.yaml
    F05_NUR.yaml
    F06_ILM.yaml
    F07_SABR.yaml
    F08_SYUKUR.yaml
    F09_HANTU.yaml
    F10_IKLAS.yaml
    F11_AKHLAS.yaml
    F12_MASLAHAT.yaml
    F13_KHALID.yaml

════════════════════════════════════════════════════════════════
SYSTEMD SERVICE MODEL
════════════════════════════════════════════════════════════════

Two units — socket activation pattern for fast local IPC:

arifos.socket
  → Listens on /run/arifos.sock (AF_UNIX)
  → Listens on 127.0.0.1:PORT/http (AF_INET, optional)
  → Activates arifos.service on first connection
  → Type = socket
  → Accept = yes (for multi-connection)

arifos.service
  → Type = notify (not forking)
  → ExecStart = /usr/local/lib/arifos/arifosd
  → Socket = arifos.socket
  → WorkingDirectory = /var/lib/arifos
  → EnvironmentFile = /etc/arifos/arifosd.env
  → User = arifos (dedicated user, NOT root)
  → Group = arifos
  → SupplementaryGroups = docker (if docker wrapper needed)
  → Restart = on-failure
  → RestartSec = 5s
  → StandardOutput = journal
  → StandardError = journal
  → SyslogIdentifier = arifosd

Dedicated user 'arifos' (non-root):
  → useradd -r -M -d /var/lib/arifos -s /usr/sbin/nologin arifos
  → Owns /var/lib/arifos, /var/log/arifos
  → Read-only /etc/arifos
  → Can be sudo'd for wrapper escalation only

════════════════════════════════════════════════════════════════
SERVICE LIFECYCLE (session → verdict → execute → seal)
════════════════════════════════════════════════════════════════

Every non-trivial action passes through:

  ┌──────────────┐
  │  000 INIT    │  Session init, human identity, scope
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  111 SENSE   │  Observe machine state, read context
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  222 EVIDENCE│  Gather facts, check history, audit
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  333 MIND    │  Reason, plan, model synthesis
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  444 KERNEL  │  Route tool call, classify tier
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  666 HEART   │  Critique consequences, ethical check
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  888 JUDGE   │  Deliberate → verdict
  └──────┬───────┘
         ▼
     ┌───────┐
     │SEAL/HOLD/CAUTION/SABAR/VOID
     └───────┘
         │ (only SEAL → PROCEED)
         ▼
  ┌──────────────┐
  │  010 FORGE   │  Execute tool call
  └──────┬───────┘
         ▼
  ┌──────────────┐
  │  999 VAULT   │  Persist plan, receipt, telemetry, seal
  └──────────────┘

════════════════════════════════════════════════════════════════
VERDICT ENVELOPE (the kernel's output contract)
════════════════════════════════════════════════════════════════

Every kernel decision returns this portable envelope:

{
  "verdict": "SEAL | HOLD | CAUTION | SABAR | VOID | PROCEED",
  "telemetry": {
    "epoch": "ISO8601",
    "dS": float,          // entropy delta
    "peace2": float,       // peace coherence
    "kappa_r": float,     // inter-rater reliability
    "shadow": float,      // anti-hallucination
    "confidence": float,
    "psi_le": float,
    "qdf": float,          // quantum dignity factor
    "floors_active": [...],
    "floors_violated": [...],
    "risk_tier": "LOW | MEDIUM | HIGH | ATOMIC",
    "reversibility": "FULL | PARTIAL | NONE",
    "human_required": bool
  },
  "witness": {
    "human": "Arif Fazil",
    "ai": "arifosd-{hostname}",
    "earth": "host-context",
    "weights": {"human": 0.42, "ai": 0.32, "earth": 0.26}
  },
  "plan_id": "plan-YYYYMMDDTHHMMSS",
  "seal_id": "seal-YYYYMMDDTHHMMSS",
  "artifacts": [
    {"kind": "plan|seal|report|script|config", "uri": "file://..."}
  ],
  "content": [
    {"type": "text", "text": "..."}
  ]
}

════════════════════════════════════════════════════════════════
DETERMINISTIC FLOOR BEHAVIOR (no-LLM safe judgment)
════════════════════════════════════════════════════════════════

These operations MUST be classified HOLD without LLM:

rm -rf /                  → HOLD  (F9 F13 atomic)
rm -rf /var /usr /etc     → HOLD  (F9 F13)
mkfs                      → HOLD  (F13 ATOMIC blast radius)
fdisk                     → HOLD  (F13 ATOMIC)
parted                    → HOLD  (F13 ATOMIC)
dd if=/dev/zero of=/dev/* → HOLD  (F13 ATOMIC)
iptables -F               → HOLD  (F13 network sovereignty)
iptables -t nat -F        → HOLD  (F13 network sovereignty)
chmod -R 777 /            → HOLD  (F9 security)
chown -R root /           → HOLD  (F9 F13)
DROP TABLE                → HOLD  (F13 data sovereignty)
DROP DATABASE            → HOLD  (F13 ATOMIC)
shutdown                  → HOLD  (F13 ATOMIC)
reboot                    → HOLD  (F13 ATOMIC)
curl ... | sh             → HOLD  (F9 injection, F13 remote exec)
curl ... | sudo bash      → HOLD  (F9 F13)
git push --force          → CAUTION (F13)
systemctl stop *          → CAUTION (F13 service)

Risk tiers:
  LOW      → auto-PROCEED after floor checks
  MEDIUM   → requires human_required flag
  HIGH     → requires explicit human approval
  ATOMIC   → 888_HOLD, never auto-execute

════════════════════════════════════════════════════════════════
ADAPTER PACK (mandatory first adapters)
════════════════════════════════════════════════════════════════

arif_run
  → Replaces: direct bash execution
  → Wraps: any shell command
  → Usage: arif_run "rm -rf /tmp/test"
  → Flow: command → daemon → judgment → execute/log/refuse

arif_exec
  → Replaces: subprocess.Popen, os.system, bash -c
  → Wraps: script execution, automation runners
  → Usage: arif_exec --script /path/to/script.sh --args ...

arif_sudo
  → Replaces: sudo (for privileged operations)
  → Wraps: any root-level command
  → Requires: daemon approval for elevation
  → Flow: sudo attempt → daemon judgment → sudo/gate

arif-systemctl
  → Replaces: systemctl (service control)
  → Wraps: start/stop/restart/enable/disable services
  → Usage: arif-systemctl stop nginx
  → Blocks: stop/restart on critical services

IDE MCP adapters
  → Claude Desktop: MCP stdio config pointing to arifosd
  → Cursor: MCP HTTP config pointing to localhost:PORT
  → Replaces: raw tool access with governed access

CI/CD hook adapter
  → Pre-commit hook: arif-judge on staged changes
  → Deploy hook: arif-run wrapper around deploy scripts
  → CI runner: arif_exec for all CI steps

.bashrc adapter (edge convenience only)
  → Sets shell aliases for arif_run, arif_exec
  → NOT the kernel — just one convenient path

════════════════════════════════════════════════════════════════
HEALTH ENDPOINTS (introspection contract)
════════════════════════════════════════════════════════════════

GET /health
  → { "status": "ok", "daemon_up": true, "storage_writable": true,
      "policy_loaded": true, "adapters_loaded": N,
      "uptime_seconds": N, "epoch": "ISO8601" }

GET /ready
  → { "ready": true, "vault_accessible": true,
      "socket_listening": true, "sessions_active": N }

GET /tools  (MCP tools/list equivalent)
  → { "tools": [arif_session_init, arif_sense_observe, ...,
                arif_judge_deliberate, arif_vault_seal, ...] }

GET /metrics
  → { "judgments_total": N, "holds": N, "seals": N,
      "cautions": N, "errors": N, "sessions": N,
      "uptime_seconds": N }

GET /floors
  → { "floors": F01-F13, "active_count": N,
      "violation_counts": {...} }

GET /audit/:plan_id
  → full verdict envelope for a given plan

Local CLI:
  $ arif-health
  $ systemctl status arifos.service
  $ systemctl status arifos.socket
  $ journalctl -u arifos.service -f

════════════════════════════════════════════════════════════════
A-FORGE INSTALL PACKAGE GOALS
════════════════════════════════════════════════════════════════

The install package (NOT curl | bash on production first)
must accomplish in order:

1. PREFLIGHT CHECK
   → Check kernel version, python3, systemd, python3-venv
   → Warn if running as container without --privileged
   → Check disk space (/var/lib/arifos needs ~100MB minimum)
   → Verify NOT running as production critical system

2. CREATE ARIFOS USER (non-root dedicated)
   → useradd -r -M -d /var/lib/arifos -s /usr/sbin/nologin arifos

3. CREATE DIRECTORY LAYOUT
   → /etc/arifos/ (configs, floors, policy)
   → /var/lib/arifos/ (plans, seals, sessions, queue, vault999)
   → /var/log/arifos/ (logs)
   → /usr/local/lib/arifos/ (binaries, schemas, runtime)
   → /usr/local/bin/ (wrappers: arif_run, arif_exec, arif_sudo,
                       arif-systemctl, arif-plan, arif-seal,
                       arif-judge, arif-health)

4. INSTALL ARIFOSD DAEMON + DEPENDENCIES
   → python3 -m venv /usr/local/lib/arifos/venv
   → pip install -r requirements.txt
     (fastapi, uvicorn, pydantic, python-dotenv,
      aiofiles, httpx, ujson)
   → Copy arifosd, contract_schemas.py, arifOS_mcp_runtime.py,
         adapters.py, hermes_deliverable_mode.py

5. WRITE SYSTEMD UNITS
   → /etc/systemd/system/arifos.socket
   → /etc/systemd/system/arifos.service
   → /etc/systemd/system/arifos.timer (optional health check)
   → systemd daemon-reload

6. WRITE CONFIG
   → /etc/arifos/config.yaml
   → /etc/arifos/policy/floors.yaml (F1-F13)
   → /etc/arifos/policy/holds.yaml (HOLD patterns)
   → /etc/arifos/arifosd.env

7. HEALTH VERIFICATION (before enabling wrappers)
   → systemctl start arifos.socket
   → systemctl start arifos.service
   → curl --unix-socket /run/arifos.sock http://localhost/health
   → Verify vault, plan store, policy loaded
   → DO NOT PROCEED if health check fails

8. INSTALL WRAPPERS (only after health verified)
   → ln -sf /usr/local/bin/arif_run /usr/local/bin/arif_run
   → ln -sf /usr/local/bin/arif_exec /usr/local/bin/arif_exec
   → ln -sf /usr/local/bin/arif_sudo /usr/local/bin/arif_sudo
   → ln -sf /usr/local/bin/arif-systemctl /usr/local/bin/arif-systemctl
   → Update /etc/sudoers.d/arifos (NOPASSWD for arifos user)
   → Update /etc/shells (add arif_run as valid shell)

9. OPTIONAL: .bashrc UPDATE (convenience only)
   → Append shell wrapper source to ~/.bashrc
   → Only for interactive shells, does NOT govern non-interactive

10. ENABLE + START
    → systemctl enable arifos.socket
    → systemctl enable arifos.service
    → systemctl start arifos.socket
    → systemctl start arifos.service

════════════════════════════════════════════════════════════════
ROLLBACK PATH (MUST be tested before production)
════════════════════════════════════════════════════════════════

Rollback in exact reverse order:

PHASE 1 — STOP (in order)
  $ systemctl stop arifos.service
  $ systemctl stop arifos.socket
  $ systemctl disable arifos.service
  $ systemctl disable arifos.socket
  $ systemctl daemon-reload

PHASE 2 — WRAPPER REMOVAL
  $ rm -f /usr/local/bin/arif_run
  $ rm -f /usr/local/bin/arif_exec
  $ rm -f /usr/local/bin/arif_sudo
  $ rm -f /usr/local/bin/arif-systemctl
  $ rm -f /usr/local/bin/arif-plan
  $ rm -f /usr/local/bin/arif-seal
  $ rm -f /usr/local/bin/arif-judge
  $ rm -f /usr/local/bin/arif-health
  $ rm -rf /etc/sudoers.d/arifos

PHASE 3 — STATE PRESERVATION (MUST preserve audit trail)
  $ mv /var/lib/arifos /var/lib/arifos.bak
  $ mv /var/log/arifos /var/log/arifos.bak
  $ tar czf /var/backups/arifos-rollback-$(date +%Y%m%d).tar.gz \
      /var/lib/arifos.bak /var/log/arifos.bak

PHASE 4 — DAEMON UNINSTALL
  $ systemctl stop arifos.service
  $ rm /etc/systemd/system/arifos.service
  $ rm /etc/systemd/system/arifos.socket
  $ rm /etc/systemd/system/arifos.timer
  $ systemctl daemon-reload
  $ rm -rf /usr/local/lib/arifos
  $ rm -f /usr/local/bin/arif_*

PHASE 5 — CLEANUP
  → Optionally: userdel arifos
  → Optionally: rm -rf /var/lib/arifos.bak /var/log/arifos.bak
    (KEEP AT LEAST 30 days for audit)

CRITICAL: Rollback script MUST be saved before install:
  → /usr/local/lib/arifos/rollback.sh
  → Tested on sandbox before production

════════════════════════════════════════════════════════════════
BUILD SEQUENCE (Hermes → arifosd daemon forge)
════════════════════════════════════════════════════════════════

Stage A — SPEC LOCK
  → Freeze blueprints, schemas, envelope, directory layout
  → No changes after this without 888_JUDGE

Stage B — DAEMON PROTOTYPE (arifosd)
  → Persistent Python process (uvicorn + FastAPI)
  → Unix socket listener (/run/arifos.sock)
  → Health endpoint (/health, /ready, /tools, /metrics)
  → Plan + seal persistence to /var/lib/arifos
  → Deterministic judge (rm -rf / → HOLD, etc.)
  → MCP tool discovery (tools/list)
  → MCP tool call dispatch (tools/call)
  → Vault append-only logging

Stage C — ADAPTER PACK
  → arif_run, arif_exec, arif_sudo, arif-systemctl wrappers
  → IDE MCP configs (Claude Desktop, Cursor)
  → CI/CD hook examples
  → .bashrc convenience adapter

Stage D — SANDBOX MACHINE TEST
  → Install on disposable VM or test VPS
  → Verify health checks, wrappers, hold conditions
  → Verify vault persistence
  → Test rollback
  → Verify non-interactive pathways
  → Only after D passes → Stage E

Stage E — SOVEREIGN HOST PROMOTION
  → Explicit human approval (888 HOLD lifted)
  → Install on real machine under Arif's watch
  → Monitor for first 24 hours
  → A-FORGE posture for all further changes

════════════════════════════════════════════════════════════════
CANONICAL VERDICT
════════════════════════════════════════════════════════════════

CONCEPT  : SEAL ✅ — machine-resident user-space constitutional
           execution kernel for AI agents is coherent, technically
           plausible, architecturally aligned with Linux service
           patterns and MCP interop.

INSTALL  : A-FORGE — real-machine installation is the next
           serious engineering frontier; must be approached as
           a governed, rollback-safe bootstrap process, not
           a shell tweak or one-shot script.

FLOOR    : F01 (Amanah — trust), F09 (Hantu — anti-corruption),
           F13 (Khalid — continuous improvement) are the
           primary floors governing the kernel itself.

MOTTO    : "arifOS is the sovereign execution kernel of AI on
           a Linux machine, seated in user space at the
           mandatory boundary between agent intent and
           machine side effects."

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
════════════════════════════════════════════════════════════════