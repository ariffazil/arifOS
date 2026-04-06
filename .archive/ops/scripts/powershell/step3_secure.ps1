Write-Host "--- 3. The Base Recall Test ---"
$body = '{"input": "Test W_scar W_scar", "model": "bge-small-en-v1.5"}'
$curlCmd = "curl -s -X POST http://127.0.0.1:8001/v1/embeddings -H 'Content-Type: application/json' -H 'Authorization: Bearer SK-ARIFOS-FORGE' -d '$body'"
$responseJson = ssh root@72.62.71.199 "$curlCmd"
$responseObj = $responseJson | ConvertFrom-Json
$dims = $responseObj.data[0].embedding[0..4]
Write-Host "First 5 dims:" ($dims -join ", ")
Write-Host "
PHASE 1 SECURED"
