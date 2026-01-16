<#
.SYNOPSIS
    System Activation Boot Script for arifOS
    Orchestrates Docker Desktop, Dependencies, and MCP Server startup.

.DESCRIPTION
    1. Checks if Docker Desktop is running. Starts it if not.
    2. Waits for Docker Daemon availability.
    3. Starts Docker dependencies (docker-compose up -d) if available.
    4. Launches MCP Server (scripts/start_cloud_mode.ps1) in new window.

.AUTHOR
    Muhammad Arif bin Fazil (Antigravity Forge)
#>

$ErrorActionPreference = "Stop"

function Assert-DockerRunning {
    Write-Host "🔍 [BOOT] Checking Docker Desktop status..." -ForegroundColor Cyan

    $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

    if (-not $dockerProcess) {
        Write-Host "⚠️ [BOOT] Docker Desktop is NOT running. Attempting to start..." -ForegroundColor Yellow
        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

        if (Test-Path $dockerPath) {
            Start-Process $dockerPath
            Write-Host "⏳ [BOOT] Waiting for Docker Desktop to initialize (this may take a minute)..." -ForegroundColor Yellow

            # Polling loop for Docker daemon
            $retries = 30
            while ($retries -gt 0) {
                docker info > $null 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ [BOOT] Docker Desktop is READY!" -ForegroundColor Green
                    return
                }
                Start-Sleep -Seconds 2
                Write-Host "." -NoNewline -ForegroundColor Gray
                $retries--
            }
            Write-Error "❌ [BOOT] Timed out waiting for Docker Daemon."
        } else {
            Write-Error "❌ [BOOT] Docker Desktop executable not found at: $dockerPath"
        }
    } else {
        # Process exists, check daemon
        docker info > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ [BOOT] Docker Desktop is running and responsive." -ForegroundColor Green
        } else {
             Write-Host "⚠️ [BOOT] Docker process running but daemon unresponsive. Waiting..." -ForegroundColor Yellow
             Start-Sleep -Seconds 5
        }
    }
}

function Start-Dependencies {
    Write-Host "🔍 [BOOT] Checking for Docker dependencies..." -ForegroundColor Cyan
    if (Test-Path "docker-compose.yml") {
        Write-Host "🚀 [BOOT] Starting containers via docker-compose..." -ForegroundColor Green
        docker-compose up -d
    } else {
        Write-Host "ℹ️ [BOOT] No docker-compose.yml found. Skipping container startup." -ForegroundColor Gray
    }
}

function Start-MCPServer {
    Write-Host "🔍 [BOOT] Launching MCP Server..." -ForegroundColor Cyan
    $mcpScript = "scripts/start_cloud_mode.ps1"

    if (Test-Path $mcpScript) {
        Write-Host "🚀 [BOOT] Spawning MCP Server in external window..." -ForegroundColor Green
        # Use Start-Process to run in new window, non-blocking
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $mcpScript
    } else {
        Write-Error "❌ [BOOT] MCP startup script not found: $mcpScript"
    }
}

# --- Main Execution ---
try {
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host "   arifOS SYSTEM BOOT SEQUENCE            " -ForegroundColor Magenta
    Write-Host "==========================================" -ForegroundColor Magenta

    Assert-DockerRunning
    Start-Dependencies
    Start-MCPServer

    Write-Host "`n✅ [BOOT] System Activation Sequence Complete." -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Magenta
} catch {
    Write-Error "❌ [BOOT] Critical Failure: $_"
}
