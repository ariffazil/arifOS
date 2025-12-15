import datetime
from dataclasses import asdict
from typing import Dict, Any, List, Optional
from ..enforcement.metrics import Metrics
from ..system.apex_prime import ApexVerdict

def log_cooling_entry(
    job_id: str,
    verdict: ApexVerdict,
    metrics: Metrics,
    stakes: str = "normal",
    pipeline_path: Optional[List[str]] = None,
    context_summary: str = "",
    tri_witness_components: Optional[Dict[str, float]] = None,
    logger=None,
) -> Dict[str, Any]:
    """Create a Cooling Ledger entry (dict).

    Caller is responsible for persistence or streaming.
    """
    if pipeline_path is None:
        pipeline_path = []

    entry = {
        "ledger_version": "v35Ω",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "job_id": job_id,
        "stakes": stakes,
        "pipeline_path": pipeline_path,
        "metrics": asdict(metrics),
        "verdict": verdict,
        "tri_witness_components": tri_witness_components or {},
        "context_summary": context_summary,
    }

    if logger:
        logger.info("CoolingLedgerEntry: %s", entry)

    return entry
