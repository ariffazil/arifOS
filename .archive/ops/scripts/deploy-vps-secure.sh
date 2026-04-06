#!/bin/bash
set -e

echo "🚀 Starting arifOS MCP Secure Auto-Deploy..."

# Configuration
MCP_PORT="${MCP_PORT:-8080}"
MCP_HOST="${MCP_HOST:-0.0.0.0}"
MCP_TRANSPORT="${MCP_TRANSPORT:-http}"
VENV_PATH="/root/arifOS/.venv"
ARIFOS_PATH="/root/arifOS"
LOG_FILE="/var/log/arifos-mcp.log"

echo "📦 Configuration:"
echo "   Host: $MCP_HOST"
echo "   Port: $MCP_PORT"
echo "   Transport: $MCP_TRANSPORT"

# Update code
echo "📥 Pulling latest code..."
cd "$ARIFOS_PATH"
git pull origin main

# Activate virtual environment
echo "🐍 Activating Python environment..."
source "$VENV_PATH/bin/activate"

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -e . --quiet
pip install uvicorn --quiet

# Run constitutional health check before deployment
echo "🏥 Running pre-deploy health check..."
if ! $VENV_PATH/bin/python -c "import arifosmcp.transport; print('✅ MCP module OK')" 2>/dev/null; then
    echo "❌ Pre-deploy check failed! Aborting."
    exit 1
fi

# Backup current service config if it exists
if [ -f /etc/systemd/system/arifos-mcp.service ]; then
    cp /etc/systemd/system/arifos-mcp.service /etc/systemd/system/arifos-mcp.service.bak
fi

# Create systemd service for HTTP transport
echo "⚙️  Configuring systemd service..."
cat > /etc/systemd/system/arifos-mcp.service << EOF
[Unit]
Description=arifOS MCP Server (HTTP Transport)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$ARIFOS_PATH
Environment=PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONUNBUFFERED=1
Environment=MCP_PORT=$MCP_PORT
Environment=MCP_HOST=$MCP_HOST
# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$ARIFOS_PATH /var/log
ExecStart=$VENV_PATH/bin/python -m arifosmcp.transport $MCP_TRANSPORT --host $MCP_HOST --port $MCP_PORT
Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3
# Logging
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
SyslogIdentifier=arifos-mcp

[Install]
WantedBy=multi-user.target
EOF

# Configure firewall (if ufw is available)
echo "🔥 Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow $MCP_PORT/tcp comment 'arifOS MCP Server'
    echo "   ✅ Firewall rule added for port $MCP_PORT"
else
    echo "   ⚠️  ufw not found, skipping firewall config"
    echo "   📝 Manually open port $MCP_PORT if needed:"
    echo "      iptables -A INPUT -p tcp --dport $MCP_PORT -j ACCEPT"
fi

# Reload systemd and restart service
echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo "🚀 Starting MCP service..."
systemctl enable arifos-mcp
systemctl restart arifos-mcp

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 3

# Verify deployment
echo "🔍 Verifying deployment..."
MAX_RETRIES=5
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -fsS "http://127.0.0.1:$MCP_PORT/health" >/dev/null 2>&1; then
        echo "   ✅ MCP server responding on port $MCP_PORT"
        break
    fi
    
    # Check if process is running
    if ! systemctl is-active --quiet arifos-mcp; then
        echo "   ❌ Service failed to start!"
        echo "   📋 Checking logs:"
        journalctl -u arifos-mcp --no-pager -n 20 || true
        exit 1
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   ⏳ Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "   ⚠️  Health check timeout, but service is running"
fi

# Get public IP for user reference
PUBLIC_IP=$(curl -fsS ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")

echo ""
echo "✨ Deployment Complete!"
echo ""
echo "📊 Service Status:"
systemctl status arifos-mcp --no-pager -l || true
echo ""
echo "🔗 Connection Info:"
echo "   Local:  http://127.0.0.1:$MCP_PORT"
echo "   Remote: http://$PUBLIC_IP:$MCP_PORT"
echo ""
echo "🧪 Test with:"
echo "   curl http://$PUBLIC_IP:$MCP_PORT/health"
echo ""
echo "📊 Monitor logs:"
echo "   journalctl -u arifos-mcp -f"
echo "   tail -f $LOG_FILE"
echo ""
echo "🛑 To stop: systemctl stop arifos-mcp"
echo "🔄 To restart: systemctl restart arifos-mcp"
echo ""
echo "✨ Deployed at $(date)"
