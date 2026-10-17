# GAP_HISTORY.md — closed and repaired gaps (receipts)
> Rows moved out of the README's "What Is Not Yet Proven" table during the
> AGENTIC-README-DOCTRINE v1 restructure (2026-10-16). Text preserved **verbatim**
> from `docs/archive/README-2026-10-16-pre-doctrine.md`. Nothing is deleted here;
> open rows remain in the README.

## Container image metadata — FIXED 2026-10-05

**Gap:** The image's own labels contradict this repository.
**Risk:** The image's own labels contradict this repository.
**Status:** **Fixed 2026-10-05** (`8372cecc3`) — labels aligned to measured reality: `licenses` → `AGPL-3.0` (matches the repo LICENSE file and PyPI metadata — both said AGPL; the BSL-1.1 label was the outlier), tool counts 13/7 → `8` (`tools_loaded: 8` measured), `PORT` env + MCP port label → `3000` (CMD/EXPOSE/HEALTHCHECK all listen on 3000 by design for Manufact cloud compat), image version → `2026.10.1`.

## Generated mirrors drift — FIXED 2026-10-05

**Gap:** `llms.txt` still prints the retired `888` judge stage and version `v2026.07.24`.
**Status:** **Fixed 2026-10-05** (`8372cecc3`) — `KERNEL 888` prose corrected to `KERNEL 666` in `arifosmcp/constitutional_map.py` and `tools_sot.yaml`; mirrors regenerated via `scripts/generate_tool_manifest.py`. The version line is now DERIVED from installed package metadata in the generator (was hardcoded `v2026.07.24`), so it cannot go stale again. Live tools/list confirms `KERNEL 666` post-deploy `a98af0d`.

## Generated discovery artifact drift — FIXED 2026-10-05

**Gap:** `smithery.yaml` no longer matches the kernel ABI registry — the guard itself fails.
**Status:** **Fixed 2026-10-05** (`8372cecc3`) — regenerated from the ABI registry: `Kernel ABI verified: 8 capabilities, 6 public tools`, `--check` exit 0.

## Development test suite — collection FIXED 2026-09-25

**Gap:** The suite needs a live kernel.
**Status:** **Fixed 2026-09-25 (collection)** — stale 269-line duplicate `tests/test_rasa_bench_10.py` removed (canonical 632-line bench lives at `/root/.hermes/policy/test_rasa_bench_10.py` where `rasa_boundary` resolves in-place); **7,668 tests collect clean** (re-measured 2026-10-05, was 7,622); `tests/conftest.py` still refuses to run without a reachable kernel at `:8088` (by design). Collection ≠ green: the identity/authority/session/attestation subset carries **34 pre-existing failures** against 321 passes (measured 2026-09-30 on a pristine `main` worktree), so quote a failure *set*, never a bare pass count.

## `__version__` strings are stale — CLOSED 2026-10-05

**Gap:** Module `__version__` lags kernel release; readers may quote it incorrectly.
**Status:** **Closed 2026-10-05** — `arifosmcp/__init__.py` derives `__version__` from installed package metadata (`_pkg_version("arifos")`), and the live wheel reports `1!2026.10.1`, identical to `pyproject.toml`. Submodule `__version__` strings (`webmcp`, `entropy_kernel`, `federation`, `hexagon`) are component tags, not kernel releases — they track their own artifacts.

## Authority floor depended on a pointer stub and an unshipped package — FIXED 2026-09-30

**Gap:** Two independent faults capped every non-exempt agent at `OBSERVE_ONLY`, so mutation-capable citizens silently lost tool access — surfacing as the "tool inexplicably unauthorized" class. (a) Boot Q5 read `identity.toml` with `_file_read(A) or _file_read(B)`; both are 101-byte DERIVED stubs reading *"superseded by: /root/AAA/identity.toml"*, and a non-empty stub short-circuits the `or`, so the canonical F13 payload was never read → `Q5=NO` → `boot_state=FAIL` → `_apply_boot_gate` demoted `LIMITED_MUTATE`/`FULL`. Authority was in practice coming from the 29-entry exemption list, not from attestation. (b) `contracts*` was absent from the wheel `include`, so the kernel's identity path resolved against a July-24 leftover. A bare `except ImportError: pass` in `_apply_boot_gate` hid a wrong module path, making the 2026-08-21 alias bypass dead code.
**Status:** **Fixed 2026-09-30** — `5cc357974` (`_read_identity_toml_chain()` joins all candidates and follows `superseded by:` pointers; Q5 `NO`→`PARTIAL`, which passes the gate since the shipped predicate is `boot_state != "FAIL"`), `2eaec19c2`+`d43b7fece` (one shared `exempt_actor_band()` resolver replacing 7 raw-string membership tests), `69175c0ec` (patched the copy production imports; boot-gate bypass moved off the fragile import), `27409ddbf` (`contracts*` ships). Verified live: 17/17 AAA identities bind `SEAL` + `mutation_allowed=True` + `VERIFIED` with an ACT carrying `LIMITED_MUTATE` and all 9 verbs, 0 boot demotions, and the control `nobody/FI-999` is still refused — trust boundary unchanged. **The generalizable defect: a stand-in served where the payload belonged, and a fail-silent `except` hid it — three times in one session.**

## Withdrawn measurement — "241,765 lines / 24 ledgers" (2026-09-21)

The figure named no population and matched no measured root, so it is **withdrawn rather than refreshed**. Two different, both-correct denominators were measured 2026-09-30T07:44:35Z (recursive whole-estate vs top-level glob); see `docs/evidence/VAULT_CENSUS.md` for both methods. Quote a count only with its method and timestamp.
