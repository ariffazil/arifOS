"""
arifOS Session Ledger (v50.5.17)
Memory Bridge: MCP ↔ VAULT999

The 999-000 Loop:
    999_vault SEALS session → writes to ledger
    000_init OPENS session → reads from ledger

Storage:
    Machine: arifos/mcp/sessions/*.json (transient)
    Human:   VAULT999/BBB_LEDGER/entries/*.md (permanent)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# PATHS
# =============================================================================

# Root of arifOS (go up from arifos/mcp/ → arifos/ → arifOS/)
ARIFOS_ROOT = Path(__file__).parent.parent.parent
VAULT999_PATH = ARIFOS_ROOT / "VAULT999"
BBB_LEDGER_PATH = VAULT999_PATH / "BBB_LEDGER" / "entries"
SESSION_PATH = Path(__file__).parent / "sessions"

# Ensure directories exist
SESSION_PATH.mkdir(parents=True, exist_ok=True)
BBB_LEDGER_PATH.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SESSION DATA
# =============================================================================

@dataclass
class SessionEntry:
    """A sealed session entry for the ledger."""
    session_id: str
    timestamp: str
    verdict: str  # SEAL, SABAR, VOID

    # Trinity Results
    init_result: Dict[str, Any] = field(default_factory=dict)
    genius_result: Dict[str, Any] = field(default_factory=dict)
    act_result: Dict[str, Any] = field(default_factory=dict)
    judge_result: Dict[str, Any] = field(default_factory=dict)

    # Telemetry
    telemetry: Dict[str, Any] = field(default_factory=dict)

    # Cryptographic
    prev_hash: str = ""
    merkle_root: str = ""
    entry_hash: str = ""

    # Context for next session
    context_summary: str = ""
    key_insights: List[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute SHA256 hash of this entry."""
        content = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# SESSION LEDGER
# =============================================================================

