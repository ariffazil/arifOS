#!/usr/bin/env python3
"""
Migrate VAULT999 data from filesystem JSONL to PostgreSQL.

Usage:
    python scripts/migrate_vault_to_postgres.py [--dry-run] [--source-dir /root/VAULT999]

This script:
1. Reads existing JSONL files from VAULT999 filesystem
2. Inserts them into PostgreSQL with proper chain reconstruction
3. Verifies the migration
4. Keeps filesystem as mirror (doesn't delete)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import asyncpg
except ImportError:
    print("❌ asyncpg not installed. Run: pip install asyncpg")
    sys.exit(1)

from arifosmcp.runtime.vault_postgres import PostgresVaultStore, VaultEvent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class VaultMigrator:
    """Migrates vault data from filesystem to PostgreSQL."""
    
    def __init__(self, dsn: str, source_dir: Path, dry_run: bool = False):
        self.dsn = dsn
        self.source_dir = source_dir
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "events_migrated": 0,
            "events_skipped": 0,
            "errors": 0,
        }
    
    async def migrate(self) -> dict[str, int]:
        """Run the migration."""
        logger.info(f"Starting migration from {self.source_dir}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        
        # Connect to database
        conn = await asyncpg.connect(self.dsn)
        try:
            # Check current state
            current_count = await conn.fetchval("SELECT COUNT(*) FROM vault_events")
            logger.info(f"Current vault_events count: {current_count}")
            
            if current_count > 0:
                logger.warning("Vault already has data. Migration will append (not idempotent).")
                response = input("Continue? [y/N]: ")
                if response.lower() != 'y':
                    logger.info("Migration cancelled.")
                    return self.stats
            
            # Find all JSONL files
            jsonl_files = list(self.source_dir.rglob("*.jsonl"))
            logger.info(f"Found {len(jsonl_files)} JSONL files")
            
            for file_path in jsonl_files:
                await self._migrate_file(conn, file_path)
            
            # Verify migration
            new_count = await conn.fetchval("SELECT COUNT(*) FROM vault_events")
            logger.info(f"Migration complete. New vault_events count: {new_count}")
            
            # Verify chain integrity
            if not self.dry_run and new_count > 0:
                result = await conn.fetchrow("SELECT * FROM verify_chain_integrity()")
                logger.info(f"Chain integrity: {result['is_valid']} ({result['total_checked']} entries)")
                
            return self.stats
            
        finally:
            await conn.close()
    
    async def _migrate_file(self, conn: asyncpg.Connection, file_path: Path):
        """Migrate a single JSONL file."""
        logger.info(f"Processing: {file_path}")
        self.stats["files_processed"] += 1
        
        try:
            with open(file_path) as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            self.stats["errors"] += 1
            return
        
        for line_num, line in enumerate(lines, 1):
            try:
                data = json.loads(line)
                await self._migrate_record(conn, file_path, line_num, data)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {file_path}:{line_num}: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                logger.error(f"Failed to migrate {file_path}:{line_num}: {e}")
                self.stats["errors"] += 1
    
    async def _migrate_record(
        self, 
        conn: asyncpg.Connection, 
        file_path: Path, 
        line_num: int, 
        data: dict[str, Any]
    ):
        """Migrate a single record to PostgreSQL."""
        # Extract fields with defaults
        event_type = self._infer_event_type(file_path, data)
        session_id = self._extract_session_id(data)
        actor_id = data.get("actor_id", data.get("agent", "migrated"))
        stage = data.get("stage", "999_VAULT")
        verdict = data.get("verdict", "SEAL")
        payload = data.get("payload", data)  # Use whole data if no payload field
        
        # Parse timestamp
        sealed_at = self._parse_timestamp(data.get("timestamp", data.get("sealed_at")))
        
        # Compute hashes (since we can't reconstruct original chain)
        content = json.dumps({
            "event_type": event_type,
            "session_id": str(session_id),
            "actor_id": actor_id,
            "stage": stage,
            "verdict": verdict,
            "payload": payload,
            "sealed_at": sealed_at.isoformat(),
        }, sort_keys=True)
        merkle_leaf = hashlib.sha256(content.encode()).hexdigest()
        
        # Get prev_hash from chain
        prev_row = await conn.fetchrow(
            "SELECT chain_hash FROM vault_events ORDER BY id DESC LIMIT 1"
        )
        if prev_row:
            prev_hash = prev_row["chain_hash"]
        else:
            prev_hash = "0" * 64
        
        # Compute chain hash
        chain_content = prev_hash + merkle_leaf
        chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
        
        if self.dry_run:
            logger.debug(f"Would insert: {event_type} from {file_path.name}")
            self.stats["events_migrated"] += 1
            return
        
        # Insert into database
        try:
            await conn.execute(
                """
                INSERT INTO vault_events (
                    event_type, session_id, actor_id, stage, verdict, risk_tier,
                    payload, merkle_leaf, prev_hash, chain_hash, sealed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT DO NOTHING
                """,
                event_type,
                session_id,
                actor_id,
                stage,
                verdict,
                "medium",
                json.dumps(payload),
                merkle_leaf,
                prev_hash,
                chain_hash,
                sealed_at,
            )
            self.stats["events_migrated"] += 1
        except asyncpg.UniqueViolationError:
            self.stats["events_skipped"] += 1
    
    def _infer_event_type(self, file_path: Path, data: dict) -> str:
        """Infer event type from file path and data."""
        path_str = str(file_path).lower()
        
        if "telemetry" in path_str:
            return "telemetry"
        elif "seal" in path_str:
            return "seal"
        elif "audit" in path_str:
            return "audit"
        elif "session" in path_str:
            return "session"
        elif "artifact" in path_str:
            return "artifact"
        else:
            return data.get("event_type", "migrated")
    
    def _extract_session_id(self, data: dict) -> Any:
        """Extract session ID from data."""
        import uuid
        
        # Try various field names
        for key in ["session_id", "session", "sid", "conversation_id"]:
            if key in data and data[key]:
                try:
                    return uuid.UUID(str(data[key]))
                except ValueError:
                    continue
        
        # Generate new UUID if not found
        return uuid.uuid4()
    
    def _parse_timestamp(self, ts: Any) -> datetime:
        """Parse timestamp from various formats."""
        if ts is None:
            return datetime.now(timezone.utc)
        
        if isinstance(ts, datetime):
            return ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
        
        # Try ISO format
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                pass
        
        return datetime.now(timezone.utc)


def main():
    parser = argparse.ArgumentParser(description="Migrate VAULT999 to PostgreSQL")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("/root/VAULT999"),
        help="Source directory containing JSONL files",
    )
    parser.add_argument(
        "--dsn",
        default=os.environ.get(
            "DATABASE_URL",
            "postgresql://arifos_admin@localhost:5432/arifos_vault"
        ),
        help="PostgreSQL connection string",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts",
    )
    
    args = parser.parse_args()
    
    if not args.source_dir.exists():
        logger.error(f"Source directory does not exist: {args.source_dir}")
        sys.exit(1)
    
    # Confirmation
    if not args.dry_run and not args.yes:
        print(f"This will migrate data from {args.source_dir} to PostgreSQL.")
        print("Filesystem data will be preserved as backup.")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Run migration
    migrator = VaultMigrator(args.dsn, args.source_dir, args.dry_run)
    stats = asyncio.run(migrator.migrate())
    
    print("\n" + "="*50)
    print("Migration Statistics:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Events migrated: {stats['events_migrated']}")
    print(f"  Events skipped:  {stats['events_skipped']}")
    print(f"  Errors:          {stats['errors']}")
    print("="*50)
    
    if stats["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
