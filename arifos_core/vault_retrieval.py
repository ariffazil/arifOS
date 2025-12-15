"""
arifos_core.vault_retrieval - BACKWARD COMPATIBILITY SHIM (v42)
Moved to: arifos_core/governance/vault_retrieval.py
This shim will be removed in v43.0.
"""
from arifos_core.governance.vault_retrieval import *
from arifos_core.governance.vault_retrieval import (
    _load_ledger,
    _entry_text_blob,
    _entry_tags,
    _simple_keyword_score,
    _matches_types,
    _matches_tags,
)
