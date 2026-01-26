#!/usr/bin/env python3
"""
Quick test for LiveMetricsService integration
"""

import sys
try:
    from arifos.core.integration.api.services.live_metrics_service import get_live_metrics_service
    
    print("🔍 Testing LiveMetricsService...")
    service = get_live_metrics_service()
    metrics = service.get_live_metrics(use_cache=False)
    
    print("✅ LiveMetricsService working")
    print(f'📊 tau (Truth): {metrics.tau:.4f}')
    print(f'❤️ kappa_r (Empathy): {metrics.kappa_r:.4f}')
    print(f'🌟 psi (Vitality): {metrics.psi:.4f}')
    print(f'⚡ entropy_delta (Clarity): {metrics.entropy_delta:.4f}')
    print(f'✅ seal_rate: {metrics.seal_rate:.2%}')
    print(f'❌ void_rate: {metrics.void_rate:.2%}')
    print(f'👥 active_sessions: {metrics.active_sessions}')
    print(f'⏱️ uptime_hours: {metrics.uptime_hours:.2f}h')
    print(f'📈 floors_passed: {metrics.floors_passed}')
    print(f'📉 floors_failed: {metrics.floors_failed}')
    print(f'🔥 sabar_triggered: {metrics.sabar_triggered}')
    print(f'🕒 timestamp: {metrics.timestamp}')
    
    # Verify all values are computed (not None)
    assert metrics.tau is not None, "tau should not be None"
    assert metrics.kappa_r is not None, "kappa_r should not be None"
    assert metrics.psi is not None, "psi should not be None"
    assert metrics.entropy_delta is not None, "entropy_delta should not be None"
    
    print("\n🎉 All metrics computed successfully!")
    print("📊 Dashboard is now LIVE with real constitutional metrics!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
