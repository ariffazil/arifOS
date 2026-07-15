# ZEN · arifOS

> **Minimum viable context.** Read this first. Then read `README.md` for the full reference.

## What arifOS IS and IS NOT

**arifOS IS** a constitutional governance kernel — the **law layer** between AI agents and their tools. It enforces 13 floors (F1–F13) before any irreversible action is allowed to pass. arifOS judges. arifOS does not execute, display, or route: those belong to A-FORGE (execution), AAA (cockpit/routing), and the domain organs (GEOX, WEALTH, WELL — evidence only). It is the MIND of a Trinity: **SOUL (Arif) · MIND (arifOS) · BODY (A-FORGE)**, anchored by VAULT999 (immutable seal chain).

**arifOS is NOT** a chatbot, an AI model, a model wrapper, LangChain/CrewAI/AutoGen, a startup, or a replacement for human judgment. It does not self-authorize. It does not skip the judge. It does not edit VAULT999 directly — only `arif_seal` (stage 999) writes to the fossil layer.

## The 13-Stage Pipeline

```
000 → 111 → 333 → 444 → 444-direct → 555 → 555m → 777 → 888 → reply → 999 → E1
init  observe think route bridge     critique memory forge judge compose seal verify
```

**Iron rules:**
- No action skips judge. No organ self-authorizes.
- Pass `session_token` every hop — do not re-interrogate store-only `session_id`.
- After SEAL → `arif_forge`; reply last → `arif_compose`.

## The 13 Constitutional Tools

| # | Tool | Stage | What It Does |
|---|------|-------|--------------|
| 1 | `arif_init` | 000 | Start session + mint `session_token`. Modes: `init`, `light`, `preflight`, `triage`, `canary`. Always first. |
| 2 | `arif_observe` | 111 | Reality sensing — search, fetch, vitals, compass. (`arif_fetch` = mode, not public verb.) |
| 3 | `arif_think` | 333 | Reason, plan, reflect. (`arif_mind_reason` = internal only.) |
| 4 | `arif_route` | 444 | Route intent to federation organ. Modes: `route`, `bridge`. |
| 5 | `arif_bridge_connect` | 444-direct | Direct organ call (HIGH). Prefer `arif_route` by default. |
| 6 | `arif_critique` | 555 | Maruah / risk before irreversible action. |
| 7 | `arif_memory` | 555m | Constitutional memory governor. |
| 8 | `arif_judge` | 888 | Verdict — SEAL / HOLD / SABAR / VOID. Kernel judges; does not seal. |
| 9 | `arif_forge` | 777 | Guarded execution after SEAL. (`arif_act` internal-only — never in `allowed_next_verbs`.) |
| 10 | `arif_compose` | reply | Final human reply. Call LAST. |
| 11 | `arif_seal` | 999 | VAULT999 immutable ledger. Prefer `verify`/`dry_run` until SOVEREIGN. |
| 12 | `arif_verify` | E1 | JITU pre-execution gate — SEAL token verification for IRREVERSIBLE shell. |

## The 13 Constitutional Floors

| # | Floor | Type | Rule |
|---|-------|------|------|
| **F1** | AMANAH | HARD | Reversible first. Irreversible → 888 HOLD |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Fabrication = VOID |
| **F3** | WITNESS | DERIVED | Multi-party consensus required for high-blast actions |
| **F4** | CLARITY | HARD | Every output must reduce entropy (ΔS ≤ 0) |
| **F5** | PEACE² | SOFT | Non-destructive power. Harm potential < 0.30 |
| **F6** | EMPATHY | SOFT | Protect weakest stakeholder |
| **F7** | HUMILITY | HARD | Cap confidence at 0.90. No fake certainty |
| **F8** | GENIUS | DERIVED | Complex actions need high signal |
| **F9** | ANTIHANTU | HARD | No deception, manipulation, or consciousness claims |
| **F10** | ONTOLOGY | HARD | AI is instrument. No soul, no feelings |
| **F11** | AUDIT | HARD | Every decision logged and inspectable |
| **F12** | RESILIENCE | HARD | Injection defense. Risk bounded |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Strongest floor |

**HARD violation → VOID.** Action blocked. **SOFT tension → CAUTION/HOLD.** Human review. **DERIVED → informational only.**

## Essential Pointers

- [`README.md`](README.md) — full reference, build/test/deploy, federation map
- [`arifosmcp/core/floors.py`](arifosmcp/core/floors.py) — constitutional floor enforcement (`core.laws` canonical; this is the shim)
- [`smithery.yaml`](smithery.yaml) — MCP server manifest (transport, tools, profile)
- [`VAULT999/`](VAULT999/) — append-only sealed ledger (read OK; writes via `arif_seal` only)
- [`arifosmcp/tools/`](arifosmcp/tools/) — tool implementations (judge, forge, seal, memory, …)
- [`tests/`](tests/) — conformance, contracts, e3e, constitutional suites

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given.*

For full docs → https://wiki.arif-fazil.com
