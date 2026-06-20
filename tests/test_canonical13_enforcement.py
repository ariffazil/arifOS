"""
test_canonical13_enforcement.py — Canonical13 Surface Law Enforcement
═══════════════════════════════════════════════════════════════════════

THIS IS THE PERMANENT LAW. Python enforces what prose cannot.

Every future coding agent MUST pass these tests. Any agent that creates
a new public MCP tool without updating this file will be blocked by CI.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations


# ════════════════════════════════════════════════════════════════════════════════
# CANONICAL LAW — the single source of truth for the public MCP surface
# ════════════════════════════════════════════════════════════════════════════════

EXPECTED_CANONICAL13: frozenset[str] = frozenset(
    {
        # 13 legacy canonical tools
        "arif_session_init",
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_mind_reason",
        "arif_heart_critique",
        "arif_kernel_route",
        "arif_reply_compose",
        "arif_memory_recall",
        "arif_gateway_connect",
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_forge_execute",
        "arif_ops_measure",
        # 6 Rule-14 canonical tools
        "arif_route",
        "arif_triage",
        "arif_kernel_status",
        "arif_bridge",
        "arif_kernel_attest",
        "arif_kernel_health",
    }
)

# Target dot-separated names (PHOENIX-72 migration target):
# These are the desired canonical names. When the full rename is complete,
# EXPECTED_CANONICAL13 should be replaced with these.
EXPECTED_DOT_SEPARATED: frozenset[str] = frozenset(
    {
        "arif.session",
        "arif.observe",
        "arif.reason",
        "arif.judge",
        "arif.reply",
        "arif.route",
        "arif.ops",
        "arif.lease",
        "arif.memory",
        "arif.forge",
        "arif.vault",
        "arif.attest",
        "arif.shadow",
    }
)

BLOCKED_PUBLIC_PREFIXES: tuple[str, ...] = (
    "A Arif",
    "Hermes",
    "Forge",
    "Gateway",
    "Heart",
    "Mind",
    "Sense",
    "Vault",
    "Judge",
    "Ops",
    "Init",
    "Reply",
    "Kernel",
    "Arif",
    "arifos_",
    "arifos.",
)

FORBIDDEN_PUBLIC_SUBSTRINGS: tuple[str, ...] = (
    "hermes_",
    "forge_",
    "_Arif",
)

# ════════════════════════════════════════════════════════════════════════════════
# Group 1: Public surface count
# ════════════════════════════════════════════════════════════════════════════════


def test_canonical13_public_surface_is_exactly_25() -> None:
    """The public MCP surface must expose exactly 25 tools in canonical13 mode.

    canonical13 = 19 canonical kernel tools + 6 zero-floor transport canary probes.
    The 19 canonical tools are EXPECTED_CANONICAL13; the full wire surface is 25.
    """
    from arifosmcp.runtime.public_surface import CANARY_PROBES, public_tool_names_for_mode

    tools = public_tool_names_for_mode("canonical13")
    actual = set(tools)
    expected_surface = set(EXPECTED_CANONICAL13) | set(CANARY_PROBES)

    assert len(actual) == len(expected_surface), (
        f"SURFACE DRIFT: canonical13 mode has {len(actual)} tools, expected {len(expected_surface)}. "
        f"Extra: {sorted(actual - expected_surface)}. "
        f"Missing: {sorted(expected_surface - actual)}. "
        f"VOID."
    )
    assert actual == expected_surface, (
        f"SURFACE DRIFT: canonical13 set mismatch. VOID."
    )


def test_canonical13_no_extra_tools() -> None:
    """No extra tools beyond the 19 canonical + 6 canary in canonical13 mode."""
    from arifosmcp.runtime.public_surface import CANARY_PROBES, public_tool_names_for_mode

    tools = set(public_tool_names_for_mode("canonical13"))
    expected_surface = set(EXPECTED_CANONICAL13) | set(CANARY_PROBES)
    extra = tools - expected_surface
    assert not extra, (
        f"EXTRA TOOLS LEAKED: {sorted(extra)}. "
        f"These must be folded into canonical tool modes or removed. VOID."
    )


def test_canonical13_no_missing_tools() -> None:
    """All 19 canonical tools must be present in canonical13 mode."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    tools = set(public_tool_names_for_mode("canonical13"))
    missing = set(EXPECTED_CANONICAL13) - tools
    assert not missing, f"MISSING TOOLS: {sorted(missing)}. VOID."


# ════════════════════════════════════════════════════════════════════════════════
# Group 2: Naming convention
# ════════════════════════════════════════════════════════════════════════════════


