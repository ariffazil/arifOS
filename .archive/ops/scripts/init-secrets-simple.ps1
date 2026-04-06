param(
    [string]$SecretsDir = "C:\Users\User\arifOS\secrets",
    [int]$SecretLength = 64
)
$ErrorActionPreference = "Stop"
Write-Host "Initializing arifOS Secrets..." -ForegroundColor Cyan
if (!(Test-Path $SecretsDir)) { New-Item -ItemType Directory -Force -Path $SecretsDir | Out-Null }
$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
function Gen-Secret([int]$len) {
    $s = -join ((1..$len) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $s
}
$gov = Gen-Secret $SecretLength
$ses = Gen-Secret $SecretLength
$pg = Gen-Secret 32
$red = Gen-Secret 32
[IO.File]::WriteAllText((Join-Path $SecretsDir "governance.secret"), $gov, [System.Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $SecretsDir "session.secret"), $ses, [System.Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $SecretsDir "postgres.password"), $pg, [System.Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $SecretsDir "redis.password"), $red, [System.Text.UTF8Encoding]::new($false))
Write-Host "Secrets generated in $SecretsDir" -ForegroundColor Green
Write-Host "ARIFOS_GOVERNANCE_SECRET_FILE=$(Join-Path $SecretsDir "governance.secret")"
Write-Host "ARIFOS_SESSION_SECRET_FILE=$(Join-Path $SecretsDir "session.secret")"
Write-Host "POSTGRES_PASSWORD_FILE=$(Join-Path $SecretsDir "postgres.password")"
Write-Host "REDIS_PASSWORD_FILE=$(Join-Path $SecretsDir "redis.password")"
