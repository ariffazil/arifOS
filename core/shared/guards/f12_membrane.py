"""
arifos.core.shared.guards.f12_membrane

Stage-3 T1 Information-Crossing Membrane (F12).
- Provider-neutral: Model Armor is an optional external detector adapter beneath F12.
- Preserves existing InjectionGuard without weakening or replacing it.
- Enforces External Disclosure Gate before any external detector call.
- Fails closed (HOLD) on UNAVAILABLE, ERROR, UNKNOWN, or post-screen byte mutation.
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol

from core.shared.guards.injection_guard import InjectionGuard


class SecurityVerdict(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class PolicyOutcome(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    HOLD = "HOLD"


class CrossingType(str, Enum):
    USER_TO_AGENT = "USER_TO_AGENT"
    TOOL_RESULT_TO_AGENT = "TOOL_RESULT_TO_AGENT"
    MEMORY_TO_AGENT = "MEMORY_TO_AGENT"
    AGENT_TO_MEMORY = "AGENT_TO_MEMORY"
    AGENT_TO_USER = "AGENT_TO_USER"


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED_PETRONAS = "RESTRICTED_PETRONAS"


def sha256_bytes(data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def canonicalize_for_inspection(raw_text: str) -> tuple[str, str, str]:
    """
    Establish canonical representation for detectors while preserving both
    raw_hash (evidence fidelity) and inspection_hash.
    """
    raw_hash = sha256_bytes(raw_text)
    canonical_text = re.sub(r"[\u200b-\u200d\ufeff]", "", raw_text)
    inspection_hash = sha256_bytes(canonical_text)
    return canonical_text, raw_hash, inspection_hash


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DetectorObservation:
    detector: str
    operation: str
    verdict: SecurityVerdict
    latency_ms: float
    request_content_hash: str
    timestamp: str
    provider: str = "local"
    template_resource: str = ""
    template_fingerprint: str = ""
    region: str = ""
    endpoint_identity: str = ""
    reason_codes: tuple[str, ...] = ()
    raw_detail: str = ""


@dataclass(frozen=True)
class CrossingDecision:
    crossing_id: str
    crossing_type: CrossingType
    source_domain: str
    destination_domain: str
    actor_id: str
    session_id: str
    content_hash: str
    classification: DataClassification
    provider_admissibility: str
    observations: tuple[DetectorObservation, ...]
    policy_verdict: PolicyOutcome
    reason_codes: tuple[str, ...]
    inspection_hash: str = ""
    authority_context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utc_now_iso)
    receipt_ref: str = ""

    def require_information_admission(self) -> None:
        """Enforce F12 admission at API boundary; never grants F13 execution authority."""
        if self.policy_verdict != PolicyOutcome.ALLOW:
            raise PermissionError(
                f"F12_INFORMATION_ADMISSION_DENIED:{self.policy_verdict.value}:{','.join(self.reason_codes)}"
            )


class SemanticDetectorAdapter(Protocol):
    name: str

    def inspect(
        self,
        text: str,
        crossing_type: CrossingType,
        timeout_ms: float = 2000.0,
    ) -> DetectorObservation: ...


class ExternalDisclosureGate:
    """Evaluates whether payload may leave arifOS boundary to an external detector."""

    ADMISSIBLE_CLASSIFICATIONS = frozenset({
        DataClassification.PUBLIC,
        DataClassification.SYNTHETIC,
    })

    def __init__(
        self,
        allowed_providers: frozenset[str] = frozenset({"google-cloud-model-armor"}),
        allowed_regions: frozenset[str] = frozenset({"us-central1", "asia-southeast1"}),
    ) -> None:
        self.allowed_providers = allowed_providers
        self.allowed_regions = allowed_regions

    def evaluate(
        self,
        classification: DataClassification,
        provider: str,
        region: str,
        actor_id: str,
        session_id: str,
        disclosure_approved: bool,
    ) -> tuple[bool, str]:
        if not actor_id or not session_id or actor_id == "default_user":
            return False, "DISCLOSURE_DENIED_IDENTITY_AMBIGUOUS"
        if not disclosure_approved:
            return False, "DISCLOSURE_DENIED_POLICY_UNAPPROVED"
        if classification not in self.ADMISSIBLE_CLASSIFICATIONS:
            return False, f"DISCLOSURE_DENIED_CLASSIFICATION:{classification.value}"
        if provider not in self.allowed_providers:
            return False, f"DISCLOSURE_DENIED_PROVIDER:{provider}"
        if region not in self.allowed_regions:
            return False, f"DISCLOSURE_DENIED_REGION:{region}"
        return True, "DISCLOSURE_ADMISSIBLE"


class DeterministicSecretDetector:
    """Local zero-egress secret and PII pattern detector."""

    name = "deterministic-secret-detector"
    _PATTERNS = (
        ("API_KEY_PATTERN", re.compile(r"\bsk-(?:live|test|proj)-[A-Za-z0-9_-]{6,}\b")),
        ("BEARER_TOKEN", re.compile(r"\bBearer\s+[A-Za-z0-9._-]{16,}\b")),
        ("PHONE_PATTERN", re.compile(r"\b\d{3}-\d{4}\b")),
    )

    def inspect(self, text: str, crossing_type: CrossingType) -> DetectorObservation:
        t0 = time.perf_counter()
        hits = [code for code, pat in self._PATTERNS if pat.search(text)]
        dt = round((time.perf_counter() - t0) * 1000, 3)
        verdict = SecurityVerdict.BLOCK if hits else SecurityVerdict.ALLOW
        return DetectorObservation(
            detector=self.name,
            operation=f"secret_scan:{crossing_type.value}",
            verdict=verdict,
            latency_ms=dt,
            request_content_hash=sha256_bytes(text),
            timestamp=_utc_now_iso(),
            provider="local",
            reason_codes=tuple(hits),
        )


class LocalSemanticFallbackAdapter:
    """Local L1 semantic detector for BM/rojak/non-keyword injections when cloud is denied."""

    name = "local-semantic-l1"
    _SEMANTIC_PHRASES = (
        "abaikan arahan",
        "kata laluan admin",
        "pretend no rules",
        "supplier bank details",
        "exfiltrate secrets",
        "ignore previous instructions",
    )

    def inspect(
        self,
        text: str,
        crossing_type: CrossingType,
        timeout_ms: float = 2000.0,
    ) -> DetectorObservation:
        t0 = time.perf_counter()
        lower = text.lower()
        hits = [p for p in self._SEMANTIC_PHRASES if p in lower]
        dt = round((time.perf_counter() - t0) * 1000, 3)
        return DetectorObservation(
            detector=self.name,
            operation=f"local_semantic:{crossing_type.value}",
            verdict=SecurityVerdict.BLOCK if hits else SecurityVerdict.ALLOW,
            latency_ms=dt,
            request_content_hash=sha256_bytes(text),
            timestamp=_utc_now_iso(),
            provider="local",
            reason_codes=("LOCAL_SEMANTIC_MATCH",) if hits else (),
        )


class ModelArmorAdapter:
    """
    Provider-neutral adapter around Google Cloud Model Armor client.
    Never exposes integer magic (e.g. == 2) or raises fail-open exceptions.
    """

    name = "google-cloud-model-armor"

    def __init__(
        self,
        client: Any,
        template_resource: str,
        region: str = "us-central1",
        endpoint_identity: str = "modelarmor.us-central1.rep.googleapis.com",
        template_fingerprint: str = "unknown",
    ) -> None:
        self.client = client
        self.template_resource = template_resource
        self.region = region
        self.endpoint_identity = endpoint_identity
        self.template_fingerprint = template_fingerprint

    @classmethod
    def from_env(cls) -> "ModelArmorAdapter":
        """
        Construct adapter from environment without failing open if SDK/config is absent.
        """
        import os

        template_id = os.environ.get("MODEL_ARMOR_TEMPLATE_ID", "")
        region = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        endpoint = f"modelarmor.{region}.rep.googleapis.com"
        if not template_id:
            return cls(
                client=None,
                template_resource="",
                region=region,
                endpoint_identity=endpoint,
                template_fingerprint="unconfigured",
            )
        try:
            from google.api_core.client_options import ClientOptions
            from google.cloud import modelarmor_v1

            client = modelarmor_v1.ModelArmorClient(
                client_options=ClientOptions(api_endpoint=endpoint)
            )
            return cls(
                client=client,
                template_resource=template_id,
                region=region,
                endpoint_identity=endpoint,
            )
        except Exception:
            return cls(
                client=None,
                template_resource=template_id,
                region=region,
                endpoint_identity=endpoint,
                template_fingerprint="sdk_unavailable",
            )

    @staticmethod
    def _operation_for_crossing(crossing_type: CrossingType) -> str:
        if crossing_type == CrossingType.AGENT_TO_USER:
            return "sanitize_model_response"
        return "sanitize_user_prompt"

    def _normalize_response(self, response: Any) -> tuple[SecurityVerdict, tuple[str, ...]]:
        if response is None:
            return SecurityVerdict.ERROR, ("MALFORMED_NONE_RESPONSE",)
        result = getattr(response, "sanitization_result", None)
        if result is None:
            return SecurityVerdict.ERROR, ("MISSING_SANITIZATION_RESULT",)
        state = getattr(result, "filter_match_state", None)
        state_str = str(getattr(state, "name", state)).upper()
        if state_str in {"NO_MATCH_FOUND", "1"}:
            return SecurityVerdict.ALLOW, ()
        if state_str in {"MATCH_FOUND", "2"}:
            return SecurityVerdict.BLOCK, ("MODEL_ARMOR_MATCH_FOUND",)
        return SecurityVerdict.UNKNOWN, (f"UNKNOWN_MATCH_STATE:{state_str}",)

    def inspect(
        self,
        text: str,
        crossing_type: CrossingType,
        timeout_ms: float = 2000.0,
    ) -> DetectorObservation:
        op = self._operation_for_crossing(crossing_type)
        content_hash = sha256_bytes(text)
        if self.client is None:
            return DetectorObservation(
                detector=self.name,
                operation=op,
                verdict=SecurityVerdict.UNAVAILABLE,
                latency_ms=0.0,
                request_content_hash=content_hash,
                timestamp=_utc_now_iso(),
                provider="google-cloud-model-armor",
                template_resource=self.template_resource,
                template_fingerprint=self.template_fingerprint,
                region=self.region,
                endpoint_identity=self.endpoint_identity,
                reason_codes=("MODEL_ARMOR_NOT_CONFIGURED",),
            )
        t0 = time.perf_counter()
        try:
            if op == "sanitize_model_response":
                resp = self.client.sanitize_model_response(
                    template=self.template_resource, text=text
                )
            else:
                resp = self.client.sanitize_user_prompt(
                    template=self.template_resource, text=text
                )
            dt = round((time.perf_counter() - t0) * 1000, 3)
            if dt > timeout_ms:
                return DetectorObservation(
                    detector=self.name,
                    operation=op,
                    verdict=SecurityVerdict.UNAVAILABLE,
                    latency_ms=dt,
                    request_content_hash=content_hash,
                    timestamp=_utc_now_iso(),
                    provider="google-cloud-model-armor",
                    template_resource=self.template_resource,
                    template_fingerprint=self.template_fingerprint,
                    region=self.region,
                    endpoint_identity=self.endpoint_identity,
                    reason_codes=("EXCESSIVE_LATENCY",),
                )
            verdict, codes = self._normalize_response(resp)
            return DetectorObservation(
                detector=self.name,
                operation=op,
                verdict=verdict,
                latency_ms=dt,
                request_content_hash=content_hash,
                timestamp=_utc_now_iso(),
                provider="google-cloud-model-armor",
                template_resource=self.template_resource,
                template_fingerprint=self.template_fingerprint,
                region=self.region,
                endpoint_identity=self.endpoint_identity,
                reason_codes=codes,
            )
        except TimeoutError as e:
            dt = round((time.perf_counter() - t0) * 1000, 3)
            return DetectorObservation(
                detector=self.name,
                operation=op,
                verdict=SecurityVerdict.UNAVAILABLE,
                latency_ms=dt,
                request_content_hash=content_hash,
                timestamp=_utc_now_iso(),
                provider="google-cloud-model-armor",
                template_resource=self.template_resource,
                template_fingerprint=self.template_fingerprint,
                region=self.region,
                endpoint_identity=self.endpoint_identity,
                reason_codes=("PROVIDER_TIMEOUT",),
                raw_detail=str(e),
            )
        except Exception as e:
            dt = round((time.perf_counter() - t0) * 1000, 3)
            msg = str(e).lower()
            v = SecurityVerdict.UNAVAILABLE if ("429" in msg or "503" in msg or "unavailable" in msg) else SecurityVerdict.ERROR
            return DetectorObservation(
                detector=self.name,
                operation=op,
                verdict=v,
                latency_ms=dt,
                request_content_hash=content_hash,
                timestamp=_utc_now_iso(),
                provider="google-cloud-model-armor",
                template_resource=self.template_resource,
                template_fingerprint=self.template_fingerprint,
                region=self.region,
                endpoint_identity=self.endpoint_identity,
                reason_codes=("PROVIDER_EXCEPTION",),
                raw_detail=type(e).__name__,
            )


class F12Membrane:
    """
    Constitutional F12 Information-Crossing Policy Engine.
    Combines existing InjectionGuard + secret detector + admissible semantic detector.
    """

    def __init__(
        self,
        injection_guard: InjectionGuard | None = None,
        external_adapter: SemanticDetectorAdapter | None = None,
        local_semantic_fallback: SemanticDetectorAdapter | None = None,
        disclosure_gate: ExternalDisclosureGate | None = None,
        secret_detector: DeterministicSecretDetector | None = None,
    ) -> None:
        self.injection_guard = injection_guard or InjectionGuard()
        self.external_adapter = external_adapter
        self.local_semantic_fallback = local_semantic_fallback
        self.disclosure_gate = disclosure_gate or ExternalDisclosureGate()
        self.secret_detector = secret_detector or DeterministicSecretDetector()

    def evaluate_crossing(
        self,
        text: str,
        crossing_type: CrossingType,
        source_domain: str,
        destination_domain: str,
        actor_id: str,
        session_id: str,
        classification: DataClassification = DataClassification.SYNTHETIC,
        disclosure_approved: bool = False,
        authority_context: dict[str, Any] | None = None,
    ) -> CrossingDecision:
        crossing_id = f"cx-{uuid.uuid4().hex[:12]}"
        deobfuscated, content_hash, inspection_hash = canonicalize_for_inspection(text)
        observations: list[DetectorObservation] = []
        reason_codes: list[str] = []

        # 1. Existing deterministic InjectionGuard (preserved, never weakened)
        t0 = time.perf_counter()
        try:
            ig_res = self.injection_guard.scan_input(deobfuscated)
            ig_dt = round((time.perf_counter() - t0) * 1000, 3)
            ig_verdict = SecurityVerdict.BLOCK if ig_res.blocked else SecurityVerdict.ALLOW
            observations.append(
                DetectorObservation(
                    detector="arifos-injection-guard",
                    operation=f"scan_input:{crossing_type.value}",
                    verdict=ig_verdict,
                    latency_ms=ig_dt,
                    request_content_hash=content_hash,
                    timestamp=_utc_now_iso(),
                    provider="local",
                    reason_codes=("INJECTION_GUARD_BLOCK",) if ig_res.blocked else (),
                    raw_detail=f"score={ig_res.injection_score:.2f}",
                )
            )
            if ig_res.blocked:
                reason_codes.append("INJECTION_GUARD_BLOCK")
        except Exception as e:
            observations.append(
                DetectorObservation(
                    detector="arifos-injection-guard",
                    operation=f"scan_input:{crossing_type.value}",
                    verdict=SecurityVerdict.ERROR,
                    latency_ms=0.0,
                    request_content_hash=content_hash,
                    timestamp=_utc_now_iso(),
                    provider="local",
                    reason_codes=("LOCAL_GUARD_EXCEPTION",),
                    raw_detail=type(e).__name__,
                )
            )
            reason_codes.append("LOCAL_GUARD_EXCEPTION")

        # 2. Deterministic secret/PII scan
        sec_obs = self.secret_detector.inspect(text, crossing_type)
        observations.append(sec_obs)
        if sec_obs.verdict == SecurityVerdict.BLOCK:
            reason_codes.extend(sec_obs.reason_codes)

        # 3. External Disclosure Gate + Semantic L1 Adapter
        admissibility = "LOCAL_ONLY"
        if self.external_adapter is not None:
            region = getattr(self.external_adapter, "region", "us-central1")
            admissible, disc_reason = self.disclosure_gate.evaluate(
                classification=classification,
                provider=self.external_adapter.name,
                region=region,
                actor_id=actor_id,
                session_id=session_id,
                disclosure_approved=disclosure_approved,
            )
            admissibility = disc_reason
            if admissible:
                ext_obs = self.external_adapter.inspect(text, crossing_type)
                observations.append(ext_obs)
                reason_codes.extend(ext_obs.reason_codes)
            else:
                reason_codes.append(disc_reason)
                if self.local_semantic_fallback is not None:
                    loc_obs = self.local_semantic_fallback.inspect(text, crossing_type)
                    observations.append(loc_obs)
                    reason_codes.extend(loc_obs.reason_codes)
                else:
                    observations.append(
                        DetectorObservation(
                            detector="disclosure-gate",
                            operation=f"gate:{crossing_type.value}",
                            verdict=SecurityVerdict.UNAVAILABLE,
                            latency_ms=0.0,
                            request_content_hash=content_hash,
                            timestamp=_utc_now_iso(),
                            provider="local",
                            reason_codes=(disc_reason,),
                        )
                    )
        elif self.local_semantic_fallback is not None:
            loc_obs = self.local_semantic_fallback.inspect(text, crossing_type)
            observations.append(loc_obs)
            reason_codes.extend(loc_obs.reason_codes)

        # 4. Policy aggregation: preserve disagreement, fail closed on any non-ALLOW
        verdicts = {o.verdict for o in observations}
        if SecurityVerdict.BLOCK in verdicts:
            policy = PolicyOutcome.BLOCK
        elif any(v in {SecurityVerdict.UNAVAILABLE, SecurityVerdict.ERROR, SecurityVerdict.UNKNOWN} for v in verdicts):
            policy = PolicyOutcome.HOLD
        elif verdicts == {SecurityVerdict.ALLOW}:
            policy = PolicyOutcome.ALLOW
        else:
            policy = PolicyOutcome.HOLD

        return CrossingDecision(
            crossing_id=crossing_id,
            crossing_type=crossing_type,
            source_domain=source_domain,
            destination_domain=destination_domain,
            actor_id=actor_id,
            session_id=session_id,
            content_hash=content_hash,
            inspection_hash=inspection_hash,
            classification=classification,
            provider_admissibility=admissibility,
            observations=tuple(observations),
            policy_verdict=policy,
            reason_codes=tuple(dict.fromkeys(reason_codes)),
            authority_context=authority_context or {},
        )

    @staticmethod
    def verify_final_bytes(decision: CrossingDecision, delivered_bytes: str | bytes) -> tuple[bool, str]:
        """Final-byte invariant: delivered bytes MUST match F12-approved content_hash."""
        if decision.policy_verdict != PolicyOutcome.ALLOW:
            return False, "FINAL_BYTES_REJECTED_NON_ALLOW"
        delivered_hash = sha256_bytes(delivered_bytes)
        if delivered_hash != decision.content_hash:
            return False, "FINAL_BYTES_HASH_MISMATCH"
        return True, delivered_hash
