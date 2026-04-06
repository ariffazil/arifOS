file_path = r"c:\Users\User\arifOS\arifosmcp.transport\server.py"

with open(file_path, encoding="utf-8") as f:
    content = f.read()

# Replace decorators and exports
replacements = {
    '@mcp.tool(name="init_session", description="000_INIT — Session ignition + L0 Kernel injection + defense scan.")': '@mcp.tool(name="anchor_session", description="[Lane: Δ Delta] [Floors: F11, F12, F13] Session ignition & injection defense.")',
    "init_session = ToolHandle(_init_session)": "anchor_session = ToolHandle(_init_session)",
    '@mcp.tool(name="agi_cognition", description="111–444_AGI — Reason + integrate + draft response.")': '@mcp.tool(name="reason_mind", description="[Lane: Δ Delta] [Floors: F2, F4, F7, F8] AGI cognition & logic grounding.")',
    "agi_cognition = ToolHandle(_agi_cognition)": "reason_mind = ToolHandle(_agi_cognition)",
    '@mcp.tool(name="phoenix_recall", description="555_RECALL — Subconscious memory retrieval.")': '@mcp.tool(name="recall_memory", description="[Lane: Ω Omega] [Floors: F4, F7, F13] Associative memory traces.")',
    "phoenix_recall = ToolHandle(_phoenix_recall)": "recall_memory = ToolHandle(_phoenix_recall)",
    '@mcp.tool(name="asi_empathy", description="555–666_ASI — Validate + align.")': '@mcp.tool(name="simulate_heart", description="[Lane: Ω Omega] [Floors: F4, F5, F6] Stakeholder impact & care constraints.")',
    "asi_empathy = ToolHandle(_asi_empathy)": "simulate_heart = ToolHandle(_asi_empathy)",
    '@mcp.tool(name="apex_verdict", description="777–888_APEX — Forge + audit final verdict.")': '@mcp.tool(name="apex_judge", description="[Lane: Ψ Psi] [Floors: F1-F13] Sovereign verdict synthesis.")',
    "apex_verdict = ToolHandle(_apex_verdict)": "apex_judge = ToolHandle(_apex_verdict)",
    '@mcp.tool(name="sovereign_actuator", description="888_FORGE — Sandboxed execution of physical state mutations.")': '@mcp.tool(name="eureka_forge", description="[Lane: Ψ Psi] [Floors: F1, F11, F12] Sandboxed action execution.")',
    "sovereign_actuator = ToolHandle(_sovereign_actuator)": "eureka_forge = ToolHandle(_sovereign_actuator)",
    '@mcp.tool(name="vault_seal", description="999_VAULT — Commit decision to immutable vault.")': '@mcp.tool(name="seal_vault", description="[Lane: Ψ Psi] [Floors: F1, F3, F10] Immutable ledger persistence.")',
    "vault_seal = ToolHandle(_vault_seal)": "seal_vault = ToolHandle(_vault_seal)",
    '@mcp.tool(name="search", description="Read-only web search (Brave API if configured).")': '@mcp.tool(name="search_reality", description="[Lane: Δ Delta] [Floors: F2, F4, F12] Web grounding (Perplexity/Brave).")',
    "search = ToolHandle(_search)": "search_reality = ToolHandle(_search)",
    '@mcp.tool(name="fetch", description="Read-only fetch by URL/id from `search` results.")': '@mcp.tool(name="fetch_content", description="[Lane: Δ Delta] [Floors: F2, F4, F12] Raw evidence content retrieval.")',
    "fetch = ToolHandle(_fetch)": "fetch_content = ToolHandle(_fetch)",
    '@mcp.tool(name="system_audit", description="Read-only system audit (health + basic invariants).")': '@mcp.tool(name="audit_rules", description="[Lane: Δ Delta] [Floors: F2, F8, F10] Rule & governance audit checks.")',
    "system_audit = ToolHandle(_system_audit)": "audit_rules = ToolHandle(_system_audit)",
    '@mcp.tool(name="analyze", description="Read-only analysis helper for structured data.")\nasync def _analyze': "# Internal Tool\nasync def _analyze",
    "analyze = ToolHandle(_analyze)": "# analyze = ToolHandle(_analyze)",
}

