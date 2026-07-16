[CmdletBinding()]
param(
    [switch]$InstallDeps,
    [switch]$StartLocalRuntime
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $repoRoot "CONFIG\mcp-clients.local.json"
$healthUrl = "http://127.0.0.1:8088/health"
$runtimeUrl = "http://127.0.0.1:8088/mcp"
$remoteUrl = "https://mcp.arif-fazil.com/mcp"

function Require-Command {
    param([string]$Name, [string]$Hint)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Missing required command '$Name'. $Hint"
    }
    return $cmd
}

function Get-PythonVersion {
    $output = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if (-not $output) {
        throw "Unable to determine Python version."
    }
    return [version]$output.Trim()
}

function Test-HttpJson {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        return [pscustomobject]@{
            Ok = $true
            StatusCode = [int]$response.StatusCode
        }
    } catch {
        return [pscustomobject]@{
            Ok = $false
            StatusCode = $null
        }
    }
}

Write-Host "=== arifOS Local Agent Connectivity Bootstrap ==="
Write-Host "Repo root: $repoRoot"
Write-Host "Client config: $configPath"
Write-Host ""

Require-Command -Name "python" -Hint "Install Python 3.12+ and ensure it is on PATH." | Out-Null
$pythonVersion = Get-PythonVersion
if ($pythonVersion -lt [version]"3.12") {
    throw "Python 3.12+ is required. Found $pythonVersion."
}
Write-Host "Python OK: $pythonVersion"

Require-Command -Name "uv" -Hint "Install uv from https://docs.astral.sh/uv/ and ensure it is on PATH." | Out-Null
Write-Host "uv OK"

if ($InstallDeps) {
    Write-Host ""
    Write-Host "Installing repo dependencies with uv sync --all-extras ..."
    Push-Location $repoRoot
    try {
        & uv sync --all-extras
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Remote arifOS MCP:"
Write-Host "  $remoteUrl"

$localHealth = Test-HttpJson -Url $healthUrl
if ($localHealth.Ok) {
    Write-Host "Local arifOS runtime: reachable at $runtimeUrl"
} else {
    Write-Host "Local arifOS runtime: not running at $runtimeUrl"
    if ($StartLocalRuntime) {
        Write-Host ""
        Write-Host "Starting local runtime with uv run python -m arifosmcp.runtime.server ..."
        Start-Process -FilePath "uv" -ArgumentList @("run", "python", "-m", "arifosmcp.runtime.server") -WorkingDirectory $repoRoot
        Start-Sleep -Seconds 5
        $localHealth = Test-HttpJson -Url $healthUrl
        if ($localHealth.Ok) {
            Write-Host "Local arifOS runtime: reachable after start"
        } else {
            Write-Warning "Local runtime did not become reachable yet. Check the started process output."
        }
    } else {
        Write-Host "  Start it with: uv run python -m arifosmcp.runtime.server"
    }
}

Write-Host ""
Write-Host "For GitHub Copilot CLI:"
Write-Host "  1. Run /mcp"
Write-Host "  2. Add arifOS using the remote URL or the local URL from $configPath"
Write-Host ""
Write-Host "Blessed MCP client config:"
Get-Content $configPath
Write-Host ""
Write-Host "Optional browser MCP note:"
Write-Host "  If this machine also runs Playwright MCP, preserve Host: localhost:8931 for http://127.0.0.1:8931."
