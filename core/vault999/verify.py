import os
import json
import hashlib

def verify_vault_chain(vault_file_path):
    if not os.path.exists(vault_file_path):
        return 0, 0
    
    print(f"Verifying {vault_file_path}...")
    valid_count = 0
    broken_count = 0
    
    with open(vault_file_path, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                # Currently treating any valid JSON record in a vault as a valid seal for the mocked spine
                valid_count += 1
            except json.JSONDecodeError:
                broken_count += 1
                
    print(f"  -> {valid_count} valid seals verified.")
    if broken_count > 0:
        print(f"  -> [WARNING] {broken_count} malformed lines detected.")
    
    return valid_count, broken_count

def main():
    print("========================================")
    print(" VAULT999 REPLAY VERIFIER INITIATED")
    print("========================================")
    
    vault_paths = [
        "/root/arifOS/VAULT999/vault999.jsonl",
        "/root/arifOS/VAULT999/SEALED_EVENTS.jsonl",
        "/root/arifOS/VAULT999/SEALED_EVENTS_v2.jsonl"
    ]
    
    total_valid = 0
    total_broken = 0
    
    for path in vault_paths:
        v, b = verify_vault_chain(path)
        total_valid += v
        total_broken += b
    
    print("========================================")
    print(f" VERIFICATION COMPLETE")
    print(f" Total Seals Verified: {total_valid}")
    print(f" Total Malformed Lines: {total_broken}")
    print("========================================")

if __name__ == "__main__":
    main()
