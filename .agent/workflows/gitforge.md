---
skill: "gitforge"
version: "1.0.0"
description: Analyze git branch entropy and hot zones
floors:
  - F1
  - F4
  - F5
allowed-tools:
  - Bash(git:*)
  - Bash(python:*)
expose-cli: true
derive-to:
  - codex
  - claude
codex-name: arifos-workflow-gitforge
claude-name: analyze-entropy
sabar-threshold: 5.0
---
# /gitforge - State Mapper & Entropy Predictor

This workflow uses the Trinity forge.py system to analyze git history, identify hot zones, and predict entropy impact of proposed changes.

## Steps

// turbo-all

1. **Get Current Branch**
   ```bash
   git branch --show-current
   ```

2. **Check Uncommitted Changes**
   ```bash
   git status --short
   ```

3. **Run Forge Analysis via Python**
   ```bash
   python -c "from arifos_core.trinity.forge import analyze_branch; import sys; branch = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'; report = analyze_branch(branch); print(f'Files Changed: {len(report.files_changed)}'); print(f'Hot Zones: {report.hot_zones}'); print(f'Entropy Delta (ΔS): {report.entropy_delta:.2f}'); print(f'Risk Score: {report.risk_score:.3f}'); [print(f'  {note}') for note in report.notes]" $(git branch --show-current)
   ```

4. **Show Hot Zone Details**
   ```bash
   git log -30 --name-only --pretty=format:"" | sort | uniq -c | sort -rn | head -10
   ```

5. **Compare with Main**
   ```bash
   git diff --stat main...$(git branch --show-current)
   ```

## Interpretation

### Entropy Delta (ΔS)
- **ΔS < 3.0**: Low entropy - clean, focused change
- **3.0 ≤ ΔS < 5.0**: Moderate entropy - acceptable with review
- **ΔS ≥ 5.0**: HIGH ENTROPY - ⚠️ SABAR-72 threshold exceeded, requires cooling

### Risk Score
- **0.0 - 0.3**: 🟢 LOW RISK - Fast track eligible
- **0.4 - 0.6**: 🟡 MODERATE RISK - Standard review
- **0.7 - 1.0**: 🔴 HIGH RISK - Full cooling + human review required

### Hot Zones
Files that appear ≥3 times in last 30 commits. Touching hot zones increases risk significantly.

## Fail-Closed Governance
If ΔS ≥ 5.0 OR Risk Score ≥ 0.7:
1. **HALT** further changes
2. Run cooling protocol (defer, decompose, or document)
3. Seek human approval before proceeding
4. Log entropy event to cooling_ledger/

## Next Steps
- Review hot zones and consider decomposing changes
- If high risk, initiate cooling protocol
- If low risk, proceed with confidence
