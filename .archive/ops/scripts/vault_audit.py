
import asyncio
import sys
from pathlib import Path

# Add the arifosmcp directory to the path so we can import the vault logic
sys.path.append("/root/arifOS")

from core.organs._4_vault import verify_vault_ledger

VAULT_PATH = Path("/root/arifOS/VAULT999/vault999.jsonl")

async def run_audit():
    print(f"--- VAULT999 Integrity Audit ---")
    print(f"Target: {VAULT_PATH}")
    
    if not VAULT_PATH.exists():
        print("Error: Vault file not found.")
        return

    ok, reason = verify_vault_ledger(VAULT_PATH)
    
    if ok:
        print("Result: SEAL (Integrity Verified)")
        print("Merkle Chain: UNBROKEN")
    else:
        print(f"Result: VOID (Integrity Breach Detected)")
        print(f"Reason: {reason}")

if __name__ == "__main__":
    asyncio.run(run_audit())
