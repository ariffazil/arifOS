#!/usr/bin/env python3
"""
AAA Cockpit — Unified Read Dashboard
====================================
Queries both production (public.arifosmcp_*) and Phase 1 design (s000/s999)
namespaces via the unified AAA views, and prints a clean summary.

Usage:
    python3 scripts/aaa_cockpit.py              # full summary
    python3 scripts/aaa_cockpit.py --seals     # seals only
    python3 scripts/aaa_cockpit.py --tool-calls # tool calls only
    python3 scripts/aaa_cockpit.py --summary    # namespace row counts only
"""

import argparse
import asyncio
import os
from datetime import datetime, timezone

import asyncpg

POOL_URL = os.getenv(
    "VAULT999_DB",
    "postgresql://postgres.utbmmjmbolmuahwixjqc:cWZ228S72IaC9UzRD5i7UHh8s8NUbaXT"
    "@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres",
)


async def fetch_rows(conn, query, params=None):
    try:
        return await conn.fetch(query, *params if params else [])
    except Exception as e:
        return [{"error": str(e)}]


async def namespace_summary(conn):
    rows = await conn.fetch("""
        SELECT
            'production' AS namespace,
            'arifosmcp_tool_calls' AS tbl, COUNT(*)::int AS c,
            'trusted production — empty until MCP kernel integration' AS note
        FROM public.arifosmcp_tool_calls
        UNION ALL
        SELECT 'production','arifosmcp_approval_tickets',COUNT(*)::int,
               'trusted production ticket model' FROM public.arifosmcp_approval_tickets
        UNION ALL
        SELECT 'production','arifosmcp_canon_records',COUNT(*)::int,
               'trusted production — may be empty' FROM public.arifosmcp_canon_records
        UNION ALL
        SELECT 'production','vault_sealed_events',COUNT(*)::int,
               'canonical L6' FROM public.vault_sealed_events
        UNION ALL
        SELECT 'production','arifosmcp_floor_rules',COUNT(*)::int,
               'F1-F13 seeded rules' FROM public.arifosmcp_floor_rules
        UNION ALL
        SELECT 'design','s000.tool_calls',COUNT(*)::int,
               'Phase 1 design' FROM s000.tool_calls
        UNION ALL
        SELECT 'design','s000.approvals',COUNT(*)::int,
               'Phase 1 design' FROM s000.approvals
        UNION ALL
        SELECT 'design','s000.evidence_items',COUNT(*)::int,
               'Phase 1 design' FROM s000.evidence_items
        UNION ALL
        SELECT 'design','s000.artifacts',COUNT(*)::int,
               'Phase 1 design' FROM s000.artifacts
        UNION ALL
        SELECT 'design','s000.judge_verdicts',COUNT(*)::int,
               'Phase 1 design' FROM s000.judge_verdicts
        UNION ALL
        SELECT 'design','s999.vault999_ledger',COUNT(*)::int,
               'Phase 1 v2 ledger' FROM s999.vault999_ledger
        ORDER BY namespace, tbl
    """)
    return rows


async def recent_seals(conn, limit=20):
    rows = await conn.fetch(
        """
        SELECT * FROM (
            SELECT
                'production' AS src,
                event_id::text AS seal_id,
                event_type::text AS seal_type,
                session_id::text,
                actor_id::text AS signed_by,
                verdict,
                risk_tier::text AS risk_tier,
                merkle_leaf::text AS content_hash,
                sealed_at AS created_at
            FROM public.vault_sealed_events
            UNION ALL
            SELECT
                'design' AS src,
                seal_id::text,
                session_ref::text,
                NULL::text,
                signed_by_ref::text,
                verdict::text,
                NULL::text,
                content_hash::text,
                created_at
            FROM s999.vault999_ledger
        ) t
        ORDER BY created_at DESC
        LIMIT $1
    """,
        limit,
    )
    return rows


async def tool_calls(conn, limit=30):
    rows = await conn.fetch(
        """
        SELECT * FROM (
            SELECT
                'production' AS src,
                id::text AS call_id,
                organ AS organ_code,
                session_id AS session_ref,
                tool_name,
                agent_id AS actor_ref,
                verdict,
                floor_triggered,
                duration_ms AS latency_ms,
                epoch AS created_at,
                result_code,
                error_msg
            FROM public.arifosmcp_tool_calls
            UNION ALL
            SELECT
                'design' AS src,
                tool_call_id AS call_id,
                organ_code,
                session_ref,
                tool_name,
                actor_ref,
                NULL::text,
                NULL::text,
                latency_ms,
                created_at,
                NULL::text,
                NULL::text
            FROM s000.tool_calls
        ) t
        ORDER BY created_at DESC
        LIMIT $1
    """,
        limit,
    )
    return rows


async def floor_rules(conn):
    rows = await conn.fetch("""
        SELECT * FROM (
            SELECT
                'production' AS src,
                floor_code::text AS law_id,
                rule_name::text AS floor_name,
                constraint_definition::text,
                is_active,
                updated_at
            FROM public.arifosmcp_floor_rules
            UNION ALL
            SELECT
                'design' AS src,
                id::text,
                name::text,
                invariant::text,
                active,
                created_at
            FROM s000.constitutional_floors
        ) t
        ORDER BY law_id
    """)
    return rows


