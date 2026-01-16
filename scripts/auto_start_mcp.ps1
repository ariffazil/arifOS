# arifOS MCP Auto-Start Script (Windows PowerShell)
# Stage 000: Auto-ignition for constitutional governance
#
# Usage:
#   1. Manual: .\scripts\auto_start_mcp.ps1
#   2. Task Scheduler: Create task to run this on system startup
#   3. Docker: Use docker-compose for containerized MCP

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

# Configuration
$ARIFOS_ROOT = "c:\Users\User\OneDrive\Documents\GitHub\arifOS"
$PYTHON_EXE = "C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe"
$MCP_ENTRY = "$ARIFOS_ROOT\scripts\arifos_mcp_entry.py"
$LOG_DIR = "$ARIFOS_ROOT\logs"
$LOG_FILE = "$LOG_DIR\mcp_autostart.log"
$PID_FILE = "$LOG_DIR\mcp.pid"

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# F2 (Truth): Logging function
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp [MCP-AUTO] $Message" | Tee-Object -FilePath $LOG_FILE -Append
}

# F6 (Amanah): Check if MCP is running
function Test-MCPRunning {
    if (Test-Path $PID_FILE) {
        $mcpPid = Get-Content $PID_FILE
        $process = Get-Process -Id $mcpPid -ErrorAction SilentlyContinue
        if ($process -and $process.ProcessName -eq "python") {
            return $true
        }
    }
    return $false
}

# 000 Stage: Start MCP Server
function Start-MCPServer {
    Write-Log "=== 000 STAGE: MCP Auto-Ignition Starting ==="

    if (Test-MCPRunning) {
        Write-Log "MCP server already running (PID: $(Get-Content $PID_FILE))"
        return
    }

    Write-Log "Starting MCP server..."
    Write-Log "Python: $PYTHON_EXE"
    Write-Log "Entry: $MCP_ENTRY"

    # Start MCP as background process
    $process = Start-Process -FilePath $PYTHON_EXE `
                            -ArgumentList $MCP_ENTRY `
                            -WorkingDirectory $ARIFOS_ROOT `
                            -PassThru `
                            -WindowStyle Hidden `
                            -RedirectStandardOutput "$LOG_DIR\mcp_stdout.log" `
                            -RedirectStandardError "$LOG_DIR\mcp_stderr.log"

    # Save PID
    $process.Id | Out-File -FilePath $PID_FILE -Encoding UTF8

    # Wait and verify
    Start-Sleep -Seconds 2

    if (Test-MCPRunning) {
        Write-Log "✅ MCP server started successfully (PID: $($process.Id))"
        Write-Log "=== 000 STAGE: MCP Auto-Ignition Complete ==="
    } else {
        Write-Log "❌ MCP server failed to start"
        Write-Log "Check logs: $LOG_DIR\mcp_stderr.log"
    }
}

# 999 Stage: Stop MCP Server
function Stop-MCPServer {
    Write-Log "=== 999 STAGE: MCP Graceful Shutdown Starting ==="

    if (-not (Test-MCPRunning)) {
        Write-Log "MCP server not running"
        return
    }

    $mcpPid = Get-Content $PID_FILE
    Write-Log "Stopping MCP server (PID: $mcpPid)..."

    Stop-Process -Id $mcpPid -Force -ErrorAction SilentlyContinue
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 1

    if (-not (Test-MCPRunning)) {
        Write-Log "✅ MCP server stopped successfully"
        Write-Log "=== 999 STAGE: Shutdown Complete ==="
    } else {
        Write-Log "⚠️ MCP server may still be running"
    }
}

# Status check
function Get-MCPStatus {
    Write-Log "=== MCP Server Status ==="

    if (Test-MCPRunning) {
        $mcpPid = Get-Content $PID_FILE
        $process = Get-Process -Id $mcpPid
        Write-Log "Status: RUNNING"
        Write-Log "PID: $mcpPid"
        Write-Log "Started: $($process.StartTime)"
        Write-Log "CPU: $($process.CPU)s"
        Write-Log "Memory: $([math]::Round($process.WorkingSet64/1MB, 2))MB"
    } else {
        Write-Log "Status: STOPPED"
    }

    Write-Log "Logs: $LOG_DIR"
}

# F11 (Command Auth): Install as Windows Task Scheduler job
function Install-AutoStart {
    Write-Log "=== Installing MCP Auto-Start ==="

    $taskName = "arifOS-MCP-AutoStart"
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
                                       -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Start"

    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    # Check if task exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Log "Removing existing task..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # Register task
    Register-ScheduledTask -TaskName $taskName `
                          -Action $action `
                          -Trigger $trigger `
                          -Principal $principal `
                          -Settings $settings `
                          -Description "Auto-start arifOS MCP server on system boot (000 Stage)" | Out-Null

    Write-Log "✅ Task Scheduler job created: $taskName"
    Write-Log "MCP will auto-start on next system boot"
    Write-Log "To test now, run: .\scripts\auto_start_mcp.ps1 -Start"
}

# Uninstall auto-start
function Uninstall-AutoStart {
    Write-Log "=== Uninstalling MCP Auto-Start ==="

    $taskName = "arifOS-MCP-AutoStart"
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Log "✅ Task Scheduler job removed"
    } else {
        Write-Log "Task not found, nothing to uninstall"
    }

    # Stop if running
    if (Test-MCPRunning) {
        Stop-MCPServer
    }
}

# Main execution
switch ($true) {
    $Install   { Install-AutoStart }
    $Uninstall { Uninstall-AutoStart }
    $Start     { Start-MCPServer }
    $Stop      { Stop-MCPServer }
    $Status    { Get-MCPStatus }
    default    {
        Write-Host @"
arifOS MCP Auto-Start Manager

Usage:
  .\scripts\auto_start_mcp.ps1 -Install    Install auto-start (runs on system boot)
  .\scripts\auto_start_mcp.ps1 -Uninstall  Remove auto-start
  .\scripts\auto_start_mcp.ps1 -Start      Start MCP server now
  .\scripts\auto_start_mcp.ps1 -Stop       Stop MCP server
  .\scripts\auto_start_mcp.ps1 -Status     Check MCP status

Examples:
  # Install auto-start
  .\scripts\auto_start_mcp.ps1 -Install

  # Start now (manual)
  .\scripts\auto_start_mcp.ps1 -Start

  # Check status
  .\scripts\auto_start_mcp.ps1 -Status

Logs: $LOG_DIR
"@
    }
}
