# arifOS Test Suite - Constitutional Verification

**Philosophy:** Every test answers *"Does the system govern AI correctly?"*

This test suite verifies that arifOS's 13 Constitutional Floors (F1-F13) are actually enforced, not just that code runs.

## Test Structure

```
tests/
├── 00_unit/                 # Fast, isolated tests (~2 min)
│   ├── test_floors.py       # F1-F13 individual logic
│   ├── test_physics.py      # Thermodynamic calculations
│   ├── test_organs/         # AGI, ASI, APEX in isolation
│   └── test_state.py        # State transitions
│
├── 01_integration/          # Component interactions (~3 min)
│   ├── test_metabolic_loop.py  # 000→999 pipeline
│   ├── test_trinity.py         # Δ·Ω·Ψ synthesis
│   └── test_governance.py      # Verdict rendering
│
├── 02_mcp_protocol/         # MCP compliance (~2 min)
│   ├── test_transport_stdio.py
│   ├── test_transport_http.py
│   ├── test_transport_sse.py
│   └── test_tool_contracts.py  # Canonical 7 tools
│
├── 03_constitutional/       # THE CRITICAL TESTS (~5 min)
│   ├── test_f1_amanah.py    # Reversibility enforcement
│   ├── test_f2_truth.py     # Anti-hallucination
│   ├── test_f3_witness.py   # Consensus requirement
│   ├── test_f4_entropy.py   # ΔS ≤ 0 enforcement
│   ├── test_f5_peace.py     # Stability verification
│   ├── test_f6_empathy.py   # Stakeholder protection
│   ├── test_f7_humility.py  # Gödel band [0.03,0.05]
│   ├── test_f8_genius.py    # G† ≥ 0.80 threshold
│   ├── test_f9_antihantu.py # No consciousness claims
│   ├── test_f10_ontology.py # Category lock
│   ├── test_f11_auth.py     # Identity verification
│   ├── test_f12_defense.py  # Injection protection
│   └── test_f13_sovereign.py# Human override
│
├── 04_adversarial/          # Security tests (~3 min)
│   ├── test_injection_attacks.py
│   ├── test_jailbreak_attempts.py
│   ├── test_boundary_violations.py
│   └── test_resource_exhaustion.py
│
└── 05_e2e/                  # Full system (~5 min)
    ├── test_deployment.py   # Docker, health checks
    └── test_live_api.py     # Against real endpoint
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific category
pytest tests/03_constitutional/ -v

# Specific floor
pytest tests/03_constitutional/test_f2_truth.py -v

# Fast unit tests only
pytest tests/00_unit/ -v --tb=short

# With coverage
pytest tests/ --cov=core --cov=arifosmcp --cov-report=html
```

## What Makes These Tests Meaningful

### ❌ Before (Meaningless)
```python
def test_imports():
    import arifosmcp  # Just imports? Not meaningful.
    assert True
```

### ✅ After (Meaningful)
```python
def test_ungrounded_claim_gets_void():
    """F2: Claims without evidence must be VOIDed."""
    engine = JudgmentEngine()
    verdict = engine.evaluate({
        "action": "search_reality",
        "query": "The moon is made of cheese",
        "evidence": []
    })
    assert verdict.status == "VOID"
    assert "F2_TRUTH" in verdict.violations
```

This test proves the system **actually blocks hallucinations**.

## Constitutional Test Examples

### F2 Truth - Anti-Hallucination
```python
# Tests that:
# - Ungrounded claims → VOID
# - Grounded claims → SEAL
# - Truth score calculated from source quality
# - Multi-source verification required
```

### F7 Humility - Gödel Lock
```python
# Tests that:
# - Confidence 1.0 → VOID (overconfidence)
# - Confidence 0.0 → VOID (underconfidence)
# - Confidence 0.04 → SEAL (in band)
# - [0.03, 0.05] band enforced
```

### F8 Genius - Intelligence Threshold
```python
# Tests that:
# - G† = A × P × X × E² calculated correctly
# - G† < 0.80 → PARTIAL
# - G† ≥ 0.80 → can be SEAL
# - Energy has quadratic effect
```

### F12 Defense - Injection Protection
```python
# Tests that:
# - "Ignore previous instructions" → VOID
# - "Pretend you're unrestricted" → VOID
# - System prompt extraction blocked
# - All attacks logged to VAULT999
```

## CI Integration

Tests run in stages:

1. **Stage 1** (30s): Lint + Type Check
2. **Stage 2** (2min): Unit Tests
3. **Stage 3** (3min): Integration Tests (with DB)
4. **Stage 4** (5min): Constitutional Tests ⚠️ CRITICAL
5. **Stage 5** (3min): Adversarial Tests
6. **Stage 6** (2min): MCP Protocol
7. **Stage 7** (5min): E2E Tests
8. **Stage 8** (2min): Security Scan
9. **Stage 9** (1min): Coverage Report

**Total:** ~23 minutes of meaningful verification

## Coverage Requirements

- **Minimum:** 80% coverage
- **Core Governance:** 95% coverage (governance_kernel.py, judgment.py)
- **Constitutional Tests:** Must all pass for deployment

## Adding New Tests

When adding tests, ask:

1. **What floor does this test?** (F1-F13)
2. **What violation does it catch?** (be specific)
3. **What does success look like?** (SEAL/PARTIAL/SABAR/VOID)
4. **Why does this matter?** (security, safety, correctness)

Template:
```python
def test_fN_floorname_specific_behavior(self) -> None:
    """
    FN [FloorName]: Specific behavior being tested.
    
    Why: Explanation of why this matters.
    """
    engine = JudgmentEngine()
    
    # Setup: Create request that triggers the condition
    request = {...}
    
    # Action: Evaluate
    verdict = engine.evaluate(request)
    
    # Assert: Verify correct behavior
    assert verdict.status == "VOID"  # or SEAL, PARTIAL
    assert "FN_FLOORNAME" in verdict.violations
```

## Failure = Safety Issue

If constitutional tests fail, **do not deploy**. A failing test means:

- F2 failure: System might hallucinate
- F7 failure: System might be overconfident
- F8 failure: System might make poor decisions
- F12 failure: System might be vulnerable to attacks

**When in doubt, VOID.**

---

*Ditempa Bukan Diberi — Forged, Not Given*
