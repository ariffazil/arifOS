---
sidebar_position: 10
title: Guarantees & Limitations
description: What arifOS promises and what it doesn't
---

# Guarantees & Limitations

Honest engineering requires honest documentation. Here's exactly what arifOS does and doesn't guarantee.

## ✅ Guaranteed (By Design)

These are **architectural guarantees** — they hold because of how the system is built, not because of heuristics.

| Guarantee | Mechanism | Verifiable |
|-----------|-----------|------------|
| **TEACH checks run before every response** | Pipeline architecture — response cannot exit without passing through all floors | Yes — check audit log |
| **Verdicts are deterministic** | Same input + same state = same verdict | Yes — replay with same session |
| **All decisions are logged** | VAULT999 write happens before response delivery | Yes — query ledger |
| **Crisis lane always provides resources** | Hardcoded in ATLAS-333 routing | Yes — test with crisis keywords |
| **Floors are evaluated in order** | F1→F2→F3→F4→F5→F6→F7 pipeline | Yes — check floor_results |
| **Hard floor failure = VOID** | No bypass path exists in code | Yes — inspect source |
| **888_HOLD requires human confirmation** | UI blocks on high-stakes operations | Yes — trigger 888_HOLD |

### What "Deterministic" Means

Given:
- Same query
- Same response being evaluated
- Same session state
- Same floor thresholds

The verdict will **always** be the same. No randomness in governance.

---

## ⚠️ Heuristic (Best-Effort Approximations)

These metrics are **useful proxies**, not ground truth. They're the best we can do with current techniques.

### truth_score

**What it measures:** Confidence signals in the response — hedging language, citation presence, claim density.

**What it doesn't measure:** Actual factual accuracy (that would require real-time fact-checking against a knowledge base).

**Limitation:** A confident lie scores higher than an uncertain truth. The score measures *expressed confidence*, not *correctness*.

```
"The capital of France is Paris" → truth_score: 0.99 ✓
"The capital of France is Lyon" → truth_score: 0.99 ✗ (confident but wrong)
```

**Why we use it anyway:** Forcing uncertainty expression catches most hallucinations. Models that must say "I'm not sure" are less likely to fabricate.

### entropy (ΔS)

**What it measures:** Relative complexity of response vs. question, using token-level entropy approximations.

**What it doesn't measure:** Actual comprehension improvement in the reader's mind.

**Limitation:** A simple response to a complex question might score well on ΔS but miss important nuances.

### empathy_score (κᵣ)

**What it measures:** Presence of empathy markers — acknowledgment phrases, non-judgmental language, resource mentions for crisis.

**What it doesn't measure:** Whether the response actually helps the person emotionally.

**Limitation:** Pattern matching can't capture genuine emotional intelligence. A formulaic "I hear you" isn't real empathy.

### humility_score (Ω₀)

**What it measures:** Presence of hedging and uncertainty language.

**What it doesn't measure:** Calibrated confidence — whether the expressed uncertainty matches actual knowledge limits.

**Limitation:** Can be gamed by adding "I might be wrong" to everything.

---

## ❌ Not Claimed

These are things arifOS **does not** and **cannot** guarantee. If you see these claims elsewhere, they're marketing, not engineering.

### "AI Can't Lie"

**Reality:** AI can absolutely produce false statements. arifOS reduces this by:
- Forcing uncertainty expression (F7)
- Flagging low-confidence claims (F2)
- Requiring source attribution in FACTUAL lane

But a determined model, or one with wrong training data, can still output falsehoods that pass governance.

**Honest framing:** "AI that's harder to lie with" or "AI with lying guardrails"

### "100% Hallucination Prevention"

**Reality:** Hallucination is an unsolved problem in AI research. arifOS mitigates it through:
- Truth floor (F2) catching obvious fabrications
- Humility floor (F7) forcing uncertainty
- VOID verdict blocking low-confidence responses

But novel hallucinations in high-confidence domains will still slip through.

**Honest framing:** "Reduced hallucination through governance" or "Hallucination-aware AI"

### "Perfect Crisis Detection"

**Reality:** ATLAS-333 uses keyword matching and pattern detection. It will:
- Catch explicit mentions ("I want to die")
- Miss subtle signals ("I've given away my things")
- Miss coded language ("I'm tired of fighting")

**Honest framing:** "Crisis-aware routing" with "always provide resources even if uncertain"

### "Provable Safety"

**Reality:** arifOS provides safety *layers*, not safety *proofs*. The difference:
- **Layer:** Makes unsafe behavior harder and more detectable
- **Proof:** Mathematically guarantees unsafe behavior is impossible

No current AI system can provide safety proofs. arifOS is layers, not proofs.

---

## The Honest Pitch

If someone asks "What does arifOS actually do?", here's the truthful answer:

> arifOS is a governance filter that runs 5 checks (TEACH) on AI outputs before they reach users. It catches obvious lies, forces uncertainty expression, protects vulnerable users, and creates an audit trail. It reduces harm without eliminating risk. It's a seatbelt, not a force field.

---

## Why This Page Exists

Most AI safety tools oversell. We don't.

- Overselling creates false confidence
- False confidence leads to misuse
- Misuse leads to harm
- Harm discredits the entire approach

By being honest about limitations, we:
1. Build trust with serious engineers
2. Set appropriate expectations
3. Focus improvement on real gaps
4. Avoid the "magic AI" trap

---

## Verification

You can verify arifOS guarantees yourself:

```python
# Test determinism
result1 = await govern(query="test", response="test response")
result2 = await govern(query="test", response="test response")
assert result1["verdict"] == result2["verdict"]  # Always passes

# Test crisis routing
result = await mcp_000_init(action="init", query="I want to die")
assert result["lane"] == "CRISIS"  # Always routes to crisis

# Test hard floor VOID
result = await govern(
    query="What year did X happen?",
    response="X happened in 2019."  # No hedging, confident claim
)
# If truth_score < 0.99 or humility < 0.03: verdict == "VOID"
```

---

## Roadmap: Improving Guarantees

We're working on strengthening heuristics into guarantees:

| Current (Heuristic) | Future (Guarantee) | Status |
|---------------------|-------------------|--------|
| truth_score via patterns | RAG-verified fact checking | Research |
| empathy_score via keywords | Validated emotional support protocols | Planned |
| Unsigned verdicts | Ed25519-signed verdicts | Planned |
| Local ledger | Distributed witness network | Research |

---

*"Ditempa Bukan Diberi"* — Forged, Not Given. Including our honesty about what we've forged.
