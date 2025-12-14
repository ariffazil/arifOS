# Start arifOS API server with SEA-LION via LiteLLM
# PowerShell script for Windows

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "arifOS v38.2 - SEA-LION LiteLLM Gateway" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Create one from .env.example:" -ForegroundColor Yellow
    Write-Host "  Copy-Item .env.example .env" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then add your SEA-LION API key:" -ForegroundColor Yellow
    Write-Host "  Edit .env and set ARIF_LLM_API_KEY=your-key-here" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Get your key at: https://playground.sea-lion.ai" -ForegroundColor Cyan
    exit 1
}

# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Validate required variables
$apiKey = $env:ARIF_LLM_API_KEY
if (-not $apiKey) {
    Write-Host "[ERROR] ARIF_LLM_API_KEY not set in .env file" -ForegroundColor Red
    Write-Host "Get your key at: https://playground.sea-lion.ai" -ForegroundColor Cyan
    exit 1
}

$provider = if ($env:ARIF_LLM_PROVIDER) { $env:ARIF_LLM_PROVIDER } else { "openai" }
$apiBase = if ($env:ARIF_LLM_API_BASE) { $env:ARIF_LLM_API_BASE } else { "https://api.sea-lion.ai/v1" }
$model = if ($env:ARIF_LLM_MODEL) { $env:ARIF_LLM_MODEL } else { "aisingapore/Llama-SEA-LION-v3-70B-IT" }

Write-Host "[CONFIG] Provider: $provider" -ForegroundColor Green
Write-Host "[CONFIG] API Base: $apiBase" -ForegroundColor Green
Write-Host "[CONFIG] Model: $model" -ForegroundColor Green
Write-Host ""

# Default host and port
$host = if ($env:ARIFOS_API_HOST) { $env:ARIFOS_API_HOST } else { "0.0.0.0" }
$port = if ($env:ARIFOS_API_PORT) { $env:ARIFOS_API_PORT } else { "8000" }

Write-Host "[STARTING] arifOS API server on ${host}:${port}" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn server
uvicorn arifos_core.api.app:app --host $host --port $port --reload
