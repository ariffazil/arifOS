from __future__ import annotations

import os


def _read_file_secret(*env_names: str) -> str:
    for env_name in env_names:
        file_path = os.getenv(env_name, "").strip()
        if not file_path:
            continue
        try:
            with open(file_path, encoding="utf-8") as handle:
                secret = handle.read().strip()
        except OSError:
            continue
        if secret:
            return secret
    return ""


def _read_env_secret(*env_names: str) -> str:
    for env_name in env_names:
        secret = os.getenv(env_name, "").strip()
        if secret:
            return secret
    return ""


def main() -> int:
    if os.getenv("ARIFOS_GOVERNANCE_OPEN_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        print("WARN: ARIFOS_GOVERNANCE_OPEN_MODE is enabled; not valid for production.")
        return 1

    current = _read_file_secret(
        "ARIFOS_GOVERNANCE_SECRET_FILE",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_FILE",
    ) or _read_env_secret("ARIFOS_GOVERNANCE_SECRET", "ARIFOS_GOVERNANCE_TOKEN_SECRET")
    if not current:
        print("FAIL: no governance signing secret configured.")
        return 1

    previous = _read_file_secret(
        "ARIFOS_GOVERNANCE_SECRET_PREVIOUS_FILE",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_PREVIOUS_FILE",
    ) or _read_env_secret(
        "ARIFOS_GOVERNANCE_SECRET_PREVIOUS",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_PREVIOUS",
    )

    source = (
        "file"
        if os.getenv("ARIFOS_GOVERNANCE_SECRET_FILE", "").strip()
        or os.getenv("ARIFOS_GOVERNANCE_TOKEN_SECRET_FILE", "").strip()
        else "env"
    )
    print(f"OK: governance secret configured via {source}.")
    print(f"INFO: previous rotation secret configured = {'yes' if previous else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
