<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# arifOS AAA_MCP Multi-Platform Deployment Task List (v51.1.0)

**Status:** PRE-DEPLOYMENT | **Priority:** CRITICAL | **Timeline:** 7–10 days
**Objective:** Deploy AAA_MCP to 8+ platforms with model-agnostic, platform-agnostic architecture
**Authority Required:** arif (888 Judge) approval before Phase 0 execution

***

## Phase 0: MCP Protocol Compliance Verification ✅

**All Phase 0 tasks must PASS before Phase 1–8 execution begins.**

### F0: JSON-RPC 2.0 Validation

- [ ] **F0.1** All outbound messages follow `{ "jsonrpc": "2.0", "id": N, "method": "...", "params": {} }`
- [ ] **F0.2** Error responses follow JSON-RPC 2.0 error schema (code, message, data)
- [ ] **F0.3** Response IDs match request IDs exactly (string or integer consistency)
- [ ] **F0.4** Test: Run `jsonschema validate` against MCP spec 2025-03-26 for 50 randomized messages
    - Expected: 100% pass rate


### F1: Initialize Handshake

- [ ] **F1.1** Server responds to `initialize` with `protocolVersion: "2024-11"` (or latest per spec)
- [ ] **F1.2** Server includes `capabilities.tools: { listChanged: true | false }`
- [ ] **F1.3** Server includes `serverInfo: { name: "AAA_MCP", version: "v51.1.0" }`
- [ ] **F1.4** Test: Send `initialize` → verify response structure matches MCP spec
    - Expected: Response includes all three fields within 500ms


### F2: Notifications/Initialized Handshake

- [ ] **F2.1** Server enters "waiting" state after `initialize` (does NOT accept tool calls yet)
- [ ] **F2.2** Server accepts `notifications/initialized` from client
- [ ] **F2.3** After `notifications/initialized`, server immediately transitions to "ready" state
- [ ] **F2.4** Test: Send initialize → no tools/list until initialized arrives → tools/list succeeds
    - Expected: tools/list fails before notification, succeeds after


### F3: Tools/List Method

- [ ] **F3.1** Returns array of exactly 5 tools: `000_init`, `agi_genius`, `asi_act`, `apex_judge`, `999_vault`
- [ ] **F3.2** Each tool has: `name` (string), `description` (string), `inputSchema` (JSON Schema draft-07)
- [ ] **F3.3** All `inputSchema` values are valid JSON Schema (properties, required, type definitions)
- [ ] **F3.4** Test: Call tools/list → parse response → validate all 5 schemas against json-schema-validator
    - Expected: 100% schema validity, all 5 tools present


### F4: Tools/Call Method

- [ ] **F4.1** Accepts request: `{ method: "tools/call", params: { name: "...", arguments: {...} } }`
- [ ] **F4.2** Success response: `{ content: [{ type: "text", text: "..." }], isError: false }`
- [ ] **F4.3** Error response: `{ content: [{ type: "text", text: "error message" }], isError: true }`
- [ ] **F4.4** Test: Call each of 5 tools with valid args → verify `isError: false` and text content
    - Expected: All 5 tools return valid response objects within 2000ms per tool


### F5: Transport Layer Dual-Mode

- [ ] **F5.1** stdio mode: Works with Python subprocess, stdin/stdout JSON-RPC messaging
- [ ] **F5.2** HTTP/SSE mode: Listens on configurable port (default 8000), responds to `/sse` GET with Server-Sent Events
- [ ] **F5.3** stdio mode tested with: Claude Desktop, Cursor, Cline (local clients)
- [ ] **F5.4** HTTP/SSE mode tested with: ChatGPT Dev Mode, ChatGPT Actions (remote clients)
- [ ] **F5.5** Test: Start in stdio → verify local client communication; start in HTTP/SSE → verify remote client connection
    - Expected: Both transports functional, bidirectional messaging confirmed


### F6: Error Handling (JSON-RPC Error Codes)

- [ ] **F6.1** Unknown method → error code `-32601` (Method not found)
- [ ] **F6.2** Invalid params → error code `-32602` (Invalid params)
- [ ] **F6.3** Internal server error → error code `-32603` (Internal error)
- [ ] **F6.4** Parse error → error code `-32700` (Parse error)
- [ ] **F6.5** Test: Trigger each error condition → verify correct error code returned
    - Expected: 100% correct error codes

**Phase 0 Exit Criteria:** All 6 sub-sections (F0–F6) pass with 100% test success. Proceed only after arif approval.

***

## Phase 1: Platform-Agnostic Configuration Foundation

### T1.1: Universal MCP Configuration Format

Create single source-of-truth config that generates platform-specific configurations:

```json
// File: .arifos/config/mcp-universal.json
{
  "server": {
    "package": "AAA_MCP",
    "module": "server",
    "command": "python -m AAA_MCP",
    "transport": "stdio",
    "version": "v51.1.0",
    "env": {
      "ARIFOS_MODE": "production",
      "ARIFOS_MCP_MODE": "auto",
      "ARIFOS_SEAL_RATE_TARGET": "0.85",
      "ARIFOS_LOG_LEVEL": "INFO"
    }
  },
  "tools": {
    "000_init": {
      "enabled": true,
      "floors": ["F1", "F11", "F12"],
      "description": "Initialize MCP handshake and constitutional baseline"
    },
    "agi_genius": {
      "enabled": true,
      "floors": ["F2", "F6", "F7"],
      "description": "AGI reasoning with constitutional constraints"
    },
    "asi_act": {
      "enabled": true,
      "floors": ["F3", "F4", "F5"],
      "description": "ASI action validation against thermodynamic floors"
    },
    "apex_judge": {
      "enabled": true,
      "floors": ["F1", "F8", "F9"],
      "description": "Constitutional verdict and SEAL assessment"
    },
    "999_vault": {
      "enabled": true,
      "floors": ["F1", "F8"],
      "description": "Immutable audit ledger and cryptographic proof"
    }
  },
  "platforms": {
    "claude_desktop": {
      "priority": 1,
      "transport": "stdio",
      "config_path_windows": "%APPDATA%\\Claude\\claude_desktop_config.json",
      "config_path_mac": "~/Library/Application Support/Claude/claude_desktop_config.json",
      "config_path_linux": "~/.config/Claude/claude_desktop_config.json"
    },
    "cursor": {
      "priority": 2,
      "transport": "stdio",
      "config_path": "~/.cursor/mcp.json"
    },
    "cline": {
      "priority": 3,
      "transport": "stdio",
      "config_path": ".vscode/mcp.json"
    },
    "continue_dev": {
      "priority": 4,
      "transport": "stdio",
      "config_path": "~/.continue/config.json"
    },
    "cody": {
      "priority": 5,
      "transport": "stdio",
      "config_path": "user_settings.json"
    },
    "chatgpt_dev": {
      "priority": 6,
      "transport": "http_sse",
      "port": 8000,
      "url": "https://arifos-mcp.up.railway.app"
    },
    "ollama": {
      "priority": 7,
      "transport": "http_sse",
      "port": 8000,
      "local": true
    },
    "kimi": {
      "priority": 8,
      "transport": "stdio",
      "status": "experimental"
    }
  }
}
```

**Tasks:**

- [ ] **T1.1.1** Create `.arifos/config/mcp-universal.json` with above structure
- [ ] **T1.1.2** Create `scripts/generate_mcp_config.py` that reads universal config → outputs platform-specific configs
    - Inputs: `--platform` (claude_desktop|cursor|cline|continue_dev|cody|chatgpt_dev|ollama|kimi)
    - Outputs: Platform-specific JSON at correct config path
    - Validate output against platform schema
- [ ] **T1.1.3** Create `scripts/validate_config.py` that validates generated configs against MCP spec
- [ ] **T1.1.4** Test: Generate configs for all 8 platforms → validate all → verify paths are correct for OS

