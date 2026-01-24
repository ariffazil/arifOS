$ErrorActionPreference = "Stop"

Write-Host "Starting deployment for arifos-openai-gateway-v50..."

# 1. Check for flyctl
$flyPath = "$env:USERPROFILE\.fly\bin\flyctl.exe"
if (-not (Test-Path $flyPath)) {
    Write-Host "flyctl not found at default location. Checking PATH..."
    if (Get-Command flyctl -ErrorAction SilentlyContinue) {
        $flyCmd = "flyctl"
    } elseif (Get-Command fly -ErrorAction SilentlyContinue) {
        $flyCmd = "fly"
    } else {
        Write-Error "Fly CLI not found. Please install it or add to PATH."
    }
} else {
    $flyCmd = $flyPath
}

# 2. Auth Check
Write-Host "Checking authentication..."
& $flyCmd auth whoami
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Opening login..."
    & $flyCmd auth login
}

# 3. Create/Check App
$appName = "arifos-openai-gateway-v50"
$tomlPath = "deploy\fly\openai-gateway\fly.toml"

Write-Host "Checking app status..."
& $flyCmd status -a $appName
if ($LASTEXITCODE -ne 0) {
    Write-Host "App does not exist. Creating..."
    # Get Org
    & $flyCmd orgs list
    $org = Read-Host "Enter the Organization Slug to use"
    & $flyCmd apps create $appName --org $org
}

# 4. Set Secrets
Write-Host "Configuring secrets..."
$composioKey = $env:COMPOSIO_API_KEY
if ([string]::IsNullOrWhiteSpace($composioKey)) {
    $composioKey = Read-Host "Enter COMPOSIO_API_KEY (hidden)" -AsSecureString
    $composioKeyBstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($composioKey)
    $composioKey = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($composioKeyBstr)
}

& $flyCmd secrets set COMPOSIO_API_KEY=$composioKey -a $appName

# 5. Deploy
Write-Host "Deploying..."
& $flyCmd deploy -c $tomlPath

Write-Host "Deployment initiated. Check output for progress."
