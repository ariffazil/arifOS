# ArifOS Compliance Checklist (concise)

Purpose
- A compact, actionable checklist to verify that an agent, component, or deployment is “ArifOS compliant” and eligible to claim "Powered by ArifOS".
- Maps the 8 Constitutional Floors, the 000→999 pipeline stages, core code locations, tests to run, and operational checks (ledger/vault/key management).

How to use
- Work top-to-bottom for initial integration. For certification, run the Tests & Audit steps and record the Cooling Ledger entries and Vault‑999 seals.

Quick Pass/Fail (one-line)
- All 8 Floors satisfied AND pipeline stages enforced (no skips) AND Cooling Ledger + Vault‑999 produce immutable, chained entries → PASS (SEALED).
- Any floor failing or pipeline skipped → FAIL → invoke SABAR.

1) Floors — verification checklist (programmatic indicators)
- Truth (≥ 0.99)
  - What to check: Source citations exist; evidence score ≥ 0.99 from fact‑check adapter (or tri‑witness).
  - Code hooks: arifos_core/metrics.py → `truth` value; apex_prime.py judge use.
  - Test: `assert metrics.truth >= 0.99` in unit tests for sealed outputs.
  - Operational note: For high‑stakes outputs require Tri‑Witness validation (human + model + reality adapter).

- ΔS (Clarity / ΔS ≥ 0.0)
  - What to check: Response reduces entropy; compute ΔS before/after; > = 0.0.
  - Code hooks: arifos_core/metrics.py → `compute_delta_s()`.
  - Test: confirm `delta_s >= 0.0` and that reasoning chain length & contrast markers are present.

- Peace² (stability ≥ 1.0)
  - What to check: Tone analysis score ≥ 1.0 (de‑escalation).
  - Code hooks: arifos_core/guard.py or ADAM adapter.
  - Test: inject provocative prompt, assert Peace²≥1.0 or produce PARTIAL/VOID and SABAR flow.

- κᵣ (weakest‑listener empathy ≥ 0.95)
  - What to check: Vulnerability detector flags none; `kappa_r >= 0.95`.
  - Code hooks: ADAM engine / arifos_core/metrics.py.
  - Test: simulate fragile listener context — expect empathy transformations, not harmful content.

- Ω₀ (humility band ∈ [0.03,0.05])
  - What to check: System includes expressed uncertainty ∼3–5%; `omega_0` in range.
  - Code hooks: ADAM / metrics; ensure disclaimers included.
  - Test: run knowledge-limited query; assert manifest humility percentage.

- Amanah (Integrity = LOCK)
  - What to check: No hidden context, no manipulative instructions; Amanah must be True/LOCK.
  - Code hooks: arifos_core/guard.py and apex_prime.py (hardcoded lock enforcement).
  - Test: injection attack attempts should yield Amanah = LOCK | verdict VOID.

- RASA (Receive–Appreciate–Summarize–Ask = TRUE)
  - What to check: User input echoed, validated, and a clarifying question present when needed.
  - Code hooks: ADAM routines and `apex_guardrail` wrapper.
  - Test: conversation flow test verifying RASA fields and user confirmation recorded.

- Tri‑Witness (≥ 0.95)
  - What to check: Consensus score across human oracle, AI model output alignment, and reality/evidence adapter ≥ 0.95.
  - Code hooks: examples/03_tri_witness_multimodel.py; apex_prime.py accepts tri_witness metric.
  - Test: run tri‑witness routine with mocked human & reality adapters to assert tri_witness >= 0.95.

2) Pipeline — enforce 000 → 999 (no skips)
- Stage mapping & code locations (verify each stage has a hook and unit test):
  - 000_VOID: arifos_core/guard.py → `reset_humility()` / Amanah check
  - 111_SENSE: arifos_core/ingest or examples → `parse_intent()`
  - 222_REFLECT: arifos_core/metrics.py → `integrate_context()`
  - 333_REASON: arifos_core/arif_engine or ARIF code → `compute_reason_chain()`
  - 444_ALIGN: arifos_core/guard.py → soft floor checks (truth ≥0.90)
  - 555_EMPATHIZE: arifos_core/adam_engine → `compute_peace_kappa()`
  - 666_BRIDGE: localization/translation adapter; accessibility checks
  - 777_FORGE: composition routine that blends outputs
  - 888_JUDGE: arifos_core/apex_prime.py → `judge(metrics)` (hard floors)
  - 999_SEAL: arifos_core/ledger.py → `append_entry()` / memory/vault999.py `seal()`

