# arifOS Unified Auto-Start Setup (000 Stage)
# Sets up both MCP and Docker REST API to auto-start on boot
#
# Usage: .\scripts\setup_auto_start.ps1

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║  arifOS Auto-Start Setup - 000 Stage Ignition            ║
║  Constitutional Governance System                         ║
╚════════════════════════════════════════════════════════════╝

This script will configure:
  ✓ MCP Server (stdio) → Auto-start on boot
  ✓ Docker REST API → Auto-restart on failure
  ✓ Logging → logs/ directory
  ✓ Health checks → Verify services running

"@ -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script should be run as Administrator for best results." -ForegroundColor Yellow
    Write-Host "   (Task Scheduler installation requires admin)" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') {
        exit 0
    }
}

Write-Host "`n=== Step 1: MCP Auto-Start ===" -ForegroundColor Green

# Check if auto_start_mcp.ps1 exists
if (Test-Path ".\scripts\auto_start_mcp.ps1") {
    Write-Host "✓ Found auto_start_mcp.ps1" -ForegroundColor Green

    $installMCP = Read-Host "`nInstall MCP auto-start (Windows Task Scheduler)? (Y/n)"
    if ($installMCP -ne 'n') {
        Write-Host "`nInstalling MCP auto-start..." -ForegroundColor Cyan
        & ".\scripts\auto_start_mcp.ps1" -Install

        Write-Host "`nChecking MCP status..." -ForegroundColor Cyan
        & ".\scripts\auto_start_mcp.ps1" -Status
    }
} else {
    Write-Host "✗ auto_start_mcp.ps1 not found, skipping MCP setup" -ForegroundColor Red
}

Write-Host "`n=== Step 2: Docker Auto-Restart ===" -ForegroundColor Green

# Check if Docker is installed
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerInstalled) {
    Write-Host "✓ Docker installed" -ForegroundColor Green

    # Check if docker-compose.yml exists
    if (Test-Path ".\docker-compose.yml") {
        Write-Host "✓ Found docker-compose.yml" -ForegroundColor Green
        Write-Host "  Restart policy: unless-stopped (already configured)" -ForegroundColor Gray

        $startDocker = Read-Host "`nStart Docker containers now? (Y/n)"
        if ($startDocker -ne 'n') {
            Write-Host "`nStarting Docker services..." -ForegroundColor Cyan
            docker-compose up -d

            Write-Host "`nWaiting for services to start..." -ForegroundColor Cyan
            Start-Sleep -Seconds 5

            Write-Host "`nDocker container status:" -ForegroundColor Cyan
            docker-compose ps

            Write-Host "`nTesting health endpoints..." -ForegroundColor Cyan
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
                Write-Host "✓ arifOS API: $($response.StatusCode) - Healthy" -ForegroundColor Green
            } catch {
                Write-Host "✗ arifOS API: Not responding (may still be starting)" -ForegroundColor Yellow
            }

            try {
                $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -TimeoutSec 5
                Write-Host "✓ Qdrant: $($response.StatusCode) - Healthy" -ForegroundColor Green
            } catch {
                Write-Host "✗ Qdrant: Not responding (may still be starting)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "✗ docker-compose.yml not found" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Docker not installed, skipping Docker setup" -ForegroundColor Red
    Write-Host "  Install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
}

Write-Host "`n=== Step 3: Verification ===" -ForegroundColor Green

Write-Host "`nCreating logs directory..." -ForegroundColor Cyan
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" -Force | Out-Null
    Write-Host "✓ Created logs/ directory" -ForegroundColor Green
} else {
    Write-Host "✓ logs/ directory exists" -ForegroundColor Green
}

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Setup Complete! 000 Stage Ignition Configured           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host @"

Next Steps:

1. MCP Server (Local IDE):
   - Status: .\scripts\auto_start_mcp.ps1 -Status
   - Logs:   Get-Content logs\mcp_autostart.log -Tail 20
   - Config: Add to Claude Desktop (see AUTO_START_GUIDE.md)

2. Docker REST API (Cloud):
   - Status: docker-compose ps
   - Logs:   docker-compose logs -f arifos
   - API:    http://localhost:8000/docs

3. Reboot Test:
   - Restart-Computer
   - After reboot, verify both services auto-started

Documentation:
  - Full guide: AUTO_START_GUIDE.md
  - MCP tools:  MCP_CONSOLIDATION_COMPLETE_v46.3.md (in .antigravity/)
  - Docker:     DOCKER_GUIDE.md

"@ -ForegroundColor White

Write-Host "DITEMPA BUKAN DIBERI - The system is forged." -ForegroundColor Magenta
Write-Host ""
