---
canon_id: 08_ARIFOS_SKILLS
bundle: CANON_APEX_V2
version: v2026.07.APEX
status: SEALED_CANON
apex_theory: T-000
floors_version: 2026.07
epoch: 2026-07-26T00:30+08
---

# ARIFOS_SKILLS — Operational Manifest

> **DITEMPA BUKAN DIBERI — Skills are forged, not collected.**

This manifest defines the operational skill surface for agents in the
arifOS federation. Skills are categorized by axis and autonomy tier.

## Substrate Skills (always loaded)

| Skill | Purpose | Floor |
|:------|:--------|:------|
| `kernel-bind` | Bind governance before action — constitutional floors, sovereign signals, autonomy tier | F1, F13 |
| `observe-ground` | Evidence before narrative — OBS/DER/INT/SPEC labels, confidence-cap | F2, F7 |
| `route-dispatch` | Right organ for right intent — classify, map, dispatch with fallback | F4 |
| `memory-manage` | Store less, recall well, forget when stale — ΔS ≤ 0 per cycle | F4, F11 |
| `verify-gate` | Four gates: authority + evidence + reversibility + lineage | F1, F11 |
| `audit-seal` | Every decision logged. Irreversible decisions sealed. | F11 |

## Knowledge Skills (domain-specific)

| Skill | Purpose |
|:------|:--------|
| `know-physics` | Conservation laws, thermodynamics, causality |
| `know-math` | Uncertainty quantified, proof has rules |
| `know-language` | Meaning ≠ syntax, pragmatics > semantics |

## Meta Skills (intelligence)

| Skill | Purpose |
|:------|:--------|
| `AGI-plan-dag` | Multi-step execution graphs, dependency-aware subtasks |
| `ASI-agentic-architecture` | Sovereign agent design — 9-skill spine, 3-agent model |
| `atlas333-cognitive-geometry` | 33 paradoxes — navigate between poles |
| `RSI-recursive-improvement` | Trace → diagnose → remediate → ledger at boundaries |
| `FLAME-router` | Classify inference: FLAME tool lane vs governed agent lane |
| `QQQ-recommendation` | ≥5 paths, BR/REV/Time/Conf, quantum effects |

## Forge Skills (execution)

| Skill | Purpose |
|:------|:--------|
| `FORGE-github` | Repository and GitHub transport operations |
| `FORGE-ci-diagnose` | Failing workflow evidence and root cause |
| `FORGE-pr-review` | Code correctness and regression review |
| `FORGE-pr-governance` | Merge authority, policy, and release gate |
| `FORGE-docker` / `FORGE-vps-docker` | Container lifecycle |
| `FORGE-mcp-smoke-test` | Server response validation |
| `FORGE-infra-guardian` | Caddy, Cloudflare, SSL, DNS |
| `FORGE-incident-triage` | Six-step incident response |
| `FORGE-verify-runtime` | Verification as terminal state |

## Domain Organ Skills

| Organ | Skills |
|:------|:-------|
| GEOX | geox-claim-grammar, geox-constitution, geox-contradiction-engine, geox-earth-evidence, geox-epistemic-ladder, geox-petrophysics-bounds, geox-redteam-hantu |
| WEALTH | wealth-capital-reasoning, wealth-capital-thermodynamics, wealth-collapse-signature, wealth-law-anthropology |
| WELL | well-substrate-readiness |

## Autonomy Tiers

| Tier | Actions | Gate |
|:-----|:--------|:-----|
| T1 AUTO-DO | Read, search, observe, plan, edit, build, test, lint, format | None |
| T2 ANNOUNCE | Multi-file refactor, new dependency, deploy after green tests | 10s window |
| T3 888_HOLD | rm -rf, DROP TABLE, force push, prod deploy w/o test pass, secrets | Arif required |

## Skill Discovery

```bash
# List live skills
ls /root/.agents/skills/ | head -30

# Check skill mesh health
bash /root/AAA/skills/scripts/skill-mesh-sync.sh --check

# Load a skill at runtime
skill(name="<skill-name>")
```

DITEMPA BUKAN DIBERI — Naming is the first act of creation.

---
CANON_STATUS: SEALED · APEX THEORY
CANON_BUNDLE: CANON_APEX_V2 (13 files)
GOVERNANCE_CORE: arifOS · APEX Theory · F1–F13 Floors
VAULT999_HASH: <pending>
TRI-WITNESS: human · AI · earth >= 0.75
