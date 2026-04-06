Write-Host "--- 1. Network Verification ---"
ssh root@72.62.71.199 "docker ps"
$netResult = ssh root@72.62.71.199 "docker exec openclaw curl -sI http://172.17.0.1:8001/docs"
Write-Host "HTTP code (200 is good): $netResult"