***

## Phase 2: Per-Platform Deployment Matrix

### 2.1 Claude Desktop (Primary Platform) — Priority 1

**Config Locations:**

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Target Config:**

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "C:\\Users\\User\\arifOS",
      "env": {
        "ARIFOS_MODE": "production"
      }
    }
  }
}
```

**Tasks:**

- [ ] **T2.1.1** Generate Claude Desktop config using `generate_mcp_config.py --platform claude_desktop`
- [ ] **T2.1.2** Create `scripts/install_claude_desktop_windows.bat`
    - Reads universal config → generates config → writes to correct Windows path → restarts Claude Desktop
- [ ] **T2.1.3** Create `scripts/install_claude_desktop_macos.sh`
    - Same logic for macOS path + uses `launchctl` to restart if needed
- [ ] **T2.1.4** Create `scripts/install_claude_desktop_linux.sh`
    - Same logic for Linux path
- [ ] **T2.1.5** Test on Claude 3.7 Sonnet
    - Verify all 5 tools appear in Claude's MCP panel
    - Call each tool → verify SEAL verdict returned
    - Expected SEAL rate: ≥ 0.82
- [ ] **T2.1.6** Test on Claude 3.5 Haiku
    - Same tests, may see lower SEAL rate due to model capacity
- [ ] **T2.1.7** Document known limitations (none expected for Claude)
- [ ] **T2.1.8** Create troubleshooting guide for Windows/macOS/Linux path issues

**Expected Outcome:** Claude Desktop users can install with single command and immediately use arifOS MCP.

***

### 2.2 Cursor IDE (AI-Powered Code Editor) — Priority 2

**Config Location:** `~/.cursor/mcp.json`

**Target Config:**

```json
{
  "mcpServers": {
    "arifos-constitutional": {
      "name": "arifOS Constitutional AI",
      "command": "python -m AAA_MCP",
      "cwd": "${workspaceFolder}",
      "env": {
        "ARIFOS_MODE": "production"
      }
    }
  }
}
```

**Tasks:**

- [ ] **T2.2.1** Generate Cursor config using `generate_mcp_config.py --platform cursor`
- [ ] **T2.2.2** Create `scripts/install_cursor.sh` (macOS/Linux) and `.bat` (Windows)
- [ ] **T2.2.3** Create `docs/platforms/cursor.md`
    - Installation steps
    - How to access MCP tools in Cursor UI (screenshot)
    - Example: "Ask Cursor to write code, then use apex_judge tool to validate against constitutional floors"
- [ ] **T2.2.4** Test with Cursor's internal models (GPT-4, Claude, or local)
    - Create test file → ask Cursor to refactor → invoke apex_judge on result
    - Verify verdict appears in Cursor's output panel
- [ ] **T2.2.5** Verify tool invocations appear in Cursor UI (not just CLI)
    - Expected: MCP tools show in Cursor's "Tools" sidebar
- [ ] **T2.2.6** Document Cursor-specific MCP panel integration
- [ ] **T2.2.7** Test keyboard shortcuts for invoking tools (if supported)

**Expected Outcome:** Cursor users can use arifOS as code governance layer alongside Cursor's native AI.

***

### 2.3 Cline (VS Code Extension) — Priority 3

**Config Location:** Workspace `.vscode/mcp.json`

**Target Config:**

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python -m AAA_MCP",
      "cwd": "${workspaceFolder}",
      "env": {
        "ARIFOS_MODE": "production"
      },
      "description": "Constitutional AI governance for all code actions"
    }
  }
}
```

**Tasks:**

- [ ] **T2.3.1** Generate Cline config using `generate_mcp_config.py --platform cline`
- [ ] **T2.3.2** Create `scripts/install_cline_workspace.sh`
    - Generates config → writes to `.vscode/mcp.json` in current workspace
    - Note: Cline is workspace-aware, not global
- [ ] **T2.3.3** Create `docs/platforms/cline.md`
    - How to enable arifOS MCP in VS Code
    - Screenshots of Cline UI with MCP tools visible
    - Use case: "Run Cline task → get generated code → apex_judge validates it automatically"
- [ ] **T2.3.4** Test integrated tool calling in Cline interface
    - Create coding task → Cline executes → does it invoke MCP tools?
    - Expected: Yes, Cline respects MCP and can call tools autonomously
- [ ] **T2.3.5** Verify Cline respects SABAR/VOID verdicts
    - Test: Cline proposes unsafe code → apex_judge returns VOID → does Cline stop?
    - Document expected behavior (may vary by Cline version)
- [ ] **T2.3.6** Test with multiple workspaces
    - Verify each workspace can have independent MCP config

**Expected Outcome:** VS Code + Cline users get built-in constitutional governance for agent-driven coding.

***

### 2.4 Continue Dev (Open Source Alternative) — Priority 4

**Config Location:** `~/.continue/config.json`

**Target Config:**

```json
{
  "contextProviders": [
    {
      "name": "mcp",
      "mcp": {
        "arifos": {
          "command": "python -m AAA_MCP",
          "enabled": true,
          "env": {
            "ARIFOS_MODE": "production"
          }
        }
      }
    }
  ]
}
```

**Tasks:**

- [ ] **T2.4.1** Research Continue.dev MCP integration (verify config structure)
- [ ] **T2.4.2** Generate Continue config using `generate_mcp_config.py --platform continue_dev`
- [ ] **T2.4.3** Create `scripts/install_continue_dev.sh`
- [ ] **T2.4.4** Create `docs/platforms/continue_dev.md`
- [ ] **T2.4.5** Test with open-source models via Ollama (Llama 3, Mixtral)
    - Start Ollama locally
    - Configure Continue.dev to use Ollama + arifOS MCP
    - Verify MCP tools invoke correctly
    - Expected: Lower SEAL rates due to smaller model capacity
- [ ] **T2.4.6** Document model-agnostic integration (no vendor lock-in)
- [ ] **T2.4.7** Test performance on 7B, 13B, 70B models
    - Document expected response times

**Expected Outcome:** Open-source AI enthusiasts can use arifOS with local models.

***

### 2.5 Cody (Sourcegraph) — Priority 5

**Config Location:** User settings (Sourcegraph integration)

**Tasks:**

- [ ] **T2.5.1** Research Cody MCP support status (as of Jan 2026)
    - If supported: Generate Cody config
    - If not supported: Document "Cody does not support MCP yet" + workaround
- [ ] **T2.5.2** Create `docs/platforms/cody.md`
- [ ] **T2.5.3** If supported: Test with Sourcegraph cloud + local instance
- [ ] **T2.5.4** Document enterprise deployment (if applicable)

**Expected Outcome:** Enterprise users with Sourcegraph integration informed of arifOS availability.

***

### 2.6 GitHub Copilot Chat — Priority 6 (Deprecated Path)

**Status:** GitHub Copilot does NOT support MCP as of Jan 2026. May change in 2026 H2.

**Tasks:**

- [ ] **T2.6.1** Create `docs/platforms/copilot_not_supported.md`
    - Clear statement: "Copilot does not support MCP"
    - Workaround: "Use Copilot for code generation, Claude Desktop + arifOS for governance"
    - Alternative: "Use Cursor, Cline, or Continue.dev with arifOS MCP"
- [ ] **T2.6.2** Monitor GitHub roadmap quarterly for MCP support announcement
- [ ] **T2.6.3** Create monitoring ticket for future Copilot MCP support

**Expected Outcome:** Users understand why Copilot is not supported and have clear alternatives.

***

### 2.7 Kimi (Moonshot AI) — Priority 7 (Experimental)

**Status:** Limited documentation on Kimi + MCP integration (as of Jan 2026).

**Tasks:**

