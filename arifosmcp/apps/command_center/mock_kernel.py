"""Mock kernel data for arifOS Command Center v0.1.

All data is synthetic. No real systems are queried.
"""

from __future__ import annotations

from arifosmcp.apps.command_center.models import VaultEntry

MOCK_VAULT_ENTRIES: list[VaultEntry] = [
    VaultEntry(
        id="VAULT-MOCK-001",
        type="session_init",
        permanent=False,
        note="Mock vault entry for v0.1",
    ),
    VaultEntry(
        id="VAULT-MOCK-002",
        type="judge_verdict",
        permanent=False,
        note="Simulated HOLD verdict on empty candidate",
    ),
    VaultEntry(
        id="VAULT-MOCK-003",
        type="forge_dry_run",
        permanent=False,
        note="Simulated dry-run of hello-world manifest",
    ),
]
