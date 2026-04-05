#!/bin/bash
# arifOS OpenCode Agent Setup & Fix Script
# Purpose: Fix failing MCP servers and reduce token usage on VPS
# Usage: Run as root or with sudo for docker group changes

set -e

echo "🔧 arifOS OpenCode Agent Setup Script"
echo "======================================"

# Detect platform
if [[ "$(uname)" == "Linux" ]]; then
    PLATFORM="linux"
    if [[ -f /etc/debian_version ]]; then
        DISTRO="debian"
    elif [[ -f /etc/redhat-release ]]; then
        DISTRO="redhat"
    else
        DISTRO="unknown"
    fi
else
    echo "⚠️  This script is intended for Linux VPS systems."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Install missing npm packages for MCP servers
echo ""
echo "1. Installing missing npm packages for MCP servers..."
if ! command_exists npm; then
    echo "   npm not found. Installing Node.js and npm..."
    if [[ "$DISTRO" == "debian" ]]; then
        apt-get update
        apt-get install -y nodejs npm
    elif [[ "$DISTRO" == "redhat" ]]; then
        yum install -y nodejs npm
    else
        echo "   ❌ Cannot install npm automatically. Please install Node.js manually."
        exit 1
    fi
fi

# Install global MCP servers
echo "   Installing @modelcontextprotocol/server-fetch..."
npm install -g @modelcontextprotocol/server-fetch || echo "   ⚠️  Failed to install fetch server (may already exist)"
echo "   Installing @modelcontextprotocol/server-git..."
npm install -g @modelcontextprotocol/server-git || echo "   ⚠️  Failed to install git server (may already exist)"

# 2. Docker permissions fix
echo ""
echo "2. Fixing Docker permissions..."
if command_exists docker; then
    DOCKER_GROUP=$(getent group docker | cut -d: -f1)
    if [[ -z "$DOCKER_GROUP" ]]; then
        echo "   Docker group not found. Creating docker group..."
        groupadd docker
    fi
    CURRENT_USER=$(whoami)
    if ! groups $CURRENT_USER | grep -q '\bdocker\b'; then
        echo "   Adding user $CURRENT_USER to docker group..."
        usermod -aG docker $CURRENT_USER
        echo "   ✅ User added to docker group. Please log out and back in for changes to take effect."
    else
        echo "   ✅ User already in docker group."
    fi
else
    echo "   ⚠️  Docker not installed. Skipping docker permissions."
fi

# 3. Reduce MCP server count in OpenCode config
echo ""
echo "3. Optimizing OpenCode configuration..."
OPENCODE_CONFIG="$HOME/.config/opencode/opencode.json"
if [[ -f "$OPENCODE_CONFIG" ]]; then
    echo "   Found OpenCode config at $OPENCODE_CONFIG"
    # Create backup
    BACKUP="$OPENCODE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$OPENCODE_CONFIG" "$BACKUP"
    echo "   Backup created at $BACKUP"
    
    # Use Python to safely edit JSON
    python3 <<'EOF'
import json, os, sys
config_path = os.path.expanduser("~/.config/opencode/opencode.json")
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"   ❌ Failed to read config: {e}")
    sys.exit(1)

# Reduce mcp servers to essential ones only
# Keep only aaa-mcp and maybe a few others
if "mcp" in config:
    servers = config["mcp"]
    # Identify servers that are failing or heavy
    keep_servers = {}
    essential = ["aaa-mcp", "filesystem", "fetch", "git"]
    for name, server in servers.items():
        # Keep aaa-mcp and essential servers, disable others
        if name in essential:
            keep_servers[name] = server
            # Ensure they are enabled
            keep_servers[name]["enabled"] = True
            print(f"   Keeping server: {name}")
        else:
            # Disable non-essential servers
            if server.get("enabled", False):
                server["enabled"] = False
                keep_servers[name] = server
                print(f"   Disabling server: {name}")
            else:
                keep_servers[name] = server
                print(f"   Server already disabled: {name}")
    config["mcp"] = keep_servers
    print(f"   ✅ Optimized MCP servers: {len([s for s in keep_servers.values() if s.get('enabled', False)])} enabled, {len(keep_servers)} total")
else:
    print("   ⚠️  No mcp key found")

# Write updated config
try:
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("   ✅ Updated OpenCode configuration")
except Exception as e:
    print(f"   ❌ Failed to write config: {e}")
EOF
else
    echo "   ⚠️  OpenCode config not found at $OPENCODE_CONFIG"
    echo "   Creating minimal configuration..."
    mkdir -p "$(dirname "$OPENCODE_CONFIG")"
    cat > "$OPENCODE_CONFIG" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aaa-mcp": {
      "type": "local",
      "command": ["python", "-m", "arifosmcp.transport", "stdio"],
      "cwd": ".",
      "enabled": true,
      "timeout": 15000,
      "environment": {
        "PYTHONPATH": ".",
        "ARIFOS_MODE": "PROD"
      }
    },
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/", "/home", "/tmp", "/var"],
      "enabled": true
    }
  }
}
EOF
    echo "   ✅ Created minimal OpenCode config"
fi

# 4. Restart OpenCode agent (if running as service)
echo ""
echo "4. Restarting OpenCode agent..."
if command_exists systemctl; then
    if systemctl is-active --quiet opencode; then
        echo "   Restarting opencode service..."
        systemctl restart opencode
        echo "   ✅ OpenCode service restarted"
    else
        echo "   ⚠️  OpenCode systemd service not found or not running"
    fi
else
    echo "   ℹ️  Manual step: Restart OpenCode agent via your terminal/IDE"
fi

echo ""
echo "✅ Setup complete!"
echo "   Next steps:"
echo "   1. Log out and back in for docker group changes"
echo "   2. Verify MCP servers are healthy in OpenCode UI"
echo "   3. Monitor token usage after reducing server count"
echo ""
echo "📝 For troubleshooting, see arifOS/docs/opencode-agent.md"
