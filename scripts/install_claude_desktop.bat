@echo off
REM ============================================================================
REM arifOS MCP - Claude Desktop Installation Script (Windows) v52
REM ============================================================================
REM
REM Installs arifos.mcp as an MCP server for Claude Desktop on Windows.
REM
REM Usage:
REM   scripts\install_claude_desktop.bat
REM   scripts\install_claude_desktop.bat --check    (verify only)
REM   scripts\install_claude_desktop.bat --uninstall
REM
REM F4 Clarity Floor: Reduce confusion, automate setup.
REM DITEMPA BUKAN DIBERI
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors (ANSI codes work in Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"
set "BOLD=[1m"

REM Get script directory (arifOS root is parent)
set "SCRIPT_DIR=%~dp0"
set "ARIFOS_ROOT=%SCRIPT_DIR%.."
pushd "%ARIFOS_ROOT%"
set "ARIFOS_ROOT=%CD%"
popd

REM Claude Desktop config location
set "CLAUDE_CONFIG_DIR=%APPDATA%\Claude"
set "CLAUDE_CONFIG_FILE=%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

echo.
echo %BOLD%============================================================================%RESET%
echo %BOLD%arifOS MCP v52 - Claude Desktop Installation (Windows)%RESET%
echo %BOLD%============================================================================%RESET%
echo.

REM Check for command line arguments
if "%1"=="--check" goto :check_only
if "%1"=="--uninstall" goto :uninstall
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

REM Main installation
:install
echo %YELLOW%Step 1: Verifying arifOS installation...%RESET%

REM Check if arifos.mcp exists
if not exist "%ARIFOS_ROOT%\arifos\mcp\__main__.py" (
    echo %RED%ERROR: arifos.mcp not found at %ARIFOS_ROOT%\arifos\mcp%RESET%
    echo Please run this script from the arifOS repository root.
    exit /b 1
)
echo   %GREEN%[OK]%RESET% arifos.mcp found at %ARIFOS_ROOT%\arifos\mcp

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Python not found in PATH%RESET%
    echo Please install Python 3.10+ and add to PATH.
    exit /b 1
)
echo   %GREEN%[OK]%RESET% Python found

REM Verify MCP module can be imported
python -c "import mcp" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%WARNING: MCP module not installed. Installing...%RESET%
    pip install mcp
)
echo   %GREEN%[OK]%RESET% MCP module available

REM Verify arifos.mcp can be imported
python -c "import arifos.mcp" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%WARNING: arifos.mcp not in PYTHONPATH. Will use absolute path.%RESET%
)

echo.
echo %YELLOW%Step 2: Creating Claude Desktop configuration...%RESET%

REM Create config directory if needed
if not exist "%CLAUDE_CONFIG_DIR%" (
    mkdir "%CLAUDE_CONFIG_DIR%"
    echo   Created %CLAUDE_CONFIG_DIR%
)

REM Check if config exists
if exist "%CLAUDE_CONFIG_FILE%" (
    echo   %YELLOW%Existing config found. Backing up...%RESET%
    copy "%CLAUDE_CONFIG_FILE%" "%CLAUDE_CONFIG_FILE%.backup" >nul
    echo   Backup saved to %CLAUDE_CONFIG_FILE%.backup

    REM Check if arifos-trinity already configured
    findstr /C:"arifos-trinity" "%CLAUDE_CONFIG_FILE%" >nul 2>&1
    if not errorlevel 1 (
        echo   %YELLOW%arifos-trinity already configured. Updating...%RESET%
    )
)

REM Write new config using PowerShell for proper JSON handling
powershell -Command ^
    "$config = @{mcpServers = @{'arifos-trinity' = @{command = 'python'; args = @('-m', 'arifos.mcp', 'trinity'); cwd = '%ARIFOS_ROOT%'; env = @{PYTHONPATH = '%ARIFOS_ROOT%'; ARIFOS_MODE = 'production'}}}}; " ^
    "if (Test-Path '%CLAUDE_CONFIG_FILE%') { " ^
    "  $existing = Get-Content '%CLAUDE_CONFIG_FILE%' -Raw | ConvertFrom-Json; " ^
    "  if (-not $existing.mcpServers) { $existing | Add-Member -NotePropertyName 'mcpServers' -NotePropertyValue @{} }; " ^
    "  $existing.mcpServers.'arifos-trinity' = $config.mcpServers.'arifos-trinity'; " ^
    "  $existing | ConvertTo-Json -Depth 10 | Set-Content '%CLAUDE_CONFIG_FILE%' " ^
    "} else { " ^
    "  $config | ConvertTo-Json -Depth 10 | Set-Content '%CLAUDE_CONFIG_FILE%' " ^
    "}"

