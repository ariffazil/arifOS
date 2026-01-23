"""
Governed Quantum Executor - Production-Grade Quantum Governance

Integrates Three Governance Layers:
1. Settlement Policy (timeouts + fallbacks)
2. Orthogonality Guard (Ω_ortho measurement)
3. Immutable Ledger (SHA256 hash chain)

Constitutional Authority:
- v47 Constitutional Law Section 8 (Quantum Governance Mandate)
- 12-Floor Constitutional Compliance
- Tri-Witness Validation (Human·AI·Earth)

This is the PRODUCTION quantum executor.
For development/testing, use OrthogonalExecutor directly.

Authority: Muhammad Arif bin Fazil > Human Sovereignty > Constitutional Law
Implementation: Engineer (Ω) + Quantum Team (3 agents)
"""

from typing import Optional, Dict, Any
from pathlib import Path

from .orthogonal_executor import OrthogonalExecutor, QuantumState
from .settlement_policy import SettlementPolicyHandler
from .orthogonality_guard import OrthogonalityGuard
from .immutable_ledger import ImmutableLedger


class GovernedQuantumExecutor:
    """
    Production quantum executor with full governance enforcement.

    Governance Layers:
    1. **Settlement Policy**: Hard timeouts (AGI: 1.5s, ASI: 1.5s, APEX: 0.5s)
    2. **Orthogonality Guard**: Ω_ortho measurement (threshold: ≥0.95)
    3. **Immutable Ledger**: SHA256 hash chain (tamper-evident history)

    Constitutional Floors Enforced:
    - F1 (Amanah): Immutable ledger + timely verdicts
    - F2 (Truth): Factual measurement history
    - F4 (ΔS Clarity): Orthogonality reduces coupling entropy
    - F5 (Peace): Timeouts prevent system hangs
    - F6 (Empathy): Fast, responsive governance
    - F8 (Tri-Witness): Ledger serves as Earth witness
    - F10 (Ontology): AGI ⊥ ASI orthogonality measured

    Usage:
        executor = GovernedQuantumExecutor()
        state, governance_proof = await executor.execute_governed(query)

        # Check governance
        print(f"Verdict: {state.final_verdict}")
        print(f"Ω_ortho: {governance_proof['omega_ortho']}")
        print(f"Settlement: {governance_proof['settlement_ms']}ms")
        print(f"Ledger hash: {governance_proof['ledger_hash']}")
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        """
        Initialize governed quantum executor.

        Args:
            ledger_path: Optional path to persist immutable ledger
        """
        # Core quantum executor
        self.quantum = OrthogonalExecutor()

        # Governance layers
        self.settlement = SettlementPolicyHandler()
        self.orthogonality = OrthogonalityGuard()
        self.ledger = ImmutableLedger(persist_path=ledger_path)

        # Metrics
        self.total_executions = 0
        self.governance_failures = 0

    async def execute_governed(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[QuantumState, Dict[str, Any]]:
        """
        Execute quantum cycle with full governance enforcement.

        Constitutional Process:
        1. Launch AGI + ASI with settlement monitoring
        2. Monitor orthogonality (Ω_ortho)
        3. Execute APEX measurement
        4. Record to immutable ledger
        5. Return state + governance proof

        Returns:
            tuple: (quantum_state, governance_proof)

        Governance Proof Contains:
            - omega_ortho: Orthogonality index
            - settlement_ms: Time to settle
            - timeout_occurred: bool
            - ledger_hash: SHA256 proof of measurement
            - constitutional_compliance: bool
        """

        self.total_executions += 1

        # Step 1: Execute with orthogonality monitoring
        agi_result, asi_result, ortho_metrics = await self.orthogonality.monitor_orthogonality(
            agi_coro=self.quantum._agi_particle(query, context),
            asi_coro=self.quantum._asi_particle(query, context),
            query=query,
            context=context
        )

        # Step 2: Execute APEX with settlement policy
        apex_settlement = await self.settlement.execute_with_settlement(
            particle_coro=self.quantum._apex_particle(agi_result, asi_result),
            deadline=self.settlement.APEX_DEADLINE,
            particle_name="APEX",
            fallback_verdict="SABAR"
        )

        # Step 3: Build quantum state
        state = QuantumState(
            query=query,
            context=context or {},
            agi_particle=agi_result,
            asi_particle=asi_result,
            apex_particle=apex_settlement.result,
            collapsed=True,
            final_verdict=apex_settlement.result.verdict if apex_settlement.result else "UNKNOWN"
        )

        # Step 4: Calculate total settlement time
        # Orthogonality metrics already tracked AGI + ASI timing
        # Add APEX settlement time
        total_settlement_ms = ortho_metrics.timing_skew_ms + apex_settlement.elapsed_ms

        # Step 5: Record to immutable ledger
        ledger_hash = self.ledger.append(
            query=query,
            verdict=state.final_verdict,
            agi_verdict=agi_result.verdict if agi_result else None,
            asi_verdict=asi_result.verdict if asi_result else None,
            apex_verdict=apex_settlement.result.verdict if apex_settlement.result else None,
            omega_ortho=ortho_metrics.orthogonality_index,
            settlement_ms=total_settlement_ms
        )

        # Step 6: Build governance proof
        governance_proof = {
            # Orthogonality
            "omega_ortho": ortho_metrics.orthogonality_index,
            "orthogonality_compliant": ortho_metrics.is_constitutionally_compliant,
            "coupling_violations": [v.value for v in ortho_metrics.coupling_violations],

            # Settlement
            "settlement_ms": total_settlement_ms,
            "timeout_occurred": apex_settlement.status.value == "TIMEOUT",
            "settlement_status": apex_settlement.status.value,

            # Ledger
            "ledger_hash": ledger_hash,
            "ledger_sequence": len(self.ledger.records) - 1,
            "ledger_epoch": self.ledger.current_epoch,

            # Constitutional compliance
            "constitutional_compliance": (
                ortho_metrics.is_constitutionally_compliant and
                apex_settlement.status.value == "SETTLED" and
                total_settlement_ms < 3000  # <3s mandate
            ),

            # Execution metadata
            "execution_number": self.total_executions,
            "sabar_triggered": self.orthogonality.sabar_triggered
        }

        # Track governance failures
        if not governance_proof["constitutional_compliance"]:
            self.governance_failures += 1

        return state, governance_proof

    def get_governance_report(self) -> Dict[str, Any]:
        """
        Comprehensive governance report for constitutional audit.

        Returns metrics from all three governance layers:
        - Settlement policy metrics
        - Orthogonality measurements
        - Ledger integrity status
        """

        return {
            "total_executions": self.total_executions,
            "governance_failures": self.governance_failures,
            "constitutional_compliance_rate": (
                1.0 - (self.governance_failures / self.total_executions)
                if self.total_executions > 0 else 1.0
            ),

            # Layer 1: Settlement
            "settlement": self.settlement.get_settlement_metrics(),

            # Layer 2: Orthogonality
            "orthogonality": self.orthogonality.get_orthogonality_report(),

            # Layer 3: Ledger
            "ledger": self.ledger.get_ledger_metrics(),

            # SABAR status
            "sabar": {
                "triggered": self.orthogonality.sabar_triggered,
                "consecutive_violations": self.orthogonality.consecutive_violations
            }
        }

    def verify_ledger_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verify immutable ledger integrity.

        Constitutional Audit:
        - Recompute all hashes
        - Verify chain continuity
        - Detect tampering

        Returns:
            tuple: (is_valid, error_message)
        """
        return self.ledger.verify_integrity()

    def export_ledger(self, output_path: Path):
        """Export immutable ledger for external audit."""
        self.ledger.export_ledger(output_path)

    def reset_sabar(self):
        """Reset SABAR trigger after investigation."""
        self.orthogonality.reset_sabar()


