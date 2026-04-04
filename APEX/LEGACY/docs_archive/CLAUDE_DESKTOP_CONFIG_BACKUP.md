# Claude Desktop Config Backup — Pre-Nuclear Reinstall
**Sealed:** 2026-03-07 | **Reason:** Claude Desktop v1.1.4498 startup crash (launch-failure.err)

---

## 1. Claude Desktop MCP Config
**Restore to:** `C:\Users\User\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
    "mcpServers": {
        "arifos": {
            "url": "https://arifosmcp.arif-fazil.com/mcp"
        },
        "filesystem": {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "C:\\Users\\User\\arifOS",
                "C:\\Users\\User\\Documents"
            ]
        },
        "github": {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
            }
        },
        "context7": {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@upstash/context7-mcp"
            ]
        },
        "sqlite": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "mcp-server-sqlite",
                "--db-path",
                "C:\\Users\\User\\mcp_databases"
            ]
        },
        "qdrant": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "mcp-server-qdrant"
            ],
            "env": {
                "QDRANT_LOCAL_PATH": "C:\\Users\\User\\.qdrant\\local-db",
                "COLLECTION_NAME": "claude-memory",
                "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
            }
        },
        "code-sandbox": {
            "command": "C:\\Users\\User\\AppData\\Local\\code-sandbox-mcp\\code-sandbox-mcp.exe"
        }
    },
    "preferences": {
        "coworkScheduledTasksEnabled": true,
        "sidebarMode": "chat",
        "coworkWebSearchEnabled": true,
        "localAgentModeTrustedFolders": [
            "C:\\Users\\User"
        ]
    }
}
```

---

## 2. Claude Code MCP Config (NOT affected by reinstall — kept for reference)
**Lives at:** `C:\Users\User\.claude\mcp.json` — **DO NOT DELETE, survives reinstall automatically**

Key arifOS entries:
- `aaa-mcp` → local Python MCP via `.venv/Scripts/python.exe -m aaa_mcp stdio`
- `aclip-cai` → local ACLIP CAI via `.venv/Scripts/python.exe -m aclip_cai stdio`
- `memory` → MCP memory → `C:/Users/User/VAULT999/mcp-memory.json`
- `qdrant` → local Qdrant vector store → `C:\Users\User\.qdrant\local-db`
- `code-sandbox` → `C:\Users\User\AppData\Local\code-sandbox-mcp\code-sandbox-mcp.exe`

---

## 3. Critical arifOS-Specific Entry (Most Important)

The single most important entry to restore is the **remote arifOS MCP server**:
```json
"arifos": {
    "url": "https://arifosmcp.arif-fazil.com/mcp"
}
```
This connects Claude Desktop directly to the live arifOS VPS constitutional governance chain.

---

## 4. Extensions to Reinstall (from Claude Desktop Marketplace)
After reinstall, these extensions were active (reinstall from marketplace):
- Filesystem
- Control Chrome
- Context7
- PDF Tools - Analyze, Extract, Fill, Compare
- Enrichr MCP Server
- ToolUniverse
- Kubernetes MCP Server
- Read and Send iMessages
- ~~Desktop Commander~~ ← **THIS CAUSED THE CRASH — skip for now**

---

## 5. Reinstall Steps

1. **Backup this file** ✅ (done)
2. Open **Microsoft Store** → Your Library → Find **Claude** → **Uninstall**
3. Reinstall **Claude** from Microsoft Store
4. On first launch, do NOT connect any MCP servers yet
5. Open `C:\Users\User\AppData\Roaming\Claude\claude_desktop_config.json`
6. Paste the config from Section 1 above
7. Restart Claude Desktop
8. Verify `arifos` MCP server connects (check MCP status in settings)

---

## 6. What Survives the Reinstall (no action needed)
- `C:\Users\User\.claude\` — entire Claude Code config directory
- `C:\Users\User\.claude\mcp.json` — Claude Code MCP servers
- `C:\Users\User\arifOS\` — the entire arifOS project
- `C:\Users\User\VAULT999\` — constitutional vault ledger
- All chat history (cloud-synced to claude.ai account)
