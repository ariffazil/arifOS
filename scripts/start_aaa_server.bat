@echo off
REM AAA MCP Server Launcher (v45.3.0)
REM Auto-sets environment and handles certificates

REM Navigate to Repo Root (Parent of scripts/)
cd /d "%~dp0.."

echo ======================================================================
echo   AAA MCP SERVER v45.3.0 (Triple-Trinity Gateway)
echo ======================================================================
echo   Repo Root: %CD%
echo.

REM Set Environment
set PYTHONPATH=%CD%
set ARIFOS_ALLOW_LEGACY_SPEC=1

REM Check/Generate SSL Certificates
if not exist arifos_core\mcp\certs\cert.pem (
    echo [SETUP] SSL Certificates missing. Generating via Python...
    python arifos_core\mcp\gen_certs.py
    if errorlevel 1 (
        echo [ERROR] Certificate generation failed.
        pause
        exit /b 1
    )
    echo [SETUP] Certificates generated.
)

REM Verify Vault Structure
if not exist vault_999\CCC (
    echo [SETUP] Creating initial vault structure...
    mkdir vault_999\CCC\L0_VAULT 2>nul
    mkdir vault_999\BBB 2>nul
    mkdir vault_999\CCC\L4_WITNESS 2>nul
)

echo.
echo [INFO] Starting Server...
echo [INFO] URL: https://127.0.0.1:8000/sse
echo.
python arifos_core\mcp\arifos_mcp_server.py

if errorlevel 1 (
    echo [ERROR] Server crashed or exited with error.
    pause
)
