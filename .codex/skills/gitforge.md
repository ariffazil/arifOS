---
description: /gitforge — State Mapper & Entropy Predictor
---
# /gitforge — State Mapper & Entropy Predictor

**Role:** Forge (Δ)
**Platform:** Codex CLI

---

## Purpose

Analyze branch entropy, hot zones, and risk before changes.

---

## Steps

1. **Branch** — `git branch --show-current`
2. **Status** — `git status --short`
3. **Forge Analysis** — Use arifOS forge if available:
   - `python -c "from arifos_core.trinity.forge import analyze_branch; import sys; branch = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'; report = analyze_branch(branch); print(f'Files Changed: {len(report.files_changed)}'); print(f'Hot Zones: {report.hot_zones}'); print(f'Entropy Delta (ΔS): {report.entropy_delta:.2f}'); print(f'Risk Score: {report.risk_score:.3f}'); [print(f'  {note}') for note in report.notes]" $(git branch --show-current)`
4. **Hot Zones (fallback)** — `git log -30 --name-only --pretty=format:"" | sort | uniq -c | sort -rn | head -10`
5. **Diff vs main** — `git diff --stat main...$(git branch --show-current)`

---

## Interpretation

- **ΔS < 3.0**: Low entropy
- **3.0 ≤ ΔS < 5.0**: Moderate entropy
- **ΔS ≥ 5.0**: High entropy (cooling required)

- **Risk 0.0–0.3**: Low
- **Risk 0.4–0.6**: Moderate
- **Risk 0.7–1.0**: High (cooling required)

---

**DITEMPA BUKAN DIBERI**
