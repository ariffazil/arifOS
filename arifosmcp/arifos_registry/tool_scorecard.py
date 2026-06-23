"""
Tool Scorecard — Per-tool OpenSSF-style score.

OpenSSF Scorecard is the supply-chain security standard for open-source repos.
Adapted here for individual MCP tools: each tool gets a 0-10 score across:
- Code review (signed commits, two-party review)
- Dangerous workflow (no unsafe eval, no shell injection)
- Pinned dependencies
- Token permissions (least privilege)
- Binary artifacts (no embedded secrets)
- License (OSI-approved)
- Test coverage
- Maintenance (recent commits, issue response)

Phase 1: scaffold + scorecard data model.
Phase 2: integrate with OpenSSF Scorecard API.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ToolScorecard:
    """Per-tool OpenSSF-style security scorecard."""

    tool_name: str
    source_repository: str
    code_review_score: float = 0.0  # 0–10
    dangerous_workflow_score: float = 0.0
    pinned_dependencies_score: float = 0.0
    token_permissions_score: float = 0.0
    binary_artifacts_score: float = 0.0
    license_score: float = 0.0
    test_coverage_score: float = 0.0
    maintenance_score: float = 0.0
    notes: dict = field(default_factory=dict)
    last_evaluated: str = ""

    @property
    def composite(self) -> float:
        weights = {
            "code_review": 0.20,
            "dangerous_workflow": 0.20,
            "pinned_dependencies": 0.10,
            "token_permissions": 0.15,
            "binary_artifacts": 0.10,
            "license": 0.05,
            "test_coverage": 0.10,
            "maintenance": 0.10,
        }
        return (
            self.code_review_score * weights["code_review"]
            + self.dangerous_workflow_score * weights["dangerous_workflow"]
            + self.pinned_dependencies_score * weights["pinned_dependencies"]
            + self.token_permissions_score * weights["token_permissions"]
            + self.binary_artifacts_score * weights["binary_artifacts"]
            + self.license_score * weights["license"]
            + self.test_coverage_score * weights["test_coverage"]
            + self.maintenance_score * weights["maintenance"]
        )

    @property
    def tier(self) -> str:
        c = self.composite
        if c >= 8.0:
            return "GOLD"
        if c >= 6.0:
            return "SILVER"
        if c >= 4.0:
            return "BRONZE"
        return "REJECT"

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "source_repository": self.source_repository,
            "scores": {
                "code_review": self.code_review_score,
                "dangerous_workflow": self.dangerous_workflow_score,
                "pinned_dependencies": self.pinned_dependencies_score,
                "token_permissions": self.token_permissions_score,
                "binary_artifacts": self.binary_artifacts_score,
                "license": self.license_score,
                "test_coverage": self.test_coverage_score,
                "maintenance": self.maintenance_score,
            },
            "composite": self.composite,
            "tier": self.tier,
            "last_evaluated": self.last_evaluated
            or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "notes": self.notes,
        }
