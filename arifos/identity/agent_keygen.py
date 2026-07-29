#!/usr/bin/env python3
"""
agent_keygen.py — Federation-wide Agent Identity Bootstrap
════════════════════════════════════════════════════════════

One-shot script to:
  1. Scan all AAA/agents/* directories
  2. Generate Ed25519 keypairs for agents without identity.json
  3. Create identity.json + identity.key (mode 600)
  4. Update agent-card.json with ed25519_pubkey field
  5. Rebuild agent_registry.json
  6. Sync to governance_identity.py VERIFIED_KEY_IDS

Usage:
    python3 agent_keygen.py              # Scan + generate missing keys
    python3 agent_keygen.py --force      # Regenerate ALL keys
    python3 agent_keygen.py --dry-run    # Show what would happen

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add arifOS to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from arifos.identity import AgentIdentity, IdentityRegistry

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("agent_keygen")

AGENTS_DIR = Path("/root/AAA/agents")
IDENTITY_DIR = Path("/root/arifOS/arifos/identity")
GOVERNANCE_IDENTITY = Path("/opt/arifos/arifosmcp/runtime/governance_identity.py")

# Agent capability defaults by type
CAPABILITY_MAP: dict[str, list[str]] = {
    "opencode": ["OBSERVE", "REASON", "EXECUTE_REVERSIBLE", "EDIT", "BUILD", "TEST", "DEPLOY"],
    "openclaw": ["OBSERVE", "REASON", "ROUTE", "MEMORY"],
    "hermes-asi": ["OBSERVE", "REASON", "ROUTE", "REFLECT"],
    "main": ["OBSERVE", "REASON", "JUDGE"],  # 888-APEX
    "makcikgpt": ["OBSERVE", "REASON"],
    "agentic-trading-companion": ["OBSERVE", "REASON", "EXECUTE_REVERSIBLE"],
    "prospect-maturation": ["OBSERVE", "REASON", "EXECUTE_REVERSIBLE"],
}


def main():
    parser = argparse.ArgumentParser(description="Agent Identity Keygen")
    parser.add_argument("--force", action="store_true", help="Regenerate ALL keys")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen, don't write"
    )
    parser.add_argument("--agent", type=str, help="Only process specific agent")
    args = parser.parse_args()

    agents_dir = AGENTS_DIR
    if not agents_dir.exists():
        logger.error(f"Agents directory not found: {agents_dir}")
        sys.exit(1)

    IDENTITY_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    skipped = []
    errors = []

    # Find all agent directories
    agent_dirs = sorted(
        [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    if args.agent:
        agent_dirs = [d for d in agent_dirs if d.name == args.agent]
        if not agent_dirs:
            logger.error(f"Agent '{args.agent}' not found in {agents_dir}")
            sys.exit(1)

    logger.info(f"Processing {len(agent_dirs)} agent directories…")

    for agent_dir in agent_dirs:
        agent_id = agent_dir.name
        identity_file = agent_dir / "identity.json"
        key_file = agent_dir / "identity.key"

        # Skip if already has keys and not forcing
        if identity_file.exists() and key_file.exists() and not args.force:
            logger.info(f"  ✅ {agent_id} — already has identity")
            skipped.append(agent_id)
            continue

        if args.dry_run:
            logger.info(f"  🔍 {agent_id} — would generate keypair")
            generated.append(agent_id)
            continue

        # Generate new identity
        try:
            capabilities = CAPABILITY_MAP.get(agent_id, ["OBSERVE", "REASON"])
            max_blast = (
                "T2" if "DEPLOY" in capabilities or "EXECUTE_REVERSIBLE" in capabilities else "T1"
            )

            identity = AgentIdentity.create(
                agent_id=agent_id,
                bound_to="arif-fazil/F13",
                capabilities=capabilities,
                max_blast_radius=max_blast,
            )

            # Save to agent directory
            identity.save(agent_dir)
            logger.info(
                f"  🔑 {agent_id} — keypair generated ({identity.ed25519_pubkey_hex[:16]}…)"
            )
            generated.append(agent_id)

            # Update agent-card.json with pubkey
            card_file = agent_dir / "agent-card.json"
            if card_file.exists():
                try:
                    with open(card_file) as f:
                        card = json.load(f)
                    card["ed25519_pubkey"] = identity.ed25519_pubkey_hex
                    card["identity_fingerprint"] = identity.fingerprint
                    card["identity_bound_at"] = identity.created_at
                    with open(card_file, "w") as f:
                        json.dump(card, f, indent=2)
                    logger.info(f"     📋 agent-card.json updated")
                except Exception as e:
                    logger.warning(f"     ⚠️ Failed to update card: {e}")

        except Exception as e:
            logger.error(f"  ❌ {agent_id} — FAILED: {e}")
            errors.append((agent_id, str(e)))

    # ── Rebuild registry ────────────────────────────────────────────────
    if not args.dry_run and generated:
        logger.info("")
        logger.info("Rebuilding agent_registry.json…")
        registry = IdentityRegistry()
        registry.load()
        registry.save_registry(IDENTITY_DIR / "agent_registry.json")

        # Show VERIFIED_KEY_IDS sync
        vkids = registry.to_verified_key_ids()
        logger.info(f"VERIFIED_KEY_IDS entries: {len(vkids)}")
        for key_id, agent_id in sorted(vkids.items()):
            logger.info(f"  {key_id} → {agent_id}")

    # ── Summary ─────────────────────────────────────────────────────────
    print("")
    print("╔══════════════════════════════════╗")
    print("║   AGENT KEYGEN — COMPLETE       ║")
    print("╚══════════════════════════════════╝")
    print(f"  Generated: {len(generated)} — {', '.join(generated) if generated else 'none'}")
    print(f"  Skipped:   {len(skipped)} — {', '.join(skipped) if skipped else 'none'}")
    if errors:
        print(f"  Errors:    {len(errors)}")
        for aid, err in errors:
            print(f"    ❌ {aid}: {err}")

    if args.dry_run:
        print("  (DRY RUN — no files written)")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
