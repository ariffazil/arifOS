@echo off
REM Setup Gemini CLI configuration for arifOS integration
REM Run this after first Gemini CLI initialization

echo === arifOS Gemini CLI Setup ===
echo.

REM Create .gemini directory if it doesn't exist
if not exist "%USERPROFILE%\.gemini" (
    echo Creating .gemini directory...
    mkdir "%USERPROFILE%\.gemini"
)

REM Copy MCP server configuration
echo Copying MCP server configuration...
copy /Y "config\gemini\mcp_servers.json" "%USERPROFILE%\.gemini\mcp_servers.json"

REM Copy baseline configuration
echo Copying baseline configuration...
copy /Y "config\gemini\config_baseline.json" "%USERPROFILE%\.gemini\config.json"

REM Copy aliases
echo Copying aliases...
copy /Y "config\gemini\aliases.json" "%USERPROFILE%\.gemini\aliases.json"

echo.
echo === Setup Complete ===
echo.
echo Your Gemini CLI is now configured with:
echo   - arifOS MCP server integration
echo   - Constitutional governance settings
echo   - Working directory: %CD%
echo   - Agent role: Architect (Δ)
echo.
echo To verify, run: gemini config show
echo.
pause
