"""Policy engine — YAML policy loader with tool/role matching.

v0.1: simple match on tool name (glob) + subject roles.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from typing import Any


class PolicyEngine:
    """Match policies against tool names and subject roles.

    Policies are ordered; first match wins.
    """

    def __init__(self, policies: list[dict[str, Any]] | None = None) -> None:
        self._policies: list[dict[str, Any]] = policies or []

    def match(self, tool_name: str, roles: list[str]) -> dict[str, Any]:
        """Return merged policy defaults for a tool + role combination.

        First matching policy wins. Returns empty dict if no match.
        """
        for policy in self._policies:
            match = policy.get("match", {})
            tool_pattern = match.get("tool", "*")
            required_roles = match.get("subject", {}).get("roles", ["*"])

            if _match_tool(tool_name, tool_pattern) and _match_roles(roles, required_roles):
                return dict(policy.get("lease_defaults", {}))
        return {}

    def add_policy(self, policy: dict[str, Any]) -> None:
        """Add a policy to the engine."""
        self._policies.append(policy)


def _match_tool(tool_name: str, pattern: str) -> bool:
    """Simple tool name matching: exact, wildcard, or prefix.

    Patterns:
      "*"           — matches all
      "geox.*"      — prefix match
      "*.read_*"    — suffix + sub-pattern
      "exact_name"  — exact match
    """
    if pattern == "*":
        return True
    if pattern.endswith("*") and not pattern.startswith("*"):
        prefix = pattern[:-1]
        return tool_name.startswith(prefix)
    if pattern.startswith("*") and not pattern.endswith("*"):
        suffix = pattern[1:]
        return tool_name.endswith(suffix)
    if "*" in pattern:
        import fnmatch
        return fnmatch.fnmatch(tool_name, pattern)
    return tool_name == pattern


def _match_roles(subject_roles: list[str], required_roles: list[str]) -> bool:
    """Check if subject has at least one required role.

    "*" in required_roles matches any subject.
    """
    if "*" in required_roles:
        return True
    if not required_roles:
        return True
    return bool(set(subject_roles) & set(required_roles))


def load_policies(raw: dict[str, Any]) -> PolicyEngine:
    """Load policies from a YAML config dict.

    Config shape:
        policies:
          policy_name:
            match:
              tool: "geox.*"
              subject:
                roles: ["geologist"]
            lease_defaults:
              risk_class: "LOW"
              max_invocations: 50
    """
    policies_list = []
    for _name, policy_def in raw.items():
        if isinstance(policy_def, dict) and "match" in policy_def:
            policies_list.append(policy_def)
    return PolicyEngine(policies_list)
