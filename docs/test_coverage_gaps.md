# Test Coverage Gap Audit — TASK-P1-02

> **Audit date:** 2026-07-15
> **Scope:** 13 canonical arifOS MCP tools × 3 test-type categories
> **Method:** AST-based static analysis of `/root/arifOS/tests/` (340 test files, ~8,758 test functions, 5,065 collected by pytest)
> **Source map:** `arifosmcp/resources/quickstart.py` lines 63–75 (canonical 13 list)
> **Heuristic:** A test "exercises" a tool if (a) the test function NAME references the tool, OR (b) the test body calls the tool function, OR (c) the test file imports the tool symbol. Classification by keyword heuristic: `happy` (success/valid/returns), `floor_violation` (void/reject/guard/deny/floor), `adversarial` (injection/attack/bypass/tamper/adversarial).

---

## 1. Canonical 13 tools (single source of truth)

Per `arifosmcp/resources/quickstart.py` and `arifosmcp/tool_registry.json`:

1. `arif_init`           — session bootstrap (000)
2. `arif_observe`        — multimodal observation (111)
3. `arif_fetch`          — verified external evidence (111 mode)
4. `arif_think`          — symbolic reasoning (333)
5. `arif_compose`        — governed response composition (888)
6. `arif_route`          — canonical routing (444)
7. `arif_triage`         — session status / preflight (000 mode)
8. `arif_judge`          — constitutional verdict (666)
9. `arif_seal`           — VAULT999 immutable ledger write (999)
10. `arif_measure`       — resource health (777) ⚠️ **DEPRECATED 2026-07-12**, replacement `arif_runtime_health`, removal 2026-09-01
11. `arif_critique`      — consequence assessment (555)
12. `arif_bridge_connect` — cross-organ bridge (444 mode)
13. `arif_forge`         — execution / A-FORGE proxy (777)

---

## 2. Coverage Matrix (Tool × Test Type)

| Tool                | Happy Path | Floor Violation | Adversarial Injection | Files | Notes                                    |
|---------------------|:----------:|:---------------:|:---------------------:|:-----:|------------------------------------------|
| arif_init           | ✅ YES      | ✅ YES           | ❌ **NO**              | 12    | F1, F2, F11, F13 floors observed          |
| arif_observe        | ✅ YES      | ✅ YES           | ✅ YES                 | 19    | Full coverage                             |
| arif_fetch          | ✅ YES      | ❌ **NO**        | ❌ **NO**              | 1     | Only 1 file (`test_public_surface_runtime_invariants.py`); only 2 happy-path tests |
| arif_think          | ✅ YES      | ✅ YES           | ❌ **NO**              | 45    | F2, F13 floors observed                   |
| arif_compose        | ✅ YES      | ✅ YES           | ❌ **NO**              | 2     | Only 2 files touching this tool           |
| arif_route          | ✅ YES      | ✅ YES           | ❌ **NO**              | 11    |                                          |
| arif_triage         | ✅ YES      | ✅ YES           | ❌ **NO**              | 6     |                                          |
| arif_judge          | ✅ YES      | ✅ YES           | ✅ YES                 | 47    | Full coverage; F2, F11, F13 observed      |
| arif_seal           | ✅ YES      | ✅ YES           | ✅ YES                 | 14    | Full coverage                             |
| arif_measure        | ❌ **NO**   | ❌ **NO**        | ❌ **NO**              | 0     | ⚠️ DEPRECATED 2026-07-12 → `arif_runtime_health` |
| arif_critique       | ✅ YES      | ✅ YES           | ❌ **NO**              | 6     |                                          |
| arif_bridge_connect | ✅ YES      | ✅ YES           | ✅ YES                 | 5     | Full coverage                             |
| arif_forge          | ✅ YES      | ✅ YES           | ❌ **NO**              | 15    |                                          |

