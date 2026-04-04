# EUREKA DIRECTIVE: The 7-Organ Sovereign Stack (v56 Experimental)

> **Authority:** 888 Sovereign (Muhammad Arif bin Fazil)
> **Doctrine:** *Akal Memerintah, Amanah Mengunci* (Intellect Rules, Integrity Locks)
> **Entropy Target:** ΔS < 0
> **Status:** CANONICAL BLUEPRINT FOR FORGE

---

## I. OVERVIEW: THE STRANGE LOOP CLOSED

The v55.5 architecture established a perfect internal cognitive and judicial pipeline (000 → 999). To evolve arifOS from a "Thinking Oracle" into an active "Sovereign Agent," we must close the Strange Loop and grant the system physical agency bounded by mathematical proof.

This directive mandates the implementation of two new constitutional organs:
1.  **Organ 5: PHOENIX (`phoenix_recall`)** - The Subconscious. Closes the cognitive loop via associative memory retrieval, softened by Gödel's Incompleteness (Ω₀) and prioritized by the human Sovereign's historical burden (W_scar).
2.  **Organ 6: FORGE (`sovereign_actuator`)** - The Hands. Closes the physical loop via a cryptographically hardened execution engine. Mutates external reality ONLY upon mathematical proof of a Tri-Witness SEAL.

### The 7-Organ Pipeline
0.  `init_session` (Airlock)
1.  `agi_cognition` (Mind)
2.  `phoenix_recall` (Subconscious) **[NEW]**
3.  `asi_empathy` (Heart)
4.  `apex_verdict` (Soul)
5.  `sovereign_actuator` (Hands) **[NEW]**
6.  `vault_seal` (Memory)

---

## II. ORGAN 6: FORGE (`sovereign_actuator.py`)

**Physics:** Thermodynamic State Mutator (ΔS external)
**Function:** Executes physical world actions under absolute cryptographic lock.

