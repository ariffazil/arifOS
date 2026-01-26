# SEAL999 Usage Guide

## Import and Use

```python
from SEAL999 import SEAL999, VaultEntry, VaultConfig

# Initialize SEAL999
vault = SEAL999()

# Create a vault entry
from datetime import datetime

entry = VaultEntry(
    entry_id="session_001_888",
    session_id="session_001",
    stage=888,
    timestamp=datetime.utcnow(),
    verdict="SEAL",
    merkle_root="a1b2c3d4e5f6",
    floor_scores={"F12_Injection": 0.15, "F2_Truth": 0.99}
)

# Seal the entry (writes to VAULT999/)
merkle_root = vault.seal_entry(entry)

# Verify an entry
is_valid = vault.verify_entry(entry)

# Get session ledger
ledger = vault.get_session_ledger("session_001")
```

## Storage Structure

SEAL999 writes operational data to `VAULT999/`:
- **BBB_LEDGER/** - Session entries and hash chains
- **L0_HOT/ through L5_ETERNAL/** - Cooling tier storage
- **entropy/** - ΔS measurements
- **constitutional_status.json** - Live status

## Cooling Tiers

Entries are auto-assigned to tiers based on verdict:
- **L5_ETERNAL** - SEAL + high genius (never expires)
- **L4_MONTHLY** - PARTIAL + high empathy (30 days)
- **L3_WEEKLY** - SABAR verdicts (7 days)
- **L2_PHOENIX** - Standard SEAL (72 hours)
- **L1_DAILY** - Daily retention (24 hours)
- **L0_HOT** - Hot storage (30 minutes)

VOID verdicts are **never stored**.