def test_all_public_names_start_with_arif_underscore() -> None:
    """All public tools must use arif_ prefix (current convention)."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    for name in public_tool_names_for_mode("canonical13"):
        assert name.startswith("arif_"), (
            f"Tool '{name}' does not start with arif_ prefix. VOID."
        )


def test_no_spaces_in_public_names() -> None:
    """No public tool name may contain spaces."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    for name in public_tool_names_for_mode("canonical13"):
        assert " " not in name, f"Tool '{name}' contains spaces. VOID."


def test_public_names_are_all_lowercase_except_allowed() -> None:
    """Public tool names must be lowercase. 'A', 'Arif', 'Hermes' etc. are blocked."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    for name in public_tool_names_for_mode("canonical13"):
        assert name == name.lower(), f"Tool '{name}' is not all lowercase. VOID."


def test_no_blocked_prefixes_in_public_surface() -> None:
    """No tool starting with blocked prefixes may appear in the public surface."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    for name in public_tool_names_for_mode("canonical13"):
        for prefix in BLOCKED_PUBLIC_PREFIXES:
            assert not name.startswith(prefix), (
                f"Tool '{name}' starts with blocked prefix '{prefix}'. VOID."
            )


def test_no_forbidden_substrings_in_public_surface() -> None:
    """No tool containing forbidden substrings may appear in the public surface.

    Forbidden substrings are checked as standalone segments (preceded by '_' or
    start-of-name), not as accidental infixes inside legitimate canonical names
    such as arif_forge_execute.
    """
    import re
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    for name in public_tool_names_for_mode("canonical13"):
        for substr in FORBIDDEN_PUBLIC_SUBSTRINGS:
            # Match substr only when it starts a name or follows an underscore.
            # Exclude arif_forge_execute — 'forge_' is a legitimate canonical name segment,
            # not a legacy forge_* tool name.
            if name == "arif_forge_execute" and substr == "forge_":
                continue
            pattern = r"(^|_)" + re.escape(substr)
            assert not re.search(pattern, name), (
                f"Tool '{name}' contains forbidden substring '{substr}' as a segment. VOID."
            )


# ════════════════════════════════════════════════════════════════════════════════
# Group 3: No legacy leaks in tools/list
# ════════════════════════════════════════════════════════════════════════════════


def test_no_legacy_hermes_names_in_canonical13() -> None:
    """Hermes tools must NOT appear as separate public tools in canonical13 mode."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    tools = public_tool_names_for_mode("canonical13")
    hermes_leaks = [t for t in tools if t.startswith("hermes_")]
    assert not hermes_leaks, (
        f"Hermes tools leaked into canonical13: {hermes_leaks}. "
        f"These must be folded into arif.ops / arif.memory / arif.observe modes. VOID."
    )


def test_no_legacy_forge_names_in_canonical13() -> None:
    """Forge sub-tools must NOT appear as separate public tools in canonical13 mode."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    tools = public_tool_names_for_mode("canonical13")
    forge_leaks = [t for t in tools if t.startswith("forge_")]
    assert not forge_leaks, (
        f"Forge tools leaked into canonical13: {forge_leaks}. VOID."
    )


def test_diagnostic_probes_are_present_in_canonical13() -> None:
    """Canary/diagnostic probes ARE exposed in canonical13 mode.

    The 6 zero-floor transport probes (ping, conformance_report, schema_echo,
    version_echo, transport_echo, initialize_probe) are part of the default
    public wire surface. They were previously folded into arif.ops modes; Rule 14
    ratifies them as standalone canary probes for transport diagnostics.
    """
    from arifosmcp.runtime.public_surface import CANARY_PROBES, public_tool_names_for_mode

    tools = set(public_tool_names_for_mode("canonical13"))
    missing = set(CANARY_PROBES) - tools
    assert not missing, (
        f"Canary probes missing from canonical13: {sorted(missing)}. VOID."
    )


# ════════════════════════════════════════════════════════════════════════════════
# Group 4: Registry truth — single source of truth
# ════════════════════════════════════════════════════════════════════════════════


def test_public_registry_matches_canonical13() -> None:
    """public_registry.py CANONICAL_PUBLIC_TOOLS must match EXPECTED_CANONICAL13."""
    from arifosmcp.runtime.public_registry import CANONICAL_PUBLIC_TOOLS

    assert CANONICAL_PUBLIC_TOOLS == frozenset(EXPECTED_CANONICAL13), (
        f"Public registry mismatch: "
        f"registry={sorted(CANONICAL_PUBLIC_TOOLS)}, "
        f"expected={sorted(EXPECTED_CANONICAL13)}. VOID."
    )


