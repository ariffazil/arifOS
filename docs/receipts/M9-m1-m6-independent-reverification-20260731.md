# RECEIPT — M9 Independent Re-verification of M1–M6 · 2026-07-31

> **Mission:** M9 — Re-verify M1–M6 from a clean context without trusting the
> prior report. Re-running the gates exposed PARTIAL results that the
> original M1–M6 receipts did not surface.

## M1 — PostgreSQL authentication

| Gate | Result |
|---|---|
| Auth works using env-derived password (no plaintext on argv) | **PASS** — `psql -h 127.0.0.1 -U arifos_admin -d vault999` with `PGPASSWORD` set from `/root/.secrets/vault.flat.env` succeeds; `current_user=arifos_admin, current_database=vault999` |
| `arif_observe` via MCP returns structured response (NOT auth error) | **PASS** — returns `{"status":"pending","tool":"arif_observe","verdicts":{"substrate":{"state":"DEGRADED",...}}}` |
| Zero new auth failures from current PID (last 10 min) | **PASS** — current PID 3544057 has 0 `password authentication failed` entries in last 10 min of journal |
| M1 receipt leaks the credential | **YES — REDACTED IN NEW RECEIPT** (this receipt uses SHA-256 fingerprint only) |

## M2 — Fail-closed totality in law_evaluator

| Gate | Result |
|---|---|
| `pytest tests/test_m2_fail_closed_totality.py` | **PASS** — 4/4 tests pass: raising-on-init → VOID + fingerprint; raising-on-check → VOID + fingerprint; literal grep gate; healthy-floor regression |
| `grep "except Exception: pass" arifosmcp/core/law_evaluator.py` | **PASS** — 0 hits |
| Alternate silent-failure forms (`except: return None`) | **PASS** — 0 hits in `arifosmcp/core/law_evaluator.py` |
| Runtime behavior matches source | **PARTIAL** — `arifosmcp/core/law_evaluator.py` is hash-aligned between local source and `/opt/arifos/app/` (sha256: `7a98be726f6d6…`). Source-level fail-closed totality is correct AND active in runtime. |

## M3 — Generated tools source of truth

| Gate | Result |
|---|---|
| `python3 scripts/gen_tools_sot.py > /tmp/tools_sot.generated.yaml` then `diff` against committed | **PASS** — 0 diff lines |
| Exactly 8 canonical tools | **PASS** — `grep -c '^  - id:'` = 8 |
| Stages exactly `000,111,333,444,555,666,777,999` | **PASS** — 8 unique stages, no 888 |
| No duplicate canonical capability | **PASS** — `grep -E '^    name:' | sort | uniq -d` = 0 |
| Live `tools/list` returns same 8 names | **PASS** — runtime returns `[arif_forge, arif_init, arif_judge, arif_memory, arif_observe, arif_route, arif_seal, arif_think]` |

**M3 caveat:** `tools_sot.yaml` in `/opt/arifos/app/` is DIVERGED from the local source (sha256 differs). The runtime MCP server still returns the 8 canonical tools correctly (likely from its own `CANONICAL_TOOLS` registry in the runtime copy of `constitutional_map.py`), but the file-on-disk divergence means **the runtime is NOT reading from the canonical tools_sot.yaml** it was supposed to read from.

## M4 — Repo-routing-validation gate

| Test case | Range | Expected | Got | Verdict |
|---|---|---|---|---|
| Clean history (3 commits with valid REPO=) | `HEAD~3..HEAD` | exit 0 | exit 0 | **PASS** |
| Planted violation (commit without REPO=) | `HEAD~1..HEAD` | exit non-zero | exit non-zero | **PASS** |
| Multi-line trailer (body with REPO= on later line) | `HEAD~1..HEAD` | exit 0 | exit 0 | **PASS** |
| Wrong REPO= value (REPO=other_repo) | `HEAD` (single commit) | exit non-zero | exit non-zero | **PASS** |
| Empty range (HEAD..HEAD) | `HEAD..HEAD` | exit 0 | exit 0 | **PASS** |
| Merge commit with valid REPO= on each parent | `HEAD~3..HEAD` | exit 0 | exit 0 | **PASS** |
| Malformed (no REPO= anywhere in body) | `HEAD` (single commit) | exit non-zero | exit non-zero | **PASS** |

All 7 M4 test cases PASS on the LOCAL source. **The runtime install still has the broken gate** (per M8) — the M4 fix is NOT deployed.

## M5 — F4/F6 transposition sweep

