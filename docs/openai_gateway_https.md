# OpenAI Gateway (HTTPS) - arifOS

An HTTP Gateway that exposes arifOS-governed tools in a format compatible with OpenAI's "Function Calling".

## Architecture
- **Endpoint**: `https://mcp.arif-fazil.com`
- **Protocol**: HTTP JSON (OpenAI Schema)
- **Engine**: Composio (Tool Execution) + arifOS (Governance)

## Usage

### 1. List Tools
`GET /tools`
Returns a list of tools in OpenAI `{"type": "function", ...}` format.

### 2. Call Tool
`POST /call`
Payload:
```json
{
  "tool_name": "google_search",
  "arguments": {"query": "arifOS"}
}
```
Response:
```json
{
  "verdict": "SEAL",
  "tool_result": "...",
  "ledger_hash": "..."
}
```

### 3. Governance
- **READ_ONLY** tools (e.g., Search, Read Repo) execute immediately (`SEAL`).
- **WRITE/DESTRUCTIVE** tools (e.g., Create Issue) return `888_HOLD` unless `approval_token` is provided.

## Local Development
1. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
2. Run server:
   ```bash
   uvicorn arifos.core.integration.openai_gateway.app:app --reload --port 8000
   ```

## Deployment (Fly.io)
1. **Login**: `fly auth login`
2. **Secrets**:
   ```bash
   fly secrets set COMPOSIO_API_KEY=your_key
   ```
3. **Deploy**:
   ```bash
   fly launch --no-deploy
   fly deploy --config deploy/fly/openai-gateway/fly.toml
   ```
4. **DNS**: Point `mcp.arif-fazil.com` to your Fly App IP.

## OpenAI Integration Example
You can use this gateway with any OpenAI client by "binding" the tools manually or via a proxy script.
```python
import requests
import openai

# 1. Fetch Tools
tools = requests.get("https://mcp.arif-fazil.com/tools").json()

# 2. Chat Completion
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Search for arifOS"}],
    tools=tools
)

# 3. Handle Tool Call
call = response.choices[0].message.tool_calls[0]
args = json.loads(call.function.arguments)

# 4. Execute via Gateway
result = requests.post(
    "https://mcp.arif-fazil.com/call",
    json={"tool_name": call.function.name, "arguments": args}
).json()

print(result["tool_result"])
```
