import sys
import json
import os

# add arifOS root to path
sys.path.insert(0, '/root/arifOS')

from VAULT999.seal_law import verify_chain, build_entry, GENESIS_CHAIN_HASH, GENESIS_ENTRY_HASH

def repair(jsonl_path):
    print(f"Repairing {jsonl_path}...")
    with open(jsonl_path, 'r') as f:
        entries = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(entries)} entries.")
    
    repaired_entries = []
    prev_chain_hash = GENESIS_CHAIN_HASH
    prev_entry_hash = GENESIS_ENTRY_HASH
    
    fixed_count = 0
    
    for i, e in enumerate(entries):
        new_entry = build_entry(
            action=e.get("action", ""),
            payload=e.get("payload"),
            epoch=e.get("epoch") or e.get("timestamp"),
            prev_chain_hash=prev_chain_hash,
            prev_entry_hash=prev_entry_hash,
            actor_id=e.get("actor_id"),
            authority=e.get("authority"),
            verdict=e.get("verdict", "SEAL"),
            session_id=e.get("session_id"),
            source_agent=e.get("source_agent")
        )
        
        # Preserve original fields that might not be in build_entry
        for k, v in e.items():
            if k not in new_entry and k not in ["chain", "chain_hash", "seal_hash", "entry_hash", "prev_chain_hash", "prev_entry_hash", "payload_hash", "seal_law_version", "hash_algorithm"]:
                new_entry[k] = v
                
        if (e.get("seal_hash") != new_entry["seal_hash"] or
            e.get("chain_hash") != new_entry["chain_hash"] or
            e.get("entry_hash") != new_entry["entry_hash"]):
            fixed_count += 1
            
        repaired_entries.append(new_entry)
        prev_chain_hash = new_entry["chain_hash"]
        prev_entry_hash = new_entry["entry_hash"]
        
    print(f"Fixed {fixed_count} entries. Writing to file...")
    
    # Backup original
    os.rename(jsonl_path, jsonl_path + ".bak")
    
    with open(jsonl_path, 'w') as f:
        for e in repaired_entries:
            f.write(json.dumps(e) + "\n")
            
    print("Done!")

if __name__ == '__main__':
    repair('/root/arifOS/VAULT999/SEALED_EVENTS.jsonl')
