"""
VaultLogHandler: Permanent Record for arifOS
=============================================

A Python logging handler that ensures all cognitive events,
floor violations, and authority issuances are permanently
persisted to the Vault as structured JSONL.

DITEMPA BUKAN DIBERI - Forged v50.4
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict


class VaultLogHandler(logging.Handler):
    """
    Persists log records to the Vault Audit Trail.
    """
    def __init__(self, vault_path: str = "vault/"):
        super().__init__()
        self.vault_path = vault_path
        self.audit_dir = os.path.join(vault_path, "audit_trail")
        os.makedirs(self.audit_dir, exist_ok=True)

    def emit(self, record: logging.LogRecord):
        """Translate log record to JSONL and write to daily audit file."""
        try:
            msg = self.format(record)

            # Construct audit entry
            entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": msg,
                "module": record.module,
                "line": record.lineno,
            }

            # Incorporate extra attributes if present (e.g. floor_violation, authority_id)
            if hasattr(record, "extra_data"):
                entry["data"] = record.extra_data

            # Daily partitioning (F1 Amanah: granular history)
            date_str = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join(self.audit_dir, f"audit_{date_str}.jsonl")

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        except Exception:
            self.handleError(record)

def setup_vault_logging(vault_path: str = "vault/", level: int = logging.INFO):
    """
    Convenience helper to attach VaultLogHandler to the root logger.
    """
    root_logger = logging.getLogger()

    # Avoid duplicate handlers
    for handler in root_logger.handlers:
        if isinstance(handler, VaultLogHandler):
            return

    handler = VaultLogHandler(vault_path)
    handler.setLevel(level)

    # Generic format for the audit message field
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    logging.info(f"Audit Trail initialised at {vault_path}/audit_trail/")
