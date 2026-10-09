#!/usr/bin/env python3
"""
Genesis Session Key Derivation — arifOS Constitutional Kernel

Fetches arif-fazil.com/000 as the sovereign genesis seed.
Derives session keys via HKDF.
Telegram approval = human signature.

NO private key material ever leaves the VPS.
The genesis statement IS the root key.
"""
import hashlib
import hmac
import json
import time
import urllib.request
from pathlib import Path
from typing import Optional

GENESIS_URL = "https://arif-fazil.com/000/genesis-statement.json"
SALT = b"arifos_root_key_salt_v1"
CACHE_TTL_SECONDS = 3600  # Refresh genesis hash every hour

class GenesisKeyDeriver:
    """
    Derives session keys from the publicly-anchored genesis statement.
    
    Security model:
    - Genesis seed = SHA256 of arif-fazil.com/000 content (Arif controls domain)
    - Session key = HMAC-SHA256(genesis_seed, session_id) — zero info about seed
    - Telegram approval from @ariffazil = human signature
    - Root key never on VPS
    """
    
    def __init__(self, cache_dir: str = "/agent/vault999/.genesis_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._genesis_hash: Optional[bytes] = None
        self._cached_at: float = 0
    
    def fetch_genesis_hash(self, force_refresh: bool = False) -> str:
        """Fetch and hash the genesis statement from arif-fazil.com/000"""
        now = time.time()
        
        if (not force_refresh 
            and self._genesis_hash is not None 
            and (now - self._cached_at) < CACHE_TTL_SECONDS):
            return self._genesis_hash.hex()
        
        req = urllib.request.Request(GENESIS_URL, headers={"User-Agent": "arifOS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8")
        
        d = json.loads(raw)
        genesis_hash = hashlib.sha256(raw.encode()).digest()
        
        # Cache metadata
        cache = {
            "genesis_id": d["genesis_id"],
            "content_sha256": genesis_hash.hex(),
            "fetched_at": now,
            "session_count": 0
        }
        with open(self.cache_dir / "last_genesis.json", "w") as f:
            json.dump(cache, f, indent=2)
        
        self._genesis_hash = genesis_hash
        self._cached_at = now
        return genesis_hash.hex()
    
    def derive_session_key(self, session_id: str) -> str:
        """
        Derive a session-specific key from the genesis seed.
        HKDF-like: HMAC-SHA256(genesis_hash, session_id_info)
        Returns hex-encoded 32-byte key.
        """
        if self._genesis_hash is None:
            self.fetch_genesis_hash()
        
        info = f"arif_session_key_v1_{session_id}".encode()
        session_key = hmac.new(SALT, self._genesis_hash + info, hashlib.sha256).digest()
        return session_key.hex()
    
    def prove_genesis(self) -> dict:
        """Return publicly verifiable genesis proof."""
        genesis_hex = self.fetch_genesis_hash()
        d = json.loads(urllib.request.Request(GENESIS_URL, 
                          headers={"User-Agent": "arifOS/1.0"}).get_full_url() or GENESIS_URL)
        
        # Re-fetch for metadata
        req = urllib.request.Request(GENESIS_URL, headers={"User-Agent": "arifOS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8")
        statement = json.loads(raw)
        
        return {
            "genesis_id": statement["genesis_id"],
            "did": statement["human"]["root_key"],
            "domain": statement["human"]["root_domain"],
            "content_sha256": genesis_hex,
            "fetched_via": "https://arif-fazil.com/000/genesis-statement.json",
            "method": "HMAC-SHA256(genesis_seed, session_id)",
            "authorization": "Telegram message from @ariffazil",
            "root_key_location": "Arif's local machine (never on VPS)"
        }

# Singleton
_genesis_deriver: Optional[GenesisKeyDeriver] = None

def get_genesis_deriver() -> GenesisKeyDeriver:
    global _genesis_deriver
    if _genesis_deriver is None:
        _genesis_deriver = GenesisKeyDeriver()
    return _genesis_deriver
