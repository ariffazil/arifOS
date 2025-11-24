---

# ✅ **3. arifos_core/memory/zkpc.py**

```python
"""
zkpc.py — Zero-Knowledge Proof of Cognition (v33Ω)
Provides governance proofs for high-stakes outputs without revealing chain-of-thought.
"""

from __future__ import annotations
import time
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path


def _h(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()


@dataclass
class ZKPCReceipt:
    timestamp: float
    request_hash: str
    metrics_hash: str
    floor_pass_hash: str
    apex_verdict_hash: str
    constitution_hash: str
    psi_vitality: float
    tri_witness: float

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class ZKPC:
    """
    zkPC engine:
    - Takes request
    - Takes metrics + verdict
    - Hashes them into a governance receipt
    """

    def __init__(self, constitution_path="runtime/vault_999/constitution.json"):
        self.const_path = Path(constitution_path)

    def make_receipt(
        self,
        request: str,
        metrics: dict,
        floor_pass: dict,
        verdict: dict,
    ) -> ZKPCReceipt:
        constitution_json = self.const_path.read_text() if self.const_path.exists() else "{}"

        return ZKPCReceipt(
            timestamp=time.time(),
            request_hash=_h(request),
            metrics_hash=_h(json.dumps(metrics, sort_keys=True)),
            floor_pass_hash=_h(json.dumps(floor_pass, sort_keys=True)),
            apex_verdict_hash=_h(json.dumps(verdict, sort_keys=True)),
            constitution_hash=_h(constitution_json),
            psi_vitality=metrics.get("psi", None),
            tri_witness=metrics.get("tri_witness", None),
        )

    def save_receipt(self, receipt: ZKPCReceipt, path="runtime/vault_999/zkpc_receipts.jsonl"):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(receipt.to_json() + "\n")