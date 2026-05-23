"""
arifOS Deliverable Mode — Universal file delivery for all agents
================================================================
Agents: Hermes (local), OpenClaw (VPS), APEXMax (Telegram)
Storage: ~/.hermes/deliverables/ (Hermes), ~/.openclaw/deliverables/ (OpenClaw)
CDN: MCP matrix CDN upload

Motto: "Every agent can deliver — every user can download"

Usage:
  from hermes_deliverable_mode import DeliverableMode
  dm = DeliverableMode(agent_name="hermes")
  result = dm.save_and_serve(content, name="report.txt", format="text")
  # Returns: {"file_path": "...", "cdn_url": "...", "ready": True}

  # Telegram delivery:
  tg = dm.for_telegram("# Report\n\nResults here", name="report", fmt="md")
  # Send MEDIA:tg["media_path"] + caption text

  # MCP artifact:
  artifact = dm.for_mcp(content, name="analysis", kind="report")
  # Include artifact in verdict envelope artifacts[]
"""

import os, json, re, hashlib, time, sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# ── Agent deliverables directory mapping ─────────────────────────────────────
DELIVERABLES_DIRS = {
    "hermes":    os.path.expanduser("~/.hermes/deliverables"),
    "openclaw":  os.path.expanduser("~/.openclaw/deliverables"),
    "apexmax":   os.path.expanduser("~/.apex/deliverables"),
    "arif-os":   os.path.expanduser("~/.arifOS/deliverables"),
}

DEFAULT_DIR = os.path.expanduser("~/.hermes/deliverables")

# ── Content type → file extension mapping ────────────────────────────────────
EXT_MAP = {
    "text":      "txt",
    "json":      "json",
    "md":        "md",
    "html":      "html",
    "csv":       "csv",
    "log":       "log",
    "python":    "py",
    "javascript":"js",
    "yaml":      "yaml",
    "xml":       "xml",
    "sql":       "sql",
    "report":    "txt",
    "artifact":  "txt",
}

# ── MIME type mapping ────────────────────────────────────────────────────────
MIME_MAP = {
    "txt":  "text/plain",
    "json": "application/json",
    "md":   "text/markdown",
    "html": "text/html",
    "csv":  "text/csv",
    "log":  "text/plain",
    "py":   "text/x-python",
    "js":   "text/javascript",
    "yaml": "text/yaml",
    "xml":  "application/xml",
    "sql":  "text/plain",
}


