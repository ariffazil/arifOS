#!/bin/bash
# arifOS Daily Tool Audit Script
# Runs daily tool calls and generates 3 MD reports

REPO="/workspace/repos/arifOS"
MCP_URL="https://arifosmcp.arif-fazil.com/mcp"
HEALTH_URL="https://arifosmcp.arif-fazil.com/health"

echo "=== arifOS Daily Audit Starting ==="
echo "Date: $(date)"

# 1. Get tools list
echo "[1/5] Fetching tools list..."
TOOLS_JSON=$(curl -s "$HEALTH_URL")
echo "$TOOLS_JSON" > "$REPO/WORKSPACE/logs/daily-health-$(date +%Y-%m-%d).json"

# 2. Test core tools (select key tools to test - testing ALL 40 would be too much)
echo "[2/5] Testing key tools..."

# Test init_anchor
curl -s -X POST "$MCP_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"init_anchor","arguments":{"mode":"status","declared_name":"1AGI","dry_run":false}},"id":1}' \
  > "$REPO/WORKSPACE/logs/tool-init_anchor-$(date +%Y-%m-%d).json"

# Test physics_reality  
curl -s -X POST "$MCP_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"physics_reality","arguments":{"mode":"time"}},"id":2}' \
  > "$REPO/WORKSPACE/logs/tool-physics_reality-$(date +%Y-%m-%d).json"

# Test math_estimator
curl -s -X POST "$MCP_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"math_estimator","arguments":{"complexity":"medium"}},"id":3}' \
  > "$REPO/WORKSPACE/logs/tool-math_estimator-$(date +%Y-%m-%d).json"

# Test engineering_memory (store)
curl -s -X POST "$MCP_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"engineering_memory","arguments":{"mode":"vector_store","content":"Daily audit test $(date)"}},"id":4}' \
  > "$REPO/WORKSPACE/logs/tool-memory_store-$(date +%Y-%m-%d).json"

# Test apex_judge
curl -s -X POST "$MCP_URL" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"apex_judge","arguments":{"verdict":"test","dry_run":true}},"id":5}' \
  > "$REPO/WORKSPACE/logs/tool-apex_judge-$(date +%Y-%m-%d).json"

echo "[3/5] Tools tested: init_anchor, physics_reality, math_estimator, engineering_memory, apex_judge"

# 3. Generate 3 reports
echo "[4/5] Generating reports..."

# Report 1: Daily Audit
cat > "$REPO/REPORTS/DAILY_AUDIT_$(date +%Y-%m-%d).md" << 'EOF'
# arifOS Daily Audit Report
## $(date +%Y-%m-%d)

## Tool Test Results

| Tool | Status | Verdict | Latency |
|------|--------|---------|---------|
| init_anchor | Tested | CHECK LOG | - |
| physics_reality | Tested | CHECK LOG | - |
| math_estimator | Tested | CHECK LOG | - |
| engineering_memory | Tested | CHECK LOG | - |
| apex_judge | Tested | CHECK LOG | - |

## Server Health
Check health endpoint logs for full status.

## Notes
EOF

# Report 2: Validator Feedback (template)
cat > "$REPO/REPORTS/VALIDATOR_FEEDBACK_$(date +%Y-%m-%d).md" << 'EOF'
# arifOS Validator Feedback Report
## $(date +%Y-%m-%d)

## Daily Review

### What Works
- 

### What Doesn't
-

### Suggestions
-

## External POV Score
Rating: /5

## Verdict
SEAL / HOLD / VOID
EOF

# Report 3: Blueprint Update (template)
cat > "$REPO/REPORTS/ENGINEERING_BLUEPRINT_$(date +%Y-%m-%d).md" << 'EOF'
# arifOS Engineering Blueprint Update
## $(date +%Y-%m-%d)

## Progress This Week

### Completed
- 

### In Progress
-

### Blocked
-

## Next Steps
1. 
2. 
3. 

## Resource Usage
- Tools tested: 5
- Reports generated: 3
EOF

echo "[5/5] Reports generated at $REPO/REPORTS/"

# 4. Commit to git
echo "[6/5] Committing to git..."
cd "$REPO"
git add WORKSPACE/logs/ REPORTS/
git commit -m "Daily audit $(date +%Y-%m-%d)" || echo "Nothing to commit"
git push

echo "=== Daily Audit Complete ==="
