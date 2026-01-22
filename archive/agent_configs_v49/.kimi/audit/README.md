# Kimi Audit Reports Directory

**Purpose:** Store APEX PRIME constitutional audit reports

## Structure

Audit reports follow the naming convention: `YYYY-MM-DD_<subject>.md`

**Example:**
```
2026-01-12_kimi_apex_setup.md
2026-01-15_f9_floor_validation.md
2026-01-20_trinity_separation_audit.md
```

## Report Format

Each audit report must include:

1. **Header:** Date, auditor (Kimi Κ), subject
2. **Verdict:** VOID/SABAR/888_HOLD/PARTIAL/SEAL
3. **Floor Status Table:** F1-F9 with evidence and PRIMARY sources
4. **Detailed Analysis:** Floor-by-floor reasoning
5. **Recommendations:** What must change (if not SEAL)
6. **Uncertainty Statement:** Ω₀ band (0.03-0.05)
7. **Compliance Canary:** Version + floor count confirmation

## PRIMARY Source Requirements

All constitutional claims must cite PRIMARY sources:

- `spec/v46/*.json` (Track B - thresholds)
- `L1_THEORY/canon/*_v45.md` (Track A - law, SEALED status only)

**NOT Evidence:**
- Grep results (discovery, not verification)
- Code comments (may be outdated)
- Documentation (may lag PRIMARY sources)

## Verdict Authority

Kimi (Κ) issues constitutional verdicts, but human (Arif) ratifies.

```
Agent Work → Ψ (First-pass) → Κ (Constitutional) → Human (Ratify)
```

No self-sealing: Kimi's own work requires external audit.

---

**Status:** INITIALIZED
**Version:** v46.0.0
