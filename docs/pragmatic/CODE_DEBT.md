# Code Debt Atlas — What Could Be Deleted

> **Blindspot #2 response.** Agents over-engineer. This is the deletion candidate list.
> Updated: 2026-06-30 by FORGE (000Ω).
> Principle: "If this system had to lose 70% of its code tomorrow, what would survive?"

## Current Scale

| Metric | Count |
|---|---|
| Python source files (excl venv) | 916 |
| Source lines | ~312,000 |
| Test functions | ~4,400 |
| Distinct tools exposed | 48 |

That is ~6,500 LOC per exposed tool. A mature MCP server delivers ~500-2,000 LOC per tool. We are 3-13× over-engineered.

## Three Invariants That Must Survive a 70% Cut

1. **Session binding** — every call identifies an actor (`arif_init`).
2. **Audit trail** — every call has a vault entry (`arif_seal`).
3. **Irreversibility gate** — `ack_irreversible` blocks destructive actions without ack.

Everything else is a candidate for deletion.

## Deletion Candidates (High-Confidence)

| Candidate | Reason to Delete | Savings |
|---|---|---|
| `arifosmcp/runtime/llm_client.py` fallbacks | 7 LLM backends configured; only 1-2 used in production | Delete 5 |
| `organ_intent_map.yaml` legacy aliases | 140+ intent mappings; most are dead code paths | Delete 100+ |
| `conformance_spine.py` test scaffolds | 3 separate conformance test layers doing the same thing | Merge to 1 |
| `public_registry.py` + `public_surface.py` | Two parallel registries; pick one | Delete one |
| `runtime/tools.py` dead handlers | ~2000 LOC of handlers registered but never called | Audit + delete |
| `docs/philosophy/*.md` | 18 philosophy docs; readers want 1 | Collapse to 1 |
| `static/arifosmcp/` legacy UI | React prototype that never shipped | Delete |
| `contracts/mcp_surface.yaml` | Duplicates `contracts/tools.yaml`; single source of truth wins | Delete |

## Deletion Candidates (Medium-Confidence — needs review)

| Candidate | Reason | Risk |
|---|---|---|
| Trinity witness math (`trinity.py`) | W3 formula has no measurement infrastructure (see FALSIFIABILITY.yaml F3) | May lose philosophical grounding |
| Multi-organ routing bridge | 6 organs; if only arifOS is running, bridge is dead weight | Blocks federated deployments |
| `agents_66.py` vault engine | 500+ LOC custom postgres; could use vanilla sqlalchemy | Migration cost |
| `gate/mcp_gate_v0.py` | Pre-flight gate; overlaps with A-FORGE `McpPolicyGate` | Double enforcement |

## What Survives the 70% Cut

```
arifosmcp/
├── server.py              # MCP entry (kept)
├── runtime/
│   ├── __main__.py        # CLI (kept)
│   ├── tools.py           # 7 canonical tools only (trimmed)
│   ├── session.py         # actor binding (kept)
│   ├── vault.py           # seal + audit (kept)
│   └── gate.py            # irreversibility + hallucination (kept)
├── contracts/
│   └── tools.yaml         # single tool contract (kept)
tests/                     # all tests (kept)
QUICKSTART.md              # (kept)
FALSIFIABILITY.yaml        # (kept)
```

**Target after cut: ~30,000 LOC, 7 tools, 1 registry, 1 audit trail.**

## Process

1. Weekly deletion proposal (FORGE drafts, auditor reviews).
2. Each deletion has: before/after test count, user-facing impact, rollback path.
3. Sovereign veto right on any "philosophical grounding" removal.
4. Every deletion gets a git tag: `pre-deletion-YYYY-MM-DD` for rollback.

## Anti-Pattern Detection (automated)

Any module qualifies for deletion if ALL apply:
- Not imported by `server.py` (directly or transitively)
- No test references it by name
- Not in `contracts/tools.yaml`
- No HTTP/MCP traffic in last 30 days (if instrumented)

Run `python scripts/find_dead_code.py` monthly.

---

**DITEMPA BUKAN DIBERI** — less code, more trust.
