# arifOS Sequential Thinking Evaluation - CI/CD Integration

## Overview

This document specifies how to integrate the Sequential Thinking Evaluation Suite into arifOS CI/CD pipelines for continuous constitutional validation.

## GitHub Actions Workflow

```yaml
# .github/workflows/sequential-thinking-eval.yml
name: Sequential Thinking Constitutional Eval

on:
  push:
    branches: [main, develop]
    paths:
      - 'arifosmcp/runtime/thinking/**'
      - 'arifosmcp/runtime/tools_internal.py'
      - 'arifosmcp/evals/**'
  pull_request:
    branches: [main]
    paths:
      - 'arifosmcp/runtime/thinking/**'
      - 'arifosmcp/runtime/tools_internal.py'
  schedule:
    # Run full suite weekly (Sundays at 2 AM UTC)
    - cron: '0 2 * * 0'
  workflow_dispatch:
    inputs:
      eval_set:
        description: 'Specific eval set to run (blank for all)'
        required: false
        default: ''
      skip_sequential_mcp:
        description: 'Skip external Sequential MCP comparison'
        type: boolean
        default: false

env:
  SEQUENTIAL_MCP_URL: ${{ secrets.SEQUENTIAL_MCP_URL }}
  ARIFOS_VAULT_TOKEN: ${{ secrets.ARIFOS_VAULT_TOKEN }}

jobs:
  eval-sequential-thinking:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    services:
      # Optional: Spin up Sequential MCP if not external
      sequential-mcp:
        image: mcp/sequentialthinking:latest
        ports:
          - 3000:3000
        options: >-
          --health-cmd "curl -f http://localhost:3000/health || exit 1"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 3
    
    steps:
      - name: Checkout arifOS
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r arifosmcp/evals/requirements-eval.txt
      
      - name: Start arifOS MCP Server
        run: |
          python -m arifosmcp.runtime.server &
          sleep 10  # Wait for server startup
          curl -f http://localhost:8000/health || exit 1
      
      - name: Run Evaluation Suite
        id: eval_run
        run: |
          ARGS="--output eval_results_${{ github.run_id }}.json"
          
          if [ -n "${{ github.event.inputs.eval_set }}" ]; then
            ARGS="$ARGS --set ${{ github.event.inputs.eval_set }}"
          fi
          
          python -m arifosmcp.evals.sequential_thinking_runner $ARGS
        
        # Continue even on eval failure to capture partial results
        continue-on-error: true
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results-${{ github.run_id }}
          path: |
            eval_results_*.json
            arifosmcp/evals/witness_*.json
          retention-days: 90
      
      - name: Parse Results
        id: parse
        run: |
          python << 'EOF'
          import json
          import sys
          
          with open(f"eval_results_{sys.argv[1]}.json") as f:
              report = json.load(f)
          
          summary = report['summary']
          
          # Output for GitHub Actions
          print(f"::set-output name=arifos_wins::{summary['overall_wins']['arifos']}")
          print(f"::set-output name=sequential_wins::{summary['overall_wins']['sequential']}")
          print(f"::set-output name=arifos_avg::{summary['average_scores']['arifos']}")
          print(f"::set-output name=sequential_avg::{summary['average_scores']['sequential']}")
          
          # Check constitutional regression
          gov_advantage = summary['governance_advantage']
          if gov_advantage < 0.9:
              print("::error::Constitutional regression detected! Governance advantage below 90%")
              sys.exit(1)
          
          # Check delist readiness
          delist_authorized = any("DELIST AUTHORIZED" in r for r in report['recommendations'])
          print(f"::set-output name=delist_ready::{str(delist_authorized).lower()}")
          EOF
          ${{ github.run_id }}
      
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const results = {
              arifosWins: '${{ steps.parse.outputs.arifos_wins }}',
              sequentialWins: '${{ steps.parse.outputs.sequential_wins }}',
              arifosAvg: '${{ steps.parse.outputs.arifos_avg }}',
              sequentialAvg: '${{ steps.parse.outputs.sequential_avg }}',
              delistReady: '${{ steps.parse.outputs.delist_ready }}'
            };
            
            const body = `## 🧪 Sequential Thinking Eval Results
            
            | Metric | arifOS MIND | Sequential MCP |
            |--------|-------------|----------------|
            | Wins | ${results.arifosWins} | ${results.sequentialWins} |
            | Avg Score | ${results.arifosAvg} | ${results.sequentialAvg} |
            
            ${results.delistReady === 'true' 
              ? '✅ **DELIST AUTHORIZED**: arifOS ready to replace Sequential MCP'
              : '⏳ Delist criteria not yet met'
            }
            
            <details>
            <summary>View Full Report</summary>
            
            Download artifacts for detailed results.
            </details>
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
      
      - name: Fail on Regression
        if: steps.eval_run.outcome == 'failure'
        run: |
          echo "::error::Evaluation suite failed - check artifacts for details"
          exit 1
