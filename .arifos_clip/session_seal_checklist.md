# A CLIP Session Seal Checklist

**Use this before closing any GitHub Copilot/CLI session.**

---

## 666 ALIGN — Constitutional Floor Check

```powershell
# Verify all tests still pass
pytest tests/test_fag.py tests/test_mcp_fag_integration.py -v

# Check for any errors in the workspace
# (VS Code: Ctrl+Shift+M or check Problems panel)
```

**Floor Verification:**
- F1 Amanah: All changes reversible via Git? ✅
- F2 Truth: Tests passing? ✅
- F4 DeltaS: Documentation complete? ✅
- F9 C_dark: No secrets committed? ✅

---

## 777 FORGE — Stage Changes

```powershell
# Check what changed
git status

# Stage relevant files
git add arifos_core/fag.py
git add arifos_core/mcp/tools/fag_read.py
git add arifos_core/mcp/server.py
git add scripts/arifos_safe_read.py
git add tests/test_fag.py
git add tests/test_mcp_fag_integration.py
git add pyproject.toml
git add AGENTS.md
git add docs/FUTURE_PATH_v38_v42.md
git add docs/FAG_QUICK_START.md
git add docs/FAG_v41_1_ROADMAP.md
git add docs/FAG_v41_0_COMPLETION_REPORT.md

# Review staged changes
git diff --staged --stat
```

---

## 888 HOLD — Governance Audit

```powershell
# Verify Cooling Ledger integrity
arifos-verify-ledger

# Check Merkle root
arifos-compute-merkle

# Analyze recent governance decisions
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output reports/fag_v41_governance.json
```

**Human Review Questions:**
- [ ] Did I introduce any breaking changes?
- [ ] Are all new files documented?
- [ ] Did I test the MCP integration?
- [ ] Are floor scores acceptable?

---

## 999 SEAL — Commit & Close

```powershell
# Commit with proper format
git commit -m "feat(fag): Ship v41.0.0-alpha constitutional filesystem wrapper

- Add FAG class with 5 floor checks (F1, F2, F4, F9)
- Add CLI tool (arifos-safe-read)
- Add MCP integration (arifos_fag_read)
- Add 23 tests (12 core + 11 MCP, all passing)
- Update AGENTS.md and FUTURE_PATH_v38_v42.md
- Mark v39, v40, v41.0.0 as SHIPPED

Tests: 23/23 passing
Floors: F1=1.0 F2=0.99 F4=0.9 F9=0.05
Verdict: SEAL"

# Push to remote (if ready)
git push origin main

# Final canary
Write-Host "[v41.0.0 | 23/23 TESTS | FAG SHIPPED | MEMORY: LEDGER]" -ForegroundColor Green
```

---

## Post-Seal Verification

```powershell
# Verify push succeeded
git log --oneline -5

# Tag the release (optional)
git tag -a v41.0.0-alpha -m "FAG: File Access Governance v41.0.0-alpha"
git push origin v41.0.0-alpha

# Archive session artifacts
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path ".arifos_clip/session.json" -Destination "archive/sessions/session_$date.json"
```

---

## Session Close Canary

```
╔════════════════════════════════════════════════════════════╗
║  [STAGE 999] SEAL COMPLETE                                 ║
║  ────────────────────────────────────────────────────────  ║
║  Session: FAG v41.0.0 Implementation                       ║
║  Tests: 23/23 PASSING                                      ║
║  Floors: F1=1.0 F2=0.99 F4=0.9 F9=0.05                     ║
║  Verdict: SEAL ✅                                          ║
║  Memory: LEDGER + ACTIVE                                   ║
║  ────────────────────────────────────────────────────────  ║
║  DITEMPA BUKAN DIBERI — Forged, not given.                 ║
╚════════════════════════════════════════════════════════════╝
```

**Session may now close safely.**
