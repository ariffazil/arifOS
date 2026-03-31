#!/bin/bash
echo "AgentZero + arifOS Status"
echo "========================"
docker compose ps
echo ""
echo "Health Checks:"
curl -s http://localhost:18080/health 2>/dev/null || echo "arifOS: Not responding"
echo ""
echo "VAULT999 Status:"
ls -la ./data/vault999/ 2>/dev/null | head -5 || echo "Vault not initialized"
