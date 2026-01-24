#!/usr/bin/env python3
"""
arifOS Burn-In Monitor (72-hour Constitutional Validation)

Monitors the Trinity MCP server during staging burn-in period.
Tracks:
- Health check responses
- Tool invocation latency
- Floor violation rates
- Verdict distribution
- Memory/ledger integrity

DITEMPA BUKAN DIBERI
"""

import asyncio
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import httpx

# =============================================================================
# CONFIGURATION
# =============================================================================

TRINITY_URL = os.environ.get("TRINITY_URL", "http://localhost:8000")
BURN_IN_HOURS = int(os.environ.get("BURN_IN_HOURS", "72"))
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL_SECONDS", "60"))
ALERT_WEBHOOK = os.environ.get("ALERT_WEBHOOK", "")
REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", "/app/reports"))


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class HealthCheck:
    """Single health check result."""
    timestamp: str
    status: str  # UP, DOWN, DEGRADED
    latency_ms: float
    details: Dict = field(default_factory=dict)


@dataclass
class BurnInReport:
    """Comprehensive burn-in report."""
    start_time: str
    end_time: str
    duration_hours: float
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percent: float
    avg_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    verdict_distribution: Dict[str, int] = field(default_factory=dict)
    floor_violations: Dict[str, int] = field(default_factory=dict)
    alerts_triggered: int = 0
    status: str = "RUNNING"  # RUNNING, PASSED, FAILED


# =============================================================================
# MONITOR
# =============================================================================

