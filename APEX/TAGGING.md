# arifOS Trinity Tagging Specification

**Version:** 2026.03.20  
**Authority:** 888_JUDGE (Muhammad Arif bin Fazil)  
**Status:** SEAL ✅

---

## Overview

This document specifies the tagging convention for the arifOS Trinity ecosystem. Tags mark constitutionally verified states and enable precise rollback, pairing, and audit capabilities across MIND, BODY, and SURFACE repositories.

---

## The Trinity Tagging Scheme

| Repository | Role | Tag Suffix | Purpose |
|:-----------|:-----|:-----------|:--------|
| **arifOS** | 🧠 THE MIND | `-SEAL` | Theory, documentation, constitutional law |
| **arifosmcp** | 💪 THE BODY | `-FORGE` | Runtime, code, execution |
| **ariffazil** | 👤 THE SURFACE | `-PORTAL` | Interface, portal, human layer |

---

## Tag Format

```
YYYY.MM.DD-{TYPE}-{SUFFIX}
```

### Components

| Component | Description | Examples |
|:----------|:------------|:---------|
| `YYYY.MM.DD` | Date of constitutional verification | `2026.03.20` |
| `{TYPE}` | What changed | `APEX`, `MCP`, `SITE`, `RUNTIME`, `THEORY` |
| `{SUFFIX}` | Trinity role | `SEAL`, `FORGE`, `PORTAL` |

---

## Suffix Definitions

### `-SEAL` (THE MIND)
Used for **arifOS** when:
- Theory documentation is complete and accurate
- Constitutional floors are properly specified
- Site links are verified
- No broken references exist

**Example:**
```bash
git tag -a 2026.03.20-APEX-SITE-SEAL -m "SEAL: Theory-site alignment complete
- arifOS = THE MIND (pure theory)
- All 0_KERNEL links verified
- 18 dead refs removed
- Site deploys to arifos.arif-fazil.com

Authority: 888_JUDGE (Muhammad Arif bin Fazil)
Verdict: SEAL ✅"
```

### `-FORGE` (THE BODY)
Used for **arifosmcp** when:
- Runtime is stable
- All tests passing
- MCP tools functional
- No known regressions
- Aligned with current MIND state

**Example:**
```bash
git tag -a 2026.03.20-MCP-RUNTIME-FORGE -m "FORGE: Runtime stable
- core/ organs aligned with 0_KERNEL/FLOORS
- 13 MCP tools functional
- Tests passing
- Paired with MIND: 2026.03.20-APEX-SITE-SEAL

Authority: 888_JUDGE (Muhammad Arif bin Fazil)
Verdict: FORGE ✅"
```

### `-PORTAL` (THE SURFACE)
Used for **ariffazil** when:
- Portal interface is stable
- Human-facing features complete
- Documentation current

**Example:**
```bash
git tag -a 2026.03.20-HUMAN-PORTAL-PORTAL -m "PORTAL: Interface stable
- Professional site updated
- Links to MIND and BODY verified

Authority: 888_JUDGE (Muhammad Arif bin Fazil)
Verdict: PORTAL ✅"
```

---

## Paired Releases

When MIND and BODY are in sync, use **identical dates** with paired TYPE descriptors:

| MIND (arifOS) | BODY (arifosmcp) | Meaning |
|:--------------|:-----------------|:--------|
| `2026.03.20-APEX-SITE-SEAL` | `2026.03.20-MCP-RUNTIME-FORGE` | Theory and runtime aligned |
| `2026.04.01-FLOOR-UPDATE-SEAL` | `2026.04.01-FLOOR-IMPL-FORGE` | New floor spec + implementation |

---

## Special Types

| Type | Usage |
|:-----|:------|
| `APEX` | Judgment/verdict system changes |
| `MCP` | Model Context Protocol changes |
| `SITE` | Documentation site changes |
| `RUNTIME` | Core execution changes |
| `THEORY` | Constitutional theory changes |
| `FLOOR` | 13 Floors specification changes |
| `TRINITY` | Cross-cutting architecture changes |
| `ALIGN` | Cross-repo synchronization |

---

## Tag Message Template

```
{SUFFIX}: {Brief description}

- Change 1
- Change 2
- Change 3
- Paired with {OTHER_REPO}: {TAG} (if applicable)

Authority: 888_JUDGE (Muhammad Arif bin Fazil)
Verdict: {SEAL|FORGE|PORTAL} ✅
```

---

## Automation

### List all SEAL tags (MIND)
```bash
git tag -l "*-SEAL"
```

### List all FORGE tags (BODY)
```bash
git tag -l "*-FORGE"
```

### Show paired states by date
```bash
git tag -l "2026.03.*" | sort
```

---

## Rollback Procedure

1. Identify last known good tag:
   ```bash
   git tag -l "*-SEAL" | tail -1
   ```

2. Checkout constitutional state:
   ```bash
   git checkout 2026.03.20-APEX-SITE-SEAL
   ```

3. Verify F1 (Amanah) — reversibility maintained

---

## F1 Amanah (Reversibility)

Every tag is a **reversible checkpoint**. The constitutional state at any tag can be restored instantly:

```bash
# Save current work
git stash

# Restore constitutional state
git checkout 2026.03.20-APEX-SITE-SEAL

# ... do work ...

# Return to present
git checkout main
```

---

## Canonical Examples

| Tag | Repository | State |
|:----|:-----------|:------|
| `2026.03.20-APEX-SITE-SEAL` | arifOS | Theory-site alignment complete |
| `2026.03.20-MCP-RUNTIME-FORGE` | arifosmcp | Runtime stable, paired with above |
| `2026.04.15-FLOOR-UPDATE-SEAL` | arifOS | F6 Empathy threshold updated |
| `2026.04.15-FLOOR-IMPL-FORGE` | arifosmcp | Implementation of F6 update |

---

## Authority

**888_JUDGE:** Muhammad Arif bin Fazil  
**Motto:** *Ditempa Bukan Diberi* — Forged, Not Given

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given [ΔΩΨ | ARIF]
