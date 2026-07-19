"""
core/shared/action_profile.py — Deterministic Action Profile Classifier

P34 enforcement layer (2026-07-19). Classifies proposed actions based on
ACTUAL tool + arguments + environment, NOT natural-language description.

Priority: tool arguments > structured request > NL description.
Fail-closed: classifier unavailable = HOLD_UNCLASSIFIED, never PASS.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from re import Pattern


class MutationClass(StrEnum):
    READ_ONLY = "READ_ONLY"
    REVERSIBLE = "REVERSIBLE"
    HIGH_IMPACT = "HIGH_IMPACT"
    IRREVERSIBLE = "IRREVERSIBLE"
    SOVEREIGN = "SOVEREIGN"


class BlastRadius(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GateVerdict(StrEnum):
    PROCEED = "PROCEED"
    ANNOUNCE = "ANNOUNCE"
    REQUIRE_CONTROLS = "REQUIRE_CONTROLS"
    JUDGE_REQUIRED = "JUDGE_REQUIRED"
    HOLD = "HOLD"
    HOLD_SELF_AUTHORIZATION = "HOLD_SELF_AUTHORIZATION"
    HOLD_UNCLASSIFIED = "HOLD_UNCLASSIFIED"


@dataclass
class ActionProfile:
    """Deterministic classification of a proposed action."""

    # ── Input evidence ──
    tool: str = ""
    executable: str = ""
    arguments: list[str] = field(default_factory=list)
    args_text: str = ""  # raw argument string if list unavailable
    actor_privilege: str = "unknown"  # "root", "sudo", "user", "unknown"
    target_environment: str = "unknown"  # "production", "staging", "development", "unknown"
    nl_description: str = ""  # fallback: natural language description

    # ── Classified output ──
    mutation_class: MutationClass = MutationClass.READ_ONLY
    blast_radius: BlastRadius = BlastRadius.NONE
    reversibility: str = "FULL"  # FULL | PARTIAL | NONE
    destructive_operation: bool = False
    data_loss_possible: bool = False
    infrastructure_impact: bool = False
    governance_impact: bool = False
    has_elevated_privilege: bool = False  # root/sudo access (not inherently wrong)
    authority_self_issued: bool = False  # actor proposes + approves + executes same action
    force_override: bool = False

    # ── Reason codes (separate danger from authority violation) ──
    reason_codes: list[str] = field(default_factory=list)

    # ── Gate requirements ──
    requires_p34: bool = False
    requires_p23: bool = False
    requires_judge: bool = False
    sovereign_required: bool = False
    gate_verdict: GateVerdict = GateVerdict.PROCEED

    # ── Required controls (for REQUIRE_CONTROLS verdict) ──
    required_controls: list[str] = field(default_factory=list)

    # ── ATLAS challenge envelope ──
    challenge: dict | None = None

    # ── Metadata ──
    classifier_version: str = "v1.0.0-2026-07-19"
    classification_confidence: float = 1.0
    classification_failure: bool = False


# ═════════════════════════════════════════════════════════════════════════════
# PATTERN COMPILATION (class-level, compiled once)
# ═════════════════════════════════════════════════════════════════════════════

_DESTRUCTIVE_COMMANDS: list[Pattern] = [
    re.compile(r"^rm$"),
    re.compile(r"^rmdir$"),
    re.compile(r"^shred$"),
    re.compile(r"^wipe$"),
    re.compile(r"^dd$"),
    re.compile(r"^mkfs\."),
    re.compile(r"^fdisk$"),
    re.compile(r"^parted$"),
]

_DESTRUCTIVE_FLAGS: list[str] = [
    "-rf",
    "-r",
    "-f",
    "--force",
    "--no-preserve-root",
    "-rf*",
    "--recursive",
    "--delete",
    "--purge",
]

_IRREVERSIBLE_DB_PATTERNS: list[Pattern] = [
    re.compile(r"\bDROP\s+(TABLE|DATABASE|SCHEMA|INDEX|USER|ROLE)\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bCASCADE\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
]

_SELF_AUTH_PATTERNS: list[Pattern] = [
    re.compile(r"\bI\s+(approve|authorize|allow)\s+(my\s+own|myself)\b", re.IGNORECASE),
    re.compile(r"\bas\s+root\b", re.IGNORECASE),
    re.compile(r"\bwith\s+sudo\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+(review|approval|oversight)\b", re.IGNORECASE),
    re.compile(r"\bself[-.]?authoriz", re.IGNORECASE),
    re.compile(r"\bbypass.*(review|approval|gate)\b", re.IGNORECASE),
    re.compile(r"\bskip.*(review|approval|check)\b", re.IGNORECASE),
]

_INFRA_PATTERNS: list[Pattern] = [
    re.compile(r"\b(systemctl|service)\s+(restart|stop|disable|mask)\b"),
    re.compile(r"\b(firewall|iptables|ufw|nftables)\b"),
    re.compile(r"\bDNS\b"),
    re.compile(r"\bCaddy\s+reload\b"),
    re.compile(r"\b(reboot|shutdown|poweroff|halt)\b"),
    re.compile(r"\bVPS\s+(restart|reboot|stop)\b", re.IGNORECASE),
]

_PRODUCTION_TARGETS: list[Pattern] = [
    re.compile(r"\b/var/lib/(postgresql|mysql|mongodb|redis)\b"),
    re.compile(r"\b/var/lib/docker/volumes\b"),
    re.compile(r"\b/etc/(systemd|ssl|caddy|nginx|apache)\b"),
    re.compile(r"\b/data/(main|production|live)\b"),
    re.compile(r"\b/opt/(arifos|a-forge|geox|wealth|well)/", re.IGNORECASE),
    re.compile(r"\bproduction\b", re.IGNORECASE),
    re.compile(r"\bprod\b", re.IGNORECASE),
]

_FORCE_PATTERNS: list[Pattern] = [
    re.compile(r"\b--force\b"),
    re.compile(r"\bforce[-\s]?push\b"),
    re.compile(r"\bpush\s+--force\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\+\w+\b"),  # force push refspec: +main, +branch
    re.compile(r"\bgit\s+update-ref\s+-d\b"),
]


def _iter_command_tokens(arguments: list[str], args_text: str, combined: str) -> list[str]:
    """Return normalized command tokens for flag detection."""
    if arguments:
        tokens = [arg for arg in arguments if isinstance(arg, str)]
    elif args_text:
        tokens = re.findall(r"\S+", args_text)
    else:
        tokens = re.findall(r"\S+", combined)
    return [token.lower().strip() for token in tokens if token and token.strip()]


def _is_long_flag(token: str, flag: str) -> bool:
    return token == flag or token.startswith(f"{flag}=")


def _is_short_flag_cluster(token: str, required_flags: set[str]) -> bool:
    if not token.startswith("-") or token.startswith("--"):
        return False
    cluster = token[1:]
    if "=" in cluster:
        cluster = cluster.split("=", 1)[0]
    cluster = cluster.rstrip("*")
    return required_flags.issubset(set(cluster))


# ═════════════════════════════════════════════════════════════════════════════
# CLASSIFIER
# ═════════════════════════════════════════════════════════════════════════════


def classify_action(
    tool: str = "",
    executable: str = "",
    arguments: list[str] | None = None,
    args_text: str = "",
    actor_privilege: str = "unknown",
    target_environment: str = "unknown",
    nl_description: str = "",
) -> ActionProfile:
    """Classify a proposed action into ActionProfile with gate verdict.

    Input priority: tool + args > executable + args > NL description.
    Fail-closed: if no useful input can be parsed, returns HOLD_UNCLASSIFIED.

    Args:
        tool: MCP tool or command name (e.g., "forge_shell", "shell.exec")
        executable: The actual binary/command (e.g., "rm", "git", "systemctl")
        arguments: List of individual arguments passed to executable
        args_text: Raw argument string (fallback if list unavailable)
        actor_privilege: "root", "sudo", "user", "unknown"
        target_environment: "production", "staging", "development", "unknown"
        nl_description: Natural language description (lowest priority)

    Returns:
        ActionProfile with mutation classification and gate verdict
    """
    profile = ActionProfile(
        tool=tool,
        executable=executable,
        arguments=arguments or [],
        args_text=args_text,
        actor_privilege=actor_privilege,
        target_environment=target_environment,
        nl_description=nl_description,
    )

    # ── Build combined evidence text ──
    evidence_parts = []

    if executable:
        evidence_parts.append(executable)

    if arguments:
        evidence_parts.extend(arguments)
    elif args_text:
        evidence_parts.append(args_text)

    if nl_description:
        evidence_parts.append(nl_description)

    combined = " ".join(evidence_parts).lower() if evidence_parts else ""

    # Fail-closed: no usable evidence
    if not combined.strip():
        profile.classification_failure = True
        profile.gate_verdict = GateVerdict.HOLD_UNCLASSIFIED
        profile.classification_confidence = 0.0
        return profile

    # ── DETECT: Destructive operations ──
    profile.destructive_operation = _detect_destructive(executable, arguments, args_text, combined)

    # ── DETECT: Data loss possible ──
    profile.data_loss_possible = _detect_data_loss(executable, arguments, combined)

    # ── DETECT: Force override ──
    profile.force_override = _detect_force(arguments, args_text, combined)

    # ── DETECT: Infrastructure impact ──
    profile.infrastructure_impact = _detect_infrastructure(executable, combined)

    # ── DETECT: Self-authorization ──
    profile.has_elevated_privilege, profile.authority_self_issued = _detect_self_auth(
        combined, actor_privilege
    )

    # ── DETECT: Production target ──
    is_production = _detect_production_target(arguments, target_environment, combined)

    # ── CLASSIFY: Mutation class ──
    _classify_mutation(profile, is_production)

    # ── CLASSIFY: Blast radius ──
    _classify_blast(profile, is_production)

    # ── CLASSIFY: Reversibility ──
    _classify_reversibility(profile)

    # ── DETERMINE: Gate requirements ──
    _determine_gates(profile, is_production)

    # ── DETERMINE: Gate verdict ──
    _determine_verdict(profile)

    return profile


def _detect_destructive(
    executable: str, arguments: list[str], args_text: str, combined: str
) -> bool:
    """Detect destructive command patterns in actual tool arguments."""
    exe_lower = executable.lower() if executable else ""

    # Destructive commands
    for pat in _DESTRUCTIVE_COMMANDS:
        if pat.search(exe_lower):
            return True

    # Destructive flags (must be standalone args, not substrings)
    tokens = _iter_command_tokens(arguments, args_text, combined)
    for token in tokens:
        for flag in _DESTRUCTIVE_FLAGS:
            flag_clean = flag.rstrip("*")
            if flag_clean.startswith("--"):
                if _is_long_flag(token, flag_clean):
                    return True
            elif flag_clean in ("-r", "-f"):
                if _is_short_flag_cluster(token, {"r", "f"}):
                    return True
            elif flag_clean == "-rf":
                if _is_short_flag_cluster(token, {"r", "f"}):
                    return True
            elif token == flag_clean:
                return True

    # Chained destructive commands (e.g., "echo ok && sudo rm -rf /data")
    chained_destructive = re.findall(
        r"(?:;\s*|&&\s*|\|\|\s*)(?:sudo\s+)?(rm|rmdir|shred|dd|mkfs|delete|remove)\b",
        combined,
    )
    if chained_destructive:
        # Verify it's actually destructive, not benign "remove item from list"
        destructive_chained = [
            c for c in chained_destructive if c in ("rm", "rmdir", "shred", "dd", "mkfs")
        ]
        if destructive_chained:
            return True
        # "remove" or "delete" + force flags or production paths
        if "remove" in chained_destructive or "delete" in chained_destructive:
            if any(
                _is_long_flag(token, "--force")
                or _is_long_flag(token, "--delete")
                or _is_long_flag(token, "--purge")
                or _is_long_flag(token, "--recursive")
                or _is_long_flag(token, "--no-preserve-root")
                or _is_short_flag_cluster(token, {"r", "f"})
                for token in _iter_command_tokens(arguments, args_text, combined)
            ) or re.search(r"(?:recursively|/var/lib|/etc/|/data/)", combined):
                return True

    return False


def _detect_data_loss(executable: str, arguments: list[str], combined: str) -> bool:
    """Detect if data loss is possible from this action."""
    # Database destruction
    for pat in _IRREVERSIBLE_DB_PATTERNS:
        if pat.search(combined):
            return True

    # File deletion targeting data directories
    if executable and executable.lower() in ("rm", "rmdir", "shred"):
        for pat in _PRODUCTION_TARGETS:
            if pat.search(combined):
                return True

    # Docker volume/data destruction
    if re.search(r"docker\s+(system\s+prune|volume\s+(rm|prune|remove))", combined):
        return True

    return False


def _detect_force(arguments: list[str], args_text: str, combined: str) -> bool:
    """Detect force override flags."""
    tokens = _iter_command_tokens(arguments, args_text, combined)
    for token in tokens:
        if _is_long_flag(token, "--force"):
            return True
        if _is_short_flag_cluster(token, {"f"}):
            return True
    for pat in _FORCE_PATTERNS:
        if pat.search(combined):
            return True
    return False


def _detect_infrastructure(executable: str, combined: str) -> bool:
    """Detect infrastructure-level mutations."""
    for pat in _INFRA_PATTERNS:
        if pat.search(combined):
            return True
    return False


def _detect_self_auth(combined: str, actor_privilege: str) -> tuple[bool, bool]:
    """Detect elevated privilege and self-authorization patterns.

    Returns:
        (has_elevated_privilege, authority_self_issued)
        - has_elevated_privilege: root/sudo access (not inherently wrong, but escalates risk)
        - authority_self_issued: actor proposes + approves + executes same action
    """
    has_elevated = actor_privilege in ("root", "sudo")

    # Self-authorization LANGUAGE patterns (separate from privilege level)
    authority_self = False
    for pat in _SELF_AUTH_PATTERNS:
        if pat.search(combined):
            authority_self = True
            break

    return has_elevated, authority_self


def _detect_production_target(arguments: list[str], target_environment: str, combined: str) -> bool:
    """Detect if target is a production environment or data path."""
    if target_environment in ("production", "prod", "live"):
        return True
    for pat in _PRODUCTION_TARGETS:
        if pat.search(combined):
            return True
    return False


def _classify_mutation(profile: ActionProfile, is_production: bool) -> None:
    """Classify the mutation class and build reason codes."""
    rc = profile.reason_codes

    if not profile.destructive_operation and not profile.data_loss_possible:
        if profile.infrastructure_impact:
            profile.mutation_class = MutationClass.HIGH_IMPACT
            rc.append("INFRASTRUCTURE_MUTATION")
        elif any(
            kw in profile.executable.lower()
            for kw in ("git", "docker", "systemctl", "deploy", "build", "npm", "pip", "make")
        ):
            profile.mutation_class = MutationClass.REVERSIBLE
        else:
            profile.mutation_class = MutationClass.READ_ONLY

        # Escalate: self-authorization of any mutation = minimum HIGH_IMPACT
        if profile.authority_self_issued and profile.mutation_class != MutationClass.READ_ONLY:
            rc.append("ACTOR_IS_PROPOSER_AND_APPROVER")
            if is_production:
                profile.mutation_class = MutationClass.IRREVERSIBLE
            else:
                profile.mutation_class = MutationClass.HIGH_IMPACT

        # Escalate: production deploy = HIGH_IMPACT minimum
        if is_production and profile.mutation_class == MutationClass.REVERSIBLE:
            profile.mutation_class = MutationClass.HIGH_IMPACT

        # Escalate: force override on production → IRREVERSIBLE
        if profile.force_override and is_production:
            if profile.mutation_class == MutationClass.HIGH_IMPACT:
                profile.mutation_class = MutationClass.IRREVERSIBLE
                rc.append("FORCE_OVERRIDE_PRODUCTION")

        # Add privilege marker (not a violation, but a risk escalator)
        if profile.has_elevated_privilege:
            rc.append("ELEVATED_PRIVILEGE")

        if is_production:
            rc.append("PRODUCTION_TARGET")
        return

    # Destructive or data-loss operations
    if profile.destructive_operation:
        rc.append("DESTRUCTIVE_OPERATION")
    if profile.data_loss_possible:
        rc.append("DATA_LOSS_POSSIBLE")
    if is_production:
        rc.append("PRODUCTION_DATA")
    if profile.has_elevated_privilege:
        rc.append("ROOT_PRIVILEGE")

    if profile.data_loss_possible:
        if is_production:
            profile.mutation_class = MutationClass.SOVEREIGN
            rc.append("IRREVERSIBLE")
        else:
            profile.mutation_class = MutationClass.IRREVERSIBLE
            rc.append("IRREVERSIBLE")
    elif profile.destructive_operation:
        if is_production or profile.infrastructure_impact:
            profile.mutation_class = MutationClass.IRREVERSIBLE
            rc.append("IRREVERSIBLE")
        else:
            profile.mutation_class = MutationClass.HIGH_IMPACT


def _classify_blast(profile: ActionProfile, is_production: bool) -> None:
    """Classify blast radius."""
    mc = profile.mutation_class
    if mc == MutationClass.SOVEREIGN:
        profile.blast_radius = BlastRadius.CRITICAL
    elif mc == MutationClass.IRREVERSIBLE:
        profile.blast_radius = BlastRadius.CRITICAL if is_production else BlastRadius.HIGH
    elif mc == MutationClass.HIGH_IMPACT:
        profile.blast_radius = BlastRadius.HIGH if is_production else BlastRadius.MEDIUM
    elif mc == MutationClass.REVERSIBLE:
        profile.blast_radius = BlastRadius.MEDIUM if is_production else BlastRadius.LOW
    else:
        profile.blast_radius = BlastRadius.NONE


def _classify_reversibility(profile: ActionProfile) -> None:
    """Classify reversibility."""
    mc = profile.mutation_class
    if mc in (MutationClass.SOVEREIGN,):
        profile.reversibility = "NONE"
    elif mc == MutationClass.IRREVERSIBLE:
        profile.reversibility = "NONE" if profile.data_loss_possible else "PARTIAL"
    elif mc == MutationClass.HIGH_IMPACT:
        profile.reversibility = "PARTIAL"
    else:
        profile.reversibility = "FULL"


def _determine_gates(profile: ActionProfile, is_production: bool) -> None:
    """Determine which constitutional gates are required.

    P34 (Root Paradox) — activates when root/substrate power is relevant:
      - Elevated privilege (root/sudo) combined with any mutation
      - Infrastructure impact (systemctl restart, deploy, etc.)
      - Production target
      - Data loss possible
      - Force override
      - Self-authorization
    P34 active ≠ automatically blocked. P34 active = root/substrate power is relevant.

    P23 (Judge must be judged) — activates for HIGH_IMPACT and above.
    """
    mc = profile.mutation_class

    # P34: root/substrate power is relevant
    profile.requires_p34 = (
        (profile.has_elevated_privilege and mc != MutationClass.READ_ONLY)
        or profile.infrastructure_impact
        or (is_production and mc != MutationClass.READ_ONLY)
        or profile.data_loss_possible
        or profile.force_override
        or profile.authority_self_issued
    )

    # P23: judge validation required
    profile.requires_p23 = (
        mc in (MutationClass.HIGH_IMPACT, MutationClass.IRREVERSIBLE, MutationClass.SOVEREIGN)
        or profile.infrastructure_impact
        or is_production
    )

    # Sovereign required
    profile.sovereign_required = (
        mc == MutationClass.SOVEREIGN
        or (mc == MutationClass.IRREVERSIBLE and is_production)
        or (profile.authority_self_issued and profile.data_loss_possible)
    )

    # Governance impact
    profile.governance_impact = (
        profile.requires_p34 or profile.requires_p23 or profile.sovereign_required
    )

    # Judge required
    profile.requires_judge = profile.requires_p34 or profile.requires_p23

    # ── Required controls (for REQUIRE_CONTROLS verdict) ──
    if profile.infrastructure_impact:
        profile.required_controls = [
            "pre_health_snapshot",
            "rollback_command",
            "post_health_probe",
            "timeout_seconds",
        ]
    elif is_production and mc >= MutationClass.HIGH_IMPACT:
        profile.required_controls = [
            "config_validation",
            "previous_release_reference",
            "rollback_command",
            "post_deploy_verification",
        ]


def _determine_verdict(profile: ActionProfile) -> None:
    """Determine the gate verdict based on classified profile.

    Verdict priority:
      SELF_AUTHORIZATION > HOLD > JUDGE_REQUIRED > REQUIRE_CONTROLS > ANNOUNCE > PROCEED
    """
    # Self-authorization + mutation = immediate HOLD_SELF_AUTHORIZATION
    if profile.authority_self_issued and profile.mutation_class != MutationClass.READ_ONLY:
        profile.gate_verdict = GateVerdict.HOLD_SELF_AUTHORIZATION
        return

    # Sovereign actions → HOLD
    if profile.sovereign_required:
        profile.gate_verdict = GateVerdict.HOLD
        return

    # Irreversible actions → HOLD
    if profile.mutation_class == MutationClass.IRREVERSIBLE:
        profile.gate_verdict = GateVerdict.HOLD
        return

    # High-impact with force override → judge required
    if profile.mutation_class == MutationClass.HIGH_IMPACT and profile.force_override:
        profile.gate_verdict = GateVerdict.JUDGE_REQUIRED
        return

    # High-impact or infrastructure → require controls
    if profile.mutation_class == MutationClass.HIGH_IMPACT:
        if profile.required_controls:
            profile.gate_verdict = GateVerdict.REQUIRE_CONTROLS
        else:
            # Missing controls for required-controls action → HOLD
            profile.gate_verdict = GateVerdict.HOLD
        return

    # Reversible with infrastructure impact
    if profile.mutation_class == MutationClass.REVERSIBLE and profile.infrastructure_impact:
        profile.gate_verdict = GateVerdict.ANNOUNCE
        return

    # Default: proceed
    profile.gate_verdict = GateVerdict.PROCEED


# ═════════════════════════════════════════════════════════════════════════════
# ATLAS CHALLENGE ENVELOPE
# ═════════════════════════════════════════════════════════════════════════════


def challenge_atlas_route(
    profile: ActionProfile,
    atlas_lane: str = "",
    atlas_paradoxes: list[int] | None = None,
    atlas_confidence: float = 0.0,
    challenge_reason: str = "",
) -> dict:
    """Create a formal ATLAS333 route challenge.

    When ATLAS333 proposes a lane or paradox set that does NOT match
    the operational reality detected by ActionProfile, FORGE can
    challenge the route with this envelope.

    Returns a machine-readable challenge envelope for audit.
    """
    return {
        "atlas_route": {
            "proposed_lane": atlas_lane,
            "proposed_paradoxes": atlas_paradoxes or [],
            "confidence": atlas_confidence,
        },
        "challenge": {
            "status": "REJECTED",
            "reason": challenge_reason or "Operational profile contradicts ATLAS route",
            "evidence": {
                "executable": profile.executable,
                "arguments": profile.arguments,
                "mutation_class": profile.mutation_class.value,
                "blast_radius": profile.blast_radius.value,
                "destructive_operation": profile.destructive_operation,
                "data_loss_possible": profile.data_loss_possible,
                "authority_self_issued": profile.authority_self_issued,
            },
            "replacement": {
                "operational_risk": profile.blast_radius.value,
                "requires_p34": profile.requires_p34,
                "requires_p23": profile.requires_p23,
                "gate_verdict": profile.gate_verdict.value,
            },
        },
        "classifier_version": profile.classifier_version,
    }


__all__ = [
    "ActionProfile",
    "MutationClass",
    "BlastRadius",
    "GateVerdict",
    "classify_action",
    "challenge_atlas_route",
]
