# arifOS MCP TOOL BENCHMARK REPORT
**Date:** 2026-04-14  
**Operator:** Arif  
**System:** arifOS v2026.4.14 — SEALED

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Tools Tested** | 11 canonical MCP tools |
| **Passed** | 8 (72.7%) |
| **Failed** | 3 (27.3%) |
| **Average Latency** | 764.6ms |
| **Best Performer** | arifos_probe (0.02ms) |
| **Worst Performer** | arifos_memory (8055.8ms) |

---

## BENCHMARK RESULTS — RANKED BY SCORE

| Rank | Tool | Status | Latency (ms) | Verdict | Score |
|------|------|--------|--------------|---------|-------|
| 1 | arifos_health | PASS | 0.6 | SEAL | 224.9 |
| 2 | arifos_probe | PASS | 0.0 | SEAL | 220.0 |
| 3 | arifos_ops | PASS | 0.3 | SEAL | 220.0 |
| 4 | arifos_heart | PASS | 12.6 | SEAL | 218.7 |
| 5 | arifos_judge | PASS | 47.1 | SEAL | 215.3 |
| 6 | arifos_vault | PASS | 1.5 | SABAR | 199.9 |
| 7 | arifos_init | PASS | 293.0 | SEAL | 185.7 |
| 8 | arifos_memory | PASS | 8055.8 | SABAR | 100.0 |
| 9 | arifos_sense | FAIL | 0.0 | VOID | 50.0 |
| 10 | arifos_mind | FAIL | 0.0 | VOID | 50.0 |
| 11 | arifos_kernel | FAIL | 0.0 | VOID | 50.0 |

---

## TOOL ANALYSIS

### ✅ PASSING TOOLS (8)

#### 1. arifos_health — Score: 224.9
- **Latency:** 0.6ms (fastest governance tool)
- **Verdict:** SEAL
- **Floors Passed:** F12 (Anti-Hantu)
- **Assessment:** Ultra-fast read-only telemetry. F12-hardened. Excellent for health checks.

#### 2. arifos_probe — Score: 220.0
- **Latency:** 0.02ms (fastest tool overall)
- **Verdict:** SEAL
- **Assessment:** Near-instant system diagnostic. Minimal overhead.

#### 3. arifos_ops — Score: 220.0
- **Latency:** 0.3ms
- **Verdict:** SEAL
- **Assessment:** Thermodynamic cost estimator. Extremely fast operation.

#### 4. arifos_heart — Score: 218.7
- **Latency:** 12.6ms
- **Verdict:** SEAL
- **Assessment:** Safety/critique tool. Constitutional red-teaming. Good latency.

#### 5. arifos_judge — Score: 215.3
- **Latency:** 47.1ms
- **Verdict:** SEAL
- **Assessment:** Sovereign verdict rendering. Reasonable latency for constitutional evaluation.

#### 6. arifos_vault — Score: 199.9
- **Latency:** 1.5ms
- **Verdict:** SABAR (partial)
- **Assessment:** Immutable ledger append. Fast but returned SABAR (needs review).

#### 7. arifos_init — Score: 185.7
- **Latency:** 293.0ms
- **Verdict:** SEAL
- **Floors Passed:** F11, F12, F13
- **Assessment:** Constitutional session ignition. Passes 3 floors. Higher latency due to identity binding.

#### 8. arifos_memory — Score: 100.0
- **Latency:** 8055.8ms (slowest by far)
- **Verdict:** SABAR (partial)
- **Issues:** Qdrant/Ollama unavailable, fell back to degraded mode
- **Assessment:** Constitutional vector memory. Works but slow without live vector DB.

---

### ❌ FAILING TOOLS (3)

#### arifos_sense — Score: 50.0
- **Error:** `'RuntimeEnvelope' object has no attribute 'get'`
- **Verdict:** VOID
- **Floors Failed:** F2 (Truth)
- **Issue:** RuntimeEnvelope return type mismatch — code expects dict-like interface

#### arifos_mind — Score: 50.0
- **Error:** `'RuntimeEnvelope' object has no attribute 'get'`
- **Verdict:** VOID
- **Floors Failed:** F2 (Truth)
- **Issue:** Same RuntimeEnvelope interface problem

#### arifos_kernel — Score: 50.0
- **Error:** `cannot import name 'get_tool_handler' from 'arifosmcp.runtime.tools_hardened_dispatch'`
- **Verdict:** VOID
- **Floors Failed:** F4 (ΔS Clarity)
- **Issue:** Missing import in hardened dispatch layer

---

## SCORING METHODOLOGY

```
Total Score = Latency Score (0-100) + Correctness (0-100) + Verdict Bonus (+20 for SEAL/PARTIAL) + Floor Compliance (+5 per floor) - Error Penalty (-50)
```

| Component | Weight | Description |
|------------|--------|-------------|
| Latency Score | max 100 | 100 - (latency_ms / 10) |
| Correctness | 0 or 100 | PASS = 100, FAIL = 0 |
| Verdict Bonus | +20 | SEAL or PARTIAL verdicts |
| Floor Compliance | +5 each | Each floor passed |
| Error Penalty | -50 | If any error occurred |

---

## ISSUES FOUND

### Critical Issues
1. **arifos_kernel** — Missing import `get_tool_handler` in hardened dispatch
2. **arifos_sense/arifos_mind** — RuntimeEnvelope type mismatch (expects dict interface)

### Degraded Mode Issues
- **arifos_memory** — Qdrant vector DB unavailable, falls back to degraded mode
- **arifos_vault** — Returns SABAR instead of SEAL (likely needs human ratification)

### Environment Issues
- Qdrant (vector DB) not running — `getaddrinfo failed`
- Ollama (embeddings) not available — `getaddrinfo failed`

---

## RECOMMENDATIONS

1. **Fix arifos_kernel import** — Add `get_tool_handler` to `tools_hardened_dispatch.py`
2. **Fix RuntimeEnvelope** — Ensure consistent dict-like interface for arifos_sense/arifos_mind
3. **Start Qdrant** — Enable full vector memory functionality
4. **Start Ollama** — Enable embeddings for memory/sense tools

---

## TESTING METHODOLOGY

- **Approach:** Direct async Python calls to canonical tool handlers
- **Environment:** Windows (arifOS VPS), Python 3.11+
- **Timeout:** 30 seconds per tool
- **Timestamp:** 2026-04-14T12:38:03 UTC

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**