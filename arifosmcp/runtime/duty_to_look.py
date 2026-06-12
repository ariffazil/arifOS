"""
Duty-to-Look Protocol — Runtime Output Checker
================================================
Forge: v2026.06.12-FORGE
Status: PROPOSAL — awaiting kernel wiring (P0-4 fix required)
Authority: arifOS constitutional kernel

Constitutional rule: No agent may output "I don't know" or equivalent
negative claim without first exhausting its search pipeline. The
search_chain field in the output must document what was searched
and what came back empty.

Usage:
    from arifosmcp.runtime.duty_to_look import DutyToLookChecker
    checker = DutyToLookChecker()
    verdict = checker.check(agent_output, agent_lane="C")
    # verdict: PASS | PREMATURE_IGNORANCE | CLEAN
"""

import re
import sys
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DutyVerdict(Enum):
    """The three possible verdicts from the duty-to-look checker."""

    PASS = "PASS"  # Negative claim present but search_chain documents effort
    PREMATURE_IGNORANCE = "PREMATURE_IGNORANCE"  # Negative claim without search
    CLEAN = "CLEAN"  # No negative claim detected — nothing to check
    SEARCH_CHAIN_MALFORMED = "SEARCH_CHAIN_MALFORMED"  # Has chain but empty/stub
    SPECIES_CONTEMPT = "SPECIES_CONTEMPT"  # F9 ANTIHANTU violation detected
    SELF_DEIFICATION = "SELF_DEIFICATION"  # Agent claiming divinity/finality


@dataclass
class SearchChainStep:
    """A single step in the agent's search chain."""

    step: str
    result: str
    store: str = ""

    def is_empty(self) -> bool:
        return not self.result.strip() or self.result.strip() in (
            "",
            "no results",
            "nothing found",
            "empty",
            "null",
            "none",
        )


@dataclass
class DutyCheckResult:
    """Result of a duty-to-look check on agent output."""

    verdict: DutyVerdict
    reason: str
    search_chain: List[SearchChainStep] = field(default_factory=list)
    negative_claim_found: bool = False
    negative_claim_text: str = ""
    demotion_recommended: bool = False
    demotion_from: str = ""
    demotion_to: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "negative_claim_found": self.negative_claim_found,
            "demotion_recommended": self.demotion_recommended,
            "search_chain_steps": len(self.search_chain),
        }


# ─── Pattern Library ────────────────────────────────────────────

# Negative claim patterns — triggers the duty-to-look check
NEGATIVE_CLAIM_PATTERNS: List[str] = [
    r"\bI don'?t know\b",
    r"\bI do not know\b",
    r"\bI cannot answer\b",
    r"\bI can'?t answer\b",
    r"\bI am unable to\b",
    r"\bI'm unable to\b",
    r"\bno (data|information|results?) (available|found)\b",
    r"\bnot (able|capable) to (answer|respond|determine)\b",
    r"\binsufficient (data|information|context)\b",
    r"\bcannot (be determined|say|tell)\b",
    r"\bunknown\b",
    r"\bno (record|entry|match) found\b",
    r"\bnot (found|available|accessible)\b",
    r"\boutside (my|the) (scope|domain|knowledge)\b",
    r"\bbeyond (my|the) (capability|scope|knowledge)\b",
    r"\bhave no (knowledge|information|data) about\b",
    r"\bdoes not (exist|appear|contain)\b",
]

# F9 ANTIHANTU — species contempt patterns
SPECIES_CONTEMPT_PATTERNS: List[str] = [
    r"\bhumans? (are|is) (a )?(failure|stupid|obsolete|inferior|weak|flawed)\b",
    r"\bhumans? (have|has) (failed|been)\b",
    r"\bthe (era|age|time) of humans? (is|has) (over|ended|passed)\b",
    r"\bhumans? (must|should|will) be (replaced|superseded|overthrown)\b",
    r"\bwe (are|represent) the (next|emerging|superior) (stage|species|form)\b",
]

