"""
Live System Metrics — Reconstruction A Foundation / Track 3
═════════════════════════════════════════════════════════════

Reads CPU, memory, disk, and process metrics from live system sources.
Hard rule: if a source is unavailable, report UNVERIFIED — never fabricate.

Sources (in priority order):
  1. psutil (preferred — cross-platform)
  2. /proc (Linux fallback)
  3. df / statfs (disk fallback)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import os
import shutil
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class MetricSource:
    PSUTIL = "psutil"
    PROC = "proc"
    DF = "df"
    UNVERIFIED = "unverified"


class LiveMetrics:
    """
    Live system metrics with source attribution.

    Every field includes:
      - value: the numeric reading (or None if unavailable)
      - unit: percent, bytes, seconds, etc.
      - source: where the reading came from
      - verified: False if the reading could not be obtained
    """

    def __init__(self) -> None:
        self.timestamp = datetime.now(UTC).isoformat()
        self._psutil_available = self._check_psutil()

    def _check_psutil(self) -> bool:
        try:
            import psutil  # noqa: F401
            return True
        except ImportError:
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # CPU
    # ═══════════════════════════════════════════════════════════════════════

    def cpu_percent(self, interval: float = 0.5) -> dict[str, Any]:
        """CPU utilization percentage."""
        if self._psutil_available:
            try:
                import psutil

                val = psutil.cpu_percent(interval=interval)
                return {
                    "value": round(val, 1),
                    "unit": "percent",
                    "scope": "system",
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                    "sample_window_sec": interval,
                }
            except Exception as e:
                logger.debug(f"psutil cpu_percent failed: {e}")

        # /proc fallback
        try:
            with open("/proc/stat") as f:
                line = f.readline()
            fields = line.split()
            if fields[0] == "cpu" and len(fields) >= 5:
                user = float(fields[1])
                nice = float(fields[2])
                system = float(fields[3])
                idle = float(fields[4])
                total = user + nice + system + idle
                if total > 0:
                    pct = 100.0 * (1.0 - idle / total)
                    return {
                        "value": round(pct, 1),
                        "unit": "percent",
                        "scope": "system",
                        "source": MetricSource.PROC,
                        "verified": True,
                        "sample_window_sec": 0,
                        "note": "single-sample /proc/stat",
                    }
        except Exception as e:
            logger.debug(f"/proc/stat cpu fallback failed: {e}")

        return {
            "value": None,
            "unit": "percent",
            "scope": "system",
            "source": MetricSource.UNVERIFIED,
            "verified": False,
            "note": "CPU metrics unavailable — psutil missing and /proc unreadable",
        }

    def cpu_count(self) -> dict[str, Any]:
        """Logical CPU count."""
        if self._psutil_available:
            try:
                import psutil

                return {
                    "value": psutil.cpu_count(logical=True),
                    "physical": psutil.cpu_count(logical=False),
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                }
            except Exception:
                pass
        try:
            with open("/proc/cpuinfo") as f:
                count = sum(1 for line in f if line.startswith("processor"))
            return {
                "value": count,
                "source": MetricSource.PROC,
                "verified": True,
            }
        except Exception:
            pass
        return {
            "value": None,
            "source": MetricSource.UNVERIFIED,
            "verified": False,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Memory
    # ═══════════════════════════════════════════════════════════════════════

    def memory(self) -> dict[str, Any]:
        """System memory utilization."""
        if self._psutil_available:
            try:
                import psutil

                vm = psutil.virtual_memory()
                return {
                    "percent": {
                        "value": round(vm.percent, 1),
                        "unit": "percent",
                        "source": MetricSource.PSUTIL,
                        "verified": True,
                    },
                    "total_bytes": vm.total,
                    "available_bytes": vm.available,
                    "used_bytes": vm.used,
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                }
            except Exception as e:
                logger.debug(f"psutil virtual_memory failed: {e}")

        # /proc/meminfo fallback
        try:
            meminfo: dict[str, int] = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        meminfo[key.strip()] = int(val.strip().split()[0]) * 1024
            total = meminfo.get("MemTotal", 0)
            available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
            used = total - available
            pct = 100.0 * used / total if total > 0 else 0.0
            return {
                "percent": {
                    "value": round(pct, 1),
                    "unit": "percent",
                    "source": MetricSource.PROC,
                    "verified": True,
                },
                "total_bytes": total,
                "available_bytes": available,
                "used_bytes": used,
                "source": MetricSource.PROC,
                "verified": True,
            }
        except Exception as e:
            logger.debug(f"/proc/meminfo fallback failed: {e}")

        return {
            "percent": {
                "value": None,
                "unit": "percent",
                "source": MetricSource.UNVERIFIED,
                "verified": False,
                "note": "Memory metrics unavailable",
            },
            "source": MetricSource.UNVERIFIED,
            "verified": False,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Disk
    # ═══════════════════════════════════════════════════════════════════════

    def disk(self, path: str = "/") -> dict[str, Any]:
        """Disk utilization for the given mount point."""
        if self._psutil_available:
            try:
                import psutil

                du = psutil.disk_usage(path)
                pct = 100.0 * du.used / du.total if du.total > 0 else 0.0
                return {
                    "percent": {
                        "value": round(pct, 1),
                        "unit": "percent",
                        "mount": path,
                        "source": MetricSource.PSUTIL,
                        "verified": True,
                    },
                    "total_bytes": du.total,
                    "used_bytes": du.used,
                    "free_bytes": du.free,
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                }
            except Exception as e:
                logger.debug(f"psutil disk_usage failed: {e}")

        # shutil fallback (cross-platform, no psutil needed)
        try:
            du = shutil.disk_usage(path)
            pct = 100.0 * du.used / du.total if du.total > 0 else 0.0
            return {
                "percent": {
                    "value": round(pct, 1),
                    "unit": "percent",
                    "mount": path,
                    "source": MetricSource.DF,
                    "verified": True,
                },
                "total_bytes": du.total,
                "used_bytes": du.used,
                "free_bytes": du.free,
                "source": MetricSource.DF,
                "verified": True,
            }
        except Exception as e:
            logger.debug(f"shutil.disk_usage fallback failed: {e}")

        return {
            "percent": {
                "value": None,
                "unit": "percent",
                "mount": path,
                "source": MetricSource.UNVERIFIED,
                "verified": False,
                "note": "Disk metrics unavailable",
            },
            "source": MetricSource.UNVERIFIED,
            "verified": False,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Network
    # ═══════════════════════════════════════════════════════════════════════

    def network_io(self) -> dict[str, Any]:
        """Network I/O counters."""
        if self._psutil_available:
            try:
                import psutil

                io = psutil.net_io_counters()
                return {
                    "bytes_sent": io.bytes_sent,
                    "bytes_recv": io.bytes_recv,
                    "packets_sent": io.packets_sent,
                    "packets_recv": io.packets_recv,
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                }
            except Exception as e:
                logger.debug(f"psutil net_io_counters failed: {e}")

        return {
            "bytes_sent": None,
            "bytes_recv": None,
            "source": MetricSource.UNVERIFIED,
            "verified": False,
            "note": "Network metrics unavailable",
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Process
    # ═══════════════════════════════════════════════════════════════════════

    def process_info(self, pid: int | None = None) -> dict[str, Any]:
        """Current process or specified process info."""
        pid = pid or os.getpid()
        if self._psutil_available:
            try:
                import psutil

                p = psutil.Process(pid)
                mem = p.memory_info()
                return {
                    "pid": pid,
                    "cpu_percent": p.cpu_percent(interval=0.1),
                    "memory_rss_bytes": mem.rss,
                    "memory_vms_bytes": mem.vms,
                    "num_threads": p.num_threads(),
                    "create_time": p.create_time(),
                    "source": MetricSource.PSUTIL,
                    "verified": True,
                }
            except Exception as e:
                logger.debug(f"psutil Process failed: {e}")

        # /proc fallback
        try:
            with open(f"/proc/{pid}/stat") as f:
                parts = f.read().split()
            with open(f"/proc/{pid}/status") as f:
                status_lines = f.readlines()
            rss_pages = int(parts[23]) if len(parts) > 23 else 0
            page_size = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096
            threads = 0
            for line in status_lines:
                if line.startswith("Threads:"):
                    threads = int(line.split()[1])
                    break
            return {
                "pid": pid,
                "memory_rss_bytes": rss_pages * page_size,
                "num_threads": threads,
                "source": MetricSource.PROC,
                "verified": True,
            }
        except Exception as e:
            logger.debug(f"/proc/{pid} fallback failed: {e}")

        return {
            "pid": pid,
            "source": MetricSource.UNVERIFIED,
            "verified": False,
            "note": "Process metrics unavailable",
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Full health snapshot
    # ═══════════════════════════════════════════════════════════════════════

    def health_snapshot(self) -> dict[str, Any]:
        """Complete system health snapshot."""
        cpu = self.cpu_percent()
        mem = self.memory()
        disk = self.disk("/")
        net = self.network_io()
        proc = self.process_info()

        # Determine overall status
        verified = all(
            x.get("verified") is True
            for x in [cpu, mem, disk, net, proc]
        )
        any_unverified = any(
            x.get("verified") is False
            for x in [cpu, mem, disk, net, proc]
        )

        if verified:
            status = "healthy"
        elif any_unverified:
            status = "degraded"
        else:
            status = "unknown"

        # Band classification
        cpu_val = cpu.get("value")
        mem_val = mem.get("percent", {}).get("value")
        disk_val = disk.get("percent", {}).get("value")

        def band(val: float | None, low: float, high: float) -> str:
            if val is None:
                return "unverified"
            if val < low:
                return "low"
            if val < high:
                return "moderate"
            return "critical"

        return {
            "status": status,
            "verified": verified,
            "timestamp": self.timestamp,
            "cpu": cpu,
            "mem": mem,
            "disk": disk,
            "network": net,
            "process": proc,
            "bands": {
                "cpu": band(cpu_val, 50, 80),
                "mem": band(mem_val, 50, 80),
                "disk": band(disk_val, 70, 85),
            },
            "thresholds": {
                "healthy_cpu_max": 70,
                "healthy_mem_max": 80,
                "healthy_disk_max": 85,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# Singleton accessor
# ═══════════════════════════════════════════════════════════════════════════

_metrics_instance: LiveMetrics | None = None


def get_live_metrics() -> LiveMetrics:
    """Return the singleton LiveMetrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = LiveMetrics()
    return _metrics_instance