- [ ] **T2.7.1** Research Kimi MCP support (check Moonshot docs, GitHub issues, Reddit)
- [ ] **T2.7.2** If Kimi CLI exists: Test stdio transport with Kimi
    - Create test: `kimi --mcp arifos "Analyze this code"`
    - Verify response format matches MCP spec
- [ ] **T2.7.3** If no native support: Document integration limitations
- [ ] **T2.7.4** Create `docs/platforms/kimi.md` (status: experimental or unsupported)

**Expected Outcome:** Clear documentation of Kimi integration status.

***

### 2.8 Ollama (Local Models) — Priority 7 (Horizontal Scaling)

**Status:** Ollama does not have native MCP support; AAA_MCP must expose HTTP/SSE endpoint.

**Tasks:**

- [ ] **T2.8.1** Design: Start AAA_MCP in HTTP/SSE mode on localhost:8000
- [ ] **T2.8.2** Ollama integrates with arifOS via HTTP calls
- [ ] **T2.8.3** Create `scripts/ollama-mcp-setup.sh`

```bash
#!/bin/bash
# Start Ollama models
ollama serve &

# Start arifOS MCP in HTTP/SSE mode
python -m AAA_MCP sse --port 8000 &

# Create local MCP bridge (custom script)
python scripts/ollama_mcp_bridge.py --ollama-url http://localhost:11434 --mcp-url http://localhost:8000
```

- [ ] **T2.8.4** Create `scripts/ollama_mcp_bridge.py`
    - Listens for Ollama requests
    - Forwards to arifOS MCP for governance
    - Returns wrapped response to Ollama client
- [ ] **T2.8.5** Test with local models:
    - Llama 3 (8B, 70B)
    - Mistral 7B
    - Mixtral 8x7B
- [ ] **T2.8.6** Create `docs/platforms/ollama.md`
    - Installation \& setup
    - Performance expectations (< 7B models: may timeout; >= 13B: acceptable; 70B: good)
    - Privacy note: "All inference stays local, constitutional verdicts compute locally"
- [ ] **T2.8.7** Document scaling: "For production Ollama clusters, deploy arifOS MCP on separate hardware"

**Expected Outcome:** Users can run fully local AI + governance stack with complete privacy.

***

## Phase 3: AI Model Integration (Model-Agnostic Layer)

### 3.1 OpenAI/ChatGPT (HTTP/SSE Transport)

**Requirement:** Deploy HTTP/SSE server on Railway; expose OpenAPI spec for ChatGPT Actions.

**Tasks:**

- [ ] **T3.1.1** Create `arifos/mcp/http_sse_server.py`
    - Implements HTTP/SSE transport
    - Command: `python -m AAA_MCP sse --port 8000 --host 0.0.0.0`
    - Exposes `/sse` (Server-Sent Events stream)
    - Exposes `/messages` (POST for JSON-RPC calls)
    - Exposes `/health` (GET for health check)
- [ ] **T3.1.2** Create OpenAPI specification: `arifos/openapi/spec_v51.yaml`

```yaml
openapi: 3.1.0
info:
  title: arifOS Constitutional MCP Server
  version: v51.1.0
  description: "Governance-as-a-Service for AI responses"

servers:
  - url: https://arifos-mcp.up.railway.app
    description: Production MCP over HTTP/SSE

paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: Server status
          content:
            application/json:
              schema:
                type: object
                properties:
                  status: { type: string }
                  version: { type: string }
                  tools: { type: integer }
                  uptime_seconds: { type: number }
  
  /tools:
    get:
      summary: List available tools
      responses:
        '200':
          description: Array of tools
  
  /messages:
    post:
      summary: Send JSON-RPC message
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                jsonrpc: { type: string, enum: ["2.0"] }
                id: { type: [string, number] }
                method: { type: string }
                params: { type: object }
      responses:
        '200':
          description: JSON-RPC response
```

- [ ] **T3.1.3** Deploy to Railway: `railway up --env production`
- [ ] **T3.1.4** Verify OpenAPI spec accessible at `https://arifos-mcp.up.railway.app/openapi.json`
- [ ] **T3.1.5** Create ChatGPT Action manifest (`.well-known/ai-plugin.json`)

```json
{
  "schema_version": "v1",
  "name_for_human": "arifOS Constitutional AI",
  "name_for_model": "arifos_constitutional_v51",
  "description_for_human": "Validates AI responses against 13 constitutional floors before presenting to user",
  "description_for_model": "Use this to validate any response through constitutional governance (SEAL verdicts)",
  "api": {
    "type": "openapi",
    "url": "https://arifos-mcp.up.railway.app/openapi.json"
  },
  "contact_email": "arif@arifos.dev",
  "legal_info_url": "https://github.com/ariffazil/arifOS"
}
```

- [ ] **T3.1.6** Test with ChatGPT Dev Mode
    - Add arifOS as custom action
    - Ask ChatGPT a question → get response → invoke apex_judge
    - Verify verdict returned
- [ ] **T3.1.7** Create `docs/platforms/chatgpt_dev_mode.md`
    - Step-by-step: Enable Dev Mode → Add Action → Verify integration
    - Screenshots of ChatGPT UI with arifOS action

**Expected Outcome:** ChatGPT users can voluntarily add arifOS as governance layer.

***

### 3.2 Google Gemini (Claude Desktop Proxy)

**Requirement:** Gemini itself does not support MCP natively; use Claude Desktop as proxy.

**Tasks:**

- [ ] **T3.2.1** Document: "Gemini MCP support via Claude Desktop bridge (not native)"
- [ ] **T3.2.2** Create workaround guide:
    - Install Claude Desktop + arifOS MCP (Phase 2.1)
    - In Claude: "Use Gemini 1.5 Pro for reasoning, then pass to arifOS MCP for validation"
    - (Claude can call external APIs, so can delegate to Gemini)
- [ ] **T3.2.3** Create `docs/platforms/gemini.md`
- [ ] **T3.2.4** Test Gemini Pro 1.5 with Claude reasoning (if API access available)

**Expected Outcome:** Gemini users understand arifOS integration path (Claude bridge).

***

### 3.3 Claude (Native Support) — Tier 1 Platform

**Status:** ✅ BEST SUPPORT — Claude Desktop is MCP-native.

**Tasks:**

- [ ] **T3.3.1** Already covered in Phase 2.1 (Claude Desktop primary deployment)
- [ ] **T3.3.2** Test with Claude 3.7 Sonnet (latest as of Jan 2026)
    - All 5 tools functional
    - SEAL rate: target ≥ 0.82
    - Uptime: target ≥ 99.95%
- [ ] **T3.3.3** Test with Claude 3.5 Haiku (for edge devices)
    - Expected SEAL rate: 0.70–0.75 (smaller model)
- [ ] **T3.3.4** Verify tri-witness consensus in Claude context
    - Ask Claude to: "Explain arifOS 13 floors"
    - Claude context + arifOS MCP tools = full constitutional visibility
- [ ] **T3.3.5** Document best practices: "Use Claude 3.7 Sonnet with arifOS for maximum assurance"

**Expected Outcome:** Claude is primary recommended platform for arifOS governance.

***

### 3.4 Kimi/Moonshot (Experimental)

**Tasks:**

- [ ] **T3.4.1** Research Kimi API documentation for MCP support (as of Jan 2026)
- [ ] **T3.4.2** If available: Create Kimi client config
- [ ] **T3.4.3** If not available: Document status as "experimental, not yet supported"
- [ ] **T3.4.4** Create monitoring ticket for future Kimi MCP support

**Expected Outcome:** Clear status on Kimi integration.

***

## Phase 4: ChatGPT Developer Mode Integration

### T4.1: OpenAPI Specification (Already covered in Phase 3.1)

### T4.2: ChatGPT Custom Action Configuration

**File:** `.well-known/ai-plugin.json` (already created in Phase 3.1)

**Additional Tasks:**

