# SECURITY — arifOS Federation

> **DITEMPA BUKAN DIBERI** — Forged, Not Given.

## Public Repository vs Live Codebase

The GitHub repository `ariffazil/arifos` is a **public snapshot**. The live production
codebase runs on VPS `af-forge` (72.62.71.199) and includes active security patches
not present in the public repo.

### What the public repo does NOT have (but live code does):

| Area | Live code state | Public repo state |
|---|---|---|
| **Identity verification** | `actor_id` stays `claimed`, NOT `verified`. Sessions stay `OBSERVE_ONLY` without crypto proof. | `SEMANTIC_KEYS` bypass existed (now removed). |
| **Schema strictness** | `additionalProperties: false` (zero occurrences of permissive schema). | `additionalProperties: True` in multiple places. |
| **CORS** | Env-driven allowed origins, defaults to federation domains only. | `allow_origins=["*"]` wildcard. |
| **Host binding** | Defaults to `127.0.0.1`. | Defaults to `0.0.0.0`. |
| **Irreversible gates** | Tier 3 tools (`arif_vault_seal`, `arif_forge_execute`) require sovereign session authorization. | Missing or advisory-only. |
| **Forge execution** | Requires prior `arif_judge` + `arif_seal` receipt. | No visible prior-judge gate. |
| **MCP error handling** | `isError` handled in multiple paths. | Only `{ok:false, verdict:"VOID"}`. |
| **Logger fix** | `session.py` has proper `import logging` + `logger` defined. | Missing logger causes `NameError` on init mode. |
| **Shadow mode routing** | `arif_critique(mode="shadow")` routes to `arif_self_evaluate`. | Falls through to generic LLM, times out at 30s. |
| **Metacognition** | VOID/failure responses get `confidence: 0.0` + honest failure text. | Boilerplate `confidence: 0.65` on all responses. |

### Security patches applied (2026-07-06):

1. **CORS hardening** — `server.py`: env-driven origins via `ARIFOS_CORS_ORIGINS`
2. **Semantic key removal** — `governance_identity.py`, `command_center/identities.py`: dead `SEMANTIC_KEYS` bypass removed
3. **Logger fix** — `tools/session.py`: missing `import logging` + `logger` definition
4. **Shadow routing** — `runtime/tools.py`: `mode="shadow"` now routes to `arif_self_evaluate`
5. **Metacognition honesty** — `runtime/tools.py`: VOID responses get `confidence: 0.0`

### Reporting vulnerabilities

Contact: Muhammad Arif bin Fazil (F13 SOVEREIGN)
Telegram: @ariffazil

Do NOT file public GitHub issues for security vulnerabilities.
