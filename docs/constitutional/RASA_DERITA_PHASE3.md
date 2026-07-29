# RASA DERITA — Phase 3 Gate Wiring

| Field | Value |
|-------|--------|
| Branch | `forge/rasa-derita-semantic-closure` |
| Phase | **3 — wire cascade + consent** |
| Public tools | **+0** |
| Verdict | `888_HOLD` — gates wired in codepaths; not VAULT-attested install |

## Wired surfaces

| Surface | Gate behaviour |
|---------|----------------|
| `runtime/kernel/judge.py` | Tripwire `RASA_DERITA` after reversibility |
| `tools/judge.py` (`arif_judge`) | Early HOLD if L3 candidate lacks cascade/lease |
| `tools/forge.py` (`arif_forge`) | Mutate modes HOLD before P0 boundary |
| `runtime/forge_preflight.py` | Stage 3c + final HOLD if `rasa_derita_ok=False` |
| `/health` | `rasa_derita` schema load receipt (not a tool) |

## Module

`arifosmcp/kernel/rasa_derita_gates.py`

## Still open

- Full boot enforcement_mode SEAL
- Live refuse probes against production deploy
- VAULT `INSTALLED_ENFORCED`
- 15 adversarial evals as e2e runtime suite
- P0 forge execution boundary still closed (only `query` allowed)

DITEMPA BUKAN DIBERI
