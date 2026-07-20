"""Runtime layer — tools, prompts, resources, and REST routes."""

from arifosmcp.runtime.compression import (
    CompressionMode,
    MemoryTier,
    auto_compress,
    compress,
    compression_stats,
    decompress,
    estimate_tokens,
)

# ──────────────────────────────────────────────────────────────────────
# Constitutional kernel primitives — wired into the runtime.
# These are loaded at process start so they are available to any
# call site. The functions themselves are pure; the wire is just an
# import. No call site has been changed.
#
# Forged by omega-forge-agent, 2026-06-11.
# Commits: df66ca05a (honesty_hotfix), 4f14b646a (witness_class),
#          a26b7af40 (lease).
# ──────────────────────────────────────────────────────────────────────
# P0-8: Self-probe SELF class. The prober cannot attest itself
# from inside itself. probe_status_self() honors the Gödel lock.
from arifosmcp.runtime.honesty_hotfix import (
    CircuitBreaker,
    min_verdict,
    probe_status_self,
    resolve_kernel_version,
)

# P2-7 / ADR-001: Canonical lease registry. No cross-organ action without
# a kernel-issued lease carrying scope, ttl, and max_uses.
from arifosmcp.runtime.lease_registry import (
    LeaseRecord,
    get_lease,
    issue_lease,
    list_active_leases,
    present_lease,
    revoke_lease,
    validate_lease_for_tool,
)

# P3-2: Positional witness taxonomy. Substance answers "what kind
# of evidence"; position answers "where is the witness standing".
# narrator_debt() counts SELF+INTERNAL receipts; a 3/3_OK report
# is only honest when debt==0.
from arifosmcp.runtime.witness_class import (
    ReceiptContext,
    WitnessPosition,
    classify_witness_position,
    narrator_debt,
    reject_narrative_seal,
    tri_witness_position_state,
)

__all__ = [
    "CompressionMode",
    "MemoryTier",
    "auto_compress",
    "compress",
    "compression_stats",
    "decompress",
    "estimate_tokens",
    # Honest capability hotfix (forged df66ca05a)
    "CircuitBreaker",
    "min_verdict",
    "probe_status_self",
    "resolve_kernel_version",
    # Positional witness taxonomy (forged 4f14b646a)
    "ReceiptContext",
    "WitnessPosition",
    "classify_witness_position",
    "narrator_debt",
    "reject_narrative_seal",
    "tri_witness_position_state",
    # Canonical lease registry (ADR-001)
    "LeaseRecord",
    "issue_lease",
    "revoke_lease",
    "get_lease",
    "list_active_leases",
    "validate_lease_for_tool",
    "present_lease",
]
