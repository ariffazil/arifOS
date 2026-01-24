# AAA_MCP Deployment Checklist

**Version:** v51.2.0 | **Status:** CORE COMPLETE, INFRA PENDING

---

## ✅ Already Complete

- [x] 5 Trinity tools (`000_init`, `agi_genius`, `asi_act`, `apex_judge`, `999_vault`)
- [x] stdio transport (`python -m AAA_MCP`)
- [x] SSE transport (`python -m AAA_MCP sse`)
- [x] bridge.py → arifos.core wiring
- [x] 13 Constitutional Floors active
- [x] Claude Desktop working locally
- [x] Railway SSE deployed

---

## Priority Order (Constitutional)

| Priority | Phase | Floor | Rationale |
|----------|-------|-------|----------|
| 1 | MCP Compliance | F2 Truth | Validate spec-compliance |
| 2 | Testing | F1 Amanah | Reversible verification |
| 3 | Config Scripts | F4 Clarity | Reduce user confusion |
| 4 | Platform Docs | F6 Empathy | Serve new users |

---

## P1: MCP Protocol Compliance (F2 Truth)

- [ ] JSON-RPC 2.0 validation (`jsonrpc`, `id`, `method`, `params`)
- [ ] Initialize handshake (`protocolVersion`, `capabilities`, `serverInfo`)
- [ ] tools/list returns 5 tools with valid JSON Schema
- [ ] tools/call response format (`content`, `isError`)
- [ ] Error codes: `-32601`, `-32602`, `-32603`
- [ ] **Quick win:** Validate with `mcp` CLI tools

---

## P2: Testing (F1 Amanah)

- [ ] `scripts/test_mcp_compliance.py`
- [ ] Test matrix: Platform × Model × Tool
- [ ] Document expected SEAL rates

---

## P3: Config Scripts (F4 Clarity)

- [ ] `scripts/install_claude_desktop.bat` (Windows)
- [ ] `scripts/install_cursor.sh`
- [ ] Universal config generator

---

## P4: Platform Docs (F6 Empathy)

- [ ] `docs/platforms/claude_desktop.md`
- [ ] `docs/platforms/cursor.md`
- [ ] `docs/platforms/cline.md`
- [ ] `docs/platforms/chatgpt.md`
- [ ] `docs/troubleshooting.md`

---

## Deferred

- Continue.dev, Cody, Kimi (waiting for MCP support)
- Prometheus metrics
- API key auth

---

**DITEMPA BUKAN DIBERI**
