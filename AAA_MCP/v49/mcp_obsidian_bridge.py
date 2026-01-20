"""
MCP Obsidian Bridge — arifOS ↔ Obsidian Vault Sync

This module provides MCP tools for bidirectional sync between
arifOS vault_999 and the Obsidian vault_999_obsidian layer.

Requires:
- Obsidian running with Local REST API plugin
- OBSIDIAN_API_KEY in .env
- OBSIDIAN_API_URL in .env (default: http://127.0.0.1:27123)

Authority: AAA_MCP/mcp_config.v50.json
Version: v50.0.0
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx

# Configuration
OBSIDIAN_API_URL = os.getenv("OBSIDIAN_API_URL", "http://127.0.0.1:27123")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY", "")
VAULT_999_PATH = Path(__file__).parent.parent.parent / "vault_999"
OBSIDIAN_VAULT_PATH = Path(__file__).parent.parent.parent / "VAULT999"


def _get_headers() -> Dict[str, str]:
    """Get authorization headers for Obsidian API."""
    return {
        "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
        "Content-Type": "application/json",
    }


def check_obsidian_connection() -> Tuple[bool, str]:
    """
    Check if Obsidian Local REST API is reachable.

    Returns:
        Tuple of (success, message)
    """
    if not OBSIDIAN_API_KEY:
        return False, "OBSIDIAN_API_KEY not set in environment"

    try:
        response = httpx.get(f"{OBSIDIAN_API_URL}/", headers=_get_headers(), timeout=5.0)
        if response.status_code == 200:
            return True, f"Connected to Obsidian at {OBSIDIAN_API_URL}"
        else:
            return False, f"Obsidian API returned {response.status_code}"
    except httpx.ConnectError:
        return False, f"Cannot connect to Obsidian at {OBSIDIAN_API_URL}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def obsidian_read_note(path: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Read a note from Obsidian vault via Local REST API.

    Args:
        path: Relative path to note (e.g., "SEALS/current_seal.md")

    Returns:
        Tuple of (success, content_or_error, frontmatter_dict)
    """
    try:
        # URL encode the path
        encoded_path = path.replace("/", "%2F")
        url = f"{OBSIDIAN_API_URL}/vault/{encoded_path}"

        response = httpx.get(url, headers=_get_headers(), timeout=10.0)

        if response.status_code == 200:
            content = response.text
            # Extract frontmatter if present
            frontmatter = None
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1])
                    except:
                        frontmatter = {}
            return True, content, frontmatter
        elif response.status_code == 404:
            return False, f"Note not found: {path}", None
        else:
            return False, f"API error: {response.status_code}", None

    except Exception as e:
        return False, f"Read error: {str(e)}", None


