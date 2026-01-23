$currentDir = Get-Location
Start-Process "cmd.exe" -ArgumentList "/k `"$currentDir\scripts\boot_server.bat`"" -WorkingDirectory $currentDir
