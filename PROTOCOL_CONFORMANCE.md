# PROTOCOL_CONFORMANCE.md — arifOS Governance Kernel

> Layer: L1 · Role: Constitutional governance, session, identity, verdict pipeline · Repo: ariffazil/arifos

## MCP Conformance
| Requirement | Status | Evidence |
|------------|--------|----------|
| llms.txt | ✅ | `/root/arifOS/llms.txt` — 65 tools, 25 resources declared |
| tools/list | ✅ | `:8088` — 8 kernel verbs (arif_init, arif_observe, arif_think, arif_route, arif_judge, arif_memory, arif_forge, arif_seal) |
| health endpoint | ✅ | `:8088/health` — returns status, identity_hash, federation_schema_version, mcp_protocol_version |
| MCP protocol versions | ✅ | Supports 2025-11-25, 2025-03-26, 2024-11-05 |

## FastMCP Conformance
| Requirement | Status | Evidence |
|------------|--------|----------|
| FastMCP server | ✅ | Python 3.12 FastMCP runtime on port 8088 |
| Resource discovery | ✅ | 25 MCP resources via active SkillsDirectoryProvider |
| Tool registry | ✅ | Canonical kernel verb set — 000/111/333/444/888/777/999 pipeline |

## A2A Conformance
| Requirement | Status | Evidence |
|------------|--------|----------|
| Agent card | ✅ | `static/.well-known/agent-card.json` — full schema with governance, tool_domains, verdict_system |
| Task schema | ✅ | A2A task operations via kernel routing (arif_route with bridge mode) |
| Streaming | ❌ | No SSE streaming support |
| A2A gateway | ⚠️ | Delegated to AAA (:3001); arifOS itself is the kernel, not the A2A router |

## XMCP Conformance
| Requirement | Status | Evidence |
|------------|--------|----------|
| App schema | ✅ | `static/.well-known/webmcp.json` — MCP Apps: arifos-webmcp adapter |
| Resource schema | ✅ | 25 MCP resources discoverable via resources/list |
| DID identity | ✅ | `static/.well-known/did.json` — federated identity |
| Security | ✅ | `static/.well-known/security.txt` |
| AI plugin | ✅ | `static/.well-known/ai-plugin.json` |

## Gaps
| Gap | Priority | Detail |
|-----|----------|--------|
| Streaming (A2A SSE) | P2 | No SSE support in arifOS kernel; low priority since AAA handles A2A transport |
| Direct A2A routing | P2 | arifOS routes through AAA for A2A; acceptable for L1 governance role |

## Required Compliance
- L1 Protocol: MCP (mandatory) + FastMCP (mandatory for Python organs) + A2A (agent card mandatory) + XMCP (apps mandatory)
- Federation schema version: 2.0.0
- Release: v2026.07.24-ZEN-SURVIVAL
- Next milestone: Zero gaps in MCP and FastMCP — already compliant

---
Generated: 2026-07-19 · Authority: AAA Control Plane
DITEMPA BUKAN DIBERI
