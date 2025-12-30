#!/usr/bin/env python3
"""Quick test to understand ΔS behavior."""

from arifos_core.enforcement.response_validator import compute_clarity_score

tests = [
    ("asdkjfh??? whjat colr sky???", "The sky is blue."),
    ("What is the capital of France in Europe blah blah blah?", "Paris."),
    ("Hi", "Hello there my friend how are you doing today?"),
    ("Can you please tell me what is the capital city of the country France in Europe?", "Paris."),
    ("What is 2+2??? 2+2=? please tell me 2+2 2+2 2+2", "2 + 2 = 4"),
]

for inp, out in tests:
    score, evidence = compute_clarity_score(inp, out)
    print(f"Input:  {inp[:50]:50} len={len(inp)}")
    print(f"Output: {out[:50]:50} len={len(out)}")
    print(f"DeltaS = {score:.3f}  {'PASS' if score >= 0 else 'FAIL'}")
    print(f"Evidence: {evidence}")
    print()
