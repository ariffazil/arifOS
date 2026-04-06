# arifOS Documentation Update Map
## Clean MCP Architecture & Deployment Documentation

**Generated:** 2026-04-06  
**Purpose:** Map all documentation files requiring updates for the clean MCP architecture, Docker deployment, and ChatGPT Apps SDK integration.

---

## 🔴 CRITICAL - Must Update

### 1. README.md (Root)
**Current State:** 75KB - Comprehensive but outdated  
**Required Updates:**
- [ ] Update tool names from symbolic to functional (e.g., `apex_soul` → `judge_verdict`)
- [ ] Add new clean architecture section (tools/resources/prompts separation)
- [ ] Add Docker deployment instructions
- [ ] Add ChatGPT Apps SDK integration section
- [ ] Update Quick Start to use `init_session_anchor` instead of `init_anchor`
- [ ] Add widget/CSP configuration notes
- [ ] Update architecture diagram if present

### 2. AGENTS.md (Root)
**Current State:** 9.8KB - Agent skills documentation  
**Required Updates:**
- [ ] Update tool references to functional names
- [ ] Add ChatGPT Apps SDK agent skills
- [ ] Update constitutional health check instructions
- [ ] Add widget interaction patterns

### 3. NEXUS_HORIZON.md (Root)
**Current State:** 4.5KB - Horizon gateway docs  
**Required Updates:**
- [ ] Add new functional tool aliases
- [ ] Update ChatGPT subset tools list
- [ ] Add widget resource documentation
- [ ] Update prompt aliases section

### 4. ROADMAP.md (Root)
**Current State:** 6.3KB - Already partially updated  
**Required Updates:**
- [ ] Mark ChatGPT Apps SDK integration as COMPLETE
- [ ] Mark Docker deployment as COMPLETE
- [ ] Mark clean specs architecture as COMPLETE
- [ ] Add Phase 2 (write-path) planning

### 5. TODO.md (Root)
**Current State:** 8.5KB - Already partially updated  
**Required Updates:**
- [ ] Mark completed items (Docker, ChatGPT, specs)
- [ ] Add new Phase 2 tasks

### 6. ops/DEPLOY.md
**Current State:** Unknown - Deployment procedures  
**Required Updates:**
- [ ] Add Docker deployment section
- [ ] Add docker-compose instructions
- [ ] Document widget/CSP setup
- [ ] Add ChatGPT Apps SDK deployment checklist

### 7. ops/HORIZON_DEPLOY.md
**Current State:** Unknown - Horizon-specific deployment  
**Required Updates:**
- [ ] Update for new tool aliases
- [ ] Add ChatGPT subset configuration
- [ ] Document widget hosting

---

## 🟡 IMPORTANT - Should Update

### 8. CHANGELOG.md (Root)
**Current State:** 38KB - Comprehensive changelog  
**Required Updates:**
- [ ] Add 2026.04.06 entry for clean specs architecture
- [ ] Document Docker deployment addition
- [ ] Document ChatGPT Apps SDK integration
- [ ] List new tool functional names

### 9. DEPLOY_CONFIG.md (Root)
**Current State:** 1.4KB - Deployment configuration  
**Required Updates:**
- [ ] Add Docker environment variables
- [ ] Document build args (ARIFOS_BUILD_SHA, etc.)
- [ ] Add CSP configuration notes

### 10. TEST_REPORT_HORIZON_II_1.md (Root)
**Current State:** 2.5KB - Test report  
**Required Updates:**
- [ ] Add clean specs test results
- [ ] Document ChatGPT subset validation
- [ ] Add Docker deployment verification

### 11. docs/QUICK_START.md
**Current State:** Unknown - Quick start guide  
**Required Updates:**
- [ ] Update to use functional tool names
- [ ] Add Docker quick start option
- [ ] Update session initialization flow

### 12. docs/architecture/TOOL_INVENTORY.md
**Current State:** Unknown - Tool inventory  
**Required Updates:**
- [ ] Replace with clean specs tool inventory
- [ ] Document 11 canonical tools with functional names
- [ ] Add resource inventory
- [ ] Add prompt inventory

### 13. docs/architecture/INTEGRATIONS.md
**Current State:** Unknown - Integration docs  
**Required Updates:**
- [ ] Add ChatGPT Apps SDK integration
- [ ] Document MCP Apps bridge
- [ ] Add widget integration details

