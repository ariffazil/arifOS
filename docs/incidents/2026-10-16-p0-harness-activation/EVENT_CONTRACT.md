# EVENT_CONTRACT.md

**Reference:** ARIFOS::BASELINE_UNIT_TESTS::v1
**Date:** 2026-10-16.

The authoritative machine-checked event contract is
`schemas/governance-event.schema.json`. Field vocabulary lives there. This
file records only what a schema cannot: the vocabulary conflict and the
refusal-cause verbs.

## Vocabulary conflict (shown, not silently resolved)

- `AGENTS.md` names only 4 "constitutional verdicts": SEAL / HOLD / VOID / SABAR.
- The runtime `SealType` enum proves 7 (`arifosmcp/models/verdicts.py`, imported
  read-only 2026-10-16): `VOID, HOLD_888, HOLD, SABAR, PARTIAL, PROVISIONAL, SEAL`.
- An earlier harness draft used `REJECT` as a verdict — **REJECT is NOT a
  verdict**. REJECT/DENY/REFUSE are refusal/transport verbs, not governance
  verdicts.
- `UNKNOWN` is NOT a SealType member. Missing evidence is `null` (absent), not
  a fake "UNKNOWN" verdict string.

**Freeze decision:** `governance.verdict` = the 7 SealType values, nullable.

## Refusal-cause verbs (transport/refusal, NOT verdicts)

- `REJECT` — transport refusal (router/capability_aware_router.py)
- `DENY` — transport denial (tools.py, fastmcp_ext/transports.py)
- `REFUSE` — transport refusal (tools.py, observatory_routes.py)

## Input contradictions preserved from the build (2026-10-16)

1. **Verdict enum** — FOUR_GAP_SOURCE_MAP.md lists `SEAL/HOLD/SABAR/VOID/UNKNOWN/PARTIAL`;
   live `SealType` proves the 7 above (`UNKNOWN` absent; `PROVISIONAL`, `HOLD_888`
   missing from the source map). Live source wins; conflict recorded.
2. **Two source roots** — INVENTED_OR_UNVERIFIED_PATHS.md probes
   `/opt/arifos/app/arifosmcp`; FOUR_GAP_SOURCE_MAP.md cites
   `/root/arifOS/arifosmcp/runtime`. Both trees exist; canonical source for this
   harness is `/root/arifOS`.
3. **888_JUDGE over-claim** — EVENT_VOCABULARY_MATRIX flags that the bundle
   over-claims 888 (musyawarah uses 666 judgment + 888 decision). Adopted: the
   harness uses `judge_source` (string) and never asserts 888 as canonical.

Critical rules enforced by the schema: verdict text never establishes identity;
signature validity never establishes authority by itself; transport success
never means governance success; a `SEAL-` prefix never authorizes.
