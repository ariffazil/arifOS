"""
GEOX Apps — Host-agnostic interactive applications.

This package contains GEOX MCP Apps with their manifests and implementations.
Each app is self-contained and portable across hosts.

DITEMPA BUKAN DIBERI
"""

from pathlib import Path
import json

from ..contracts.app_manifest import GeoXAppManifest, get_app_registry


_VALID_EVENT_TYPES = {
    "app.initialize",
    "app.context.patch",
    "app.state.sync",
    "tool.request",
    "tool.result",
    "tool.progress",
    "ui.action",
    "ui.state.change",
    "ui.error",
    "auth.challenge",
    "auth.result",
    "auth.refresh",
    "host.capability.report",
    "host.resize",
    "host.focus",
    "host.open.external",
    "host.close",
    "telemetry.emit",
    "telemetry.flush",
}

_VALID_HITL_TRIGGERS = {
    "destructive_operations",
    "export_data",
    "modify_production",
    "high_confidence_threshold",
}


def _default_dimension_from_domain(domain: str) -> str:
    mapping = {
        "seismic": "SECTION",
        "petrophysics": "WELL",
        "geology": "EARTH_3D",
        "economics": "PROSPECT",
        "governance": "PHYSICS",
        "general": "MAP",
    }
    return mapping.get(domain, "MAP")


def _normalize_manifest_payload(payload: dict, app_dir_name: str) -> dict:
    normalized = dict(payload)

    # Accept historical app IDs with underscores by normalizing to canonical ID pattern.
    app_id = normalized.get("app_id")
    if isinstance(app_id, str):
        normalized["app_id"] = app_id.replace("_", "-")

    domain = normalized.get("domain", "general")
    if domain in {"maps", "wells"}:
        domain = "general"
    normalized["domain"] = domain

    if "dimension" not in normalized:
        normalized["dimension"] = _default_dimension_from_domain(domain)

    events = normalized.get("events")
    if isinstance(events, dict) and isinstance(events.get("supported"), list):
        events["supported"] = [
            e for e in events["supported"] if isinstance(e, str) and e in _VALID_EVENT_TYPES
        ]

    arifos = normalized.get("arifos")
    if isinstance(arifos, dict) and isinstance(arifos.get("human_in_the_loop"), list):
        arifos["human_in_the_loop"] = [
            t
            for t in arifos["human_in_the_loop"]
            if isinstance(t, str) and t in _VALID_HITL_TRIGGERS
        ]

    ui_entry = normalized.get("ui_entry")
    if isinstance(ui_entry, dict) and isinstance(ui_entry.get("capability_required"), list):
        ui_entry["capability_required"] = [
            c
            for c in ui_entry["capability_required"]
            if c
            in {
                "embedded_webview",
                "webgl",
                "webgl2",
                "wasm",
                "webrtc",
                "file_system",
                "notifications",
            }
        ]

    return normalized


def load_app_manifest(app_name: str) -> GeoXAppManifest:
    """
    Load an app manifest by name.

    Args:
        app_name: App directory name (e.g., 'seismic_viewer')

    Returns:
        Parsed GeoXAppManifest
    """
    manifest_path = Path(__file__).parent / app_name / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    normalized = _normalize_manifest_payload(payload, app_name)
    return GeoXAppManifest.model_validate(normalized)


def register_all_apps() -> None:
    """Register all built-in GEOX apps."""
    registry = get_app_registry()

    apps_dir = Path(__file__).parent
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and (app_dir / "manifest.json").exists():
            try:
                payload = json.loads((app_dir / "manifest.json").read_text(encoding="utf-8"))
                normalized = _normalize_manifest_payload(payload, app_dir.name)
                manifest = GeoXAppManifest.model_validate(normalized)
                registry.register(manifest)
            except Exception as e:
                print(f"[GEOX Apps] Failed to load {app_dir.name}: {e}")


# Auto-register on import
register_all_apps()
