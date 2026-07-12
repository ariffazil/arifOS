"""
MCP Registration for arifOS Entropy Integrity tools.

Import this module and call register_entropy_tools(mcp) to add
the 6 entropy integrity tools to an arifOS FastMCP server.

Usage in arifOS server.py:
    from entropy_integrity.mcp.entropy_kernel.register import register_entropy_tools
    register_entropy_tools(mcp)
"""

from typing import Any


def register_entropy_tools(mcp: Any) -> None:
    """Register all 6 entropy integrity tools on the arifOS MCP server."""

    from .entropy_observe import arif_entropy_observe
    from .j_state_assess import arif_j_state_assess
    from .correction_probe import arif_correction_probe
    from .consequence_trace import arif_consequence_trace
    from .entropy_route import arif_entropy_route
    from .j_gate import arif_j_gate

    @mcp.tool(
        name="arif_entropy_observe",
        description=(
            "Register a structured entropy or dark-geometry observation from an authorised organ. "
            "Collects observations WITHOUT producing a verdict. Validates against prohibited-inference policy. "
            "Observation enters J-state computation pipeline only after validation."
        ),
        tags={"domain": "entropy", "kind": "observe", "canonical": "v1"},
    )
    async def _entropy_observe(observation: dict) -> dict:
        return arif_entropy_observe(observation)

    @mcp.tool(
        name="arif_j_state_assess",
        description=(
            "Fuse organ observations into a judgment-integrity map. "
            "Computes 5 J-planes (reality_contact, authority_legitimacy, consequence_integration, "
            "correctability, purpose_fidelity) using MINIMUM-FLOOR aggregation. "
            "Never outputs a diagnosis or moral identity."
        ),
        tags={"domain": "entropy", "kind": "assess", "canonical": "v1"},
    )
    async def _j_state_assess(
        observation_refs: list[str],
        observations: list[dict],
        decision_ref: str,
        intended_purpose: str = "",
        claimed_authority: str = "",
        affected_parties: list[str] | None = None,
        action_reversibility: str = "REVERSIBLE",
    ) -> dict:
        return arif_j_state_assess(
            observation_refs=observation_refs,
            observations=observations,
            decision_ref=decision_ref,
            intended_purpose=intended_purpose,
            claimed_authority=claimed_authority,
            affected_parties=affected_parties,
            action_reversibility=action_reversibility,
        )

    @mcp.tool(
        name="arif_correction_probe",
        description=(
            "Generate a neutral challenge and record the response. "
            "Response to correction is stronger evidence than a single phrase. "
            "Modes: draft_probe, record_response, classify_response, close_probe."
        ),
        tags={"domain": "entropy", "kind": "probe", "canonical": "v1"},
    )
    async def _correction_probe(
        mode: str,
        observation_ref: str | None = None,
        signal_class: str | None = None,
        challenge_text: str | None = None,
        response_text: str | None = None,
        response_class: str | None = None,
    ) -> dict:
        return arif_correction_probe(
            mode=mode,
            observation_ref=observation_ref,
            signal_class=signal_class,
            challenge_text=challenge_text,
            response_text=response_text,
            response_class=response_class,
        )

    @mcp.tool(
        name="arif_consequence_trace",
        description=(
            "Trace who makes the decision, who receives benefits, who bears harm, "
            "and who can reverse it. Computes consequence_gap composite metric."
        ),
        tags={"domain": "entropy", "kind": "trace", "canonical": "v1"},
    )
    async def _consequence_trace(
        decision_ref: str,
        decision_owner: dict | None = None,
        benefit_bearers: list[dict] | None = None,
        cost_bearers: list[dict] | None = None,
        reversal_owner: dict | None = None,
        responsibility_gaps: list[str] | None = None,
    ) -> dict:
        return arif_consequence_trace(
            decision_ref=decision_ref,
            decision_owner=decision_owner,
            benefit_bearers=benefit_bearers,
            cost_bearers=cost_bearers,
            reversal_owner=reversal_owner,
            responsibility_gaps=responsibility_gaps,
        )

    @mcp.tool(
        name="arif_entropy_route",
        description=(
            "Route domain questions to the correct organ. "
            "Human stress/regulation → WELL; capital incentive/power → WEALTH; "
            "physical/ecological irreversibility → GEOX; implementation/runtime → A-FORGE."
        ),
        tags={"domain": "entropy", "kind": "route", "canonical": "v1"},
    )
    async def _entropy_route(
        signal_class: str | None = None,
        question: str | None = None,
        domain_hint: str | None = None,
    ) -> dict:
        return arif_entropy_route(
            signal_class=signal_class,
            question=question,
            domain_hint=domain_hint,
        )

    @mcp.tool(
        name="arif_j_gate",
        description=(
            "The only Kernel tool that converts J-state evidence into action posture. "
            "J0→VOID, J1→HOLD, J2→reversible only, J3→bounded, J4→witnessed. "
            "Never issues VAULT999 SEAL autonomously."
        ),
        tags={"domain": "entropy", "kind": "gate", "canonical": "v1"},
    )
    async def _j_gate(
        j_state: dict,
        intended_action: str = "",
        action_reversibility: str = "REVERSIBLE",
        requires_seal: bool = False,
    ) -> dict:
        return arif_j_gate(
            j_state=j_state,
            intended_action=intended_action,
            action_reversibility=action_reversibility,
            requires_seal=requires_seal,
        )
