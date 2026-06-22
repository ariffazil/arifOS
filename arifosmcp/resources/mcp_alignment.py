"""
arifos://mcp-alignment — MCP Spec Conformance Matrix
══════════════════════════════════════════════════════

Transparent conformance status vs. MCP 2025-11-25 specification.
Enables MCP clients (Claude Desktop, Cursor, etc.) to understand
which protocol features are supported, deprecated, or planned.

Auto-generated from live tool registry. Should be kept current
with each arifOS release cycle.

F-binding:
  F2: deterministic — derived from live tool/schema hashes
  F4: clarity — reduces discovery friction for MCP clients
  F11: auditable — every extension claim is verifiable

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

MCP_ALIGNMENT_TEXT = """\
---arifos_meta
resource_class: supplemental
authority_level: TRUSTED_REPO
truth_level: 3  # TRUSTED_REPO (1-7 scale)
owner: ARIF_FAZIL
version: 2026.06.21
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: LOW
evidence_level: DERIVED
staleness_policy: warn
last_attested: 2026-06-22T00:00:00Z
---end_arifos_meta

arifOS MCP Conformance Matrix
══════════════════════════════
Protocol Baseline: MCP 2025-11-25
arifOS Version: v2026.06.21-SSCT
Generated: 2026-06-21

CORE SPEC CONFORMANCE
─────────────────────
[✓] tools/list          — 27 tools registered (21 canonical + 6 canary)
[✓] tools/call          — Full JSON-RPC 2.0 tool invocation
[✓] resources/list      — 13 constitutional resources
[✓] resources/read      — All resources readable via URI
[✓] prompts/list        — Constitutional prompts registered
[✓] prompts/get         — Prompt template resolution
[✓] initialize          — MCP handshake with capabilities
[✓] ping                — Liveness probe
[✓] logging             — Structured log notifications
[~] elicitation         — Partial: form-elicitation on SEAL-class tools
[ ] completions         — Not implemented (constitutional guard)

EXTENSIONS SUPPORT
──────────────────
[✓] JSON Schema 2020-12 — inputSchema/outputSchema on all 21 canonical tools
[~] Pagination (SEP-2549) — Cursor-based on memory recall; not universal
[ ] Tasks (SEP-xxxx)   — Under evaluation for long-running governance adjudication
[ ] MCP Apps            — Not targeted (AAA cockpit serves operator surface)
[ ] OAuth Client Credentials — Not implemented (bearer token on A-FORGE)
[ ] Stateless Core      — Session required by constitutional design (F1, F11)

TRANSPORT
─────────
[✓] streamable-http     — Primary transport
[✓] SSE                 — Server-sent events for streaming responses
[✓] JSON-RPC 2.0        — Message framing

AUTH & SECURITY
───────────────
[✓] Session binding     — arif_init required for governed tools
[✓] Floor enforcement   — F1-F13 constitutional gates on all tool calls
[✓] Lease gating        — Mutation-class operations require capability lease
[✓] VAULT999 sealing    — Immutable audit trail for all terminal verdicts
[~] Bearer token        — A-FORGE only; not required on public arifOS surface
[ ] OAuth 2.0           — Not planned (sovereign single-operator system)

DEPRECATIONS
────────────
[!] arif_bridge         — Use arif_bridge_connect (canonical name)
[!] arif_kernel_attest  — Moving to arif_diag_attest
[!] arif_kernel_health  — Moving to arif_diag_health
[!] arif_kernel_route   — Use arif_route (canonical name)
[!] arif_kernel_status  — Moving to arif_diag_telemetry
[!] arif_memory_recall  — Use arif_memory (canonical name)
[!] forge_* on arifOS   — Deprecated proxy; canonical home is A-FORGE :7071

RESOURCES (13 LIVE)
───────────────────
arifos://doctrine        — F1-F13 immutable constitution
arifos://trinity          — AAA Trinity lane architecture
arifos://schema           — Complete MCP surface blueprint
arifos://civilization     — Federation organ ontology
arifos://seal-readiness   — Vault integrity + seal gate
arifos://jurisdiction     — Autonomy bands + capability grants
arifos://identity         — Sovereign identity manifest
arifos://memory           — Six-layer memory architecture (L1-L6)
arifos://vitals           — Constitutional metrics reference
arifos://bootstrap        — Full federation world-model (v2026.06.14)
arifos://human/metabolized — Compact sovereign context
tree777://index           — TREE777 wiki full index
runner://policy/v1        — Context runner pinned policy

MCP REGISTRY READINESS
──────────────────────
[✓] server-card.json     — .well-known/mcp/server-card.json
[✓] llms.txt             — LLM-readable discovery document
[~] Registry publishing  — Not yet submitted to official MCP Registry
[ ] Conformance tests    — MCP Inspector not yet run against 2025-11-25 suite

CLIENT COMPATIBILITY
────────────────────
Claude Desktop  — Full (primary client)
Cursor          — Partial (resources not yet indexed)
VS Code Copilot — Untested
Continue.dev    — Untested
Zed             — Untested

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""


def register_mcp_alignment(mcp: FastMCP) -> list[str]:
    """Register arifos://mcp-alignment — MCP spec conformance matrix.

    Static resource. Update text content when protocol surface changes.
    """
    resource = TextResource(
        uri="arifos://mcp-alignment",
        name="MCP Spec Conformance Matrix",
        description=(
            "Current conformance status of arifOS vs. MCP 2025-11-25 specification. "
            "Covers core spec (tools, resources, prompts, elicitation), extensions "
            "(JSON Schema 2020-12, Pagination, Tasks, MCP Apps, OAuth), transport, "
            "auth/security posture, deprecations, live resource inventory, and "
            "client compatibility matrix. Use to understand what an MCP client can "
            "expect from this server before connecting."
        ),
        text=MCP_ALIGNMENT_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://mcp-alignment"]


__all__ = [
    "MCP_ALIGNMENT_TEXT",
    "register_mcp_alignment",
]
