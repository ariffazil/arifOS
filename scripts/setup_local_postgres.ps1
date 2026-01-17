# Local Postgres Setup for VAULT-999 (Alternative to Docker)
# Version: v47.1
# Purpose: Install and configure local Postgres when Docker unavailable
# Authority: Ω Claude Code (Engineer)

Write-Host "=== VAULT-999 Local Postgres Setup (Docker Alternative) ===" -ForegroundColor Cyan
Write-Host "Version: v47.1 | Date: 2026-01-17" -ForegroundColor Gray
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "  Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Function to check if Postgres is installed
function Test-PostgresInstalled {
    try {
        $pgVersion = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Function to check if Postgres service is running
function Test-PostgresRunning {
    $service = Get-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue
    return ($service -and $service.Status -eq "Running")
}

# Step 1: Check installation
Write-Host "[1/5] Checking Postgres installation..." -ForegroundColor Cyan

if (Test-PostgresInstalled) {
    Write-Host "  Postgres 16 is installed!" -ForegroundColor Green
}
else {
    Write-Host "  Postgres 16 is NOT installed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installation options:" -ForegroundColor Cyan
    Write-Host "  [1] Auto-install via winget (recommended)" -ForegroundColor White
    Write-Host "  [2] Manual download link" -ForegroundColor White
    Write-Host "  [Q] Quit" -ForegroundColor White
    Write-Host ""

    $choice = Read-Host "Select option [1/2/Q]"

    switch ($choice.ToUpper()) {
        "1" {
            Write-Host "  Installing PostgreSQL 16 via winget..." -ForegroundColor Yellow
            winget install --id PostgreSQL.PostgreSQL.16 --silent

            if ($LASTEXITCODE -ne 0) {
                Write-Host "  Installation failed" -ForegroundColor Red
                Write-Host "  Try manual installation: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
                exit 1
            }

            Write-Host "  PostgreSQL 16 installed successfully!" -ForegroundColor Green
        }
        "2" {
            Write-Host "  Download PostgreSQL 16 from:" -ForegroundColor Cyan
            Write-Host "  https://www.enterprisedb.com/downloads/postgres-postgresql-downloads" -ForegroundColor White
            Write-Host ""
            Write-Host "  After installation, re-run this script" -ForegroundColor Yellow
            Start-Process "https://www.enterprisedb.com/downloads/postgres-postgresql-downloads"
            exit 0
        }
        default {
            Write-Host "Cancelled by user" -ForegroundColor Gray
            exit 0
        }
    }
}

Write-Host ""

# Step 2: Check service
Write-Host "[2/5] Checking Postgres service..." -ForegroundColor Cyan

if (Test-PostgresRunning) {
    Write-Host "  Postgres service is running!" -ForegroundColor Green
}
else {
    Write-Host "  Postgres service is NOT running" -ForegroundColor Yellow
    Write-Host "  Starting service..." -ForegroundColor Gray

    Start-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 3

    if (Test-PostgresRunning) {
        Write-Host "  Postgres service started successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "  Failed to start Postgres service" -ForegroundColor Red
        Write-Host "  Try manually: Services -> postgresql-x64-16 -> Start" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Step 3: Create database and user
Write-Host "[3/5] Creating arifOS database and user..." -ForegroundColor Cyan

$postgresPath = "C:\Program Files\PostgreSQL\16\bin"
$env:PATH = "$postgresPath;$env:PATH"

# Prompt for postgres superuser password
Write-Host "  Enter postgres superuser password (set during installation):" -ForegroundColor Gray
$postgresPassword = Read-Host -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

# Create SQL commands
$createUserSQL = @"
-- Create arifOS user
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'arifos') THEN
        CREATE USER arifos WITH PASSWORD 'arifos_local_dev';
    END IF;
END
`$`$;
"@

$createDbSQL = @"
-- Create arifOS database
SELECT 'CREATE DATABASE arifos_vault999 OWNER arifos ENCODING UTF8'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'arifos_vault999')\gexec
"@

# Execute SQL
Write-Host "  Creating user 'arifos'..." -ForegroundColor Gray
$env:PGPASSWORD = $postgresPasswordPlain
& "$postgresPath\psql.exe" -U postgres -h localhost -c $createUserSQL

Write-Host "  Creating database 'arifos_vault999'..." -ForegroundColor Gray
& "$postgresPath\psql.exe" -U postgres -h localhost -c $createDbSQL

# Grant permissions
$grantSQL = "GRANT ALL PRIVILEGES ON DATABASE arifos_vault999 TO arifos;"
& "$postgresPath\psql.exe" -U postgres -h localhost -c $grantSQL

Write-Host "  Database and user created successfully!" -ForegroundColor Green

Write-Host ""

# Step 4: Load schema
Write-Host "[4/5] Loading VAULT-999 schema..." -ForegroundColor Cyan

$schemaPath = Join-Path (Get-Item $PSScriptRoot).Parent.FullName "arifos_core\memory\ledger\schema.sql"

if (Test-Path $schemaPath) {
    Write-Host "  Found schema at: $schemaPath" -ForegroundColor Gray

    $env:PGPASSWORD = "arifos_local_dev"
    & "$postgresPath\psql.exe" -U arifos -h localhost -d arifos_vault999 -f $schemaPath

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Schema loaded successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "  Failed to load schema" -ForegroundColor Red
        Write-Host "  Check logs above for SQL errors" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  Schema file not found: $schemaPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Verify installation
Write-Host "[5/5] Verifying installation..." -ForegroundColor Cyan

$env:PGPASSWORD = "arifos_local_dev"

# Check tables
Write-Host "  Checking tables..." -ForegroundColor Gray
$tables = & "$postgresPath\psql.exe" -U arifos -h localhost -d arifos_vault999 -t -c "\dt" 2>&1

if ($tables -match "cooling_ledger" -and $tables -match "zkpc_receipts" -and $tables -match "ccc_constitutional_floors") {
    Write-Host "  All tables created successfully!" -ForegroundColor Green
}
else {
    Write-Host "  Some tables missing - check schema load" -ForegroundColor Yellow
}

# Check F1-F12 seed data
Write-Host "  Checking F1-F12 seed data..." -ForegroundColor Gray
$floorCount = & "$postgresPath\psql.exe" -U arifos -h localhost -d arifos_vault999 -t -c "SELECT COUNT(*) FROM ccc_constitutional_floors" 2>&1

if ($floorCount -match "12") {
    Write-Host "  All 12 constitutional floors seeded!" -ForegroundColor Green
}
else {
    Write-Host "  Floor seed data missing (expected 12, got $floorCount)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== VAULT-999 Local Postgres Ready ===" -ForegroundColor Green
Write-Host ""
Write-Host "Connection details:" -ForegroundColor Cyan
Write-Host "  Host:     localhost" -ForegroundColor White
Write-Host "  Port:     5432" -ForegroundColor White
Write-Host "  Database: arifos_vault999" -ForegroundColor White
Write-Host "  User:     arifos" -ForegroundColor White
Write-Host "  Password: arifos_local_dev" -ForegroundColor White
Write-Host ""
Write-Host "Connection string:" -ForegroundColor Cyan
Write-Host "  postgresql://arifos:arifos_local_dev@localhost:5432/arifos_vault999" -ForegroundColor Gray
Write-Host ""
Write-Host "Test connection:" -ForegroundColor Cyan
Write-Host "  psql -U arifos -h localhost -d arifos_vault999" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Update Python code to use this database" -ForegroundColor White
Write-Host "  2. Run integration tests" -ForegroundColor White
Write-Host "  3. Verify zkPC/cooling write to database" -ForegroundColor White
Write-Host ""
Write-Host "DITEMPA BUKAN DIBERI - Local database forged and ready." -ForegroundColor Cyan

# Save connection info to .env file
$envPath = Join-Path (Get-Item $PSScriptRoot).Parent.FullName ".env.local"
$envContent = @"
# VAULT-999 Local Postgres Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Database Connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=arifos_vault999
POSTGRES_USER=arifos
POSTGRES_PASSWORD=arifos_local_dev

# Connection String
DATABASE_URL=postgresql://arifos:arifos_local_dev@localhost:5432/arifos_vault999

# Redis (optional - install separately or skip)
REDIS_HOST=localhost
REDIS_PORT=6379

# Qdrant (optional - install separately or skip)
QDRANT_HOST=localhost
QDRANT_PORT=6333
"@

Set-Content -Path $envPath -Value $envContent
Write-Host "Configuration saved to: .env.local" -ForegroundColor Green