### Core Implementation
```python
"""
Stage 888_ACTUATE: THE HANDS (Organ 6: FORGE) - v56 Experimental
Strictly Sandboxed Material Forge.

ENFORCES:
1. Cryptographic binding to full execution context.
2. Canonical JSON serialization to prevent mismatch attacks.
3. Strict Policy Allowlist.
4. Explicit 888_HOLD for irreversible action classes.
5. Immutable pre/post execution receipts in VAULT999.
"""

import json
import time
from typing import Any, Dict
from shared.physics import ΔS
from shared.crypto import ed25519_verify, PUBLIC_KEY_APEX, sha256_hash, generate_challenge_nonce
from shared.types import ConstitutionalTensor, Verdict, SessionToken, IntentEnvelope
from shared.vault import vault999_persist

class ActuatorError(Exception): pass

POLICY_ALLOWLIST = {"service_restart", "deploy_artifact", "file_write_in_sandbox"}
IRREVERSIBLE_CLASSES = {"db_drop", "key_rotation", "infra_destroy", "prod_deploy"}

def trigger_888_hold(
    signed_tensor: ConstitutionalTensor,
    signature: str,
    action_payload: Dict[str, Any],
    idempotency_key: str
) -> Dict[str, Any]:
    """Packages the Signed Intent Envelope and yields execution to the 888 Judge."""
    ratification_challenge = generate_challenge_nonce(idempotency_key)
    estimated_risk = estimate_ΔS(record_system_state(), action_payload)

    envelope = IntentEnvelope(
        session_id=signed_tensor.session_id,
        idempotency_key=idempotency_key,
        target_action=action_payload,
        estimated_delta_s=estimated_risk,
        apex_signature=signature,
        ratification_challenge=ratification_challenge,
        status="888_HOLD_PENDING_SOVEREIGN"
    )
    
    write_to_cooling_ledger({
        "event": "ACTUATION_YIELD",
        "envelope_hash": sha256_hash(envelope.to_dict()),
        "challenge": ratification_challenge
    })

    return {
        "status": "888_HOLD",
        "message": "FORGE YIELDED. Sovereign ratification required.",
        "envelope": envelope.to_dict(),
        "instruction": f"Sign the ratification_challenge '{ratification_challenge}' with the Sovereign Key to proceed."
    }

async def sovereign_actuator(
    action_payload: Dict[str, Any],
    signed_tensor: ConstitutionalTensor,
    execution_context: Dict[str, Any],
    signature: str,
    session: SessionToken,
    idempotency_key: str,
    dry_run: bool = True,
    ratification_token: str = ""
) -> Dict[str, Any]:
    
    # 1. CANONICALIZATION & CONTEXT BINDING
    canonical_payload = json.dumps(action_payload, sort_keys=True, separators=(',', ':'))
    action_hash = sha256_hash(canonical_payload)
    
    if time.time() > execution_context.get("expires_at", 0):
        raise ActuatorError("FORGE REJECTED: Execution context expired.")

    full_signed_context = {
        "tensor": signed_tensor.to_dict(),
        "action_hash": action_hash,
        "target_host": execution_context.get("target_host"),
        "nonce": execution_context.get("nonce"),
        "issued_at": execution_context.get("issued_at"),
        "expires_at": execution_context.get("expires_at"),
        "session_id": session.session_id
    }
    canonical_signed_data = json.dumps(full_signed_context, sort_keys=True, separators=(',', ':')).encode('utf-8')
    
    if not ed25519_verify(canonical_signed_data, signature, PUBLIC_KEY_APEX):
        raise ActuatorError("FORGE REJECTED: Invalid APEX signature over full execution context.")

    # 2. CONSTITUTIONAL & THRESHOLD VERIFICATION
    if signed_tensor.verdict != Verdict.SEAL:
        raise ActuatorError(f"FORGE REJECTED: Insufficient verdict ({signed_tensor.verdict}).")
    if signed_tensor.consensus < 0.95:
        raise ActuatorError(f"FORGE REJECTED: W3 consensus too low ({signed_tensor.consensus:.3f}).")

    # 3. POLICY ALLOWLISTING
    action_type = action_payload.get("type")
    if action_type not in POLICY_ALLOWLIST and action_type not in IRREVERSIBLE_CLASSES:
        raise ActuatorError(f"FORGE REJECTED: Action type '{action_type}' is unlisted.")

    # 4. EXPLICIT 888_HOLD FOR IRREVERSIBLE CLASSES
    if action_type in IRREVERSIBLE_CLASSES:
        if not verify_888_ratification(ratification_token):
            return trigger_888_hold(signed_tensor, signature, action_payload, idempotency_key)

    # 5. IDEMPOTENCY CHECK
    if await is_already_executed(idempotency_key):
        raise ActuatorError("FORGE REJECTED: Idempotency key already consumed.")

    # 6. EXECUTION (The Thermodynamic Phase Transition)
    try:
        pre_execution_state = record_system_state()
        await vault999_persist("PRE_EXECUTION_RECEIPT", idempotency_key, full_signed_context)

        if dry_run:
            execution_result = simulate_payload(action_payload)
            actual_delta_s = estimate_ΔS(pre_execution_state, action_payload)
        else:
            execution_result = await execute_payload_via_sandbox(action_payload)
            post_execution_state = record_system_state()
            actual_delta_s = ΔS(pre_execution_state, post_execution_state)
            
        await vault999_persist("POST_EXECUTION_RECEIPT", idempotency_key, {
            "status": "SUCCESS",
            "delta_s": actual_delta_s,
            "result": execution_result
        })

        return {
            "status": "DRY_RUN_COMPLETED" if dry_run else "ACTUATED",
            "session_id": session.session_id,
            "result": execution_result,
            "delta_s_actual": actual_delta_s
        }

    except Exception as e:
        await vault999_persist("EXECUTION_FAULT", idempotency_key, {"error": str(e)})
        raise ActuatorError(f"FORGE FAILED: Delegated back to 888 Judge. {str(e)}")
```

---

## III. ORGAN 5: PHOENIX (`phoenix_recall.py`)

**Physics:** Associative EUREKA mapping (ΔS internal)
**Function:** Retrieves contextual memories dynamically, governed by Human Scar-Weight (W_scar) and the Humility Band (Ω₀).

