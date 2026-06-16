"""
Irreversible Action Receipt — 888_HOLD trigger.

Per F1 AMANAH: any irreversible action must be explicitly approved.
This receipt is generated BEFORE the action and sealed AFTER.

Used by: arif_vault_seal, hostinger-vps, Caddy reload, secret rotation.
"""

from __future__ import annotations

import time
from typing import Literal, Optional

from pydantic import BaseModel, Field


class IrreversibleActionReceipt(BaseModel):
    """Receipt for an irreversible action requiring 888_HOLD."""

    action_id: str
    action_class: Literal["DESTRUCTIVE", "OVERWRITE", "EXTERNAL", "CREDENTIAL", "VAULT_WRITE"]
    action_description: str
    actor_id: str
    session_id: Optional[str] = None
    blast_radius: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    reversible: bool = False
    human_ack: bool = False  # Must be True to proceed
    human_ack_signature: Optional[str] = None
    proposed_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    authorized_at: Optional[str] = None
    executed_at: Optional[str] = None
    vault_seal_id: Optional[int] = None
    rollback_plan: str = ""
    pre_state_hash: Optional[str] = None
    post_state_hash: Optional[str] = None

    def is_authorized(self) -> bool:
        return self.human_ack and self.human_ack_signature is not None
