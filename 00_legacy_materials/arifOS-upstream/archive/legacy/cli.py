#!/usr/bin/env python3
"""
arifOS Model Registry — CLI
Usage: python cli.py <command> [options]

Commands:
  validate                    Validate all registry files against schemas
  list-providers              List all registered provider soul archetypes
  list-models                 List all registered models
  show-soul <soul_key>        Show a provider soul profile
  show-model <model_key>      Show a model profile (provider/family/variant)
  show-runtime <runtime_key>  Show a runtime deployment profile
  create-anchor               Create a session anchor (dry-run)
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent
MODELS_PATH = REGISTRY_PATH / "models"
SOULS_PATH = REGISTRY_PATH / "provider_souls"
RUNTIME_PATH = REGISTRY_PATH / "runtime_profiles"
CATALOG_PATH = REGISTRY_PATH / "catalog.json"
SCHEMAS_PATH = REGISTRY_PATH / "schemas"


# =============================================================================
# Helpers
# =============================================================================


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def fail(msg: str) -> None:
    print(f"  ❌ {msg}", file=sys.stderr)


# =============================================================================
# Commands
# =============================================================================


def cmd_validate(args) -> int:
    """Validate all registry files against schemas."""
    try:
        import jsonschema
    except ImportError:
        print("❌ jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
        return 1

    error_count = 0
    print("🔍 Validating arifOS Model Registry...\n")

    # 1. Load schemas
    soul_schema_path = SCHEMAS_PATH / "provider_soul.schema.json"
    runtime_schema_path = SCHEMAS_PATH / "runtime_truth.schema.json"
    soul_schema = load_json(soul_schema_path)
    runtime_schema = load_json(runtime_schema_path)

    # 2. Validate provider souls
    print("1. Checking provider_souls/*.json files...")
    for soul_file in sorted(SOULS_PATH.glob("*.json")):
        if soul_file.stem.startswith("wrong_"):
            ok(f"{soul_file.name} (honeypot — skipped)")
            continue
        try:
            data = load_json(soul_file)
            jsonschema.validate(instance=data, schema=soul_schema)
            ok(soul_file.name)
        except jsonschema.ValidationError as e:
            fail(f"{soul_file.name}: {e.message}")
            error_count += 1
        except Exception as e:
            fail(f"{soul_file.name}: {e}")
            error_count += 1

    # 3. Validate catalog consistency
    print("\n2. Checking catalog.json consistency...")
    try:
        catalog = load_json(CATALOG_PATH)
        catalog_archetypes = set(catalog.get("soul_archetypes", []))
        actual_files = {f.stem for f in SOULS_PATH.glob("*.json")}
        missing_files = catalog_archetypes - actual_files
        extra_files = actual_files - catalog_archetypes
        if missing_files:
            fail(f"In catalog but no file: {missing_files}")
            error_count += 1
        if extra_files:
            fail(f"Has file but not in catalog: {extra_files}")
            error_count += 1
        if not missing_files and not extra_files:
            ok(f"catalog.json matches provider_souls/ ({len(catalog_archetypes)} archetypes)")
    except Exception as e:
        fail(f"catalog.json: {e}")
        error_count += 1

    # 4. Validate model files exist for catalog entries
    print("\n3. Checking models/ files for catalog entries...")
    catalog_models = catalog.get("models", [])
    for model_key in catalog_models:
        model_path = MODELS_PATH / f"{model_key}.json"
        if model_path.exists():
            ok(model_key)
        else:
            fail(f"Model file not found: {model_path}")
            error_count += 1

    # 5. Validate runtime profiles
    print("\n4. Checking runtime_profiles/*.json files...")
    for rt_file in sorted(RUNTIME_PATH.glob("*.json")):
        try:
            data = load_json(rt_file)
            jsonschema.validate(instance=data, schema=runtime_schema)
            ok(rt_file.name)
        except jsonschema.ValidationError as e:
            fail(f"{rt_file.name}: {e.message}")
            error_count += 1
        except Exception as e:
            fail(f"{rt_file.name}: {e}")
            error_count += 1

    # Summary
    print("\n" + "=" * 50)
    if error_count:
        print(f"❌ VALIDATION FAILED: {error_count} error(s)")
        return 1
    else:
        print("✅ ALL VALIDATIONS PASSED")
        return 0


def cmd_list_providers(args) -> int:
    """List all registered provider soul archetypes."""
    catalog = load_json(CATALOG_PATH)
    souls = catalog.get("soul_archetypes", [])
    print(f"Provider Soul Archetypes ({len(souls)}):")
    print()
    for soul_key in souls:
        soul_path = SOULS_PATH / f"{soul_key}.json"
        label = ""
        if soul_path.exists():
            soul = load_json(soul_path)
            label = f"  — {soul.get('soul_label', '')}  |  {soul.get('in_one_sentence', '')}"
        print(f"  {soul_key}{label}")
    return 0


def cmd_list_models(args) -> int:
    """List all registered models."""
    catalog = load_json(CATALOG_PATH)
    model_keys = catalog.get("models", [])
    print(f"Registered Models ({len(model_keys)}):")
    print()
    for mk in model_keys:
        print(f"  {mk}")
    return 0


def cmd_show_soul(args) -> int:
    """Show a provider soul profile."""
    soul_key = args.soul_key
    soul_path = SOULS_PATH / f"{soul_key}.json"
    if not soul_path.exists():
        print(
            f"❌ Soul '{soul_key}' not found. Use 'list-providers' to see available keys.",
            file=sys.stderr,
        )
        return 1
    print_json(load_json(soul_path))
    return 0


def cmd_show_model(args) -> int:
    """Show a model profile."""
    model_key = args.model_key
    model_path = MODELS_PATH / f"{model_key}.json"
    if not model_path.exists():
        print(
            f"❌ Model '{model_key}' not found. Use 'list-models' to see available keys.",
            file=sys.stderr,
        )
        return 1
    print_json(load_json(model_path))
    return 0


def cmd_show_runtime(args) -> int:
    """Show a runtime deployment profile."""
    runtime_key = args.runtime_key
    rt_path = RUNTIME_PATH / f"{runtime_key}.json"
    if not rt_path.exists():
        available = [f.stem for f in RUNTIME_PATH.glob("*.json")]
        print(f"❌ Runtime '{runtime_key}' not found. Available: {available}", file=sys.stderr)
        return 1
    print_json(load_json(rt_path))
    return 0


def cmd_create_anchor(args) -> int:
    """Create a session anchor (dry-run — prints the anchor JSON)."""
    soul_key = args.soul
    runtime_key = args.runtime
    actor_id = args.actor or "cli_user"

    # Load soul
    soul_path = SOULS_PATH / f"{soul_key}.json"
    if not soul_path.exists():
        print(
            f"❌ Soul '{soul_key}' not found. Use 'list-providers' to see available keys.",
            file=sys.stderr,
        )
        return 1
    soul = load_json(soul_path)

    # Load runtime
    rt_path = RUNTIME_PATH / f"{runtime_key}.json"
    if not rt_path.exists():
        available = [f.stem for f in RUNTIME_PATH.glob("*.json")]
        print(f"❌ Runtime '{runtime_key}' not found. Available: {available}", file=sys.stderr)
        return 1
    runtime = load_json(rt_path)

    anchor = {
        "schema_version": "SESSION_ANCHOR_V1",
        "session_id": f"sess_{actor_id}_{int(time.time())}",
        "actor_id": actor_id,
        "soul_key": soul_key,
        "soul_label": soul.get("soul_label"),
        "deployment_id": runtime.get("deployment_id", runtime_key),
        "provider_key": runtime.get("provider_key"),
        "family_key": runtime.get("family_key"),
        "self_claim_boundary": {
            "identity": "provider_family_only_unless_verified",
            "tools": "verified_only",
            "knowledge": "mark_verified_vs_inferred",
            "actions": "mark_executed_vs_suggested",
        },
        "runtime_truth": {
            "memory_mode": runtime.get("memory_mode"),
            "tools_live": runtime.get("tools_live"),
            "web_on": runtime.get("web_on"),
            "execution_mode": runtime.get("execution_mode"),
        },
        "identity_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    print_json(anchor)
    return 0


# =============================================================================
# Entry point
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="arifos-registry",
        description="arifOS Model Registry CLI — governance layer for AI agent identity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py validate
  python cli.py list-providers
  python cli.py list-models
  python cli.py show-soul anthropic_claude
  python cli.py show-model anthropic/claude/claude-3-7-sonnet
  python cli.py show-runtime vps_main_arifos
  python cli.py create-anchor --soul anthropic_claude --runtime vps_main_arifos
  python cli.py create-anchor --soul openai_gpt --runtime vps_main_arifos --actor my_agent
        """,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # validate
    subparsers.add_parser("validate", help="Validate all registry files against schemas")

    # list-providers
    subparsers.add_parser("list-providers", help="List all provider soul archetypes")

    # list-models
    subparsers.add_parser("list-models", help="List all registered models")

    # show-soul
    p = subparsers.add_parser("show-soul", help="Show a provider soul profile")
    p.add_argument("soul_key", help="Soul key (e.g. anthropic_claude)")

    # show-model
    p = subparsers.add_parser("show-model", help="Show a model profile")
    p.add_argument("model_key", help="Model key (e.g. anthropic/claude/claude-3-7-sonnet)")

    # show-runtime
    p = subparsers.add_parser("show-runtime", help="Show a runtime deployment profile")
    p.add_argument("runtime_key", help="Runtime key (e.g. vps_main_arifos)")

    # create-anchor
    p = subparsers.add_parser("create-anchor", help="Create a session anchor (dry-run)")
    p.add_argument("--soul", required=True, help="Provider soul key (e.g. anthropic_claude)")
    p.add_argument("--runtime", required=True, help="Runtime profile key (e.g. vps_main_arifos)")
    p.add_argument("--actor", default="cli_user", help="Actor/agent ID (default: cli_user)")

    args = parser.parse_args()

    commands = {
        "validate": cmd_validate,
        "list-providers": cmd_list_providers,
        "list-models": cmd_list_models,
        "show-soul": cmd_show_soul,
        "show-model": cmd_show_model,
        "show-runtime": cmd_show_runtime,
        "create-anchor": cmd_create_anchor,
    }

    if args.command is None:
        parser.print_help()
        return 0

    fn = commands.get(args.command)
    if fn is None:
        parser.print_help()
        return 1

    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
