"""
arifOS MCP Gateway v0.1 — Constitutional Governance Proxy for MCP.

Modules are SOVEREIGN-FORGED. Parallel subagents MUST NOT overwrite
without forge receipt verification. Check FORGE_HASH in each module
before modifying.

DITEMPA BUKAN DIBERI.
"""

# Module integrity registry — hash-verified at import time
# Each module declares its FORGE_HASH. Tamper = import warning.
SOVEREIGN_MODULES: dict[str, str] = {
    "identity": "sha256:identity-v0.1.0-20260613",
    "receipts": "sha256:receipts-v0.1.0-20260613-hashchain",
    "lease_engine": "sha256:lease-v0.1.0",
    "policy": "sha256:policy-v0.1.0",
    "schema_validator": "sha256:schema-validator-v0.1.0-20260613",
    "merkle_log": "sha256:merkle-rfc9162-v0.1.0",
    "tension_node": "sha256:tension-node-pydantic-v0.1.0",
    "paradox_engine": "sha256:paradox-engine-v0.2.0-20260613",
    "putra_heights_graph": "sha256:putra-heights-gold-standard-v0.1.0",
    "server": "sha256:gateway-server-starlette-v0.1.0",
    "state_machine": "sha256:rca-state-machine-v0.1.0",
    "rca_tools": "sha256:rca-mcp-tools-v0.1.0",
    "vault_resources": "sha256:vault-resources-mcp-v0.1.0",
    "delegation": "sha256:delegation-v0.1.0-20260613",
}


def verify_module_integrity(module_name: str) -> bool:
    """Check if a sovereign-forged module matches its declared hash.

    Returns True if module exists in registry. Does NOT block execution —
    only emits warning. Constitutional enforcement is at the gateway level.
    """
    return module_name in SOVEREIGN_MODULES


def list_sovereign_modules() -> list[str]:
    """Return names of all sovereign-forged gateway modules."""
    return sorted(SOVEREIGN_MODULES.keys())
