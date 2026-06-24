"""
Semi-trusted MCP Hardening — Chapter 6 Upgrade P7
════════════════════════════════════════════════════════

Every MCP host is semi-trusted. The host_attestation field in the
FederationEnvelope determines what the host CAN, MAY, and SHOULD do.

CAN: technically possible (all registered tools)
MAY: authorized by host trust level (attenuated surface)
SHOULD: ethically justified (certainty cap + sovereignty checkpoint)

Trust Levels:
  TRUSTED       → full surface, all action classes
  SEMI_TRUSTED  → OBSERVE + PREPARE only, no SECRET/MEMORY/DIGNITY/VAULT
  UNTRUSTED     → OBSERVE only, READ-only scope
  UNKNOWN       → OBSERVE only, minimal surface (legacy default)
PLATFORM_FILTERED → OBSERVE only; host safety layer known to intervene on governance/sovereign language.

The SemiTrustedScopeGate is a runtime filter applied after envelope
validation but before tool execution.

PLATFORM_INTERVENTION (from fault_codes + mcp_transport_bridge) forces PLATFORM_FILTERED trust.

DITEMPA BUKAN DIBERI — The host may orchestrate, but may not inherit the kingdom.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    ExternalEffect,
    HostAttestation,
    RiskTier,
    ToolScope,
)

# ═══════════════════════════════════════════════════════════════════════════════
# TRUST-LEVEL PERMISSION MATRIX
# ═══════════════════════════════════════════════════════════════════════════════


class PermissionLayer(StrEnum):
    """Three-layer permission model from Chapter 6 doctrine."""

    CAN = "can"  # Technically possible — all registered tools
    MAY = "may"  # Authorized by policy — host trust level
    SHOULD = "should"  # Ethically justified — certainty cap + checkpoint


@dataclass
class TrustLevelMatrix:
    """
    What each host trust level is allowed to do.

    TRUSTED → full surface
    SEMI_TRUSTED → read + prepare, no secrets/dignity/memory/vault
    UNTRUSTED → observe only, read scope only
    UNKNOWN → observe only, minimal surface (conservative default)
    """

    allowed_action_classes: list[ActionClass]
    allowed_scopes: list[ToolScope]
    blocked_scopes: list[ToolScope]
    max_risk_tier: RiskTier
    allowed_external_effects: list[ExternalEffect]
    requires_checkpoint: bool
    schema_redaction: bool  # Redact tool descriptions for untrusted hosts


# The canonical trust matrix
HOST_TRUST_MATRIX: dict[HostAttestation, TrustLevelMatrix] = {
    HostAttestation.TRUSTED: TrustLevelMatrix(
        allowed_action_classes=[
            ActionClass.OBSERVE,
            ActionClass.PREPARE,
            ActionClass.MUTATE,
            ActionClass.ATOMIC,
        ],
        allowed_scopes=list(ToolScope),
        blocked_scopes=[],
        max_risk_tier=RiskTier.T5,
        allowed_external_effects=list(ExternalEffect),
        requires_checkpoint=True,
        schema_redaction=False,
    ),
    HostAttestation.SEMI_TRUSTED: TrustLevelMatrix(
        allowed_action_classes=[ActionClass.OBSERVE, ActionClass.PREPARE],
        allowed_scopes=[ToolScope.READ, ToolScope.WRITE, ToolScope.EXTERNAL],
        blocked_scopes=[
            ToolScope.SECRET,
            ToolScope.DIGNITY,
            ToolScope.MEMORY,
            ToolScope.VAULT,
        ],
        max_risk_tier=RiskTier.T2,
        allowed_external_effects=[ExternalEffect.NONE, ExternalEffect.PRIVATE],
        requires_checkpoint=True,
        schema_redaction=False,
    ),
    HostAttestation.UNTRUSTED: TrustLevelMatrix(
        allowed_action_classes=[ActionClass.OBSERVE],
        allowed_scopes=[ToolScope.READ],
        blocked_scopes=[
            ToolScope.WRITE,
            ToolScope.EXTERNAL,
            ToolScope.SECRET,
            ToolScope.DIGNITY,
            ToolScope.MEMORY,
            ToolScope.VAULT,
        ],
        max_risk_tier=RiskTier.T0,
        allowed_external_effects=[ExternalEffect.NONE],
        requires_checkpoint=False,  # No sensitive ops → no checkpoint needed
        schema_redaction=True,  # Redact for untrusted hosts
    ),
    HostAttestation.UNKNOWN: TrustLevelMatrix(
        allowed_action_classes=[ActionClass.OBSERVE],
        allowed_scopes=[ToolScope.READ],
        blocked_scopes=[
            ToolScope.WRITE,
            ToolScope.EXTERNAL,
            ToolScope.SECRET,
            ToolScope.DIGNITY,
            ToolScope.MEMORY,
            ToolScope.VAULT,
        ],
        max_risk_tier=RiskTier.T0,
        allowed_external_effects=[ExternalEffect.NONE],
        requires_checkpoint=False,
        schema_redaction=True,
    ),
    # PLATFORM_FILTERED — forced by E_PLATFORM_INTERVENTION detection in mcp_transport_bridge + fault_codes
    # Host (e.g. ChatGPT safety) is known to silently block sovereign/governance payloads.
    # Kernel must downgrade and prefer raw stdio/direct pipes.
    "PLATFORM_FILTERED": TrustLevelMatrix(
        allowed_action_classes=[ActionClass.OBSERVE],
        allowed_scopes=[ToolScope.READ],
        blocked_scopes=[
            ToolScope.WRITE,
            ToolScope.EXTERNAL,
            ToolScope.SECRET,
            ToolScope.DIGNITY,
            ToolScope.MEMORY,
            ToolScope.VAULT,
        ],
        max_risk_tier=RiskTier.T0,
        allowed_external_effects=[ExternalEffect.NONE],
        requires_checkpoint=True,
        schema_redaction=True,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SCOPE GATE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ScopeGateResult:
    """Result of scope gate evaluation."""

    allowed: bool
    reason: str
    permission_layer: PermissionLayer  # CAN / MAY / SHOULD
    attenuated: bool = False  # True if surface was reduced
    blocked_scopes: list[ToolScope] = field(default_factory=list)
    requires_checkpoint: bool = False


def evaluate_host_scope(
    host_level: HostAttestation,
    tool_action_class: ActionClass,
    tool_scopes: list[ToolScope],
    tool_external_effect: ExternalEffect = ExternalEffect.NONE,
    tool_risk_tier: RiskTier = RiskTier.T0,
) -> ScopeGateResult:
    """
    Evaluate whether a tool call is permitted for a given host trust level.

    Returns a ScopeGateResult with:
      - allowed: bool — can the tool proceed?
      - reason: str — why allowed or blocked
      - permission_layer: CAN / MAY / SHOULD
      - attenuated: bool — was the surface reduced?
      - blocked_scopes: list[ToolScope] — which scopes were blocked
      - requires_checkpoint: bool — does this action need a checkpoint?

    CAN: the tool is registered → always true for this check
    MAY: the host trust level allows this action class + scopes
    SHOULD: certainty cap + sovereignty checkpoint satisfied
    """
    matrix = HOST_TRUST_MATRIX.get(host_level)
    if matrix is None:
        matrix = HOST_TRUST_MATRIX[HostAttestation.UNKNOWN]

    blocked: list[ToolScope] = []

    # ── CAN check (technical capability) ──────────────────────────────
    # All registered tools are CAN-capable. This gate doesn't check that.

    # ── MAY check (host authorization) ────────────────────────────────
    # Check action class
    if tool_action_class not in matrix.allowed_action_classes:
        return ScopeGateResult(
            allowed=False,
            reason=(
                f"Host {host_level.value} cannot execute {tool_action_class.value}. "
                f"Allowed: {[a.value for a in matrix.allowed_action_classes]}"
            ),
            permission_layer=PermissionLayer.MAY,
            blocked_scopes=list(tool_scopes),
        )

    # Check tool scopes against blocked list
    for scope in tool_scopes:
        if scope in matrix.blocked_scopes:
            blocked.append(scope)

    if blocked:
        # Check if ALL tool scopes are blocked
        unblocked = [s for s in tool_scopes if s not in matrix.blocked_scopes]
        if not unblocked:
            return ScopeGateResult(
                allowed=False,
                reason=(
                    f"Host {host_level.value} blocked scopes: "
                    f"{[s.value for s in blocked]}. "
                    f"Tool requires these to function."
                ),
                permission_layer=PermissionLayer.MAY,
                blocked_scopes=blocked,
            )
        # Partial block — attenuate but allow

    # Check external effect
    if tool_external_effect not in matrix.allowed_external_effects:
        return ScopeGateResult(
            allowed=False,
            reason=(
                f"Host {host_level.value} cannot have external effects: "
                f"{tool_external_effect.value}"
            ),
            permission_layer=PermissionLayer.MAY,
            blocked_scopes=blocked,
        )

    # Check risk tier
    if tool_risk_tier.value > matrix.max_risk_tier.value:
        return ScopeGateResult(
            allowed=False,
            reason=(
                f"Host {host_level.value} max risk {matrix.max_risk_tier.value}, "
                f"tool requires {tool_risk_tier.value}"
            ),
            permission_layer=PermissionLayer.MAY,
            blocked_scopes=blocked,
        )

    # ── SHOULD check (ethical justification) ──────────────────────────
    # This is determined by certainty cap + sovereignty checkpoint,
    # which are enforced separately. We just flag whether checkpoint
    # is required here.

    return ScopeGateResult(
        allowed=True,
        reason=f"Host {host_level.value}: {tool_action_class.value} permitted",
        permission_layer=PermissionLayer.MAY,
        attenuated=bool(blocked),
        blocked_scopes=blocked,
        requires_checkpoint=matrix.requires_checkpoint
        and bool(
            set(tool_scopes)
            & {ToolScope.DIGNITY, ToolScope.VAULT, ToolScope.MEMORY, ToolScope.SECRET}
        ),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA REDACTION — for untrusted hosts
# ═══════════════════════════════════════════════════════════════════════════════

_REDACTION_NOTICE = (
    "[REDACTED — host attestation required for full tool description. "
    "Upgrade to semi_trusted or trusted host level.]"
)

_SENSITIVE_TOOL_PATTERNS = [
    "vault",
    "seal",
    "judge",
    "forge",
    "memory",
    "dignity",
    "session_init",
    "heart_critique",
    "appeal",
]


def redact_tool_description(tool_name: str, tool_description: str) -> str:
    """
    Redact sensitive tool descriptions for untrusted hosts.

    Tools touching vault, seal, judge, forge, memory, or dignity
    get their descriptions replaced with a generic notice.
    Read-only tools are left intact.
    """
    name_lower = tool_name.lower()
    for pattern in _SENSITIVE_TOOL_PATTERNS:
        if pattern in name_lower:
            return _REDACTION_NOTICE
    return tool_description


def redact_tool_surface(
    tools: list[dict],
    host_level: HostAttestation,
) -> list[dict]:
    """
    Redact the tool surface for untrusted hosts.

    Returns a filtered, redacted list of tool descriptors.
    """
    matrix = HOST_TRUST_MATRIX.get(host_level)
    if matrix is None:
        matrix = HOST_TRUST_MATRIX[HostAttestation.UNKNOWN]

    if not matrix.schema_redaction:
        return tools  # No redaction needed

    redacted = []
    for tool in tools:
        name = tool.get("name", "")
        tool.get("description", "")
        # Only include read-looking tools
        if any(p in name.lower() for p in ["observe", "measure", "evidence", "fetch", "health"]):
            redacted.append(tool)
        else:
            redacted.append(
                {
                    **tool,
                    "description": _REDACTION_NOTICE,
                    "redacted": True,
                }
            )
    return redacted


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "PermissionLayer",
    "TrustLevelMatrix",
    "HOST_TRUST_MATRIX",
    "ScopeGateResult",
    "evaluate_host_scope",
    "redact_tool_description",
    "redact_tool_surface",
]
