#!/usr/bin/env python3
"""
review_operator — CLI review tool for CLI-L2 (cooling_queue) ratification
=====================================================================
Role: Arif reviews pending 888_HOLD items and ratifies via CLI
Interface: Terminal CLI (phase 1)

Author: arifOS_bot
Date: 2026-04-18
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Optional

import asyncpg

# ============================================================
# CONFIG
# ============================================================
DB_DSN = os.getenv(
    "VAULT999_DB",
    "postgresql://vault_writer_svc:VaultWriterSecret2026!@72.62.71.199:5432/arifos_vault"
)
TELEMETRY_SEQ = {"value": 0}

def get_next_sig_seq() -> int:
    TELEMETRY_SEQ["value"] += 1
    return TELEMETRY_SEQ["value"]

def format_sig(seq: int) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"SIG_ARIF_TELEMETRY_{date}_{seq:02d}"

# ============================================================
# DB CONNECTION
# ============================================================
async def get_conn():
    return await asyncpg.connect(DB_DSN)

# ============================================================
# COMMANDS
# ============================================================
async def cmd_list_pending(conn):
    """List all pending 888_HOLD items"""
    rows = await conn.fetch("""
        SELECT 
            id::text, action_type, risk_class, judge_verdict,
            proposal_hash, session_id, created_at, hold_initiated_at,
            (SELECT COUNT(*) FROM cooling_queue WHERE status = 'awaiting_human') as pending_total
        FROM cooling_queue 
        WHERE status = 'awaiting_human'
        ORDER BY 
            CASE risk_class WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END,
            created_at ASC
    """)
    
    if not rows:
        print("✅ No pending 888_HOLD items")
        return

    total = rows[0]["pending_total"]
    print(f"\n{'='*60}")
    print(f"  888_HOLD PENDING — {total} items")
    print(f"{'='*60}\n")
    
    for i, r in enumerate(rows, 1):
        age = (datetime.now(timezone.utc) - r["created_at"]).total_seconds()
        age_str = f"{int(age//60)}m ago" if age < 3600 else f"{int(age//3600)}h ago"
        
        risk_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(r["risk_class"], "⚪")
        
        print(f"  [{i}] {risk_emoji} {r['action_type']}")
        print(f"      risk={r['risk_class']} | verdict={r['judge_verdict']} | age={age_str}")
        print(f"      id={r['id'][:8]}... | session={r['session_id'] or 'n/a'}")
        print()

async def cmd_inspect(conn, cooling_id: str):
    """Inspect a single cooling_queue record"""
    row = await conn.fetchrow("""
        SELECT 
            id::text, session_id, agent_id, action_type, prospect_id,
            proposal_hash, judge_verdict, risk_class, status,
            payload::text as payload_raw, created_at, hold_initiated_at,
            reviewed_by, reviewed_at, review_notes, human_signature
        FROM cooling_queue WHERE id = $1
    """, cooling_id)
    
    if not row:
        print(f"❌ cooling_id not found: {cooling_id}")
        return

    print(f"\n{'='*60}")
    print(f"  INSPECT: {cooling_id}")
    print(f"{'='*60}")
    print(f"  action_type:    {row['action_type']}")
    print(f"  agent_id:       {row['agent_id']}")
    print(f"  prospect_id:    {row['prospect_id'] or 'n/a'}")
    print(f"  risk_class:     {row['risk_class']}")
    print(f"  judge_verdict:  {row['judge_verdict']}")
    print(f"  status:         {row['status']}")
    print(f"  session_id:    {row['session_id'] or 'n/a'}")
    print(f"  proposal_hash:  {row['proposal_hash'] or 'n/a'}")
    print(f"  hold_initiated: {row['hold_initiated_at']}")
    print(f"  created_at:     {row['created_at']}")
    
    if row["reviewed_by"]:
        print(f"  reviewed_by:    {row['reviewed_by']}")
        print(f"  reviewed_at:    {row['reviewed_at']}")
        print(f"  review_notes:   {row['review_notes'] or 'n/a'}")
        print(f"  human_signature:{row['human_signature'] or 'n/a'}")
    
    print(f"\n  payload:")
    try:
        payload = json.loads(row["payload_raw"]) if row["payload_raw"] else {}
        for k, v in payload.items():
            vstr = str(v)[:200]
            print(f"    {k}: {vstr}")
    except:
        print(f"    {row['payload_raw'][:500]}")
    print()

async def cmd_ratify(conn, cooling_id: str, decision: str, reason: str, irr_ack: bool = False):
    """Ratify (SEAL or VOID) a cooling_queue record"""
    # Validate decision
    if decision not in ("SEAL", "VOID"):
        print(f"❌ decision must be SEAL or VOID, got: {decision}")
        return

    # Check record exists and is pending
    row = await conn.fetchrow(
        "SELECT id, status, action_type, payload, proposal_hash, session_id FROM cooling_queue WHERE id = $1",
        cooling_id
    )
    if not row:
        print(f"❌ cooling_id not found: {cooling_id}")
        return
    if row["status"] != "awaiting_human":
        print(f"❌ Record already {row['status']} — cannot ratify")
        return

    # Build signature
    sig_seq = get_next_sig_seq()
    human_signature = format_sig(sig_seq)
    ratified_at = datetime.now(timezone.utc).isoformat()

    # Write human_reviews first
    review_id = await conn.fetchval("""
        INSERT INTO human_reviews (cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at)
        VALUES ($1, 'arif', $2, $3, $4, $5)
        RETURNING review_id::text
    """, cooling_id, decision, reason, human_signature, ratified_at)

    if decision == "VOID":
        # Update cooling_queue only — no vault_seals
        await conn.execute("""
            UPDATE cooling_queue 
            SET status = 'voided', reviewed_by = 'arif', reviewed_at = $1, 
                human_signature = $2, review_notes = $3
            WHERE id = $4
        """, ratified_at, human_signature, reason, cooling_id)
        print(f"✅ VOID: cooling_id={cooling_id}, review_id={review_id}")
        return

    # SEAL path — write to vault_seals via vault_writer
    # Get prev seal
    prev_row = await conn.fetchrow(
        "SELECT id, seal_hash FROM vault_seals ORDER BY ratified_at DESC LIMIT 1"
    )
    prev_seal_id = prev_row["id"] if prev_row else None
    prev_seal_hash = prev_row["seal_hash"] if prev_row else None

    # Compute hashes
    import hashlib
    import json as jsonmod
    
    payload_dict = json.loads(row["payload"]) if isinstance(row["payload"], str) else dict(row["payload"])
    
    canonical = {
        "agent_id": "arifOS-E",
        "action": row["action_type"],
        "payload": payload_dict,
        "epoch": ratified_at,
        "verdict": "SEAL",
        "human_ratifier": "arif",
        "human_signature": human_signature,
        "ratified_at": ratified_at,
        "cooling_id": str(cooling_id),
        "cli_proposal_hash": row["proposal_hash"]
    }
    seal_hash = hashlib.sha256(
        jsonmod.dumps(canonical, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    
    chain_input = "SEAL" + human_signature + ratified_at + (prev_seal_hash or "GENESIS")
    chain_hash = hashlib.sha256(chain_input.encode("utf-8")).hexdigest()

    # Insert vault_seals
    seal_row = await conn.fetchrow("""
        INSERT INTO vault_seals (
            seal_hash, chain_hash, prev_seal_id,
            cooling_id, cli_proposal_hash, session_id,
            agent_id, action, payload, epoch,
            verdict, human_ratifier, human_signature, ratified_at,
            irreversibility_ack, provenance_tag, tags, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, 'human', $16, $17)
        RETURNING id::text, seal_hash
    """,
        seal_hash, chain_hash, prev_seal_id,
        cooling_id, row["proposal_hash"], row["session_id"],
        "arifOS-E", row["action_type"], jsonmod.dumps(payload_dict), ratified_at,
        "SEAL", "arif", human_signature, ratified_at,
        irr_ack, [row["action_type"], "ratified"],
        jsonmod.dumps({"review_reason": reason})
    )

    # Insert vault999_witness
    await conn.execute("""
        INSERT INTO vault999_witness (ledger_id, human_witness, ai_witness, evidence_witness, w_score, metadata)
        VALUES ($1, true, true, true, 1.00, $2)
    """, seal_row["id"], jsonmod.dumps({"review_reason": reason}))

    # Update cooling_queue
    await conn.execute("""
        UPDATE cooling_queue 
        SET status = 'sealed', reviewed_by = 'arif', reviewed_at = $1, 
            human_signature = $2, review_notes = $3
        WHERE id = $4
    """, ratified_at, human_signature, reason, cooling_id)

    print(f"✅ SEAL: cooling_id={cooling_id}")
    print(f"   seal_id={seal_row['id'][:8]}...")
    print(f"   seal_hash={seal_hash[:16]}...")
    print(f"   chain_hash={chain_hash[:16]}...")
    print(f"   human_signature={human_signature}")
    print(f"   review_id={review_id}")

async def cmd_recent_reviews(conn, limit: int = 10):
    """List recent human_reviews"""
    rows = await conn.fetch("""
        SELECT review_id::text, cooling_id::text, reviewer_id, decision, 
               reason, human_signature, reviewed_at
        FROM human_reviews 
        ORDER BY reviewed_at DESC 
        LIMIT $1
    """, limit)
    
    if not rows:
        print("No reviews yet")
        return
    
    print(f"\nRecent reviews:")
    for r in rows:
        print(f"  [{r['decision']}] {r['reviewed_at']} | {r['human_signature']} | {r['reason'][:60]}...")

# ============================================================
# MAIN
# ============================================================
async def main():
    parser = argparse.ArgumentParser(description="review_operator — CLI for 888_HOLD ratification")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List pending 888_HOLD items")
    sub.add_parser("recent", help="Recent reviews")
    
    insp = sub.add_parser("inspect", help="Inspect a cooling_queue record")
    insp.add_argument("cooling_id", help="cooling_queue UUID")
    
    rat = sub.add_parser("ratify", help="Ratify a cooling_queue record")
    rat.add_argument("cooling_id", help="cooling_queue UUID")
    rat.add_argument("decision", help="SEAL or VOID")
    rat.add_argument("--reason", "-r", default="", help="Review reason")
    rat.add_argument("--irr-ack", action="store_true", help="Set irreversibility_ack=true")

    args = parser.parse_args()

    conn = await get_conn()
    try:
        if args.cmd == "list":
            await cmd_list_pending(conn)
        elif args.cmd == "inspect":
            await cmd_inspect(conn, args.cooling_id)
        elif args.cmd == "ratify":
            await cmd_ratify(conn, args.cooling_id, args.decision.upper(), args.reason, args.irr_ack)
        elif args.cmd == "recent":
            await cmd_recent_reviews(conn)
    finally:
        await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())