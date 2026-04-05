# 1. Network Verification
Write-Host "--- 1. Network Verification ---"
$networkResult = ssh root@72.62.71.199 "docker exec openclaw curl -s -o /dev/null -w '%{http_code}' -X POST http://172.17.0.1:8000/v1/embeddings"
Write-Host "HTTP Status from openclaw container to host: $networkResult"

# 2. Config Hot-Swap
Write-Host "--- 2. Config Hot-Swap ---"
$bashScript = "
jq '.memory.providers.custom = {\"type\": \"openai\", \"apiKey\": \"SK-ARIFOS-FORGE\", \"baseURL\": \"http://172.17.0.1:8000/v1\"}' /root/openclaw_data/config/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json /root/openclaw_data/config/openclaw.json
sed -i 's/API_TOKEN = \"dummy_key\"/API_TOKEN = \"SK-ARIFOS-FORGE\"/' /opt/arifos-embeddings/embed_server.py
systemctl restart arifos-embeddings
"
ssh root@72.62.71.199 "$bashScript"
Write-Host "Config hot-swapped and server restarted."

Start-Sleep -Seconds 5

# 3. The Base Recall Test
Write-Host "--- 3. The Base Recall Test ---"
$body = '{"input": "Test W_scar W_scar", "model": "bge-small-en-v1.5"}'
$curlCmd = "curl -s -X POST http://127.0.0.1:8000/v1/embeddings -H 'Content-Type: application/json' -H 'Authorization: Bearer SK-ARIFOS-FORGE' -d '$body'"
$response = ssh root@72.62.71.199 "$curlCmd"
$responseObj = $response | ConvertFrom-Json
$dims = $responseObj.data[0].embedding[0..4]
Write-Host "First 5 embedding dimensions:"
Write-Host ($dims -join ", ")

Write-Host "
PHASE 1 SECURED"
