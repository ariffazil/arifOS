"""
c:/ariffazil/arifOS/scripts/replay_apex_comparison.py
═════════════════════════════════════════════════════════

APEX Theory T-000 Step C: 50-Receipt Replay & Acceptance Band Evaluator.
Replays the 50 most recent VAULT999 sealed receipts under --legacy-apex
and compares apex_legacy vs apex_v2 scores side-by-side to enforce:
  1. Mean Delta |G_v2 - G_legacy| <= 0.05
  2. Max Delta  |G_v2 - G_legacy| <= 0.10
  3. Zero Verdict Flips (verdict_v2 == verdict_legacy across all 50 receipts)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import json
import math
import sys
from pathlib import Path

def geom_mean(vals: list[float]) -> float:
    if not vals:
        return 0.0
    prod = 1.0
    for v in vals:
        prod *= max(0.001, min(1.0, float(v)))
    return prod ** (1.0 / len(vals))

def arithmetic_mean(vals: list[float]) -> float:
    if not vals:
        return 0.0
    return sum(max(0.0, min(1.0, float(v))) for v in vals) / len(vals)

def verdict_from_score(score: float) -> str:
    if score >= 0.80:
        return "SEAL"
    elif score >= 0.50:
        return "SABAR"
    else:
        return "HOLD"

def compute_legacy_apex(floors: dict[str, float], energy: float = 0.90) -> dict[str, float]:
    """Legacy 6-variable formulation: g(t) = A * P * H * S * U * E^2."""
    f1 = floors.get("F1", 0.95)
    f2 = floors.get("F2", 0.95)
    f3 = floors.get("F3", 0.95)
    f4 = floors.get("F4", 0.95)
    f5 = floors.get("F5", 0.95)
    f6 = floors.get("F6", 0.95)
    f7 = floors.get("F7", 0.95)
    f8 = floors.get("F8", 0.95)
    f9 = floors.get("F9", 0.95)
    f10 = floors.get("F10", 0.95)
    f11 = floors.get("F11", 0.95)
    f12 = floors.get("F12", 0.95)
    f13 = floors.get("F13", 0.95)

    A = arithmetic_mean([f2, f4, f10])
    P = arithmetic_mean([f1, f11, f13])
    H = arithmetic_mean([f6, f9, f13])
    S = arithmetic_mean([f3, f5, f8])
    U = arithmetic_mean([f7, f4])
    E = arithmetic_mean([f12, energy])

    g_t = A * P * H * S * U * (E ** 2)
    verdict = verdict_from_score(g_t)
    return {
        "A": round(A, 4),
        "P": round(P, 4),
        "H": round(H, 4),
        "S": round(S, 4),
        "U": round(U, 4),
        "E": round(E, 4),
        "g_t": round(g_t, 4),
        "verdict": verdict,
    }

def compute_apex_v2(
    floors: dict[str, float],
    energy_score: float = 0.90,
    exploration_score: float = 0.90,
    c_dark: float = 0.0,
    use_dark_correction: bool = False,
) -> dict[str, float]:
    """Canonical 4-variable formulation: G = A * P * E * X."""
    f1 = floors.get("F1", 0.95)
    f2 = floors.get("F2", 0.95)
    f3 = floors.get("F3", 0.95)
    f4 = floors.get("F4", 0.95)
    f5 = floors.get("F5", 0.95)
    f6 = floors.get("F6", 0.95)
    f7 = floors.get("F7", 0.95)
    f8 = floors.get("F8", 0.95)
    f9 = floors.get("F9", 0.95)
    f10 = floors.get("F10", 0.95)
    f11 = floors.get("F11", 0.95)
    f12 = floors.get("F12", 0.95)
    f13 = floors.get("F13", 0.95)

    A = geom_mean([f2, f4, f7, f10])
    P = geom_mean([f1, f5, f11, f13])
    E = geom_mean([f3, f4, f12, energy_score, energy_score])
    X = geom_mean([f6, f8, f9, exploration_score])

    G = geom_mean([A, P, E, X])
    if use_dark_correction:
        G = G * (1.0 - c_dark)

    verdict = verdict_from_score(G)
    return {
        "A": round(A, 4),
        "P": round(P, 4),
        "E": round(E, 4),
        "X": round(X, 4),
        "G": round(G, 4),
        "verdict": verdict,
    }

def run_50_receipt_replay(sealed_events_path: Path):
    print("=========================================================================")
    print("  APEX THEORY T-000: 50-RECEIPT VAULT999 REPLAY & ACCEPTANCE BAND AUDIT  ")
    print("=========================================================================\n")

    if not sealed_events_path.exists():
        print(f"Path not found: {sealed_events_path}")
        return

    records = []
    with open(sealed_events_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    # Select the most recent 50 receipts
    recent_50 = records[-50:] if len(records) >= 50 else records
    print(f"Total Sealed Receipts: {len(records)} | Evaluating Most Recent: {len(recent_50)}\n")

    print(
        f"{'IDX':<4} | {'EVENT_ID':<16} | {'STAGE':<10} | "
        f"{'LEGACY g(t)':<11} | {'VERD_LEG':<8} | "
        f"{'APEX v2 G':<10} | {'VERD_v2':<7} | "
        f"{'DELTA':<7} | {'FLIP':<5}"
    )
    print("-" * 95)

    deltas = []
    verdict_flips = 0

    for idx, rec in enumerate(recent_50):
        event_id = str(rec.get("event_id", f"EVT-{idx}"))[:16]
        stage = str(rec.get("stage", rec.get("pipeline_stage", "999_SEAL")))[:10]

        # Extract floor scores from record
        payload = rec.get("payload", {})
        zkpc = rec.get("zkpc_receipt", {})
        raw_floors = payload.get("floors", zkpc.get("floors", []))

        floors = {}
        if isinstance(raw_floors, list):
            for fid in range(1, 14):
                k = f"F{fid}"
                floors[k] = 1.0 if k in raw_floors else 0.90
        elif isinstance(raw_floors, dict):
            for k, v in raw_floors.items():
                floors[k] = 1.0 if v in ("pass", True, 1.0) else 0.0

        w3_score = float(payload.get("w3_score", 0.95))

        leg = compute_legacy_apex(floors, energy=w3_score)
        v2 = compute_apex_v2(floors, energy_score=w3_score, exploration_score=w3_score)

        delta = abs(v2["G"] - leg["g_t"])
        deltas.append(delta)

        is_flip = leg["verdict"] != v2["verdict"]
        if is_flip:
            verdict_flips += 1

        flip_str = "YES ❌" if is_flip else "NO  "

        print(
            f"{idx:<4} | {event_id:<16} | {stage:<10} | "
            f"{leg['g_t']:<11.4f} | {leg['verdict']:<8} | "
            f"{v2['G']:<10.4f} | {v2['verdict']:<7} | "
            f"{delta:<7.4f} | {flip_str:<5}"
        )

    mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
    max_delta = max(deltas) if deltas else 0.0

    print("\n-------------------------------------------------------------------------")
    print("  ACCEPTANCE BAND CERTIFICATION RECEIPT")
    print("-------------------------------------------------------------------------")
    print(f"  • Total Receipts Replayed  : {len(recent_50)}")
    print(f"  • Mean Delta |G_v2 - g_t|   : {mean_delta:.4f}  (Threshold: <= 0.05)")
    print(f"  • Max Delta  |G_v2 - g_t|   : {max_delta:.4f}  (Threshold: <= 0.10)")
    print(f"  • Verdict Flips            : {verdict_flips}       (Threshold: == 0)")

    pass_mean = mean_delta <= 0.05
    pass_max = max_delta <= 0.10
    pass_flips = verdict_flips == 0

    overall_pass = pass_mean and pass_max and pass_flips

    print("-" * 75)
    if overall_pass:
        print("  VERDICT: SEALED — APEX T-000 REPLAY PASSED ALL ACCEPTANCE BANDS ✅")
        print("  STATUS : APEX_T000.md CERTIFIED FOR PROJECTION MATURATION")
    else:
        print("  VERDICT: 888_HOLD — REPLAY ACCEPTANCE BAND BREACH DETECTED ❌")
        print("  STATUS : APEX_T000.md REMAINS UNDER REVISION HOLD")
    print("=========================================================================\n")

if __name__ == "__main__":
    sealed_events_file = Path(__file__).resolve().parent.parent / "VAULT999" / "SEALED_EVENTS.jsonl"
    run_50_receipt_replay(sealed_events_file)