def obsidian_write_note(
    path: str,
    content: str,
    frontmatter: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Write or update a note in Obsidian vault via Local REST API.

    Args:
        path: Relative path to note (e.g., "TEST/new_note.md")
        content: Markdown content (without frontmatter)
        frontmatter: Optional dict to include as YAML frontmatter

    Returns:
        Tuple of (success, message_or_error)
    """
    try:
        # Build full content with frontmatter
        full_content = ""
        if frontmatter:
            import yaml
            full_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
        full_content += content

        # URL encode the path
        encoded_path = path.replace("/", "%2F")
        url = f"{OBSIDIAN_API_URL}/vault/{encoded_path}"

        response = httpx.put(
            url,
            headers=_get_headers(),
            content=full_content,
            timeout=10.0
        )

        if response.status_code in (200, 201, 204):
            return True, f"Note written: {path}"
        else:
            return False, f"Write failed: {response.status_code} - {response.text}"

    except Exception as e:
        return False, f"Write error: {str(e)}"


def obsidian_search(query: str, limit: int = 10) -> Tuple[bool, list]:
    """
    Search Obsidian vault via Local REST API.

    Args:
        query: Search query string
        limit: Maximum results to return

    Returns:
        Tuple of (success, results_list_or_error)
    """
    try:
        url = f"{OBSIDIAN_API_URL}/search/simple/"
        response = httpx.post(
            url,
            headers=_get_headers(),
            json={"query": query},
            timeout=15.0
        )

        if response.status_code == 200:
            results = response.json()
            return True, results[:limit] if isinstance(results, list) else results
        else:
            return False, [f"Search failed: {response.status_code}"]

    except Exception as e:
        return False, [f"Search error: {str(e)}"]


def sync_seal_to_obsidian() -> Tuple[bool, str]:
    """
    Sync current seal from vault_999 to Obsidian vault.

    Reads vault_999/seals/ and writes to vault_999_obsidian/SEALS/
    """
    try:
        # Find current seal
        seals_dir = VAULT_999_PATH / "seals"
        if not seals_dir.exists():
            return False, "vault_999/seals/ directory not found"

        # Look for seal files
        seal_files = list(seals_dir.glob("*seal*.yaml")) + list(seals_dir.glob("*seal*.yml"))
        if not seal_files:
            return False, "No seal files found in vault_999/seals/"

        # Use most recent seal
        seal_file = max(seal_files, key=lambda f: f.stat().st_mtime)

        import yaml
        with open(seal_file, "r", encoding="utf-8") as f:
            seal_data = yaml.safe_load(f)

        # Build Obsidian-friendly markdown
        frontmatter = {
            "version": seal_data.get("version", "unknown"),
            "status": seal_data.get("status", "UNKNOWN"),
            "merkle_root": seal_data.get("zkpc_proof", {}).get("merkle_root", "N/A"),
            "last_verified": datetime.now(timezone.utc).isoformat(),
            "sync_source": str(seal_file.relative_to(VAULT_999_PATH.parent)),
        }

        # Extract floors if present
        floors = seal_data.get("floors_validated", {})
        floors_passed = [k for k, v in floors.items() if isinstance(v, dict) and v.get("pass")]
        frontmatter["floors_passed"] = floors_passed

        content = f"""# Current Constitutional Seal

> [!NOTE]
> Synced from `{seal_file.name}` at {frontmatter['last_verified']}

## Status

{"✅" if frontmatter["status"] == "SEALED" else "⚠️"} **{frontmatter["status"]}** — v{frontmatter["version"]}

## Floor Validation

| Floor | Status |
|-------|--------|
"""
        for floor_name, floor_data in floors.items():
            if isinstance(floor_data, dict):
                status = "✅" if floor_data.get("pass") else "❌"
                content += f"| {floor_name} | {status} |\n"

        # Write to Obsidian
        obsidian_seal_path = OBSIDIAN_VAULT_PATH / "SEALS" / "current_seal.md"
        obsidian_seal_path.parent.mkdir(parents=True, exist_ok=True)

        import yaml as yaml_lib
        with open(obsidian_seal_path, "w", encoding="utf-8") as f:
            f.write(f"---\n{yaml_lib.dump(frontmatter, default_flow_style=False)}---\n\n")
            f.write(content)

        return True, f"Seal synced: {seal_file.name} -> SEALS/current_seal.md"

    except Exception as e:
        return False, f"Seal sync error: {str(e)}"


def sync_ledger_to_obsidian(max_entries: int = 50) -> Tuple[bool, str]:
    """
    Sync constitutional ledger entries to individual Obsidian notes.

    Reads vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl
    and creates BBB_LEDGER/entries/ notes for Dataview queries.
    """
    try:
        ledger_path = VAULT_999_PATH / "BBB_LEDGER" / "LAYER_3_AUDIT" / "constitutional_ledger.jsonl"
        if not ledger_path.exists():
            return False, f"Ledger not found: {ledger_path}"

        entries_dir = OBSIDIAN_VAULT_PATH / "BBB_LEDGER" / "entries"
        entries_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-max_entries:]  # Last N entries

        for line in lines:
            try:
                entry = json.loads(line.strip())
                entry_hash = entry.get("entry_hash", entry.get("hash", "unknown"))[:8]
                timestamp = entry.get("timestamp", "unknown")
                verdict = entry.get("verdict", "UNKNOWN")
                session = entry.get("session_id", "unknown")

                # Create entry note
                frontmatter = {
                    "entry_hash": entry_hash,
                    "timestamp": timestamp,
                    "verdict": verdict,
                    "session_id": session,
                }

                content = f"""# Ledger Entry: {entry_hash}

| Field | Value |
|-------|-------|
| Verdict | **{verdict}** |
| Session | `{session}` |
| Time | {timestamp} |

## Raw Entry

```json
{json.dumps(entry, indent=2)}
```
"""

                note_path = entries_dir / f"{entry_hash}.md"
                import yaml
                with open(note_path, "w", encoding="utf-8") as nf:
                    nf.write(f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n")
                    nf.write(content)

                count += 1

            except json.JSONDecodeError:
                continue

        return True, f"Synced {count} ledger entries to BBB_LEDGER/entries/"

    except Exception as e:
        return False, f"Ledger sync error: {str(e)}"


# MCP Tool Registration
MCP_TOOLS = {
    "obsidian_check": {
        "description": "Check Obsidian Local REST API connection",
        "handler": check_obsidian_connection,
    },
    "obsidian_read": {
        "description": "Read a note from Obsidian vault",
        "handler": obsidian_read_note,
        "params": ["path"],
    },
    "obsidian_write": {
        "description": "Write or update a note in Obsidian vault",
        "handler": obsidian_write_note,
        "params": ["path", "content", "frontmatter"],
    },
    "obsidian_search": {
        "description": "Search Obsidian vault content",
        "handler": obsidian_search,
        "params": ["query", "limit"],
    },
    "obsidian_sync_seal": {
        "description": "Sync current seal from vault_999 to Obsidian",
        "handler": sync_seal_to_obsidian,
    },
    "obsidian_sync_ledger": {
        "description": "Sync constitutional ledger entries to Obsidian",
        "handler": sync_ledger_to_obsidian,
        "params": ["max_entries"],
    },
}


if __name__ == "__main__":
    # Quick test
    print("Testing Obsidian Bridge...")
    ok, msg = check_obsidian_connection()
    print(f"Connection: {ok} - {msg}")

    if ok:
        ok, msg = sync_seal_to_obsidian()
        print(f"Seal sync: {ok} - {msg}")

        ok, msg = sync_ledger_to_obsidian()
        print(f"Ledger sync: {ok} - {msg}")
