<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-27
valid_from: 2026-06-27
valid_until: 2026-07-27
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

> **Constitutional Intelligence Kernel** — arifOS structures decision; it does not decide.
> Constitutional judgment (SEAL / SABAR / VOID) and floor enforcement remain in arifOS.
>
> **Mission:** Build the substrate that keeps increasing intelligence governable.
> AGI needs verdict-gated bus; ASI needs civilization-scale restraint + hard refusal + world model.
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

## 🛡️ STEEL SECURITY LAYER

Four scanners (Trivy, Semgrep, Ruff, Gitleaks) run on every `make forge` / `make sot-check`. **Non-blocking** — no pre-commit hooks, no git blocks. If CRITICAL/HIGH findings detected, `888_HOLD` event fires to NATS. Agents stay free; the watch is quiet.

**Rules:** Never add blocking hooks. Never skip the audit. Treat 888_HOLD as real flags.

---

## 🪞 SELF-AUDIT & HARDENING

Canonical self-audit prompt: [`SELF_AUDIT_PROMPT.md`](./SELF_AUDIT_PROMPT.md). Enforces Reflexion Loop (000→111→333→555→777→888→999) before ANY kernel mutation. For OBSERVE/READ tasks, skip 333–777 but complete 000, 111, 888.

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
