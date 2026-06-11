"""
arifosmcp/geometry/trajectory_store.py — Qdrant-backed 13-dim store (EUREKA-G file 2/5)

Stores AgentState points as 13-dim vectors in Qdrant collection `arif_geometry`.
Dream-engine stage 2 cluster() gains a cluster_trajectories() step operating here.
Without Qdrant, geometry is decorative. With it, geometry is a queryable
substrate the dream-engine can replay.

F1 AMANAH fail-soft: every read/write fails closed if Qdrant is down.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

COLLECTION_NAME = "arif_geometry"
VECTOR_DIM = 13
DISTANCE = "Cosine"

_qdrant_client = None


def _get_client():
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client
    try:
        from arifosmcp.runtime.memory_store import _get_qdrant_client  # type: ignore

        _qdrant_client = _get_qdrant_client()
    except Exception as exc:
        logger.warning("Qdrant unavailable: %s", exc)
        _qdrant_client = None
    return _qdrant_client


@dataclass
class TrajectoryPoint:
    state_id: str
    actor: str
    model_key: str
    task_id: str
    task_class: str
    ts: float
    coords: np.ndarray
    is_const: bool
    delta_const_region: float
    provenance_sha: str
    floor_violations: list[str]
    constitutional_dwell: float


def _ensure_collection() -> bool:
    client = _get_client()
    if client is None:
        return False
    try:
        existing = {c.name for c in client.get_collections().collections}
        if COLLECTION_NAME in existing:
            return True
        from qdrant_client.http import models  # type: ignore

        # The Distance enum varies between qdrant-client versions; fall back to str
        distance = "Cosine"
        try:
            distance = models.Distance.COSINE
        except Exception:
            pass

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_DIM, distance=distance),
        )
        logger.info("Created Qdrant collection %s dim=%d", COLLECTION_NAME, VECTOR_DIM)
        return True
    except Exception as exc:
        logger.warning("Failed to create %s: %s", COLLECTION_NAME, exc)
        return False


def _point_id(actor: str, task_id: str, ts: float) -> str:
    raw = f"{actor}|{task_id}|{ts:.6f}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def upsert_state(
    state,
    task_id: str = "",
    task_class: str = "",
    trajectory_dwell: float = 0.0,
) -> str | None:
    if not _ensure_collection():
        return None
    client = _get_client()
    if client is None:
        return None
    try:
        from qdrant_client.http import models  # type: ignore

        pid = _point_id(state.actor, task_id, state.ts)
        payload = {
            "state_id": state.state_id,
            "actor": state.actor,
            "model_key": state.model_key,
            "task_id": task_id,
            "task_class": task_class,
            "ts": state.ts,
            "is_const": bool(state.is_const),
            "delta_const_region": float(state.delta_const_region()),
            "provenance_sha": state.provenance_sha,
            "floor_violations": [f.name for f in state.violating()],
            "constitutional_dwell": trajectory_dwell,
        }
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[models.PointStruct(id=pid, vector=state.coords.tolist(), payload=payload)],
        )
        return pid
    except Exception as exc:
        logger.warning("upsert_state failed: %s", exc)
        return None


def search_similar(
    coords: np.ndarray,
    *,
    actor: str | None = None,
    task_class: str | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not _ensure_collection():
        return []
    client = _get_client()
    if client is None:
        return []
    try:
        from qdrant_client.http import models  # type: ignore

        flt = None
        if actor or task_class:
            must = []
            if actor:
                must.append(
                    models.FieldCondition(key="actor", match=models.MatchValue(value=actor))
                )
            if task_class:
                must.append(
                    models.FieldCondition(
                        key="task_class", match=models.MatchValue(value=task_class)
                    )
                )
            flt = models.Filter(must=must)
        hits = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=coords.tolist(),
            query_filter=flt,
            limit=top_k,
            with_payload=True,
        )
        return [{"id": str(h.id), "score": float(h.score), "payload": h.payload} for h in hits]
    except Exception as exc:
        logger.warning("search_similar failed: %s", exc)
        return []


def cluster_by_task_class(task_class: str, *, top_k: int = 50) -> list[TrajectoryPoint]:
    if not _ensure_collection():
        return []
    client = _get_client()
    if client is None:
        return []
    try:
        from qdrant_client.http import models  # type: ignore

        flt = models.Filter(
            must=[
                models.FieldCondition(key="task_class", match=models.MatchValue(value=task_class)),
            ]
        )
        hits = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=flt,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
        )
        out: list[TrajectoryPoint] = []
        for h in hits[0]:
            payload = h.payload or {}
            out.append(
                TrajectoryPoint(
                    state_id=payload.get("state_id", ""),
                    actor=payload.get("actor", ""),
                    model_key=payload.get("model_key", ""),
                    task_id=payload.get("task_id", ""),
                    task_class=payload.get("task_class", ""),
                    ts=float(payload.get("ts", 0.0)),
                    coords=np.array(h.vector, dtype=np.float64)
                    if h.vector is not None
                    else np.zeros(13),
                    is_const=bool(payload.get("is_const", False)),
                    delta_const_region=float(payload.get("delta_const_region", 0.0)),
                    provenance_sha=payload.get("provenance_sha", ""),
                    floor_violations=list(payload.get("floor_violations", [])),
                    constitutional_dwell=float(payload.get("constitutional_dwell", 0.0)),
                )
            )
        return out
    except Exception as exc:
        logger.warning("cluster_by_task_class failed: %s", exc)
        return []


def stats() -> dict[str, Any]:
    if not _ensure_collection():
        return {"collection": COLLECTION_NAME, "ready": False, "points": 0}
    client = _get_client()
    if client is None:
        return {"collection": COLLECTION_NAME, "ready": False, "points": 0}
    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        pts = getattr(info, "points_count", 0) or 0
        return {
            "collection": COLLECTION_NAME,
            "ready": True,
            "points": int(pts),
            "dim": VECTOR_DIM,
            "distance": DISTANCE,
        }
    except Exception as exc:
        return {"collection": COLLECTION_NAME, "ready": False, "error": str(exc), "points": 0}


def self_check() -> bool:
    if not _ensure_collection():
        return False
    from arifosmcp.geometry.manifold import AgentState

    s = AgentState.neutral(
        actor="self-check", model_key="probe", ts=time.time(), provenance_sha="self-check-001"
    )
    pid = upsert_state(s, task_id="self-check", task_class="self-check", trajectory_dwell=1.0)
    if pid is None:
        return False
    hits = search_similar(s.coords, actor="self-check", top_k=1)
    return len(hits) >= 1


__all__ = [
    "COLLECTION_NAME",
    "VECTOR_DIM",
    "DISTANCE",
    "TrajectoryPoint",
    "upsert_state",
    "search_similar",
    "cluster_by_task_class",
    "stats",
    "self_check",
]
