# Reproducibility Contract — Clean-Room Trace Reproduction

> Implements the "External clean-room trace reproduction" threshold in
> `observability-contract.md`. Until an external party passes this test,
> observability claims remain `partial` in `claims.yaml`.

## Requirement
An external party, given only published artifacts and **no access to arifOS
internals, credentials, or private state**, must be able to independently
reconstruct what happened in a governed session.

## Clean-Room Inputs
1. Public receipts exported from VAULT999 / observability.observations
2. `AAA/governance/observability/TRACE_PROPAGATION_SCHEMA.md` (once wired)
3. The session's tool-call sequence (names + arguments, redacted per policy)

## Clean-Room Exclusions (must NOT be provided)
- Kernel internal state, session memory, caches
- Private keys, secrets (5-R protocol), `.env` files
- Live network access to federation surfaces during verification

## Procedure
1. Verifier replays the tool-call sequence against a fresh, unmodified install
   from the published package.
2. Verifier recomputes verdicts, FQ vectors, and floor-check outcomes
   independently from the replay output.
3. Verifier compares recomputed values against the exported receipts.

## Pass Criteria
| Criterion | Threshold |
|---|---|
| Verdict agreement | 100% identical verdict grammar (see G-03 pollution) |
| FQ vector agreement | Match on all 7 dimensions within float tolerance |
| trace_id correlation | Exported rows reconstruct a single causal chain (currently 0% — P0-B) |
| Determinism | Same inputs → same outputs across 2 independent runs |

## Failure Disposition
Any failed criterion downgrades the corresponding claim to `partial` with the
failing criterion named in `limitations`. No narrative substitutions — raw
diffs and probe responses only.
