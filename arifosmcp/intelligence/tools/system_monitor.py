from __future__ import annotations

from typing import Any


def _is_running_in_container() -> bool:
    return any(
        (
            __import__("os").path.exists("/.dockerenv"),
            __import__("os").path.exists("/run/.containerenv"),
        )
    )


def list_processes(
    filter_name: str | None = None,
    filter_user: str | None = None,
    min_cpu_percent: float = 0.0,
    min_memory_mb: float = 0.0,
    limit: int = 50,
    include_threads: bool = False,
) -> dict[str, Any]:
    try:
        import psutil

        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "username", "cpu_percent", "memory_info", "num_threads"]
        ):
            info = proc.info
            if filter_name and filter_name.lower() not in str(info.get("name", "")).lower():
                continue
            if filter_user and filter_user != info.get("username"):
                continue
            mem_mb = (getattr(info.get("memory_info"), "rss", 0) or 0) / (1024 * 1024)
            if (info.get("cpu_percent") or 0.0) < min_cpu_percent:
                continue
            if mem_mb < min_memory_mb:
                continue
            entry = {
                "pid": info.get("pid"),
                "name": info.get("name"),
                "user": info.get("username"),
                "cpu_percent": info.get("cpu_percent") or 0.0,
                "memory_mb": round(mem_mb, 2),
            }
            if include_threads:
                entry["threads"] = info.get("num_threads")
            processes.append(entry)
            if len(processes) >= limit:
                break
        return {"processes": processes}
    except Exception as exc:
        return {"error": str(exc), "processes": []}


def get_resource_usage(
    include_swap: bool = True,
    include_io: bool = False,
    include_temp: bool = False,
) -> dict[str, Any]:
    try:
        import psutil

        payload: dict[str, Any] = {
            "cpu_percent": psutil.cpu_percent(interval=0.0),
            "memory": dict(psutil.virtual_memory()._asdict()),
        }
        if include_swap:
            payload["swap"] = dict(psutil.swap_memory()._asdict())
        if include_io:
            payload["io"] = (
                dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {}
            )
        if include_temp:
            try:
                payload["temp"] = {
                    key: [entry.current for entry in values]
                    for key, values in psutil.sensors_temperatures().items()
                }
            except Exception:
                payload["temp"] = {}
        return payload
    except Exception as exc:
        return {"error": str(exc)}
