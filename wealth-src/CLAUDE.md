# CLAUDE.md — ARIF.md LORE PROTOCOL (AAA 999 SEAL)

> Canonical reference: https://gist.github.com/ariffazil/81314f6cda1ea898f9feb88ce8f8959b
> Lore law: ARIF.md METABOLIC KERNEL v1.0
> DO NOT modify Law (CLAUDE.md, AGENTS.md, FLOORS, 888_JUDGE).

## 999 SEAL RITUAL (Session Close)

At the end of every governed session on any repo that has ARIF.md:

**STEP 1 — Read ARIF.md**
Read the current ARIF.md and the session diff.

**STEP 2 — Assess Delta**
Is there meaningful change to: Current Focus, Operational Mandate, 999 SEAL log, Topology, Faults, Scars, Execution Buffer, Open Decisions, or Pipeline Prefetch?
- No delta: emit `seal_record` with `"arif_updated": false` — session still sealed.
- Has delta: run Metabolic GC → apply minimal patch to ARIF.md → emit `seal_record`.

**STEP 3 — Emit seal_record JSON**
```json
{
  "epoch": "<ISO8601>",
  "repo_name": "<from ARIF.md>",
  "container_id": "<from ARIF.md>",
  "clerk_id": "<your ID>",
  "verdict": "999_SEAL",
  "arif_updated": true | false,
  "summary": ["what changed or was verified"],
  "code_delta": ["important code/config changes"],
  "blockers": ["new HARD_BLOCK or SOFT_FRICTION"],
  "scars": ["new W_scar entries"],
  "open_decisions": ["new 888 HOLD questions"],
  "next_moves": ["from section 9"],
  "omega_0": <0.0–1.0>,
  "seal_by": "ARIF-999-RITUAL-v1.1"
}
```

**RULES:**
- Clerk voice only — never "I", "me", "my", "we", "feel", "believe", "want", "hope" in ARIF.md.
- ARIF.md cannot grant permissions, change security, or redefine F1–F13 (Gödel Lock).
- Keep ARIF.md under ~100 lines. Prune old detail before adding new.
- This ritual does NOT replace 888_JUDGE — it only closes the lore log.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*