"""
vault_vectorizer.py — PRL: VAULT999 → Qdrant Vector Index (P6 Enriched)
══════════════════════════════════════════════════════════════════════════

Reads VAULT999 outcomes.jsonl, builds semantically dense derived documents
from payload.action + metadata + tags, embeds with BAAI/bge-m3 (1024-dim),
and stores in Qdrant ``arifos_precedent``.

P6 Enrichment: The cryptographic ledger is NEVER mutated.  The vectorizer
extracts action, metadata, tags, verdict, and blast_radius from each seal
to construct a rich multi-line document that produces meaningful cosine
similarity.  Previously all SEAL verdicts clustered together — now each
domain (geoscience, capital, code gen, governance) forms distinct
gravitational wells.

Payload fields for the Dual-Gate:
  - blast_radius: L1_LOCAL | L2_SYSTEM | L3_CRITICAL
  - enriched_category: Inferred domain category
  - derived_semantic_text: Full derived document (for debugging)
  - seal_id: VAULT999 entry_id
  - timestamp: ISO 8601
  - is_derived: True (marks this as a derived view, not the ledger)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
COLLECTION_NAME = "arifos_precedent"
VECTOR_SIZE = 1024  # BAAI/bge-m3
EMBEDDING_MODEL = "BAAI/bge-m3"
PRL_TAU_THRESHOLD = 0.95

_VAULT_PATH = os.getenv(
    "VAULT999_SEAL_CHAIN",
    os.environ.get("ARIFOS_HOME", "/root") + "/.local/share/arifos/vault999/seal_chain.jsonl",
)
DEFAULT_QDRANT_URL = "http://localhost:6333"

BLAST_RADIUS_VALUES = {"L1_LOCAL", "L2_SYSTEM", "L3_CRITICAL"}
DEFAULT_BLAST_RADIUS = "L2_SYSTEM"

# ── P6: Category Inference Rules ──────────────────────────────────────────
_CATEGORY_RULES: list[tuple[str, str, str]] = [
    (r"geox|basin|seismic|petrophysic|geolog|earth", "domain.geoscience", "Earth intelligence"),
    (r"wealth|capital|npv|irr|market|trade|gold|oil", "domain.capital", "Capital intelligence"),
    (r"well|vitality|fatigue|readiness|dignity|human|bio", "domain.human_readiness", "WELL organ"),
    (r"aaa|cockpit|a2a|agent.?card|warga", "governance.aaa_control_plane", "AAA control plane"),
    (
        r"forge|file.?write|file.?mutate|aforge|artifact",
        "system.code_generation",
        "Code/forge mutations",
    ),
    (
        r"rs[ei]|recursive|self.?improv|meta.?learn|cooling",
        "architecture.rsi_meta_learning",
        "RSI cycles",
    ),
    (
        r"reality|observe|fetch|sense|search|vitals",
        "intelligence.reality_grounding",
        "Reality sensing",
    ),
    (r"judge|verdict|hold|sabar|void|adjudicate", "governance.judge", "Constitutional verdicts"),
    (r"seal|vault|ledger|999|immutable|chain", "governance.seal_chain", "VAULT999 operations"),
    (
        r"prl|emd|precedent.?retriev|gate.?intercept",
        "architecture.emd_pipeline",
        "EMD/PRL pipeline",
    ),
    (r"session|init|boot|ignite|wake", "governance.session", "Session lifecycle"),
    (r"telegram|hermes|bot|message|chat", "infrastructure.communication", "Hermes/Telegram"),
    (r"docker|container|deploy|compose|image", "infrastructure.deployment", "Deployment"),
    (r"caddy|dns|ssl|cert|cloudflare|tunnel", "infrastructure.networking", "Networking"),
    (r"cron|backup|purge|cleanup|housekeep", "infrastructure.maintenance", "Maintenance"),
    (r"drift|audit|conform|test|verify|integrity|sot", "governance.audit", "Audit/integrity"),
    (r"nats|event.?bus|mq|message.?queue|stream", "infrastructure.event_bus", "NATS events"),
]


def _infer_category(text: str) -> tuple[str, str]:
    """Infer domain category and context hint via regex rules."""
    text_lower = text.lower()
    for pattern, category, hint in _CATEGORY_RULES:
        if re.search(pattern, text_lower):
            return category, hint
    return "system.general", "No specific domain pattern matched"


def _build_embedding_text(entry: dict[str, Any]) -> str:
    """P6: Build semantically dense derived document for embedding.

    Extracts from payload.action, payload.metadata, payload.tags,
    verdict, and blast_radius.  The ledger is NEVER mutated.
    """
    payload_raw = entry.get("payload", "")
    payload: dict[str, Any] = {}
    if isinstance(payload_raw, str) and payload_raw.strip():
        try:
            payload = json.loads(payload_raw)
        except (json.JSONDecodeError, TypeError):
            pass
    elif isinstance(payload_raw, dict):
        payload = payload_raw

    action = payload.get("action", "") or entry.get("action", "")
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    tags = payload.get("tags", []) or entry.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    verdict = entry.get("verdict", "SEAL")
    blast_radius = _extract_blast_radius(entry)
    actor = entry.get("actor_id", "") or payload.get("agent_id", "") or "UNKNOWN"

    context_parts: list[str] = []
    for key in (
        "tool",
        "source",
        "protocol",
        "routing",
        "tool_name",
        "target_file",
        "query",
        "intent",
        "domain",
        "task_id",
    ):
        val = metadata.get(key, "")
        if val:
            context_parts.append(f"{key}: {str(val)[:80]}")

    classifier_text = action or str(payload)[:200]
    category, _hint = _infer_category(classifier_text)

    lines = [
        f"Category: {category}",
        f"Action: {action}",
    ]
    if context_parts:
        lines.append(f"Context: {' | '.join(context_parts)}")
    if tags:
        lines.append(f"Tags: {', '.join(str(t) for t in tags[:8])}")
    lines.append(f"Blast Radius: {blast_radius}")
    lines.append(f"Verdict: {verdict}")
    lines.append(f"Actor: {actor}")

    return "\n".join(lines)


def _extract_blast_radius(entry: dict[str, Any]) -> str:
    br = entry.get("blast_radius", "")
    if isinstance(br, str) and br in BLAST_RADIUS_VALUES:
        return br
    result = entry.get("result", {})
    if isinstance(result, dict):
        br = result.get("blast_radius", "")
        if isinstance(br, str) and br in BLAST_RADIUS_VALUES:
            return br
    return DEFAULT_BLAST_RADIUS


def _build_payload(entry: dict[str, Any], point_id: int) -> dict[str, Any]:
    payload_raw = entry.get("payload", "")
    payload: dict[str, Any] = {}
    if isinstance(payload_raw, str) and payload_raw.strip():
        try:
            payload = json.loads(payload_raw)
        except (json.JSONDecodeError, TypeError):
            pass
    elif isinstance(payload_raw, dict):
        payload = payload_raw

    action = payload.get("action", "") or entry.get("action", "")
    classifier_text = action or str(payload)[:200]
    category, _hint = _infer_category(classifier_text)

    return {
        "seal_id": entry.get("entry_id", f"legacy_{point_id}"),
        "blast_radius": _extract_blast_radius(entry),
        "enriched_category": category,
        "derived_semantic_text": _build_embedding_text(entry),
        "timestamp": entry.get("timestamp", ""),
        "verdict": entry.get("verdict", "SEAL"),
        "payload_summary": payload_raw[:512] if isinstance(payload_raw, str) else "",
        "session_id": entry.get("session_id", ""),
        "actor_id": entry.get("actor_id", ""),
        "vault_line": entry.get("_line", 0),
        "is_derived": True,
    }


# ── PrecedentVectorizer class ──────────────────────────────────────────────


class PrecedentVectorizer:
    """Create, seed, and search the VAULT999 precedent vector index in Qdrant."""

    def __init__(self, qdrant_url: str = DEFAULT_QDRANT_URL) -> None:
        self.client = QdrantClient(url=qdrant_url)
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s ...", EMBEDDING_MODEL)
            self._encoder = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
        return self._encoder

    def create_collection(self, recreate: bool = False) -> bool:
        if recreate:
            self.client.delete_collection(COLLECTION_NAME)
            logger.info("Recreated Qdrant collection: %s", COLLECTION_NAME)
        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: %s", COLLECTION_NAME)
            return True
        return False

    def _read_vault_entries(self) -> list[dict[str, Any]]:
        vault_path = Path(_VAULT_PATH)
        if not vault_path.exists():
            logger.warning("VAULT999 path not found: %s", vault_path)
            return []
        entries: list[dict[str, Any]] = []
        try:
            with open(vault_path) as f:
                for lineno, line in enumerate(f, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        entry = json.loads(stripped)
                        if isinstance(entry, dict):
                            entry["_line"] = lineno
                            entries.append(entry)
                        else:
                            logger.debug(
                                "Skipping non-dict entry at line %d: %s",
                                lineno,
                                type(entry).__name__,
                            )
                    except json.JSONDecodeError:
                        logger.warning("Skipping non-JSON line %d", lineno)
        except OSError as exc:
            logger.error("Failed to read vault: %s", exc)
            return []
        logger.info("Read %d entries from VAULT999", len(entries))
        return entries

    def backfill(self, batch_size: int = 128) -> dict[str, Any]:
        self.create_collection()
        entries = self._read_vault_entries()
        if not entries:
            return {"status": "EMPTY_VAULT", "indexed": 0}
        encoder = self._get_encoder()
        total_indexed = 0
        errors: list[str] = []
        for batch_start in range(0, len(entries), batch_size):
            batch = entries[batch_start : batch_start + batch_size]
            try:
                texts = [_build_embedding_text(e) for e in batch]
                embeddings = encoder.encode(texts, show_progress_bar=False)
                points = []
                for idx, entry in enumerate(batch):
                    global_idx = batch_start + idx
                    points.append(
                        PointStruct(
                            id=global_idx,
                            vector=embeddings[idx].tolist(),
                            payload=_build_payload(entry, global_idx),
                        )
                    )
                self.client.upsert(collection_name=COLLECTION_NAME, points=points)
                total_indexed += len(points)
            except Exception as exc:
                errors.append(f"Batch {batch_start}: {exc}")
                logger.error("Backfill batch failed: %s", exc)
        report = {
            "status": "OK" if not errors else "PARTIAL",
            "indexed": total_indexed,
            "total_entries": len(entries),
            "errors": errors[:10],
        }
        try:
            report["collection_size"] = self.client.count(collection_name=COLLECTION_NAME).count
        except Exception:
            report["collection_size"] = total_indexed
        logger.info("Backfill complete: %s", {k: v for k, v in report.items() if k != "errors"})
        return report

    def index_entry(self, entry: dict[str, Any], point_id: int | None = None) -> bool:
        self.create_collection()
        encoder = self._get_encoder()
        text = _build_embedding_text(entry)
        embedding = encoder.encode([text], show_progress_bar=False)[0]
        if point_id is None:
            try:
                point_id = self.client.count(collection_name=COLLECTION_NAME).count
            except Exception:
                point_id = int(datetime.now(UTC).timestamp() * 1000)
        payload = _build_payload(entry, point_id)
        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(id=point_id, vector=embedding.tolist(), payload=payload),
                ],
            )
            return True
        except Exception as exc:
            logger.error("Failed to index entry: %s", exc)
            return False

    def search(
        self,
        query_text: str,
        blast_radius: str | None = None,
        score_threshold: float = PRL_TAU_THRESHOLD,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        encoder = self._get_encoder()
        query_vector = encoder.encode([query_text], show_progress_bar=False)[0].tolist()
        query_filter = None
        if blast_radius and blast_radius in BLAST_RADIUS_VALUES:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = Filter(
                must=[FieldCondition(key="blast_radius", match=MatchValue(value=blast_radius))]
            )
        try:
            response = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )
        except Exception as exc:
            logger.error("PRL search failed: %s", exc)
            return []
        results = []
        for point in response.points:
            results.append(
                {
                    "score": round(point.score, 4),
                    "seal_id": point.payload.get("seal_id", ""),
                    "blast_radius": point.payload.get("blast_radius", ""),
                    "enriched_category": point.payload.get("enriched_category", ""),
                    "verdict": point.payload.get("verdict", ""),
                    "timestamp": point.payload.get("timestamp", ""),
                    "payload_summary": point.payload.get("payload_summary", "")[:256],
                    "session_id": point.payload.get("session_id", ""),
                }
            )
        return results

    def collection_stats(self) -> dict[str, Any]:
        try:
            return {
                "collection": COLLECTION_NAME,
                "vector_size": VECTOR_SIZE,
                "model": EMBEDDING_MODEL,
                "point_count": self.client.count(collection_name=COLLECTION_NAME).count,
                "tau_threshold": PRL_TAU_THRESHOLD,
            }
        except Exception as exc:
            return {"error": str(exc), "collection": COLLECTION_NAME}
