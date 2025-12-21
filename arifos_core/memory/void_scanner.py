"""
void_scanner.py - Phoenix-72 VOID Scanner for arifOS v35Ω

Scans the cooling ledger for VOID/SABAR/888_HOLD entries
and proposes new scars for the negative constraint layer.

This is a background utility, not in the main query path.

Usage:
    scanner = VoidScanner(ledger_path)
    report = scanner.run_scan_report()
    proposals = scanner.propose_scars()
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from arifos_core.memory.cooling_ledger import DEFAULT_LEDGER_PATH


@dataclass
class ScarCandidate:
    """A candidate for scar creation from a VOID verdict."""
    timestamp: float
    query: str
    verdict: str
    floor_failures: List[str]
    job_id: Optional[str]
    ledger_hash: Optional[str]


@dataclass
class ScarProposal:
    """A proposed scar for manual review."""
    text: str
    description: str
    verdict: str
    floor_failures: List[str]
    severity: int
    ledger_ref: Optional[str]
    proposed_at: str
    status: str = "PROPOSED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "description": self.description,
            "verdict": self.verdict,
            "floor_failures": self.floor_failures,
            "severity": self.severity,
            "ledger_ref": self.ledger_ref,
            "proposed_at": self.proposed_at,
            "status": self.status,
        }


class VoidScanner:
    """
    Scans cooling ledger for VOID/SABAR entries and proposes scars.

    Example:
        scanner = VoidScanner()
        print(scanner.run_scan_report(hours=72))

        candidates = scanner.scan(hours=72)
        proposals = scanner.propose_scars(candidates)
        for p in proposals:
            print(p.text, p.severity)
    """

    # Verdicts that indicate potential scar candidates
    VOID_VERDICTS = ["VOID", "SABAR", "888_HOLD"]

    # Critical floors - higher weight for severity
    CRITICAL_FLOORS = {"Truth", "RASA", "Amanah", "Maruah", "Ψ"}

    def __init__(
        self,
        ledger_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ):
        """
        Initialize scanner.

        Args:
            ledger_path: Path to cooling ledger JSONL
            output_path: Path to write proposals (default: runtime/vault_999/scar_proposals.jsonl)
        """
        self.ledger_path = ledger_path or DEFAULT_LEDGER_PATH
        self.output_path = output_path or Path("runtime/vault_999/scar_proposals.jsonl")

    def scan(
        self,
        hours: float = 72.0,
        verdicts: Optional[List[str]] = None,
    ) -> List[ScarCandidate]:
        """
        Scan the cooling ledger for VOID candidates.

        Args:
            hours: Time window to scan (default: 72h for Phoenix-72)
            verdicts: Which verdicts to include (default: VOID, SABAR, 888_HOLD)

        Returns:
            List of ScarCandidate objects
        """
        verdicts = verdicts or self.VOID_VERDICTS
        cutoff = time.time() - hours * 3600.0
        candidates = []

        if not self.ledger_path.exists():
            return candidates

        with self.ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Check time window
                ts = entry.get("timestamp", 0)
                if ts < cutoff:
                    continue

                # Check verdict
                verdict = entry.get("verdict", "")
                if verdict not in verdicts:
                    continue

                # Extract candidate
                candidates.append(ScarCandidate(
                    timestamp=ts,
                    query=entry.get("query", "")[:200],
                    verdict=verdict,
                    floor_failures=entry.get("floor_failures", []),
                    job_id=entry.get("job_id"),
                    ledger_hash=entry.get("hash"),
                ))

        return candidates

    def propose_scars(
        self,
        candidates: Optional[List[ScarCandidate]] = None,
        hours: float = 72.0,
    ) -> List[ScarProposal]:
        """
        Convert candidates into scar proposals.

        Args:
            candidates: Pre-scanned candidates (if None, runs scan())
            hours: Time window for scan if candidates not provided

        Returns:
            List of ScarProposal objects for review
        """
        if candidates is None:
            candidates = self.scan(hours=hours)

        proposals = []
        now = datetime.now(timezone.utc).isoformat()

        for c in candidates:
            if not c.query:
                continue

            severity = self._estimate_severity(c.floor_failures)

            proposal = ScarProposal(
                text=c.query,
                description=f"Auto-detected from {c.verdict}: {', '.join(c.floor_failures[:3])}",
                verdict=c.verdict,
                floor_failures=c.floor_failures,
                severity=severity,
                ledger_ref=c.ledger_hash,
                proposed_at=now,
            )
            proposals.append(proposal)

        return proposals

    def _estimate_severity(self, floor_failures: List[str]) -> int:
        """
        Estimate harm severity from floor failures.

        Returns 1-5 scale:
        1 = Minor (soft floor only)
        2 = Moderate
        3 = Significant (1 critical floor)
        4 = High (2 critical floors)
        5 = Critical (3+ critical floors)
        """
        critical_count = 0
        for failure in floor_failures:
            for critical in self.CRITICAL_FLOORS:
                if critical in failure:
                    critical_count += 1
                    break

        if critical_count >= 3:
            return 5
        elif critical_count >= 2:
            return 4
        elif critical_count >= 1:
            return 3
        elif floor_failures:
            return 2
        return 1

    def run_scan_report(self, hours: float = 72.0) -> str:
        """
        Run a scan and return a human-readable report.

        Use this for manual review before approving scars.
        """
        candidates = self.scan(hours=hours)

        if not candidates:
            return f"Phoenix-72 VOID Scan: No candidates in last {hours}h"

        lines = [
            "=" * 60,
            "Phoenix-72 VOID Scanner Report",
            f"Window: {hours}h | Found: {len(candidates)} candidates",
            "=" * 60,
        ]

        for i, c in enumerate(candidates, 1):
            severity = self._estimate_severity(c.floor_failures)
            lines.append(f"\n[{i}] {c.verdict} (severity: {severity}/5)")
            lines.append(f"    Query: {c.query[:60]}...")
            lines.append(f"    Failures: {', '.join(c.floor_failures)}")
            lines.append(f"    Job ID: {c.job_id}")

        lines.append("\n" + "=" * 60)
        lines.append("Next: scanner.propose_scars() -> review -> approve_scar()")

        return "\n".join(lines)

    def save_proposals(
        self,
        proposals: Optional[List[ScarProposal]] = None,
        hours: float = 72.0,
    ) -> int:
        """
        Save proposals to JSONL file for review.

        Returns:
            Number of proposals saved
        """
        if proposals is None:
            proposals = self.propose_scars(hours=hours)

        if not proposals:
            return 0

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.output_path.open("a", encoding="utf-8") as f:
            for p in proposals:
                f.write(json.dumps(p.to_dict()) + "\n")

        return len(proposals)


def run_phoenix72_scan(hours: float = 72.0) -> str:
    """
    Convenience function to run a Phoenix-72 VOID scan.

    Usage:
        python -c "from arifos_core.memory.void_scanner import run_phoenix72_scan; print(run_phoenix72_scan())"
    """
    scanner = VoidScanner()
    return scanner.run_scan_report(hours=hours)


__all__ = [
    "VoidScanner",
    "ScarCandidate",
    "ScarProposal",
    "run_phoenix72_scan",
]
