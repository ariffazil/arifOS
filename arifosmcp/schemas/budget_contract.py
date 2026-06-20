"""
Budget Contract Schema — AAA-GOV-BUDGET-v1 (Pydantic v2)
══════════════════════════════════════════════════════

The canonical Pydantic model for the budget contract. This is the
type-safe, serializable schema that can be attached to FederationEnvelopes
and used by the runtime enforcement layer.

Runtime enforcement class: arifosmcp.runtime.budget.BudgetContract
YAML declaration:       contracts/budget_enforcement.py
This schema:           arifosmcp/schemas/budget_contract.py (type-safe model)

DITEMPA BUKAN DIBERI — Every tool call has a price, and the price is governed.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET DOMAINS
# ═══════════════════════════════════════════════════════════════════════════════


class BudgetDomain(StrEnum):
    """Seven-domain budget model — every tool call consumes from these pools."""

    ENTROPY = "entropy"         # Cognitive entropy budget (ΔS)
    TOKEN = "token"            # LLM token budget
    EXECUTION = "execution"    # Tool execution count budget
    RETRY = "retry"            # Failed tool retry budget
    SIDE_EFFECT = "side_effect"  # External side-effect budget
    WALL_CLOCK = "wall_clock"  # Session wall-clock time budget
    BLAST_RADIUS = "blast_radius"  # Blast radius accumulation budget


class ViolationPolicy(StrEnum):
    """What happens when a budget limit is exceeded."""

    HOLD = "888_HOLD"         # HOLD the session — sovereign review required
    WARN = "WARN"             # Log warning but continue
    DEGRADE = "DEGRADE"       # Downgrade action class (ATOMIC→MUTATE, MUTATE→PREPARE)
    VOID = "VOID"             # VOID the action entirely


# ═══════════════════════════════════════════════════════════════════════════════
# PER-DOMAIN BUDGET LIMIT
# ═══════════════════════════════════════════════════════════════════════════════


class DomainLimit(BaseModel):
    """Budget limit for a single domain."""

    domain: BudgetDomain
    limit: float = Field(description="Maximum allowed value")
    current: float = Field(default=0.0, description="Current consumption")
    unit: str = Field(default="count", description="Unit: count, tokens, seconds, joules")
    on_violation: ViolationPolicy = Field(
        default=ViolationPolicy.HOLD,
        description="Policy when limit is exceeded",
    )

    def remaining(self) -> float:
        return max(0.0, self.limit - self.current)

    def is_exhausted(self) -> bool:
        return self.current >= self.limit

    def percent_used(self) -> float:
        if self.limit <= 0:
            return 100.0
        return min(100.0, (self.current / self.limit) * 100.0)


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET CONTRACT SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════


class BudgetContractSchema(BaseModel):
    """
    The canonical budget contract for a session.

    Every FederationEnvelope may carry a budget contract that defines
    how much of each resource the session is allowed to consume.

    Contract ID: AAA-GOV-BUDGET-v1
    Version: 1.1.0 (schema upgrade — 7-domain model)
    """

    # Identity
    contract_id: str = Field(default="AAA-GOV-BUDGET-v1")
    version: str = Field(default="1.1.0")
    session_id: str = Field(description="Session this budget bound to")

    # ── Domain limits ────────────────────────────────────────────────────

    domains: list[DomainLimit] = Field(
        default_factory=lambda: [
            DomainLimit(domain=BudgetDomain.ENTROPY, limit=10.0, unit="joules"),
            DomainLimit(domain=BudgetDomain.TOKEN, limit=200000, unit="tokens"),
            DomainLimit(domain=BudgetDomain.EXECUTION, limit=12, unit="count"),
            DomainLimit(domain=BudgetDomain.RETRY, limit=3, unit="count"),
            DomainLimit(domain=BudgetDomain.SIDE_EFFECT, limit=5, unit="count"),
            DomainLimit(domain=BudgetDomain.WALL_CLOCK, limit=3600, unit="seconds"),
            DomainLimit(
                domain=BudgetDomain.BLAST_RADIUS,
                limit=3,
                unit="count",
                on_violation=ViolationPolicy.VOID,
            ),
        ],
        description="Per-domain budget limits",
    )

    # ── Session tracking ─────────────────────────────────────────────────

    turns: int = Field(default=0, description="Turns consumed this session")
    max_turns: int = Field(default=8, ge=1, description="Maximum turns per session")
    max_no_progress_turns: int = Field(default=2, ge=0, description="Max consecutive no-progress turns")
    max_context_percent: float = Field(default=0.75, ge=0.0, le=1.0, description="Max context window usage")

    # ── State ─────────────────────────────────────────────────────────────

    held: bool = Field(default=False, description="Session in HOLD state")
    hold_reason: str | None = Field(default=None, description="Reason for HOLD")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ── Judgment methods ──────────────────────────────────────────────────

    def is_exhausted(self, domain: BudgetDomain | None = None) -> bool:
        """True if the budget (or a specific domain) is exhausted."""
        if domain:
            d = self.get_domain(domain)
            return d is not None and d.is_exhausted()
        return any(d.is_exhausted() for d in self.domains)

    def get_domain(self, domain: BudgetDomain) -> DomainLimit | None:
        """Get a specific domain limit by name."""
        for d in self.domains:
            if d.domain == domain:
                return d
        return None

    def consume(self, domain: BudgetDomain, amount: float) -> tuple[bool, str]:
        """
        Consume budget from a domain.

        Returns (allowed, reason). If consumption exceeds the limit,
        the HOLD is NOT emitted here — callers must call check_and_hold().
        """
        d = self.get_domain(domain)
        if d is None:
            return False, f"Unknown budget domain: {domain}"

        if self.held:
            return False, f"HOLD: {self.hold_reason or 'session held'}"

        new_total = d.current + amount
        if new_total > d.limit:
            return False, (
                f"Budget exceeded: {domain.value} "
                f"({new_total:.0f}{d.unit} > {d.limit:.0f}{d.unit})"
            )

        d.current = new_total
        self.updated_at = datetime.now(UTC)
        return True, "OK"

    def check_and_hold(self, domain: BudgetDomain, amount: float) -> tuple[bool, str]:
        """
        Check if consumption would exceed budget, and emit HOLD if it does.
        This is the main gate for tool calls.
        """
        d = self.get_domain(domain)
        if d is None:
            return False, f"Unknown budget domain: {domain}"

        if self.held:
            return False, f"HOLD: {self.hold_reason or 'session held'}"

        new_total = d.current + amount
        if new_total > d.limit:
            reason = (
                f"888_HOLD: {domain.value} budget exceeded "
                f"({d.current:.0f} + {amount:.0f} > {d.limit:.0f} {d.unit})"
            )
            self.held = True
            self.hold_reason = reason
            self.updated_at = datetime.now(UTC)
            return False, reason

        # Consume
        d.current = new_total
        self.updated_at = datetime.now(UTC)
        return True, "OK"

    def remaining_percent(self, domain: BudgetDomain) -> float:
        """Remaining budget as a percentage (0-100)."""
        d = self.get_domain(domain)
        if d is None:
            return 0.0
        return 100.0 - d.percent_used()

    def summary(self) -> dict:
        """Return a human-readable budget summary."""
        return {
            "contract_id": self.contract_id,
            "session_id": self.session_id,
            "held": self.held,
            "hold_reason": self.hold_reason,
            "turns": f"{self.turns}/{self.max_turns}",
            "domains": {
                d.domain.value: {
                    "used": d.current,
                    "limit": d.limit,
                    "unit": d.unit,
                    "remaining_pct": round(self.remaining_percent(d.domain), 1),
                }
                for d in self.domains
            },
        }

    @model_validator(mode="after")
    def _validate_contract(self) -> BudgetContractSchema:
        """Contract semantics validation."""
        if self.max_turns < 1:
            raise ValueError("max_turns must be >= 1")
        if self.max_no_progress_turns < 0:
            raise ValueError("max_no_progress_turns must be >= 0")
        if not 0.0 <= self.max_context_percent <= 1.0:
            raise ValueError("max_context_percent must be between 0.0 and 1.0")
        return self
