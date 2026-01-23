@echo off
REM Backup Gemini CLI configuration to arifOS repo

echo === Backing up Gemini CLI configuration ===
echo.

REM Get date in YYYYMMDD format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set backup_date=%datetime:~0,8%

REM Create backup directory
if not exist "config\gemini\backups" mkdir "config\gemini\backups"

REM Backup current configs
if exist "%USERPROFILE%\.gemini\config.json" (
    echo Backing up config.json...
    copy "%USERPROFILE%\.gemini\config.json" "config\gemini\backups\config_%backup_date%.json"
)

if exist "%USERPROFILE%\.gemini\mcp_servers.json" (
    echo Backing up mcp_servers.json...
    copy "%USERPROFILE%\.gemini\mcp_servers.json" "config\gemini\backups\mcp_servers_%backup_date%.json"
)

if exist "%USERPROFILE%\.gemini\aliases.json" (
    echo Backing up aliases.json...
    copy "%USERPROFILE%\.gemini\aliases.json" "config\gemini\backups\aliases_%backup_date%.json"
)

echo.
echo Backup complete! Files saved to: config\gemini\backups\
echo.
pause
