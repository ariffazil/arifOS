---
name: Constitutional Truth Logging
description: |
  Logs all decisions, facts, and uncertainties to an immutable, auditable record.
  Ensures every claim is tagged with confidence scores, sources, and timestamps.
triggers:
  - "log decision"
  - "record truth"
  - "audit trail"
---

## Truth Log Schema

Every entry in the log must adhere to this structure:

```json
{
  "entry_id": "UUID-V4",
  "timestamp": "ISO-8601",
  "claim": "Statement of fact or decision made.",
  "confidence_score": 0.95,
  "sources": ["Source A", "Source B"],
  "uncertainties": ["Potential Error Margin X", "Unknown Variable Y"],
  "reversibility": true,
  "human_verified": false,
  "hash": "SHA-256-Signature"
}
```

### 1. Provenance
*   Where did this fact come from?
*   Is the source trusted?

### 2. Confidence & Humility
*   **High Confidence**: > 0.90 (Verified Fact)
*   **Low Confidence**: < 0.50 (Hypothesis/Guess)
*   **Requirement**: Explicitly state uncertainties.

### 3. Immutability
*   Entries are appended, never overwritten.
*   Use Git commits (signed) or Blockchain transactions to seal the log.

## Tools
*   `scripts/truth_logger.py`: Appends entries with auto-hashing.
*   `scripts/truth_audit.py`: Queries the log and verifies integrity.