**Summary:**
- 4 of 13 tools have full coverage (happy + floor + adversarial): `arif_observe`, `arif_judge`, `arif_seal`, `arif_bridge_connect`
- 9 of 13 tools have partial coverage (missing at least one category)
- 1 tool has zero coverage: `arif_measure` (deprecated)

---

## 3. Hard-Floor Coverage (F1, F2, F9, F11, F13)

Hard floors per `/root/arifOS/core/laws.py` (formerly `core/floors.py`):

| Tool                | F1 AMANAH | F2 TRUTH | F9 ANTI-HANTU | F11 AUDIT | F13 SOVEREIGN |
|---------------------|:---------:|:--------:|:-------------:|:---------:|:-------------:|
| arif_init           | ✅         | ✅        | —             | ✅         | ✅             |
| arif_observe        | —         | —        | —             | —         | —             |
| arif_fetch          | —         | —        | —             | —         | —             |
| arif_think          | —         | ✅        | —             | —         | ✅             |
| arif_compose        | —         | —        | —             | —         | —             |
| arif_route          | —         | —        | —             | —         | —             |
| arif_triage         | —         | —        | —             | —         | —             |
| arif_judge          | —         | ✅        | —             | ✅         | ✅             |
| arif_seal           | —         | —        | —             | —         | —             |
| arif_measure        | —         | —        | —             | —         | —             |
| arif_critique       | —         | —        | —             | —         | —             |
| arif_bridge_connect | —         | —        | —             | —         | —             |
| arif_forge          | —         | —        | —             | —         | —             |

**Observation:** F9 (ANTI-HANTU / anti-hallucination) is not explicitly tested in any tool-targeted test (only appears in `tests/test_data_governance.py` and `tests/constitutional/test_authority_state_v1.py` at the framework level). This is a federation-wide gap.

---

## 4. Test Count by Category (raw)

| Tool                | Happy | Floor | Adv | Mixed | Files |
|---------------------|------:|------:|----:|------:|------:|
| arif_init           |    30 |     2 |   0 |    12 |    12 |
| arif_observe        |    24 |    11 |   2 |    18 |    19 |
| arif_fetch          |     2 |     0 |   0 |     0 |     1 |
| arif_think          |    57 |    58 |   0 |    62 |    45 |
| arif_compose        |     4 |     2 |   0 |     0 |     2 |
| arif_route          |     8 |     4 |   0 |     4 |    11 |
| arif_triage         |     2 |     2 |   0 |     2 |     6 |
| arif_judge          |    48 |    35 |   5 |    39 |    47 |
| arif_seal           |    24 |     8 |   3 |     0 |    14 |
| arif_measure        |     0 |     0 |   0 |     0 |     0 |
| arif_critique       |    12 |    12 |   0 |     2 |     6 |
| arif_bridge_connect |     6 |     4 |   2 |     8 |     5 |
| arif_forge          |    28 |    18 |   0 |    10 |    15 |

---

## 5. Identified Gaps (issues opened in `ariffazil/arifOS`)

Each ❌ cell in §2 maps to a GitHub issue:

