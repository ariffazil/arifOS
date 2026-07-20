"""
meta_precedent_review.py — PRL Phase 2: Classification Audit Engine

Asynchronous Meta-Precedent Review: scans Qdrant arifos_precedent,
clusters vectors by cosine similarity, detects blast_radius outliers,
and generates review_required.json for sovereign review.

Architecture:
  - Reads all vectors from Qdrant (read-only, never mutates)
  - Computes pairwise cosine similarity within enriched_category clusters
  - Flags entries whose blast_radius deviates from cluster median
  - Output: /root/forge_work/YYYY-MM-DD/review_required.json

Run: scheduled (cron/systemd timer), not in critical path.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

PRL_COLLECTION = "arifos_precedent"
BLAST_HIERARCHY: dict[str, int] = {
    "L1_LOCAL": 1,
    "L2_SYSTEM": 2,
    "L3_CRITICAL": 3,
}
OUTPUT_DIR = Path("/root/forge_work")


def _get_qdrant() -> Any:
    """Return QdrantClient or None."""
    try:
        from qdrant_client import QdrantClient  # noqa: PLC0415
        return QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"), timeout=10)
    except Exception as exc:
        logger.error("Qdrant unreachable: %s", exc)
        return None


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def _fetch_vectors(client: Any) -> list[dict[str, Any]]:
    """Fetch all vectors with payloads from Qdrant."""
    entries: list[dict[str, Any]] = []
    try:
        scroll_result = client.scroll(
            collection_name=PRL_COLLECTION,
            limit=10_000,
            with_payload=True,
            with_vectors=True,
        )
        for pt in scroll_result[0] or []:
            if pt.vector and pt.payload:
                entries.append({
                    "point_id": str(pt.id),
                    "vector": np.array(pt.vector, dtype=np.float32),
                    "entry_id": pt.payload.get("entry_id", ""),
                    "blast_radius": pt.payload.get("blast_radius", "L2_SYSTEM"),
                    "enriched_category": pt.payload.get("enriched_category", "UNCATEGORIZED"),
                    "derived_semantic_text": pt.payload.get("derived_semantic_text", ""),
                    "actor": pt.payload.get("actor", ""),
                    "is_derived": pt.payload.get("is_derived", False),
                })
    except Exception as exc:
        logger.error("Failed to fetch vectors: %s", exc)
    return entries


def _cluster_by_category(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group entries by enriched_category."""
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in entries:
        cat = e["enriched_category"]
        clusters[cat].append(e)
    return dict(clusters)


def _detect_outliers(
    cluster: list[dict[str, Any]],
    min_cluster_size: int = 3,
    max_pairwise_samples: int = 50,
) -> list[dict[str, Any]]:
    """Detect blast_radius outliers within a category cluster.

    An entry is flagged if its blast_radius differs from the cluster's
    median blast_radius AND its vector is similar to the cluster centroid
    (cosine >= 0.70 — structurally related, so classification should match).

    Args:
        cluster: List of entries in the same category.
        min_cluster_size: Skip clusters smaller than this.
        max_pairwise_samples: Cap pairwise computation for large clusters.

    Returns:
        List of outlier reports.
    """
    if len(cluster) < min_cluster_size:
        return []

    # Compute cluster median blast_radius
    blast_levels = [BLAST_HIERARCHY.get(e["blast_radius"], 2) for e in cluster]
    median_level = int(np.median(blast_levels))
    median_br = {v: k for k, v in BLAST_HIERARCHY.items()}.get(median_level, "L2_SYSTEM")

    # Filter to entries that deviate from median
    deviants = [e for e in cluster if BLAST_HIERARCHY.get(e["blast_radius"], 2) != median_level]
    if not deviants:
        return []

    # Compute centroid from a sample
    sample = cluster[:max_pairwise_samples]
    vectors = np.stack([e["vector"] for e in sample])
    centroid = np.mean(vectors, axis=0)

    outliers: list[dict[str, Any]] = []
    for e in deviants:
        sim = _cosine(e["vector"], centroid)
        if sim >= 0.70:  # Structurally similar — classification should match
            outliers.append({
                "entry_id": e["entry_id"],
                "point_id": e["point_id"],
                "blast_radius_current": e["blast_radius"],
                "blast_radius_cluster_median": median_br,
                "enriched_category": e["enriched_category"],
                "cosine_to_centroid": round(sim, 4),
                "actor": e["actor"],
                "derived_text_preview": e["derived_semantic_text"][:200],
                "recommendation": f"Review: current={e['blast_radius']}, cluster_median={median_br}",
            })
    return outliers


def run_meta_review(
    output_dir: str | None = None,
    min_cluster_size: int = 3,
) -> dict[str, Any]:
    """Execute the full Meta-Precedent Review.

    Args:
        output_dir: Where to write review_required.json.
        min_cluster_size: Minimum entries per category to audit.

    Returns:
        Summary dict.
    """
    t0 = time.monotonic()

    client = _get_qdrant()
    if client is None:
        return {"status": "QDRANT_DOWN", "outliers": 0, "clusters": 0, "total_vectors": 0}

    entries = _fetch_vectors(client)
    if not entries:
        return {"status": "NO_VECTORS", "outliers": 0, "clusters": 0, "total_vectors": 0}

    clusters = _cluster_by_category(entries)
    all_outliers: list[dict[str, Any]] = []

    for cat, cluster_entries in sorted(clusters.items()):
        if len(cluster_entries) < min_cluster_size:
            continue
        outliers = _detect_outliers(cluster_entries, min_cluster_size=min_cluster_size)
        all_outliers.extend(outliers)

    elapsed = round(time.monotonic() - t0, 1)

    # Write output
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    out_dir = Path(output_dir or OUTPUT_DIR) / today
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "review_required.json"

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "OK",
        "total_vectors": len(entries),
        "total_clusters": len(clusters),
        "clusters_audited": sum(1 for v in clusters.values() if len(v) >= min_cluster_size),
        "outliers_found": len(all_outliers),
        "outliers": all_outliers,
        "elapsed_s": elapsed,
        "note": (
            "These entries have blast_radius classifications that deviate "
            "from their category cluster median. Review and re-classify if needed. "
            "Sovereign authority (W_scar) required for reclassification."
        ),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)

    logger.info(
        "Meta-Precedent Review: %d vectors, %d clusters, %d outliers → %s",
        len(entries), len(clusters), len(all_outliers), out_path,
    )

    return report


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    result = run_meta_review()
    print(json.dumps({k: v for k, v in result.items() if k != "outliers"}, indent=2, default=str))
    if result.get("outliers_found", 0) > 0:
        print(f"\n⚠ {result['outliers_found']} classification anomalies found.")
        print(f"  → {OUTPUT_DIR}/{datetime.now(UTC).strftime('%Y-%m-%d')}/review_required.json")
