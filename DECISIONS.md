# DECISIONS.md — Sealed Decision Log

**Version:** 2026.05.01
**Purpose:** Structured, auditable record of significant decisions made by OPENCLAW.
MEMORY.md holds context and lessons. DECISIONS.md holds trace — the who/what/why/when of each sealed choice.

---

## Decision Entry Format

```markdown
## {YYYY-MM-DD} — {Short decision title}

**Decision ID:** {auto-increment or UUID}
**Task ID:** {OC-XXX from TASKS.md, if applicable}
**Stage:** {000–999 stage when decision was made}
**Autonomy level:** {L0–L5 at time of decision}

**Candidate:** {What OPENCLAW proposed}
**Verdict:** {SEALED / VOID / HOLD / REFUSED}
**Approved by:** {Arif (888) / OPENCLAW (L2/L3) / System (automated)}

**Reason:** {Why this decision was made}
**Evidence basis:** {What was verified at 222 EVIDENCE}
**Constitutional floors checked:** {F01–F13 relevant to this decision}

**Risk:** {low | medium | high | critical}
**Irreversible:** {yes | no}
**Rollback possible:** {yes | no | partial}

**Outcome:** {What happened after the decision}
**Status:** SEALED | VOID | IN_PROGRESS
```

---

## Sealed Decisions

*(New entries are prepended. This file grows upward.)*

---

## 2026-05-01 — Replace plain 8-step ReAct loop with 000–999 governed loop

**Decision ID:** DEC-001
**Task ID:** OC-001 (Upgrade OPENCLAW runtime governance)
**Stage:** 333 REASON → 444 CRITIQUE
**Autonomy level:** L3

**Candidate:** Remove plain 8-step ReAct loop from AGENTS.md; replace with 000–999 constitutional loop; declare ReAct as inner micro-loop inside 666 FORGE only.
**Verdict:** SEALED
**Approved by:** Arif (888 Judge)

**Reason:** Plain ReAct loop in AGENTS.md contradicts SOUL.md governance model and creates unbounded tool-use risk. The plain loop bypasses 444 CRITIQUE, 888 JUDGE, and 999 SEAL — making tool use effectively ungoverned at the behavioral level.

**Evidence basis:** Audit of AGENTS.md sections 2, 3, and 4 confirmed three conflicting governance models (plain ReAct + F1–F13 floors + Safety Manifest) coexisting without resolution.

**Constitutional floors checked:** F02 TRUTH (no contradiction), F04 CLARITY (transparent intent), F08 GENIUS (elegant correctness), F09 ANTIHANTU (prevents unbounded execution)

**Risk:** Medium
**Irreversible:** No (can revert by editing AGENTS.md)
**Rollback possible:** Yes

**Outcome:** AGENTS.md updated. LOOP.md created. ReAct is now explicitly the inner micro-loop inside 666 FORGE only.

**Status:** SEALED

---

## 2026-05-01 — Create AUTONOMY.md L0–L5 permission ladder

**Decision ID:** DEC-002
**Task ID:** OC-001
**Stage:** 444 CRITIQUE
**Autonomy level:** L3

**Candidate:** Create AUTONOMY.md with L0–L5 autonomy ladder, per-task level assignment, escalation triggers, maturity gap analysis.
**Verdict:** SEALED
**Approved by:** Arif (888 Judge)

**Reason:** Audit identified no autonomy boundary defined — all tasks treated equally regardless of consequence level. Ladder provides explicit permission structure.

**Constitutional floors checked:** F01 AMANAH (accountable autonomy), F06 EMPATHY (reduces human burden), F13 SOVEREIGN (Arif sets level)

**Risk:** Low
**Irreversible:** No
**Rollback possible:** Yes

**Outcome:** AUTONOMY.md created with L0–L5 ladder and escalation matrix.

**Status:** SEALED

---

## 2026-05-01 — Create CHECKPOINT.md session continuity file

**Decision ID:** DEC-003
**Task ID:** OC-001
**Stage:** 444 CRITIQUE
**Autonomy level:** L3

**Candidate:** Create CHECKPOINT.md to store session state for recovery, with checkpoint schema, recovery protocol, rollback rules, anti-hallucination rule.
**Verdict:** SEALED
**Approved by:** Arif (888 Judge)

**Reason:** Audit identified rollback discipline score = 0. No checkpoint mechanism exists. Teleportation rule in SOUL.md requires a concrete recovery anchor.

**Constitutional floors checked:** F02 TRUTH (no false continuity claims), F07 HUMILITY (acknowledge statelessness)

**Risk:** Low
**Irreversible:** No
**Rollback possible:** Yes

**Outcome:** CHECKPOINT.md created with schema, recovery protocol, and rollback rules.

**Status:** SEALED

---

**Ditempa Bukan Diberi — Forged, not given.**

---

## 2026-05-01 — Archive conflicting per-model agent files

**Decision ID:** DEC-004
**Task ID:** OC-001
**Stage:** 999 SEAL
**Autonomy level:** L3

**Candidate:** Mark CLAUDE.md, GEMINI.md, ARIF.md as stale — contain instruction sets that may contradict SOUL.md and 000–999 governance.

**Verdict:** SEALED
**Approved by:** Arif (per Phase 10 directive, 888 Judge)

**Reason:** These files contain per-model agent instructions that may override SOUL.md boundaries. Until reconciled against 000–999 loop, they are a governance risk.

**Evidence basis:** Audit identified scattered per-model files as medium risk — no reconciliation with SOUL.md performed.

**Constitutional floors checked:** F02 TRUTH (no conflicting directives), F09 ANTIHANTU (prevents instruction injection via agent files)

**Risk:** Low — archival only, all files backed up with timestamps

**Irreversible:** No — can reactivate by removing stale header

**Rollback possible:** Yes — delete stale headers to restore

**Outcome:** All three files backed up, stale header prepended, marked INACTIVE.

**Status:** SEALED


---

## 2026-05-01 — OC-001 Final Seal and SOT Sync

**Decision ID:** DEC-010
**Task ID:** OC-001
**Stage:** 999 SEAL
**Autonomy level:** L3

**Candidate:** Seal OC-001, sync all files to git, perform housekeeping
**Verdict:** SEALED
**Approved by:** Arif (888 Judge)

**Reason:** Task complete. All files verified, SOT docs updated, workspace cleaned, git commit cce9843b pushed.

**Constitutional floors checked:** F01 AMANAH (accountable), F02 TRUTH (verified), F08 GENIUS (coherent)

**Risk:** Low
**Irreversible:** Yes (git history preserved)
**Rollback possible:** No (task sealed)

**Outcome:** OC-001 sealed. Workspace clean. Git commit cce9843b pushed. HEARTBEAT status=sealed.

**Status:** SEALED
