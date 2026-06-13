"""
arifosmcp/federation/__main__.py
══════════════════════════════════════════════════════════════════════════════
Standalone entry point for the federation constitution package.

Usage:
  python -m arifosmcp.federation            # print aggregate as JSON
  python -m arifosmcp.federation --force     # bypass 30s cache
  python -m arifosmcp.federation --organ GEOX  # single organ
  python -m arifosmcp.federation --gates   # promotion gate criteria

Useful for CLI debugging and for F2 audit scripts.
"""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="arifosmcp.federation",
        description="Federation Constitution — F2-auditable organ registry",
    )
    parser.add_argument("--force", action="store_true", help="bypass 30s cache")
    parser.add_argument("--organ", type=str, help="show single organ constitution")
    parser.add_argument("--gates", action="store_true", help="show promotion gates")
    parser.add_argument(
        "--summary", action="store_true", help="compact summary (no per-organ payload)"
    )
    args = parser.parse_args()

    if args.gates:
        from arifosmcp.federation.routes import get_promotion_gates

        print(json.dumps(get_promotion_gates(), indent=2, default=str))
        return 0

    if args.organ:
        from arifosmcp.federation.routes import get_organ_constitution

        try:
            payload = get_organ_constitution(args.organ)
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(json.dumps(payload, indent=2, default=str))
        return 0

    from arifosmcp.federation.constitution_aggregator import get_federation_constitution

    fc = get_federation_constitution(force_refresh=args.force)
    if args.summary:
        from arifosmcp.federation.promotion_gates import tier_color

        s = {
            "federation_id": fc.federation_id,
            "version": fc.version,
            "as_of": fc.as_of.isoformat(),
            "aggregate_tier": fc.aggregate_tier,
            "aggregate_color": tier_color(fc.aggregate_tier),
            "total_organs": fc.total_organs,
            "green_organs": fc.green_organs,
            "yellow_organs": fc.yellow_organs,
            "red_organs": fc.red_organs,
            "black_organs": fc.black_organs,
            "federation_constitution_hash": fc.federation_constitution_hash,
            "pending_promotions_count": len(fc.pending_promotions),
            "pending_demotions_count": len(fc.pending_demotions),
        }
        print(json.dumps(s, indent=2))
    else:
        from arifosmcp.federation.constitution_aggregator import as_dict

        print(json.dumps(as_dict(fc), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
