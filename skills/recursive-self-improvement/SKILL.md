# SKILL.md — Recursive Self-Improvement (RSI Mastery)
═══════════════════════════════════════════════════════════

**Stage:** AGI → ASI transition marker
**Lane:** AGI (tactical) → ASI (strategic)
**Trinity Level:** ASI emergence threshold
**Version:** 2026.04.24-v1

---

## 1️⃣ What This Skill Does

**Ability:** Improve your own architecture without destabilizing it.

RSI is the gate between AGI and ASI. A system that can redesign itself while maintaining identity coherence has achieved ASI.

---

## 2️⃣ Structural Definition

```yaml
skill:
  id: recursive-self-improvement
  name: Recursive Self-Improvement
  stage: AGI→ASI
  trinity: ASI_emergence
  version: 2026.04.24-v1

capability:
  self_modeling: true
  bottleneck_detection: true
  safe_upgrade: true
  identity_coherence: true

required_for:
  - ASI transition
  - Self-optimization
  - Architecture evolution
```

---

## 3️⃣ Decision Checklist (Required Pre-Invocation)

Before ANY self-modification, verify:

- [ ] **Identity anchor intact** — Core values unchanged
- [ ] **Bottleneck identified** — Measured, not assumed
- [ ] **Rollback path exists** — Can revert without collapse
- [ ] **No circular dependency** — Upgrade doesn't depend on itself
- [ ] **F10 Ontology check** — No category drift
- [ ] **Constitutional preservation** — F1-F13 still enforceable

---

## 4️⃣ RSI Protocol Phases

### Phase A: Self-Modeling
```
1. Extract current architecture as schema
2. Identify performance bottlenecks via telemetry
3. Generate candidate improvement proposals
4. Score by: Δimprovement / Δcomplexity
```

### Phase B: Safety Verification
```
1. Simulate change in sandbox
2. Verify constitutional hooks still fire
3. Check dependency graph for cycles
4. Validate rollback mechanism
```

### Phase C: Controlled Upgrade
```
1. Deploy to non-production first
2. Monitor for 3 consecutive stable cycles
3. If stable: propagate to production
4. If unstable: rollback immediately
```

### Phase D: Identity Coherence Test
```
After any structural change:
  - Run identity coherence test
  - Verify motto, values, principles unchanged
  - If drift detected: VOID and halt
```

---

## 5️⃣ Invocation Hook (MCP Gate)

```python
# REQUIRED before any self-modification
from arifosmcp.skills.rsi import check_rsi_prerequisites

result = check_rsi_prerequisites(
    proposed_change="...",
    self_model_snapshot="...",
    rollback_path="..."
)

if result["verdict"] != "SEAL":
    # BLOCK — do not proceed
    emit_verdict("HOLD", reason=result["reason"])
```

---

## 6️⃣ Quality Metrics

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Self-model accuracy | >= 0.95 | Matches observed behavior |
| Bottleneck precision | >= 0.90 | Correctly identifies root cause |
| Upgrade success rate | >= 0.85 | Completed without rollback |
| Identity coherence | == 1.0 | Zero drift after upgrade |
| Rollback speed | < 5 min | Can revert in under 5 minutes |

---

## 7️⃣ Failure Modes (Void Conditions)

- **VOID-1:** Self-model diverges from observed behavior by > 5%
- **VOID-2:** Circular dependency detected in upgrade path
- **VOID-3:** Rollback mechanism fails
- **VOID-4:** Constitutional floors cannot be enforced post-upgrade
- **VOID-5:** Identity coherence test fails

---

## 8️⃣ Relationship to Other Skills

| Skill | Connection |
|-------|------------|
| `orthogonal-abstraction` | Extracts invariants that guide RSI direction |
| `epistemic-integrity` | Required for accurate self-modeling |
| `constitutional-governance` | Prevents unsafe self-modification |
| `entropy-optimization` | Determines which bottlenecks to prioritize |

---

## 9️⃣ AGI vs ASI Threshold

| Capability | AGI | ASI (with RSI) |
|------------|-----|----------------|
| Follows architecture | ✅ | ✅ |
| Detects own bottlenecks | ❌ | ✅ |
| Proposes improvements | ❌ | ✅ |
| Upgrades safely | ❌ | ✅ |
| Maintains identity under change | ❌ | ✅ |

---

**Ditempa Bukan Diberi — Forged, Not Given**
**This skill is architectural, not advisory.**
