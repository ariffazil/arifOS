"""
codebase.mcp.maintenance (v53.2.7)
Background maintenance tasks for arifOS MCP Server.
"""

import asyncio
import logging
from codebase.mcp.session_ledger import get_orphaned_sessions, recover_orphaned_session

logger = logging.getLogger(__name__)


async def session_maintenance_loop(interval_seconds: int = 300):
    """
    Background loop to clean up orphaned sessions.
    Default: Every 5 minutes.
    """
    logger.info(f"🚀 Session maintenance loop started (interval={interval_seconds}s)")

    while True:
        try:
            # Wait for the next cycle
            await asyncio.sleep(interval_seconds)

            # Find orphaned sessions
            # A session is orphaned if process is gone or timeout (default 30m) exceeded
            orphans = get_orphaned_sessions(timeout_minutes=30)

            if orphans:
                logger.info(f"🧹 Found {len(orphans)} orphaned sessions. Starting recovery...")
                for orphan in orphans:
                    try:
                        recover_orphaned_session(orphan)
                    except Exception as e:
                        logger.error(
                            f"Failed to recover session {orphan.get('session_id', 'unknown')}: {e}"
                        )
            else:
                logger.debug("No orphaned sessions detected.")

        except asyncio.CancelledError:
            logger.info("Session maintenance loop stopping...")
            break
        except Exception as e:
            logger.error(f"Error in session maintenance loop: {e}")
            # Wait a bit before retrying to avoid tight loop on persistent errors
            await asyncio.sleep(60)


def start_maintenance(app=None):
    """
    Start maintenance tasks.
    Can be called during app startup.
    """
    return asyncio.create_task(session_maintenance_loop())