for old, new in replacements.items():
    content = content.replace(old, new)


# Extract tools array in info resource and replace
old_tools = """        "tools": [
            "init_session",
            "agi_cognition",
            "asi_empathy",
            "apex_verdict",
            "vault_seal",
            "search",
            "fetch",
            "analyze",
            "system_audit",
        ],"""

new_tools = """        "tools": [
            "anchor_session",
            "reason_mind",
            "recall_memory",
            "simulate_heart",
            "critique_thought",
            "apex_judge",
            "eureka_forge",
            "seal_vault",
            "search_reality",
            "fetch_content",
            "inspect_file",
            "audit_rules",
            "check_vital",
        ],"""

content = content.replace(old_tools, new_tools)

# Extract __all__ list and replace
old_all = """__all__ = [
    "create_unified_mcp_server",
    "mcp",
    "init_session",
    "agi_cognition",
    "asi_empathy",
    "apex_verdict",
    "vault_seal",
    "search",
    "fetch",
    "analyze",
    "system_audit",
    "_resource_full_context_template",
    "_resource_tool_schemas",
    "_prompt_trinity_forge",
    "_prompt_anchor_reason",
    "_prompt_audit_then_seal",
]"""

new_all = """__all__ = [
    "create_unified_mcp_server",
    "mcp",
    "anchor_session",
    "reason_mind",
    "recall_memory",
    "simulate_heart",
    "critique_thought",
    "apex_judge",
    "eureka_forge",
    "seal_vault",
    "search_reality",
    "fetch_content",
    "inspect_file",
    "audit_rules",
    "check_vital",
    "_resource_full_context_template",
    "_resource_tool_schemas",
    "_prompt_trinity_forge",
    "_prompt_anchor_reason",
    "_prompt_audit_then_seal",
]"""

content = content.replace(old_all, new_all)

# Append missing stubs right before info resource
stubs = """
@mcp.tool(name="critique_thought", description="[Lane: Ω Omega] [Floors: F4, F7, F8] 7-organ alignment & bias critique.")
async def _critique_thought(session_id: str, query: str) -> Dict[str, Any]:
    return _envelope(stage="666_CRITIQUE", session_id=session_id, verdict="SEAL", payload={"status": "STUB_IMPLEMENTATION"})

critique_thought = ToolHandle(_critique_thought)

@mcp.tool(name="inspect_file", description="[Lane: Δ Delta] [Floors: F1, F4, F11] Filesystem inspection (read-only).")
async def _inspect_file(session_id: str, path: str) -> Dict[str, Any]:
    return _envelope(stage="111_INSPECT", session_id=session_id, verdict="SEAL", payload={"status": "STUB_IMPLEMENTATION"})

inspect_file = ToolHandle(_inspect_file)

@mcp.tool(name="check_vital", description="[Lane: Ω Omega] [Floors: F4, F5, F7] System health & vital signs.")
async def _check_vital(session_id: str) -> Dict[str, Any]:
    return _envelope(stage="555_HEALTH", session_id=session_id, verdict="SEAL", payload={"status": "STUB_IMPLEMENTATION"})

check_vital = ToolHandle(_check_vital)

# ═══════════════════════════════════════════════════════
# RESOURCES, TEMPLATES, PROMPTS (Full-context orchestration + Inspector completeness)
# ═══════════════════════════════════════════════════════
"""

content = content.replace(
    """# ═══════════════════════════════════════════════════════
# RESOURCES, TEMPLATES, PROMPTS (Full-context orchestration + Inspector completeness)
# ═══════════════════════════════════════════════════════""",
    stubs,
    1,
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates completed successfully.")
