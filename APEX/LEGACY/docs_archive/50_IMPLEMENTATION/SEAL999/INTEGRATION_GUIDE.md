# SEAL-999 Integration Guide

## Replace Old Scattered Files

Below are the old vault file paths that should be DELETED after switching to canonical implementation:

### Files to Delete (Old Chaos)
❌ arifos/core/memory/vault/vault999.py
❌ arifos/core/memory/vault/vault_manager.py
❌ arifos/core/memory/vault/vault_seal_accessor.py
❌ arifos/mcp/_archive/vault999_tac_eureka.py
❌ arifos/spec/v47/999_vault/
❌ arifos/core/vault/

### Files to Keep (Canonical)
✅ SEAL999_CANONICAL/__init__.py
✅ SEAL999_CANONICAL/vault.py
✅ SEAL999_CANONICAL/state.py
✅ SEAL999_CANONICAL/ledger.py
✅ SEAL999_CANONICAL/zkpc.py
✅ SEAL999_CANONICAL/tests/

## Import Path Changes

### Old (Broken):
```python
from arifos.core.memory.vault import SEAL999  # WRONG
from arifos.core.vault import vault            # WRONG
```

### New (Canonical):
```python
from SEAL999_CANONICAL import SEAL999        # CORRECT
from SEAL999_CANONICAL import VaultEntry      # CORRECT
```

## Next Steps

1. Update MCP tools to use canonical SEAL-999
2. Delete old scattered vault implementations
3. Run integration tests
4. Deploy to production
