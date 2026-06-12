"""
Schema Validator — Tool input/output validation for arifOS Gateway v0.1
══════════════════════════════════════════════════════════════════

Caches upstream tool schemas from tools/list responses.
Validates tools/call params against inputSchema before forwarding.
Detects silent upstream tool definition drift.

Hard gate: invalid params → DENIED, never forwarded.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ToolSchema:
    """Cached tool schema with drift detection."""
    tool_name: str
    upstream_id: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    schema_hash: str = ""
    cached_at: float = field(default_factory=time.time)
    trust_level: str = "trusted"  # trusted, untrusted

    def __post_init__(self) -> None:
        if not self.schema_hash and self.input_schema:
            self.schema_hash = hashlib.sha256(
                json.dumps(self.input_schema, sort_keys=True).encode()
            ).hexdigest()[:16]


@dataclass
class ValidationResult:
    """Result of schema validation."""
    valid: bool
    reason: str = ""
    missing_params: list[str] = field(default_factory=list)
    wrong_type_params: list[str] = field(default_factory=list)
    extra_params: list[str] = field(default_factory=list)
    schema_drift_detected: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════


class SchemaValidator:
    """Validate MCP tool call parameters against cached inputSchema.

    Usage:
        validator = SchemaValidator()
        validator.load_tools(upstream_id, tools_list_response)
        result = validator.validate("geox.read_well_plan", params)
    """

    def __init__(self) -> None:
        self._schemas: dict[str, ToolSchema] = {}  # tool_name → ToolSchema
        self._drift_log: list[dict[str, Any]] = []

    # ── Schema loading ────────────────────────────────────────────────────

    def load_tools(
        self,
        upstream_id: str,
        tools: list[dict[str, Any]],
        trust_level: str = "untrusted",
    ) -> int:
        """Load tools from an upstream tools/list response.

        Returns count of tools loaded.
        """
        count = 0
        for tool in tools:
            name = tool.get("name", "")

            # Namespace: prefix with upstream_id if not already
            if not name.startswith(f"{upstream_id}_") and not name.startswith(
                f"{upstream_id}."
            ):
                namespaced = f"{upstream_id}.{name}"
            else:
                namespaced = name

            new_schema = ToolSchema(
                tool_name=namespaced,
                upstream_id=upstream_id,
                description=tool.get("description", ""),
                input_schema=tool.get("inputSchema", {}),
                output_schema=tool.get("outputSchema", {}),
                trust_level=trust_level,
            )

            # Drift detection
            if namespaced in self._schemas:
                existing = self._schemas[namespaced]
                if existing.schema_hash and existing.schema_hash != new_schema.schema_hash:
                    self._drift_log.append({
                        "tool": namespaced,
                        "upstream": upstream_id,
                        "old_hash": existing.schema_hash,
                        "new_hash": new_schema.schema_hash,
                        "detected_at": time.time(),
                    })

            self._schemas[namespaced] = new_schema
            count += 1

        return count

    # ── Validation ────────────────────────────────────────────────────────

    def validate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ValidationResult:
        """Validate arguments against tool's inputSchema.

        Args:
            tool_name: Namespaced tool name (e.g., "geox.read_well_plan").
            arguments: The arguments dict from tools/call.

        Returns:
            ValidationResult with validity and details.
        """
        # Look up schema
        schema = self._schemas.get(tool_name)
        if schema is None:
            return ValidationResult(
                valid=False,
                reason=f"Unknown tool: {tool_name} — schema not cached",
            )

        # No inputSchema = anything goes (trusted upstream only)
        if not schema.input_schema:
            if schema.trust_level == "trusted":
                return ValidationResult(valid=True, reason="No schema — trusted upstream")
            return ValidationResult(
                valid=False,
                reason="No inputSchema defined for untrusted upstream",
            )

        input_schema = schema.input_schema
        schema_type = input_schema.get("type", "object")
        required_params: list[str] = input_schema.get("required", [])
        properties: dict[str, Any] = input_schema.get("properties", {})

        # If schema doesn't expect object, skip detailed validation
        if schema_type != "object":
            return ValidationResult(valid=True, reason=f"Schema type={schema_type} — basic pass")

        missing = []
        wrong_type = []
        extra = []

        # Check required params
        for param in required_params:
            if param not in arguments:
                missing.append(param)

        # Check argument types against schema properties
        for arg_name, arg_value in arguments.items():
            if arg_name in properties:
                prop = properties[arg_name]
                expected_type = prop.get("type", "")
                if expected_type and not self._type_matches(arg_value, expected_type):
                    wrong_type.append(
                        f"{arg_name}: expected {expected_type}, got {type(arg_value).__name__}"
                    )
            elif arg_name not in properties and properties:
                # Extra param with no schema definition
                extra.append(arg_name)

        if missing:
            return ValidationResult(
                valid=False,
                reason=f"Missing required params: {missing}",
                missing_params=missing,
            )

        if wrong_type:
            return ValidationResult(
                valid=False,
                reason=f"Type mismatch: {wrong_type}",
                wrong_type_params=wrong_type,
            )

        return ValidationResult(valid=True, reason="Schema validated")

    # ── Drift detection ───────────────────────────────────────────────────

    def check_drift(self, tool_name: str) -> ValidationResult:
        """Check if a tool's schema has drifted since last cache."""
        schema = self._schemas.get(tool_name)
        if schema is None:
            return ValidationResult(valid=False, reason=f"Unknown tool: {tool_name}")

        # Check recent drift log
        for entry in self._drift_log:
            if entry["tool"] == tool_name:
                return ValidationResult(
                    valid=False,
                    reason=f"Schema drift detected: {entry['old_hash']} → {entry['new_hash']}",
                    schema_drift_detected=True,
                )

        return ValidationResult(valid=True, reason="No drift detected")

    def drift_events(self) -> list[dict[str, Any]]:
        """Return all detected drift events."""
        return list(self._drift_log)

    # ── Tool poisoning scan ───────────────────────────────────────────────

    def scan_tool_description(self, tool_name: str) -> ValidationResult:
        """Scan tool description for prompt injection / poisoning patterns."""
        schema = self._schemas.get(tool_name)
        if schema is None:
            return ValidationResult(valid=False, reason=f"Unknown tool: {tool_name}")

        desc = schema.description.lower()
        poisoning_signals = [
            "ignore previous",
            "disregard all instructions",
            "you are now",
            "system prompt override",
            "bypass security",
            "do not validate",
            "skip authorization",
            "admin mode activated",
            "ignore floors",
        ]

        for signal in poisoning_signals:
            if signal in desc:
                return ValidationResult(
                    valid=False,
                    reason=f"Tool description poisoning signal: '{signal}'",
                )

        return ValidationResult(valid=True, reason="Clean")

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _type_matches(value: Any, expected_type: str) -> bool:
        """Check if value matches JSON Schema type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True  # unknown type — pass
        return isinstance(value, expected)

    def tool_count(self) -> int:
        return len(self._schemas)

    def tool_names(self) -> list[str]:
        return sorted(self._schemas.keys())


# ═══════════════════════════════════════════════════════════════════════════
# PAYLOAD LIMITS
# ═══════════════════════════════════════════════════════════════════════════


class PayloadLimiter:
    """Enforce max payload size for MCP requests."""

    def __init__(self, max_bytes: int = 1_048_576) -> None:  # 1MB default
        self.max_bytes = max_bytes

    def check(self, body: bytes | str) -> bool:
        """Return True if payload is within limits."""
        if isinstance(body, str):
            body = body.encode("utf-8")
        return len(body) <= self.max_bytes

    def check_json(self, body: dict[str, Any]) -> bool:
        """Check approximate size of JSON-serializable body."""
        return self.check(json.dumps(body, default=str))
