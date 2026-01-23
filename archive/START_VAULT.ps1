
# START_VAULT.ps1 - Start Vault 999 Infrastructure (Port 9999)

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  VAULT 999 LAUNCHER (v46.1)" -ForegroundColor Cyan
Write-Host "  Port: 9999 (Bypassing System Block)" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Kill old processes
Write-Host "1. Killing old python/cloudflared..."
Stop-Process -Name "python" -ErrorAction SilentlyContinue
Stop-Process -Name "cloudflared" -ErrorAction SilentlyContinue

# 2. Start Server (Background)
Write-Host "2. Starting Server on Port 9999..."
$server = Start-Process python -ArgumentList "arifos_core/mcp/vault999_server.py" -PassThru -NoNewWindow

# 3. Start Tunnel (Pointing to 9999)
Write-Host "3. Starting Tunnel (Mapping 9999 -> Cloudflare)..."
# We override the local-service URL to 9999
Start-Process cloudflared -ArgumentList "tunnel --url https://localhost:9999 run vault999" -NoNewWindow

Write-Host "==============================================" -ForegroundColor Green
Write-Host "  SYSTEM LIVE" -ForegroundColor Green
Write-Host "  Server PID: $($server.Id)"
Write-Host "  Monitor this window."
Write-Host "==============================================" -ForegroundColor Green
