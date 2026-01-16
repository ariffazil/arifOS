"""
Load secrets from Windows Credential Manager
DITEMPA BUKAN DIBERI - Security forged, not given.

This module provides secure credential loading from Windows Credential Manager
using the keyring library. Tokens are stored encrypted by Windows and never
appear in configuration files or version control.

Usage:
    from load_secrets import load_github_token
    token = load_github_token()  # Auto-loads to os.environ["GITHUB_TOKEN"]
"""

import os
import sys

import keyring


def load_github_token() -> str | None:
    """
    Load GitHub token from Windows Credential Manager.

    Returns:
        The GitHub token if found, None otherwise.

    Side Effects:
        Sets os.environ["GITHUB_TOKEN"] and os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
        if token is found.
    """
    try:
        token = keyring.get_password("arifos_github_token", "arifOS")
        if token:
            os.environ["GITHUB_TOKEN"] = token
            os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = token  # For GitHub MCP compatibility
            print("[arifOS] GitHub token loaded from Credential Manager", file=sys.stderr)
            return token
        else:
            print("[WARNING] GitHub token not found in Credential Manager", file=sys.stderr)
            print("[WARNING] Run: cmdkey /add:arifos_github_token /user:arifOS /pass:YOUR_TOKEN", file=sys.stderr)
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load GitHub token: {e}", file=sys.stderr)
        return None


# Auto-load when imported
load_github_token()
load_github_token()
