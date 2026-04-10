#!/usr/bin/env pwsh
# arifOS Test and Deploy Script
# Tests with MCP Inspector and deploys to VPS/Horizon
#
# Usage:
#   .\test-and-deploy.ps1 test        # Run tests only
#   .\test-and-deploy.ps1 vps         # Deploy to VPS
#   .\test-and-deploy.ps1 horizon     # Deploy to Horizon

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("test", "vps", "horizon")]
    [string]$Target
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  arifOS Test and Deploy" -ForegroundColor Cyan
Write-Host "  Target: $Target" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Phase
if ($Target -eq "test" -or $Target -eq "vps" -or $Target -eq "horizon") {
    Write-Info "Running MCP Inspector tests..."
    
    try {
        python arifosmcp/evals/mcp_inspector_test.py --all --output deployments/mcp_inspector_report.json
        if ($LASTEXITCODE -ne 0) {
            Write-Error "MCP Inspector tests FAILED"
            exit 1
        }
        Write-Success "MCP Inspector tests PASSED"
    } catch {
        Write-Error "MCP Inspector tests failed: $_"
        exit 1
    }
    
    Write-Info "Running deployment gate tests..."
    try {
        python arifosmcp/evals/deploy_gate.py --output deployments/deploy_gate_report.json
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Deployment gates PASSED (SEAL)"
        } elseif ($LASTEXITCODE -eq 2) {
            Write-Warn "Deployment gates: HOLD (needs human ratification)"
        } else {
            Write-Warn "Deployment gates: SABAR or VOID (review required)"
        }
    } catch {
        Write-Warn "Deployment gate check had issues: $_"
    }
}

# Deploy Phase
if ($Target -eq "vps") {
    Write-Info "Deploying to VPS..."
    
    # Check if we should proceed
    $proceed = Read-Host "Continue with VPS deployment? (y/N)"
    if ($proceed -ne 'y' -and $proceed -ne 'Y') {
        Write-Info "Deployment cancelled"
        exit 0
    }
    
    # Build Docker image
    Write-Info "Building Docker image..."
    docker build -t arifos/arifosmcp:latest .
    
    # Deploy via SSH (requires SSH access configured)
    Write-Info "Deploying via SSH..."
    ssh root@arif-fazil.com "cd /root/arifOS && git pull origin main && docker-compose -f docker-compose.yml -f deployments/vps-deploy.yml up -d"
    
    Write-Success "VPS deployment complete!"
    Write-Info "Check health: https://arifosmcp.arif-fazil.com/health"
}

if ($Target -eq "horizon") {
    Write-Info "Deploying to Horizon..."
    
    $proceed = Read-Host "Continue with Horizon deployment? (y/N)"
    if ($proceed -ne 'y' -and $proceed -ne 'Y') {
        Write-Info "Deployment cancelled"
        exit 0
    }
    
    Write-Info "Building Docker image..."
    docker build -t arifos/arifosmcp:horizon .
    
    Write-Info "Deploying via SSH..."
    ssh root@horizon.arif-fazil.com "cd /root/arifOS && git pull origin main && docker-compose -f docker-compose.yml -f deployments/horizon-deploy.yml up -d"
    
    Write-Success "Horizon deployment complete!"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DITEMPA BUKAN DIBERI" -ForegroundColor Green
Write-Host "  999 SEAL ALIVE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
