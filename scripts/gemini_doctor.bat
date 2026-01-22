@echo off
REM Gemini CLI health check for arifOS integration

echo === Gemini CLI Health Check ===
echo.

echo [1/7] Checking installation...
where gemini
if %errorlevel% neq 0 (
    echo   ERROR: Gemini CLI not found in PATH
    echo   Run: npm install -g @google/gemini-cli
    goto :end
)
echo   OK: Gemini CLI installed
echo.

echo [2/7] Checking version...
gemini --version
echo.

echo [3/7] Checking config directory...
if exist "%USERPROFILE%\.gemini" (
    echo   OK: Config directory exists at %USERPROFILE%\.gemini
) else (
    echo   WARNING: Config directory not found - will be created on first run
)
echo.

echo [4/7] Checking MCP server configuration...
if exist "%USERPROFILE%\.gemini\mcp_servers.json" (
    echo   OK: MCP servers configured
    type "%USERPROFILE%\.gemini\mcp_servers.json"
) else (
    echo   WARNING: MCP servers not configured
    echo   Run: scripts\setup_gemini_config.bat
)
echo.

echo [5/7] Checking arifOS MCP gateway...
if exist "arifos\orchestrator\mcp_gateway.py" (
    echo   OK: arifOS MCP gateway found
) else (
    echo   ERROR: MCP gateway not found at expected location
)
echo.

echo [6/7] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo   ERROR: Python not found
    goto :end
)
echo   OK: Python installed
echo.

echo [7/7] Checking arifOS module...
python -c "import sys; sys.path.append('.'); import arifos; print('  OK: arifOS module importable')" 2>nul
if %errorlevel% neq 0 (
    echo   WARNING: arifOS module not importable - activate venv first
    echo   Run: .venv\Scripts\activate.bat
)
echo.

echo === Health Check Complete ===
echo.

:end
pause
