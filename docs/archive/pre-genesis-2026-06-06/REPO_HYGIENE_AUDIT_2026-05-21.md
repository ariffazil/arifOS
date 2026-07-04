# Repo Hygiene Audit - 2026-05-21

## git status --short
```
 D .cursor/mcp.json
 M .gitignore
 M arifosmcp/sessions/hermes-briefings/2026-05-20-MALAM-BRIEF.md
 M docs/AGENT_LAYOUT_CONTRACT.md
 M tests/runtime/test_msap_ack.py
 M tests/runtime/test_zkpc_v2.py
?? docs/REPO_HYGIENE_AUDIT_2026-05-21.md
```

## git branch --show-current
```
chore/repo-hygiene-arifos-20260521
```

## git log --oneline --decorate --graph --max-count=12
```
* 1cb30ce9 (HEAD -> chore/repo-hygiene-arifos-20260521, origin/main, origin/HEAD, main) vault999-writer: two-lane architecture + ZKPC quarantine + Ed25519 opt-in
* f89fdbf3 docs(arifOS): add malam brief from hermes session
* e28b9143 feat(arifOS): wire metabolize mode across kernel_route and mind_reason
* 2c25b0cf fix(arifOS): add metabolize mode to eureka_insight tool
* e4dd8bbd feat(deploy): absorb remaining A-FORGE arifOS deploy artifacts
* 33677f71 (origin/feat/kernel-purity-workspace-isolation) feat(kernel): finalize kernel purity and secure workspace isolation
* 2dbf7b1a feat(deploy): absorb A-FORGE deploy configs and arifOS-supabase
* 5589fa74 fix(arifOS): metabolize mode delegation + datetime compat in mind_reason
* 661fc01e fix(arifOS): add metabolize mode to mind_reason tool modes
* 42bc9d1e A-RIF Discovery Forge: ordinal evidence levels, Jaccard contrast, 488 tests pass
*   253acbe0 merge: resolve pyproject.toml conflicts — take newer dep versions from origin/main
|\  
| * 42414555 revert: undo Imgbot (#460) (#461)
```

## git log --oneline origin/main..HEAD
```
```

## git diff --stat
```
 .cursor/mcp.json                                   |  10 --
 .gitignore                                         |   5 +
 .../hermes-briefings/2026-05-20-MALAM-BRIEF.md     | 176 ++++++++-------------
 docs/AGENT_LAYOUT_CONTRACT.md                      | 155 ++++++++++++------
 tests/runtime/test_msap_ack.py                     |  12 +-
 tests/runtime/test_zkpc_v2.py                      |  18 ++-
 6 files changed, 200 insertions(+), 176 deletions(-)
```

## git diff --check
```
PASS
```

## verification

```txt
pytest tests/runtime/test_msap_ack.py tests/runtime/test_zkpc_v2.py -q: PASS (31/31)
python -m pytest tests/ -q --tb=short: PASS (1939 passed, 18 skipped)
```
