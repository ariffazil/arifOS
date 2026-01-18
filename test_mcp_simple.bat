@echo off
echo ============================================================
echo Testing arifOS MCP Server Startup
echo ============================================================
echo.

REM Set environment variables
set ARIFOS_ALLOW_LEGACY_SPEC=1
set ARIFOS_PHYSICS_DISABLED=0
set PYTHONPATH=C:\Users\User\OneDrive\Documents\GitHub\arifOS

echo Environment variables set:
echo   ARIFOS_ALLOW_LEGACY_SPEC = %ARIFOS_ALLOW_LEGACY_SPEC%
echo   ARIFOS_PHYSICS_DISABLED  = %ARIFOS_PHYSICS_DISABLED%
echo.

echo Test 1: Importing arifos.mcp module...
python -c "import arifos.mcp; print('SUCCESS: Module imported')" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Module imports correctly
) else (
    echo [FAIL] Module import failed
    exit /b 1
)

echo.
echo ============================================================
echo MCP Server Configuration is READY
echo ============================================================
echo Next step: Restart Claude Desktop to activate arifOS MCP tools
echo ============================================================
