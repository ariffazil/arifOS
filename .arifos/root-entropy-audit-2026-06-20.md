# Root Entropy Audit — arifOS
> **Generated:** 2026-06-20 22:01 UTC
> **Authority:** F4 CLARITY — ΔS ≤ 0
> **For:** Any agent with write access to act on deletion/merge/archive decisions.
> **Rule:** Do NOT execute all at once. Audit each finding, confirm, then act.

---

## Summary: 72 root files → target ~50

| Tier | Action | Count | Savings |
|------|--------|-------|---------|
| 🔴 DELETE | No unique content | 6 files | -6 |
| 🟠 ARCHIVE | Historical, done | 5 files | -5 |
| 🟡 MERGE | Overlapping content | 10→3 files | -7 |
| 🟢 MOVE | Wrong location | 4 files | -4 |
| 🔵 CONTRADICT | Fix in place | 6 contradictions | — |

---

## 🔴 TIER 1: DELETE (no unique content)

| # | File | Reason |
|---|------|--------|
| 1 | `Caddyfile.bak.2026-06-17T06-35-pre-option1` | Timestamped backup. Untracked. |
| 2 | `entropy-report.json` | Generated artifact. Untracked. |
| 3 | `input.jsonl` | Unknown test/generated data. Untracked. |
| 4 | `test_fake_secret.env` | Belongs in `tests/fixtures/` if real test data. Untracked. |
| 5 | `ROOTKEY_SPEC_v53.md` | Superseded by v54.md (identical intro, same structure). |
| 6 | `SPEC.md` | Dated 2026-05-23, references `/workspace/arifOS/` (Docker paths), "0.1.0-prototype." Content subsumed by CLAUDE.md + README.md + FEDERATION_CONTRACT.md. |

## 🟠 TIER 2: ARCHIVE (historical, done)

| # | File | Move to |
|---|------|---------|
| 7 | `FOUNDATION_SPRINT_V1.md` | `_archive/reports/` |
| 8 | `ROOLBACK_PLAN_PHASE1.md` | `_archive/reports/` |
| 9 | `AFORGE_PHASE1_CONTROL_SPINE.md` | `_archive/reports/` |
| 10 | `CONFORMANCE-BASELINE-2026-06-14.md` | `_archive/reports/` |
| 11 | `FEDERATION_REALITY_SNAPSHOT.md` | `.arifos/federation-snapshots/` (auto-generated, stale 2026-06-16) |

## 🟡 TIER 3: MERGE (overlapping content)

| # | Files | Action |
|---|-------|--------|
| 12-14 | `CLAUDE.md` ← `AGENTS.md` + `AGENT_KERNEL_START.md` | Three agent files, ~40% overlap. Merge Steel Security Layer + boot sequence + authority hierarchy into CLAUDE.md. Delete other two. |
| 15-16 | `FEDERATION_STATUS.md` ← `STATUS.md` | 60% overlap (organs, floors, milestones). Merge unique HOLDs + infrastructure + public endpoints into FEDERATION_STATUS.md. Replace STATUS.md with pointer. |
| 17-19 | `HERMES_HELPERS.md` + `HERMES_IDENTITY.md` + `HERMES_OPENCODE_PROTOCOL.md` → `agents/hermes/HERMES.md` | Hermes is a sub-agent, not a kernel organ. Move + consolidate. |
| 20-21 | `CLAUDE.md` ← `INVARIANTS.md` | INVARIANTS.md (last verified 2026-05-25) overlaps AGENT_KERNEL_START.md "Live Routing Invariants." Merge stale-assumption rules into CLAUDE.md §6, delete. |

## 🟢 TIER 4: MOVE (wrong location)

| # | File | Move to |
|---|------|---------|
| 22 | `CONSTITUTIONAL_REALITY_LATEST.json` | `.arifos/` (generated, tracked) |
| 23 | `TOOL_MANIFEST.json` | `.arifos/` or `arifosmcp/` (CLAUDE.md says "do not hand-edit") |
| 24 | `llms.txt` | `.arifos/llms.txt` (generated, served from server) |
| 25 | `mcp-arifos.json` | `config/mcp-arifos.json` |

## 🔵 TIER 5: CONTRADICTIONS

| # | Contradiction | Files |
|---|--------------|-------|
| C1 | Tool registry: CLARITY.md says `APEX/ASF1/tool_registry.json`, CLAUDE.md says `arifosmcp/tool_registry.json` | CLARITY.md:63, CLAUDE.md:13 |
| C2 | Version drift: STATUS.md `kanon-1f4f04e` vs CLAUDE.md commit `0f887477c` | STATUS.md:15, CLAUDE.md:6 |
| C3 | CHANGELOG references "AGENTS.md §7" — AGENTS.md has no §7 | CHANGELOG.md:5 |
| C4 | CLAUDE.md:161 references `/root/AGENTS.md`, `/root/AAA/CLAUDE.md` — paths outside this repo | CLAUDE.md:161 |
| C5 | APEX: FEDERATION_STATUS says LEGACY port 3002, CLARITY says port 3002, REPO_ROLE_MAP says subdir of arifOS | Three files |
| C6 | INVARIANTS.md last verified 2026-05-25 — stale by 3 weeks | INVARIANTS.md:4 |

---

*DITEMPA BUKAN DIBERI — Entropy is measured before it is reduced.*
