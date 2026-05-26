# arifOS Federation — Source of Truth Map

**Sealed:** 2026-05-26  
**Authority:** Ω-FORGE (arifOS Forge Agent)  
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

## Live Values (Verified 2026-05-26T14:05:00Z)

```
arifOS:  port=8088, tools=13,  status=healthy
GEOX:    port=8081,  tools=11,  status=healthy
WEALTH:  port=18082, tools=33,  status=healthy
WELL:    port=18083, tools=13,  status=healthy (WELL_HOLD active)
AAA:     port=443,   tools=—,   status=healthy
A-FORGE: port=7071,  tools=—,   status=degraded
```

**70 confirmed live tools** across 4 organs. A-FORGE: no /tools endpoint.

---

## SOT Verdict

```
/inspector/sot → SEAL | live=13 | main=13 | ✅
```

---

## Contradiction Resolution Log

| Date | Issue | Fix |
|------|-------|-----|
| 2026-05-26 | Caddy static manifest had stale ports (8081/8082/8083) and wrong tool counts | Updated `/var/www/html/arifos/federation-manifest.json` |
| 2026-05-26 | Repo static used different schema (arifos-federation-manifest-v1) vs Caddy (federation-manifest/v1) | Synced all 3 copies to federation-manifest/v1 |
| 2026-05-26 | In-app static was out of date | Synced to match Caddy |

---

## Deployment State

| Layer | Commit | Age |
|-------|--------|-----|
| Running service (`/opt/arifos/app/`) | `0bb99a59` | 21 days |
| Repo HEAD | `aad35885` | current |
| Observatory build | `0bb99a5` | 21 days |
| Committed fix | `1985b7c8` | just now |

**Note:** Running service has uncommitted local modifications. Repo is 47 commits ahead of running service.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
