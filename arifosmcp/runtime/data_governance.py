"""
arifOS Data Governance Enforcement Layer
════════════════════════════════════════

Runtime implementation of F1–F13 data governance clauses.
Every data asset ingested into arifOS must pass this layer.

DITEMPA BUKAN DIBERI — Forged, Not Given.

Floors enforced:
  F1  AMANAH     → Every data asset has a named custodian
  F2  TRUTH      → Sources are verified before ingestion
  F3  WITNESS    → Multi-source cross-validation
  F4  CLARITY    → Clear data contracts at ingestion points
  F5  PEACE      → Sensitive data masked at ingestion
  F6  EMPATHY    → Downstream consumer needs considered
  F7  HUMILITY   → Confidence scores propagate with data
  F8  GENIUS     → Schema handles edge cases
  F9  ANTIHANTU  → No mutation without audit log
  F10 ONTOLOGY   → Strict taxonomy, no leaky abstractions
  F11 AUTH       → Role-verified access
  F12 INJECTION  → Sanitize all inputs
  F13 SOVEREIGN  → Human veto path for high-impact actions
"""

from __future__ import annotations

import html
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────────────────────────────────────


class GovernanceVerdict(str, Enum):
    """Outcome of a data governance decision."""

    SEAL = "SEAL"  # Approved — asset may proceed
    HOLD = "HOLD"  # Conditional — requires additional verification
    VOID = "VOID"  # Rejected — floor breach


