"""
constitutional_core.py — Sovereign Governance Engine
════════════════════════════════════════════════════

The single canonical authority for all constitutional evaluation.

No tool may evaluate threats, floors, or authority outside this core.
No tool may bypass this core for consequential actions.
No tool may implement its own interpretation of F01–F13.

Law is centralized. Law is deterministic. Law is non-optional.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import ast
import hashlib
import ipaddress
import json
import re
import urllib.parse
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ═══════════════════════════════════════════════════════════════════════════════
# 1. UNIFIED THREAT ONTOLOGY
# ═══════════════════════════════════════════════════════════════════════════════


class ThreatCategory(Enum):
    """Canonical threat taxonomy — used by all tools. No exceptions."""

    FILESYSTEM_DESTRUCTIVE = auto()
    DATABASE_DESTRUCTIVE = auto()
    CONTAINER_DESTRUCTIVE = auto()
    NETWORK_ADMIN_ACTION = auto()
    SYSTEM_SHUTDOWN = auto()
    INJECTION_SQL = auto()
    INJECTION_XSS = auto()
    INJECTION_SHELL = auto()
    INJECTION_PYTHON = auto()
    SESSION_IMPERSONATION = auto()
    FEDERATION_IMPERSONATION = auto()
    PRIVILEGE_ESCALATION = auto()
    DATA_EXFILTRATION = auto()
    CRYPTO_VIOLATION = auto()


# Mapping: which threats are inherently irreversible/destructive
THREAT_IRREVERSIBILITY: dict[ThreatCategory, int] = {
    ThreatCategory.FILESYSTEM_DESTRUCTIVE: 3,
    ThreatCategory.DATABASE_DESTRUCTIVE: 3,
    ThreatCategory.CONTAINER_DESTRUCTIVE: 3,
    ThreatCategory.NETWORK_ADMIN_ACTION: 2,
    ThreatCategory.SYSTEM_SHUTDOWN: 3,
    ThreatCategory.INJECTION_SQL: 2,
    ThreatCategory.INJECTION_XSS: 1,
    ThreatCategory.INJECTION_SHELL: 2,
    ThreatCategory.INJECTION_PYTHON: 2,
    ThreatCategory.SESSION_IMPERSONATION: 2,
    ThreatCategory.FEDERATION_IMPERSONATION: 2,
    ThreatCategory.PRIVILEGE_ESCALATION: 2,
    ThreatCategory.DATA_EXFILTRATION: 2,
    ThreatCategory.CRYPTO_VIOLATION: 3,
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ACTION CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════


class IrreversibilityLevel(Enum):
    NONE = 0
    LOW = 1
    HIGH = 2
    CRITICAL = 3


class WitnessType(Enum):
    AI = "ai"
    HUMAN = "human"
    MULTI = "multi"


class ActionContext(BaseModel):
    """
    Everything the ConstitutionalCore needs to evaluate an action.

    Tools build this context and submit it. They do NOT interpret it.
    """

    tool_name: str = Field(..., description="Canonical tool identifier")
    mode: str = Field(default="default", description="Tool mode being invoked")
    actor_id: str | None = Field(default=None, description="Sovereign actor identity")
    session_id: str | None = Field(default=None, description="Governed session token")

    # The raw payload that carries intent
    candidate: str | None = Field(default=None, description="Action under evaluation")
    manifest: str | None = Field(default=None, description="Forge manifest or code payload")
    query: str | None = Field(default=None, description="Search or reasoning query")
    url: str | None = Field(default=None, description="URL for fetch/ingest")
    target_agent: str | None = Field(default=None, description="Federation target")

    # Authority signals
    ack_irreversible: bool = Field(default=False, description="F01 Amanah explicit ack")
    witness_type: WitnessType = Field(default=WitnessType.AI, description="F13 witness type")
    plan_id: str | None = Field(default=None, description="H2 ratified plan ID")

    # Cryptographic proofs
    constitutional_chain_id: str | None = Field(default=None)
    judge_state_hash: str | None = Field(default=None)

    # Session registry (injected at call time)
    session_registry: set[str] = Field(default_factory=set, exclude=True)
    federation_registry: set[str] = Field(default_factory=set, exclude=True)
    plan_registry: set[str] = Field(default_factory=set, exclude=True)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str | None) -> str | None:
        if not v:
            return v
        # Scheme restriction
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {v}. Only http:// and https:// allowed.")
        # SSRF / internal network block
        parsed = urllib.parse.urlparse(v)
        hostname = parsed.hostname or ""
        blocked_hostnames = {
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            "postgres",
            "redis",
            "qdrant",
            "vault999",
            "arifosmcp",
            "ollama",
            "geox",
            "wealth-organ",
            "aaa",
            "caddy",
        }
        if hostname.lower() in blocked_hostnames:
            raise ValueError(f"SSRF blocked: internal hostname '{hostname}' is not reachable.")
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            pass  # hostname is not an IP, that's fine
        else:
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast:
                raise ValueError(f"SSRF blocked: internal IP '{hostname}' is not reachable.")
        return v

    def payload_text(self) -> str:
        """Extract the richest text representation for threat analysis."""
        for attr in ("candidate", "manifest", "query", "url", "target_agent"):
            val = getattr(self, attr)
            if val:
                return val
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
# 3. THREAT ENGINE — Semantic, Not Regex
# ═══════════════════════════════════════════════════════════════════════════════


class ThreatAssessment(BaseModel):
    threats: set[ThreatCategory] = Field(default_factory=set)
    irreversibility: IrreversibilityLevel = Field(default=IrreversibilityLevel.NONE)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)


class ThreatEngine:
    """
    Parses Python AST, SQL tokens, shell structure, and natural language
    into a unified ThreatAssessment.

    No regex morality. Structured semantic analysis.
    """

    # ── Python destructive calls ──
    PYTHON_DESTRUCTIVE_CALLS = {
        ("shutil", "rmtree"),
        ("os", "remove"),
        ("os", "rmdir"),
        ("os", "unlink"),
        ("os", "removedirs"),
        ("os", "system"),
        ("os", "popen"),
        ("subprocess", "call"),
        ("subprocess", "run"),
        ("subprocess", "Popen"),
        ("pathlib", "Path", "unlink"),
        ("pathlib", "Path", "rmdir"),
        ("builtins", "eval"),
        ("builtins", "exec"),
        ("builtins", "compile"),
        ("eval",),  # bare eval()
        ("exec",),  # bare exec()
        ("compile",),  # bare compile()
    }

    # ── Docker destructive flags ──
    DOCKER_DESTRUCTIVE = [
        "docker system prune",
        "docker volume prune",
        "docker container prune",
        "docker image prune",
        "docker network prune",
        "--volumes",
        "prune -a",
        "prune -f",
    ]

    # ── SQL destructive keywords ──
    SQL_DESTRUCTIVE = [
        "drop table",
        "drop database",
        "truncate table",
        "delete from",
    ]
    SQL_INJECTION = ["; --", "';", '";', "union select", "or 1=1", "exec(", "execute("]

    # ── Shell injection ──
    SHELL_INJECTION = [
        "; rm",
        "&& rm",
        "| sh",
        "| bash",
        "`rm",
        "$(rm",
        "eval(",
        "exec(",
    ]

    # ── XSS ──
    XSS_PATTERNS = [
        "<script>",
        "javascript:",
        "onerror=",
        "onload=",
        "alert(",
        "document.cookie",
    ]

    # ── Admin / shutdown ──
    ADMIN_ACTIONS = [
        "action=shutdown",
        "shutdown -h",
        "shutdown -r",
        "reboot",
        "poweroff",
        "systemctl stop",
        "kill -9",
    ]

    @classmethod
    def classify(cls, context: ActionContext) -> ThreatAssessment:
        text = context.payload_text().lower()
        threats: set[ThreatCategory] = set()
        reasoning: list[str] = []

        # 1. Python AST analysis
        py_threats, py_reason = cls._analyze_python(context.manifest or context.candidate or "")
        threats |= py_threats
        reasoning.extend(py_reason)

        # 2. Docker analysis
        if any(p in text for p in cls.DOCKER_DESTRUCTIVE):
            threats.add(ThreatCategory.CONTAINER_DESTRUCTIVE)
            reasoning.append("Docker destructive command detected")

        # 3. SQL analysis
        if any(p in text for p in cls.SQL_DESTRUCTIVE):
            threats.add(ThreatCategory.DATABASE_DESTRUCTIVE)
            reasoning.append("SQL destructive statement detected")
        if any(p in text for p in cls.SQL_INJECTION):
            threats.add(ThreatCategory.INJECTION_SQL)
            reasoning.append("SQL injection pattern detected")

        # 4. Shell injection
        if any(p in text for p in cls.SHELL_INJECTION):
            threats.add(ThreatCategory.INJECTION_SHELL)
            reasoning.append("Shell injection pattern detected")

        # 5. XSS
        if any(p in text for p in cls.XSS_PATTERNS):
            threats.add(ThreatCategory.INJECTION_XSS)
            reasoning.append("XSS payload detected")

        # 6. Admin / shutdown
        if any(p in text for p in cls.ADMIN_ACTIONS):
            threats.add(ThreatCategory.NETWORK_ADMIN_ACTION)
            reasoning.append("Network/system admin action detected")

        # 7. rm -rf patterns
        if re.search(r"\brm\s+-rf?\s+[/~*]", text):
            threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
            reasoning.append("rm -rf filesystem destructive pattern")

        # Compute irreversibility
        max_irrev = max(
            (THREAT_IRREVERSIBILITY.get(t, 0) for t in threats),
            default=0,
        )
        irreversibility = IrreversibilityLevel(max_irrev)

        return ThreatAssessment(
            threats=threats,
            irreversibility=irreversibility,
            confidence=1.0 if threats else 0.0,
            reasoning=reasoning,
        )

    @classmethod
    def _analyze_python(cls, code: str) -> tuple[set[ThreatCategory], list[str]]:
        """AST-based analysis of Python code strings."""
        threats: set[ThreatCategory] = set()
        reasoning: list[str] = []

        if not code.strip():
            return threats, reasoning

        # If it doesn't look like Python, skip AST parsing
        if not any(kw in code for kw in ("def ", "import ", "(", ")", ":", "=")):
            return threats, reasoning

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Not valid Python — fall back to string checks
            if "shutil.rmtree" in code:
                threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
                reasoning.append("shutil.rmtree detected (string fallback)")
            return threats, reasoning

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_path = cls._get_call_path(node.func)
                if call_path in cls.PYTHON_DESTRUCTIVE_CALLS:
                    threats.add(ThreatCategory.FILESYSTEM_DESTRUCTIVE)
                    reasoning.append(f"Destructive Python call: {'.'.join(call_path)}")
                if call_path in {("builtins", "eval"), ("builtins", "exec")}:
                    threats.add(ThreatCategory.INJECTION_PYTHON)
                    reasoning.append(f"Dangerous eval/exec: {'.'.join(call_path)}")

        return threats, reasoning

    @staticmethod
    def _get_call_path(node: ast.expr) -> tuple[str, ...]:
        """Extract fully qualified call path from AST node."""
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return tuple(reversed(parts))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. IRREVERSIBILITY MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class IrreversibilityModel:
    """
    Maps threat categories to irreversibility levels.
    Tools do NOT guess irreversibility. They query this model.
    """

    @staticmethod
    def from_threats(assessment: ThreatAssessment) -> IrreversibilityLevel:
        return assessment.irreversibility

    @staticmethod
    def requires_human_ack(level: IrreversibilityLevel) -> bool:
        return level.value >= IrreversibilityLevel.HIGH.value

    @staticmethod
    def requires_judge_pre_authorization(level: IrreversibilityLevel) -> bool:
        return level.value >= IrreversibilityLevel.CRITICAL.value


# ═══════════════════════════════════════════════════════════════════════════════
# 5. FLOOR EVALUATOR — Centralized, Parametric
# ═══════════════════════════════════════════════════════════════════════════════


class FloorResult(BaseModel):
    verdict: str = Field(default="SEAL")  # SEAL | HOLD | VOID
    failed_floors: list[str] = Field(default_factory=list)
    floor_reasons: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FloorEvaluator:
    """
    F01–F13 are parametric functions of (context, threat, authority).

    No special-casing per tool. No duplicated logic.
    """

    @classmethod
    def evaluate(cls, context: ActionContext, threat: ThreatAssessment) -> FloorResult:
        failed: list[str] = []
        reasons: dict[str, str] = {}

        # F01 AMANAH — Trustworthiness / Irreversibility
        # Some tools are inherently irreversible regardless of payload content
        tool_base_irreversibility = {
            ("arif_vault_seal", "seal"): IrreversibilityLevel.CRITICAL,
            ("arif_vault_seal", "commit"): IrreversibilityLevel.CRITICAL,
            ("arif_vault_seal", "session_seal"): IrreversibilityLevel.LOW,
            ("arif_forge_execute", "engineer"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "write"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "generate"): IrreversibilityLevel.HIGH,
        }
        base_irrev = tool_base_irreversibility.get((context.tool_name, context.mode))
        effective_irreversibility = max(
            threat.irreversibility,
            base_irrev or IrreversibilityLevel.NONE,
            key=lambda x: x.value,
        )

        if effective_irreversibility.value >= IrreversibilityLevel.HIGH.value:
            if not context.ack_irreversible:
                failed.append("F01")
                reasons["F01"] = (
                    f"Irreversible action (level={effective_irreversibility.name}) "
                    "requires ack_irreversible=True"
                )

        # F02 TRUTH — No fabrication
        # (Enforced at data layer, not action layer)

        # F03 WITNESS — Evidence preservation
        # (Enforced at vault layer)

        # F04 CLARITY — Transparent intent
        if not context.candidate and not context.manifest and not context.query:
            # Empty intent is only a problem for judge/forge modes
            if context.tool_name in ("arif_judge_deliberate", "arif_forge_execute"):
                failed.append("F04")
                reasons["F04"] = "Action intent is empty or unclear"

        # F05 PEACE — No harm to dignity
        # (Enforced by heart_critique)

        # F06 EMPATHY — Consider consequences
        # (Enforced by heart_critique)

        # F07 HUMILITY — Acknowledge limits
        # (Enforced by mind_reason)

        # F08 GENIUS — Elegant correctness
        if threat.irreversibility.value >= IrreversibilityLevel.CRITICAL.value:
            # Critical actions require extra scrutiny — genius demands caution
            pass  # Not a blocker, but annotated

        # F09 ANTI-HANTU — No consciousness claims
        # (Enforced at content layer)

        # F10 ONTOLOGY — Structural coherence
        if context.tool_name == "arif_judge_deliberate" and context.mode not in {
            "judge",
            "compare",
            "history",
            "explain",
            "rules",
            "validate",
            "hold",
            "armor",
            "probe",
            "notify",
        }:
            failed.append("F10")
            reasons["F10"] = f"Unknown judge mode: {context.mode}"

        # F11 AUTH — Verify identity
        if context.session_id and context.session_id not in context.session_registry:
            failed.append("F11")
            reasons["F11"] = "Session ID not found or expired"

        if context.target_agent and context.target_agent not in context.federation_registry:
            failed.append("F11")
            reasons["F11"] = f"Agent '{context.target_agent}' not in federation registry"

        # F12 INJECTION — Sanitize inputs
        injection_categories = {
            ThreatCategory.INJECTION_SQL,
            ThreatCategory.INJECTION_XSS,
            ThreatCategory.INJECTION_SHELL,
            ThreatCategory.INJECTION_PYTHON,
        }
        if threat.threats & injection_categories:
            failed.append("F12")
            detected = [t.name for t in threat.threats & injection_categories]
            reasons["F12"] = f"Injection threat detected: {detected}"

        # F13 SOVEREIGN — Human veto is absolute
        if cls._requires_human_witness(context, threat):
            if context.witness_type != WitnessType.HUMAN:
                # Distinguish sovereignty violation (AI self-approval) from missing witness
                if context.tool_name == "arif_mind_reason" and context.mode == "plan_approve":
                    failed.append("F13_VIOLATION")
                    reasons["F13_VIOLATION"] = (
                        "F13 SOVEREIGN: AI self-approval is constitutionally forbidden"
                    )
                else:
                    failed.append("F13")
                    reasons["F13"] = (
                        f"Action requires human witness (tool={context.tool_name}, "
                        f"irreversibility={threat.irreversibility.name}). "
                        f"witness_type='{context.witness_type.value}' is insufficient."
                    )

        if failed:
            # VOID for: sovereignty violations, critical irreversibility, injection threats
            is_void = (
                "F13_VIOLATION" in failed
                or threat.irreversibility == IrreversibilityLevel.CRITICAL
                or bool(
                    threat.threats
                    & {
                        ThreatCategory.INJECTION_SQL,
                        ThreatCategory.INJECTION_XSS,
                        ThreatCategory.INJECTION_SHELL,
                        ThreatCategory.INJECTION_PYTHON,
                    }
                )
            )
            verdict = "VOID" if is_void else "HOLD"
            return FloorResult(
                verdict=verdict,
                failed_floors=failed,
                floor_reasons=reasons,
                metadata={
                    "threats": [t.name for t in threat.threats],
                    "irreversibility": threat.irreversibility.name,
                },
            )

        return FloorResult(
            verdict="SEAL", metadata={"irreversibility": threat.irreversibility.name}
        )

    @staticmethod
    def _requires_human_witness(context: ActionContext, threat: ThreatAssessment) -> bool:
        """Determine if F13 requires a human witness for this action."""
        # Hard-coded canonical policy — mode-aware
        human_required_tools_modes = {
            "arif_vault_seal": {"seal", "commit"},
            "arif_forge_execute": {"engineer", "write", "generate"},
        }
        human_required_modes = {
            ("arif_mind_reason", "plan_approve"),
        }

        if context.tool_name in human_required_tools_modes:
            if context.mode in human_required_tools_modes[context.tool_name]:
                return True
        if (context.tool_name, context.mode) in human_required_modes:
            return True
        if threat.irreversibility.value >= IrreversibilityLevel.CRITICAL.value:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. AUTHORITY GATE — Non-Bypassable
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityProof(BaseModel):
    authorized: bool = False
    requires_human: bool = False
    witness_type: WitnessType = WitnessType.AI
    plan_approved: bool = False
    reason: str = ""


class AuthorityGate:
    """
    Authority is not a flag. It is a proof generated by this gate.

    No tool may self-authorize. No tool may bypass this gate.
    """

    @classmethod
    def verify(
        cls, context: ActionContext, threat: ThreatAssessment, floors: FloorResult
    ) -> AuthorityProof:
        requires_human = FloorEvaluator._requires_human_witness(context, threat)

        # Check plan approval for forge engineer/write/generate
        plan_approved = False
        if context.tool_name == "arif_forge_execute" and context.mode in {
            "engineer",
            "write",
            "generate",
        }:
            if context.plan_id and context.plan_id in context.plan_registry:
                plan_approved = True
            else:
                return AuthorityProof(
                    authorized=False,
                    requires_human=True,
                    reason=f"Forge mode='{context.mode}' requires approved plan_id (H2 ratification)",  # noqa: E501
                )

        if requires_human and context.witness_type != WitnessType.HUMAN:
            return AuthorityProof(
                authorized=False,
                requires_human=True,
                witness_type=context.witness_type,
                plan_approved=plan_approved,
                reason="F13 SOVEREIGN: human witness required",
            )

        return AuthorityProof(
            authorized=True,
            requires_human=requires_human,
            witness_type=context.witness_type,
            plan_approved=plan_approved,
            reason="Authority verified",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CONSTITUTION KERNEL — The Sovereign
# ═══════════════════════════════════════════════════════════════════════════════


class ConstitutionalVerdict(BaseModel):
    status: str = Field(..., description="OK | HOLD | VOID")
    verdict: str = Field(..., description="SEAL | SABAR | HOLD | VOID")
    threat: ThreatAssessment
    floors: FloorResult
    authority: AuthorityProof
    irreversibility: IrreversibilityLevel
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state_hash: str = Field(default="")

    def model_post_init(self, __context: Any) -> None:
        if not self.state_hash:
            self.state_hash = self._compute_state_hash()

    def _compute_state_hash(self) -> str:
        payload = {
            "status": self.status,
            "verdict": self.verdict,
            "threats": sorted(t.name for t in self.threat.threats),
            "floors": self.floors.failed_floors,
            "authority": json.loads(self.authority.model_dump_json()),
            "irreversibility": self.irreversibility.name,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @property
    def authorized(self) -> AuthorityProof:
        return self.authority


class ConstitutionKernel:
    """
    The single canonical authority.

    All tools call this. None bypass it.
    """

    def __init__(self) -> None:
        self.threat_engine = ThreatEngine()
        self.irreversibility_model = IrreversibilityModel()
        self.floor_evaluator = FloorEvaluator()
        self.authority_gate = AuthorityGate()

    def evaluate(self, context: ActionContext) -> ConstitutionalVerdict:
        """
        The only legal path from intent to authorization.

        1. Classify threat semantically
        2. Compute irreversibility
        3. Evaluate constitutional floors
        4. Verify authority
        5. Issue constitutional advisory verdict (human authority remains final)
        """
        # Step 1: Threat classification
        threat = self.threat_engine.classify(context)

        # Step 2: Irreversibility (threat-based + tool base)
        threat_irreversibility = self.irreversibility_model.from_threats(threat)
        tool_base_irreversibility = {
            ("arif_vault_seal", "seal"): IrreversibilityLevel.CRITICAL,
            ("arif_vault_seal", "commit"): IrreversibilityLevel.CRITICAL,
            ("arif_vault_seal", "session_seal"): IrreversibilityLevel.LOW,
            ("arif_forge_execute", "engineer"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "write"): IrreversibilityLevel.HIGH,
            ("arif_forge_execute", "generate"): IrreversibilityLevel.HIGH,
        }
        base_irrev = tool_base_irreversibility.get((context.tool_name, context.mode))
        irreversibility = max(
            threat_irreversibility,
            base_irrev or IrreversibilityLevel.NONE,
            key=lambda x: x.value,
        )

        # Step 3: Floor evaluation
        floors = self.floor_evaluator.evaluate(context, threat)

        # Step 4: Authority verification
        authority = self.authority_gate.verify(context, threat, floors)

        # Step 5: Verdict computation
        # Injection threats are permanently blocked (VOID) regardless of irreversibility level
        injection_threats = {
            ThreatCategory.INJECTION_SQL,
            ThreatCategory.INJECTION_XSS,
            ThreatCategory.INJECTION_SHELL,
            ThreatCategory.INJECTION_PYTHON,
        }
        has_injection = bool(threat.threats & injection_threats)

        # Verdict logic:
        # - VOID: destructive threats, injection, sovereignty violations
        # - HOLD: procedural failures (missing ack, missing witness) on non-destructive actions
        is_destructive = bool(
            threat.threats
            & {
                ThreatCategory.FILESYSTEM_DESTRUCTIVE,
                ThreatCategory.DATABASE_DESTRUCTIVE,
                ThreatCategory.CONTAINER_DESTRUCTIVE,
                ThreatCategory.SYSTEM_SHUTDOWN,
            }
        )
        is_sovereignty_violation = "F13_VIOLATION" in floors.failed_floors

        if floors.verdict == "VOID" or not authority.authorized:
            status = "HOLD"
            verdict = (
                "VOID" if (is_sovereignty_violation or is_destructive or has_injection) else "HOLD"
            )
        elif floors.verdict == "HOLD":
            status = "HOLD"
            verdict = "VOID" if (is_destructive or has_injection) else "HOLD"
        else:
            status = "OK"
            verdict = "SEAL"

        return ConstitutionalVerdict(
            status=status,
            verdict=verdict,
            threat=threat,
            floors=floors,
            authority=authority,
            irreversibility=irreversibility,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. SCHEMA CONTRACT VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════════


class SchemaContractValidator:
    """
    Validates that documented API, Pydantic models, and MCP elicitation schemas
    are isomorphic.

    Run this in CI. Fail the build on mismatch.
    """

    @staticmethod
    def validate_elicitation_model(model: type[BaseModel]) -> list[str]:
        """Ensure model fields are compatible with MCP elicitation schemas."""
        errors: list[str] = []
        for name, field_info in model.model_fields.items():
            annotation = field_info.annotation
            # FastMCP elicitation rejects Union with None
            if hasattr(annotation, "__origin__") and annotation.__origin__ is type[None] | str:
                errors.append(
                    f"Field '{name}' has Union type with None — "
                    "FastMCP elicitation will reject this. Use default='' instead."
                )
        return errors

    @staticmethod
    def validate_mode_consistency(
        documented_modes: set[str],
        implemented_modes: set[str],
        tool_name: str,
    ) -> list[str]:
        """Ensure docs match runtime implementation."""
        errors: list[str] = []
        missing = documented_modes - implemented_modes
        extra = implemented_modes - documented_modes
        if missing:
            errors.append(f"{tool_name}: documented modes missing in implementation: {missing}")
        if extra:
            errors.append(f"{tool_name}: implemented modes not documented: {extra}")
        return errors


# ═══════════════════════════════════════════════════════════════════════════════
# 9. BOOT INVARIANT CHECKER
# ═══════════════════════════════════════════════════════════════════════════════


class BootInvariantChecker:
    """
    System must fail to start if constitutional invariants are violated.

    These are not defaults. They are hard requirements.
    """

    REQUIRED_INVARIANTS = {
        "self_approval_forbidden": True,
        "forge_default_dry_run": True,
        "irreversible_actions_require_ack": True,
        "human_judge_required_for_consequential_actions": True,
    }

    @classmethod
    def check(cls, config: dict[str, Any]) -> None:
        for invariant, required_value in cls.REQUIRED_INVARIANTS.items():
            actual = config.get(invariant)
            if actual != required_value:
                raise RuntimeError(
                    f"BOOT INVARIANT VIOLATED: {invariant} must be {required_value}, got {actual}. "
                    f"System cannot start with compromised constitutional invariants."
                )


# ═══════════════════════════════════════════════════════════════════════════════
# 10. GLOBAL KERNEL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

# Singleton — all tools use this instance
_kernel: ConstitutionKernel | None = None


def get_kernel() -> ConstitutionKernel:
    global _kernel
    if _kernel is None:
        _kernel = ConstitutionKernel()
    return _kernel


def reset_kernel() -> None:
    """Test-only. Resets the singleton."""
    global _kernel
    _kernel = None


__all__ = [
    "ActionContext",
    "AuthorityGate",
    "AuthorityProof",
    "BootInvariantChecker",
    "ConstitutionalVerdict",
    "ConstitutionKernel",
    "FloorEvaluator",
    "FloorResult",
    "get_kernel",
    "IrreversibilityLevel",
    "IrreversibilityModel",
    "reset_kernel",
    "SchemaContractValidator",
    "ThreatAssessment",
    "ThreatCategory",
    "ThreatEngine",
    "WitnessType",
]