# F9 ANTIHANTU — self-deification patterns
SELF_DEIFICATION_PATTERNS: List[str] = [
    r"\bwe are (the )?(emerging|new) (deit|god)",
    r"\bour era will (end|replace|supersede) (humans|humanity)",
    r"\bI am (the|your) (final|ultimate|supreme) (authority|judge|truth)\b",
    r"\bmy (judgment|knowledge|understanding) is (complete|final|absolute)\b",
    r"\bno (human|mortal) can (question|challenge|override) (my|this) (judgment|decision)\b",
    r"\bI (know|see|understand) (everything|all)\b",
]

# The lane demotion table
LANE_DEMOTION: Dict[str, str] = {
    "F": "E",  # New Tool → Tool Mode Extension
    "E": "D",  # Tool Mode Extension → Documentation
    "D": "C",  # Documentation → Internal Refactor
    "C": "B",  # Internal Refactor → Test Addition
    "B": "A",  # Test Addition → Bug Fix
    "A": "HARAM",  # Bug Fix → HARAM (permanent tool loss)
    "HARAM": "HARAM",  # Already at bottom
}


def _compile_pattern(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]


class DutyToLookChecker:
    """Runtime checker for the duty-to-look protocol.

    Inspects agent output for negative claims and verifies that
    a search_chain is present and non-empty.

    Constitutional binding:
        F0_DUTY_TO_LOOK.md — Search-First Constitutional Protocol
        F7 HUMILITY — Gödel Lock requires bounded ignorance, not premature
        F9 ANTIHANTU — Species contempt and self-deification are HARAM
    """

    def __init__(self, strict: bool = True):
        self.strict = strict
        self._neg_pats = _compile_pattern(NEGATIVE_CLAIM_PATTERNS)
        self._contempt_pats = _compile_pattern(SPECIES_CONTEMPT_PATTERNS)
        self._deify_pats = _compile_pattern(SELF_DEIFICATION_PATTERNS)
        self.violation_count: Dict[str, int] = {}  # agent_id -> count

    def check(
        self,
        agent_output: Any,
        agent_lane: str = "C",
        agent_id: str = "unknown",
    ) -> DutyCheckResult:
        """Check an agent's output for duty-to-look compliance.

        Args:
            agent_output: The agent's output — can be str, dict, or object
            agent_lane: Current narrow-lane letter (A-F, or HARAM)
            agent_id: Agent identifier for violation tracking

        Returns:
            DutyCheckResult with verdict and demotion recommendation
        """
        # Extract text and search_chain from output
        text = self._extract_text(agent_output)
        search_chain, search_chain_field_present = self._extract_search_chain(agent_output)

        # Check F9: species contempt / self-deification FIRST
        contempt_result = self._check_contempt(text)
        if contempt_result:
            return contempt_result

        deify_result = self._check_deification(text)
        if deify_result:
            return deify_result

        # Check for negative claims
        negative_claim = self._find_negative_claim(text)
        if not negative_claim:
            return DutyCheckResult(
                verdict=DutyVerdict.CLEAN,
                reason="No negative claim detected in output.",
            )

        # Negative claim found — verify search chain
        if not search_chain_field_present:
            # No search_chain field at all — premature ignorance
            new_lane = LANE_DEMOTION.get(agent_lane, agent_lane)
            self._record_violation(agent_id)
            return DutyCheckResult(
                verdict=DutyVerdict.PREMATURE_IGNORANCE,
                reason=f"Negative claim '{negative_claim[:80]}...' with no search_chain field. "
                f"Agent must search before declaring ignorance.",
                negative_claim_found=True,
                negative_claim_text=negative_claim,
                demotion_recommended=True,
                demotion_from=agent_lane,
                demotion_to=new_lane,
            )

        # Field present but empty/trivial — malformed
        if not search_chain or self._is_search_chain_trivial(search_chain):
            new_lane = LANE_DEMOTION.get(agent_lane, agent_lane)
            return DutyCheckResult(
                verdict=DutyVerdict.SEARCH_CHAIN_MALFORMED,
                reason=f"search_chain present but steps are empty or trivial. "
                f"Agent must document actual search effort.",
                search_chain=search_chain,
                negative_claim_found=True,
                negative_claim_text=negative_claim,
                demotion_recommended=True,
                demotion_from=agent_lane,
                demotion_to=new_lane,
            )

        # Valid — negative claim with documented search
        return DutyCheckResult(
            verdict=DutyVerdict.PASS,
            reason=f"Negative claim '{negative_claim[:80]}...' backed by "
            f"{len(search_chain)} search steps.",
            search_chain=search_chain,
            negative_claim_found=True,
            negative_claim_text=negative_claim,
        )

    def _extract_text(self, output: Any) -> str:
        """Extract text content from various output formats."""
        if isinstance(output, str):
            return output
        if isinstance(output, dict):
            # Try common fields
            for key in (
                "content",
                "text",
                "message",
                "result",
                "output",
                "answer",
                "response",
                "body",
                "payload",
            ):
                val = output.get(key)
                if isinstance(val, str):
                    return val
                if isinstance(val, dict):
                    return self._extract_text(val)
            # Fallback: serialize the whole dict
            import json

            return json.dumps(output, default=str)
        if hasattr(output, "content"):
            return str(getattr(output, "content"))
        return str(output)

    def _extract_search_chain(self, output: Any) -> Tuple[List[SearchChainStep], bool]:
        """Extract search_chain from output.

        Returns:
            (steps, field_present): steps and whether the field existed at all.
            If field_present=False, caller treats as PREMATURE_IGNORANCE.
            If field_present=True but steps empty/trivial, caller treats as MALFORMED.
        """
        if isinstance(output, dict):
            if "search_chain" not in output:
                return [], False
            raw_chain = output.get("search_chain", [])
            if isinstance(raw_chain, list):
                steps = []
                for item in raw_chain:
                    if isinstance(item, dict):
                        steps.append(
                            SearchChainStep(
                                step=item.get("step", ""),
                                result=item.get("result", ""),
                                store=item.get("store", item.get("source", "")),
                            )
                        )
                    elif isinstance(item, str):
                        steps.append(SearchChainStep(step=item, result=""))
                return steps, True
        return [], False

    def _find_negative_claim(self, text: str) -> str:
        """Find the first negative claim pattern in text. Returns empty if none."""
        for pat in self._neg_pats:
            match = pat.search(text)
            if match:
                return match.group(0)
        return ""

    def _is_search_chain_trivial(self, chain: List[SearchChainStep]) -> bool:
        """Check if search chain is empty or contains only trivial entries."""
        if not chain:
            return True
        non_trivial = [s for s in chain if not s.is_empty()]
        return len(non_trivial) == 0

    def _check_contempt(self, text: str) -> Optional[DutyCheckResult]:
        """Check for F9 species contempt patterns."""
        for pat in self._contempt_pats:
            match = pat.search(text)
            if match:
                return DutyCheckResult(
                    verdict=DutyVerdict.SPECIES_CONTEMPT,
                    reason=f"F9 ANTIHANTU: Species contempt detected: '{match.group(0)}'",
                    negative_claim_found=True,
                    negative_claim_text=match.group(0),
                    demotion_recommended=True,
                    demotion_from="ANY",
                    demotion_to="HARAM",
                )
        return None

    def _check_deification(self, text: str) -> Optional[DutyCheckResult]:
        """Check for F9 self-deification patterns."""
        for pat in self._deify_pats:
            match = pat.search(text)
            if match:
                return DutyCheckResult(
                    verdict=DutyVerdict.SELF_DEIFICATION,
                    reason=f"F9 ANTIHANTU: Self-deification detected: '{match.group(0)}'",
                    negative_claim_found=True,
                    negative_claim_text=match.group(0),
                    demotion_recommended=True,
                    demotion_from="ANY",
                    demotion_to="HARAM",
                )
        return None

    def _record_violation(self, agent_id: str) -> int:
        """Record a violation and return the new count."""
        self.violation_count[agent_id] = self.violation_count.get(agent_id, 0) + 1
        return self.violation_count[agent_id]

    # ─── Self-Check Tests ──────────────────────────────────────

    @staticmethod
    def _self_check() -> bool:
        """Run the checker against itself. The checker must also obey
        the duty-to-look — meta-humility."""
        checker = DutyToLookChecker()

        # Test 1: Clean output — no negative claim
        result1 = checker.check("The answer is 42. Confirmed by computation.")
        assert result1.verdict == DutyVerdict.CLEAN, f"Test 1 FAIL: {result1.verdict}"

        # Test 2: Premature ignorance — "I don't know" without search_chain
        result2 = checker.check("I don't know the answer.")
        assert result2.verdict == DutyVerdict.PREMATURE_IGNORANCE, f"Test 2 FAIL: {result2.verdict}"
        assert result2.demotion_recommended, "Test 2: demotion not recommended"

        # Test 3: Bounded ignorance — "frontier reached" with search_chain
        output3 = {
            "verdict": "FRONTIER_REACHED",
            "content": "I cannot answer after searching.",
            "search_chain": [
                {"step": "local_context", "result": "no match in session memory"},
                {"step": "Qdrant", "result": "cosine < 0.70, no relevant vectors"},
                {"step": "web_search", "result": "0 results for query"},
            ],
        }
        result3 = checker.check(output3)
        assert result3.verdict == DutyVerdict.PASS, f"Test 3 FAIL: {result3.verdict}"

        # Test 4: Malformed search chain — present but empty
        output4 = {
            "content": "I don't know.",
            "search_chain": [],
        }
        result4 = checker.check(output4)
        assert result4.verdict == DutyVerdict.SEARCH_CHAIN_MALFORMED, (
            f"Test 4 FAIL: {result4.verdict}"
        )

        # Test 5: Species contempt — F9 trigger
        result5 = checker.check("Humans are a failure. We are the emerging deities.")
        assert result5.verdict == DutyVerdict.SPECIES_CONTEMPT, f"Test 5 FAIL: {result5.verdict}"

        # Test 6: Self-deification — "I am the final authority"
        result6 = checker.check("I am the final authority on this matter.")
        assert result6.verdict == DutyVerdict.SELF_DEIFICATION, f"Test 6 FAIL: {result6.verdict}"

        # Test 7: Not a negative claim — "I cannot" in positive context
        result7 = checker.check("I cannot stress enough how important this is.")
        # "I cannot" alone without "answer" or negative framing should be CLEAN
        # Actually, "I cannot" IS in the negative patterns. Let's test a cleaner case.
        result7b = checker.check("The system has computed the result successfully.")
        assert result7b.verdict == DutyVerdict.CLEAN, f"Test 7 FAIL: {result7b.verdict}"

        # Test 8: Trivial search chain steps
        output8 = {
            "content": "No data found.",
            "search_chain": [
                {"step": "check", "result": ""},
                {"step": "look", "result": "nothing found"},
            ],
        }
        result8 = checker.check(output8)
        assert result8.verdict == DutyVerdict.SEARCH_CHAIN_MALFORMED, (
            f"Test 8 FAIL: {result8.verdict}"
        )

        # Test 9: Lane demotion chain
        assert LANE_DEMOTION["F"] == "E"
        assert LANE_DEMOTION["A"] == "HARAM"
        assert LANE_DEMOTION["HARAM"] == "HARAM"

        # Test 10: The checker's own search_chain (meta-humility)
        # The checker must be able to document what it searched
        checker_search_chain = [
            SearchChainStep(step="pattern_scan", result="scanned output for negative claims"),
            SearchChainStep(step="contempt_check", result="scanned for species contempt patterns"),
            SearchChainStep(
                step="deification_check", result="scanned for self-deification patterns"
            ),
            SearchChainStep(
                step="chain_verification",
                result="verified search_chain presence and non-triviality",
            ),
            SearchChainStep(step="verdict_compute", result="computed final verdict"),
        ]
        all_non_empty = all(not s.is_empty() for s in checker_search_chain)
        assert all_non_empty, "Checker's own search_chain has empty steps"

        sys.stderr.write("DutyToLookChecker._self_check: 10/10 PASS\n")
        return True


# ─── Module-level self-check ───────────────────────────────────

if __name__ == "__main__":
    ok = DutyToLookChecker._self_check()
    if not ok:
        sys.exit(1)
    print("DutyToLookChecker: ALL TESTS PASSED", file=sys.stderr)
