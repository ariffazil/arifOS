#!/usr/bin/env python3
"""
Phase 2: Meta-Precedent Review — Asynchronous Audit Hook
══════════════════════════════════════════════════════════

Weekly background sweep over arifos_precedent (Qdrant):
  1. Cluster vectors by cosine similarity
  2. Detect blast_radius classification anomalies
     ("L1 seal sitting in L3 cluster" → flag for sovereign review)
  3. Generate review_required.json for Monday morning

Runs async — never in the critical path.
Non-mutating — reads Qdrant only, writes report to disk.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

REPORT_PATH = os.path.expanduser("~/.local/share/arifos/prl/review_required.json")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = "arifos_precedent"
ANOMALY_THRESHOLD = 0.70  # Cosine threshold for "same cluster"
MAX_POINTS = 500


def load_all_points() -> list[dict[str, Any]]:
    """Scroll all points from Qdrant arifos_precedent."""
    from qdrant_client import QdrantClient

    client = QdrantClient(url=QDRANT_URL)
    points: list[dict[str, Any]] = []

    try:
        # Use scroll for efficient full-collection retrieval
        records, next_offset = client.scroll(
            collection_name=COLLECTION,
            limit=MAX_POINTS,
            with_payload=True,
            with_vectors=True,
        )
        for record in records:
            payload = record.payload or {}
            points.append({
                "id": record.id,
                "vector": record.vector,
                "blast_radius": payload.get("blast_radius", "L2_SYSTEM"),
                "enriched_category": payload.get("enriched_category", "system.general"),
                "verdict": payload.get("verdict", ""),
                "timestamp": payload.get("timestamp", ""),
                "seal_id": payload.get("seal_id", str(record.id)),
            })
    except Exception as e:
        print(f"[ERROR] Failed to scroll Qdrant: {e}", file=sys.stderr)
        return []

    return points


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cluster_by_similarity(points: list[dict]) -> list[list[int]]:
    """Greedy clustering: points with cosine ≥ ANOMALY_THRESHOLD form a cluster."""
    n = len(points)
    visited = [False] * n
    clusters: list[list[int]] = []

    for i in range(n):
        if visited[i]:
            continue
        cluster = [i]
        visited[i] = True
        for j in range(i + 1, n):
            if visited[j]:
                continue
            # Check similarity against ALL existing members
            all_similar = True
            for member_idx in cluster:
                sim = cosine_similarity(
                    points[i]["vector"], points[j]["vector"]
                )
                if sim < ANOMALY_THRESHOLD:
                    all_similar = False
                    break
            if all_similar:
                cluster.append(j)
                visited[j] = True
        clusters.append(cluster)

    return clusters


def detect_anomalies(points: list[dict], clusters: list[list[int]]) -> list[dict]:
    """Flag blast_radius outliers within each cluster.

    If a cluster has majority L3 but one L1 → anomaly.
    If a cluster has majority L1 but one L3 → soft flag.
    """
    anomalies: list[dict] = []

    for cluster in clusters:
        if len(cluster) < 3:
            continue  # Too small for meaningful cluster analysis

        br_counts: dict[str, int] = defaultdict(int)
        for idx in cluster:
            br = points[idx]["blast_radius"]
            br_counts[br] += 1

        # Find majority blast_radius
        total = len(cluster)
        majority_br, majority_count = max(br_counts.items(), key=lambda x: x[1])

        # Flag minority entries
        for idx in cluster:
            br = points[idx]["blast_radius"]
            if br != majority_br and br_counts[br] <= total * 0.3:
                anomaly = {
                    "point_id": str(points[idx]["id"]),
                    "seal_id": points[idx]["seal_id"],
                    "current_blast_radius": br,
                    "cluster_majority_blast_radius": majority_br,
                    "cluster_size": total,
                    "majority_count": majority_count,
                    "enriched_category": points[idx]["enriched_category"],
                    "verdict": points[idx]["verdict"],
                    "timestamp": points[idx]["timestamp"],
                    "severity": (
                        "HIGH" if br == "L1_LOCAL" and majority_br == "L3_CRITICAL"
                        else "MEDIUM" if br != majority_br else "LOW"
                    ),
                    "recommendation": (
                        f"Review: L1_LOCAL in L3_CRITICAL cluster. "
                        f"Consider upgrading to {majority_br}."
                        if br == "L1_LOCAL" and majority_br == "L3_CRITICAL"
                        else f"Outlier: {br} in {majority_br}-majority cluster. "
                        f"Sovereign review recommended."
                    ),
                }
                anomalies.append(anomaly)

    return anomalies


def generate_report(points: list[dict], anomalies: list[dict]) -> dict:
    """Build the review_required.json report."""
    br_dist = defaultdict(int)
    cat_dist = defaultdict(int)
    for p in points:
        br_dist[p["blast_radius"]] += 1
        cat_dist[p["enriched_category"]] += 1

    return {
        "meta": {
            "tool": "prl_meta_precedent_review",
            "phase": "2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_points": len(points),
            "anomalies_found": len(anomalies),
            "anomaly_threshold": ANOMALY_THRESHOLD,
        },
        "distribution": {
            "blast_radius": dict(br_dist),
            "category": dict(sorted(cat_dist.items(), key=lambda x: -x[1])[:20]),
        },
        "anomalies": anomalies[:50],  # Cap at 50 for readability
        "next_action": (
            "Review anomalies above. For each HIGH severity: "
            "verify blast_radius classification. For misclassified: "
            "re-seal with correct blast_radius or ratify as accepted risk."
        ) if anomalies else "No anomalies detected. All blast_radius tags consistent with cluster membership.",
    }


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] PRL Phase 2: Meta-Precedent Review")

    points = load_all_points()
    if not points:
        print("[DONE] No points in collection — nothing to audit.")
        return

    print(f"  Loaded {len(points)} points from {COLLECTION}")

    # Clustering
    t0 = time.time()
    clusters = cluster_by_similarity(points)
    cluster_time = time.time() - t0
    print(f"  Clustered into {len(clusters)} groups "
          f"(took {cluster_time:.1f}s, threshold={ANOMALY_THRESHOLD})")

    # Anomaly detection
    anomalies = detect_anomalies(points, clusters)
    print(f"  Detected {len(anomalies)} blast_radius anomalies")

    # Generate report
    report = generate_report(points, anomalies)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"  Report written to {REPORT_PATH}")

    # Summary
    high = sum(1 for a in anomalies if a["severity"] == "HIGH")
    med = sum(1 for a in anomalies if a["severity"] == "MEDIUM")
    print(f"\n[DONE] {high} HIGH, {med} MEDIUM anomalies flagged for sovereign review.")
    print("[DITEMPA BUKAN DIBERI]")


if __name__ == "__main__":
    main()