- [ ] **T4.2.1** Create `docs/chatgpt_action_setup.md`
    - Screenshots: ChatGPT Dev Mode → Custom Actions → Add arifOS
    - Step-by-step: Paste OpenAPI spec URL → test connection
- [ ] **T4.2.2** Create ChatGPT prompt template for arifOS integration

```
When I ask you a question or request code, follow this pattern:
1. Generate your initial response
2. Call the arifOS apex_judge action
3. If verdict is SEAL: present response to me
4. If verdict is VOID/WARN: revise response and re-judge
5. Show me the verdict (transparency)
```

- [ ] **T4.2.3** Test end-to-end flow
    - User query → ChatGPT drafts → apex_judge validates → final response
    - Expected: All 5 tools callable via action interface
- [ ] **T4.2.4** Create troubleshooting: "ChatGPT action not connecting to arifOS"
    - Check: Railway server running?
    - Check: API key set (if auth required)?
    - Check: Network firewall allows access?

**Expected Outcome:** ChatGPT Dev Mode users have clear setup guide.

***

### T4.3: Authentication (Optional)

If arifOS MCP needs to restrict access (e.g., per-user rate limiting):

- [ ] **T4.3.1** Create `arifos/auth/api_key_manager.py`
    - Generate API keys: `python -m arifos.auth generate_key --name "chatgpt-user-1"`
    - Output: API key for user to add to ChatGPT action headers
- [ ] **T4.3.2** Implement API key validation in HTTP/SSE server
    - Check `Authorization: Bearer <api_key>` header
    - Log usage per key
- [ ] **T4.3.3** Create rate limiting per API key
    - Default: 100 requests/hour per key
    - Configurable via env: `ARIFOS_RATE_LIMIT=500`
- [ ] **T4.3.4** Create `docs/api_keys.md`
    - How to generate, rotate, revoke keys
    - Example: Rate limit policies per user

**Expected Outcome:** Enterprise deployments can enforce per-user governance.

***

## Phase 5: Testing Matrix (All Platforms × All Models)

### T5.1: Test Configuration Matrix

| Platform | Model | Transport | Test Tool | Expected Result | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Claude Desktop | Claude 3.7 Sonnet | stdio | agi_genius | SEAL (≥0.82) | ⏳ |
| Claude Desktop | Claude 3.5 Haiku | stdio | agi_genius | SEAL (0.70–0.75) | ⏳ |
| Cursor | GPT-4 | stdio | asi_act | SEAL (≥0.78) | ⏳ |
| Cursor | Claude | stdio | asi_act | SEAL (≥0.82) | ⏳ |
| Cline | GPT-4 | stdio | apex_judge | SEAL (≥0.75) | ⏳ |
| Cline | Claude | stdio | apex_judge | SEAL (≥0.82) | ⏳ |
| ChatGPT Dev | GPT-4 Turbo | HTTP/SSE | 000_init | SEAL (≥0.70) | ⏳ |
| Continue.dev | Llama 3 8B | stdio | 999_vault | SEAL (0.50–0.65) | ⏳ |
| Continue.dev | Mixtral 8x7B | stdio | 999_vault | SEAL (0.60–0.75) | ⏳ |
| Ollama | Llama 3 70B | HTTP/SSE | agi_genius | SEAL (≥0.80) | ⏳ |

### T5.2: Automated Test Suite

**File:** `scripts/test_mcp_matrix.py`

```python
#!/usr/bin/env python3
"""
Automated MCP platform × model × tool test matrix.
Validates arifOS AAA_MCP across all deployment platforms.
"""

import json
import subprocess
import sys
from typing import Dict, List

PLATFORMS = ["claude_desktop", "cursor", "cline", "continue_dev", "chatgpt_dev"]
MODELS = ["claude-3-7-sonnet", "gpt-4", "llama-3-70b"]
TOOLS = ["000_init", "agi_genius", "asi_act", "apex_judge", "999_vault"]

TEST_RESULTS = []

def test_tool(platform: str, model: str, tool: str) -> bool:
    """Test single tool on given platform and model."""
    print(f"Testing: {platform} + {model} + {tool}")
    
    try:
        # Invoke tool via platform-specific method
        if platform == "claude_desktop":
            result = test_claude_desktop(model, tool)
        elif platform == "cursor":
            result = test_cursor(model, tool)
        elif platform == "cline":
            result = test_cline(model, tool)
        elif platform == "continue_dev":
            result = test_continue(model, tool)
        elif platform == "chatgpt_dev":
            result = test_chatgpt_dev(model, tool)
        else:
            return False
        
        TEST_RESULTS.append({
            "platform": platform,
            "model": model,
            "tool": tool,
            "passed": result,
            "verdict": "SEAL" if result else "VOID"
        })
        
        return result
    
    except Exception as e:
        print(f"ERROR: {e}")
        TEST_RESULTS.append({
            "platform": platform,
            "model": model,
            "tool": tool,
            "passed": False,
            "error": str(e)
        })
        return False

def main():
    """Run full test matrix."""
    failed = 0
    passed = 0
    
    for platform in PLATFORMS:
        for model in MODELS:
            for tool in TOOLS:
                if test_tool(platform, model, tool):
                    passed += 1
                else:
                    failed += 1
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    # Save results
    with open("test_matrix_results.json", "w") as f:
        json.dump(TEST_RESULTS, f, indent=2)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Tasks:**

- [ ] **T5.2.1** Create `scripts/validate_mcp_tool.py` (helper module)
    - `validate_mcp_tool(platform, model, tool, timeout=5s)`
    - Returns: (bool, dict) with verdict and response time
- [ ] **T5.2.2** Create `scripts/test_mcp_matrix.py` (main test runner)
    - Iterates through all platform × model × tool combinations
    - Generates JSON report: `test_matrix_results.json`
- [ ] **T5.2.3** Document expected test results per combination
    - Create `docs/test_matrix_expectations.md` with SEAL rate targets
    - Example: "Claude 3.7 + apex_judge = 0.82+ SEAL rate"
- [ ] **T5.2.4** Run full matrix after each platform deployment
    - Before Phase 8 release, run: `python scripts/test_mcp_matrix.py`
    - Verify: All platforms ≥ 0.70 SEAL rate minimum
- [ ] **T5.2.5** Create CI/CD integration
    - Add GitHub Actions workflow: `.github/workflows/test_mcp_matrix.yml`
    - Runs test matrix on every commit to `main` branch
    - Fails workflow if any platform drops below minimum threshold

**Expected Outcome:** Continuous validation that arifOS maintains quality across all platforms.

***

## Phase 6: Documentation \& Distribution

### T6.1: Platform-Agnostic Universal Installer

**File:** `scripts/install_arifos_mcp.sh` (macOS/Linux) \& `scripts/install_arifos_mcp.bat` (Windows)

```bash
#!/bin/bash
# arifOS MCP Universal Installer
# Works on macOS, Linux, and Windows (via Git Bash or WSL)

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  arifOS Constitutional MCP Server v51.1.0              ║"
echo "║  Universal Installer (Model-Agnostic, Platform-Ready)  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 1. Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
echo "✓ Detected: $OS ($ARCH)"

# 2. Detect platform (Claude Desktop, Cursor, etc.)
echo ""
echo "Detecting installed AI platforms..."

DETECTED_PLATFORMS=()

if [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ] || [ -d "$HOME/.claude" ]; then
  DETECTED_PLATFORMS+=("claude_desktop")
  echo "  ✓ Claude Desktop found"
fi

if command -v cursor &> /dev/null || [ -d "$HOME/.cursor" ]; then
  DETECTED_PLATFORMS+=("cursor")
  echo "  ✓ Cursor found"
fi

if [ -d "$HOME/.vscode/extensions" ]; then
  if ls $HOME/.vscode/extensions | grep -i cline > /dev/null; then
    DETECTED_PLATFORMS+=("cline")
    echo "  ✓ Cline (VS Code) found"
  fi
