"""
arifOS Canonical Codes
Source of Truth: REPO_STRUCTURE_v49.md
"""

from enum import Enum


class Stage(str, Enum):
    INIT_000 = "000_INIT"
    SENSE_111 = "111_SENSE"
    THINK_222 = "222_THINK"
    ATLAS_333 = "333_ATLAS"
    ALIGN_444 = "444_ALIGN"
    EMPATHY_555 = "555_EMPATHY"
    BRIDGE_666 = "666_BRIDGE"
    EUREKA_777 = "777_EUREKA"
    JUDGE_888 = "888_JUDGE"
    PROOF_889 = "889_PROOF"
    VAULT_999 = "999_VAULT"

class Verdict(str, Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    VOID = "VOID"
    HOLD_888 = "888_HOLD"

class Role(str, Enum):
    ARCHITECT = "Δ"
    ENGINEER = "Ω"
    AUDITOR = "Ψ"
    VALIDATOR = "Κ"
