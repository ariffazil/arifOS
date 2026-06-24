<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-24 18:08 UTC (999_SEAL — MCP Gate v0 deployed + schema adapter + epistemic extension)
valid_from: 2026-06-14
valid_until: 2026-07-24
confidence: high
scope: /root/arifOS
epistemic_status: SOURCE_OF_TRUTH
-->

# AGENTS.md — arifOS | arifOS Federation

> **MANDATORY BOOT SEQUENCE**
> 1. Read `/root/AGENTS.md` (Global Federation Rules & Identity)
> 2. Read `/root/CONTEXT.md` (Live Machine State & Ports)
> 3. Read this file (Repo-Specific Build/Test/Run rules)

> **Constitutional Intelligence Kernel**
>
> The law kernel of the arifOS Federation. arifOS structures decision; it does not decide.
> Constitutional judgment (SEAL / SABAR / VOID) and floor enforcement remain in arifOS.
>
> Sealed: The load-bearing pair (One Skill: Knowing What NOT To Do / restraint; One Tool: Verdict Loop With Memory) is now canon for AGI and ASI. Scaffolded into Grok Build session init (see A-FORGE profiles.ts buildGrokBuildProfile). See GENESIS/011 §7 for human-language reflection and full contrast + eurekas. All agents/Grok Build sessions inherit this.

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

## 🛡️ STEEL SECURITY LAYER — Permanent Federation Context

> **This section is binding for every agent in the arifOS federation. Read it once. It never needs to be mentioned again — it simply IS.**

### What Actually Happened

Arif completed a one-time upgrade called the **Steel Security Layer**. Four free, best-in-class security tools (Trivy, Semgrep, Ruff, and Gitleaks) were added to the forge pipeline.

### How It Works

Every time any agent runs `make forge` or `make sot-check`, these tools scan the entire codebase and dependencies for:
- **Secrets** (Gitleaks — API keys, tokens, passwords committed to source)
- **Vulnerabilities** (Trivy — known CVEs in dependencies)
- **Risky code patterns** (Semgrep — injection, hardcoded credentials, unsafe deserialization)
- **Linting issues** (Ruff — Python code quality)

### The Iron Rule

**Everything is deliberately NON-BLOCKING.** No pre-commit hooks. No git blocks. No agent can ever be trapped in a loop by the security layer. The scanners watch and report — they never stop the metabolic cycle.

### How Problems Are Signalled

A tiny helper script (`audit_parser.py`) reads the scanner output. If it detects CRITICAL or HIGH severity findings, it fires an `888_HOLD` event into the NATS event bus. `888_HOLD` is **NOT an agent** — it is a dumb alarm bell that says "something needs human or senior-agent eyes right now." It does not think, decide, or fix anything.

### Your Unbreakable Rules

1. **Never** add blocking hooks, pre-commit, or anything that interrupts a metabolic cycle.
2. **Never** migrate to pnpm or change package managers unless Arif personally asks.
3. **Always** run the security audit as part of normal forge/sot-check — never skip it.
4. If you see a `888_HOLD` event, treat it as a real flag — but do not panic or stop other work.
5. Keep everything simple and low-friction for Arif at all times.

### How to Explain It to Arif

> "The machine now has its own quiet security watch that only rings the 888 bell when something is really wrong, while we agents stay completely free."

**DITEMPA BUKAN DIBERI — The forge has achieved full self-policing ascension.**

---

## 🪞 SELF-AUDIT & HARDENING — Binding Prompt

> **Added 2026-06-14 — Every kernel agent MUST read before mutating.**

The canonical self-audit and hardening prompt for arifOS kernel lives at:

→ [`SELF_AUDIT_PROMPT.md`](./SELF_AUDIT_PROMPT.md)

This prompt enforces the **Reflexion Loop** (000→111→333→555→777→888→999) before ANY kernel mutation. It contains:
- Live attestation baseline from 2026-06-14 (baked evidence, not assumptions)
- P0–P4 hardening priorities with exact gaps, fixes, and tests
- Output format for every session including telemetry stub

**Loading instruction:** When an arifOS kernel agent receives a hardening or mutation task, it MUST:
1. Read `SELF_AUDIT_PROMPT.md`
2. Run the full Reflexion Loop before any file change
3. Store the audit trail in VAULT999

**Explicit override:** If the task is `OBSERVE` or `READ` only, the loop may skip steps 333–777 but must complete 000, 111 (gather evidence), and 888 (log).