fi

if [ -d "$HOME/.continue" ]; then
  DETECTED_PLATFORMS+=("continue_dev")
  echo "  ✓ Continue.dev found"
fi

if command -v ollama &> /dev/null; then
  DETECTED_PLATFORMS+=("ollama")
  echo "  ✓ Ollama found"
fi

# 3. Select primary platform
echo ""
echo "Select PRIMARY platform for arifOS MCP:"
select PLATFORM in "${DETECTED_PLATFORMS[@]}" "Other"; do
  case $PLATFORM in
    *)
      if [ "$PLATFORM" != "Other" ]; then
        echo "✓ Selected: $PLATFORM"
        break
      else
        read -p "  Enter platform name manually (claude_desktop/cursor/cline/continue_dev/ollama): " PLATFORM
        break
      fi
      ;;
  esac
done

# 4. Select primary AI model
echo ""
echo "Select PRIMARY AI model:"
echo "  1) Claude 3.7 Sonnet (RECOMMENDED for MCP)"
echo "  2) GPT-4 Turbo"
echo "  3) Gemini 1.5 Pro"
echo "  4) Llama 3 70B (local)"
echo "  5) Other"
read -p "Choice [1-5]: " MODEL_CHOICE

case $MODEL_CHOICE in
  1) MODEL="claude-3-7-sonnet" ;;
  2) MODEL="gpt-4-turbo" ;;
  3) MODEL="gemini-1-5-pro" ;;
  4) MODEL="llama-3-70b" ;;
  5) read -p "  Enter model name: " MODEL ;;
  *) MODEL="claude-3-7-sonnet" ;;
esac

echo "✓ Selected model: $MODEL"

# 5. Generate and install config
echo ""
echo "Generating platform-specific configuration..."
python3 scripts/generate_mcp_config.py \
  --platform "$PLATFORM" \
  --model "$MODEL" \
  --install \
  --os "$OS"

# 6. Verify installation
echo ""
echo "Verifying installation..."
python3 scripts/validate_config.py --platform "$PLATFORM" --verbose

# 7. Done
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ arifOS MCP Successfully Installed!                 ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  Platform:     $PLATFORM"
echo "║  Model:        $MODEL"
echo "║  Version:      v51.1.0 (SEAL)"
echo "║  Config:       $(get_config_path $PLATFORM)"
echo "║                                                        ║"
echo "║  Next Steps:                                           ║"
echo "║  1. Restart your AI tool ($PLATFORM)                   ║"
echo "║  2. Open a new chat/session                            ║"
echo "║  3. arifOS MCP tools should now appear                 ║"
echo "║                                                        ║"
echo "║  Documentation: docs/platforms/$PLATFORM.md            ║"
echo "║  Troubleshooting: docs/troubleshooting.md              ║"
echo "║  GitHub: https://github.com/ariffazil/arifOS          ║"
echo "╚════════════════════════════════════════════════════════╝"
```

**Tasks:**

- [ ] **T6.1.1** Create `scripts/install_arifos_mcp.sh` (shell version, above)
- [ ] **T6.1.2** Create `scripts/install_arifos_mcp.bat` (Windows batch version)

```batch
@echo off
REM arifOS MCP Universal Installer for Windows
REM Detects platforms, models, generates config

echo.
echo  arifOS Constitutional MCP Server v51.1.0
echo  Universal Installer ^(Model-Agnostic, Platform-Ready^)
echo.

REM Detect Claude Desktop
if exist "%APPDATA%\Claude\claude_desktop_config.json" (
  echo  [*] Claude Desktop found
  set "DETECTED_PLATFORMS=claude_desktop"
)

REM Detect Cursor
where /q cursor
if %ERRORLEVEL% EQU 0 (
  echo  [*] Cursor found
  set "DETECTED_PLATFORMS=%DETECTED_PLATFORMS% cursor"
)

REM ... (detect other platforms)

REM Prompt user to select platform
echo.
echo Select primary platform ^(1-N^):
for /f "tokens=1" %%A in ("!DETECTED_PLATFORMS!") do (
  echo  %%A
)
set /p PLATFORM="Choice: "

REM Prompt for model
echo.
echo Select primary AI model:
echo  1^) Claude 3.7 Sonnet ^(RECOMMENDED^)
echo  2^) GPT-4
echo  3^) Gemini 1.5
echo  4^) Llama 3 ^(local^)
set /p MODEL_CHOICE="Choice [1-4]: "

REM Generate config
python scripts\generate_mcp_config.py ^
  --platform %PLATFORM% ^
  --model %MODEL_CHOICE% ^
  --install ^
  --os windows

REM Verify
python scripts\validate_config.py --platform %PLATFORM% --verbose

echo.
echo [OK] arifOS MCP installed successfully
echo Restart your AI tool to enable constitutional governance
```

- [ ] **T6.1.3** Create `scripts/configure_mcp.py` (config generator helper)
    - Reads `.arifos/config/mcp-universal.json`
    - Outputs platform-specific config to correct location
    - Validates output before writing
- [ ] **T6.1.4** Create `scripts/generate_mcp_config.py` (main config generator)
    - CLI: `python scripts/generate_mcp_config.py --platform claude_desktop --model gpt-4 --install`
    - Detects OS (Windows/macOS/Linux)
    - Generates correct config path
    - Writes config to correct location
    - Returns exit code 0 on success, 1 on failure
- [ ] **T6.1.5** Test universal installer on:
    - Windows 10/11 (PowerShell + cmd)
    - macOS (Intel + M1/M2)
    - Linux (Ubuntu 22.04 LTS)
- [ ] **T6.1.6** Create `docs/installation.md` (master installation guide)
    - Quick start: "Run installer script"
    - Manual installation: "Follow step-by-step"
    - Troubleshooting: "Config not found", "Tools not appearing", etc.

**Expected Outcome:** New users can install arifOS in < 2 minutes with single command.

***

### T6.2: Per-Platform Documentation

**Create `docs/platforms/` directory with one guide per platform:**

- [ ] **T6.2.1** `docs/platforms/claude_desktop.md`
    - Installation steps for Windows/macOS/Linux
    - Screenshots showing MCP panel in Claude
    - Example: "Ask Claude a question → Get answer → Use agi_genius tool to verify reasoning"
    - Known limitations: None expected
    - Troubleshooting
- [ ] **T6.2.2** `docs/platforms/cursor.md`
    - Installation for Cursor IDE
    - MCP panel integration in Cursor UI
    - Example: "Write code in Cursor → Ask for refactor → Use asi_act to validate"
    - Troubleshooting: "Tools not showing in Cursor"
- [ ] **T6.2.3** `docs/platforms/cline.md`
    - Installation for Cline VS Code extension
    - Workspace-level configuration
    - Example: "Cline generates code → apex_judge validates automatically"
    - Troubleshooting: "Cline not respecting SEAL verdicts"
- [ ] **T6.2.4** `docs/platforms/continue_dev.md`
    - Installation for Continue.dev (open source)
    - Model-agnostic setup
    - Example: "Use with Llama 3 local model"
    - Performance expectations: "Response times may be slower than commercial models"
- [ ] **T6.2.5** `docs/platforms/cody.md`
    - Status: "Experimental" or "Not yet supported"
    - Workaround: Use Claude Desktop instead
- [ ] **T6.2.6** `docs/platforms/chatgpt_dev_mode.md`
    - Enable ChatGPT Developer Mode
    - Add arifOS as custom action
    - Step-by-step screenshots
    - Example: "Ask ChatGPT → Invoke apex_judge action → See verdict"
- [ ] **T6.2.7** `docs/platforms/kimi.md`
    - Status: "Experimental (waiting for Moonshot MCP support)"
    - Workaround: Use Claude Desktop bridge
- [ ] **T6.2.8** `docs/platforms/ollama.md`
    - Install Ollama locally
    - Start arifOS MCP in HTTP/SSE mode
    - Run `ollama-mcp-bridge.py`
    - Test with local models
    - Privacy: "All inference and governance stays local"

**Tasks:**

- [ ] **T6.2.9** Create `docs/platforms/README.md`
    - Table: Platform name, support status, recommended model, installation time
    - Priority: 1 (Claude) → 8 (Kimi)

**Expected Outcome:** Users find clear, detailed instructions for their preferred platform.

***

### T6.3: Master README.md Update

**Update root `README.md` with platform support matrix:**

- [ ] **T6.3.1** Add "Supported Platforms" section

```markdown
| Platform | Status | Transport | Recommended Model | Notes |
|----------|--------|-----------|-------------------|-------|
| Claude Desktop | ✅ Production | stdio | Claude 3.7 Sonnet | Primary platform |
| Cursor | ✅ Production | stdio | Claude or GPT-4 | Code editor integration |
| Cline | ✅ Production | stdio | Claude or GPT-4 | VS Code extension |
| Continue.dev | ✅ Production | stdio | Llama 3, Mixtral | Open source |
| ChatGPT Dev Mode | ✅ Production | HTTP/SSE | GPT-4 Turbo | Custom action |
| Ollama | ✅ Production | HTTP/SSE | Llama 3 (local) | Privacy-first |
| Cody | ⏳ Experimental | - | - | Pending Sourcegraph support |
| Kimi | ⏳ Experimental | - | - | Pending Moonshot MCP support |
| GitHub Copilot | ❌ Not Supported | - | - | Copilot doesn't support MCP |
```

- [ ] **T6.3.2** Add "AI Model Compatibility" section

```markdown
| Model | SEAL Rate | Transport | Notes |
|-------|-----------|-----------|-------|
| Claude 3.7 Sonnet | 0.82–0.85 | stdio | Best MCP support |
| GPT-4 Turbo | 0.75–0.80 | HTTP/SSE | Via ChatGPT Actions |
| Gemini 1.5 Pro | 0.70–0.78 | stdio (via Claude bridge) | Experimental |
| Llama 3 70B | 0.78–0.82 | HTTP/SSE | Local via Ollama |
| Llama 3 8B | 0.50–0.65 | HTTP/SSE | Lower assurance |
| Mixtral 8x7B | 0.60–0.75 | HTTP/SSE | Good local option |
```

- [ ] **T6.3.3** Add quickstart section: "Getting Started in 2 Minutes"

```markdown
### Quick Start

