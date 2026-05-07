"""
audit_data_structure.py — Full audit data model for arifOS dual-node dashboard

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

audit_data = {
    "meta": {
        "epoch": "2026-04-19T19:39:00+08:00",
        "auditor": "ARIF-Perplexity Coarchitect",
        "pipeline_stage": "000 INIT → 888 AUDIT",
        "verdict": "SEAL",
        "dS": -0.01,
        "peace2": 1.0,
        "confidence": 0.91,
    },
    "nodes": {
        "vps": {
            "endpoint": "https://mcp.arif-fazil.com/",
            "server_id": "arifos_vps_0e93e5ecc88449ad881a32f0ecbee703",
            "status": "ALIVE",
            "session": "sess-eeb69dfa0f2fa473",
            "session_anchored": False,
            "governance_verdict": "SEAL",
            "verified": False,
            "risk_tier": "low",
            "platform": "mcp",
            "stage": "000_INIT",
            "tools_loaded": 44,
            "tool_namespaces": ["arifos_", "P_", "T_", "V_", "M_", "E_"],
            "chaos_score": "HIGH",
            "metabolic": {
                "dS": -0.01,
                "peace_squared": 1.0,
                "vitality": 1.0,
                "metabolic_stage": "LEBUR/MELTED",
                "governance_state": "BIJAKSANA/WISE",
                "actions_pending": 1,
                "pending_action_type": "GANTUNG",
            },
            "issues": [
                "GANTUNG-001",
                "SESSION-PERSIST-001",
                "TOOL-SURFACE-001",
                "TOOL-SURFACE-002",
            ],
        },
        "fastmcp": {
            "endpoint": "https://arifOS.fastmcp.app/mcp",
            "server_id": "arifos_2e43a6d010d84bf2ba2e7a7a82774b71",
            "status": "ALIVE",
            "session": "sess-f7b4798c4a36a2bf",
            "session_anchored": False,
            "governance_verdict": "SEAL",
            "verified": False,
            "risk_tier": "low",
            "platform": "mcp",
            "stage": "000_INIT",
            "tools_loaded": 11,
            "tool_namespaces": ["arifos_"],
            "chaos_score": "LOW",
            "metabolic": None,
            "notes": "Lightweight routing layer; metabolic tools not exposed by design",
            "issues": [],
        },
    },
    "side_by_side": {
        "tool_count": {"vps": 44, "fastmcp": 11},
        "namespace_count": {"vps": 6, "fastmcp": 1},
        "chaos_comparison": "fastMCP wins on clarity for external agents",
        "optimal_public_surface": 13,
    },
    "issues": [
        {
            "id": "GANTUNG-001",
            "title": "GANTUNG Pending Action",
            "node": "VPS",
            "difficulty": "Easy",
            "status": "OPEN",
            "priority": "HIGH",
            "action": "Run arifos_vault(mode='read') with credentials to inspect queued HOLD",
            "root_cause_hypothesis": "Stranded vault write or unresolved HOLD from a prior session",
            "fix_command": "python arifOS_horizon_cli.py vault --mode read --actor_id ARIF --intent 'inspect gantung'",
        },
        {
            "id": "SESSION-PERSIST-001",
            "title": "Session Token Not Persisting Across Tool Calls",
            "node": "VPS",
            "difficulty": "Medium",
            "status": "OPEN",
            "priority": "CRITICAL",
            "root_cause": (
                "CANONICAL_TOOL_HANDLERS['arifos_sense'] pointed to raw arifos_sense function "
                "instead of _arifos_sense_public wrapper, bypassing _load_public_session_context"
            ),
            "fix_deployed_locally": True,
            "fix_deployed_vps": False,
            "fix_description": "Line 2990 in tools.py: 'arifos_sense': arifos_sense  →  'arifos_sense': _arifos_sense_public",
            "verify_command": (
                "python arifOS_horizon_cli.py init --actor_id ARIF --intent 'test'\n"
                "# Then call arifos_sense with returned session token\n"
                "# Expected: actor=ARIF, verified=True persists\n"
                "# Before fix: actor=anonymous, verified=False"
            ),
        },
        {
            "id": "TOOL-SURFACE-001",
            "title": "VPS Tool Surface Too Large for External Agents",
            "node": "VPS",
            "difficulty": "Low",
            "status": "OPEN",
            "priority": "MEDIUM",
            "observation": "44 tools across 6 namespaces (P/T/V/M/E) vs fastMCP's 11 tools in 1 namespace",
            "recommendation": (
                "Keep 44 tools server-side for internal orchestration; "
                "expose only 13 tools publicly via arifos_kernel as routing gateway"
            ),
            "rationale": (
                "External agents cold-start better with fewer tools; "
                "selection error probability scales with N"
            ),
            "architecture_preferred": (
                "fastMCP = public face (13 tools) + VPS = governed internal brain (44 tools)"
            ),
        },
        {
            "id": "TOOL-SURFACE-002",
            "title": "Domain Internals Leaked to External Agents",
            "node": "VPS",
            "difficulty": "Medium",
            "status": "OPEN",
            "priority": "MEDIUM",
            "leaked_tools": [
                "T_petrophysics_compute",
                "T_stratigraphy_correlate",
                "V_npv_evaluate",
                "P_well_floor_scan",
            ],
            "recommendation": (
                "Gate domain tools behind arifos_kernel routing; "
                "do not enumerate in public tool manifest"
            ),
        },
    ],
    "next_actions": [
        {
            "step": 1,
            "tool": "arifos_init",
            "params": {"mode": "init", "actor_id": "ARIF", "intent": "anchor session"},
            "node": "VPS",
            "purpose": "Establish verified session",
        },
        {
            "step": 2,
            "tool": "arifos_vault",
            "params": {"mode": "read"},
            "node": "VPS",
            "purpose": "Inspect GANTUNG-001 pending action",
        },
        {
            "step": 3,
            "tool": "arifos_sense",
            "params": {"query": "test", "mode": "governed"},
            "node": "VPS",
            "purpose": "Verify session persistence fix after VPS deploy",
        },
        {
            "step": 4,
            "tool": "P_well_readiness_check",
            "params": {},
            "node": "VPS",
            "purpose": "Confirm WELL biological floor status",
        },
    ],
    "constitutional_checks": {
        "F1_AMANAH": {
            "status": "PASS",
            "note": "No destructive operations observed",
        },
        "F2_TRUTH": {
            "status": "PASS",
            "note": "F2 floor active on both nodes",
        },
        "F3_TRI_WITNESS": {
            "status": "PASS",
            "note": "Witness: human=1, AI=1 on VPS",
        },
        "F4_CLARITY": {
            "status": "FAIL",
            "note": "fastMCP wins; VPS 44-tool surface violates clarity (ΔS≤0)",
        },
        "F5_PEACE2": {
            "status": "PASS",
            "note": "peace2=1.0 on VPS",
        },
        "F9_ETHICS": {
            "status": "PASS",
            "note": "C_dark threshold not reached",
        },
        "F11_AUTH": {
            "status": "PASS",
            "note": "Unanchored sessions correctly require init first",
        },
        "F13_SOVEREIGN": {
            "status": "PASS",
            "note": "Human override always possible",
        },
    },
    "witness": {
        "human": 1.0,
        "ai": 1.0,
        "earth": 0.0,
        "nodes_audited": 2,
        "nodes_alive": 2,
        "holds": 1,
    },
}


if __name__ == "__main__":
    import json

    print(json.dumps(audit_data, indent=2))