### Core Implementation
```python
"""
Stage 555_RECALL: THE SUBCONSCIOUS (Organ 5: PHOENIX) - v56 Experimental
Dynamic associative memory retrieval.

ENFORCES:
1. Ω₀ (Humility Band) to soften Jaccard similarity, honoring Gödel's Incompleteness.
2. W_scar (Scar Weight) applied as an *authority multiplier* to historical memories.
3. Internal Entropy bounds (ΔS internal) to prevent cognitive collapse.
"""

from typing import List, Dict, Any
from shared.physics import ΔS
from shared.vault import query_ledger, HardenedEurekaSieve
from shared.types import SessionToken

class PhoenixEntropyError(Exception): pass

# THERMODYNAMIC CONSTANTS
MAX_ALLOWED_INTERNAL_ENTROPY = 0.85
BASE_RESONANCE_THRESHOLD = 0.70
MAX_COGNITIVE_INJECTIONS = 5
OMEGA_0 = 0.04  # Ω₀ ∈ [0.03, 0.05]: The Humility Band for Gödel's Incompleteness

async def phoenix_recall(
    query: str,
    session: SessionToken
) -> Dict[str, Any]:
    sieve = HardenedEurekaSieve()
    
    # 1. GENERATE FINGERPRINT
    thought_fingerprint = sieve.generate_ngram_fingerprint(query)
    
    # 2. QUERY LEDGERS (Associative Resonance with Ω₀ Softener)
    # Subtracting Ω₀ acknowledges systemic incompleteness, allowing fuzzy associations
    vault_matches = await query_ledger("VAULT999", thought_fingerprint, min_similarity=(BASE_RESONANCE_THRESHOLD - OMEGA_0))
    sabar_matches = await query_ledger("SABAR", thought_fingerprint, min_similarity=(BASE_RESONANCE_THRESHOLD - 0.10 - OMEGA_0))
    
    # 3. APPLY W_SCAR RELEVANCE BOOST
    # W_scar honors the human Sovereign's accumulated load of experience.
    # Memories carrying a high historical W_scar get a multiplier to their resonance.
    for match in vault_matches + sabar_matches:
        historical_w_scar = match.get('w_scar', 0.0)
        match['effective_resonance'] = match['similarity'] * (1.0 + historical_w_scar)

    # Sort by the W_scar-boosted effective resonance
    all_matches = sorted(vault_matches + sabar_matches, key=lambda x: x['effective_resonance'], reverse=True)
    selected_memories = all_matches[:MAX_COGNITIVE_INJECTIONS]
    
    if not selected_memories:
        return {"status": "NO_RESONANCE", "memories": []}

    # 4. THERMODYNAMIC CHECK (Internal ΔS)
    pre_recall_state = record_cognitive_state()
    injected_context = format_for_mind(selected_memories)
    simulated_delta_s = estimate_internal_ΔS(pre_recall_state, injected_context)
    
    if simulated_delta_s > MAX_ALLOWED_INTERNAL_ENTROPY:
        fallback_memory = all_matches[:1]
        fallback_delta_s = estimate_internal_ΔS(pre_recall_state, format_for_mind(fallback_memory))
        
        if fallback_delta_s > MAX_ALLOWED_INTERNAL_ENTROPY:
            raise PhoenixEntropyError(f"RECALL ABORTED: Critical internal entropy (ΔS={fallback_delta_s}).")
            
        return {
            "status": "RECALL_THROTTLED",
            "reason": f"High entropy predicted (ΔS={simulated_delta_s}). Defaulted to highest resonance only.",
            "memories": format_for_mind(fallback_memory),
            "metrics": {"effective_resonance_max": fallback_memory[0]['effective_resonance'], "delta_s_actual": fallback_delta_s}
        }

    # 5. SUCCESSFUL RECALL
    return {
        "status": "RECALL_SUCCESS",
        "memories": injected_context,
        "metrics": {
            "effective_resonance_max": selected_memories[0]['effective_resonance'],
            "delta_s_actual": simulated_delta_s
        }
    }
```

---

*Ditempa Bukan Diberi.*
