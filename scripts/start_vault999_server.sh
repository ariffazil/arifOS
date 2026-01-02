#!/bin/bash
# Quick start script for VAULT999 MCP Server (Unix/Mac)

set -e

echo "======================================================================"
echo "  VAULT999 MCP Server - Quick Start (Unix/Mac)"
echo "======================================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "[1/4] Checking dependencies..."
if ! python3 -c "import mcp.server.fastmcp" 2>/dev/null; then
    echo "  Installing dependencies..."
    pip install -r arifos_core/mcp/requirements.txt
fi
echo "  OK"

echo ""
echo "[2/4] Checking SSL certificates..."
if [ ! -f arifos_core/mcp/certs/cert.pem ]; then
    echo "  Generating SSL certificates..."
    mkdir -p arifos_core/mcp/certs
    cd arifos_core/mcp/certs
    openssl req -x509 -newkey rsa:4096 -nodes \
      -out cert.pem -keyout key.pem -days 365 \
      -subj "/CN=127.0.0.1" \
      -addext "subjectAltName=IP:127.0.0.1"
    cd ../../..
    if [ ! -f arifos_core/mcp/certs/cert.pem ]; then
        echo "  [ERROR] OpenSSL not found or certificate generation failed"
        exit 1
    fi
fi
echo "  OK"

echo ""
echo "[3/4] Checking vault structure..."
if [ ! -d vault_999/VAULT999/L0_Vault ]; then
    echo "  Creating vault structure..."
    mkdir -p vault_999/VAULT999/L0_Vault
    mkdir -p vault_999/VAULT999/L1_Ledger
    mkdir -p vault_999/VAULT999/L4_Witness
fi
echo "  OK"

echo ""
echo "[4/4] Starting VAULT999 MCP Server..."
echo "  Press Ctrl+C to stop"
echo ""
python3 arifos_core/mcp/vault999_server.py
