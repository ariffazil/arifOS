# FEDERATION CONTRACT — arifOS Constitutional Federation

> **SOT-MANIFEST**
> owner: Arif
> last_verified: 2026-05-19
> valid_from: 2026-05-19
> valid_until: 2026-06-19
> confidence: high
> scope: /root (all repos)

## 1. Sovereign Stack Definition

```
Arif (Human Sovereign)
         |
    arifOS (Law Kernel) — F1-F13, 888 JUDGE, 999 SEAL, VAULT999
         |
    +--------+--------+--------+--------+--------+
    |        |        |        |        |        |
 A-FORGE   GEOX    WEALTH    AAA      WELL    APEX
(Execution)(Earth) (Capital)(Control)(Human) (Judge)
```

## 2. Cross-Repo Call Matrix

| Caller → Callee | Interface | Data Crosses | Authority |
|-----------------|-----------|--------------|-----------|
| **arifOS → GEOX** | MCP tool call (port 8081) | Earth-truth artifacts, prospect verdicts | GEOX is source of earth truth; arifOS governs retrieval |
| **arifOS → WEALTH** | MCP tool call (port 8082) | Capital scores, decision memos | WEALTH is source of capital truth; arifOS governs retrieval |
| **arifOS → WELL** | Health probe (port 18083) | Human readiness score | WELL is source of human truth; arifOS reads only |
| **AAA → arifOS** | MCP streamable-http (port 8080) | Tool registry, floor status, session tokens | arifOS is authority; AAA is consumer |
| **AAA → A-FORGE** | HTTP bridge (port 7071) / A2A mesh | Deploy status, release artifacts | A-FORGE is authority; AAA is consumer |
| **A-FORGE → arifOS** | MCP stdio / HTTP | Constitutional constraints, floor results | arifOS is authority; A-FORGE is consumer |
| **A-FORGE → GEOX** | MCP mesh via MiniMaxMcpClient | Earth-truth artifacts (delegated) | GEOX is authority; A-FORGE is proxy |
| **A-FORGE → WEALTH** | MCP mesh via MiniMaxMcpClient | Capital scores (delegated) | WEALTH is authority; A-FORGE is proxy |
| **GEOX → arifOS** | Federation probe / MCP mesh | Constitutional constraints, seal requirements | arifOS is authority; GEOX is subject |
| **WEALTH → arifOS** | Federation probe / MCP mesh | Constitutional constraints, seal requirements | arifOS is authority; WEALTH is subject |

## 3. Object Authority Map

| Object | Canonical Repo | Why |
|--------|---------------|-----|
| Session ID | **arifOS** | 000_INIT generates and binds sessions |
| Actor Identity | **arifOS** | F11_AUTH gates all identity claims |
| Floor Verdict (SEAL/HOLD/VOID) | **arifOS** | 888_JUDGE is the only adjudicator |
| Vault999 Entry | **arifOS** | 999_VAULT is append-only hash-chained |
| Tool Registry | **arifOS** | Canonical manifest is source of truth |
| Schema Definition | **arifOS** | Pydantic schemas govern all outputs |
| Earth-Truth Artifact | **GEOX** | Physics9 boundary enforcement |
| Prospect Evaluation | **GEOX** | Subsurface reasoning + 888_JUDSEAL gateway |
| Capital Score / NPV / IRR | **WEALTH** | wealth.physics_economics.v1 |
| Decision Memo | **WEALTH** | Structured capital intelligence verdict |
| Operator Dashboard | **AAA** | React cockpit is the UX surface |
| Agent Identity Pack | **AAA** | SOUL.md, IDENTITY.md seed data |
| A2A Task | **AAA** | A2A v1.0.0 gateway (port 3001) |
| Container Image | **A-FORGE** | GHCR publishing pipeline |
| Compose Definition | **A-FORGE** | Canonical deploy orchestration |
| Build SHA / Release | **A-FORGE** | `make publish-ghcr` |
| Human Readiness Score | **WELL** | H-WELL / M-WELL / C-WELL scoring |
| Constitutional Amendment | **APEX** | Cross-model deliberation + resilience contract |

## 4. Boundary Enforcement Rules

1. **No repo may duplicate constitutional law.** F1-F13 live only in arifOS. Other repos may reference but not redefine.
2. **No repo may seal without arifOS.** Only 888_JUDGE and 999_VAULT may emit seals.
3. **GEOX and WEALTH may fail-closed independently** on Physics9 or wealth.physics_economics.v1 boundaries, but must escalate to arifOS for constitutional overrides.
4. **AAA may not adjudicate.** It routes, displays, and asserts identity — it does not judge.
5. **A-FORGE may not define policy.** It packages, deploys, and executes — it does not legislate.

## 5. Deployment Topology

| Service | Compose File | Canonical Source | Runtime Copy |
|---------|-------------|------------------|--------------|
| arifosmcp | `compose/docker-compose.yml` | `arifOS/deploy/` | `/root/compose/` |
| geox_eic | `compose/docker-compose.yml` | `geox/` (image build) | `/root/compose/` |
| wealth-organ | `compose/docker-compose.yml` | `WEALTH/` (image build) | `/root/compose/` |
| well | `compose/docker-compose.yml` | `WELL/` (image build) | `/root/compose/` |
| aaa-a2a | `A-FORGE/docker-compose.yml` | `A-FORGE/deploy/` | `/root/compose/` |
| af-bridge | `A-FORGE/docker-compose.yml` | `A-FORGE/deploy/` | `/root/compose/` |

**Rule:** Edit canonical source → commit → rsync to runtime copy → `docker compose up -d`

## 6. Change Control

| Change Type | Authority | Review | Seal Required |
|-------------|-----------|--------|---------------|
| Constitutional floor change (F1-F13) | Arif (human) | 888_JUDGE | YES — 72h Phoenix-72 |
| Cross-repo interface change | arifOS + affected repo | Federation probe | YES |
| Deploy config change | A-FORGE | CI build pass | NO (but smoke test) |
| Domain tool addition (GEOX/WEALTH) | Repo owner | Unit tests | NO |
| UI change (AAA) | AAA | Build + lint | NO |
| Repo surgery (move/delete files) | Arif (human) | 888 HOLD report | YES |

## 7. Machine-Readable Contract Locations

| Repo | Contract Path | Format |
|------|--------------|--------|
| arifOS | `contracts/tools.yaml` | YAML |
| GEOX | `contracts/tools.yaml` | YAML |
| WEALTH | `contracts/tools.yaml` | YAML |
| AAA | `contracts/tools.yaml` | YAML |
| A-FORGE | `contracts/tools.yaml` | YAML |
| Cross-repo | `FEDERATION_CONTRACT.md` | Markdown (this file) |

---

DITEMPA BUKAN DIBERI — Forged, not given.
