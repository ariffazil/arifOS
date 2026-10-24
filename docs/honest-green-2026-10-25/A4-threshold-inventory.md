# A4 — F1–F13 Threshold Inventory (branch fix/honest-green-2026-10-25)

observed_at: 2026-10-24T18:55Z. READ-ONLY inventory. NO value chosen — the
decision belongs to Arif (Lane B5).

## Proposed single source (proposal only)
Promote `core/shared/laws.py` → `LAW_SPECS` (the machine table actually used by
`get_floor_spec()` / `get_law_threshold()` / `_floor_passes()`) into a ratified
contract file **`contracts/floor_policy.yaml`** (sibling of the already-ratified
`contracts/fq_policy.yaml`), with every other table below referenced/derived from
it. Values unchanged in this branch; reconciliation is B5.

## The machine source
`core/shared/laws.py` `LAW_SPECS` (lines 46-93), reached via
`get_floor_spec()` (laws.py:189) and `get_law_threshold()` (laws.py:197),
consumed by `rest_routes._floor_passes` (rest_routes.py:299/570/740).

## Every disagreement found

| Floor | Machine (core/shared/laws.py) | Other definitions | Disagreement |
|---|---|---|---|
| F3 | **0.75** (`F3_QuadWitness`, laws.py:48-50) | Rest-rendered doctrine table **≥0.95** (rest_routes.py:2321); `models/verdicts.py:143` `w3_min = 0.95` (SEAL gate "W³ ≥ 0.95", verdicts.py:45) | **TRIPLE: 0.75 vs 0.95 vs 0.95.** Live F3 = 0.9385 marked PASS → proves the BINDING value today is ≤0.9385 (0.75). Under the table/verdicts 0.95 it would FAIL. The audit's "0.94/0.95" dispute: machine passes it, doctrine says fail. |
| F2 | 0.99 (laws.py:47) | Table ≥0.99 ✓ (rest_routes.py:2320); **TRM signal threshold 0.94 tagged `floor: "F2"`** (runtime/tools.py:10631, megaTools/tool_01_init_anchor.py:483) | 0.94 literal wearing the F2 floor tag (0.94 ≠ 0.99) — tag/scope ambiguity |
| F8 | 0.80 (laws.py:67) | `verdict.py` compose G-gates: SEAL 0.80 / SABAR 0.50 / DEGRADED 0.30; table row F8 has **no number** ("Delta-logged", rest_routes.py:2326) | 0.80 aligned with G_SEAL ✓; table declares no threshold (informational gap) |
| F1 | 0.5 (laws.py:46) | fq_policy.yaml `healthy_min/observe_only_below 0.5` (F13-ratified 2026-09-12) ✓; table ≥0.50 ✓ | aligned |
| F5 | 1.00 (laws.py:58) | Table ≥1.0 ✓; but LIVE F5 is produced by the seal-chain producer (floor_producers._f5_peace), not the numeric score | producer path vs score path (which one gates is implicit) |
| F6 | 0.70 κᵣ (laws.py:59) | Table row: "VOID check" (no number, rest_routes.py:2324); live F6 = unmeasured_default | number vs no-number; unmeasured anyway |
| F4 | 0.00 (laws.py:55, ≤0) | Table ≤0 ✓ | aligned |
| F9 | 0.30 (laws.py:72) | Table <0.30 ✓ (rest_routes.py:2327) | aligned |
| F7 | 0.85 confidence cap (laws.py:83) | Table "0.85 ceiling" ✓ | aligned |
| F2 coverage axis | `floor_producers.COVERAGE_THRESHOLD = 0.5` (floor_producers.py:37) | separate axis (evidence-source coverage, not the 0.99 score) | name-adjacent, document not merge |

Downstream consumers that must follow the single source once ratified:
`rest_routes._floor_passes` / rendered table (rest_routes.py:2319-2327),
`models/verdicts.py` (w3_min), `verdict.py` (G gates), megaTools TRM (0.94 tag),
`contracts/fq_policy.yaml` (0.5 floor), floor_producers (COVERAGE 0.5).

## Decision rows for Arif (B5 — DO NOT auto-resolve)
1. Which file is SOT: proposed `contracts/floor_policy.yaml` vs keep `core/shared/laws.py`?
2. F3: 0.75 (machine, live behaviour) vs 0.95 (doctrine table + verdicts.py) — pick one.
3. TRM 0.94: retag (not-F2) or retune to 0.99 — pick one.
