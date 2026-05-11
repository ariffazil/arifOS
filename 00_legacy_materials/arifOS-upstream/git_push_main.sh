#!/bin/bash
# arifOS Substrate Seal & Push
# Executes the L5 Deploy Gate and pushes to main only upon SEAL.

echo "🏗️  ARIFOS: INITIATING DEPLOY GATE..."

# Run the deploy gate orchestrator
python -m arifosmcp.evals.deploy_gate

# Capture the exit code
GATE_STATUS=$?

if [ $GATE_STATUS -eq 0 ]; then
    echo "✅ DEPLOY GATE SEALED. COMMENCING PUSH..."
    git add .
    git commit -m "DITEMPA BUKAN DIBERI — Substrate Forge Sealed [$(date -u +%Y-%m-%dT%H:%M:%SZ)]"
    git push origin main
    echo "🚀 DEPLOYMENT COMPLETE."
else
    echo "🚨 DEPLOY GATE VOIDed. PUSH ABORTED."
    exit 1
fi
