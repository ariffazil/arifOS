@echo off
REM arifOS Unified MCP Server Startup Script (Live SSE Mode)
REM Starts the MCP server on Port 8000

echo ================================================================================
echo arifOS Unified MCP Server v49.0.0 (SSE/Live)
echo ================================================================================
echo.

REM Set environment variables
set ARIFOS_ALLOW_LEGACY_SPEC=1
set ARIFOS_PHYSICS_DISABLED=0
set PYTHONPATH=%PYTHONPATH%;%CD%

echo Environment:
echo   ARIFOS_ALLOW_LEGACY_SPEC=%ARIFOS_ALLOW_LEGACY_SPEC%
echo   ARIFOS_PHYSICS_DISABLED=%ARIFOS_PHYSICS_DISABLED%
echo.

echo Starting SSE Server (Port 8000)...
echo Press Ctrl+C to stop
echo.

REM Start the server module
python -m arifos.mcp.sse

echo.
echo MCP server stopped.
pause
