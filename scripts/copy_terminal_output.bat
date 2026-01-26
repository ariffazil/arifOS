@echo off
REM Capture terminal output and send to Kimi CLI
REM Designed for VS Code integration on Windows

setlocal enabledelayedexpansion

REM Default parameters
set LINES=50
set OUTPUT_FILE=%USERPROFILE%\.arifos_clip\terminal_output.log
set COMMAND=/paste

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :execute
if "%~1"=="-l" set LINES=%~2 & shift & shift & goto :parse_args
if "%~1"=="--lines" set LINES=%~2 & shift & shift & goto :parse_args
if "%~1"=="-f" set OUTPUT_FILE=%~2 & shift & shift & goto :parse_args
if "%~1"=="--file" set OUTPUT_FILE=%~2 & shift & shift & goto :parse_args
if "%~1"=="-c" set COMMAND=%~2 & shift & shift & goto :parse_args
if "%~1"=="--command" set COMMAND=%~2 & shift & shift & goto :parse_args
shift
goto :parse_args

:execute
REM Check if output file exists
if not exist "%OUTPUT_FILE%" (
    echo [ERROR] Terminal output file not found: %OUTPUT_FILE%
    echo [TIP] Configure VS Code to log terminal output to this file
    exit /b 1
)

REM Create temp directory if needed
set TEMP_DIR=%TEMP%\.arifos_clip
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Generate temp filename
set TEMP_FILE=%TEMP_DIR%\terminal_capture_%RANDOM%.log

REM Extract last N lines using PowerShell for reliability
echo [INFO] Capturing last %LINES% lines from terminal output...
powershell -ExecutionPolicy Bypass -Command "Get-Content '%OUTPUT_FILE%' -Tail %LINES% | Out-File -FilePath '%TEMP_FILE%' -Encoding UTF8"

REM Check if content was captured
for %%A in ("%TEMP_FILE%") do set SIZE=%%~zA
if %SIZE% EQU 0 (
    echo [WARNING] No content captured from terminal output
    del "%TEMP_FILE%"
    exit /b 0
)

echo [SUCCESS] Captured content from terminal output
echo.
echo --- Preview (first 10 lines) ---
powershell -ExecutionPolicy Bypass -Command "Get-Content '%TEMP_FILE%' -Head 10 | ForEach-Object { Write-Host '  ' $_ }"

REM Count lines
for /f %%i in ('find /v /c "" ^< "%TEMP_FILE%"') do set LINE_COUNT=%%i
echo ... (%LINE_COUNT% total lines)
echo.

REM Check for kimi command
where kimi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Sending to Kimi CLI...
    kimi %COMMAND% %TEMP_FILE%
) else (
    REM Fallback to python
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Sending to Kimi CLI via Python...
        python -m kimi_cli %COMMAND% %TEMP_FILE%
    ) else (
        echo [ERROR] Neither 'kimi' nor 'python' commands found in PATH
        echo [TIP] Please ensure Kimi CLI is installed
        del "%TEMP_FILE%"
        exit /b 1
    )
)

REM Cleanup temp file after a delay
start /min cmd /c "timeout /t 30 /nobreak >nul & del ""%TEMP_FILE%"" 2>nul"

endlocal