# =============================================================================
# CONVENIENCE WRAPPERS (AAA-Level API)
# =============================================================================

async def govern_query_async(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    ledger_path: Optional[Path] = None
) -> tuple[QuantumState, Dict[str, Any]]:
    """
    AAA-level: Execute governed quantum validation (async).

    This is the PRODUCTION function for quantum governance.

    Returns:
        tuple: (quantum_state, governance_proof)

    Example:
        state, proof = await govern_query_async("What is 2+2?")

        if state.final_verdict == "SEAL":
            print("Approved!")
            print(f"Ω_ortho: {proof['omega_ortho']}")
            print(f"Ledger: {proof['ledger_hash']}")
    """
    executor = GovernedQuantumExecutor(ledger_path=ledger_path)
    return await executor.execute_governed(query, context)


def govern_query_sync(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    ledger_path: Optional[Path] = None
) -> tuple[QuantumState, Dict[str, Any]]:
    """
    AAA-level: Execute governed quantum validation (sync).

    Sync wrapper around govern_query_async.

    Returns:
        tuple: (quantum_state, governance_proof)
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            govern_query_async(query, context, ledger_path)
        )
        return result
    finally:
        loop.close()


# =============================================================================
# CONSTITUTIONAL EXPORTS
# =============================================================================

__all__ = [
    "GovernedQuantumExecutor",
    "govern_query_async",
    "govern_query_sync",
]
