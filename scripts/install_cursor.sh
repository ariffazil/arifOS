#!/bin/bash
# ============================================================================
# arifOS MCP - Cursor Installation Script (macOS/Linux/WSL) v52
# ============================================================================
#
# Installs arifos.mcp as an MCP server for Cursor IDE.
#
# Usage:
#   ./scripts/install_cursor.sh
#   ./scripts/install_cursor.sh --check
#   ./scripts/install_cursor.sh --uninstall
#
# F4 Clarity Floor: Reduce confusion, automate setup.
# DITEMPA BUKAN DIBERI
# ============================================================================

set -e

# Colors
GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
BOLD='\033[1m'
RESET='\033[0m'

# Get script directory and arifOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Cursor config location (varies by OS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CURSOR_CONFIG_DIR="$HOME/Library/Application Support/Cursor/User"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
    # Windows (Git Bash, Cygwin, or WSL)
    if [[ -n "$WSL_DISTRO_NAME" ]]; then
        # WSL - access Windows AppData
        WIN_HOME=$(wslpath "$(cmd.exe /c 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')")
        CURSOR_CONFIG_DIR="$WIN_HOME/AppData/Roaming/Cursor/User"
    else
        CURSOR_CONFIG_DIR="$APPDATA/Cursor/User"
    fi
else
    # Linux
    CURSOR_CONFIG_DIR="$HOME/.config/Cursor/User"
fi

CURSOR_CONFIG_FILE="$CURSOR_CONFIG_DIR/globalStorage/cursor.mcp/mcp.json"

echo ""
echo -e "${BOLD}============================================================================${RESET}"
echo -e "${BOLD}arifOS MCP v52 - Cursor Installation${RESET}"
echo -e "${BOLD}============================================================================${RESET}"
echo ""

# Parse arguments
case "${1:-}" in
    --check)
        echo -e "${YELLOW}Checking installation status...${RESET}"
        echo ""
        if [[ ! -f "$CURSOR_CONFIG_FILE" ]]; then
            echo -e "${RED}[NOT INSTALLED]${RESET} Cursor MCP config not found"
            echo "Expected: $CURSOR_CONFIG_FILE"
            exit 1
        fi
        if grep -q "arifos-trinity" "$CURSOR_CONFIG_FILE" 2>/dev/null; then
            echo -e "${GREEN}[INSTALLED]${RESET} arifos-trinity configured in Cursor"
            echo "Config: $CURSOR_CONFIG_FILE"
            echo ""
            cat "$CURSOR_CONFIG_FILE"
        else
            echo -e "${RED}[NOT INSTALLED]${RESET} arifos-trinity not in config"
            exit 1
        fi
        exit 0
        ;;
    --uninstall)
        echo -e "${YELLOW}Uninstalling arifos-trinity from Cursor...${RESET}"
        echo ""
        if [[ ! -f "$CURSOR_CONFIG_FILE" ]]; then
            echo -e "${YELLOW}Config file not found. Nothing to uninstall.${RESET}"
            exit 0
        fi
        cp "$CURSOR_CONFIG_FILE" "$CURSOR_CONFIG_FILE.uninstall-backup"
        echo "Backup saved to $CURSOR_CONFIG_FILE.uninstall-backup"

        # Remove arifos-trinity using jq or python
        if command -v jq &> /dev/null; then
            jq 'del(.mcpServers."arifos-trinity")' "$CURSOR_CONFIG_FILE" > "$CURSOR_CONFIG_FILE.tmp" && \
                mv "$CURSOR_CONFIG_FILE.tmp" "$CURSOR_CONFIG_FILE"
        else
            python3 -c "
import json
with open('$CURSOR_CONFIG_FILE', 'r') as f:
    config = json.load(f)
if 'mcpServers' in config and 'arifos-trinity' in config['mcpServers']:
    del config['mcpServers']['arifos-trinity']
with open('$CURSOR_CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
        fi
        echo -e "${GREEN}[OK]${RESET} arifos-trinity removed from config"
        echo ""
        echo "Restart Cursor to apply changes."
        exit 0
        ;;
    --help|-h)
        echo "Usage: install_cursor.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  (none)       Install arifos-trinity MCP server"
        echo "  --check      Check if already installed"
        echo "  --uninstall  Remove from Cursor"
        echo "  --help, -h   Show this help"
        exit 0
        ;;
