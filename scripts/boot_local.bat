@echo off
set "PYTHONPATH=%~dp0\.."
set "ARIFOS_ALLOW_LEGACY_SPEC=1"
set "ARIFOS_CONSTITUTIONAL_MODE=AAA"
set "ARIFOS_HUMAN_SOVEREIGN=Arif"

:: Force creation of log dir
if not exist "%~dp0\..\logs" mkdir "%~dp0\..\logs"

:: Set Python Path
set "PYTHON_EXE=%~dp0\..\.venv\Scripts\python.exe"

:: Run with -u for unbuffered binary I/O (CRITICAL for MCP stdio)
"%PYTHON_EXE%" -u -m arifos.core.mcp.unified_server 2> "%~dp0\..\logs\kimi_mcp_stderr.log"
