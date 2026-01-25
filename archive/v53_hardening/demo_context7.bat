@echo off
REM Demonstrate context7 MCP server in Kimi CLI
echo Starting Kimi CLI with context7 MCP demonstration...
echo ===================================================
echo This will open an interactive Kimi session.
echo Try these commands:
echo.
echo 1. Ask: "What MCP tools do you have access to?"
echo 2. Ask "Use context7 to find the latest FastAPI documentation about middleware"
echo 3. Ask "Resolve the library ID for 'numpy' using context7"
echo.
echo Press Ctrl+C to exit
echo ===================================================
timeout /t 5
kimikimi -p "Use context7 to resolve the library ID for 'requests' library and show me the latest documentation for making GET requests" --yolo --quiet
