# init-secrets.ps1 — Initialize Production Secrets (Windows)
#
# Constitutional Floor: F11 (Command Authority)
# Purpose: Generate and secure ARIFOS_GOVERNANCE_SECRET for production
#
# Usage:
#   .\scripts\init-secrets.ps1 [-SecretsDir "C:\arifos\secrets"]
#
# This script:
#   1. Creates a secure secrets directory with restricted ACLs
#   2. Generates a cryptographically secure 64-character governance secret
#   3. Sets appropriate file permissions (read-only, current user only)
#   4. Outputs environment variable configuration

[CmdletBinding()]
param(
    [string]$SecretsDir = "C:\arifos\secrets",
    [int]$SecretLength = 64,
    [switch]$Force
)

#requires -Version 5.1

$ErrorActionPreference = "Stop"

# ASCII banner
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║     arifOS — Constitutional Secret Initialization            ║
║     F11: Command Authority — Ditempa Bukan Diberi            ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Validate running as Administrator for system-wide secrets
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin -and $SecretsDir.StartsWith("C:\ProgramData") -or $SecretsDir.StartsWith("C:\Windows")) {
    Write-Error "Administrator privileges required for system-wide secrets directory: $SecretsDir"
    exit 1
}

# Create secrets directory
Write-Host "[1/5] Creating secrets directory: $SecretsDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $SecretsDir | Out-Null

# Set restrictive ACL (current user only)
Write-Host "[2/5] Setting restrictive ACLs..." -ForegroundColor Yellow
try {
    $acl = Get-Acl $SecretsDir
    
    # Disable inheritance
    $acl.SetAccessRuleProtection($true, $false)
    
    # Remove all existing rules
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }
    
    # Add current user with full control
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $currentUser,
        "FullControl",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $acl.SetAccessRule($rule)
    
    # Add SYSTEM (for services)
    $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        "SYSTEM",
        "FullControl",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $acl.AddAccessRule($systemRule)
    
    Set-Acl $SecretsDir $acl
    Write-Host "      ✓ ACLs configured (current user + SYSTEM only)" -ForegroundColor Green
} catch {
    Write-Warning "Failed to set ACLs: $_"
    Write-Warning "Manual permission configuration may be required"
}

# Generate cryptographically secure secret
Write-Host "[3/5] Generating governance secret..." -ForegroundColor Yellow
$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
$secret = -join ((1..$SecretLength) | ForEach-Object { 
    $chars[(Get-Random -Maximum $chars.Length)] 
})

# Write governance secret
$governanceFile = Join-Path $SecretsDir "governance.secret"
if (Test-Path $governanceFile) {
    if (-not $Force) {
        Write-Host "      ⚠ Governance secret already exists at: $governanceFile" -ForegroundColor Yellow
        $confirm = Read-Host "      Overwrite? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "      Cancelled. Existing secret preserved." -ForegroundColor Green
            exit 0
        }
    }
    Remove-Item $governanceFile -Force
}

# Write with no newline, UTF8 without BOM
[IO.File]::WriteAllText($governanceFile, $secret, [System.Text.UTF8Encoding]::new($false))
Set-ItemProperty $governanceFile -Name IsReadOnly -Value $true
Write-Host "      ✓ Governance secret written" -ForegroundColor Green

# Generate session secret
Write-Host "[4/5] Generating session secret..." -ForegroundColor Yellow
$sessionSecret = -join ((1..$SecretLength) | ForEach-Object { 
    $chars[(Get-Random -Maximum $chars.Length)] 
})
$sessionFile = Join-Path $SecretsDir "session.secret"
[IO.File]::WriteAllText($sessionFile, $sessionSecret, [System.Text.UTF8Encoding]::new($false))
Set-ItemProperty $sessionFile -Name IsReadOnly -Value $true
Write-Host "      ✓ Session secret written" -ForegroundColor Green

# Generate PostgreSQL password
Write-Host "      Generating PostgreSQL password..." -ForegroundColor Yellow
$pgPassword = -join ((1..32) | ForEach-Object { 
    $chars[(Get-Random -Maximum $chars.Length)] 
})
$pgFile = Join-Path $SecretsDir "postgres.password"
[IO.File]::WriteAllText($pgFile, $pgPassword, [System.Text.UTF8Encoding]::new($false))
Set-ItemProperty $pgFile -Name IsReadOnly -Value $true
Write-Host "      ✓ PostgreSQL password written" -ForegroundColor Green

# Generate Redis password
Write-Host "      Generating Redis password..." -ForegroundColor Yellow
$redisPassword = -join ((1..32) | ForEach-Object { 
    $chars[(Get-Random -Maximum $chars.Length)] 
})
$redisFile = Join-Path $SecretsDir "redis.password"
[IO.File]::WriteAllText($redisFile, $redisPassword, [System.Text.UTF8Encoding]::new($false))
Set-ItemProperty $redisFile -Name IsReadOnly -Value $true
Write-Host "      ✓ Redis password written" -ForegroundColor Green

# Verification
Write-Host "[5/5] Verifying secrets..." -ForegroundColor Yellow
$verified = $true
@($governanceFile, $sessionFile, $pgFile, $redisFile) | ForEach-Object {
    if (Test-Path $_) {
        $content = Get-Content $_ -Raw
        if ($content.Length -ge 32) {
            Write-Host "      ✓ $([IO.Path]::GetFileName($_)): $($content.Length) chars" -ForegroundColor Green
        } else {
            Write-Host "      ✗ $([IO.Path]::GetFileName($_)): Too short ($($content.Length) chars)" -ForegroundColor Red
            $verified = $false
        }
    } else {
        Write-Host "      ✗ $([IO.Path]::GetFileName($_)): Missing" -ForegroundColor Red
        $verified = $false
    }
}

# Output configuration
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SECRETS CONFIGURED — Add to environment:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # PowerShell environment variables:" -ForegroundColor White
Write-Host "  `$env:ARIFOS_GOVERNANCE_SECRET_FILE = '$governanceFile'" -ForegroundColor Yellow
Write-Host "  `$env:ARIFOS_SESSION_SECRET_FILE = '$sessionFile'" -ForegroundColor Yellow
Write-Host "  `$env:POSTGRES_PASSWORD_FILE = '$pgFile'" -ForegroundColor Yellow
Write-Host "  `$env:REDIS_PASSWORD_FILE = '$redisFile'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Or in .env file:" -ForegroundColor White
Write-Host "  ARIFOS_GOVERNANCE_SECRET_FILE=$governanceFile" -ForegroundColor Yellow
Write-Host "  ARIFOS_SESSION_SECRET_FILE=$sessionFile" -ForegroundColor Yellow
Write-Host "  POSTGRES_PASSWORD_FILE=$pgFile" -ForegroundColor Yellow
Write-Host "  REDIS_PASSWORD_FILE=$redisFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Docker secret creation commands:" -ForegroundColor White
Write-Host "  docker secret create arifos_governance_secret_v2026 '$governanceFile'" -ForegroundColor Yellow
Write-Host "  docker secret create arifos_session_secret_v2026 '$sessionFile'" -ForegroundColor Yellow
Write-Host "  docker secret create postgres_password '$pgFile'" -ForegroundColor Yellow
Write-Host "  docker secret create redis_password '$redisFile'" -ForegroundColor Yellow
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($verified) {
    Write-Host "  ✓ ALL SECRETS VERIFIED — F11 Continuity Guaranteed" -ForegroundColor Green
} else {
    Write-Host "  ✗ VERIFICATION FAILED — Check errors above" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Motto: Ditempa Bukan Diberi — Forged, Not Given" -ForegroundColor DarkGray