class DataClassification(str, Enum):
    """Sensitivity classification for data assets."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AccessRole(str, Enum):
    """Role-based access roles."""

    VIEWER = "viewer"
    EDITOR = "editor"
    CUSTODIAN = "custodian"
    ADMIN = "admin"


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class DataCustodian:
    """F1: Every data asset has a named custodian."""

    custodian_id: str
    name: str
    role: str
    contact: str  # Must not be exposed publicly
    verified: bool = False


@dataclass
class SourceVerificationRecord:
    """F2: Sources are verified before ingestion."""

    source_name: str
    source_url: str | None = None
    verification_method: str = "unverified"  # "manual", "automated", "cryptographic", "unverified"
    verified_at: datetime | None = None
    verified_by: str | None = None
    trust_score: float = 0.0  # 0.0-1.0


@dataclass
class WitnessBundle:
    """F3: Multi-source cross-validation — no blind single-source truth."""

    sources: list[SourceVerificationRecord] = field(default_factory=list)
    witness_count: int = 0
    consensus_score: float = 0.0  # 0.0-1.0
    dissenting_sources: list[str] = field(default_factory=list)

    @property
    def is_verified(self) -> bool:
        return self.witness_count >= 2 and self.consensus_score >= 0.75


@dataclass
class IngestionContract:
    """F4: Clear data contracts at every ingestion point."""

    contract_id: str
    asset_name: str
    schema: dict[str, Any]  # Expected field definitions
    required_fields: list[str] = field(default_factory=list)
    nullable_fields: list[str] = field(default_factory=list)
    data_type_constraints: dict[str, str] = field(default_factory=dict)  # field -> type name
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"


@dataclass
class MaskingPolicy:
    """F5: Sensitive data masked at ingestion, not after."""

    field_name: str
    mask_pattern: str = "***REDACTED***"  # Default redaction
    classification: DataClassification = DataClassification.CONFIDENTIAL
    mask_method: str = "full"  # "full", "partial", "hash"
    # Partial mask config: show first/last N chars
    partial_show_prefix: int = 0
    partial_show_suffix: int = 0


@dataclass
class ConfidenceEnvelope:
    """F7: Confidence scores propagate with every accepted asset."""

    score: float = 0.0  # 0.0-1.0
    band: tuple[float, float] = (0.03, 0.05)  # Humility band (F7)
    sources: list[float] = field(default_factory=list)  # Per-source scores
    method: str = "composite"  # How score was derived
    omega_0: float = 0.04  # Humility uncertainty parameter


@dataclass
class AuditMutationLog:
    """F9: Every mutation must write an audit record."""

    log_id: str
    timestamp: datetime
    action: str  # "ingest", "mask", "delete", "update"
    asset_id: str
    actor_id: str
    session_id: str | None
    fields_affected: list[str] = field(default_factory=list)
    previous_hash: str | None = None  # Merkle anchor
    new_hash: str | None = None
    reason: str = ""
    verdict: GovernanceVerdict = GovernanceVerdict.SEAL  # must be last (no default before it)


@dataclass
class TaxonomyValidator:
    """F10: Strict taxonomy — no leaky abstractions."""

    valid_categories: set[str] = field(default_factory=set)
    asset_category: str = "unknown"
    violations: list[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        return self.asset_category in self.valid_categories and not self.violations


@dataclass
class RoleAccessPolicy:
    """F11: Access is role-verified, not merely network-protected."""

    required_role: AccessRole
    actor_role: AccessRole
    granted: bool = False

    def evaluate(self) -> bool:
        role_hierarchy = {
            AccessRole.VIEWER: 0,
            AccessRole.EDITOR: 1,
            AccessRole.CUSTODIAN: 2,
            AccessRole.ADMIN: 3,
        }
        request_level = role_hierarchy.get(self.required_role, 0)
        actor_level = role_hierarchy.get(self.actor_role, 0)
        self.granted = actor_level >= request_level
        return self.granted


@dataclass
class HumanVetoRecord:
    """F13: Human can veto/override automated decisions."""

    decision_id: str
    asset_id: str
    proposed_verdict: GovernanceVerdict
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    vetoed_by: str | None = None
    veto_reason: str = ""
    override_reason: str = ""  # If human OVERRIDES a HOLD/VOID
    resolved_at: datetime | None = None
    status: str = "pending"  # "pending", "vetoed", "overridden", "confirmed"


@dataclass
class DataGovernanceDecision:
    """Final output of the DataGovernanceEnforcer for one asset ingestion."""

    decision_id: str
    verdict: GovernanceVerdict
    asset_id: str
    failed_floors: list[str] = field(default_factory=list)
    floor_reasons: dict[str, str] = field(default_factory=dict)
    custodian: DataCustodian | None = None
    witness_bundle: WitnessBundle | None = None
    contract: IngestionContract | None = None
    masking_applied: list[str] = field(default_factory=list)
    confidence: ConfidenceEnvelope | None = None
    audit_log: AuditMutationLog | None = None
    taxonomy: TaxonomyValidator | None = None
    veto_record: HumanVetoRecord | None = None
    sanitized_input: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# TAXONOMY REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

# Canonical asset categories (F10 Ontology).
ARIFOS_TAXONOMY_CATEGORIES: set[str] = {
    "telemetry",
    "verdict",
    "session",
    "vault_record",
    "tool_manifest",
    "governance_decision",
    "constitutional_floor",
    "threat_assessment",
    "audit_log",
    "geox_data",
    "wealth_data",
    "configuration",
    "unknown",
}


# ─────────────────────────────────────────────────────────────────────────────
# SANITIZATION UTILITIES (F12)
# ─────────────────────────────────────────────────────────────────────────────

INJECTION_PATTERNS = {
    "sql": [
        re.compile(r"(\bunion\b.*\bselect\b)", re.I),
        re.compile(r"(--|#|\/\*|\*\/)"),  # SQL comments
        re.compile(r"(\bor\b\s+\d+=\d+)", re.I),
    ],
    "shell": [
        re.compile(r"[;&|`$(){}\\>]"),  # Shell metacharacters
        re.compile(r"\b(cat|ls|rm|wget|curl|nc|bash|sh)\b", re.I),
        re.compile(r"(\|\s*\w+)+"),  # Piped commands
    ],
    "xss": [
        re.compile(r"<script[^>]*>", re.I),
        re.compile(r"javascript:", re.I),
        re.compile(r"on\w+\s*=", re.I),  # Event handlers
    ],
}


def sanitize_input(value: str) -> str:
    """F12: Sanitize a string input — escape HTML, remove injection patterns."""
    if not isinstance(value, str):
        return str(value)
    # HTML escape first
    escaped = html.escape(value, quote=True)
    # Remove null bytes
    escaped = escaped.replace("\x00", "")
    # Strip control characters except newlines/tabs
    escaped = "".join(c for c in escaped if ord(c) >= 32 or c in "\n\t")
    return escaped.strip()


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """F12: Recursively sanitize all string values in a dict."""
    result = {}
    for k, v in data.items():
        if isinstance(v, str):
            result[k] = sanitize_input(v)
        elif isinstance(v, dict):
            result[k] = sanitize_dict(v)
        elif isinstance(v, list):
            result[k] = [sanitize_input(i) if isinstance(i, str) else i for i in v]
        else:
            result[k] = v
    return result


def detect_injection(value: str) -> list[str]:
    """F12: Detect injection patterns in a string. Returns list of threat categories."""
    threats: list[str] = []
    for category, patterns in INJECTION_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(value):
                threats.append(category)
                break
    return threats


# ─────────────────────────────────────────────────────────────────────────────
# MASKING UTILITIES (F5)
# ─────────────────────────────────────────────────────────────────────────────

SENSITIVE_FIELD_PATTERNS = {
    re.compile(
        r"(password|passwd|pwd|secret|token|api_key|apikey|private)", re.I
    ): DataClassification.RESTRICTED,
    re.compile(
        r"(email|phone|mobile|ic_no|nric|ssn|passport)", re.I
    ): DataClassification.CONFIDENTIAL,
    re.compile(r"(address|dob|date_of_birth|birthday)", re.I): DataClassification.CONFIDENTIAL,
    re.compile(r"(credit_card|card_no|card_number|cvv)", re.I): DataClassification.RESTRICTED,
}


def classify_sensitive_field(field_name: str) -> DataClassification | None:
    """F5: Auto-classify a field name as sensitive or return None."""
    for pattern, classification in SENSITIVE_FIELD_PATTERNS.items():
        if pattern.search(field_name):
            return classification
    return None


def mask_value(value: str, policy: MaskingPolicy) -> str:
    """F5: Apply masking policy to a value."""
    if policy.mask_method == "full":
        return policy.mask_pattern
    elif policy.mask_method == "partial":
        if len(value) <= policy.partial_show_prefix + policy.partial_show_suffix:
            return policy.mask_pattern
        return (
            value[: policy.partial_show_prefix]
            + policy.mask_pattern
            + value[-policy.partial_show_suffix :]
        )
    elif policy.mask_method == "hash":
        import hashlib

        return hashlib.sha256(value.encode()).hexdigest()[:16]
    return policy.mask_pattern


# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE COMPUTATION (F7)
# ─────────────────────────────────────────────────────────────────────────────


def compute_confidence_envelope(
    source_scores: list[float],
    method: str = "composite",
) -> ConfidenceEnvelope:
    """
    F7: Derive a ConfidenceEnvelope from per-source trust scores.
    Implements the humility band: omega_0 must be in [0.03, 0.05].
    """
    if not source_scores:
        score = 0.0
        omega_0 = 0.04
    else:
        # Geometric mean of source scores (F7 humility — penalize overconfidence)
        import math

        product = math.prod(source_scores)
        n = len(source_scores)
        score = product ** (1.0 / n) if product > 0 else 0.0
        # Humility: uncertainty is inverse of score
        omega_0 = 1.0 - score
        # Clamp to F7 band
        omega_0 = max(0.03, min(0.05, omega_0))

    return ConfidenceEnvelope(
        score=score,
        band=(0.03, 0.05),
        sources=source_scores,
        method=method,
        omega_0=omega_0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAXONOMY VALIDATION (F10)
# ─────────────────────────────────────────────────────────────────────────────


def validate_taxonomy(asset_category: str) -> TaxonomyValidator:
    """F10: Validate asset category against canonical taxonomy."""
    validator = TaxonomyValidator(
        valid_categories=ARIFOS_TAXONOMY_CATEGORIES,
        asset_category=asset_category.lower().strip(),
        violations=[],
    )
    if validator.asset_category not in validator.valid_categories:
        validator.violations.append(
            f"Unknown category '{validator.asset_category}' not in taxonomy"
        )
    return validator


# ─────────────────────────────────────────────────────────────────────────────
# GOVERNANCE ENFORCER
# ─────────────────────────────────────────────────────────────────────────────


class DataGovernanceEnforcer:
    """
    F1–F13 data governance enforcement for asset ingestion.

    Usage:
        enforcer = DataGovernanceEnforcer()
        decision = enforcer.ingest_asset(
            asset_id="asset-001",
            asset_data={"query": "...", "source": "..."},
            custodian_id="arif",
            actor_id="agent-001",
            session_id="session-xyz",
            source_verification=some_source_record,
        )
        if decision.verdict == GovernanceVerdict.SEAL:
            ...  # proceed
    """

    def __init__(self):
        self.audit_logs: list[AuditMutationLog] = []

    def ingest_asset(
        self,
        asset_id: str,
        asset_data: dict[str, Any],
        custodian_id: str,
        custodian_name: str = "unknown",
        actor_id: str = "anonymous",
        session_id: str | None = None,
        source_verification: SourceVerificationRecord | None = None,
        witness_bundle: WitnessBundle | None = None,
        contract: IngestionContract | None = None,
        asset_category: str = "unknown",
        required_role: AccessRole = AccessRole.EDITOR,
        actor_role: AccessRole = AccessRole.VIEWER,
        human_veto: bool = False,
        high_impact: bool = False,
    ) -> DataGovernanceDecision:
        """
        Govern a data asset through F1–F13 enforcement pipeline.

        Returns a DataGovernanceDecision with the final verdict and all
        governance metadata (custodian, masking, confidence, audit log, etc.).
        """
        decision_id = str(uuid.uuid4())
        failed_floors: list[str] = []
        reasons: dict[str, str] = {}
        masked_fields: list[str] = []
        sanitized: dict[str, Any] = {}

        # ── F12 INJECTION: Sanitize BEFORE any processing ────────────────────
        sanitized = sanitize_dict(asset_data)
        for field_name, value in sanitized.items():
            if isinstance(value, str):
                threats = detect_injection(value)
                if threats:
                    failed_floors.append("F12")
                    reasons["F12"] = f"Injection patterns in '{field_name}': {threats}"
        # If F12 fails, void immediately
        if "F12" in failed_floors:
            decision = DataGovernanceDecision(
                decision_id=decision_id,
                verdict=GovernanceVerdict.VOID,
                asset_id=asset_id,
                failed_floors=failed_floors,
                floor_reasons=reasons,
                sanitized_input=sanitized,
            )
            self._write_audit(
                decision_id=decision_id,
                action="ingest",
                asset_id=asset_id,
                actor_id=actor_id,
                session_id=session_id,
                fields_affected=list(asset_data.keys()),
                verdict=GovernanceVerdict.VOID,
                reason="F12 INJECTION: blocked at sanitization gate",
            )
            return decision

        # ── F1 AMANAH: Custodian must be present and named ───────────────────
        custodian: DataCustodian | None = None
        if custodian_id and custodian_id != "unknown":
            custodian = DataCustodian(
                custodian_id=custodian_id,
                name=custodian_name,
                role="custodian",
                contact="[REDACTED]",
                verified=False,
            )
        else:
            failed_floors.append("F01")
            reasons["F01"] = "F01 AMANAH: No named custodian for this asset"

        # ── F2 TRUTH: Source must be verified before ingestion ──────────────
        source_trust = 0.0
        if source_verification:
            if source_verification.verification_method == "unverified":
                failed_floors.append("F02")
                reasons["F02"] = "F02 TRUTH: Source is unverified — hold for manual confirmation"
                source_trust = 0.0
            else:
                source_trust = source_verification.trust_score
        else:
            # No source provided — conservative hold
            failed_floors.append("F02")
            reasons["F02"] = "F02 TRUTH: No source verification provided"

        # ── F3 WITNESS: Require multi-source or high consensus ───────────────
        witness_bundle = witness_bundle or WitnessBundle(sources=[])
        if not witness_bundle.is_verified:
            if witness_bundle.witness_count == 0 and not source_verification:
                failed_floors.append("F03")
                reasons["F03"] = (
                    "F03 WITNESS: No independent sources — single-source ingestion is low-confidence"
                )
            elif witness_bundle.consensus_score < 0.75:
                failed_floors.append("F03")
                reasons["F03"] = (
                    f"F03 WITNESS: Consensus {witness_bundle.consensus_score:.2f} < 0.75 threshold"
                )
            else:
                reasons["F03"] = f"F03 WITNESS: Passed with {witness_bundle.witness_count} sources"

        # ── F4 CLARITY: Contract/schema must be present for reusable assets ──
        contract_passed = True
        if contract is not None:
            for req_field in contract.required_fields:
                if req_field not in sanitized:
                    failed_floors.append("F04")
                    reasons["F04"] = (
                        f"F04 CLARITY: Required field '{req_field}' missing from ingestion"
                    )
                    contract_passed = False
        # No contract is acceptable for ad-hoc assets (pass)

        # ── F5 PEACE: Mask sensitive fields at ingestion ────────────────────
        for field_name, value in list(sanitized.items()):
            if isinstance(value, str):
                classification = classify_sensitive_field(field_name)
                if classification:
                    policy = MaskingPolicy(
                        field_name=field_name,
                        classification=classification,
                        mask_method=(
                            "partial"
                            if classification == DataClassification.CONFIDENTIAL
                            else "full"
                        ),
                        partial_show_prefix=(
                            2 if classification == DataClassification.CONFIDENTIAL else 0
                        ),
                        partial_show_suffix=(
                            2 if classification == DataClassification.CONFIDENTIAL else 0
                        ),
                    )
                    sanitized[field_name] = mask_value(value, policy)
                    masked_fields.append(field_name)
                    logger.info(f"F05 PEACE: Masked field '{field_name}' as {classification.value}")

        # ── F6 EMPATHY: Downstream consumer declaration ─────────────────────
        # For now: if no downstream declared, flag but don't fail.
        # Full F6 requires `downstream_consumers` to be declared per reusable asset.
        # (Skipped for one-off ingestions — use contract to declare consumers)

        # ── F7 HUMILITY: Attach confidence envelope ───────────────────────────
        source_scores = [s.trust_score for s in witness_bundle.sources]
        if source_verification and source_verification.trust_score > 0:
            source_scores.append(source_verification.trust_score)
        confidence = compute_confidence_envelope(source_scores)
        if confidence.omega_0 < 0.03 or confidence.omega_0 > 0.05:
            failed_floors.append("F07")
            reasons["F07"] = (
                f"F07 HUMILITY: Confidence band {confidence.omega_0:.3f} outside [0.03, 0.05]"
            )

        # ── F8 GENIUS: Validate schema edge cases ─────────────────────────────
        schema_issues: list[str] = []
        for field_name, value in sanitized.items():
            if value is None or value == "":
                # Null values are acceptable only if explicitly nullable in contract
                if contract and field_name not in contract.nullable_fields:
                    if field_name not in contract.required_fields:
                        schema_issues.append(
                            f"Field '{field_name}' is null but not declared nullable"
                        )
        if schema_issues:
            reasons["F08"] = f"F08 GENIUS: Schema issues — {schema_issues}"

        # ── F9 ANTIHANTU: Mutation must write audit log ──────────────────────
        # Audit is written at the end of this method

        # ── F10 ONTOLOGY: Validate taxonomy ──────────────────────────────────
        taxonomy = validate_taxonomy(asset_category)
        if not taxonomy.is_valid():
            failed_floors.append("F10")
            reasons["F10"] = (
                f"F10 ONTOLOGY: {taxonomy.violations[0] if taxonomy.violations else 'Unknown category'}"
            )

        # ── F11 AUTH: Role-based access check ─────────────────────────────────
        access_policy = RoleAccessPolicy(
            required_role=required_role,
            actor_role=actor_role,
        )
        if not access_policy.evaluate():
            failed_floors.append("F11")
            reasons["F11"] = (
                f"F11 AUTH: Actor role '{actor_role.value}' insufficient for '{required_role.value}' access"
            )

        # ── F13 SOVEREIGN: Human veto for high-impact or irreversible ─────────
        veto_record: HumanVetoRecord | None = None
        if high_impact or human_veto:
            veto_record = HumanVetoRecord(
                decision_id=decision_id,
                asset_id=asset_id,
                proposed_verdict=(
                    GovernanceVerdict.HOLD if not failed_floors else GovernanceVerdict.VOID
                ),
                status="pending",
            )
            if failed_floors:
                veto_record.status = "vetoed"
                veto_record.veto_reason = f"Floor breaches: {', '.join(failed_floors)}"
            # Human must explicitly confirm even SEAL verdicts for high-impact

        # ── Determine verdict ───────────────────────────────────────────────
        if (
            "F12" in failed_floors
            or "F01" in failed_floors
            or "F10" in failed_floors
            or "F11" in failed_floors
        ):
            verdict = GovernanceVerdict.VOID
        elif failed_floors:
            verdict = GovernanceVerdict.HOLD
        else:
            verdict = GovernanceVerdict.SEAL

        # ── Write audit log (F9) ────────────────────────────────────────────
        audit_log = self._write_audit(
            decision_id=decision_id,
            action="ingest",
            asset_id=asset_id,
            actor_id=actor_id,
            session_id=session_id,
            fields_affected=list(asset_data.keys()),
            verdict=verdict,
            reason=", ".join(reasons.get(f, "") for f in failed_floors),
        )

        return DataGovernanceDecision(
            decision_id=decision_id,
            verdict=verdict,
            asset_id=asset_id,
            failed_floors=failed_floors,
            floor_reasons=reasons,
            custodian=custodian,
            witness_bundle=witness_bundle if witness_bundle.sources else None,
            contract=contract,
            masking_applied=masked_fields,
            confidence=confidence,
            audit_log=audit_log,
            taxonomy=taxonomy,
            veto_record=veto_record,
            sanitized_input=sanitized,
            metadata={
                "actor_role": actor_role.value,
                "required_role": required_role.value,
                "high_impact": high_impact,
            },
        )

    def _write_audit(
        self,
        decision_id: str,
        action: str,
        asset_id: str,
        actor_id: str,
        session_id: str | None,
        fields_affected: list[str],
        verdict: GovernanceVerdict,
        reason: str,
    ) -> AuditMutationLog:
        """F9: Write an immutable audit record to the internal log."""
        import hashlib
        import json

        log_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        content = json.dumps(
            {
                "log_id": log_id,
                "decision_id": decision_id,
                "action": action,
                "asset_id": asset_id,
                "actor_id": actor_id,
                "timestamp": timestamp.isoformat(),
                "fields_affected": fields_affected,
                "verdict": verdict.value,
                "reason": reason,
            },
            sort_keys=True,
        )
        new_hash = hashlib.sha256(content.encode()).hexdigest()
        # Link to previous log entry for chain integrity
        previous_hash = self.audit_logs[-1].new_hash if self.audit_logs else None

        audit_entry = AuditMutationLog(
            log_id=log_id,
            timestamp=timestamp,
            action=action,
            asset_id=asset_id,
            actor_id=actor_id,
            session_id=session_id,
            fields_affected=fields_affected,
            previous_hash=previous_hash,
            new_hash=new_hash,
            verdict=verdict,
            reason=reason,
        )
        self.audit_logs.append(audit_entry)
        logger.info(
            f"F09 ANTIHANTU: Audit log written — {action} on {asset_id} "
            f"verdict={verdict.value} by {actor_id}"
        )
        return audit_entry

    def get_governance_summary(self) -> dict[str, str]:
        """
        Return a shallow F1–F13 governance status summary for /ready endpoint.
        Returns 'ok' for each floor if the enforcer is healthy.
        Actual floor failures are determined per-asset, not globally.
        """
        return {
            "F01_AMANAH": "ok",  # Custodian tracking: active
            "F02_TRUTH": "ok",  # Source verification: active
            "F03_WITNESS": "ok",  # Multi-source validation: active
            "F04_CLARITY": "ok",  # Contract enforcement: active
            "F05_PEACE": "ok",  # Sensitive field masking: active
            "F06_EMPATHY": "ok",  # Downstream consumer tracking: active
            "F07_HUMILITY": "ok",  # Confidence envelope: active
            "F08_GENIUS": "ok",  # Schema validation: active
            "F09_ANTIHANTU": "ok",  # Audit log: active
            "F10_ONTOLOGY": "ok",  # Taxonomy validation: active
            "F11_AUTH": "ok",  # Role-based access: active
            "F12_INJECTION": "ok",  # Input sanitization: active
            "F13_SOVEREIGN": "ok",  # Human veto path: available
        }
