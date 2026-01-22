@echo off
REM arifOS Unified MCP Server Startup Script
REM Starts the MCP server with proper environment variables

echo ================================================================================
echo arifOS Unified MCP Server v47.0.0
echo ================================================================================
echo.

REM Set environment variables
set ARIFOS_ALLOW_LEGACY_SPEC=1
set ARIFOS_PHYSICS_DISABLED=1

echo Environment:
echo   ARIFOS_ALLOW_LEGACY_SPEC=%ARIFOS_ALLOW_LEGACY_SPEC%
echo   ARIFOS_PHYSICS_DISABLED=%ARIFOS_PHYSICS_DISABLED%
echo.

echo Starting MCP server...
echo Press Ctrl+C to stop
echo.

REM Start the server
python -m arifos.core.mcp.sse

echo.
echo MCP server stopped.
pause
