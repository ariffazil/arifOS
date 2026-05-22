"""
Regression test: docker-compose env vars must win over image-baked .env files.

Root cause: load_dotenv(override=True) made .env values override OS env vars.
Fix: load_dotenv(override=False) makes OS env vars take precedence.

Covers: F1 Amanah (correct credential selection), F4 Clarity (audit trail).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch


def test_env_precedence_docker_compose_wins_over_dotenv_file(tmp_path: Path) -> None:
    """OS/Docker env var must win when .env file has a different (stale) value."""
    stale_key = "sk-STALE_BAKED_IN_IMAGE_KEY_THAT_EXPIRED"
    runtime_key = "sk-RUNTIME_DOCKER_COMPOSE_VAR"

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text(f'SEA_LION_API_KEY="{stale_key}"\n')

    with tempfile.TemporaryDirectory():
        server_path = Path(__file__).resolve().parents[1] / "arifosmcp" / "server.py"
        assert server_path.exists(), f"server.py not found at {server_path}"

        env_backup = os.environ.get("SEA_LION_API_KEY")

        os.environ["SEA_LION_API_KEY"] = runtime_key

        try:
            with patch.dict(os.environ, {"SEA_LION_API_KEY": runtime_key}):
                import importlib.util

                spec = importlib.util.spec_from_file_location("server_regression", server_path)
                assert spec is not None and spec.loader is not None
                module = importlib.util.module_from_spec(spec)

                with patch.dict(os.environ, {"SEA_LION_API_KEY": runtime_key}):
                    spec.loader.exec_module(module)

                from arifosmcp.runtime.llm_client import SEA_LION_API_KEY as loaded_key

                assert loaded_key == runtime_key, (
                    f"Expected runtime key from docker-compose, got: {loaded_key}"
                )

        finally:
            if env_backup is not None:
                os.environ["SEA_LION_API_KEY"] = env_backup
            elif "SEA_LION_API_KEY" in os.environ:
                del os.environ["SEA_LION_API_KEY"]