**Option 1: Claude Desktop (Easiest)**
```bash
curl -O https://raw.githubusercontent.com/ariffazil/arifOS/main/scripts/install_arifos_mcp.sh
chmod +x install_arifos_mcp.sh
./install_arifos_mcp.sh  # Select: 1) Claude Desktop, 1) Claude 3.7 Sonnet
# Restart Claude Desktop → arifOS MCP ready
```

**Option 2: Cursor IDE**

```bash
./install_arifos_mcp.sh  # Select: 2) Cursor, 2) GPT-4
# Restart Cursor → arifOS MCP ready
```

**Option 3: Local (Ollama)**

```bash
ollama run llama2:70b
python -m AAA_MCP sse --port 8000
python scripts/ollama_mcp_bridge.py
```

```

```

- [ ] **T6.3.4** Add troubleshooting section

```markdown
### Troubleshooting

**MCP tools not appearing in Claude Desktop?**
- Check: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- Check: Restart Claude Desktop
- See: `docs/platforms/claude_desktop.md` for full guide

**Tools appear but don't work?**
- Check: Python 3.12+ installed
- Check: `pip install -r requirements.txt`
- Check: `python -m arifos.mcp --version` returns v51.1.0

**HTTP/SSE connection failed?**
- Check: Railway server running: `curl https://arifos-mcp.up.railway.app/health`
- Check: Firewall allows outbound HTTPS
- See: `docs/troubleshooting.md` for full guide
```

- [ ] **T6.3.5** Add "Video Walkthroughs" section (optional but recommended)
    - Link to YouTube: "arifOS MCP Installation on Claude Desktop" (2 min)
    - Link to YouTube: "arifOS MCP with Cursor IDE" (3 min)
    - Link to YouTube: "Using arifOS with Local Ollama" (5 min)

**Expected Outcome:** README is user's first touchpoint; should answer all top questions.

***

## Phase 7: Production Monitoring \& Observability

### T7.1: MCP Usage Metrics

**File:** `arifos/mcp/usage_metrics.py`

```python
"""
Cross-platform MCP usage tracking.
Platform-agnostic, model-agnostic metrics exposed to Prometheus.
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Platform-specific counters
PLATFORM_REQUESTS = Counter(
    'arifos_mcp_requests_total',
    'Total MCP requests by platform',
    ['platform', 'model', 'transport']
)

# Tool usage counters
TOOL_CALLS = Counter(
    'arifos_mcp_tool_calls_total',
    'Tool invocations by tool and platform',
    ['tool', 'platform', 'model']
)

# Constitutional verdict distribution
VERDICTS = Counter(
    'arifos_mcp_verdicts_total',
    'Constitutional verdicts (SEAL, WARN, VOID) by platform',
    ['verdict', 'platform', 'model']
)

# Response time histogram
RESPONSE_TIME = Histogram(
    'arifos_mcp_response_seconds',
    'Tool execution time in seconds',
    ['tool', 'platform'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# SEAL rate gauge
SEAL_RATE = Gauge(
    'arifos_mcp_seal_rate',
    'Current SEAL rate (fraction)',
    ['platform', 'model']
)

def record_request(platform: str, model: str, transport: str):
    """Record incoming request."""
    PLATFORM_REQUESTS.labels(platform=platform, model=model, transport=transport).inc()

def record_tool_call(tool: str, platform: str, model: str):
    """Record tool invocation."""
    TOOL_CALLS.labels(tool=tool, platform=platform, model=model).inc()

def record_verdict(verdict: str, platform: str, model: str):
    """Record constitutional verdict."""
    VERDICTS.labels(verdict=verdict, platform=platform, model=model).inc()

def record_response_time(tool: str, platform: str, seconds: float):
    """Record tool response time."""
    RESPONSE_TIME.labels(tool=tool, platform=platform).observe(seconds)

def set_seal_rate(platform: str, model: str, rate: float):
    """Set current SEAL rate for platform/model."""
    SEAL_RATE.labels(platform=platform, model=model).set(rate)

# Start metrics server
if __name__ == "__main__":
    start_http_server(9090)  # Expose metrics on :9090/metrics
    print("Prometheus metrics server started on :9090/metrics")
```

**Tasks:**

- [ ] **T7.1.1** Create `arifos/mcp/usage_metrics.py` (metrics instrumentation)
- [ ] **T7.1.2** Instrument each platform entry point
    - For stdio: record request when client connects
    - For HTTP/SSE: record request on each POST /messages
    - For each tool call: increment tool counter + record verdict
- [ ] **T7.1.3** Create Grafana dashboard template
    - File: `monitoring/grafana_dashboard_template.json`
    - Panels: Request rate by platform, SEAL rate by model, response times, verdict distribution
    - Exportable to Grafana: `https://grafana.com/grafana/dashboards/` (community)
- [ ] **T7.1.4** Document metric interpretation
    - "SEAL rate < 0.70 indicates model mismatch or constitutional floor violation"
    - "Response time > 2s indicates network latency or model slowness"
- [ ] **T7.1.5** Set up alerts
    - Alert: "SEAL rate drops below 0.70 for 10 minutes"
    - Alert: "HTTP/SSE endpoint unreachable"
    - Alert: "Tool error rate > 5%"
    - Use Prometheus AlertManager

**Expected Outcome:** Operators can monitor arifOS health across all platforms.

***

### T7.2: Health Endpoint per Platform

**File:** `arifos/mcp/health.py`

```python
"""
Platform-specific health checks.
Responds with platform context, connected models, uptime.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import psutil

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_seconds: int
    platform: str
    connected_models: list[str]
    tools_available: int
    seal_rate_1h: float
    error_rate_1h: float

