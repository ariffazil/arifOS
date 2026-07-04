"""
arifosmcp/runtime/vc.py — Verifiable Credentials (VC) issuer and verifier.
Implements the W3C Verifiable Credentials Data Model for agent delegation.
"""

from __future__ import annotations

import base64
import json
import time
import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from arifosmcp.runtime.did_resolver import resolve_did

# Default Contexts for W3C Verifiable Credentials
DEFAULT_CONTEXTS = [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/security/suites/ed25519-2020/v1",
]


def _canonicalize_credential(credential: dict[str, Any]) -> bytes:
    """Canonicalize the credential (excluding the proof object) for signing."""
    # Create a copy and strip the proof
    temp = credential.copy()
    temp.pop("proof", None)
    # Serialize sorted JSON representation
    return json.dumps(temp, sort_keys=True, separators=(",", ":")).encode("utf-8")


def issue_credential(
    issuer_did: str,
    issuer_private_key_pem: str,
    subject: dict[str, Any],
    credential_type: list[str] | None = None,
    cred_id: str | None = None,
    expiry_seconds: int | None = None,
) -> dict[str, Any]:
    """
    Issue a signed W3C Verifiable Credential.
    """
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    c_type = credential_type or ["VerifiableCredential", "AgentDelegationCredential"]

    vc: dict[str, Any] = {
        "@context": DEFAULT_CONTEXTS,
        "id": cred_id or f"urn:uuid:{uuid.uuid4()}",
        "type": c_type,
        "issuer": issuer_did,
        "issuanceDate": now,
        "credentialSubject": subject,
    }

    if expiry_seconds:
        expiry_time = datetime.fromtimestamp(time.time() + expiry_seconds, UTC)
        vc["expirationDate"] = expiry_time.isoformat().replace("+00:00", "Z")

    # Load private key and sign
    try:
        private_key = serialization.load_pem_private_key(
            issuer_private_key_pem.encode("utf-8"),
            password=None,
        )
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise ValueError("Only Ed25519 private keys are supported for default VC signing.")
    except Exception as e:
        raise ValueError(f"Invalid private key format: {e}")

    canonical_data = _canonicalize_credential(vc)
    signature = private_key.sign(canonical_data)
    sig_b64 = base64.b64encode(signature).decode("utf-8")

    # Linked Data Proof representation
    vc["proof"] = {
        "type": "Ed25519Signature2020",
        "created": now,
        "verificationMethod": f"{issuer_did}#key-1",
        "proofPurpose": "assertionMethod",
        "proofValue": sig_b64,
    }

    return vc


def verify_credential(credential: dict[str, Any]) -> tuple[bool, str]:
    """
    Verify the signature and validity of a W3C Verifiable Credential.

    Returns:
        (True, "verified") if valid, (False, error_reason) if invalid.
    """
    if not isinstance(credential, dict):
        return False, "credential_must_be_a_dict"

    # 1. Essential field presence checks
    for field in ["@context", "id", "type", "issuer", "issuanceDate", "credentialSubject", "proof"]:
        if field not in credential:
            return False, f"missing_required_field: {field}"

    proof = credential["proof"]
    if not isinstance(proof, dict) or "proofValue" not in proof:
        return False, "missing_proof_or_signature"

    # 2. Check Expiry
    expiration_date = credential.get("expirationDate")
    if expiration_date:
        try:
            # Parse ISO-8601 UTC date
            exp_dt = datetime.fromisoformat(expiration_date.replace("Z", "+00:00"))
            if datetime.now(UTC) > exp_dt:
                return False, "credential_expired"
        except ValueError:
            return False, "invalid_expiration_date_format"

    # 3. Resolve Issuer's Public Key
    issuer_did = credential["issuer"]
    did_doc = resolve_did(issuer_did)
    if not did_doc:
        return False, f"unable_to_resolve_issuer_did: {issuer_did}"

    # Extract public key from DID Document
    vmethods = did_doc.get("verificationMethod", [])
    if not vmethods:
        return False, "no_verification_methods_in_did_document"

    # Use first available verification method or find verificationMethod matching proof.verificationMethod
    proof_vmethod = proof.get("verificationMethod")
    target_method = None
    for vm in vmethods:
        if proof_vmethod and vm.get("id") == proof_vmethod:
            target_method = vm
            break
    if not target_method:
        target_method = vmethods[0]

    # Load public key
    try:
        # If public key is provided as PEM format
        if "publicKeyPem" in target_method:
            pub_key_pem = target_method["publicKeyPem"]
            public_key = serialization.load_pem_public_key(pub_key_pem.encode("utf-8"))
        elif "publicKeyMultibase" in target_method:
            multibase = target_method["publicKeyMultibase"]
            if multibase.startswith("z6M"):
                # decode base58 multicodec key
                from arifosmcp.runtime.did_resolver import base58_decode

                raw_bytes = base58_decode(multibase[1:])
                # strip 2-byte prefix if present
                if raw_bytes.startswith(b"\xed\x01"):
                    raw_bytes = raw_bytes[2:]
                public_key = ed25519.Ed25519PublicKey.from_public_bytes(raw_bytes)
            else:
                return False, f"unsupported_publicKeyMultibase_format: {multibase}"
        else:
            return False, "no_supported_public_key_fields_in_did_document"
    except Exception as e:
        return False, f"failed_to_load_resolved_public_key: {e}"

    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        return False, "unsupported_public_key_type_for_vc"

    # 4. Verify Signature
    try:
        canonical_data = _canonicalize_credential(credential)
        sig_bytes = base64.b64decode(proof["proofValue"])
        public_key.verify(sig_bytes, canonical_data)
    except Exception as e:
        return False, f"signature_verification_failed: {e}"

    return True, "verified"
