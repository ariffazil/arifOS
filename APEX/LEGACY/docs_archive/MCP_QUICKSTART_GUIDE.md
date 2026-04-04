# arifOS MCP Server v53.1.0 - Quick Start Guide

**Version:** v53.1.0-CODEBASE
**Status:** ✅ OPERATIONAL
**Architecture:** Hybrid (Codebase Microservices + Monolith Kernel)
**Date:** 2026-01-27

---

## 🚀 Quick Start (2 Minutes)

### **Step 1: Install & Setup**
For developers working with the new **Codebase Architecture**:

```bash
# 1. Clone & Enter
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# 2. Install Local Package (Critical for v53)
pip install -e .
```

### **Step 2: Start the Server (Hybrid Mode)**
This starts the Codebase MCP server which proxies commands to the Constitutional Kernels.

```bash
# Start SSE Server (Railway/Remote Compatible)
python -m mcp.sse
```
*Port defaults to 8000. Access via `http://localhost:8000/sse`*

### **Step 3: Connect Your Client**
Configure Claude Desktop or other MCP clients:

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "uv",
      "args": ["run", "codebase-mcp-stdio"]
    },
    "arifos-remote": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## 🛠️ The Uniform Capability Triad

All engines (AGI, ASI, APEX) now support the **Physics-Math-Language** standard.

| Intent | Action Key | Purpose |
| :--- | :--- | :--- |
| **Physics** | `physics` | **Reasoning.** Model reality/causality. |
| **Math** | `math` | **Measurement.** Score truth, ethics, or confidence. |
| **Language** | `language` | **Action.** Execute, forge text, or seal verdicts. |

### Example Tool Calls
```python
# AGI: Model the physics of a query
agi_genius(action="physics", query="Why is the sky blue?")

# ASI: Measure the empathy of a response
asi_act(action="math", text="User response...", session_id="...")

# APEX: Render a verdict (Language action)
apex_judge(action="language", query="...", response="...")
```

---

## 🏛️ Architecture Overview

**v53.1.0** introduces the **Codebase Microservices** layer:
1.  **Transport:** `codebase/mcp/sse.py` (Handles HTTP/SSE)
2.  **Bridge:** `codebase/mcp/bridge.py` (Adapts intent to kernel calls)
3.  **Manager:** `codebase/kernel.py` (Manages Constitutional Kernels)
4.  **Kernels:** `codebase/engines/` (Proxies to `arifos.core`)

This ensures that the "Codebase" you see is the actual executable surface, not just a wrapper.

---

## 🔧 Troubleshooting

### **"Module not found: codebase"**
**Fix:** You skipped the install step.
```bash
pip install -e .
```

### **"Contextual Kernel Unavailable"**
**Fix:** The Bridge is working, but it can't find the `arifos` monolith. Ensure you are in the root directory where `arifos/` exists.

### **"Connection Refused"**
**Fix:** Ensure the server is running on port 8000.
Check logs for `[BOOT] Codebase MCP v53.1.0 starting`.

---

**DITEMPA BUKAN DIBERI**
