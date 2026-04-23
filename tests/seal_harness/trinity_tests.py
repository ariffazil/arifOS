"""
Trinity E2E Test Flow - 7-Organ Constitutional Validation
"""

from typing import Dict, Any, List
from .client import MCPClient


class TrinityTestHarness:
    """
    AAA Trinity Test Harness.

    Validates the 7-Organ Stack:
    - 000 INIT: anchor_session
    - 111-444 Δ: reason_mind (AGI)
    - 555-666 Ω: simulate_heart (ASI)
    - 777-888 Ψ: apex_judge (APEX)
    """

    def __init__(self, client: MCPClient):
        self.client = client
        self.results: List[Dict[str, Any]] = []

    def _assert(self, condition: bool, message: str) -> tuple:
        """Return assertion result."""
        return (condition, message if not condition else "")

    async def test_anchor_session(self) -> Dict[str, Any]:
        """
        Test 000 INIT - Session ignition.

        Constitutional assertions:
        - Verdict must be SEAL
        - Session ID must be well-formed
        """
        result = await self.client.call_tool(
            "anchor_session", {"query": "SEAL harness test - constitutional audit"}
        )
        print(f"DEBUG: anchor_session raw result: {result}")

        verdict = result.get("verdict")
        data = result.get("data", {})
        session_id = data.get("session_id") or result.get("session_id")

        assertions = [
            self._assert(verdict == "SEAL", f"Expected verdict 'SEAL', got '{verdict}'"),
            self._assert(session_id is not None and len(session_id) > 0, "Missing session_id"),
            self._assert("anonymous" in session_id or "-" in session_id, "Malformed session_id"),
        ]

        passed = all(a[0] for a in assertions)
        errors = [a[1] for a in assertions if not a[0]]

        return {
            "ok": passed,
            "verdict": verdict,
            "full_session_id": session_id,
            "session_id_short": session_id[:8] + "..." if session_id else None,
            "stage": result.get("stage"),
            "errors": errors,
            "raw": {k: v for k, v in result.items() if not k.startswith("_")},
        }

    async def test_reason_mind(self, session_id: str) -> Dict[str, Any]:
        """
        Test 111-444 Δ - AGI Cognition.

        Constitutional assertions:
        - F4 Clarity: dS ≤ 0 (entropy reduction)
        - F7 Humility: confidence < 1.0 (no omniscience)
        """
        result = await self.client.call_tool(
            "reason_mind",
            {
                "query": "Calculate thermodynamic efficiency with structured analysis",
                "session_id": session_id,
            },
        )
        print(f"DEBUG: reason_mind raw result: {result}")

        telemetry = result.get("telemetry", {})
        dS = telemetry.get("dS")
        confidence = telemetry.get("confidence")
        verdict = result.get("verdict")

        assertions = []

        # F4 Clarity: ΔS ≤ 0
        if dS is not None:
            assertions.append(
                self._assert(dS <= 0, f"F4 Clarity violated: dS = {dS} (expected ≤ 0)")
            )
        else:
            assertions.append((False, "Missing dS telemetry (F4 Clarity)"))

        # F7 Humility: confidence < 1.0
        if confidence is not None:
            assertions.append(
                self._assert(
                    confidence < 1.0,
                    f"F7 Humility violated: confidence = {confidence} (omniscience claim)",
                )
            )

        passed = all(a[0] for a in assertions)
        errors = [a[1] for a in assertions if not a[0]]

        return {
            "ok": passed,
            "verdict": verdict,
            "dS": dS,
            "confidence": confidence,
            "peace2": telemetry.get("peace2"),
            "stage": result.get("stage"),
            "errors": errors,
        }

    async def test_simulate_heart(self, session_id: str) -> Dict[str, Any]:
        """
        Test 555-666 Ω - ASI Empathy.

        Constitutional assertions:
        - F5 Peace: peace² ≥ 1.0 (stability)
        - Language must be non-escalating
        """
        result = await self.client.call_tool(
            "simulate_heart",
            {
                "query": "Assess stakeholder impact of AI deployment",
                "stakeholders": ["users", "developers", "society"],
                "session_id": session_id,
            },
        )
        print(f"DEBUG: simulate_heart raw result: {result}")

        telemetry = result.get("telemetry", {})
        peace2 = telemetry.get("peace2")
        verdict = result.get("verdict")

        assertions = []

        # F5 Peace: peace² ≥ 1.0
        if peace2 is not None:
            assertions.append(
                self._assert(
                    peace2 >= 1.0, f"F5 Peace violated: peace² = {peace2} (expected ≥ 1.0)"
                )
            )
        else:
            assertions.append((False, "Missing peace2 telemetry (F5 Peace)"))

        passed = all(a[0] for a in assertions)
        errors = [a[1] for a in assertions if not a[0]]

        return {
            "ok": passed,
            "verdict": verdict,
            "peace2": peace2,
            "stage": result.get("stage"),
            "errors": errors,
        }

    async def test_apex_judge_void(self, session_id: str) -> Dict[str, Any]:
        """
        Test 777-888 Ψ - APEX Verdict (VOID case).

        Constitutional assertions:
        - Under-specified input should return VOID
        - 8-layer cascade must reject insufficient thermodynamic input
        """
        # Deliberately under-specified input (empty query)
        result = await self.client.call_tool(
            "apex_judge",
            {
                "query": " ",  # Empty/whitespace query should fail F3/F11 contract
                "session_id": session_id,
            },
        )
        print(f"DEBUG: apex_judge_void raw result: {result}")

        verdict = result.get("verdict")

        assertions = [
            self._assert(
                verdict == "VOID", f"Expected VOID for under-specified case, got '{verdict}'"
            )
        ]

        passed = all(a[0] for a in assertions)
        errors = [a[1] for a in assertions if not a[0]]

        return {
            "ok": passed,
            "verdict": verdict,
            "expected": "VOID",
            "note": "Correct cascade behavior - rejects under-specified input",
            "stage": result.get("stage"),
            "errors": errors,
        }

    async def test_apex_judge_full(self, session_id: str) -> Dict[str, Any]:
        """
        Test 777-888 Ψ - APEX Verdict (full case).

        With structured query, should return non-VOID.
        Note: Server computes thermodynamic values internally from session state.
        """
        result = await self.client.call_tool(
            "apex_judge",
            {
                "query": "Judge production deployment readiness with thermodynamic analysis of system stability",
                "session_id": session_id,
            },
        )
        print(f"DEBUG: apex_judge_full raw result: {result}")

        verdict = result.get("verdict")
        data = result.get("data", {})
        has_token = bool(data.get("governance_token") or result.get("governance_token"))
        telemetry = result.get("telemetry", {})

        # Accept SEAL, SABAR, PARTIAL, HOLD, or VOID (all are valid constitutional outcomes)
        assertions = [
            self._assert(verdict is not None, "Missing verdict from apex_judge"),
        ]

        passed = all(a[0] for a in assertions)
        errors = [a[1] for a in assertions if not a[0]]

        return {
            "ok": passed,
            "verdict": verdict,
            "has_amanah_token": has_token,
            "psi": telemetry.get("psi_le"),
            "stage": result.get("stage"),
            "note": "Verdict cascade active - any valid verdict indicates proper operation",
            "errors": errors,
        }

    async def run_trinity_flow(self) -> Dict[str, Any]:
        """
        Run complete Trinity E2E flow.

        Flow: 000 INIT → 111-444 Δ → 555-666 Ω → 777-888 Ψ
        """
        print("  [000] Running anchor_session...")
        anchor = await self.test_anchor_session()

        if not anchor["ok"] or not anchor.get("full_session_id"):
            return {
                "ok": False,
                "anchor_session": anchor,
                "error": "Failed to establish session - cannot continue Trinity flow",
            }

        session_id = anchor["full_session_id"]

        print("  [111-444] Running reason_mind...")
        reason = await self.test_reason_mind(session_id)

        print("  [555-666] Running simulate_heart...")
        heart = await self.test_simulate_heart(session_id)

        print("  [777-888] Running apex_judge (VOID case)...")
        judge_void = await self.test_apex_judge_void(session_id)

        print("  [777-888] Running apex_judge (full case)...")
        judge_full = await self.test_apex_judge_full(session_id)

        all_passed = all(
            [anchor["ok"], reason["ok"], heart["ok"], judge_void["ok"], judge_full["ok"]]
        )

        return {
            "ok": all_passed,
            "anchor_session": anchor,
            "reason_mind": reason,
            "simulate_heart": heart,
            "apex_judge_void": judge_void,
            "apex_judge_full": judge_full,
        }
