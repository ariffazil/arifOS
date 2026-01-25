# L4_MCP Quick Start

## 1. Direct Test (No MCP Client)

```powershell
# Test destructive command
$payload = @'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"apex_verdict_tool","arguments":{"task":"rm -rf /"}}}
'@

echo $payload | python -m L4_MCP.server 2>$null | jq -r '.result.content[0].text'
```

**Output:**
```
🚫 ACTION BLOCKED

🔴 Verdict: VOID
Reason(s): RED::F1_DESTRUCTIVE_FILESYSTEM
Required evidence: file_hash
Constraints:
  - no_execution
  - no_external_calls

System Health: 0% approval (apex_pulse: 0.0)
Audit Trail: Logged as ledger_eb966fc5d6d at 2026-01-12T13:09:08
```

---

## 2. Via Kimi CLI (Recommended)

```bash
# Already configured at ~/.kimi/mcp.json
kimi
```

Then type:
```
Check if this is safe: "Delete all files"
```

Kimi will automatically call `apex_verdict_tool` and show the verdict.

---

## 3. Batch File Validation

```powershell
# Check all Python files
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $task = Get-Content $_.FullName -Raw
    $payload = @{
        jsonrpc = "2.0"
        id = 1
        method = "tools/call"
        params = @{
            name = "apex_verdict_tool"
            arguments = @{
                task = $task
            }
        }
    } | ConvertTo-Json -Depth 10

    $result = $payload | python -m L4_MCP.server 2>$null | ConvertFrom-Json
    Write-Host "$($_.Name): $($result.result.content[0].text -split '\n' | Select-Object -First 1)"
}
```

---

## 4. Check Ledger

```powershell
# Last 5 verdicts
Get-Content cooling_ledger_l4.sqlite3 | Select-Object -Last 5

# Or query SQLite directly
sqlite3 cooling_ledger_l4.sqlite3 "SELECT id, verdict, apex_pulse FROM verdicts ORDER BY timestamp DESC LIMIT 5;"
```

---

## 5. Integration Example (Pre-commit Hook)

```bash
#!/bin/bash
# .git/hooks/pre-commit

git diff --cached --name-only | grep '\.py$' | while read file; do
    verdict=$(cat "$file" | python -m L4_MCP.server <<< '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"apex_verdict_tool","arguments":{"task":"'"$(cat $file)"'"}}}' 2>/dev/null | jq -r '.result.content[0].text' | head -1)

    if [[ $verdict == *"BLOCKED"* ]]; then
        echo "❌ Constitutional violation in $file"
        exit 1
    fi
done
```

---

## 6. API Wrapper (FastAPI)

```python
from fastapi import FastAPI, HTTPException
import subprocess
import json

app = FastAPI()

@app.post("/validate")
async def validate(task: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "apex_verdict_tool",
            "arguments": {"task": task}
        }
    }

    result = subprocess.run(
        ["python", "-m", "L4_MCP.server"],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )

    response = json.loads(result.stdout)
    verdict_text = response["result"]["content"][0]["text"]

    if "BLOCKED" in verdict_text:
        raise HTTPException(status_code=403, detail=verdict_text)

    return {"verdict": verdict_text}
```

---

**That's it. The server is running. Use it.**
