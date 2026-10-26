# DEPLOY RECEIPT — arifOS hotfix 8359618feaed (2026-10-26)

> F13 directive: **"1234 deploy, ikat adat, advice guide inclusive agentic execution intelligence state"**
> Independent review: 888-APEX → `RECOMMEND_SABAR` with 5 conditions (§5 below, all satisfied).
> Author ≠ judge: the deploy was executed by 333-AGI; the verdict came from 888-APEX.

---

## 1. What shipped

| Field | Value |
|---|---|
| Deploy commit | `8359618feaed386d3cae23350915f2df95967b87` |
| Branch | `deploy/honest-green-hotfix-20261026` (pushed to origin before deploy) |
| Base | `origin/main` = `bb756d95818614032fb44708ae470b1846366db7` |
| Relationship | **prod = main + this hotfix.** Not merged to main. |
| Predecessor runtime (backed up) | `/opt/arifos/backups/pre-deploy-20261026T112735/` |

### Module parity (live site-packages vs the deployed commit)

| Module | pre | post | live == commit |
|---|---|---|---|
| runtime/verdict.py | 68cb34d832 | c08961798c | YES |
| runtime/rest_routes/rest_routes.py | f8c36156d3 | 3cd960bba8 | YES |
| runtime/floor_producers.py | b82d5763e0 | 01c715cd09 | YES |
| runtime/capability_drift.py | 800f65c60e | 5035b38cd7 | YES |
| runtime/health_truth.py | a6261b0ee9 | a6261b0ee9 | YES |
| runtime/v2_envelope.py | c9e706fd70 | c9e706fd70 | YES |
| runtime/tools.py | ab3b9b2e1f | dcef98c0b1 | YES |

`/opt/arifos/app/.git_commit` now equals the deploy SHA (was `bb756d95`, while `/health` claimed `e62a940` — three disagreeing stamps before this deploy).

---

## 2. The four patches

1. **`verdict.py` — the all-HOLD cause.** The walker judged v2_envelope's own transport projection (`intermediate_trace_states.canonical_verdict`, vocabulary DENY/PROCEED/HOLD/SEALED) as a kernel verdict claim → `UNKNOWN_VERDICT_TOKEN` → HOLD on every v2-enveloped response. Carved out by suffix. Top-level copy was already stripped.
2. **`rest_routes.py` — F1.** Score from `_phi_fq_from_quotient` (floor 0.5, ratified 2026-09-12) instead of "FLOWING or zero". Constellation becomes a diagnostic. **No threshold changed.**
3. **`rest_routes.py` — F8.** A skipped producer (uncalibrated G) can no longer render the 0.8 placeholder as `pass, measured: true`.
4. **`capability_drift.py`** — schema-hash match is tri-state; also **`floor_producers.py`** F6 tolerates the real seal-row payload shape (string/None).

---

## 3. Effect verification (live, after restart)

| Probe | Before | After |
|---|---|---|
| `F1` provenance | `arifflow_verdict:FLOWING;fq=…` | **`arifflow_probe:quotient=1.0032;floor=0.5;constellation=PARTIAL_WIRING`** |
| `F1` outcome in the old-failure scenario | FAIL 0.0 when constellation ≠ FLOWING | **PASS 1.0 while constellation = PARTIAL_WIRING** — the exact case that used to fail |
| `F8` | `status pass, measured true` on a skipped reading | **`status unmeasured, measured false`** |
| `floors_unmeasured` | `[F10, F6]` (F1/F8 mislabelled measured) | **`[F10, F4, F6, F7, F8, F9]`** |
| `floors_aggregate` | 9 measured / 4 unmeasured | 7 measured / 6 unmeasured (honest: fewer green, no lies) |
| `arif_judge` (read-only candidate) | reason #1 `UNKNOWN_VERDICT_TOKEN:intermediate_trace_states.canonical_verdict=DENY` | **flag gone**; remaining reason `Effective verdict HOLD dominates intercept decision` |
| `vault999_health` / sealer breaker | healthy / closed | healthy / closed |
| `origin_ok` / `runtime_import_path` | true / venv | true / venv |
| `/health` after restart | — | **200 after 6 s**, service `active` |

**NOT changed, by design:** `execution_readiness` remains `held` and `floor_passed` remains `null`. 888-APEX verified readiness is substrate-driven (`JUDGE_SEAL_AUTHORIZATION`), not floor-driven — a perfect deploy cannot move it. F6/F10 instruments are the missing input.

---

## 4. Rollback (one move, ~2 minutes)

```bash
rsync -a --delete /opt/arifos/backups/pre-deploy-20261026T112735/arifosmcp-sitepkgs/ \
  /opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp/
rsync -a --delete /opt/arifos/backups/pre-deploy-20261026T112735/app/ /opt/arifos/app/
systemctl restart arifos.service
```
(An automated version of this already runs inline if `/health` fails to answer within 90 s.)

**Triggers:** `/health` not 200 for 120 s · service not active · `runtime_import_path` outside the venv · `origin_enforced=false` · `vault999_health != healthy` · sealer breaker open · any pre-deploy **measured** floor becomes FAIL.
**Not triggers:** `floors_pass` dropping because F8 became unmeasured · `execution_readiness` still held · `floor_passed` still null.

---

## 5. 888-APEX conditions — disposition

| # | Condition | Status |
|---|---|---|
| 1 | Exact commit on origin (not just locally) | **MET** — branch pushed before deploy; `git push` exit 0 |
| 2 | Sovereign directive on the record | **MET** — F13 message this session, quoted verbatim at the top of this receipt |
| 3 | Purge `__pycache__` in both copies; prove behaviourally, not by hash | **MET** — 0 caches remain; behavioural probe in §3 |
| 4 | Run the tests against a clean export of the commit, not the dirty tree | **MET** — `git archive` per commit; 15 new assertions pass, 126 pre-existing pass; 2 F6 test failures reproduced identically on pristine `origin/main` |
| 5 | Corrected receipt, pre/post hashes, no self-seal | **MET** — this file. No VAULT999 append was made by the author. |

---

## 6. What this deploy did NOT fix (named, not hidden)

1. **Prod is ahead of main** by one commit. Merge is a separate reviewed act.
2. **`execution_readiness: held`** — needs F6 and F10 instruments (F6 work already landing on main as `runtime/f6/*`).
3. **`actor_verified: true` on an `actor_id` swap inside a valid session** — P0-security, F13 decision (is `actor_id` advisory or binding?).
4. **F13 PASS scope** — proves "no unratified machine self-acceptance in the last 100 seal rows", not "this action is authorised".
5. **`arif_judge` still HOLDs** for read-only candidates — now for a substantive intercept reason, not a vocabulary bug.
