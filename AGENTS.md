<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-30
valid_from: 2026-06-27
valid_until: 2026-07-30
confidence: high
scope: /root/arifOS
epistemic_status: SOURCE_OF_TRUTH
refresh_history:
  - 2026-06-27 23:25 UTC (FORGE KERNEL HARDENING — 7 patches, C-1/C-2 bypasses closed, H-1/H-3/H-4/M-1/M-3)
  - 2026-06-27 18:30 UTC (FORGE RSI — SOT cleanup, tightened header narrative)
  - 2026-06-27 18:08 UTC (999_SEAL — MCP Gate v0 deployed + schema adapter + epistemic extension)
-->

# AGENTS.md — arifOS | arifOS Federation

> **MANDATORY BOOT SEQUENCE**
> 1. Read `/root/AGENTS.md` (Global Federation Rules & Identity)
> 2. Read `/root/CONTEXT.md` (Live Machine State & Ports)
> 3. Read this file (Repo-Specific Build/Test/Run rules)

> **Constitutional Separation (Substrate / Constitution / Cognition):**
- **Substrate (Δ)** carries and changes state (A-FORGE :7071/7072 executor, transport, ports).
- **Constitution (Ω)** bounds and authorizes action (arifOS :8088 judge, seal, lease, policy).
- **Cognition (Ψ)** interprets and reduces uncertainty (AAA :3001 cockpit, A2A, reasoning).
Each layer has a bounded function. No layer may impersonate another: never let Ψ execute, never let Δ judge, never let Ω hallucinate. All high-risk execution requires lease + prior arifOS judgment path. See `docs/philosophy/THREE_LAYER_ONTOLOGY.md`.
>
> **Load-bearing pair:** One Skill (Knowing What NOT To Do / restraint) + One Tool (Verdict Loop With Memory).
>
> **AGI/ASI tiers:** runtime/action_bus.py enforces AGI vs ASI tiers. BRAIN owns skill + firewall. HANDS owns substrate. ASI_TIER never default.
> Contract: `docs/BRAIN_HANDS_MCP_MAPPING.md`. Receipt: `forge_work/AGI-ASI-ONE-SKILL-ONE-TOOL-FORGE-2026-06-24.md`.

## Allowed Actions

- Read, explore, organize, code, test, refactor
- Propose changes, create plans, draft documentation
- Work within the arifOS repo boundary
- Run `docker compose config`, health checks, diagnostics
- Update `memory/YYYY-MM-DD.md`, `CONTEXT.md`, `MEMORY.md`

## Forbidden Actions

- Issue SEAL / SABAR / VOID without human approval (F13 SOVEREIGN)
- Modify constitutional floors F1-F13 without explicit approval
- Force push, reset hard, overwrite unknown local changes
- Drop databases or delete data directories
- Mutate archived/read-only repos
- Perform broad formatting churn

## Verification Commands

```bash
python -m pytest tests/ -q --tb=short
ruff check .
ruff format .
make health
make sot-check
```

## Escalation Rules

- **888_HOLD:** Irreversible actions, git mutations, secret exposure, cross-repo architecture changes, production deployment without verified build + test pass
- **F13 SOVEREIGN (Arif):** Constitutional floor changes, new repo creation, external communications, budget/capital allocation

## Repo-Specific Notes

- Canonical MCP runtime lives in `arifosmcp/`
- Deepest constitutional enforcement lives in `core/`
- `arifosmcp/AGENTS.md` contains MCP-tool-specific guidance

---

## 🧠 CI ARCHITECTURE — Dual-Lane Agentic CI (FORGED 2026-07-01)

> **DITEMPA BUKAN DIBERI** — CI is forged, not given.
> **Architecture receipt:** `forge_work/AGENTIC-CI-FORGE-2026-07-01.md`

Every push to `main` triggers **two lanes**:

| Lane | Name | What It Does | Verdict |
|------|------|-------------|---------|
| **Lane 1** | Standard CI | Lint (Ruff) → Type check (MyPy) → Test (Pytest) → Build check | Pass/Fail |
| **Lane 2** | BIJAKSANA (Agentic CI) | ΔS (entropy) → Φ (clarity) → Ψ (truth/manifest) → Ω (governance) | SEAL_READY / SABAR / HOLD |

**The Report:** Both lanes feed into an `Agentic CI Report` — a structured JSON artifact posted as a GitHub Check Run with label `Agentic CI`. Federation cron picks up Check Run → `arif_judge` → AAA register → VAULT999 seal.

**Workflow file:** `.github/workflows/agentic-ci.yml`

**The Loop:**
```
git push → Lane 1 (Standard) + Lane 2 (BIJAKSANA)
       → Agentic CI Report (JSON + Check Run)
       → Federation cron → arif_judge → AAA → VAULT999
```

**Cross-organ:** This architecture is deployed identically across all 6 federation organs (arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL). Each organ's `AGENTS.md` carries this section. The workflow adapts to Python (pytest/ruff/mypy) or Node (npm test/build/lint).

---

## 🛡️ STEEL SECURITY LAYER

