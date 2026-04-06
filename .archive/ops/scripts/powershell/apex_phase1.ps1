Write-Host "--- 1. Network Verification ---"
$netResult = ssh root@72.62.71.199 "docker exec openclaw curl -s -o /dev/null -w '%{http_code}' -X POST http://172.17.0.1:8001/v1/embeddings"
Write-Host "HTTP code (422 is good): $netResult"

Write-Host "--- 2. Config Hot-Swap ---"
$configScript = "
jq '.memory.providers.custom = {\"type\": \"openai\", \"apiKey\": \"SK-ARIFOS-FORGE\", \"baseURL\": \"http://172.17.0.1:8001/v1\"}' /root/openclaw_data/config/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json /root/openclaw_data/config/openclaw.json
sed -i 's/API_TOKEN = \"dummy_key\"/API_TOKEN = \"SK-ARIFOS-FORGE\"/' /opt/arifos-embeddings/embed_server.py
systemctl restart arifos-embeddings
"
ssh root@72.62.71.199 "$configScript"
Write-Host "Re-configured and restarted embeddings service"

Start-Sleep -Seconds 5

Write-Host "--- 3. Base Recall Test ---"
$body = '{"input": "Test W_scar W_scar", "model": "bge-small-en-v1.5"}'
$curlCmd = "curl -s -X POST http://127.0.0.1:8001/v1/embeddings -H 'Content-Type: application/json' -H 'Authorization: Bearer SK-ARIFOS-FORGE' -d '$body'"
$responseJson = ssh root@72.62.71.199 "$curlCmd"
$dims = ($responseJson | ConvertFrom-Json).data[0].embedding[0..4]
Write-Host "First 5 dims: " ($dims -join ", ")
Write-Host "PHASE 1 SECURED"
