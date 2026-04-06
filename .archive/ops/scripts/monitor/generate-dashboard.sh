#!/bin/bash
# Agent Activity Dashboard Generator
# Creates a simple HTML dashboard

OUTPUT_FILE="/var/www/arifosmcp/agents.html"
VAULT_FILE="/root/arifOS/VAULT999/vault999.jsonl"

echo "🔄 Generating Agent Activity Dashboard..."

# Generate HTML
cat > "$OUTPUT_FILE" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>arifOS Agent Activity Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        h1 { color: #00d9ff; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #16213e; padding: 15px; border-radius: 8px; border-left: 4px solid #00d9ff; }
        .stat-value { font-size: 2em; color: #00d9ff; }
        .stat-label { color: #888; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #16213e; color: #00d9ff; }
        tr:hover { background: #0f3460; }
        .SEAL { color: #4ade80; }
        .VOID { color: #f87171; }
        .SABAR { color: #fbbf24; }
        .refresh { margin: 20px 0; padding: 10px 20px; background: #00d9ff; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; }
        .refresh:hover { background: #00a8cc; }
        .timestamp { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🔥 arifOS Agent Activity Dashboard</h1>
    <p class="timestamp">Last updated: EOF

echo "$(date)" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EOF'
</p>
    
    <div class="stats">
EOF

# Calculate stats
TOTAL=$(wc -l < "$VAULT_FILE")
TODAY=$(date +%Y-%m-%d)
TODAY_COUNT=$(grep "\"timestamp\":\"$TODAY" "$VAULT_FILE" 2>/dev/null | wc -l)
SEAL_COUNT=$(grep '"verdict":"SEAL"' "$VAULT_FILE" 2>/dev/null | wc -l)
VOID_COUNT=$(grep '"verdict":"VOID"' "$VAULT_FILE" 2>/dev/null | wc -l)

cat >> "$OUTPUT_FILE" << EOF
        <div class="stat-card">
            <div class="stat-value">$TOTAL</div>
            <div class="stat-label">Total Actions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">$TODAY_COUNT</div>
            <div class="stat-label">Actions Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">$SEAL_COUNT</div>
            <div class="stat-label">Successful (SEAL)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">$VOID_COUNT</div>
            <div class="stat-label">Failed (VOID)</div>
        </div>
    </div>
    
    <h2>Recent Agent Activity (Last 50)</h2>
    <table>
        <thead>
            <tr>
                <th>Time</th>
                <th>Session</th>
                <th>Verdict</th>
                <th>Query</th>
            </tr>
        </thead>
        <tbody>
EOF

# Add recent entries
tail -50 "$VAULT_FILE" | while read -r line; do
    TIMESTAMP=$(echo "$line" | jq -r '.timestamp[:19] // "N/A"')
    SESSION=$(echo "$line" | jq -r '.session_id[:8] // "N/A"')
    VERDICT=$(echo "$line" | jq -r '.verdict // "N/A"')
    QUERY=$(echo "$line" | jq -r '.query[:50] // "N/A"')
    
    cat >> "$OUTPUT_FILE" << EOF
            <tr>
                <td>$TIMESTAMP</td>
                <td>$SESSION</td>
                <td class="$VERDICT">$VERDICT</td>
                <td>$QUERY</td>
            </tr>
EOF
done

cat >> "$OUTPUT_FILE" << 'EOF'
        </tbody>
    </table>
    
    <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
EOF

echo "✅ Dashboard created at: $OUTPUT_FILE"
echo "🌐 Access at: https://arifosmcp.arif-fazil.com/agents.html"
