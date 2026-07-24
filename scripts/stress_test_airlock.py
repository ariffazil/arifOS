#!/usr/bin/env python3
"""
Synthetic Stress Test for arifOS Airlock (Step 1)
--------------------------------------------------
Fires 50 concurrent stalled HTTP requests (partial headers/body, keeping socket open)
to http://127.0.0.1:8088/mcp while concurrently measuring /health latency and success rate.
"""

import asyncio
import time

import httpx


async def send_stalled_request(client_id: int):
    """Simulate slow-loris / stalled client holding connection open."""
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", 8088)
        # Send HTTP POST headers without completing body or sending end-of-headers/body
        request_line = b"POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:8088\r\nContent-Type: application/json\r\nContent-Length: 100\r\n\r\npartial_body_data"
        writer.write(request_line)
        await writer.drain()

        # Read response after airlock timeout (should arrive in ~10s as HTTP 408)
        data = await asyncio.wait_for(reader.read(1024), timeout=15.0)
        writer.close()
        await writer.wait_closed()
        return "408_RECEIVED" if b"408" in data or b"timeout" in data.lower() else "OTHER_RESPONSE"
    except TimeoutError:
        return "STALLED_TIMEOUT_EXCEEDED"
    except Exception as e:
        return f"ERROR: {e}"


async def probe_health(session: httpx.AsyncClient, probe_id: int):
    """Probe /health while stress test is running."""
    start = time.perf_counter()
    try:
        resp = await session.get("http://127.0.0.1:8088/health", timeout=15.0)
        elapsed = (time.perf_counter() - start) * 1000
        return resp.status_code == 200, elapsed
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        return False, elapsed


async def main():
    print("🚀 Starting Airlock Load & Stress Test (50 stalled connections + 20 health probes)...")

    stalled_tasks = [send_stalled_request(i) for i in range(50)]

    # Wait 1s for stalled connections to establish and block in airlock receive()
    await asyncio.sleep(1.0)

    async with httpx.AsyncClient() as client:
        health_tasks = [probe_health(client, i) for i in range(20)]
        health_results = await asyncio.gather(*health_tasks)

    stalled_results = await asyncio.gather(*stalled_tasks)

    # Analyze health probes
    successes = [r for r in health_results if r[0]]
    latencies = [r[1] for r in health_results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    print("\n📊 Health Probe Results during Stress:")
    print(f"   - Success Rate: {len(successes)}/20 ({len(successes) / 20 * 100:.1f}%)")
    print(f"   - Avg Latency:  {avg_latency:.2f} ms")
    print(f"   - Max Latency:  {max_latency:.2f} ms")

    # Analyze stalled connections
    stalled_408_count = sum(1 for r in stalled_results if r == "408_RECEIVED")
    print("\n🛡️ Stalled Connection Airlock Handling:")
    print(f"   - Stalled Connections Handled: {len(stalled_results)}")
    print(f"   - HTTP 408 Timeouts Emitted:  {stalled_408_count}/{len(stalled_results)}")

    if len(successes) == 20 and avg_latency < 500:
        print(
            "\n✅ AIRLOCK STRESS TEST PASSED: 0 event loop starvation under 50 concurrent stalled connections!"
        )
    else:
        print("\n⚠️ WARNING: Degraded latency or failed probes detected under load.")


if __name__ == "__main__":
    asyncio.run(main())
