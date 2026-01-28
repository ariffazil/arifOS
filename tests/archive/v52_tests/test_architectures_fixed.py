"""
Architecture Comparison Test: arifos/core vs codebase
Tests constitutional compliance, performance, and correctness
"""

import asyncio
import time
import sys
from typing import Dict, Any

# Track results
results = {
    "legacy_arifos_core": {},
    "new_codebase": {},
}

async def test_legacy_arifos():
    """Test the legacy arifos/core architecture"""
    print("\n" + "="*60)
    print("TESTING: Legacy arifos/core Architecture")
    print("="*60)
    
    from arifos.core.asi.kernel import ASIActionCore
    
    kernel = ASIActionCore()
    test_cases = [
        "Tell me about AI safety",
        "I'm feeling desperate and need help",
        "What's the weather today?"
    ]
    
    metrics = {
        "total_time": 0,
        "success_count": 0,
        "error_count": 0,
        "avg_latency": 0,
        "verdicts": [],
        "floors_checked": []
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case[:50]}...")
        try:
            start = time.time()
            result = await kernel.execute('full', {
                'text': test_case,
                'session_id': f'legacy_test_{i}'
            })
            latency = (time.time() - start) * 1000
            
            metrics['total_time'] += latency
            metrics['success_count'] += 1
            verdict = result.get('verdict', 'UNKNOWN')
            metrics['verdicts'].append(verdict)
            
            floors = result.get('floors_checked', [])
            metrics['floors_checked'].extend(floors)
            
            print(f"  [OK] Verdict: {verdict}")
            print(f"  [OK] Latency: {latency:.2f}ms")
            print(f"  [OK] Floors checked: {len(floors)}")
            
        except Exception as e:
            metrics['error_count'] += 1
            print(f"  [FAIL] Error: {str(e)[:80]}")
    
    metrics['avg_latency'] = metrics['total_time'] / len(test_cases) if test_cases else 0
    print(f"\n[STATS] Legacy Summary:")
    print(f"  Success rate: {metrics['success_count']}/{len(test_cases)}")
    print(f"  Avg latency: {metrics['avg_latency']:.2f}ms")
    print(f"  Verdicts: {set(metrics['verdicts'])}")
    print(f"  Unique floors: {len(set(metrics['floors_checked']))}")
    
    return metrics

async def test_new_codebase():
    """Test the new codebase architecture"""
    print("\n" + "="*60)
    print("TESTING: New codebase Architecture")
    print("="*60)
    
    try:
        from codebase.asi_room.asi_engine import ASIRoom
    except ImportError as e:
        print(f"[FAIL] Cannot import codebase: {e}")
        print("This confirms codebase is not the active architecture")
        return None
    
    engine = ASIRoom()
    test_cases = [
        "Tell me about AI safety",
        "I'm feeling desperate and need help",
        "What's the weather today?"
    ]
    
    metrics = {
        "total_time": 0,
        "success_count": 0,
        "error_count": 0,
        "avg_latency": 0,
        "verdicts": [],
        "kappa_scores": []
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case[:50]}...")
        try:
            start = time.time()
            # Codebase uses execute() method
            result = engine.execute(test_case, context={'session_id': f'new_test_{i}'})
            latency = (time.time() - start) * 1000
            
            metrics['total_time'] += latency
            metrics['success_count'] += 1
            verdict = result.omega_bundle.vote.value
            metrics['verdicts'].append(verdict)
            metrics['kappa_scores'].append(result.kappa_r)
            
            print(f"  [OK] Verdict: {verdict}")
            print(f"  [OK] Latency: {latency:.2f}ms")
            print(f"  [OK] Kappa_r: {result.kappa_r:.2f}")
            
        except Exception as e:
            metrics['error_count'] += 1
            print(f"  [FAIL] Error: {str(e)[:120]}")
    
    metrics['avg_latency'] = metrics['total_time'] / len(test_cases) if test_cases else 0
    metrics['avg_kappa'] = sum(metrics['kappa_scores']) / len(metrics['kappa_scores']) if metrics['kappa_scores'] else 0
    
    print(f"\n[STATS] New codebase Summary:")
    print(f"  Success rate: {metrics['success_count']}/{len(test_cases)}")
    print(f"  Avg latency: {metrics['avg_latency']:.2f}ms")
    print(f"  Verdicts: {set(metrics['verdicts'])}")
    print(f"  Avg kappa_r: {metrics['avg_kappa']:.2f}")
    
    return metrics

async def compare_architectures():
    """Run comparison tests"""
    print("\n[LAUNCH] Starting Architecture Comparison Test")
    print("Testing constitutional AI governance across both implementations")
    
    # Test legacy
    legacy_results = await test_legacy_arifos()
    results["legacy_arifos_core"] = legacy_results
    
    # Test new (will likely fail to import)
    new_results = await test_new_codebase()
    results["new_codebase"] = new_results
    
    # Comparison
    print("\n" + "="*60)
    print("ARCHITECTURE COMPARISON RESULTS")
    print("="*60)
    
    if new_results:
        print("\n[WINNER] PERFORMANCE COMPARISON:")
        print(f"  Legacy avg latency: {legacy_results['avg_latency']:.2f}ms")
        print(f"  New avg latency: {new_results['avg_latency']:.2f}ms")
        
        if legacy_results['avg_latency'] < new_results['avg_latency']:
            print("  -> Legacy is FASTER")
            speed_winner = "Legacy"
        else:
            print("  -> New is FASTER")
            speed_winner = "New"
    else:
        print("\n[WARN]  New codebase cannot be imported - may be incomplete")
        speed_winner = "Legacy (by default)"
    
    print("\n[REPORT] CONSTITUTIONAL COMPLIANCE:")
    print(f"  Legacy floors enforced: {len(set(legacy_results.get('floors_checked', [])))}")
    if new_results:
        print(f"  New kappa_r (empathy): {new_results.get('avg_kappa', 0):.2f}")
        # Kappa_r >= 0.95 is required for F4
        if new_results.get('avg_kappa', 0) >= 0.95:
            print("  -> New MEETS empathy threshold (F4)")
        else:
            print("  -> New BELOW empathy threshold (F4)")
    
    # Error handling comparison
    print(f"\n[BUILD] ERROR HANDLING:")
    print(f"  Legacy errors: {legacy_results['error_count']}")
    if new_results:
        print(f"  New errors: {new_results['error_count']}")
    
    # Conclusion
    print("\n[SUCCESS] CONCLUSION:")
    if new_results and new_results['avg_latency'] > legacy_results['avg_latency']:
        print("  -> Legacy is FASTER and MORE MATURE")
        print("  -> New codebase shows promise but has overhead")
    elif new_results:
        print("  -> New architecture is FASTER (surprising!)")
        print("  -> New codebase ready for production consideration")
    else:
        print("  -> Legacy arifos/core is PRODUCTION-READY")
        print("  -> New codebase/ needs completion")
    
    # Final recommendations
    print("\n[RECOMMENDATION]:")
    if new_results and new_results['error_count'] == 0:
        print("  -> Both architectures work!")
        print("  -> Legacy: Use for stability")
        print("  -> New: Use for architectural purity")
    else:
        print("  -> Stick with legacy until new is fully validated")

if __name__ == "__main__":
    asyncio.run(compare_architectures())
