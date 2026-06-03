#!/usr/bin/env python3
"""
Capability Resolver — Gateway runtime secret injection

Constitutional anchor: F1 AMANAH, F7 STEWARDSHIP
Authority: YANG ARIF seal directive 'Seal all' (2025-01-08)

Purpose:
  Agents query: "Do I have capability X for scope Y?"
  Gateway resolves: capability pointer → actual secret
  Gateway injects: secret into HTTP header / env var
  Agent never sees: raw secret value

Usage:
  from capability_resolver import resolve_capability, inject_secret
  
  # Check if agent has capability
  cap = resolve_capability(provider="github", action="write", scope="ariffazil/arifOS")
  if cap:
      secret = inject_secret(cap)
      # Use secret in HTTP header / env var
  else:
      raise PermissionError("Agent does not have github.write capability")

DITEMPA BUKAN DIBERI
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone

CAPABILITIES_FILE = Path("/root/.secrets/capabilities.json")


class CapabilityNotFoundError(Exception):
    """Raised when requested capability does not exist"""
    pass


class CapabilityExpiredError(Exception):
    """Raised when capability has expired"""
    pass


class CapabilityDeniedError(Exception):
    """Raised when 888_HOLD gate blocks action"""
    pass


def load_capabilities() -> Dict[str, Any]:
    """Load capabilities.json from disk"""
    if not CAPABILITIES_FILE.exists():
        raise FileNotFoundError(f"Capabilities file not found: {CAPABILITIES_FILE}")
    
    with open(CAPABILITIES_FILE, "r") as f:
        return json.load(f)


def resolve_capability(
    provider: str,
    action: str,
    scope: Optional[str] = None,
    check_expiry: bool = True,
    check_888_hold: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Resolve capability pointer to capability object
    
    Args:
        provider: Provider name (e.g., "github", "openai", "supabase")
        action: Action name (e.g., "read", "write", "api")
        scope: Optional scope filter (e.g., "ariffazil/arifOS")
        check_expiry: Raise error if capability expired (default: True)
        check_888_hold: Raise error if requires_888 is true (default: True)
    
    Returns:
        Capability object or None if not found
    
    Raises:
        CapabilityNotFoundError: Capability does not exist
        CapabilityExpiredError: Capability has expired
        CapabilityDeniedError: 888_HOLD gate blocks action
    """
    caps = load_capabilities()
    
    # Traverse: capabilities → provider → action
    if provider not in caps["capabilities"]:
        raise CapabilityNotFoundError(f"Provider not found: {provider}")
    
    provider_caps = caps["capabilities"][provider]
    
    if action not in provider_caps:
        raise CapabilityNotFoundError(f"Action not found: {provider}.{action}")
    
    cap = provider_caps[action]
    
    # Optional: Check scope match
    if scope and cap.get("scope") != scope:
        raise CapabilityNotFoundError(
            f"Scope mismatch: requested {scope}, found {cap.get('scope')}"
        )
    
    # Check expiry
    if check_expiry and cap.get("expires"):
        expires = datetime.fromisoformat(cap["expires"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if now > expires:
            raise CapabilityExpiredError(
                f"Capability expired: {provider}.{action} (expired {cap['expires']})"
            )
    
    # Check 888_HOLD gate
    if check_888_hold and cap.get("requires_888", False):
        raise CapabilityDeniedError(
            f"Capability blocked by 888_HOLD: {provider}.{action}"
        )
    
    return cap


def inject_secret(cap: Dict[str, Any]) -> str:
    """
    Resolve secret_location and return actual secret value
    
    Args:
        cap: Capability object from resolve_capability()
    
    Returns:
        Secret value (string)
    
    Raises:
        FileNotFoundError: Secret file does not exist
        PermissionError: Secret file has wrong permissions (not 600)
    """
    secret_location = cap.get("secret_location")
    
    if not secret_location:
        raise ValueError(f"Capability missing secret_location: {cap}")
    
    # Handle special cases
    if secret_location == "sudo":
        # System capabilities (e.g., Caddy reload) don't have secrets
        return ""
    
    # Resolve file path
    secret_path = Path(secret_location)
    
    if not secret_path.exists():
        raise FileNotFoundError(f"Secret file not found: {secret_path}")
    
    # Check permissions (must be 600)
    stat = secret_path.stat()
    if stat.st_mode & 0o777 != 0o600:
        raise PermissionError(
            f"Secret file has wrong permissions: {secret_path} "
            f"(expected 600, got {oct(stat.st_mode & 0o777)})"
        )
    
    # Read secret
    with open(secret_path, "r") as f:
        secret = f.read().strip()
    
    return secret


def update_last_used(provider: str, action: str) -> None:
    """
    Update last_used timestamp for capability
    
    Args:
        provider: Provider name
        action: Action name
    """
    caps = load_capabilities()
    
    if provider in caps["capabilities"] and action in caps["capabilities"][provider]:
        caps["capabilities"][provider][action]["last_used"] = (
            datetime.now(timezone.utc).isoformat()
        )
        
        # Write back to disk
        with open(CAPABILITIES_FILE, "w") as f:
            json.dump(caps, f, indent=2)


def check_capability(provider: str, action: str, scope: Optional[str] = None) -> bool:
    """
    Check if agent has capability (without raising exceptions)
    
    Args:
        provider: Provider name
        action: Action name
        scope: Optional scope filter
    
    Returns:
        True if capability exists and is not expired/blocked, False otherwise
    """
    try:
        resolve_capability(provider, action, scope)
        return True
    except (CapabilityNotFoundError, CapabilityExpiredError, CapabilityDeniedError):
        return False


def list_capabilities(provider: Optional[str] = None) -> Dict[str, Any]:
    """
    List all capabilities (or filter by provider)
    
    Args:
        provider: Optional provider name filter
    
    Returns:
        Dict of capabilities
    """
    caps = load_capabilities()
    
    if provider:
        return {provider: caps["capabilities"].get(provider, {})}
    
    return caps["capabilities"]


# Example usage
if __name__ == "__main__":
    # Example 1: Check GitHub write capability
    try:
        cap = resolve_capability("github", "write", scope="ariffazil/arifOS")
        print(f"✓ GitHub write capability found: {cap['description']}")
        
        # Don't actually inject in this example (secret files may not exist yet)
        # secret = inject_secret(cap)
        # print(f"✓ Secret injected (length: {len(secret)})")
        
    except CapabilityNotFoundError as e:
        print(f"✗ {e}")
    except CapabilityExpiredError as e:
        print(f"✗ {e}")
    except CapabilityDeniedError as e:
        print(f"✗ {e}")
    
    # Example 2: Check Caddy reload capability (888_HOLD blocked)
    try:
        cap = resolve_capability("caddy", "reload")
        print(f"✓ Caddy reload capability found (this should not print)")
    except CapabilityDeniedError as e:
        print(f"✓ Expected: {e}")
    
    # Example 3: List all GitHub capabilities
    github_caps = list_capabilities("github")
    if github_caps and "github" in github_caps:
        print(f"\nGitHub capabilities: {list(github_caps['github'].keys())}")
    else:
        print("\nNo GitHub capabilities found")
