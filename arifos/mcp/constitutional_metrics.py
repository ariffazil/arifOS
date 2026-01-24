# arifos/mcp/constitutional_metrics.py

from dataclasses import dataclass, field
import time
import threading
from collections import defaultdict
from typing import Dict, List, Optional

@dataclass
class Counter:
    name: str
    help: str
    _values: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, labels: Dict[str, str], value: float = 1.0):
        key = "_".join(f"{k}:{v}" for k, v in sorted(labels.items()))
        with self._lock:
            self._values[key] += value

@dataclass
class Histogram:
    name: str
    help: str
    _values: List[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float):
        with self._lock:
            self._values.append(value)

@dataclass
class Gauge:
    name: str
    help: str
    _value: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float):
        with self._lock:
            self._value = value

# Metrics
F11_COMMAND_AUTH = Counter('arifos_f11_total', 'F11 decisions')
CONSTITUTIONAL_REFLEX = Histogram('arifos_reflex_duration', 'Verdict latency')
SEAL_RATE = Gauge('arifos_seal_rate_1h', 'Rolling SEAL rate')

_VERDICTS: List[tuple] = []  # (timestamp, verdict)
_VERDICT_LOCK = threading.Lock()

def record_verdict(tool: str, verdict: str, duration: float, mode: str):
    """Record a verdict and its metadata."""
    F11_COMMAND_AUTH.inc({"verdict": verdict, "tool": tool, "mode": mode})
    CONSTITUTIONAL_REFLEX.observe(duration)
    
    with _VERDICT_LOCK:
        now = time.time()
        _VERDICTS.append((now, verdict))
        # Keep only last hour
        while _VERDICTS and _VERDICTS[0][0] < now - 3600:
            _VERDICTS.pop(0)
        
        # Calculate SEAL rate
        if _VERDICTS:
            seals = sum(1 for _, v in _VERDICTS if v == "SEAL")
            SEAL_RATE.set(seals / len(_VERDICTS))

def get_seal_rate() -> float:
    """Get the current rolling SEAL rate."""
    return SEAL_RATE._value
