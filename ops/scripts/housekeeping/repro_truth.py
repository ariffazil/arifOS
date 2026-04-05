from arifosmcp.runtime.models import RuntimeEnvelope, CanonicalMetrics, TelemetryVitals
import json

def test_truth_property():
    metrics_dict = {
        "telemetry": {
            "dS": -0.1,
            "peace2": 1.0,
            "G_star": 0.85,
            "shadow": 0.15,
            "confidence": 0.85,
            "psi_le": "0.8 (Estimate Only)",
            "verdict": "Alive"
        }
    }
    
    # Test 1: Direct object
    m = CanonicalMetrics(**metrics_dict)
    print(f"Direct object truth: {m.truth}")
    
    # Test 2: Via RuntimeEnvelope
    envelope_dict = {
        "ok": True,
        "tool": "test",
        "stage": "000_INIT",
        "metrics": metrics_dict
    }
    
    env = RuntimeEnvelope(**envelope_dict)
    print(f"Envelope metrics truth: {env.metrics.truth}")
    
    # Test 3: model_dump mode="json" and back
    dumped = env.model_dump(mode="json")
    print(f"Dumped metrics truth present? {'truth' in dumped['metrics']}")
    
    env2 = RuntimeEnvelope(**dumped)
    print(f"Reconstructed metrics truth: {env2.metrics.truth}")

if __name__ == "__main__":
    try:
        test_truth_property()
        print("Test PASSED")
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