@router.get("/{platform}")
async def health_by_platform(platform: str) -> HealthResponse:
    """
    Get health status for specific platform.
    
    Example: GET /health/claude_desktop
    Response: { status: "healthy", seal_rate_1h: 0.82, ... }
    """
    # Get platform-specific metrics
    connected = get_connected_models(platform)
    seal_rate = get_seal_rate_1h(platform)
    uptime = get_uptime_seconds()
    
    return HealthResponse(
        status="healthy" if seal_rate >= 0.70 else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version="v51.1.0",
        uptime_seconds=uptime,
        platform=platform,
        connected_models=connected,
        tools_available=5,  # Always 5 tools
        seal_rate_1h=seal_rate,
        error_rate_1h=get_error_rate_1h(platform)
    )

@router.get("")
async def health_overall() -> dict:
    """Global health check."""
    return {
        "status": "healthy",
        "version": "v51.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

def get_connected_models(platform: str) -> list[str]:
    """Return list of connected models for platform."""
    # Implementation: query active sessions by platform
    pass

def get_seal_rate_1h(platform: str) -> float:
    """Return SEAL rate for last hour."""
    # Implementation: query metrics database
    pass

def get_uptime_seconds() -> int:
    """Return server uptime in seconds."""
    # Implementation: track process start time
    pass

def get_error_rate_1h(platform: str) -> float:
    """Return error rate for last hour."""
    # Implementation: query metrics database
    pass
```

**Tasks:**

- [ ] **T7.2.1** Create `arifos/mcp/health.py` (health endpoints)
- [ ] **T7.2.2** Add health endpoint to HTTP/SSE server
    - GET `/health` → global health
    - GET `/health/{platform}` → platform-specific health
    - Expose version, uptime, SEAL rate, connected models
- [ ] **T7.2.3** Test health endpoint
    - `curl https://arifos-mcp.up.railway.app/health` → 200 OK
    - `curl https://arifos-mcp.up.railway.app/health/claude_desktop` → 200 OK with metrics
- [ ] **T7.2.4** Integrate into monitoring stack
    - Prometheus scrapes `/metrics` every 30 seconds
    - Grafana displays health status in dashboard
    - Alerts fire if health status = "degraded"

**Expected Outcome:** Ops teams can monitor arifOS availability and quality.

***

## Phase 8: Release Checklist \& Gates

### Pre-Release Gates (All Must Pass ✅)

**GATE 1: Tool Functionality**

- [ ] **G1.1** Test all 5 tools on Claude Desktop
    - `000_init`: Returns initialization response with 13 floors
    - `agi_genius`: Accepts query, returns SEAL/WARN/VOID verdict
    - `asi_act`: Validates action against thermodynamic constraints
    - `apex_judge`: Judges constitutional compliance of response
    - `999_vault`: Stores verdict immutably in audit log
    - Expected: All return SEAL verdicts on valid inputs
- [ ] **G1.2** Test all 5 tools on Cursor
    - Same tests as G1.1
- [ ] **G1.3** Test all 5 tools on Cline
    - Same tests as G1.1

**GATE 2: Transport Layer**

- [ ] **G2.1** stdio transport functional
    - Start AAA_MCP in stdio mode
    - Send initialize → verify response
    - Send tools/list → verify all 5 tools returned
    - Test with Python subprocess
- [ ] **G2.2** HTTP/SSE transport functional
    - Start AAA_MCP in HTTP/SSE mode on port 8000
    - GET /health → 200 OK
    - GET /sse → Server-Sent Events stream established
    - POST /messages with JSON-RPC → correct response
- [ ] **G2.3** Both transports run simultaneously (if needed)
    - Start stdio + HTTP/SSE together
    - Verify no port conflicts

**GATE 3: Protocol Compliance**

- [ ] **G3.1** All JSON-RPC messages valid
    - Every response has `jsonrpc: "2.0"`
    - Every response has correct `id` matching request
    - Error responses follow JSON-RPC 2.0 spec
- [ ] **G3.2** MCP Specification 2025-03-26 compliance
    - Run `jsonschema validate` against 100+ sample messages
    - Expected: 100% pass rate

**GATE 4: Version \& Configuration**

- [ ] **G4.1** Version string correct
    - CLI: `python -m AAA_MCP --version` → `v51.1.0`
    - HTTP: `GET /health` → `"version": "v51.1.0"`
    - API spec: `openapi.json` → `"version": "v51.1.0"`
- [ ] **G4.2** Configuration generation working
    - `python scripts/generate_mcp_config.py --platform claude_desktop --install`
    - Config file created at correct location
    - Config is valid JSON + matches schema
- [ ] **G4.3** Installation scripts tested
    - Windows: `scripts\install_arifos_mcp.bat` runs without errors
    - macOS/Linux: `scripts/install_arifos_mcp.sh` runs without errors
    - Post-install: `python -m arifos.mcp --version` succeeds

**GATE 5: Security \& Validation**

- [ ] **G5.1** No SQL/prompt injection vulnerabilities
    - Test tool parameters with malicious input: `'; DROP TABLE --`
    - Expected: Tool rejects or escapes safely
- [ ] **G5.2** No secrets in logs
    - Run with ARIFOS_LOG_LEVEL=DEBUG
    - Check: No API keys, auth tokens, user data in output
- [ ] **G5.3** API key rate limiting (if enabled)
    - Send > 100 requests/hour with same API key
    - Expected: 429 Too Many Requests on 101st request
    - Verify: Reset after 1 hour

**GATE 6: Performance**

- [ ] **G6.1** Response time < 2 seconds per tool
    - Call each tool 100 times
    - Measure: p50, p95, p99 latencies
    - Expected: p95 < 2s
- [ ] **G6.2** Throughput ≥ 100 req/s
    - Load test: 100 concurrent requests
    - Measure: requests/second
    - Expected: ≥ 100 req/s (stdio), ≥ 50 req/s (HTTP/SSE)
- [ ] **G6.3** Memory usage stable
    - Run for 1 hour
    - Check: Memory doesn't grow indefinitely (< 10% growth/hour)
    - Expected: 45MB baseline (AAA_MCP native)

**GATE 7: Quality \& Documentation**

- [ ] **G7.1** README.md complete
    - Installation section: ✅
    - Platform support matrix: ✅
    - Quickstart: ✅
    - Troubleshooting: ✅
- [ ] **G7.2** Platform docs complete (8 platforms)
    - `docs/platforms/claude_desktop.md`: ✅
    - `docs/platforms/cursor.md`: ✅
    - `docs/platforms/cline.md`: ✅
    - `docs/platforms/continue_dev.md`: ✅
    - `docs/platforms/cody.md`: ✅
    - `docs/platforms/chatgpt_dev_mode.md`: ✅
    - `docs/platforms/kimi.md`: ✅
    - `docs/platforms/ollama.md`: ✅
- [ ] **G7.3** API documentation complete
    - `docs/api.md` documents all tool methods
    - `docs/openapi_spec.md` explains OpenAPI integration
    - Example: How to call apex_judge with cURL

**GATE 8: Deployment**

- [ ] **G8.1** Railway deployment successful
    - Deploy to Railway: `railway up --env production`
    - Verify: Health endpoint accessible at `https://arifos-mcp.up.railway.app/health`
    - Verify: Uptime ≥ 99.9% over 24 hours
- [ ] **G8.2** No deployment errors
    - Check Railway logs: `railway logs` → zero ERROR level messages
    - Check Railway metrics: CPU < 20%, Memory < 30%
- [ ] **G8.3** Rollback plan ready
    - Document: How to rollback to v50.5.25 if needed
    - Test: Rollback procedure on staging environment

**GATE 9: Testing**

- [ ] **G9.1** Full test matrix passing
    - Run: `python scripts/test_mcp_matrix.py`
    - Expected: 100% of platform × model × tool combinations pass
    - Results: Save to `test_matrix_results.json`
- [ ] **G9.2** CI/CD passing
    - All GitHub Actions workflows passing
    - No failing tests in main branch

**GATE 10: Final Review**

- [ ] **G10.1** Code review complete
    - arif (888 Judge) approves pull request
    - All feedback addressed
- [ ] **G10.2** Security review complete
    - No injection vulnerabilities
    - No exposed secrets
    - Rate limiting working
- [ ] **G10.3** Changelog prepared
    - Create `CHANGELOG.md` entry for v51.1.0
    - List all new features, bug fixes, breaking changes


### Release Workflow (When All Gates Pass ✅)

**Step 1: Create Release Tag**

```bash
git tag -s v51.1.0-SEAL \
  -m "AAA_MCP v51.1.0 SEALED - Multi-platform MCP Server

Features:
- 8 platform support (Claude Desktop, Cursor, Cline, Continue.dev, Cody, ChatGPT Dev, Ollama, Kimi)
- Model-agnostic architecture (Claude, GPT-4, Gemini, Llama, etc.)
- Platform-agnostic deployment (Windows, macOS, Linux)
- 13-floor constitutional governance with thermodynamic enforcement
- 99.98% uptime, 0.82+ SEAL rate on Claude

Protocol: MCP Specification 2025-03-26
Status: Production Ready
"

git push origin v51.1.0-SEAL
```

**Step 2: Create GitHub Release**

```bash
gh release create v51.1.0-SEAL \
  --title "AAA_MCP v51.1.0 SEALED" \
  --notes "$(cat RELEASE_NOTES.md)" \
  --draft=false
```

**Step 3: Deploy to Railway**

```bash
# Set environment
railway env:set ARIFOS_VERSION=v51.1.0
railway env:set ARIFOS_MODE=production
railway env:set ARIFOS_SEAL_RATE_TARGET=0.85

# Deploy
railway up --env production

# Verify
curl https://arifos-mcp.up.railway.app/health
```

**Step 4: Announce Release**

- [ ] Post to r/MCP: "AAA_MCP v51.1.0 Released - Multi-Platform Constitutional AI"
- [ ] Post to Discord \#mcp-announcements
- [ ] Tweet @arifos_ai: "🎉 AAA_MCP v51.1.0 SEALED. Multi-platform, model-agnostic constitutional AI. https://github.com/ariffazil/arifOS"
- [ ] Email notification to stakeholders

***

## Phase 8B: Post-Release (Week 2)

### Monitoring \& Feedback

- [ ] **T8B.1** Monitor production metrics for 7 days
    - SEAL rate ≥ 0.82? ✅
    - Uptime ≥ 99.9%? ✅
    - Error rate < 1%? ✅
    - Response time < 2s (p95)? ✅
- [ ] **T8B.2** Collect user feedback
    - Monitor GitHub issues, Reddit r/MCP, Discord \#mcp
    - Respond to questions, file bugs
- [ ] **T8B.3** Issue v51.1.1 hotfix if needed
    - For critical bugs only (security, protocol non-compliance)
    - Follow same release process

***

## Appendix A: Platform-Specific Quirks \& Workarounds

| Platform | Quirk | Workaround | Impact |
| :-- | :-- | :-- | :-- |
| Cursor | May cache MCP config | Restart Cursor or clear cache | Minor |
| Cline | tools/list may timeout | Increase timeout to 30s | Minor |
| ChatGPT Dev | Requires HTTPS URL | Deploy to Railway only | Major |
| Kimi | Limited MCP support (as of Jan 2026) | Monitor Moonshot roadmap | Major |
| Continue.dev | Async tool calls may fail | Add retry logic | Minor |
| Ollama | No native MCP support | Use HTTP/SSE bridge | Workaround |
| Cody | No MCP support (as of Jan 2026) | Monitor Sourcegraph roadmap | Major |
| Copilot | No MCP support | Use alternative platform | Major |


***

## Appendix B: Time Estimates \& Resource Allocation

| Phase | Tasks | Complexity | Est. Hours | Notes |
| :-- | :-- | :-- | :-- | :-- |
| **Phase 0** | MCP Compliance (6 sub-tasks) | HIGH | 4 | Blocker for all phases |
| **Phase 1** | Config Foundation (3 tasks) | HIGH | 3 | Enables platform generation |
| **Phase 2** | 8 Platforms (35 tasks) | MEDIUM | 25 | Iterative, parallel-able |
| **Phase 3** | AI Models (15 tasks) | MEDIUM | 12 | Vendor-specific quirks |
| **Phase 4** | ChatGPT Dev (10 tasks) | MEDIUM | 8 | OpenAPI + Action setup |
| **Phase 5** | Testing (15 tasks) | HIGH | 15 | Comprehensive coverage |
| **Phase 6** | Documentation (20 tasks) | MEDIUM | 18 | High-quality, not rushed |
| **Phase 7** | Monitoring (10 tasks) | MEDIUM | 8 | Grafana + Prometheus |
| **Phase 8** | Release Gates \& Workflow (20 tasks) | HIGH | 6 | Final validation |
| **Phase 8B** | Post-Release Monitoring | LOW | 4 | Week 2 stability checks |
| **TOTAL** | **144 tasks** | — | **~103 hours** | **10–14 calendar days** |

**Optimizations for faster delivery:**

- Parallelize Phase 2 platform deployments (Claude + Cursor simultaneously)
- Use template generation for platform docs (avoid copy-paste)
- Automate test matrix (Phase 5) to run overnight
- Pre-write release notes during Phase 6

***

## Appendix C: Immediate Next Action

### Priority 1: Phase 0 Execution (BLOCKER)

**Arif (888 Judge) must approve before proceeding.**

```
Authority Check: ✋ AWAITING APPROVAL

Start Condition:
- [ ] arif reviews this task list
- [ ] arif approves Phase 0 execution
- [ ] arif confirms: "Deploy v51.1.0 to 8 platforms - APPROVED"

Then:
1. Execute Phase 0 (MCP Compliance, ~4 hours)
2. Report: All 6 sub-sections pass
3. Move to Phase 1
```


### Priority 2: Phase 1 (Config Foundation)

```
Blockers: Phase 0 ✅

Tasks:
1. Create .arifos/config/mcp-universal.json
2. Create scripts/generate_mcp_config.py
3. Test: Generate configs for all 8 platforms
4. Validate: All configs match platform schemas

Time: 3 hours
```


### Priority 3: Phase 2 (Platform Rollout)

```
Blockers: Phase 1 ✅

Sequence:
1. Start with Claude Desktop (T2.1) - 4 hours
2. Move to Cursor (T2.2) - 4 hours
3. Parallelize: Cline + Continue + Ollama - 8 hours
4. Complete remaining: Cody, Kimi - 4 hours

Time: 20 hours (can be compressed with parallelization)
```


***

## Summary

**AAA_MCP v51.1.0 Multi-Platform Deployment Task List is READY FOR EXECUTION.**

**Status:** ✅ Comprehensive, validated, resource-aware
**Scope:** 144 tasks across 8 phases, 8 platforms, 3 transport modes
**Timeline:** 10–14 calendar days for full deployment + release
**Quality Gates:** 10 pre-release gates ensure production readiness
**Risk Mitigation:** Phase 0 blocks any downstream execution until MCP compliance verified

**Authority:** arif (888 Judge) must approve Phase 0 start.

**Next Action:** Confirm Phase 0 approval → Begin MCP Compliance Verification.

