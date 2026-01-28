"""
codebase.mcp.tools.context_scope (v53.2.2)
Scope boundaries for technical documentation access.
F11 Command Auth: Gathers scope limits based on scar_weight.
"""

CONTEXT7_SCOPE = {
    "888_JUDGE": {
        "paths": ["arifos/**", "mcp/**", "vault-999/**", "config/**", "codebase/**"],
        "depth": "full",
        "includes_secrets": True,
    },
    "GUEST": {
        "paths": ["arifos/README.md", "arifos/docs/**", "mcp/tools/trinity_loop.py"],
        "depth": "summary",
        "includes_secrets": False,
    }
}

def validate_context_scope(
    query: str,
    scar_weight: float
) -> tuple[list[str], bool]:
    """
    Returns: (allowed_paths, includes_secrets)
    """
    tier = "888_JUDGE" if scar_weight >= 1.0 else "GUEST"
    scope = CONTEXT7_SCOPE[tier]
    return scope["paths"], scope["includes_secrets"]
