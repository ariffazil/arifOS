#!/usr/bin/env python3
"""
Test LiveMetricsService in isolation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Test imports
try:
    from pathlib import Path
    from arifos.core.integration.api.services.live_metrics_service import LiveMetricsService
    
    print("Testing LiveMetricsService...")
    
    # Create service with test ledger path
    ledger_path = Path("./VAULT999/BBB_LEDGER/cooling_ledger.jsonl")
    service = LiveMetricsService(cooling_ledger_path=ledger_path, metrics_window_minutes=60)
    
    # Get metrics
    metrics = service.get_live_metrics(use_cache=False)
    
    print(f"tau: {metrics.tau}")
    print(f"kappa_r: {metrics.kappa_r}")
    print(f"psi: {metrics.psi}")
    print(f"entropy_delta: {metrics.entropy_delta}")
    print(f"seal_rate: {metrics.seal_rate}")
    print(f"SUCCESS: All metrics computed")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