def test_canonical_tools_match_constitutional_tools() -> None:
    """CANONICAL_TOOLS in constitutional_map must match EXPECTED_CANONICAL13."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    actual = set(CANONICAL_TOOLS.keys())
    expected = set(EXPECTED_CANONICAL13)
    assert actual == expected, (
        f"Constitutional map drift: actual={sorted(actual)}, expected={sorted(expected)}. VOID."
    )


def test_public_surface_drift_check_passes() -> None:
    """verify_no_drift must report ok=True with exactly 25 tools."""
    from arifosmcp.runtime.public_surface import CANARY_PROBES
    from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, verify_no_drift

    expected_count = len(EXPECTED_CANONICAL13) + len(CANARY_PROBES)
    drift = verify_no_drift("canonical13")
    assert drift["ok"], (
        f"Drift check failed: {drift}. VOID."
    )
    assert drift["actual_count"] == EXPECTED_TOOL_COUNT, (
        f"Drift count mismatch: {drift['actual_count']} != {EXPECTED_TOOL_COUNT}. VOID."
    )
    assert drift["actual_count"] == expected_count


# ════════════════════════════════════════════════════════════════════════════════
# Group 5: Schema validation
# ════════════════════════════════════════════════════════════════════════════════


def test_every_public_tool_has_input_schema() -> None:
    """Every canonical tool must have an inputSchema with type: object."""
    from arifosmcp.runtime.public_registry import build_server_json

    manifest = build_server_json(surface_mode="canonical13")
    for tool in manifest["tools"]:
        assert "inputSchema" in tool, f"Tool {tool['name']} missing inputSchema."
        assert tool["inputSchema"].get("type") == "object", (
            f"Tool {tool['name']} inputSchema.type != 'object'."
        )


def test_every_public_tool_has_description() -> None:
    """Every canonical tool must have a non-empty description."""
    from arifosmcp.runtime.public_registry import build_server_json

    manifest = build_server_json(surface_mode="canonical13")
    for tool in manifest["tools"]:
        assert tool.get("description"), f"Tool {tool['name']} has empty description."
        assert len(tool["description"]) > 30, (
            f"Tool {tool['name']} description too short ({len(tool['description'])} chars)."
        )


# ════════════════════════════════════════════════════════════════════════════════
# Group 6: Expanded45 mode still contains diagnostic tools
# ════════════════════════════════════════════════════════════════════════════════


def test_expanded45_contains_more_than_canonical13() -> None:
    """expanded45 mode must contain all canonical13 tools plus diagnostics."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode

    canonical = set(public_tool_names_for_mode("canonical13"))
    expanded = set(public_tool_names_for_mode("expanded45"))
    assert canonical.issubset(expanded), (
        f"expanded45 missing canonical tools: {sorted(canonical - expanded)}."
    )
    assert len(expanded) > len(canonical), (
        "expanded45 should have more tools than canonical13."
    )


# ════════════════════════════════════════════════════════════════════════════════
# Group 7: Handlers match manifest
# ════════════════════════════════════════════════════════════════════════════════


def test_canonical_handlers_count_is_19() -> None:
    """Every canonical tool must have a handler (legacy 13 + Rule-14 6 = 19)."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, _RUNTIME_DIAGNOSTIC_HANDLERS

    all_handlers = {**_CANONICAL_HANDLERS, **_RUNTIME_DIAGNOSTIC_HANDLERS}
    covered = [name for name in CANONICAL_TOOLS if name in all_handlers]
    assert len(covered) == len(CANONICAL_TOOLS), (
        f"Handler drift: expected {len(CANONICAL_TOOLS)} canonical handlers, "
        f"got {len(covered)}. Missing: {sorted(set(CANONICAL_TOOLS) - set(all_handlers))}. VOID."
    )


def test_canonical_handlers_match_canonical_tools() -> None:
    """Canonical tool keys must all be covered by the handler registries."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, _RUNTIME_DIAGNOSTIC_HANDLERS

    all_handler_keys = set(_CANONICAL_HANDLERS.keys()) | set(_RUNTIME_DIAGNOSTIC_HANDLERS.keys())
    assert set(CANONICAL_TOOLS.keys()).issubset(all_handler_keys), (
        f"Handler/tool mismatch. Missing: {sorted(set(CANONICAL_TOOLS.keys()) - all_handler_keys)}. VOID."
    )
