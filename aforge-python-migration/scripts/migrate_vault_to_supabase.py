import json
import os
from pathlib import Path
from datetime import datetime, timezone
from supabase import create_client

# 1. Load Credentials
VAULT_ENV = Path("/root/.secrets/vault.env")
creds = {}
if VAULT_ENV.exists():
    with open(VAULT_ENV) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                creds[k] = v

SUPABASE_URL = creds.get("SUPABASE_URL")
SUPABASE_KEY = creds.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase credentials in vault.env")
    exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Migration Logic
JSONL_PATH = Path("/root/VAULT999/SEALED_EVENTS.jsonl")
if not JSONL_PATH.exists():
    print(f"Error: {JSONL_PATH} not found")
    exit(1)

print(f"Starting migration of {JSONL_PATH} to Supabase...")

events_dict = {} # Use dict to filter duplicates locally by seal_id
prev_hash = "0" * 64

with open(JSONL_PATH, "r") as f:
    for line in f:
        if not line.strip(): continue
        try:
            raw = json.loads(line)
            
            seal_id = raw.get("sealId") or raw.get("event_id") or f"MIGRATED_{datetime.now().timestamp()}_{os.urandom(4).hex()}"
            agent_id = raw.get("agent") or raw.get("operator") or "MIGRATED_AGENT"
            action = raw.get("action") or raw.get("event_type") or "MIGRATED_ACTION"
            epoch_str = raw.get("timestamp") or datetime.now(timezone.utc).isoformat()
            current_event_hash = raw.get("hash") or "MIGRATED_DATA"
            
            event = {
                "seal_id": seal_id,
                "prev_hash": prev_hash,
                "agent_id": str(agent_id),
                "action": str(action),
                "payload": raw,
                "confidence": 1.0,
                "epoch": epoch_str
            }
            
            # Store in dict to handle local duplicates
            events_dict[seal_id] = event
            
            # Update prev_hash
            prev_hash = current_event_hash if len(current_event_hash) == 64 else prev_hash
            
        except Exception as e:
            print(f"Skipping malformed line: {e}")

# 3. Execute Insert (Row-by-row for maximum safety against partial failures)
events_list = list(events_dict.values())
if events_list:
    print(f"Migrating {len(events_list)} unique events...")
    success_count = 0
    for event in events_list:
        try:
            sb.table("arifosmcp_vault_seals").upsert(event, on_conflict="seal_id").execute()
            success_count += 1
        except Exception as e:
            print(f"Failed to migrate event {event['seal_id']}: {e}")
    
    print(f"Successfully migrated {success_count}/{len(events_list)} events.")
else:
    print("No unique events found to migrate.")
