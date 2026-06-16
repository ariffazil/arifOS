"""
Capability Manifest — Per-tool capability matrix.

Cross-references a tool with:
- What organs it can call
- What data it can read
- What data it can write
- Whether it can hold leases
- Whether it can issue leases
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CapabilityManifest:
    """Per-tool capability matrix."""

    tool_name: str
    can_call_organs: list[str] = field(default_factory=list)
    can_read_data: list[str] = field(default_factory=list)
    can_write_data: list[str] = field(default_factory=list)
    can_hold_leases: bool = False
    can_issue_leases: bool = False
    requires_session: bool = True
    requires_actor: bool = True
    network_egress_allowed: bool = True
    filesystem_paths: list[str] = field(default_factory=list)
    secret_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "can_call_organs": self.can_call_organs,
            "can_read_data": self.can_read_data,
            "can_write_data": self.can_write_data,
            "can_hold_leases": self.can_hold_leases,
            "can_issue_leases": self.can_issue_leases,
            "requires_session": self.requires_session,
            "requires_actor": self.requires_actor,
            "network_egress_allowed": self.network_egress_allowed,
            "filesystem_paths": self.filesystem_paths,
            "secret_paths": self.secret_paths,
        }