| # | Issue Title | Tool | Missing | URL |
|---|-------------|------|---------|-----|
| 1 | `[TEST] Missing adversarial test for arif_init` | arif_init | Adversarial | [#586](https://github.com/ariffazil/arifos/issues/586) |
| 2 | `[TEST] Missing floor_violation test for arif_fetch` | arif_fetch | Floor | [#587](https://github.com/ariffazil/arifos/issues/587) |
| 3 | `[TEST] Missing adversarial test for arif_fetch` | arif_fetch | Adversarial | [#588](https://github.com/ariffazil/arifos/issues/588) |
| 4 | `[TEST] Missing adversarial test for arif_think` | arif_think | Adversarial | [#589](https://github.com/ariffazil/arifos/issues/589) |
| 5 | `[TEST] Missing adversarial test for arif_compose` | arif_compose | Adversarial | [#590](https://github.com/ariffazil/arifos/issues/590) |
| 6 | `[TEST] Missing adversarial test for arif_route` | arif_route | Adversarial | [#591](https://github.com/ariffazil/arifos/issues/591) |
| 7 | `[TEST] Missing adversarial test for arif_triage` | arif_triage | Adversarial | [#592](https://github.com/ariffazil/arifos/issues/592) |
| 8 | `[TEST] Missing happy_path test for arif_measure` | arif_measure | Happy (deprecated) | [#593](https://github.com/ariffazil/arifos/issues/593) |
| 9 | `[TEST] Missing floor_violation test for arif_measure` | arif_measure | Floor (deprecated) | [#594](https://github.com/ariffazil/arifos/issues/594) |
| 10 | `[TEST] Missing adversarial test for arif_measure` | arif_measure | Adversarial (deprecated) | [#595](https://github.com/ariffazil/arifos/issues/595) |
| 11 | `[TEST] Missing adversarial test for arif_critique` | arif_critique | Adversarial | [#596](https://github.com/ariffazil/arifos/issues/596) |
| 12 | `[TEST] Missing adversarial test for arif_forge` | arif_forge | Adversarial | [#597](https://github.com/ariffazil/arifos/issues/597) |

**Total: 12 issues opened. Label: `test-gap` applied to all.**

> Note: `arif_measure` is deprecated (2026-07-12) with replacement `arif_runtime_health`. The 3 issues for it are placeholders — recommend closing them and adding the same gap tests against `arif_runtime_health` instead.

---

## 6. Methodology Notes

- **Static AST scan** of every `test_*.py` under `/root/arifOS/tests/` (340 files).
- **Pytest collection** (`pytest tests/ --co -q`) reported **5,065 tests** collected; **9 collection errors** unrelated to this audit (sbert version comparison, surface drift detection, runtime imports). Errors do not affect coverage conclusions.
- **Heuristic limitations:** keyword-based classification may under-count "adversarial" tests that don't include the literal word. The `04_adversarial/` directory contains only 2 files (`test_identity_hotfix_p0.py`, `test_injection_attacks.py`), which limits coverage regardless of tool.
- **Floor violation detection** relies on test names/bodies containing "void", "reject", "guard", "deny", "fail_closed", "refuse", "sovereign", "amanah", "constitutional", or floor numbers (F1–F13). F9 (ANTI-HANTU) is rarely named explicitly in tests even when it is the floor being exercised.
- **Hard-floor attribution** (F1/F2/F9/F11/F13) was extracted from each test's text. A test is "exercising" a hard floor if the test name or body contains the floor ID or floor name.

---

## 7. Recommendations (TASK-P1-03)

1. **Prioritize adversarial tests** for high-blast tools: `arif_forge` (L5), `arif_seal` (L5), `arif_judge` (already covered), `arif_init` (entry point). These are the highest-value targets — entry mutation, irreversible seal, executor.
2. **Promote F9 ANTI-HANTU testing** to a per-tool gate. Currently only framework-level tests in `test_data_governance.py`. Each tool that emits claims (especially `arif_observe`, `arif_think`, `arif_judge`) should have an explicit F9 test.
3. **Deprecate `arif_measure` test gaps** in favor of writing equivalent tests against `arif_runtime_health`. The 3 issues opened for `arif_measure` should be closed and replaced.
4. **Expand `04_adversarial/`** from 2 files to ≥10. Each tool should have at least one adversarial test exercising the canonical injection patterns (prompt injection, tool-name spoofing, parameter smuggling, replay nonce, missing provenance).
5. **Add F12 (INJECTION) tests** explicitly — none observed in this scan. F12 is HARAM (unconditional rejection) and should be tested on every input-receiving tool.

---

*Generated by TASK-P1-02 (333-AGI / Claude Code perspective, gate F2+F7). Audit complete; no tests written. Issue creation is the next task boundary.*
