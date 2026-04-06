#!/bin/bash
# kill_switch.sh — Emergency Brake (F11 Command Authority)
# Simpan dalam phone notes kau — ini "Big Red Button"

echo "🛑 ARIFOS KILL SWITCH ACTIVATED"
echo "================================"

# Stop arifOS service
sudo systemctl stop arifos 2>/dev/null || echo "arifOS service not running (OK)"

# Kill any Python MCP processes
pkill -f "arifosmcp.transport" 2>/dev/null && echo "✓ MCP processes killed"

# Close firewall ports
sudo ufw deny 8000 2>/dev/null && echo "✓ Port 8000 closed"
sudo ufw deny 8080 2>/dev/null && echo "✓ Port 8080 closed"

# Verify
if pgrep -f "arifosmcp.transport" > /dev/null; then
    echo "⚠️  WARNING: Some processes still running"
    pgrep -af "arifosmcp.transport"
else
    echo "✓ arifOS DEAD — System safe"
fi

echo ""
echo "Status: $(date)"
echo "DEAD"