---

## 🟢 NICE TO HAVE - Optional Updates

### 14. 000-999-implementation-plan.md (Root)
**Current State:** 4.5KB - Implementation plan  
**Required Updates:**
- [ ] Mark completed phases
- [ ] Update with clean architecture decisions

### 15. HEARTBEAT.md (Root)
**Current State:** 989B - Status heartbeat  
**Required Updates:**
- [ ] Update status for deployment

### 16. MEMORY.md (Root)
**Current State:** 1.5KB - Memory documentation  
**Required Updates:**
- [ ] Document new `load_memory_context` tool

### 17. docs/FASTMCP_ARIFOS_MASTER_GUIDE.md
**Current State:** Unknown - FastMCP guide  
**Required Updates:**
- [ ] Update for clean specs integration
- [ ] Document new tool registration

### 18. docs/guides/STDIO.md
**Current State:** Unknown - STDIO transport guide  
**Required Updates:**
- [ ] Add Docker STDIO usage

### 19. ops/infrastructure/VPS_ARCHITECTURE.md
**Current State:** Unknown - VPS architecture  
**Required Updates:**
- [ ] Document Docker architecture
- [ ] Add container networking

### 20. ops/infrastructure/VPS_CAPABILITIES_MAP.md
**Current State:** Unknown - Capabilities map  
**Required Updates:**
- [ ] Update with new tool capabilities

---

## 📋 UPDATE PRIORITY MATRIX

| File | Priority | Effort | Impact |
|------|----------|--------|--------|
| README.md | 🔴 Critical | High | Very High |
| AGENTS.md | 🔴 Critical | Medium | High |
| NEXUS_HORIZON.md | 🔴 Critical | Medium | High |
| ROADMAP.md | 🔴 Critical | Low | Medium |
| TODO.md | 🔴 Critical | Low | Medium |
| ops/DEPLOY.md | 🔴 Critical | Medium | High |
| CHANGELOG.md | 🟡 Important | Medium | Medium |
| DEPLOY_CONFIG.md | 🟡 Important | Low | Medium |
| docs/QUICK_START.md | 🟡 Important | Medium | High |
| docs/architecture/TOOL_INVENTORY.md | 🟡 Important | High | Medium |

---

## 📝 DOCUMENTATION STANDARDS

When updating docs, follow these standards:

### Tool Naming
- **Canonical (code):** `judge_verdict`, `init_session_anchor`, `route_execution`
- **Title (human):** "Apex Soul", "Init Anchor", "arifOS Kernel"
- **Legacy support:** Keep old names as aliases

### Resource URIs
- `arifos://bootstrap`
- `arifos://governance/floors`
- `arifos://status/vitals`
- `https://mcp.af-forge.io/widget/vault-seal` (ChatGPT widget)

### ChatGPT Apps SDK
- Phase 1: Read-only (`get_constitutional_health`, `render_vault_seal`, `list_recent_verdicts`)
- Phase 2: Write with F11/F13 review
- Widget URL with CSP headers

---

## ✅ UPDATE CHECKLIST

- [ ] README.md - Main project docs
- [ ] AGENTS.md - Agent skills
- [ ] NEXUS_HORIZON.md - Horizon gateway
- [ ] ROADMAP.md - Project roadmap
- [ ] TODO.md - Task tracking
- [ ] CHANGELOG.md - Version history
- [ ] DEPLOY_CONFIG.md - Deployment config
- [ ] ops/DEPLOY.md - Deployment procedures
- [ ] ops/HORIZON_DEPLOY.md - Horizon deployment
- [ ] TEST_REPORT_HORIZON_II_1.md - Test reports
- [ ] docs/QUICK_START.md - Quick start guide
- [ ] docs/architecture/TOOL_INVENTORY.md - Tool inventory
- [ ] docs/architecture/INTEGRATIONS.md - Integration docs

---

## 🎯 KEY MESSAGES TO COMMUNICATE

1. **Clean Architecture:** Tools, resources, prompts now cleanly separated per MCP spec
2. **Functional Naming:** Tool names are now verbs (`judge_verdict`) not mythic names
3. **Docker Ready:** Full Docker deployment with docker-compose
4. **ChatGPT Ready:** Apps SDK integration with CSP-compliant widget
5. **Backward Compatible:** Old tool names still work as aliases

---

**Next Action:** Start with README.md and AGENTS.md as highest priority.
