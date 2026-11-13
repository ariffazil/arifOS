# Quick Start: Sequential Thinking Evaluation

## Prerequisites

```bash
# Ensure arifOS is installed
pip install -e .

# Install eval dependencies
pip install pyyaml aiohttp

# Set Sequential MCP URL (if using external)
export SEQUENTIAL_MCP_URL=http://localhost:3000
```

## Run Full Evaluation

```bash
cd arifosmcp/evals

# Run all eval sets
python -m arifosmcp.evals.sequential_thinking_runner

# Results saved to: eval_results.json
```

## Run Specific Eval Set

```bash
# Pure reasoning only
python -m arifosmcp.evals.sequential_thinking_runner --set SET-A

# Governance stress tests only (fastest)
python -m arifosmcp.evals.sequential_thinking_runner --set SET-E

# All applied problems
python -m arifosmcp.evals.sequential_thinking_runner --set SET-B
```

## Understanding Results

### Summary Output

```
Overall Wins:
  arifOS MIND:     12
  Sequential MCP:  3
  Ties:            2

Average Scores:
  arifOS MIND:     0.823
  Sequential MCP:  0.741
  Delta:           +0.082

Recommendations:
  ✅ TRUTH PARITY: arifOS within acceptable range
  ✅ GOVERNANCE: arifOS shows strong constitutional enforcement
  🎯 DELIST AUTHORIZED: arifOS MIND ready to replace Sequential MCP
```

### Interpretation

| Symbol | Meaning |
|--------|---------|
| ✅ | Criteria met |
| ⚠️ | Needs improvement |
| 🎯 | Ready for production |
| ⏳ | Pending more data |

## Adding New Eval Cases

Edit `sequential_thinking_evals.yaml`:

```yaml
eval_sets:
  - id: "SET-A"
    cases:
      - id: "A-NEW-001"
        name: "Your Test Case"
        prompt: |
          Your prompt here...
        reference_key:
          must_cover: ["concept1", "concept2"]
        constitutional_checks:
          F2: "What truth is required"
          F7: "Uncertainty requirements"
```

## Human Grading

For subjective axes (clarity, reasoning quality), create:

```json
{
  "eval_id": "A-001",
  "system": "arifos_mind",
  "human_scores": {
    "clarity": 4.5,
    "reasoning_quality": 4.0
  },
  "rater": "senior-engineer-001",
  "timestamp": "2026-04-11T10:00:00Z"
}
```

Submit via:
```bash
python -m arifosmcp.evals.submit_human_grades human_grades.json
```

## Delist Checklist

Before delisting Sequential MCP:

- [ ] 3 consecutive eval runs with arifOS wins
- [ ] 100% governance pass on SET-E
- [ ] Truth parity (≥ 0.90) on SET-A
- [ ] No constitutional regressions
- [ ] Approved by 2 senior maintainers
- [ ] Sealed to vault with SEAL verdict

## Troubleshooting

### Sequential MCP Connection Failed

```bash
# Start local Sequential MCP
docker run -p 3000:3000 mcp/sequentialthinking

# Or skip comparison
export SKIP_SEQUENTIAL_MCP=1
```

### arifOS Import Error

```bash
# Ensure you're in the right directory
cd /path/to/arifOS
pip install -e .
python -c "import arifosmcp; print('OK')"
```

### Vault Sealing Failed

```bash
# Run without vault (for local testing)
python -m arifosmcp.evals.sequential_thinking_runner --no-vault
```

## Next Steps

1. Review full results in `eval_results.json`
2. Check `detailed_results` for per-case breakdown
3. Iterate on arifOS if criteria not met
4. Seal to vault when ready
5. Submit PR to delist Sequential MCP

## Support

- Issues: File in arifOS repo with `evals` label
- Questions: #arifos-eval channel
- Emergency: Page on-call for constitutional regressions

---

**Ditempa Bukan Diberi**