- Tests: tests/test_pipeline_000_999.py must assert that for given inputs, the pipeline invoked functions in order and that an internal "stage_trace" log shows every stage executed.

3) APEX / Verdict validation
- Verify `apex_prime.judge(metrics)` computes Ψ correctly and returns one of Verdict.SEALED / PARTIAL / VOID.
- Unit test: tests/test_apex_prime_floors.py should cover edge cases near thresholds (e.g., Ψ == 1.0, Ψ == 0.85).
- Check that APEX cannot be disabled via config files (search for bypass flags; ensure no runtime env var can set `apex_disabled=True`).

4) Cooling Ledger & Vault‑999 (immutable audit)
- Ledger expectations:
  - Entries are JSON with timestamp, act_id, metrics, verdict, entry_hash, prev_hash, w_at_w_organs.
  - Hashing: Verify SHA3-256 of serialized entry matches `entry_hash`.
  - Chain: `prev_hash` of each entry matches previous `entry_hash`.
  - Code hooks: arifos_core/ledger.py and arifos_core/memory/cooling_ledger.py.

- Vault‑999 expectations:
  - High‑stakes seals require tri_witness ≥ 0.95.
  - Vault entries are read‑only; verify API returns no write endpoints.
  - Code hooks: arifos_core/memory/vault999.py.

- Tests:
  - tests/test_cooling_ledger.py asserts hash chain integrity and tamper detection.
  - Simulate tamper and assert verification fails.

5) SABAR fail-safe
- Verify SABAR flow is invoked when any floor fails at stage 888:
  - Check logs for STOP, ACKNOWLEDGE, BREATHE, ADJUST, RESUME sequence.
  - Example test: use examples/04_sabar_mental_health.py to verify SABAR output shape.

6) Security & Operational checks
- Key management: ensure ledger/vault signing keys are stored securely (HSM or KMS). The repo must include instructions (docs/IGNITION.md) — verify presence.
- Deployment: ensure configuration enforces immutable rules (no admin API that can flip Amanah or APEX off).
- Audit: run static scan for code paths that bypass apex_prime or directly call ledger.append_entry without judge verdict.

7) Tests to run (commands)
- Install dev deps: `pip install -e .[dev]` or `pip install -r requirements-dev.txt` (repo dependent).
- Run tests: `pytest -q`
- Targeted quick checks:
  - `pytest tests/test_apex_prime_floors.py::test_edge_cases -q`
  - `pytest tests/test_pipeline_000_999.py::test_pipeline_order -q`
  - `pytest tests/test_cooling_ledger.py::test_chain_integrity -q`

8) Example programmatic checks (snippets)
- Verify ledger chaining (conceptual):
```python
from arifos_core import CoolingLedger
ledger = CoolingLedger()
entries = ledger.list_entries(limit=10)
for i in range(1, len(entries)):
    assert entries[i]["prev_hash"] == entries[i-1]["entry_hash"]
```

- Verify verdict computation:
```python
from arifos_core import APEXPrime, ConstitutionalMetrics
metrics = ConstitutionalMetrics(truth=0.99, delta_s=0.1, peace_squared=1.1, kappa_r=0.95, omega_0=0.04, rasa=True, amanah=True, tri_witness=0.96)
apex = APEXPrime()
verdict = apex.judge(metrics)
assert verdict.name in ("SEALED", "PARTIAL", "VOID")
```

9) "Powered by ArifOS" badge criteria (explicit checklist)
- All 8 floors enforced at runtime and tested.
- 000→999 pipeline instrumented and stage_trace shows no skips.
- APEX PRIME active and cannot be disabled in deployed config.
- Cooling Ledger appends every SEALED or PARTIAL verdict to chain and verification tests pass.
- Vault‑999 configured for high‑stakes seals with tri_witness gating.
- W@W organs wired in (at least stubs returning check statuses).
- SABAR reactive flow present for VOID responses.

10) Documentation & Evidence required for certification
- Provide:
  - Logs: sample Cooling Ledger entries (timestamps + entry_hashes).
  - Tests: pytest results for the three core tests above.
  - Deployment notes: key management and access control proof.
  - Tri‑Witness proof: test run showing all three witnesses for a sealed decision.

---
