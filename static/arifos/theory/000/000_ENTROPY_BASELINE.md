# 000 Entropy Baseline (Commit 62cffa2)

Scope: baseline audit derived from `main@62cffa2a92de740a6d521393921d33744257f4f2` using filesystem and git history.

Session sequence executed for this phase:
1) VAULT999 restore context (read-only vault inventory)
2) 000 INIT audit framing
3) AAA baseline scan (no cleanup changes)

No destructive actions taken. 888_HOLD remains required before any cleanup/removal pass.

## Entropy Scorecard (0-10)

Scoring model (weighted sum):
- duplication: 0.30
- test_debt: 0.25
- undocumented_modules: 0.15
- branch_drift: 0.15
- tool_contract_gaps: 0.15

| Metric | Score (0-10) | Evidence |
|---|---:|---|
| Duplication | 8.3 | `SEAL_*.md` in root: 6 (12 total repo); overlapping docs `AGENTS/ARCHITECTURE/CLAUDE/GEMINI` in root + archive/docs: 12 variants; config overlap: 5 root configs (6 including `static/.well-known/mcp/server.json`) |
| Test Debt | 7.4 | forensic artifacts in root: 8 files (`pytest_*.txt` x4 + `ruff_errors.txt` + `tests_output.txt` + temp artifacts); recorded failures in `pytest_output.txt`, `pytest_errors.txt`, `pytest_full.txt`, `pytest_core.txt` |
| Undocumented Modules | 5.7 | missing module README in `arifos_aaa_mcp/`, `memory/`, `verification/`, `vps/` (4/7 targeted dirs undocumented) |
| Branch Drift | 6.0 | 6 unmerged Dependabot branches against `origin/main` |
| Tool Contract Gaps | 5.8 | AGENTS lists 11 legacy verbs; runtime exposes 13 canonical tools with aliasing and stage-name drift |

Weighted total entropy score: `6.90 / 10`

Release gate target: `< 5.0` before v48 release.

## Structural Drift Details

- Multiple seal documents
  - root: `SEAL_000_INIT_FORGE_AAA.md`, `SEAL_PHASE3_AAA_MCP.md`, `SEAL_PHASE4_AAA_RUNTIME_BRIDGE.md`, `SEAL_PHASE5_COMPLETE.md`, `SEAL_PHASE5_START_VERIFICATION.md`, `SEAL_PHASE6_DEPRECATION.md`
  - repo-wide `SEAL_*.md`: 12
- Overlapping governance docs
  - root: `AGENTS.md`, `ARCHITECTURE.md`, `CLAUDE.md`, `GEMINI.md`
  - duplicates in `docs/00_META/` and `_ARCHIVE/`
- Config duplication
  - root: `fastmcp.json`, `dev.fastmcp.json`, `prod.fastmcp.json`, `mcp-manifest.json`, `server.json`
  - extra copy: `static/.well-known/mcp/server.json`
- Temporary and stale artifacts in root
  - `.tmp_generate_readme.py`
  - `${SQLITE_DB_PATH}` (0-byte file)
  - `.venv313/Scripts/python.exe` tracked in git
  - `pytest_output.txt`, `pytest_errors.txt`, `pytest_full.txt`, `pytest_core.txt`, `ruff_errors.txt`, `tests_output.txt`

## Test and Error Debt Snapshot

- Root forensic logs indicate unresolved failures and lint debt at baseline.
- Example recorded failures include:
  - `FunctionTool object is not callable` in MCP core operation tests
  - floor verdict mismatch (`test_clean_action_seal`) in `pytest_core.txt`
  - import/runtime dependency error path in `tests_output.txt`

## Module Documentation Audit

Target directories checked: `aaa_mcp/`, `arifos_aaa_mcp/`, `aclip_cai/`, `core/`, `memory/`, `verification/`, `vps/`

- README present: `aaa_mcp/`, `aclip_cai/`, `core/`
- README missing: `arifos_aaa_mcp/`, `memory/`, `verification/`, `vps/`

Purpose/status checkpoints:
- `333_APPS/`: active layered app stack docs, mixed statuses from production to pilot/research (`333_APPS/README.md`, `333_APPS/STATUS.md`)
- `_ARCHIVE/`: historical/deprecated content sink; no top-level README in baseline
- `VAULT999/`: canonical forensic memory and seal ledger with explicit README and banded access model

## Branch Drift and VPS Alignment

- Remote branch drift: 6 unmerged Dependabot branches
  - `origin/dependabot/github_actions/actions/setup-node-6`
  - `origin/dependabot/github_actions/actions/setup-python-6`
  - `origin/dependabot/github_actions/actions/upload-pages-artifact-4`
  - `origin/dependabot/github_actions/codecov/codecov-action-5`
  - `origin/dependabot/github_actions/github/codeql-action-4`
  - `origin/dependabot/pip/fastmcp-3.0.2`
- VPS repo alignment check (`/root/arifOS`): local `main` is behind `origin/main` by 3 commits (`0 ahead, 3 behind`)
- Commit chain around baseline:
  - `62cffa2` -> `b7b2569c` -> `8b92b721`

Interpretation: VPS working copy is not currently aligned to latest GitHub main.

## Tool Contract Gap Snapshot

AGENTS reference surface (11):
- governance verbs: `anchor`, `reason`, `integrate`, `respond`, `validate`, `align`, `forge`, `audit`, `seal`
- utility verbs: `search`, `fetch`

Runtime canonical surface (13):
- `anchor_session`, `reason_mind`, `recall_memory`, `simulate_heart`, `critique_thought`, `apex_judge`, `eureka_forge`, `seal_vault`, `search_reality`, `fetch_content`, `inspect_file`, `audit_rules`, `check_vital`

Gap classes:
- naming drift across generations (legacy -> mid-gen -> canonical)
- compressed stage wrappers (`reason_mind` folds reason/integrate/respond)
- 2 additional runtime utility/safety tools not in AGENTS 11-list (`inspect_file`, `check_vital`)

## Uncertainty and Confidence

- Omega0 estimate: `0.06`
- Confidence bounds by section:
  - structural/test/doc counts: `0.96`
  - branch drift and commit lineage: `0.99`
  - tool-contract interpretation across aliases: `0.86`
  - overall baseline confidence: `0.92`