async def run_full():
    pool = await asyncpg.create_pool(POOL_URL, min_size=1, max_size=3)
    async with pool.acquire() as conn:
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║          AAA COCKPIT — arifOS Federation L4              ║")
        print(f"║          {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'):<43}║")
        print("╚══════════════════════════════════════════════════════════════╝")

        # Namespace summary
        print("\n── Namespace Summary ──────────────────────────────────────────")
        rows = await namespace_summary(conn)
        current_ns = None
        for row in rows:
            ns = row["namespace"]
            if ns != current_ns:
                print(f"\n  [{ns.upper()}]")
                current_ns = ns
            note = row["note"] or ""
            print(f"    {row['tbl']:<40} {row['c']:>6}  {note}")

        # Recent seals
        print("\n── Recent Seals (L6) ─────────────────────────────────────────")
        seals = await recent_seals(conn, 10)
        if seals and "error" not in seals[0]:
            for s in seals:
                src = s["src"]
                sid = (s["seal_id"] or "")[:20]
                v = s["verdict"] or "—"
                risk = s["risk_tier"] or "—"
                dt = s["created_at"]
                dt_str = dt.strftime("%m-%d %H:%M") if dt else "—"
                print(f"  [{src:<9}] {dt_str}  {v:<6}  risk={risk:<10}  {sid}")
        else:
            print(f"  Error fetching seals: {seals[0].get('error', 'unknown')}")

        # Floor rules
        print("\n── Constitutional Floors (F1–F13) ─────────────────────────────")
        floors = await floor_rules(conn)
        if floors and "error" not in floors[0]:
            for f in floors:
                src = f["src"]
                fid = f["law_id"] or ""
                fname = f["floor_name"] or ""
                active = "ACTIVE" if f["is_active"] else "inactive"
                print(f"  [{src:<9}] {fid:<6} {fname:<35} {active}")
        else:
            print(
                f"  Error fetching floors: {floors[0].get('error', 'unknown') if floors else 'no rows'}"
            )

        print("\n── Tool Calls (recent) ───────────────────────────────────────")
        calls = await tool_calls(conn, 15)
        if calls and "error" not in calls[0]:
            for c in calls:
                src = c["src"]
                tool = c["tool_name"] or ""
                organ = c["organ_code"] or ""
                dt = c["created_at"]
                dt_str = dt.strftime("%m-%d %H:%M") if dt else "—"
                lat = c["latency_ms"]
                lat_str = f"{lat}ms" if lat else "—"
                print(f"  [{src:<9}] {dt_str}  {organ:<10} {tool:<30} {lat_str}")
        else:
            print(
                f"  Error fetching tool calls: {calls[0].get('error', 'unknown') if calls else 'no rows'}"
            )

        print()

    await pool.close()


async def run_seals():
    pool = await asyncpg.create_pool(POOL_URL, min_size=1, max_size=3)
    async with pool.acquire() as conn:
        seals = await recent_seals(conn, 30)
        print(
            f"\n{'SRC':<10} {'DATE':<12} {'VERDICT':<8} {'RISK':<10} {'SEAL_ID':<25} {'SIGNED_BY'}"
        )
        print("-" * 100)
        for s in seals:
            src = s["src"]
            dt = s["created_at"].strftime("%Y-%m-%d %H:%M") if s["created_at"] else "—"
            v = s["verdict"] or "—"
            risk = s["risk_tier"] or "—"
            sid = (s["seal_id"] or "")[:24]
            by = s["signed_by"] or "—"
            print(f"{src:<10} {dt:<12} {v:<8} {risk:<10} {sid:<25} {by}")
    await pool.close()


async def run_tool_calls():
    pool = await asyncpg.create_pool(POOL_URL, min_size=1, max_size=3)
    async with pool.acquire() as conn:
        calls = await tool_calls(conn, 50)
        print(f"\n{'SRC':<10} {'DATE':<12} {'ORGAN':<12} {'TOOL':<35} {'LATENCY'}")
        print("-" * 90)
        for c in calls:
            src = c["src"]
            dt = c["created_at"].strftime("%Y-%m-%d %H:%M") if c["created_at"] else "—"
            organ = c["organ_code"] or ""
            tool = c["tool_name"] or ""
            lat = f"{c['latency_ms']}ms" if c["latency_ms"] else "—"
            print(f"{src:<10} {dt:<12} {organ:<12} {tool:<35} {lat}")
    await pool.close()


async def run_summary():
    pool = await asyncpg.create_pool(POOL_URL, min_size=1, max_size=3)
    async with pool.acquire() as conn:
        rows = await namespace_summary(conn)
        print(f"\n{'NAMESPACE':<12} {'TABLE':<40} {'ROWS':>8}  {'NOTE'}")
        print("-" * 90)
        for row in rows:
            print(f"{row['namespace']:<12} {row['tbl']:<40} {row['c']:>8}  {row['note'] or ''}")
    await pool.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AAA Cockpit — Unified L4 Read Dashboard")
    parser.add_argument("--seals", action="store_true", help="Show recent seals only")
    parser.add_argument("--tool-calls", action="store_true", help="Show tool calls only")
    parser.add_argument("--summary", action="store_true", help="Show namespace row counts only")
    args = parser.parse_args()

    if args.seals:
        asyncio.run(run_seals())
    elif args.tool_calls:
        asyncio.run(run_tool_calls())
    elif args.summary:
        asyncio.run(run_summary())
    else:
        asyncio.run(run_full())