esac

# Main installation
echo -e "${YELLOW}Step 1: Verifying arifOS installation...${RESET}"

# Check if arifos.mcp exists
if [[ ! -f "$ARIFOS_ROOT/arifos/mcp/__main__.py" ]]; then
    echo -e "${RED}ERROR: arifos.mcp not found at $ARIFOS_ROOT/arifos/mcp${RESET}"
    echo "Please run this script from the arifOS repository root."
    exit 1
fi
echo -e "  ${GREEN}[OK]${RESET} arifos.mcp found at $ARIFOS_ROOT/arifos/mcp"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${RESET}"
    echo "Please install Python 3.10+ and ensure it's in PATH."
    exit 1
fi
echo -e "  ${GREEN}[OK]${RESET} Python 3 found"

# Verify MCP module
if ! python3 -c "import mcp" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: MCP module not installed. Installing...${RESET}"
    pip3 install mcp
fi
echo -e "  ${GREEN}[OK]${RESET} MCP module available"

echo ""
echo -e "${YELLOW}Step 2: Creating Cursor configuration...${RESET}"

# Create config directory if needed
CONFIG_PARENT="$(dirname "$CURSOR_CONFIG_FILE")"
if [[ ! -d "$CONFIG_PARENT" ]]; then
    mkdir -p "$CONFIG_PARENT"
    echo "  Created $CONFIG_PARENT"
fi

# Backup existing config
if [[ -f "$CURSOR_CONFIG_FILE" ]]; then
    echo -e "  ${YELLOW}Existing config found. Backing up...${RESET}"
    cp "$CURSOR_CONFIG_FILE" "$CURSOR_CONFIG_FILE.backup"
    echo "  Backup saved to $CURSOR_CONFIG_FILE.backup"
fi

# Generate config using Python for reliable JSON handling
python3 << EOF
import json
import os

config_file = "$CURSOR_CONFIG_FILE"
arifos_root = "$ARIFOS_ROOT"

# Load existing config or create new
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add/update arifos-trinity (v52 path)
config['mcpServers']['arifos-trinity'] = {
    'command': 'python3',
    'args': ['-m', 'arifos.mcp', 'trinity'],
    'cwd': arifos_root,
    'env': {
        'PYTHONPATH': arifos_root,
        'ARIFOS_MODE': 'production'
    }
}

# Write config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"  Config written to {config_file}")
EOF

echo -e "  ${GREEN}[OK]${RESET} Configuration written"

echo ""
echo -e "${YELLOW}Step 3: Verifying installation...${RESET}"

# Verify config is valid JSON
if python3 -c "import json; json.load(open('$CURSOR_CONFIG_FILE'))" 2>/dev/null; then
    echo -e "  ${GREEN}[OK]${RESET} Config is valid JSON"
else
    echo -e "${RED}ERROR: Config file is not valid JSON${RESET}"
    exit 1
fi

# Test server can start
echo "  Testing arifos.mcp server..."
if PYTHONPATH="$ARIFOS_ROOT" python3 -c "from arifos.mcp.server import create_mcp_server; s = create_mcp_server(); print('  Server created')" 2>/dev/null; then
    echo -e "  ${GREEN}[OK]${RESET} arifos.mcp server initializes correctly"
else
    echo -e "${YELLOW}WARNING: Server test failed. Check Python environment.${RESET}"
fi

echo ""
echo -e "${GREEN}============================================================================${RESET}"
echo -e "${GREEN}Installation Complete!${RESET}"
echo -e "${GREEN}============================================================================${RESET}"
echo ""
echo "Next steps:"
echo "  1. Restart Cursor"
echo "  2. Open Command Palette (Cmd/Ctrl+Shift+P)"
echo "  3. Search for 'MCP: List Servers'"
echo "  4. Look for 'arifos-trinity'"
echo ""
echo "Tools available:"
echo "  000_init    - Constitutional gateway"
echo "  agi_genius  - Truth and reasoning (AGI Mind)"
echo "  asi_act     - Safety and empathy (ASI Heart)"
echo "  apex_judge  - Final judgment (APEX Soul)"
echo "  999_vault   - Immutable seal"
echo ""
echo "Config location: $CURSOR_CONFIG_FILE"
echo ""
echo "DITEMPA BUKAN DIBERI"
