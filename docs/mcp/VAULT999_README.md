# VAULT999 MCP Server — Setup Guide

**Status:** Production-ready (v45.2.0)

**Purpose:** FastMCP server exposing `search()` and `fetch()` tools for ChatGPT memory integration via HTTPS/SSE.

---

## ?? Prerequisites

1. **Python 3.10+**
2. **OpenSSL** (for certificate generation)
3. **ChatGPT account** (Pro/Plus/Business/Enterprise/Education)
4. **Developer mode enabled** in ChatGPT

---

## ?? Quick Start (5 Minutes)

### **Step 1: Install Dependencies**

```bash
pip install -r arifos_core/mcp/requirements.txt
```

### **Step 2: Generate SSL Certificates**

```bash
# Create certs directory
mkdir -p arifos_core/mcp/certs

# Navigate to certs directory
cd arifos_core/mcp/certs

# Generate self-signed certificate (valid 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=127.0.0.1" \
  -addext "subjectAltName=IP:127.0.0.1"

# Return to repo root
cd ../../..
```

**Expected output:**
```
Generating a RSA private key
.....++++
......++++
writing new private key to 'key.pem'
-----
```

**Verify:**
```bash
ls -la arifos_core/mcp/certs/
# Should show: cert.pem, key.pem
```

### **Step 3: Create Vault Structure (if not exists)**

```bash
mkdir -p vault_999/VAULT999/L0_Vault
mkdir -p vault_999/VAULT999/L1_Ledger
mkdir -p vault_999/VAULT999/L4_Witness
```

**Optional:** Add some test content:

```bash
# Create sample constitutional document
cat > vault_999/VAULT999/L0_Vault/Constitutional_Law.md << 'EOF'
# Constitutional Law (L0_VAULT)

This is canonical constitutional law (confidence: 1.0).

Constitutional floors (F1-F9):
- F1 Amanah: Integrity and reversibility
- F2 Truth: Factual accuracy
- F3 Tri-Witness: Human-AI-Earth consensus
- F4 ?S: Clarity gain
- F5 Peace²: Non-destructive
- F6 ??: Empathy for weakest listener
- F7 ??: Humility and uncertainty
- F8 GENIUS: Governed intelligence
- F9 Anti-Hantu: No consciousness claims

DITEMPA BUKAN DIBERI — Forged, not given.
EOF
```

### **Step 4: Start VAULT999 Server**

```bash
python arifos_core/mcp/vault999_server.py
```

**Expected output:**
```
======================================================================
  VAULT999 MCP Server v45.2.0
  Constitutional Memory Gateway for ChatGPT
======================================================================
  Vault Root: /path/to/arifOS/vault_999/VAULT999
  Listening on: https://127.0.0.1:8000/sse/
  Certificate: arifos_core/mcp/certs/cert.pem
  Private key: arifos_core/mcp/certs/key.pem

  Tools:
    • search(query) - Search L0_VAULT + L1_LEDGER + L4_WITNESS
    • fetch(id) - Retrieve full document

  ChatGPT Registration:
    1. Settings ? Connectors ? Advanced ? Developer mode ON
    2. Create app: Name='VAULT999', URL='https://127.0.0.1:8000/sse/'
    3. In chat: Use 'Developer mode' and select VAULT999 app

  DITEMPA BUKAN DIBERI — Forged, not given.
======================================================================

[2026-01-02 03:55:12] [VAULT999] INFO: Ready for ChatGPT connection...
```

---

## ?? ChatGPT Integration

### **Step 1: Enable Developer Mode**

