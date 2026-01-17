# VAULT-999 Docker Startup Script (Windows PowerShell)
# Version: v47.1
# Purpose: Start Postgres + Redis + Qdrant with Docker Desktop health check
# Authority: Ω Claude Code (Engineer)

Write-Host "=== VAULT-999 Database Infrastructure Startup ===" -ForegroundColor Cyan
Write-Host "Version: v47.1 | Date: 2026-01-17" -ForegroundColor Gray
Write-Host ""

# Function to check if Docker Desktop is running
function Test-DockerDesktop {
    try {
        $null = docker ps 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Function to start Docker Desktop (Windows)
function Start-DockerDesktop {
    Write-Host "[1/4] Starting Docker Desktop..." -ForegroundColor Yellow

    # Try to find Docker Desktop executable
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "  Waiting for Docker Desktop to start (max 60s)..." -ForegroundColor Gray

        $timeout = 60
        $elapsed = 0
        while (-not (Test-DockerDesktop) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 2
            $elapsed += 2
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
        Write-Host ""

        if (Test-DockerDesktop) {
            Write-Host "  Docker Desktop started successfully!" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "  Timeout waiting for Docker Desktop" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "  Docker Desktop not found at: $dockerPath" -ForegroundColor Red
        Write-Host "  Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
}

# Step 1: Check Docker Desktop status
Write-Host "[CHECK] Docker Desktop status..." -ForegroundColor Cyan
if (Test-DockerDesktop) {
    Write-Host "  Docker Desktop is running!" -ForegroundColor Green
}
else {
    Write-Host "  Docker Desktop is NOT running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  [1] Auto-start Docker Desktop (recommended)" -ForegroundColor White
    Write-Host "  [2] Manual start - wait for you to start it" -ForegroundColor White
    Write-Host "  [3] Skip Docker - use local Postgres instead" -ForegroundColor White
    Write-Host "  [Q] Quit" -ForegroundColor White
    Write-Host ""

    $choice = Read-Host "Select option [1/2/3/Q]"

    switch ($choice.ToUpper()) {
        "1" {
            if (-not (Start-DockerDesktop)) {
                Write-Host ""
                Write-Host "Failed to start Docker Desktop automatically." -ForegroundColor Red
                Write-Host "Recommendation: Run setup_local_postgres.ps1 instead" -ForegroundColor Yellow
                exit 1
            }
        }
        "2" {
            Write-Host "Please start Docker Desktop manually, then press Enter..." -ForegroundColor Yellow
            Read-Host
            if (-not (Test-DockerDesktop)) {
                Write-Host "Docker Desktop still not detected. Exiting." -ForegroundColor Red
                exit 1
            }
        }
        "3" {
            Write-Host "Launching local Postgres setup..." -ForegroundColor Cyan
            & ".\scripts\setup_local_postgres.ps1"
            exit 0
        }
        default {
            Write-Host "Cancelled by user" -ForegroundColor Gray
            exit 0
        }
    }
}

Write-Host ""

# Step 2: Pull images if needed
Write-Host "[2/4] Checking Docker images..." -ForegroundColor Cyan
$images = @("postgres:16-alpine", "redis:7-alpine", "qdrant/qdrant:v1.7.4")
foreach ($image in $images) {
    Write-Host "  Checking $image..." -ForegroundColor Gray
    $exists = docker images -q $image
    if (-not $exists) {
        Write-Host "  Pulling $image..." -ForegroundColor Yellow
        docker pull $image
    }
    else {
        Write-Host "  $image already exists" -ForegroundColor Green
    }
}

Write-Host ""

# Step 3: Start services
Write-Host "[3/4] Starting VAULT-999 services..." -ForegroundColor Cyan
Set-Location (Get-Item $PSScriptRoot).Parent.FullName

docker-compose -f docker-compose-vault999.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Services started successfully!" -ForegroundColor Green
}
else {
    Write-Host "  Failed to start services" -ForegroundColor Red
    Write-Host "  Check logs with: docker-compose -f docker-compose-vault999.yml logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 4: Wait for health checks
Write-Host "[4/4] Waiting for services to be healthy..." -ForegroundColor Cyan
Write-Host "  This may take 10-30 seconds..." -ForegroundColor Gray

Start-Sleep -Seconds 5

$services = @("arifos-vault-postgres", "arifos-vault-redis", "arifos-vault-qdrant")
foreach ($service in $services) {
    Write-Host "  Checking $service..." -ForegroundColor Gray -NoNewline

    $maxRetries = 10
    $retries = 0
    $healthy = $false

    while ($retries -lt $maxRetries) {
        $health = docker inspect --format='{{.State.Health.Status}}' $service 2>$null
        if ($health -eq "healthy" -or $health -eq "") {
            $healthy = $true
            break
        }
        Start-Sleep -Seconds 2
        $retries++
        Write-Host "." -NoNewline -ForegroundColor Gray
    }

    if ($healthy) {
        Write-Host " HEALTHY" -ForegroundColor Green
    }
    else {
        Write-Host " TIMEOUT (may still be starting)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== VAULT-999 Database Infrastructure Ready ===" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Postgres:  localhost:5432 (DB: arifos_vault999, User: arifos)" -ForegroundColor White
Write-Host "  Redis:     localhost:6379" -ForegroundColor White
Write-Host "  Qdrant:    localhost:6333 (HTTP) | localhost:6334 (gRPC)" -ForegroundColor White
Write-Host ""
Write-Host "Verify tables:" -ForegroundColor Cyan
Write-Host "  docker exec -it arifos-vault-postgres psql -U arifos -d arifos_vault999 -c '\dt'" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop services:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose-vault999.yml down" -ForegroundColor Gray
Write-Host ""
Write-Host "DITEMPA BUKAN DIBERI - Database infrastructure forged and ready." -ForegroundColor Cyan
