# RASA DERITA — Phase 1 Land Receipt

| Field | Value |
|-------|--------|
| Branch | `forge/rasa-derita-semantic-closure` |
| Phase | **1 — freeze & specify** |
| Production behaviour | **unchanged** |
| Public tools | **+0** |
| Verdict | `888_HOLD` — specification landed; installation not proven |

## What Phase 1 includes

- Canonical schema: `arifosmcp/schemas/constitutional/rasa-derita-schema.json`
- Structural loader (no enforcement): `arifosmcp/schemas/constitutional/`
- Gate schemas: claim_envelope, entropy_ledger, federated_evidence, human_impact
- Failing/target tests for six gates + e2e trauma scenarios
- Eval fixtures: `tests/fixtures/rasa_derita/evals.json`
- Invariant ledger: `arifosmcp/schemas/constitutional/INVARIANTS.md`

## What Phase 1 deliberately excludes

- No `core/laws.py` rewrite
- No scar fail-closed wiring
- No judge/forge consent-cascade gate
- No boot-time enforcement mode
- No VAULT `INSTALLED_ENFORCED`
- No new public MCP tools

## Proper statement

> RASA DERITA is a machine-readable constitutional specification **landed in-repo**.  
> It is **not** an installed and enforced kernel module.

## Next

Phase 2 — repair semantics against failing tests.  
Promotion only after live refuse probes + VAULT receipt.

DITEMPA BUKAN DIBERI
