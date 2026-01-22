# Time-based governance utilities (optional)

from datetime import datetime, timedelta

def now_iso():
    """Return the current time as an ISO8601 string."""
    return datetime.now().isoformat()

def cooling_period_elapsed(start_iso, hours=72):
    """
    Check if a cooling period (default 72 hours) has elapsed since the given start time.
    Returns True if the current time is at least `hours` hours past `start_iso`.
    """
    try:
        start_time = datetime.fromisoformat(start_iso)
    except Exception:
        return False
    return datetime.now() - start_time >= timedelta(hours=hours)
