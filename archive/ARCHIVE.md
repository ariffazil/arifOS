# arifOS Archive

**Status**: Historical reference only  
**Active Version**: v43 (see `arifos_clip/README.md`)  
**Last Updated**: 2025-12-19  

---

## What's Here

Documentation and specs from arifOS versions prior to v43.

---

## Why Archive?

v43 introduces **architectural changes**:

- **ICL Alignment**: Full integration with Intelligence Control Layer v43
- **Semantic Exit Codes**: Meaningful status signals (0, 1, 88, 89, 100, 255)
- **Hard vs Soft Floors**: F1/F9 block (VOID); F4/F5/F7 flag (FLAG)
- **/DOC PUSH Command**: New specialized pipeline for documentation
- **Authority Tokens**: Mandatory for /999 SEAL

These are non-backward-compatible. v42 docs kept for historical reference.

---

## Migration Path (v42 → v43)

### Exit Codes

**v42**:
```
0   – PASS
20  – PARTIAL
30  – SABAR
40  – VOID
88  – HOLD
100 – SEALED
```

**v43**:
```
0   → PASS     (Stage OK; continue)
1   → FLAG     (Soft floor violation; may override)
88  → HOLD     (Governance issue; must resolve)
89  → VOID     (Hard floor violation; must redesign)
100 → SEALED   (Decision immutable; done)
255 → ERROR    (System crash)
```

### Hard vs Soft Floors

**v42**: Floors were mentioned but not architecturally enforced.

**v43**: 
- **Hard floors (F1, F9)** → Exit 89 (VOID) — cannot override
- **Soft floors (F4, F5, F7)** → Exit 1 (FLAG) — may override with token

### /DOC PUSH

New in v43. Specialized pipeline for documentation governance automation.

### Authority Tokens

**v42**: Optional.

**v43**: **Mandatory for /999 SEAL.** No auto-sealing (preserves F9 Anti-Hantu).

---

## Files in This Archive

(Add historical docs here as needed)

---

## Questions?

See active documentation:
- Main README: `README.md` (root)
- aCLIP docs: `arifos_clip/README.md` (v43)
- ICL spec: `docs/ICL_v43_CANONICAL_SPEC.md`

---

**Ditempa, bukan diberi.** ✊

Version: Archive | Status: Historical | Governance: v43
