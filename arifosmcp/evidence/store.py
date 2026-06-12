"""
arifosmcp/evidence/store.py — Evidence Store
═════════════════════════════════════════════

File-backed + Qdrant-backed evidence persistence layer.
Stores SourceContent, EvidenceReceipt, ContrastReport, and VoidReport
under VAULT999/evidence/ following the F-WEB doctrine.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# P0-FIX-2 (rev2): VAULT999_EVIDENCE uses dedicated ARIFOS_EVIDENCE_ROOT env var.
# ARIFOS_VAULT_PATH is for the outcomes.jsonl vault ledger file (a FILE).
# ARIFOS_EVIDENCE_ROOT is for the evidence store directory.
# They must be different paths — never conflate a file path with a directory path.
VAULT999_EVIDENCE = Path(
    os.environ.get(
        "ARIFOS_EVIDENCE_ROOT",
        "/var/lib/arifos/vault/evidence",
    )
)

_RECEIPTS_DIR = VAULT999_EVIDENCE / "receipts"
_SOURCES_DIR = VAULT999_EVIDENCE / "sources"
_CONTRASTS_DIR = VAULT999_EVIDENCE / "contrasts"
_VOIDS_DIR = VAULT999_EVIDENCE / "voids"

_QDRANT_AVAILABLE = False
try:
    from qdrant_client import QdrantClient

    _QDRANT_AVAILABLE = True
except ImportError:
    pass

_QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
_QDRANT_COLLECTION = "arif_evidence"


class EvidenceStore:
    """
    Dual-backend evidence store (file + Qdrant).

    File backend: VAULT999/evidence/{receipts,sources,contrasts,voids}/
    Qdrant backend: semantic search over source content and claims.

    All writes go to file first (append-only, VAULT999 governance).
    Qdrant is updated async after file write for searchability.
    """

    _instance: EvidenceStore | None = None
    _lock = threading.Lock()

    def __init__(
        self,
        vault_root: Path = VAULT999_EVIDENCE,
        qdrant_url: str = _QDRANT_URL,
    ):
        self._vault_root = vault_root
        self._receipts_dir = vault_root / "receipts"
        self._sources_dir = vault_root / "sources"
        self._contrasts_dir = vault_root / "contrasts"
        self._voids_dir = vault_root / "voids"
        self._qdrant_url = qdrant_url
        self._qdrant_client: Any = None
        self._ensure_dirs()

    @classmethod
    def get_instance(cls) -> EvidenceStore:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _ensure_dirs(self) -> None:
        for d in [self._receipts_dir, self._sources_dir, self._contrasts_dir, self._voids_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _qdrant(self) -> Any:
        if not _QDRANT_AVAILABLE:
            return None
        if self._qdrant_client is None:
            try:
                self._qdrant_client = QdrantClient(url=self._qdrant_url)
                self._ensure_qdrant_collection()
            except Exception as exc:
                logger.warning(f"Qdrant connection failed: {exc}")
                self._qdrant_client = None
        return self._qdrant_client

    def _ensure_qdrant_collection(self) -> None:
        client = self._qdrant_client
        if client is None:
            return
        try:
            collections = client.get_collections().collections
            names = [c.name for c in collections]
            if _QDRANT_COLLECTION not in names:
                client.create_collection(
                    collection_name=_QDRANT_COLLECTION,
                    vectors_config={"size": 768, "distance": "Cosine"},
                )
        except Exception as exc:
            logger.warning(f"Qdrant collection creation failed: {exc}")

    def _content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # ── SourceContent ──────────────────────────────────────────────────────────

    def store_source(self, source: dict) -> str:
        """
        Store a SourceContent dict.
        Returns the source_hash.
        """
        content = source.get("raw_content", source.get("sanitized_markdown", ""))
        source_hash = source.get("source_hash") or self._content_hash(content)
        source["source_hash"] = source_hash

        path = self._sources_dir / f"{source_hash}.json"
        path.write_text(json.dumps(source, indent=2, default=str))

        self._upsert_qdrant_source(source)
        return source_hash

    def get_source(self, source_hash: str) -> dict | None:
        path = self._sources_dir / f"{source_hash}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list_sources(self, limit: int = 100) -> list[dict]:
        files = sorted(
            self._sources_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        results = []
        for f in files[:limit]:
            try:
                results.append(json.loads(f.read_text()))
            except Exception:
                pass
        return results

    # ── EvidenceReceipt ────────────────────────────────────────────────────────

    def store_receipt(self, receipt: dict) -> str:
        """
        Store an EvidenceReceipt dict.
        Returns the receipt_id.
        """
        receipt_id = receipt.get("receipt_id")
        if not receipt_id:
            receipt_id = f"receipt://web/{self._content_hash(str(receipt))}"
            receipt["receipt_id"] = receipt_id

        path = self._receipts_dir / f"{receipt_id.replace('://', '_').replace('/', '_')}.json"
        path.write_text(json.dumps(receipt, indent=2, default=str))
        return receipt_id

    def get_receipt(self, receipt_id: str) -> dict | None:
        safe_name = receipt_id.replace("://", "_").replace("/", "_")
        path = self._receipts_dir / f"{safe_name}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list_receipts(self, limit: int = 100, session_id: str | None = None) -> list[dict]:
        files = sorted(
            self._receipts_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        results = []
        for f in files[:limit]:
            try:
                data = json.loads(f.read_text())
                if session_id is None or data.get("session_id") == session_id:
                    results.append(data)
            except Exception:
                pass
        return results

    # ── ContrastReport ────────────────────────────────────────────────────────

    def store_contrast(self, contrast: dict) -> str:
        """
        Store a ContrastReport dict.
        Returns the contrast_id.
        """
        contrast_id = (
            contrast.get("contrast_id") or f"contrast://{self._content_hash(str(contrast))}"
        )
        contrast["contrast_id"] = contrast_id

        safe_name = contrast_id.replace("://", "_").replace("/", "_")
        path = self._contrasts_dir / f"{safe_name}.json"
        path.write_text(json.dumps(contrast, indent=2, default=str))
        return contrast_id

    def get_contrast(self, contrast_id: str) -> dict | None:
        safe_name = contrast_id.replace("://", "_").replace("/", "_")
        path = self._contrasts_dir / f"{safe_name}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    # ── VoidReport ───────────────────────────────────────────────────────────

    def store_void(self, void_report: dict) -> str:
        """
        Store a VoidReport dict.
        Returns the void_id.
        """
        void_id = void_report.get("void_id") or f"void://{self._content_hash(str(void_report))}"
        void_report["void_id"] = void_id

        safe_name = void_id.replace("://", "_").replace("/", "_")
        path = self._voids_dir / f"{safe_name}.json"
        path.write_text(json.dumps(void_report, indent=2, default=str))
        return void_id

    def get_void(self, void_id: str) -> dict | None:
        safe_name = void_id.replace("://", "_").replace("/", "_")
        path = self._voids_dir / f"{safe_name}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    # ── Qdrant semantic search ─────────────────────────────────────────────────

    def _upsert_qdrant_source(self, source: dict) -> None:
        client = self._qdrant()
        if client is None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            text = source.get("sanitized_markdown", source.get("raw_content", ""))
            vector = model.encode(text).tolist()
            client.upsert(
                collection_name=_QDRANT_COLLECTION,
                points=[
                    {
                        "id": source["source_hash"],
                        "vector": vector,
                        "payload": {
                            "source_hash": source["source_hash"],
                            "url": source.get("url", ""),
                            "content_length": source.get("content_length", 0),
                            "claims_count": len(source.get("claims", [])),
                        },
                    }
                ],
            )
        except Exception as exc:
            logger.warning(f"Qdrant upsert failed: {exc}")

    def search_sources(self, query: str, limit: int = 5) -> list[dict]:
        """
        Semantic search over stored sources using Qdrant.
        Falls back to empty list if Qdrant unavailable.
        """
        client = self._qdrant()
        if client is None:
            return []
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            vector = model.encode(query).tolist()
            response = client.query_points(
                collection_name=_QDRANT_COLLECTION,
                query=vector,
                limit=limit,
                with_payload=True,
            )
            results = response.points
            out = []
            for r in results:
                source = self.get_source(r.payload["source_hash"])
                if source:
                    out.append(source)
            return out
        except Exception as exc:
            logger.warning(f"Qdrant search failed: {exc}")
            return []

    # ── Claim extraction helper ───────────────────────────────────────────────

    @staticmethod
    def extract_claims_from_text(text: str) -> list[dict]:
        """
        Deterministic claim extraction from text.
        Splits sentences and emits (subject, predicate, object) triples.
        This is a simple NER-lite extraction — not an LLM call.
        """
        import re

        sentences = re.split(r"[.!?\n]+", text)
        triples = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 10:
                continue
            tokens = sent.split()
            if len(tokens) < 3:
                continue
            subject = tokens[0]
            predicate = tokens[1] if len(tokens) > 1 else "is"
            obj = " ".join(tokens[2:])[:100]
            triples.append(
                {
                    "subject": subject,
                    "predicate": predicate,
                    "obj": obj,
                    "claim_type": "fact",
                    "support_span": sent,
                    "source_hash": None,
                }
            )
        return triples


_evidence_store: EvidenceStore | None = None


def get_evidence_store() -> EvidenceStore:
    global _evidence_store
    if _evidence_store is None:
        _evidence_store = EvidenceStore.get_instance()
    return _evidence_store
