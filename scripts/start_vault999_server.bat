@echo off
REM Quick start script for VAULT999 MCP Server (Windows)

echo ======================================================================
echo   VAULT999 MCP Server - Quick Start (Windows)
echo ======================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show fastmcp >nul 2>&1
if errorlevel 1 (
    echo   Installing dependencies...
    pip install -r arifos_core\mcp\requirements.txt
)
echo   OK

echo.
echo [2/4] Checking SSL certificates...
if not exist arifos_core\mcp\certs\cert.pem (
    echo   Generating SSL certificates...
    mkdir arifos_core\mcp\certs 2>nul
    cd arifos_core\mcp\certs
    openssl req -x509 -newkey rsa:4096 -nodes ^
      -out cert.pem -keyout key.pem -days 365 ^
      -subj "/CN=127.0.0.1" ^
      -addext "subjectAltName=IP:127.0.0.1"
    cd ..\..\..
    if not exist arifos_core\mcp\certs\cert.pem (
        echo   [ERROR] OpenSSL not found or certificate generation failed
        echo   Install OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html
        pause
        exit /b 1
    )
)
echo   OK

echo.
echo [3/4] Checking vault structure...
if not exist vault_999\VAULT999\L0_Vault (
    echo   Creating vault structure...
    mkdir vault_999\VAULT999\L0_Vault
    mkdir vault_999\VAULT999\L1_Ledger
    mkdir vault_999\VAULT999\L4_Witness
)
echo   OK

echo.
echo [4/4] Starting VAULT999 MCP Server...
echo   Press Ctrl+C to stop
echo.
python arifos_core\mcp\vault999_server.py