1. Open [ChatGPT Settings](https://chatgpt.com/#settings/Connectors)
2. Navigate to **Apps ? Advanced settings**
3. Toggle **Developer mode** to ON

### **Step 2: Create App**

1. In [Apps settings](https://chatgpt.com/#settings/Connectors), click **"Create app"**
2. Fill in:
   - **Name:** `VAULT999`
   - **Description:** `arifOS Constitutional Memory - L0_VAULT + L1_LEDGER + L4_WITNESS`
   - **MCP Server URL:** `https://127.0.0.1:8000/sse/`
   - **Authentication:** No Auth
3. Check: ? "I understand and want to continue"
4. Click **Create**

**Note:** You may see a security warning about self-signed certificates. This is expected for localhost development.

### **Step 3: Use in ChatGPT**

1. Start a new chat
2. Click the **Plus (+)** menu in the composer
3. Select **"Developer mode"**
4. Select **VAULT999** app
5. Ask: "Search my memory for Constitutional"

**Expected response:**
```
I found several constitutional documents in your memory:

1. [CANONICAL] Constitutional Law (L0_VAULT)
   Confidence: 1.0
   Snippet: "This is canonical constitutional law..."

Would you like me to fetch the full document?
```

---

## ?? Testing (Without ChatGPT)

### **Test 1: Check Server Status**

```bash
# In another terminal (while server is running)
curl -k https://127.0.0.1:8000/sse/

# Expected: Server responds (SSE endpoint active)
```

### **Test 2: Call search() Tool (Manual)**

Using `httpx` or `requests`:

```python
import requests
import json

url = "https://127.0.0.1:8000/sse/"
headers = {"Content-Type": "application/json"}
payload = {
    "jsonrpc": "2.0",
    "method": "call_tool",
    "params": {
        "name": "search",
        "arguments": {"query": "Constitutional"}
    },
    "id": 1
}

response = requests.post(url, headers=headers, json=payload, verify=False)
print(json.dumps(response.json(), indent=2))
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "results": [
      {
        "id": "L0Vault_Constitutional_Law",
        "title": "[CANONICAL] Constitutional Law",
        "text": "This is canonical constitutional law...",
        "url": "vault://L0_Vault/Constitutional_Law.md",
        "confidence": 1.0,
        "band": "L0_Vault"
      }
    ]
  },
  "id": 1
}
```

---

## ?? Tool Reference

### **Tool 1: `search(query)`**

**Description:** Search across L0_VAULT, L1_LEDGER, and L4_WITNESS memory bands.

**Parameters:**
- `query` (string, required): Search query (case-insensitive)

**Returns:**
```json
{
  "results": [
    {
      "id": "L0Vault_Constitutional_Law",
      "title": "[CANONICAL] Constitutional Law",
      "text": "First 300 chars of content...",
      "url": "vault://L0_VAULT/Constitutional_Law.md",
      "confidence": 1.0,
      "band": "L0_Vault"
    }
  ]
}
```

**Constitutional Compliance:**
- **F2 (Truth):** Confidence bands per tier (L0/L1=1.0, L4?0.85)
- **F4 (Clarity):** Tagged results ([CANONICAL], [SEALED], [OBSERVATION])
- **F6 (??):** Max 10 results to protect cognitive load

**Example prompts:**
- "Search my memory for Constitutional"
- "Find entries about Amanah floor"
- "Show me sealed verdicts about Truth"

---

### **Tool 2: `fetch(id)`**

**Description:** Retrieve full document content by ID.

**Parameters:**
- `id` (string, required): Document ID from search results (e.g., "L0Vault_Constitutional_Law")

**Returns:**
```json
{
  "id": "L0Vault_Constitutional_Law",
  "title": "[CANONICAL] Constitutional Law",
  "text": "[FULL FILE CONTENT]",
  "url": "vault://L0_VAULT/Constitutional_Law.md",
  "metadata": {
    "confidence": 1.0,
    "band": "L0_VAULT",
    "canonical": true,
    "file_size": 5432,
    "last_modified": "2026-01-02T00:00:00Z"
  }
}
```

**Constitutional Compliance:**
- **F1 (Amanah):** Read-only (no write operations)
- **F2 (Truth):** Returns actual file content with metadata

**Example prompts:**
- "Fetch the full Constitutional Law document"
- "Show me the complete content of L0Vault_Constitutional_Law"

---

## ?? Vault Structure

Your Obsidian vault should have this structure:

```
vault_999/VAULT999/
??? L0_Vault/         ? Constitutional law (confidence: 1.0, canonical)
?   ??? Constitutional_Law.md
?   ??? Decision_Axioms.md
?   ??? Constants.json
??? L1_Ledger/        ? Sealed verdicts (confidence: 1.0, canonical)
?   ??? verdicts_2026_01.jsonl
?   ??? cooling_ledger.jsonl
??? L2_Active/        ? Not searched (session-only)
??? L3_Phoenix/       ? Not searched (pending amendments)
??? L4_Witness/       ? Observations (confidence: ?0.85, non-canonical)
?   ??? evidence_pack_001.md
?   ??? witness_log.json
??? L5_Void/          ? Not searched (rejected outputs)
```

**Searchable bands:**
- `L0_Vault` - Constitutional law ([CANONICAL], confidence: 1.0)
- `L1_Ledger` - Sealed verdicts ([SEALED], confidence: 1.0)
- `L4_Witness` - Observations ([OBSERVATION], confidence: ?0.85)

---

## ??? Security Notes

1. **Self-signed certificates:** Only for localhost development. For production, use CA-signed certificates.

2. **No authentication:** Current setup uses "No Auth" for ChatGPT. For production:
   - Implement OAuth or API key authentication
   - Add rate limiting
   - Use firewall rules to restrict access

3. **Read-only by design:** No write tools exposed (F1 Amanah compliance).

4. **Credential exclusion:** `.gitignore` prevents `*.pem` files from being committed.

---

## ?? Troubleshooting

### **Error: "SSL certificates not found!"**

**Solution:** Generate certificates:
```bash
cd arifos_core/mcp/certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=127.0.0.1" \
  -addext "subjectAltName=IP:127.0.0.1"
```

### **Error: "VAULT_ROOT not found"**

**Solution:** Create vault structure:
```bash
mkdir -p vault_999/VAULT999/L0_Vault
mkdir -p vault_999/VAULT999/L1_Ledger
mkdir -p vault_999/VAULT999/L4_Witness
```

### **ChatGPT shows "Unsafe URL" error**

**Causes:**
- Server not running
- Certificate issue
- Wrong URL

**Solution:**
1. Verify server is running: `python arifos_core/mcp/vault999_server.py`
2. Check URL is exact: `https://127.0.0.1:8000/sse/`
3. Try regenerating certificates

### **Search returns no results**

**Causes:**
- Vault is empty
- Query doesn't match any content

**Solution:**
1. Check vault has content: `ls vault_999/VAULT999/L0_Vault/`
2. Try broader query: "Search for any content"

---

## ?? Updating

### **Refresh Tools in ChatGPT**

If you update the server code:
1. Go to ChatGPT Apps settings
2. Find VAULT999 app
3. Click "Refresh" to pull new tool definitions

### **Regenerate Certificates (after expiry)**

Certificates expire after 365 days:
```bash
cd arifos_core/mcp/certs
rm cert.pem key.pem
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=127.0.0.1" \
  -addext "subjectAltName=IP:127.0.0.1"
```

---

## ?? Reference Documents

- **MCP Protocol:** https://modelcontextprotocol.io/
- **ChatGPT Developer Mode:** https://platform.openai.com/docs/mcp
- **FastMCP SDK:** https://github.com/modelcontextprotocol/python-sdk

---

## ? Validation Checklist

Before using with ChatGPT:

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Dependencies installed (`pip install -r arifos_core/mcp/requirements.txt`)
- [ ] SSL certificates generated (`ls arifos_core/mcp/certs/`)
- [ ] Vault structure exists (`ls vault_999/VAULT999/`)
- [ ] Server starts successfully (`python arifos_core/mcp/vault999_server.py`)
- [ ] Console shows "Ready for ChatGPT connection..."
- [ ] ChatGPT Developer mode enabled
- [ ] VAULT999 app created in ChatGPT
- [ ] Search tool returns results in ChatGPT

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

**Version:** v45.2.0  
**License:** Apache-2.0  
**Author:** arifOS Project
