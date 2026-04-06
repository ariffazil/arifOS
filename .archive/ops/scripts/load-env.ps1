# load-env.ps1 - Master Secrets Loader
$MasterEnv = "C:\Users\User\.secrets\MASTER.env"

if (Test-Path $MasterEnv) {
    Write-Host "Loading secrets from $MasterEnv"
    $lines = Get-Content $MasterEnv
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if ($trimmed -and -not $trimmed.StartsWith("#")) {
            $pos = $trimmed.IndexOf("=")
            if ($pos -gt 0) {
                $name = $trimmed.Substring(0, $pos).Trim()
                $value = $trimmed.Substring($pos + 1).Trim().Trim('"').Trim("'")
                [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
    Write-Host "Variables bound to session."
}

# arifOS Governance
$SecretFile = "C:\arifos\secrets\governance.secret"
if (Test-Path $SecretFile) {
    $env:ARIFOS_GOVERNANCE_SECRET = Get-Content $SecretFile -Raw
    Write-Host "Loaded ARIFOS_GOVERNANCE_SECRET from file."
} else {
    $env:ARIFOS_GOVERNANCE_SECRET = "arifos-internal-forge-secret"
    Write-Host "Using default development secret."
}

Write-Host "arifOS and Codex CLI are now ARMED."
