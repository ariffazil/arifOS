# -*- coding: utf-8 -*-
"""
Memory Tower - EUREKA Sieve & TTL (Phase 9.4)

Constitutional Alignment: F4 (Clarity - Entropy Reduction)
Authority: Vault (999)

Purpose:
- Filter memory storage based on Novelty (Genius) and Consensus (Tri-Witness)
- Assign storage bands L0-L5 with appropriate TTLs
- Prevent entropy buildup (Digital Hoarding)
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict


class EurekaSieve:
    """
    Implements the EUREKA Sieve for memory tiering.
    """

    BANDS = {
        "L0_GENESIS": {"ttl": None, "desc": "Immutable Canon"},
        "L1_ARCHIVE": {"ttl": None, "desc": "Permanent Storage"},
        "L2_WITNESS": {"ttl": 90, "desc": "Verified Facts (90 days)"},
        "L3_REFLECT": {"ttl": 30, "desc": "Reflective buffer (30 days)"},
        "L4_SESSION": {"ttl": 7, "desc": "Session Context (7 days)"},
        "L5_VOID":    {"ttl": 1, "desc": "Ephemeral/Trash (24h)"}
    }

    def assess_ttl(
        self,
        novelty_score: float,
        tri_witness_consensus: float,
        verdict: str,
        constitutional_pass: bool
    ) -> Dict[str, Any]:
        """
        Assess memory TTL and Band based on input metrics.

        Args:
            novelty_score: 0.0-1.0 (How new/insightful is this?)
            tri_witness_consensus: 0.0-1.0 (Agreement level)
            verdict: SEAL, PARTIAL, VOID, etc.
            constitutional_pass: True/False

        Returns:
            Dict with memory_band, ttl_days, expiry_date
        """

        # Rule 1: Constitutional Failures -> L5 VOID
        if not constitutional_pass or verdict == "VOID":
            band = "L5_VOID"

        # Rule 2: High Stakes / Sealed / High Consensus -> L1 ARCHIVE
        elif verdict == "SEAL" and tri_witness_consensus > 0.98:
            band = "L1_ARCHIVE"

        # Rule 3: High Novelty or Moderate Consensus -> L2 WITNESS
        elif novelty_score > 0.8 or tri_witness_consensus > 0.90:
            band = "L2_WITNESS"

        # Rule 4: Moderate Novelty -> L3 REFLECT
        elif novelty_score > 0.5:
            band = "L3_REFLECT"

        # Rule 5: Standard Interaction -> L4 SESSION
        else:
            band = "L4_SESSION"

        # Calculate expiry
        ttl_days = self.BANDS[band]["ttl"]
        if ttl_days is None:
            expiry = "PERMANENT"
        else:
            # TTL in days
            expiry = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).isoformat()

        return {
            "memory_band": band,
            "description": self.BANDS[band]["desc"],
            "ttl_days": ttl_days,
            "expiry": expiry,
            "metrics": {
                "novelty": novelty_score,
                "consensus": tri_witness_consensus,
                "verdict": verdict
            }
        }

# Singleton Instance
EUREKA_SIEVE = EurekaSieve()