Four scanners (Trivy, Semgrep, Ruff, Gitleaks) run on every `make forge` / `make sot-check`. **Non-blocking** — no pre-commit hooks, no git blocks. If CRITICAL/HIGH findings detected, `888_HOLD` event fires to NATS. Agents stay free; the watch is quiet.

**Rules:** Never add blocking hooks. Never skip the audit. Treat 888_HOLD as real flags.

---

## 🪞 SELF-AUDIT & HARDENING

Canonical self-audit prompt: [`SELF_AUDIT_PROMPT.md`](./SELF_AUDIT_PROMPT.md). Enforces Reflexion Loop before ANY kernel mutation.

### Zen Circuit Alignment (2026-06-28)

Two loops, one constitution. Both use the same circuits — diverge only at the middle:

```
GOVERNANCE (kernel hardening):  000→111→333→555→777→888→999
CODING/FORGE (agent execution):  000→111→333→666→888→010→999
```

| Circuit | Governance Role | Coding/Forge Role | arifOS Tool |
|---------|----------------|-------------------|-------------|
| **000** | Clarify Task | Orient + Session + Preflight | `arif_init` |
| **111** | Gather Evidence | Observe + Label Truth | `arif_observe` |
| **333** | Draft Change | Plan + DAG + Humility (0.90) | `arif_think` |
| **555/666** | Self-Critique (555) | Consequence Critique (666) | `arif_think` (mode: critique) |
| **777/010** | Compare & Decide (777) | Execute with Warrant (010) | `arif_act` |
| **888** | Audit Trail | Constitutional Verdict | `arif_judge` |
| **999** | Self-Improvement | Seal + Cleanup + Health | `arif_seal` |

For OBSERVE/READ tasks, skip 333–777 but complete 000, 111, 888.
For agent-side coding, use OpenCode 7 Zen skills: `000-init-intent-classify` through `999-vault-seal-immutable`.

---

## 🌿 M-LAYER — Human-Facing Delivery Governance (FORGED 2026-06-24)

> **Origin:** Extracted from azwaOS pattern — Hermes agent's conversational
> discipline when serving Arif's sister Naazira "Azwa" Fazil (UKM student).
> Pattern observed across many rounds; six principles consistently distinguished
> good from bad responses.

arifOS constitutional floors (F1-L13) govern **tool calls and agent actions**.
The **M-Layer (M1-M6)** governs **delivery register to humans** — tone,
framing, capacity-awareness, repair-readiness, time-respect, and honesty-about-self.

| Principle | Floor | What it enforces |
| :--- | :--- | :--- |
| **M1** | Dignity-first | Recipient's maruah preserved (no condescension markers) |
| **M2** | Capacity-aware | Output matches recipient's current cognitive load |
| **M3** | Pedestrian-first | Plain register default; jargon only when topic justifies |
| **M4** | Repair-ready | Problem statements always paired with concrete next step |
| **M5** | Time-respect | Don't add pressure when recipient is already pressured |
| **M6** | Honesty-about-self | No false inner-state claims (L10 ONTOLOGY + F9 ANTIHANTU) |

### Orthogonality to F1-L13 (DO NOT BREAK)

- M-Layer is **ADVISORY OVERLAY**. It cannot override F1-L13 verdicts.
- M-Layer is **POST-OUTPUT**. Runs after text is generated, before send.
- M-Layer does **NOT** modify F1-L13 thresholds or evaluation logic.
- `DeliveryVerdict` (M_CLEAN / M_ADJUST / M_REPAIR / M_HOLD) is **disjoint**
  from `Verdict` (SEAL / HOLD / SABAR / VOID / PARTIAL).
- Only F1-L13 can block output. M-Layer can advise rephrasing, but cannot
  auto-suppress — that's L13 SOVEREIGN territory.

### File Locations

| File | Purpose |
| :--- | :--- |
| `arifosmcp/core/maruah_layer.py` | M1-M6 evaluator (~26KB) |
| `tests/test_maruah_layer.py` | 29 tests covering all principles + orthogonality |
| `arifosmcp/core/human_substrate.py` | (separate) Arif-specific constitutional substrate |

### When to Invoke M-Layer

```python
from arifosmcp.core.maruah_layer import get_maruah_layer, MaruahLevel

layer = get_maruah_layer()
receipt = layer.evaluate(
    output="...",
    maruah_level=MaruahLevel.SOFT,        # PHATIC/SOFT/HARD/CRISIS/REFUSE
    human_id="azwa",                      # optional recipient handle
    context={"urgency_signal": "high"},   # capacity calibration input
)
if receipt.verdict == DeliveryVerdict.M_HOLD:
    # log + suggest repair, do not auto-send
```

### Status

- **M1-M6**: Substrate implemented, 29/29 tests pass.
- **F1-L13 regression**: 24/24 floor tests still pass. No mutasi.
- **Forge receipt**: `/root/forge_work/maruah-layer-forge-2026-06-24/`

**DITEMPA BUKAN DIBERI — The kernel now governs not just what the agent does,
but how it speaks to humans.**
