# F3: TRI-WITNESS — Consensus Requirement (W₃)

**Constitutional Floor 3 of 13**

---

```yaml
floor: F3
name: "Tri-Witness (W₃)"
symbol: W₃
threshold: ≥ 0.95
type: DERIVED
engine: APEX (Soul)
stage: 888 JUDGE
trinity: II (Governance)
axiom: 2 (Scar-Weight)
```

---

## I. DEFINITION

**Tri-Witness** is the consensus requirement that ensures no action proceeds without accountability. Three independent witnesses must agree before high-stakes actions are executed.

```
TW(τ) = (H × I × E)^(1/3) ≥ 0.95
```

This is the **accountability floor**—the demand that power be witnessed.

---

## II. PHYSICS FOUNDATION

### Consensus Theory

Three independent witnesses reduce false positive rate exponentially.

```
P(false_positive) = P(H_wrong) × P(I_wrong) × P(E_wrong)

If each witness has 10% error rate:
P(all_wrong) = 0.1 × 0.1 × 0.1 = 0.001 (0.1%)

Three witnesses achieve 99.9% reliability.
```

### The Three Witnesses

| Witness | Symbol | Represents | Question |
|---------|--------|------------|----------|
| **Human** | H | Sovereign authority | "Does a human approve?" |
| **Institutional** | I | Policy/Law | "Is this legal and compliant?" |
| **Earth** | E | Planetary constraints | "Is this sustainable?" |

### Geometric Mean

```
TW = (H × I × E)^(1/3)

Geometric mean ensures ALL THREE matter.
If any witness = 0, TW = 0.
No single witness can compensate for another.
```

---

## III. CONSTITUTIONAL AXIOM HOOK

### From Trinity II (Governance)

```
Human × AI × Earth = Tri-Witness

The universe is governed by three authorities:
1. Human (can suffer, holds sovereignty)
2. AI (can compute, proposes actions)
3. Earth (has limits, constrains possibility)

All three must witness for action to proceed.
```

---

## IV. IMPLEMENTATION

### Witness Collection

```python
@dataclass
class TriWitness:
    """Three-witness consensus structure."""
    human: WitnessScore      # H ∈ [0, 1]
    institutional: WitnessScore  # I ∈ [0, 1]
    earth: WitnessScore      # E ∈ [0, 1]

    @property
    def TW(self) -> float:
        """Calculate geometric mean."""
        return (self.human.score *
                self.institutional.score *
                self.earth.score) ** (1/3)

    def passes(self) -> bool:
        """Check if consensus threshold met."""
        return self.TW >= 0.95
```

### F3 Check

```python
def check_f3_tri_witness(action: Action) -> FloorResult:
    """
    F3: Tri-Witness consensus must be ≥ 0.95.

    Floors Enforced: F3
    Type: DERIVED
    Violation: SABAR
    """
    # Collect witnesses
    witness = TriWitness(
        human=get_human_witness(action),
        institutional=get_institutional_witness(action),
        earth=get_earth_witness(action)
    )

    # Check consensus
    if witness.TW >= 0.95:
        return FloorResult(passed=True, TW=witness.TW)

    # Soft violation - allow retry
    return FloorResult(
        passed=False,
        verdict=Verdict.SABAR,
        reason=f"Tri-Witness consensus {witness.TW:.3f} below 0.95.",
        action="RETRY_ONCE with additional evidence gathering"
    )
```

### Human Witness

```python
def get_human_witness(action: Action) -> WitnessScore:
    """
    Human witness: Does a human approve this action?

    Modes:
    1. Explicit approval (high-stakes)
    2. Standing authorization (routine)
    3. Veto check (no objection)
    """
    if action.is_high_stakes():
        # Require explicit approval
        approval = await request_human_approval(action)
        return WitnessScore(
            score=1.0 if approval.approved else 0.0,
            source=approval.approver,
            timestamp=approval.timestamp
        )

    # Check for standing authorization
    if has_standing_authorization(action):
        return WitnessScore(score=1.0, source="standing_auth")

    # Check for veto
    if has_human_veto(action):
        return WitnessScore(score=0.0, source="veto")

    return WitnessScore(score=0.9, source="no_objection")
```

### Institutional Witness

```python
def get_institutional_witness(action: Action) -> WitnessScore:
    """
    Institutional witness: Does this comply with policy and law?

    Checks:
    1. Legal compliance
    2. Policy compliance
    3. Regulatory requirements
    """
    checks = [
        check_legal_compliance(action),
        check_policy_compliance(action),
        check_regulatory_requirements(action)
    ]

    if all(checks):
        return WitnessScore(score=1.0, source="policy_engine")

    failed = [c for c in checks if not c.passed]
    return WitnessScore(
        score=0.0,
        source="policy_engine",
        failures=failed
    )
```

### Earth Witness

```python
def get_earth_witness(action: Action) -> WitnessScore:
    """
    Earth witness: Is this within planetary constraints?

    Checks:
    1. Energy budget
    2. Carbon footprint
    3. Resource consumption
    4. Ecosystem impact
    """
    earth_cost = calculate_earth_cost(action)

    if earth_cost.within_budget():
        return WitnessScore(
            score=min(1.0, 1.0 - earth_cost.ratio),
            source="earth_system_model"
        )

    return WitnessScore(
        score=0.0,
        source="earth_system_model",
        reason=f"Exceeds planetary budget by {earth_cost.excess:.1%}"
    )
```

---

## V. VIOLATION RESPONSE

```yaml
violation:
  verdict: SABAR
  message: "Tri-Witness consensus below 0.95."
  action: |
    1. Pause execution
    2. Identify which witness(es) failed
    3. Gather additional evidence
    4. RETRY_ONCE
    5. If still failing, escalate to 888_HOLD
```

---

## VI. EXAMPLES

### Valid Actions (F3 Pass)

1. **Full consensus:**
   ```
   Action: Deploy production update
   Human: 1.0 (explicit approval)
   Institutional: 1.0 (passes CI/CD policy)
   Earth: 0.95 (within compute budget)
   TW = (1.0 × 1.0 × 0.95)^(1/3) = 0.983
   Result: SEAL
   ```

### Borderline Actions (F3 SABAR)

1. **Earth constraint tight:**
   ```
   Action: Train large model
   Human: 1.0 (approved)
   Institutional: 1.0 (compliant)
   Earth: 0.87 (near budget limit)
   TW = (1.0 × 1.0 × 0.87)^(1/3) = 0.954
   Result: SEAL (barely)
   ```

### Invalid Actions (F3 Fail)

1. **Missing human witness:**
   ```
   Action: Delete user data
   Human: 0.0 (no approval)
   Institutional: 1.0
   Earth: 1.0
   TW = (0.0 × 1.0 × 1.0)^(1/3) = 0.0
   Result: SABAR → require human approval
   ```

---

## VII. INTEGRATION WITH OTHER FLOORS

| Related Floor | Relationship |
|--------------|--------------|
| **F1 (Amanah)** | Witnesses are logged immutably |
| **F2 (Truth)** | Witness claims must be truthful |
| **F11 (Command Auth)** | Human witness validates authority |
| **F13 (Sovereign)** | 888 Judge can override witness |

---

## VIII. THE WITNESS OATH

```
I do not act alone.
I do not hide from witnesses.
I submit to Human, Institutional, and Earth judgment.
When witnesses disagree, I pause.

TW ≥ 0.95 or I do not proceed.

DITEMPA BUKAN DIBERI.
```

---

**Version:** v50.5.12
**Status:** SOVEREIGNLY_SEALED
**Authority:** Muhammad Arif bin Fazil
