
# Start arifOS Web Mode (SSE Server)

$pythonPath = "C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe"
$scriptPath = "C:\Users\User\OneDrive\Documents\GitHub\arifOS\scripts\arifos_sse_server.py"
$env:PYTHONPATH = "C:\Users\User\OneDrive\Documents\GitHub\arifOS"
$env:PYTHONUNBUFFERED = "1"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   arifOS CLOUD MODE (Web Server)         " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting SSE Server on Port 8000..." -ForegroundColor Yellow

# Start Python Server
& $pythonPath $scriptPath
