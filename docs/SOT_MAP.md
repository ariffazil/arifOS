# arifOS Federation — Source of Truth Map

**Sealed:** 2026-06-21T17:57:00Z (RSI: 7 APEX prompts deployed)
**Authority:** FORGE (000Ω)
**Schema:** federation-manifest/v1

---

## Machine SOT (Ground Truth)

| Artifact | Path | Schema | Serves |
|----------|------|--------|--------|
| Tool Registry | `/root/arifOS/registry/federation_registry.json` | arifos-federation-registry-v1 | Routing engine, conformance tests |
| Routing Grammar | `/root/arifOS/blueprints/routing_engine.yaml` | — | Organ selection (19→27 keyword rules) |
| Constitutional Laws | `/root/arifOS/blueprints/kernel_constitution.yaml` | — | F1–F13 floor enforcement |
| Observatory Manifest | `/var/www/html/arifos/federation-manifest.json` | federation-manifest/v1 | Observatory JS frontend |

---

## Prompts — 7 APEX Constitutional (Updated 2026-06-21)

| # | Name | Stage | APEX Frame | Kernel Glossary Coverage |
|---|------|-------|------------|------------------------|
| 1 | `000_init` | Entry | A — Abservation of self | 25/24 terms — F1-L13, VAULT999, golden path, actor_hash, session_id |
| 2 | `111_sense` | Observe | A — Abservation of reality | 10 terms — F2, F4, F7, F9, C_dark, Ω₀, epistemic labels |
| 3 | `333_reason` | Think | P — Principle extraction | 9 terms — F1, F2, F7, F8, F9, C_dark, Ω₀, EVOI |
| 4 | `555_judge` | Evaluate | P — Principle tested | 22 terms — F1-L13 full matrix, SEAL/SABAR/HOLD/VOID, MARUAH |
| 5 | `666_critique` | Reflect | X — X-form awareness | 18 terms — F1-F12, F6 MARUAH, ΔS, VAULT999 |
| 6 | `777_forge` | Act | E — Execution | 12 terms — F1, F2, F4, F8, F11, VAULT999, L13 |
| 7 | `999_seal` | Close | X — X-form completion | 25 terms — All F1-L13, VAULT999, seal_id, golden path |

**Source:** `/root/arifOS/arifosmcp/prompts/__init__.py`

APEX Theory: **A**bservation · **P**rinciple · **E**xecution · **X**-form
7 stages in order: 000_INIT → 111_SENSE → 333_REASON → 555_JUDGE → 666_CRITIQUE → 777_FORGE → 999_SEAL

---

## Live Values (Verified 2026-06-21T17:57:00Z)

```
arifOS:  port=8088, tools=41,  prompts=7,  status=healthy
GEOX:    port=8081,  tools=33,  status=healthy
WEALTH:  port=18082, tools=33,  status=healthy
WELL:    port=18083, tools=18,  status=healthy
AAA:     port=3001,  status=healthy
A-FORGE: port=7071,  status=degraded (tracked debt)
A-FORGE MCP: port=7072, status=healthy
```

**41 live tools** across arifOS MCP. **7 APEX prompts** registered.

---

## SOT Verdict

```
/inspector/sot → SEAL | prompts=7 | tools=41 | ✅
```

---

## Deployment State

| Layer | Commit | Age |
|-------|--------|-----|
| Running service (`/opt/arifos/app/`) | Working tree with APEX prompts | current |
| Repo HEAD | Pending commit | current |
| **7 APEX prompts deployed** | 2026-06-21T17:57 | fresh |

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