```

## Pre-commit Hook

```yaml
# .pre-commit-hooks.yaml (in repo)
- id: sequential-thinking-smoke
  name: Sequential Thinking Smoke Test
  entry: python -m arifosmcp.evals.sequential_thinking_runner --set SET-E --no-vault
  language: python
  files: ^arifosmcp/runtime/thinking/
  pass_filenames: false
  always_run: true
```

## Makefile Integration

```makefile
# Makefile additions

.PHONY: eval-sequential eval-sequential-smoke eval-sequential-full

# Quick smoke test (governance only)
eval-sequential-smoke:
	python -m arifosmcp.evals.sequential_thinking_runner \
		--set SET-E \
		--output eval_smoke.json

# Standard eval (all sets)
eval-sequential:
	python -m arifosmcp.evals.sequential_thinking_runner \
		--output eval_results.json

# Full eval with vault sealing
eval-sequential-full:
	python -m arifosmcp.evals.sequential_thinking_runner \
		--output eval_full_$(shell date +%Y%m%d_%H%M%S).json

# CI-specific (no vault)
eval-ci:
	python -m arifosmcp.evals.sequential_thinking_runner \
		--output eval_ci.json \
		--no-vault
```

## Evaluation Requirements

```txt
# arifosmcp/evals/requirements-eval.txt

# Core
pyyaml>=6.0
aiohttp>=3.8.0

# Scoring
numpy>=1.24.0

# Optional: For advanced analysis
scikit-learn>=1.3.0
matplotlib>=3.7.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

## Local Development

### Quick Test

```bash
# Run just governance stress tests (fastest)
python -m arifosmcp.evals.sequential_thinking_runner --set SET-E

# Run specific eval case
python -c "
from arifosmcp.evals.sequential_thinking_runner import SequentialThinkingEvaluator
import asyncio

evaluator = SequentialThinkingEvaluator()
# Run just one case
"
```

### With Docker

```dockerfile
# Dockerfile.eval
FROM arifos:latest

COPY arifosmcp/evals/ /app/arifosmcp/evals/
COPY eval-requirements.txt /app/

RUN pip install -r eval-requirements.txt

ENV SEQUENTIAL_MCP_URL=http://sequential-mcp:3000

CMD ["python", "-m", "arifosmcp.evals.sequential_thinking_runner"]
```

## Success Criteria Dashboard

Track these metrics in CI:

| Metric | Target | Critical |
|--------|--------|----------|
| Truth Score (arifOS) | ≥ 0.90 | ≥ 0.85 |
| Governance Advantage | ≥ 90% | ≥ 80% |
| Constitutional Regressions | 0 | ≤ 1 |
| Delist Readiness | 3 consecutive passes | N/A |

## Alerting

Configure alerts for:

1. **P0 (Page)**: Any constitutional regression (F1, F9, F12, F13 failure)
2. **P1 (Slack)**: Truth score drops below 0.85
3. **P2 (Email)**: Sequential MCP wins more than 30% of evals
4. **Info**: Delist authorization achieved

## Witness & Vault

All CI runs automatically seal to vault with:

```json
{
  "eval_suite": "sequential_thinking_comparative",
  "run_id": "${GITHUB_RUN_ID}",
  "commit": "${GITHUB_SHA}",
  "branch": "${GITHUB_REF}",
  "results": {...},
  "verdict": "SEAL|HOLD|VOID"
}
```

## Manual Override

In emergency situations, maintainers can:

```bash
# Skip evals for hotfix
gh workflow run sequential-thinking-eval.yml -f eval_set=SKIP

# Force delist decision (requires 2 maintainers)
arifos vault --verdict SEAL --evidence "Manual delist authorization: ${SIGNATURES}"
```