class SessionLedger:
    """
    Manages the 999-000 loop session persistence.

    Machine storage: JSON in arifos/mcp/sessions/
    Human storage: Markdown in VAULT999/BBB_LEDGER/entries/
    """

    def __init__(self):
        self.session_path = SESSION_PATH
        self.bbb_path = BBB_LEDGER_PATH
        self._current_session: Optional[SessionEntry] = None
        self._chain_head: Optional[str] = None
        self._load_chain_head()

    def _load_chain_head(self):
        """Load the latest entry hash from chain."""
        chain_file = self.session_path / "chain_head.txt"
        if chain_file.exists():
            self._chain_head = chain_file.read_text().strip()

    def _save_chain_head(self, hash: str):
        """Save the latest entry hash."""
        chain_file = self.session_path / "chain_head.txt"
        chain_file.write_text(hash)
        self._chain_head = hash

    # =========================================================================
    # READ (for 000_init)
    # =========================================================================

    def get_last_session(self) -> Optional[SessionEntry]:
        """
        Get the last sealed session for 000_init to inject.

        Returns:
            SessionEntry if exists, None if first session
        """
        if not self._chain_head:
            return None

        json_file = self.session_path / f"{self._chain_head[:16]}.json"
        if not json_file.exists():
            return None

        data = json.loads(json_file.read_text())
        return SessionEntry(**data)

    def get_context_for_init(self) -> Dict[str, Any]:
        """
        Get context to inject into 000_init.

        Returns:
            Dict with previous session summary, key insights, and continuity data
        """
        last = self.get_last_session()

        if not last:
            return {
                "is_first_session": True,
                "previous_session": None,
                "context_summary": "First session - no prior context",
                "key_insights": [],
                "chain_length": 0
            }

        return {
            "is_first_session": False,
            "previous_session": {
                "session_id": last.session_id,
                "timestamp": last.timestamp,
                "verdict": last.verdict,
                "entry_hash": last.entry_hash
            },
            "context_summary": last.context_summary,
            "key_insights": last.key_insights,
            "chain_length": self._count_chain()
        }

    def _count_chain(self) -> int:
        """Count total entries in chain."""
        return len(list(self.session_path.glob("*.json")))

    # =========================================================================
    # WRITE (for 999_vault)
    # =========================================================================

    def seal_session(
        self,
        session_id: str,
        verdict: str,
        init_result: Dict[str, Any],
        genius_result: Dict[str, Any],
        act_result: Dict[str, Any],
        judge_result: Dict[str, Any],
        telemetry: Dict[str, Any],
        context_summary: str = "",
        key_insights: List[str] = None
    ) -> SessionEntry:
        """
        Seal a session and write to ledger.

        This is called by 999_vault at end of session.

        Args:
            session_id: Current session ID
            verdict: Final verdict (SEAL, SABAR, VOID)
            init_result: Result from 000_init
            genius_result: Result from agi_genius
            act_result: Result from asi_act
            judge_result: Result from apex_judge
            telemetry: Full telemetry data
            context_summary: Summary for next session
            key_insights: Key insights to carry forward

        Returns:
            The sealed SessionEntry
        """
        # Create entry
        entry = SessionEntry(
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            verdict=verdict,
            init_result=init_result,
            genius_result=genius_result,
            act_result=act_result,
            judge_result=judge_result,
            telemetry=telemetry,
            prev_hash=self._chain_head or "GENESIS",
            context_summary=context_summary or self._generate_summary(judge_result),
            key_insights=key_insights or []
        )

        # Compute hashes
        entry.entry_hash = entry.compute_hash()
        entry.merkle_root = self._compute_merkle([
            entry.init_result,
            entry.genius_result,
            entry.act_result,
            entry.judge_result
        ])

        # Write to machine storage (JSON)
        self._write_json(entry)

        # Write to human storage (Markdown in VAULT999)
        self._write_markdown(entry)

        # Update chain head
        self._save_chain_head(entry.entry_hash)

        return entry

    def _write_json(self, entry: SessionEntry):
        """Write entry to JSON file."""
        filename = f"{entry.entry_hash[:16]}.json"
        filepath = self.session_path / filename
        filepath.write_text(json.dumps(asdict(entry), indent=2))

    def _write_markdown(self, entry: SessionEntry):
        """Write entry to Markdown in VAULT999/BBB_LEDGER."""
        filename = f"{entry.timestamp[:10]}_{entry.session_id[:8]}.md"
        filepath = self.bbb_path / filename

        md_content = f"""# Session Seal: {entry.session_id[:8]}

**Timestamp:** {entry.timestamp}
**Verdict:** {entry.verdict}
**Entry Hash:** `{entry.entry_hash[:16]}...`
**Previous:** `{entry.prev_hash[:16]}...`

---

## Summary

{entry.context_summary}

## Key Insights

{chr(10).join(f"- {i}" for i in entry.key_insights) if entry.key_insights else "- No key insights recorded"}

---

## Telemetry

```yaml
verdict: {entry.verdict}
p_truth: {entry.telemetry.get('p_truth', 'N/A')}
TW: {entry.telemetry.get('TW', 'N/A')}
dS: {entry.telemetry.get('dS', 'N/A')}
peace2: {entry.telemetry.get('peace2', 'N/A')}
kappa_r: {entry.telemetry.get('kappa_r', 'N/A')}
omega_0: {entry.telemetry.get('omega_0', 'N/A')}
```

---

## Merkle Root

`{entry.merkle_root}`

---

**DITEMPA BUKAN DIBERI**
"""
        filepath.write_text(md_content)

    def _generate_summary(self, judge_result: Dict[str, Any]) -> str:
        """Generate context summary from judge result."""
        synthesis = judge_result.get("synthesis", "")
        verdict = judge_result.get("verdict", "UNKNOWN")
        return f"Previous session ended with {verdict}. {synthesis[:200]}"

    def _compute_merkle(self, items: List[Dict]) -> str:
        """Compute Merkle root from items."""
        if not items:
            return hashlib.sha256(b"EMPTY").hexdigest()

        hashes = [
            hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()
            for item in items
        ]

        while len(hashes) > 1:
            if len(hashes) % 2:
                hashes.append(hashes[-1])
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]

        return hashes[0]


# =============================================================================
# SINGLETON
# =============================================================================

_ledger: Optional[SessionLedger] = None

def get_ledger() -> SessionLedger:
    """Get the singleton session ledger."""
    global _ledger
    if _ledger is None:
        _ledger = SessionLedger()
    return _ledger


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def inject_memory() -> Dict[str, Any]:
    """
    Called by 000_init to inject previous session context.

    Returns:
        Context dict with previous session data
    """
    return get_ledger().get_context_for_init()


def seal_memory(
    session_id: str,
    verdict: str,
    init_result: Dict,
    genius_result: Dict,
    act_result: Dict,
    judge_result: Dict,
    telemetry: Dict,
    context_summary: str = "",
    key_insights: List[str] = None
) -> Dict[str, Any]:
    """
    Called by 999_vault to seal session.

    Returns:
        Seal result with entry hash and merkle root
    """
    entry = get_ledger().seal_session(
        session_id=session_id,
        verdict=verdict,
        init_result=init_result,
        genius_result=genius_result,
        act_result=act_result,
        judge_result=judge_result,
        telemetry=telemetry,
        context_summary=context_summary,
        key_insights=key_insights
    )

    return {
        "sealed": True,
        "session_id": entry.session_id,
        "entry_hash": entry.entry_hash,
        "merkle_root": entry.merkle_root,
        "timestamp": entry.timestamp,
        "verdict": entry.verdict,
        "prev_hash": entry.prev_hash
    }
