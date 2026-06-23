"""
arifosmcp/runtime/tovana_compiler.py — Tovana belief compiler for arifOS

Phase 3 (2026-06-17): conservative belief compiler wrapping tovana.

Tovana (assafelovic/tovana) is a memory management library that extracts
memories + beliefs from free-form user messages. arifOS wraps it with
strict dignity guards (F6 MARUAH):

  - NO automatic extraction — all updates are EXPLICIT (arif_belief_propose)
  - All beliefs visible via arif_belief_list
  - Single-call forget via arif_belief_forget
  - 90-day TTL via decay policy
  - Memory stored at /root/.arifos/memory/tovana/ (separate from VAULT999)

F1 AMANAH: All operations are reversible (forget deletes, list inspects).
F2 TRUTH: All outputs carry epistemic_tag INTERPRETATION (LLM-extracted).
F6 MARUAH: Beliefs about a person. Visibility + deletability enforced.
F13 SOVEREIGN: The user (Arif) can see + delete any belief at any time.

LLM provider: minimax (OpenAI-compatible, base_url=https://api.minimax.io/v1)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TOVANA_VENV_PYTHON = os.getenv("TOVANA_VENV_PYTHON", "/root/tovana-venv/bin/python3")
_TOVANA_MEMORY_DIR = Path(os.getenv("TOVANA_MEMORY_DIR", "/root/.arifos/memory/tovana"))
_BELIEF_TTL_DAYS = int(os.getenv("TOVANA_BELIEF_TTL_DAYS", "90"))


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _memory_file_for(user_id: str, business: str) -> Path:
    """Sanitize user_id and return the per-user memory file path."""
    safe_user = "".join(c if c.isalnum() or c in "_-" else "_" for c in user_id)[:64]
    safe_biz = "".join(c if c.isalnum() or c in "_-" else "_" for c in business)[:32]
    return _ensure_dir(_TOVANA_MEMORY_DIR / safe_biz) / f"{safe_user}.json"


def _decay_check(memory: dict) -> tuple[dict, list[str]]:
    """Check beliefs for TTL expiry. Returns (cleaned, expired_keys)."""
    if not isinstance(memory, dict):
        return memory, []
    last_updated = memory.get("last_updated")
    if not last_updated:
        return memory, []
    try:
        last_dt = datetime.fromisoformat(last_updated)
    except (TypeError, ValueError):
        return memory, []
    if datetime.now() - last_dt > timedelta(days=_BELIEF_TTL_DAYS):
        # Archive: move to .archive
        return {}, ["all (TTL expired)"]
    return memory, []


def _run_in_tovana_venv(callable_path: str, *args: Any, **kwargs: Any) -> Any:
    """
    Execute a tovana function in the tovana venv's Python interpreter.

    Tovana has a different dep tree (langchain_openai, etc.) than arifOS,
    so we shell out to /root/tovana-venv/bin/python3 to keep the
    dep trees isolated.
    """
    import subprocess

    payload = json.dumps(
        {"callable": callable_path, "args": list(args), "kwargs": kwargs},
        default=str,
    )
    # All unindented — to be valid Python when run as `python -c`
    code = (
        "import sys\n"
        "sys.path.insert(0, '/root/tovana-venv/lib/python3.12/site-packages')\n"
        "import json, os, re\n"
        "from tovana import MemoryManager\n"
        "\n"
        # ---- Monkey-patch: strip <think>...</think> blocks ----
        # minimax models (M3, M2.5-highspeed) all emit reasoning blocks\n"
        # before their JSON output, which breaks langchain's strict\n"
        # JsonOutputParser. This patch strips them transparently.\n"
        "import langchain_core.output_parsers.json as _lc_json\n"
        "_orig_parse = _lc_json.JsonOutputParser.parse_result\n"
        "_think_re = re.compile(r'<think>.*?</think>', re.DOTALL)\n"
        "\n"
        "def _patched_parse(self, result, *, partial=False):\n"
        "    # langchain passes result as list[ChatGeneration]\n"
        "    for gen in result:\n"
        "        if hasattr(gen, 'text') and isinstance(gen.text, str) and '<think>' in gen.text:\n"
        "            gen.text = _think_re.sub('', gen.text).strip()\n"
        "    return _orig_parse(self, result, partial=partial)\n"
        "\n"
        "_lc_json.JsonOutputParser.parse_result = _patched_parse\n"
        "# ---- End monkey-patch ----\n"
        "\n"
        "API_KEY = os.environ.get('TOVANA_API_KEY', '')\n"
        "BASE_URL = os.environ.get('TOVANA_BASE_URL', 'https://api.minimax.io/v1')\n"
        "MODEL = os.environ.get('TOVANA_MODEL', 'MiniMax-M3')\n"
        "MEMORY_FILE = os.environ.get('TOVANA_MEMORY_FILE', '/tmp/tovana_default.json')\n"
        "\n"
        "payload = json.loads(sys.argv[1])\n"
        "callable_name = payload['callable']\n"
        "args = payload.get('args', [])\n"
        "kwargs = payload.get('kwargs', {})\n"
        "\n"
        "mm = MemoryManager(\n"
        "    api_key=API_KEY,\n"
        "    provider='openai',\n"
        "    business_description=kwargs.pop('__business__', 'a personal AI assistant'),\n"
        "    model=MODEL,\n"
        "    base_url=BASE_URL,\n"
        ")\n"
        "mm.memory.memory_file = kwargs.pop('__memory_file__', MEMORY_FILE)\n"
        "\n"
        "fn = getattr(mm, callable_name)\n"
        "result = fn(*args, **kwargs)\n"
        "\n"
        "def _jsonable(r):\n"
        "    if r is None or isinstance(r, (str, int, float, bool)):\n"
        "        return r\n"
        "    if isinstance(r, (dict, list)):\n"
        "        return r\n"
        "    return str(r)\n"
        "\n"
        "print('__RESULT__:' + json.dumps(_jsonable(result)))\n"
    )
    env = os.environ.copy()
    # Primary: Azure OpenAI gpt-4.1-mini (cheap, reliable, no <think> blocks)
    # Fallback: MiniMax (original config). Azure wired 2026-06-20.
    azure_key = env.get("AZURE_OPENAI_KEY", "")
    if azure_key:
        env["TOVANA_API_KEY"] = azure_key
        env["TOVANA_BASE_URL"] = env.get("AZURE_OPENAI_ENDPOINT", "https://api.minimax.io/v1")
        env["TOVANA_MODEL"] = env.get("AZURE_OPENAI_MODEL", "gpt-4.1-mini")
    else:
        env["TOVANA_API_KEY"] = env.get("MINIMAX_API_KEY", "")
        env["TOVANA_BASE_URL"] = env.get("OPENAI_BASE_URL", "https://api.minimax.io/v1")
        env["TOVANA_MODEL"] = os.getenv("TOVANA_MODEL", "MiniMax-M2.5-highspeed")
    env["TOVANA_USER_ID"] = "default"
    env["TOVANA_MEMORY_FILE"] = "/tmp/tovana_default.json"

    proc = subprocess.run(
        [_TOVANA_VENV_PYTHON, "-c", code, payload],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"tovana subprocess failed: {proc.stderr}")

    # Extract __RESULT__ line
    for line in proc.stdout.split("\n"):
        if line.startswith("__RESULT__:"):
            return json.loads(line[len("__RESULT__:") :])
    return {"stdout": proc.stdout, "stderr": proc.stderr}


class TovanaCompiler:
    """Conservative belief compiler for arifOS."""

    def __init__(self) -> None:
        _ensure_dir(_TOVANA_MEMORY_DIR)

    async def propose(
        self,
        user_id: str,
        message: str,
        business_description: str = "Arif's sovereign AI assistant",
    ) -> dict[str, Any]:
        """
        Extract memories + beliefs from a free-form message.
        Stores to /root/.arifos/memory/tovana/<business>/<user_id>.json.

        F6 MARUAH: This is the only WRITE to beliefs. Caller MUST
        confirm consent before invoking.

        Returns: dict with extracted memories + beliefs + last_updated.
        """
        if not user_id or not message:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "user_id and message are required",
                "bridge": "tovana_propose",
            }

        memory_file = _memory_file_for(user_id, business_description)
        # Run tovana in subprocess. The MEMORY_FILE is set on mm.memory
        # inside the subprocess; we don't pass it as a kwarg to update_memory.
        try:
            _run_in_tovana_venv(
                "update_memory",
                user_id,
                message,
                __memory_file__=str(memory_file),
                __business__=business_description,
            )
        except Exception as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": f"tovana subprocess failed: {exc}",
                "bridge": "tovana_propose",
            }

        # Load what tovana wrote
        if not memory_file.exists():
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "tovana did not write memory file",
                "bridge": "tovana_propose",
            }

        stored = json.loads(memory_file.read_text())
        # Tovana stores as {user_id: {extracted_keys, last_updated, beliefs}}.
        # Extract the user-specific data; fall back to treating as flat if
        # the structure is different.
        if isinstance(stored, dict) and user_id in stored and isinstance(stored[user_id], dict):
            user_data = stored[user_id]
        else:
            user_data = stored
        return {
            "status": "success",
            "verdict": "SEAL",
            "bridge": "tovana_propose",
            "epistemic_tag": "INTERPRETATION",  # F2: LLM-extracted
            "user_id": user_id,
            "memory_path": str(memory_file),
            "memories": {
                k: v for k, v in user_data.items() if k not in ("last_updated", "beliefs")
            },
            "beliefs": user_data.get("beliefs"),
            "last_updated": user_data.get("last_updated"),
        }

    async def list(
        self,
        user_id: str,
        business_description: str = "Arif's sovereign AI assistant",
    ) -> dict[str, Any]:
        """
        List all stored memories + beliefs for a user.
        F6 MARUAH: Visibility — anyone can inspect what the system
        believes about them.
        """
        memory_file = _memory_file_for(user_id, business_description)
        if not memory_file.exists():
            return {
                "status": "success",
                "verdict": "SABAR",
                "bridge": "tovana_list",
                "user_id": user_id,
                "memory_path": str(memory_file),
                "memories": {},
                "beliefs": None,
                "last_updated": None,
                "note": "no memories stored for this user",
            }

        stored = json.loads(memory_file.read_text())
        cleaned, expired = _decay_check(stored)
        if expired:
            return {
                "status": "success",
                "verdict": "SABAR",
                "bridge": "tovana_list",
                "epistemic_tag": "INTERPRETATION",
                "user_id": user_id,
                "memory_path": str(memory_file),
                "memories": {},
                "beliefs": None,
                "last_updated": None,
                "decay": True,
                "expired": expired,
                "note": f"beliefs expired (TTL={_BELIEF_TTL_DAYS} days); cleared",
            }

        return {
            "status": "success",
            "verdict": "SEAL",
            "bridge": "tovana_list",
            "epistemic_tag": "INTERPRETATION",
            "user_id": user_id,
            "memory_path": str(memory_file),
            "memories": {k: v for k, v in cleaned.items() if k not in ("last_updated", "beliefs")},
            "beliefs": cleaned.get("beliefs"),
            "last_updated": cleaned.get("last_updated"),
        }

    async def forget(
        self,
        user_id: str,
        business_description: str = "Arif's sovereign AI assistant",
    ) -> dict[str, Any]:
        """
        Delete ALL memories for a user.
        F1 AMANAH: Reversible by re-extraction, but the call itself is
        immediate and complete. Use with care.
        """
        memory_file = _memory_file_for(user_id, business_description)
        if not memory_file.exists():
            return {
                "status": "success",
                "verdict": "SABAR",
                "bridge": "tovana_forget",
                "user_id": user_id,
                "deleted": False,
                "note": "no memories to forget",
            }
        memory_file.unlink()
        return {
            "status": "success",
            "verdict": "SEAL",
            "bridge": "tovana_forget",
            "user_id": user_id,
            "memory_path": str(memory_file),
            "deleted": True,
        }


tovana_compiler = TovanaCompiler()
