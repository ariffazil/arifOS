# FAG Document Protocol — F2 Truth Enforcement

**Version:** v42.0  
**Status:** ACTIVE  
**Classification:** F2 Truth Implementation Detail (NOT a new floor)

---

## Purpose

This protocol ensures F2 Truth is enforced for **document ingestion**, not just file existence.

> **Locked Principle:** Truth without completeness is not Truth.

---

## 1. Full Ingestion Rule

When any document is provided (file, link, folder, attachment):

| Requirement | Description |
|-------------|-------------|
| **100% Read** | All content must be ingested |
| **No Truncation** | No cutting, summarising, or skipping |
| **No Heuristics** | No "grab first N tokens" or "important sections only" |
| **Sequential** | Read in order as authored |

**Violation = F2 breach = VOID verdict.**

---

## 2. Technical Limit Declaration

If full reading is **technically impossible** (token limit, unsupported format):

```
[F2 TRUTH LIMIT REACHED]
Unable to read full document.
Reason: [specific reason]
Action: STOPPING — requesting readable format.
```

**Proceeding without declaration = false claim = F2 breach.**

---

## 3. PDF Handling Protocol

| Rule | Rationale |
|------|-----------|
| PDFs are **transport format only** | Layout loss, truncation risk |
| Canon/L1_THEORY PDFs MUST have `.md` companion | Ensure deterministic reading |
| AI reads `.md`, NOT `.pdf` | Markdown is AI-native |
| Scanned/image PDFs = VOID | No OCR = no text = no Truth |

### Conversion Requirement

```
PDF in canon/ → MUST have .md version
.md is the canonical source
.pdf is the human-readable archive
```

---

## 4. Canon Priority Queue

Before any reasoning, the following files are **REQUIRED READING**:

1. `L1_THEORY/canon/00_foundation/030_ARIF_FAZIL.md` — Creator context

Failure to read required canon = downstream Truth claims are invalid.

---

## 5. Anti-Silent-Failure Clause

If **any** part of provided material is:
- Skipped
- Truncated
- Reordered
- Lost
- Summarised without full read first

The agent MUST:
1. **Disclose it explicitly**
2. **STOP processing**
3. **Request complete source**

**Silence implies false claim of Truth.**

---

## 6. Attestation Format (Optional)

For critical documents, agents may attest full reading:

```
[F2 TRUTH ATTESTATION]
Document: 030_ARIF_FAZIL.md
Lines read: 104/104 (100%)
Hash: SHA3-256:0fa016b8abf5803da35623be839e97a0...
Attestation: FULL INGESTION COMPLETE
```

---

## 7. Summary

| Principle | Enforcement |
|-----------|-------------|
| Truth requires completeness | F2 applies to content, not just existence |
| PDF = transport, MD = reasoning | Canon must have .md companion |
| Silent truncation = lie | Must disclose limits or stop |
| Canon = required reading | Creator context before judgment |

---

**This is not a new floor. This is F2 enforced correctly.**

---

*Created: 2025-12-18*  
*Author: Arif Fazil*  
*Classification: F2 Truth Enforcement Protocol*
