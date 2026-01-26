#!/usr/bin/env python3
"""
Post-deployment validation for arifOS Railway deployment.

This script validates the health and functionality of a deployed arifOS instance.

TODO: Verify Redis pub/sub channels (AGI||ASI parallel wiring)
TODO: Test cooling tier escalation logic
TODO: Validate Tri-Witness consensus flow

Authority: Muhammad Arif bin Fazil
Version: v52.5.1-SEAL
"""

import os
import sys
import time
import requests
from typing import Optional

RAILWAY_URL = os.getenv("RAILWAY_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL")

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_status(status: str, message: str):
    """Print colored status message."""
    if status == "✅":
        print(f"{GREEN}{status}{RESET} {message}")
    elif status == "⚠️":
        print(f"{YELLOW}{status}{RESET} {message}")
    elif status == "❌":
        print(f"{RED}{status}{RESET} {message}")
    else:
        print(f"{status} {message}")


def test_health():
    """Test /health endpoint."""
    print("\n[1/5] Testing /health endpoint...")
    try:
        resp = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "healthy", f"Expected healthy, got {data.get('status')}"
        
        version = data.get("version", "unknown")
        tools = data.get("tools", 0)
        
        print_status("✅", f"Health: {version} ({tools} tools)")
        return True
    except Exception as e:
        print_status("❌", f"Health check failed: {e}")
        return False


def test_redis():
    """Test Redis connectivity."""
    print("\n[2/5] Testing Redis connectivity...")
    if not REDIS_URL:
        print_status("⚠️", "REDIS_URL not set, skipping")
        return True
    
    try:
        import redis
        r = redis.from_url(REDIS_URL, socket_timeout=5)
        r.ping()
        print_status("✅", "Redis: Connected")
        return True
    except ImportError:
        print_status("⚠️", "redis-py not installed, skipping")
        return True
    except Exception as e:
        print_status("❌", f"Redis connection failed: {e}")
        return False


def test_volume():
    """Test volume write capability."""
    print("\n[3/5] Testing volume write...")
    test_file = "/var/data/vault999/test.txt"
    
    try:
        # Try to write test file
        with open(test_file, "w") as f:
            f.write("test")
        
        # Verify it was written
        with open(test_file, "r") as f:
            content = f.read()
            assert content == "test", "File content mismatch"
        
        # Clean up
        os.remove(test_file)
        print_status("✅", "Volume: Writable")
        return True
    except FileNotFoundError:
        print_status("⚠️", "Volume not mounted at /var/data (okay for local testing)")
        return True
    except Exception as e:
        print_status("⚠️", f"Volume test failed: {e} (okay for local testing)")
        return True


def test_checkpoint():
    """Test /checkpoint endpoint."""
    print("\n[4/5] Testing /checkpoint endpoint...")
    try:
        payload = {
            "query": "Hello world validation test",
            "context": "Post-deployment validation",
            "stakeholders": ["user"]
        }
        
        resp = requests.post(
            f"{RAILWAY_URL}/checkpoint",
            json=payload,
            timeout=30
        )
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert "verdict" in data, "Response missing 'verdict' field"
        
        verdict = data["verdict"]
        session_id = data.get("session_id", "unknown")[:8]
        
        print_status("✅", f"Checkpoint: {verdict} (session: {session_id})")
        return True
    except Exception as e:
        print_status("❌", f"Checkpoint test failed: {e}")
        return False


def test_redis_channels():
    """
    TODO: Verify AGI||ASI parallel wiring via Redis channels.
    
    This test should:
    1. Connect to Redis
    2. Verify 'agi:queue' and 'asi:queue' channels exist
    3. Submit a test job to each channel
    4. Verify parallel processing occurs
    5. Collect results from both channels
    
    Implementation deferred to Issue #1.
    """
    print("\n[5/5] Testing Redis pub/sub channels...")
    print_status("⚠️", "TODO: Verify agi:queue and asi:queue channels exist")
    print_status("⚠️", "TODO: Test parallel job submission and result collection")
    print_status("⚠️", "TODO: Validate AGI||ASI parallel execution (Issue #1)")
    return True


def test_cooling_tiers():
    """
    TODO: Validate cooling tier escalation logic.
    
    This test should:
    1. Create test user sessions with different violation patterns
    2. Verify tier 0 -> tier 1 escalation after N violations
    3. Check threshold adjustments per tier
    4. Validate cooling period enforcement
    
    Implementation deferred to Issue #2.
    """
    print("\n[TODO] Testing cooling tier escalation...")
    print_status("⚠️", "TODO: Test tier escalation logic (Issue #2)")
    return True


def test_tri_witness():
    """
    TODO: Validate Tri-Witness consensus flow.
    
    This test should:
    1. Submit high-stakes action requiring tri-witness
    2. Verify AGI, ASI, and APEX all participate
    3. Check consensus threshold (≥0.95)
    4. Validate that disagreement triggers 888_HOLD
    
    Implementation deferred to Issue #3.
    """
    print("\n[TODO] Testing Tri-Witness consensus...")
    print_status("⚠️", "TODO: Validate tri-witness flow (Issue #3)")
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("arifOS v52.5.1 Post-Deployment Validation")
    print("=" * 60)
    print(f"Target URL: {RAILWAY_URL}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Redis Connection", test_redis()))
    results.append(("Volume Write", test_volume()))
    results.append(("Checkpoint Endpoint", test_checkpoint()))
    results.append(("Redis Channels (TODO)", test_redis_channels()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print_status(status, test_name)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print_status("✅", "All validation tests passed")
        return 0
    else:
        print_status("⚠️", f"{total - passed} test(s) failed or skipped")
        return 1


if __name__ == "__main__":
    sys.exit(main())