| Gate | Result |
|---|---|
| `grep "F4 Empathy\|F6 Clarity\|F4 (Empathy)\|F6 (Clarity)" static/ docs/` | **PASS** — 0 hits in actual content; the 1 hit is inside `docs/receipts/M5-f4-f6-transposition-sweep-20260731.md` (the receipt itself documents the wrong pairings as a before/after table) |
| Correct F4 (Clarity) | ΔS entropy reduction pairings | **PASS** — 3 files |
| Correct F6 (Empathy) | κ_r stakeholder alignment pairings | **PASS** — 3 files |
| Only label+description transpositions changed (no semantic drift) | **PASS** — verified row-by-row on K111_PHYSICS.md |
| No changes to constitutional_map.py / runtime / core | **PASS** — diff shows 0 changes outside static/ and docs/core/ |

**M5 caveat:** the runtime install has 5 of 11 M5-corrected files still serving the wrong pairings (per M8 file-hash comparison).

## M6 — Sovereign decision stubs

| Gate | Result |
|---|---|
| `docs/sovereign/D1-D6-receipts-20260731.md` exists | **PASS** — file present in working tree (after transient restoration from HEAD), 14,136 bytes, 291 lines |
| Each stub (D1–D6) present with evidence citations | **PASS** — 6 `^## D[1-6]` headings |
| No canon values changed (M6 was docs-only) | **PASS** — verified 0-line diff across `constitutional_map.py`, `server.py`, `runtime/tools.py`, `runtime/law.py`, `core/laws.py`, `core/shared/types.py` |
| Each recommendation labelled non-binding | **PASS** — every stub uses "Recommendation (M6 stub, NOT sovereign ratification)" wording |
| No stub describes itself as ratified | **PASS** — all use 888_HOLD status |

## CONSTRAINT MISMATCH (per brief, honest)

The previous M1–M6 reports claimed "one commit per mission" but M1's
receipt was bundled into M2 commit `4daeb9185`:

```
commit 4daeb9185c0d6a3d95c9cf79e8d6a631d33ec6d2
fix(kernel): fail-closed totality in law_evaluator (M2)

 arifosmcp/core/law_evaluator.py                   | 210 ++++++++--------------
 docs/receipts/M1-postgres-auth-repair-20260731.md |  56 ++++++   ← bundled M1 receipt
 docs/receipts/M2-fail-closed-totality-20260731.md |  64 ++++++
 tests/test_m2_fail_closed_totality.py             | 200 +++++++++++++++++++++
```

**Classification per brief: PARTIAL — operational M1 had no dedicated commit.**

## M9 SUMMARY

| Mission | M9 verdict | Runtime deployed? |
|---|---|---|
| M1 — Postgres auth | **PARTIAL** (operational fix works; receipt leaks credential — see M7) | operational ALTER USER applied at sprint time; never reverted |
| M2 — Fail-closed totality | **PASS** (4/4 tests, 0 silent-failures) | **YES** — `arifosmcp/core/law_evaluator.py` is hash-aligned source↔runtime |
| M3 — tools_sot codegen | **PASS** (8 tools, 0 diff, no 888) | **NO** — runtime `tools_sot.yaml` is DIVERGED; runtime `tools/list` returns correct 8 names from its own registry |
| M4 — Repo-routing gate | **PASS** (7/7 synthetic tests) | **NO** — runtime workflow file is DIVERGED; broken gate is still served |
| M5 — F4/F6 transposition | **PASS** (0 wrong, 3+3 correct) | **NO** — runtime install has 5 of 11 M5-corrected files still serving wrong pairings |
| M6 — Sovereign stubs | **PASS** (6 stubs present, no canon changes) | **N/A** — docs only |

## KEY M9 DISCOVERY

The M8 file-hash comparison revealed that **the runtime install is PARTIAL**.
Only M2's `arifosmcp/core/law_evaluator.py` made it to runtime. M3, M4, M5, F13
ratifications, and M6 receipts did NOT deploy. The M1–M6 sprint's previous
success reports were based on code-level tests (pytest, synthetic bash,
grep), not runtime deployment. The runtime version string `kanon-2026.07.31+0b03b5b`
is a hardcoded legacy value that does NOT reflect actual installed code.

This means the F13 ratification work (D1–D6) — committed at `63fcda1bc` —
is also not deployed. The D5 JUDGE=666 change in `arifosmcp/constitutional_map.py`
is NOT in the runtime install; the runtime still has JUDGE=888.

**Until M8's deploy is acknowledged (`ACK_M8_DEPLOY_CANONICAL`), the live
runtime is at pre-M3 state.**

DITEMPA BUKAN DIBERI.