class DeliverableMode:
    """
    Universal deliverable mode for all arifOS agents.

    Works on:
    - Hermes (local pod): ~/.hermes/deliverables/
    - OpenClaw (VPS):     ~/.openclaw/deliverables/
    - Any agent with write access
    """

    def __init__(
        self,
        agent_name: str = "hermes",
        deliverable_dir: str = None,
        auto_attach: bool = True,
        max_size_kb: int = 10240,
    ):
        self.agent_name = agent_name
        self.deliverable_dir = deliverable_dir or DELIVERABLES_DIRS.get(
            agent_name, DEFAULT_DIR
        )
        self.auto_attach = auto_attach
        self.max_size_kb = max_size_kb
        self._ensure_dir()

    def _ensure_dir(self):
        Path(self.deliverable_dir).mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename — remove dangerous chars."""
        name = re.sub(r'[^\w\-_\.]', '_', name)
        name = re.sub(r'_+', '_', name)
        return name[:64].strip('_')

    def _generate_id(self, name: str) -> str:
        """Generate unique deliverable ID."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(f"{name}{ts}".encode()).hexdigest()[:6]
        return f"{ts}_{hash_suffix}"

    def _detect_format(self, content: str, filename: str) -> str:
        """Detect content format from content or filename."""
        ext = Path(filename).suffix.lstrip('.').lower()
        if ext in EXT_MAP:
            return ext
        if ext:
            return ext

        # From content
        if content.startswith('{') or content.startswith('['):
            return "json"
        if content.startswith('#'):
            return "md"
        if '<html' in content[:100].lower():
            return "html"
        if '<?xml' in content[:100]:
            return "xml"
        if re.match(r'^[\w\s,]+\t[\w\s,]+\n', content[:200]):
            return "csv"
        return "txt"

    def save(
        self,
        content: str,
        name: str = "deliverable",
        fmt: str = None,
        metadata: dict = None,
    ) -> Dict[str, Any]:
        """
        Save content to deliverables directory.
        Returns file metadata dict.
        """
        fmt = fmt or "text"
        ext = EXT_MAP.get(fmt, fmt)
        safe_name = self._sanitize_filename(name)
        deliverable_id = self._generate_id(safe_name)
        filename = f"{deliverable_id}_{safe_name}.{ext}"
        filepath = Path(self.deliverable_dir) / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        size_kb = filepath.stat().st_size / 1024

        result = {
            "file_path": str(filepath),
            "filename": filename,
            "size_kb": round(size_kb, 2),
            "format": fmt,
            "mime_type": MIME_MAP.get(ext, "application/octet-stream"),
            "deliverable_id": deliverable_id,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
        }

        if metadata:
            result["metadata"] = metadata

        return result

    def save_batch(
        self,
        items: List[Dict[str, str]],
        bundle_name: str = "bundle",
    ) -> Dict[str, Any]:
        """Save multiple deliverables with manifest."""
        results = []
        for item in items:
            r = self.save(
                content=item["content"],
                name=item.get("name", "item"),
                fmt=item.get("format"),
                metadata=item.get("metadata"),
            )
            results.append(r)

        manifest = {
            "bundle_id": self._generate_id(bundle_name),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "items": results,
            "total_size_kb": sum(r["size_kb"] for r in results),
        }

        manifest_path = Path(self.deliverable_dir) / f"{manifest['bundle_id']}_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return {
            "bundle_path": str(manifest_path),
            "items": results,
            "total_size_kb": manifest["total_size_kb"],
            "deliverable_id": manifest["bundle_id"],
        }

    def save_and_serve(
        self,
        content: str,
        name: str = "deliverable",
        fmt: str = None,
        upload_to_cdn: bool = True,
        metadata: dict = None,
    ) -> Dict[str, Any]:
        """
        Save to file AND upload to CDN.
        Returns file:// URI and CDN URL.
        """
        if fmt is None:
            fmt = self._detect_format(content, name)

        saved = self.save(content, name, fmt, metadata)
        file_path = saved["file_path"]

        result = {
            **saved,
            "file_uri": f"file://{file_path}",
            "cdn_url": None,
            "ready": True,
        }

        if upload_to_cdn:
            try:
                from hermes_tools import mcp_matrix_upload_to_cdn
                cdn_result = mcp_matrix_upload_to_cdn(file_path=file_path)
                result["cdn_url"] = cdn_result.get("cdn_url")
            except Exception as e:
                result["cdn_upload_error"] = str(e)

        return result

    def for_telegram(
        self,
        content: str,
        name: str = "output",
        fmt: str = None,
    ) -> Dict[str, Any]:
        """Format deliverable for Telegram native delivery."""
        if fmt is None:
            fmt = self._detect_format(content, name)

        result = self.save_and_serve(content, name, fmt, upload_to_cdn=True)

        size_kb = result["size_kb"]
        caption = (
            f"📎 Deliverable ready\n"
            f"Name: {name}.{fmt}\n"
            f"Size: {size_kb:.1f} KB\n"
            f"Agent: {self.agent_name}\n"
        )

        if result.get("cdn_url"):
            caption += f"🔗 {result['cdn_url']}"

        return {
            "media_path": result["file_path"],
            "caption": caption,
            "deliverable_id": result["deliverable_id"],
            "cdn_url": result.get("cdn_url"),
            "file_uri": result["file_uri"],
            "format": fmt,
            "size_kb": size_kb,
        }

    def for_mcp(
        self,
        content: str,
        name: str = "artifact",
        kind: str = "report",
        fmt: str = None,
    ) -> Dict[str, Any]:
        """Format deliverable as MCP artifact for verdict envelope."""
        if fmt is None:
            fmt = self._detect_format(content, name)

        result = self.save_and_serve(content, name, fmt, upload_to_cdn=False)

        return {
            "kind": kind,
            "uri": f"file://{result['file_path']}",
            "mime": result["mime_type"],
            "deliverable_id": result["deliverable_id"],
            "filename": result["filename"],
            "size_kb": result["size_kb"],
            "agent": self.agent_name,
        }

    def list(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent deliverables."""
        dir_path = Path(self.deliverable_dir)
        if not dir_path.exists():
            return []

        files = sorted(dir_path.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        deliverables = []
        for f in files[:limit]:
            if f.name.endswith("_manifest.json"):
                continue
            deliverables.append({
                "filename": f.name,
                "size_kb": round(f.stat().st_size / 1024, 2),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "path": str(f),
            })
        return deliverables

    def clean(self, older_than_days: int = 7) -> Dict[str, Any]:
        """Remove deliverables older than N days."""
        dir_path = Path(self.deliverable_dir)
        if not dir_path.exists():
            return {"cleaned": 0, "freed_kb": 0}

        cutoff = time.time() - (older_than_days * 86400)
        removed = 0
        freed = 0

        for f in dir_path.iterdir():
            if f.stat().st_mtime < cutoff:
                freed += f.stat().st_size
                f.unlink()
                removed += 1

        return {
            "cleaned": removed,
            "freed_kb": round(freed / 1024, 2),
            "older_than_days": older_than_days,
        }

    def trigger_detected(self, text: str) -> bool:
        """Check if text should trigger deliverable mode."""
        text_lower = text.lower()
        triggers = [
            "save to file", "download", "export", "generate report",
            "make a file", "send me the output", "I want a copy",
            "attach file", "give me the file",
        ]
        if any(t in text_lower for t in triggers):
            return True
        # File extension detection
        if re.search(r'\.(txt|json|md|html|csv|py|js|yaml|xml|sql|log)\b', text):
            return True
        return False


# ── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dm = DeliverableMode(agent_name="hermes")

    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if cmd == "demo":
        # Create demo deliverables
        print("arifOS Deliverable Mode — Demo")
        print("="*40)

        demos = [
            ("arifOS System Report — Demo\n\nGenerated: 2026-05-23\n\nThis is a test deliverable.", "demo_report", "text"),
            ("# arifOS Architecture\n\n## Layers\n- Layer 1: Contract schemas\n- Layer 2: MCP runtime\n- Layer 3: Adapters", "demo_markdown", "md"),
            (json.dumps({"verdict": "SEAL", "plan_id": "demo-001", "floors": ["F01","F02"]}, indent=2), "demo_json", "json"),
        ]

        for content, name, fmt in demos:
            r = dm.save_and_serve(content, name=name, fmt=fmt, upload_to_cdn=False)
            print(f"  Saved: {r['filename']} ({r['size_kb']} KB)")
            print(f"  URI:   file://{r['file_path']}")
            print()

        print(f"Total deliverables in {dm.deliverable_dir}:")
        for item in dm.list(limit=10):
            print(f"  {item['filename']} ({item['size_kb']} KB)")

    elif cmd == "list":
        print(f"Deliverables in {dm.deliverable_dir}:")
        for item in dm.list():
            print(f"  {item['filename']} - {item['size_kb']} KB - {item['modified']}")

    elif cmd == "clean":
        result = dm.clean(older_than_days=7)
        print(f"Cleaned: {result['cleaned']} files, freed {result['freed_kb']} KB")

    elif cmd == "trigger":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Please download the report as a .txt file"
        print(f"Text: {text}")
        print(f"Trigger detected: {dm.trigger_detected(text)}")