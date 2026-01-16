# Quick .env loader - Simple version
# Usage: . .\load-env.ps1  (note the dot space dot!)

$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host "Loading .env..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=#]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"').Trim("'")
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            Set-Item -Path "env:$key" -Value $value -Force
            Write-Host "  OK $key" -ForegroundColor Green
        }
    }
    Write-Host "Done! Variables loaded into current session." -ForegroundColor Green
} else {
    Write-Host ".env file not found" -ForegroundColor Red
}