class BurnInMonitor:
    """72-hour burn-in monitor for arifOS Trinity."""

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + timedelta(hours=BURN_IN_HOURS)
        self.checks: List[HealthCheck] = []
        self.report = BurnInReport(
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            duration_hours=BURN_IN_HOURS,
            total_checks=0,
            successful_checks=0,
            failed_checks=0,
            uptime_percent=0.0,
            avg_latency_ms=0.0,
            max_latency_ms=0.0,
            min_latency_ms=float('inf')
        )
        self.client = httpx.AsyncClient(timeout=30.0)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    async def health_check(self) -> HealthCheck:
        """Perform a single health check."""
        start = time.time()
        try:
            response = await self.client.get(f"{TRINITY_URL}/health")
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                status = "UP" if data.get("status") == "healthy" else "DEGRADED"
            else:
                status = "DEGRADED"
                data = {"error": f"HTTP {response.status_code}"}

            return HealthCheck(
                timestamp=datetime.utcnow().isoformat(),
                status=status,
                latency_ms=latency,
                details=data
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthCheck(
                timestamp=datetime.utcnow().isoformat(),
                status="DOWN",
                latency_ms=latency,
                details={"error": str(e)}
            )

    async def test_tools(self) -> Dict:
        """Test all 5 Trinity tools."""
        results = {}

        tools = [
            ("000_init", {"action": "validate"}),
            ("agi_genius", {"action": "sense", "query": "burn-in test"}),
            ("asi_act", {"action": "evidence", "text": "burn-in test"}),
            ("apex_judge", {"action": "judge", "query": "burn-in test"}),
            ("999_vault", {"action": "list", "target": "ledger"}),
        ]

        for tool_name, payload in tools:
            start = time.time()
            try:
                response = await self.client.post(
                    f"{TRINITY_URL}/tools/{tool_name}",
                    json=payload
                )
                latency = (time.time() - start) * 1000
                results[tool_name] = {
                    "status": "OK" if response.status_code == 200 else "ERROR",
                    "latency_ms": latency,
                    "response": response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "ERROR",
                    "latency_ms": (time.time() - start) * 1000,
                    "error": str(e)
                }

        return results

    async def get_metrics(self) -> Optional[Dict]:
        """Fetch metrics from the server."""
        try:
            response = await self.client.get(f"{TRINITY_URL}/metrics")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    def update_report(self, check: HealthCheck):
        """Update the burn-in report with new check."""
        self.checks.append(check)
        self.report.total_checks += 1

        if check.status == "UP":
            self.report.successful_checks += 1
        else:
            self.report.failed_checks += 1

        # Update latency stats
        latencies = [c.latency_ms for c in self.checks]
        self.report.avg_latency_ms = sum(latencies) / len(latencies)
        self.report.max_latency_ms = max(latencies)
        self.report.min_latency_ms = min(latencies)

        # Calculate uptime
        self.report.uptime_percent = (
            self.report.successful_checks / self.report.total_checks * 100
        )

    async def send_alert(self, message: str):
        """Send alert via webhook."""
        if not ALERT_WEBHOOK:
            print(f"[ALERT] {message}")
            return

        try:
            await self.client.post(ALERT_WEBHOOK, json={
                "text": f"[arifOS Burn-In] {message}",
                "timestamp": datetime.utcnow().isoformat()
            })
            self.report.alerts_triggered += 1
        except Exception as e:
            print(f"[ALERT FAILED] {e}")

    def save_report(self):
        """Save current report to file."""
        report_file = REPORTS_DIR / f"burn_in_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(asdict(self.report), f, indent=2)

        # Also save latest
        latest_file = REPORTS_DIR / "burn_in_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(self.report), f, indent=2)

    async def run(self):
        """Run the burn-in monitor."""
        print(f"=" * 60)
        print(f"arifOS Burn-In Monitor Started")
        print(f"=" * 60)
        print(f"Target: {TRINITY_URL}")
        print(f"Duration: {BURN_IN_HOURS} hours")
        print(f"Check Interval: {CHECK_INTERVAL} seconds")
        print(f"Start: {self.start_time.isoformat()}")
        print(f"End: {self.end_time.isoformat()}")
        print(f"=" * 60)

        consecutive_failures = 0
        max_consecutive_failures = 5

        try:
            while datetime.utcnow() < self.end_time:
                # Health check
                check = await self.health_check()
                self.update_report(check)

                # Log status
                status_icon = {"UP": "+", "DEGRADED": "~", "DOWN": "!"}[check.status]
                print(f"[{check.timestamp}] {status_icon} {check.status} ({check.latency_ms:.1f}ms)")

                # Track consecutive failures
                if check.status == "DOWN":
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        await self.send_alert(
                            f"CRITICAL: {consecutive_failures} consecutive failures!"
                        )
                else:
                    consecutive_failures = 0

                # Alert on high latency
                if check.latency_ms > 5000:
                    await self.send_alert(f"High latency: {check.latency_ms:.1f}ms")

                # Periodic tool test (every 10 checks)
                if self.report.total_checks % 10 == 0:
                    tool_results = await self.test_tools()
                    failed_tools = [k for k, v in tool_results.items() if v["status"] != "OK"]
                    if failed_tools:
                        await self.send_alert(f"Tool failures: {failed_tools}")

                # Periodic metrics check
                if self.report.total_checks % 5 == 0:
                    metrics = await self.get_metrics()
                    if metrics:
                        self.report.verdict_distribution = metrics.get("verdicts", {})
                        self.report.floor_violations = metrics.get("floor_violations", {})

                # Save report periodically
                if self.report.total_checks % 10 == 0:
                    self.save_report()

                await asyncio.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[!] Burn-in interrupted by user")
            self.report.status = "INTERRUPTED"

        # Final report
        self.report.end_time = datetime.utcnow().isoformat()

        if self.report.uptime_percent >= 99.9:
            self.report.status = "PASSED"
        elif self.report.uptime_percent >= 99.0:
            self.report.status = "PASSED_WITH_WARNINGS"
        else:
            self.report.status = "FAILED"

        self.save_report()

        print(f"\n{'=' * 60}")
        print(f"BURN-IN COMPLETE: {self.report.status}")
        print(f"{'=' * 60}")
        print(f"Duration: {self.report.duration_hours} hours")
        print(f"Total Checks: {self.report.total_checks}")
        print(f"Uptime: {self.report.uptime_percent:.2f}%")
        print(f"Avg Latency: {self.report.avg_latency_ms:.1f}ms")
        print(f"Alerts: {self.report.alerts_triggered}")
        print(f"{'=' * 60}")

        await self.client.aclose()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    monitor = BurnInMonitor()
    asyncio.run(monitor.run())
