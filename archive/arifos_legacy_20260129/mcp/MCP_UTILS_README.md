# arifOS MCP Utils Server

**Version:** 1.0.0  
**Purpose:** Critical gap fillers for the arifOS MCP ecosystem

## Overview

This server provides essential utility tools that complement the constitutional AI tools in the main arifOS MCP server. While the main server focuses on AI governance (F1-F13 floors), this server provides practical utilities for development workflows.

## Tools

### 1. `fetch_url` - Web Content Fetcher

Fetch and extract content from URLs. Great for reading documentation, articles, and web pages.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to fetch (http/https only) |
| `method` | string | "GET" | HTTP method (GET, POST) |
| `timeout` | integer | 30 | Request timeout in seconds |
| `extract_text` | boolean | true | Extract main article text from HTML |
| `max_length` | integer | 100000 | Maximum characters to return |

**Example:**
```json
{
  "url": "https://arifos.arif-fazil.com/docs",
  "extract_text": true,
  "max_length": 50000
}
```

**Returns:**
```json
{
  "status": "success",
  "url": "https://...",
  "title": "Page Title",
  "content": "Extracted text content...",
  "status_code": 200,
  "text_extracted": true
}
```

---

### 2. `shell` - Command Executor

Execute shell commands with security guardrails. Uses a whitelist approach for allowed commands.

**Security Features:**
- ✅ Whitelist-based command filtering (60+ allowed commands)
- ✅ Blocked dangerous patterns (fork bombs, disk writes, etc.)
- ✅ Timeout protection (max 300s)
- ✅ Output size limits (10MB)
- ✅ Working directory validation

**Allowed Commands:**
- Python: `python`, `python3`, `pip`, `pytest`, `black`, `ruff`, `mypy`
- Node: `node`, `npm`, `npx`, `yarn`
- Git: `git`, `git status`, `git log`, `git diff`, `git branch`
- Build: `make`, `cmake`, `cargo`, `go`, `javac`
- Docker: `docker`, `docker-compose`
- System: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `pwd`, `echo`
- Files: `mkdir`, `touch`, `cp`, `mv`, `rm` (careful)
- Utils: `curl`, `tar`, `zip`, `sort`, `uniq`

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | string | required | Shell command to execute |
| `cwd` | string | "." | Working directory |
| `timeout` | integer | 300 | Timeout in seconds (max 300) |

**Example:**
```json
{
  "command": "git status",
  "cwd": "."
}
```

**Returns:**
```json
{
  "status": "success",
  "command": "git status",
  "returncode": 0,
  "stdout": "On branch main...",
  "stderr": "",
  "execution_time": 0.123
}
```

---

### 3. `grep_search` - Content Search

Search file contents using regex. Uses ripgrep (`rg`) when available, falls back to Python regex.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern` | string | required | Regex pattern to search |
| `path` | string | "." | Directory or file to search |
| `glob` | string | null | File pattern filter (e.g., "*.py") |
| `case_sensitive` | boolean | false | Case sensitive search |
| `output_mode` | string | "content" | "content", "files", or "count" |
| `head_limit` | integer | null | Limit number of results |
| `context_lines` | integer | 2 | Lines of context around matches |

**Example:**
```json
{
  "pattern": "class.*Engine",
  "path": "./arifos",
  "glob": "*.py",
  "output_mode": "content",
  "context_lines": 2
}
```

**Returns:**
```json
{
  "status": "success",
  "pattern": "class.*Engine",
  "tool": "ripgrep",
  "matches": [
    {
      "file": "arifos/core/agi/engine.py",
      "line": 42,
      "content": "class AGIEngine:"
    }
  ],
  "match_count": 15,
  "files_searched": 42,
  "execution_time": 0.045
}
```

---

## Installation

### Install Dependencies

```bash
# Required for fetch_url
pip install httpx beautifulsoup4

# Required for grep_search (optional but recommended)
# Install ripgrep: https://github.com/BurntSushi/ripgrep#installation
```

### Install as MCP Server

Add to your `.mcp.json` (Kimi CLI) or Claude Desktop config:

```json
{
  "mcpServers": {
    "arifOS-Utils": {
      "command": "python",
      "args": ["-m", "arifos.mcp.mcp_utils_server"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Or use the entry point after pip install:

```bash
pip install -e .
aaa-mcp-utils
```

---

## Running Standalone

```bash
# Direct execution
python -m arifos.mcp.mcp_utils_server

# Or via entry point (after pip install)
aaa-mcp-utils
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    arifOS MCP Utils Server                   │
├─────────────────────────────────────────────────────────────┤
│  fetch_url  │   shell   │   grep_search                      │
├─────────────────────────────────────────────────────────────┤
│  httpx      │ asyncio   │  ripgrep (rg)                      │
│  bs4        │ subprocess│  or Python regex                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparison: Main Server vs Utils Server

| Feature | arifOS Constitutional | arifOS Utils |
|---------|----------------------|--------------|
| **Purpose** | AI governance | Development utilities |
| **Tools** | init_000, agi_genius, asi_act, apex_judge, vault_999 | fetch_url, shell, grep_search |
| **Floors** | F1-F13 enforced | No constitutional enforcement |
| **Use Case** | AI safety filtering | Code development workflows |
| **Rate Limiting** | Yes (F11) | No |

---

## Security Considerations

### fetch_url
- ✅ Only http/https protocols allowed
- ✅ Timeout protection
- ✅ Content length limits
- ✅ User-Agent identification

### shell
- ✅ Whitelist-only commands
- ✅ Regex-based dangerous pattern blocking
- ✅ Timeout protection (5 min max)
- ✅ Output size limits (10MB)
- ✅ Working directory validation

### grep_search
- ✅ Path validation (must exist)
- ✅ No arbitrary file execution
- ✅ Read-only operation

---

## Changelog

### v1.0.0 (2026-01-29)
- Initial release
- Added `fetch_url` tool
- Added `shell` tool with security guardrails
- Added `grep_search` tool with ripgrep support

---

**DITEMPA BUKAN DIBERI**