if errorlevel 1 (
    echo %RED%ERROR: Failed to write config%RESET%
    exit /b 1
)
echo   %GREEN%[OK]%RESET% Configuration written to %CLAUDE_CONFIG_FILE%

echo.
echo %YELLOW%Step 3: Verifying installation...%RESET%

REM Verify the config is valid JSON
powershell -Command "Get-Content '%CLAUDE_CONFIG_FILE%' | ConvertFrom-Json" >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Config file is not valid JSON%RESET%
    exit /b 1
)
echo   %GREEN%[OK]%RESET% Config is valid JSON

REM Test that server can start
echo   Testing arifos.mcp server...
python -c "from arifos.mcp.server import create_mcp_server; s = create_mcp_server(); print('Server created')" 2>nul
if errorlevel 1 (
    echo %YELLOW%WARNING: Server test failed. Check Python environment.%RESET%
) else (
    echo   %GREEN%[OK]%RESET% arifos.mcp server initializes correctly
)

echo.
echo %GREEN%============================================================================%RESET%
echo %GREEN%Installation Complete!%RESET%
echo %GREEN%============================================================================%RESET%
echo.
echo Next steps:
echo   1. Restart Claude Desktop
echo   2. Look for "arifos-trinity" in the MCP servers list
echo   3. Try: "Call 000_init with action=validate"
echo.
echo Tools available:
echo   000_init    - Constitutional gateway
echo   agi_genius  - Truth and reasoning (AGI Mind)
echo   asi_act     - Safety and empathy (ASI Heart)
echo   apex_judge  - Final judgment (APEX Soul)
echo   999_vault   - Immutable seal
echo.
echo Config location: %CLAUDE_CONFIG_FILE%
echo.
echo DITEMPA BUKAN DIBERI
goto :eof

REM ============================================================================
:check_only
echo %YELLOW%Checking installation status...%RESET%
echo.

if not exist "%CLAUDE_CONFIG_FILE%" (
    echo %RED%[NOT INSTALLED]%RESET% Claude Desktop config not found
    echo Expected: %CLAUDE_CONFIG_FILE%
    exit /b 1
)

findstr /C:"arifos-trinity" "%CLAUDE_CONFIG_FILE%" >nul 2>&1
if errorlevel 1 (
    echo %RED%[NOT INSTALLED]%RESET% arifos-trinity not in config
    exit /b 1
)

echo %GREEN%[INSTALLED]%RESET% arifos-trinity configured in Claude Desktop
echo Config: %CLAUDE_CONFIG_FILE%
echo.
type "%CLAUDE_CONFIG_FILE%"
goto :eof

REM ============================================================================
:uninstall
echo %YELLOW%Uninstalling arifos-trinity from Claude Desktop...%RESET%
echo.

if not exist "%CLAUDE_CONFIG_FILE%" (
    echo %YELLOW%Config file not found. Nothing to uninstall.%RESET%
    goto :eof
)

REM Backup first
copy "%CLAUDE_CONFIG_FILE%" "%CLAUDE_CONFIG_FILE%.uninstall-backup" >nul
echo Backup saved to %CLAUDE_CONFIG_FILE%.uninstall-backup

REM Remove arifos-trinity from config using PowerShell
powershell -Command ^
    "$config = Get-Content '%CLAUDE_CONFIG_FILE%' -Raw | ConvertFrom-Json; " ^
    "if ($config.mcpServers.'arifos-trinity') { " ^
    "  $config.mcpServers.PSObject.Properties.Remove('arifos-trinity'); " ^
    "  $config | ConvertTo-Json -Depth 10 | Set-Content '%CLAUDE_CONFIG_FILE%' " ^
    "}"

echo %GREEN%[OK]%RESET% arifos-trinity removed from config
echo.
echo Restart Claude Desktop to apply changes.
goto :eof

REM ============================================================================
:show_help
echo.
echo Usage: install_claude_desktop.bat [OPTIONS]
echo.
echo Options:
echo   (none)       Install arifos-trinity MCP server
echo   --check      Check if already installed
echo   --uninstall  Remove from Claude Desktop
echo   --help, -h   Show this help
echo.
goto :eof
