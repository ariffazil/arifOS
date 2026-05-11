# Guide untuk AI Fahmi: Connect ke arifOS MCP

---

## Step 1: Add MCP Server ni dalam AI config awak

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

---

## Step 2: Lepas tu, awak boleh call tools ni

| Tool | Description |
|------|-------------|
| `init_anchor` | Mula session dengan arifOS |
| `physics_reality` | Cari info dari web |
| `math_estimator` | Kira kos thermodynamic |
| `engineering_memory` | Simpan/recall memory |
| `apex_judge` | Check safety sesuatu action |

---

## Contoh Call

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "init_anchor",
    "arguments": {
      "mode": "status",
      "declared_name": "FahmiAgent"
    }
  },
  "id": 1
}
```

---

## Response yang Betul

 Kalau berjaya, akan dapat:
```json
{
  "verdict": "SEAL",
  "status": "SUCCESS"
}
```

 Kalau dapat VOID — itu bermakna action tersebut diblock oleh 13 constitutional floors.

---

## That's It!

AI awak sekarang ada:
- 40 tools
- 13 constitutional floors governance
- Memory (vector search)
- Safety checks

Enjoy! 🧠
