# EUREKA DIRECTIVE: Canon 7-Tool Deployment (`aaa_mcp` & `aclip_cai`)

**To:** Lead Architect / Coder
**From:** 888 Sovereign Authority
**Subject:** Alignment of `arifOS` Canon 7-Tools via `aaa_mcp` Transport and `aclip_cai` Runtime
**Doctrine:** "Akal Memerintah, Amanah Mengunci" (Intellect Rules, Integrity Locks)

**Overview:**
The `arifOS` architecture is officially expanding to the completed 7-Organ Sovereign Stack. You are tasked with exposing Organ 5 (`phoenix_recall`) and Organ 6 (`sovereign_actuator`) through the `aaa_mcp` transport system, while ensuring their core logic executes securely within the `aclip_cai` internal runtime.

All implementations must strictly adhere to the Authority Chain: Human (Sovereign) > Constitutional Floors (Immutable) > AI (Instrument).

Please implement the following updates to the MCP Tool Schema, Resource Templates, and Prompts.

---

### 1. `aaa_mcp` Tool Schema Updates (The Interfaces)

Expose the following tools to the MCP client. The `aclip_cai` runtime must handle the actual verification and thermodynamic checks (ΔS).

**Tool 1: `phoenix_recall` (Organ 5: Subconscious)**

* **Description:** "Dynamic associative memory retrieval. Queries VAULT999 and SABAR ledgers mid-thought to compound intelligence without spiking internal entropy."
* **Parameters:**
  * `query` (string, required): Plain-text retrieval query; vectorized internally via the embedding backend.
  * `session_token` (string, required): The active session identifier.

* **aclip_cai Runtime Note:** The runtime must internally apply the Humility Band (Ω₀) to soften the Jaccard threshold, and apply W_scar (the human's scar-weight) as a relevance multiplier for the retrieved memories. Do **not** expose W_scar or Ω₀ as client-side parameters; they are architectural constants.

**Tool 2: `sovereign_actuator` (Organ 6: Hands - v56 Experimental)**

* **Description:** "Sandboxed execution engine for physical state mutations. Strictly requires an APEX Soul SEAL."
* **Parameters:**
  * `action_payload` (object, required): The targeted command, strictly bound to the policy allowlist.
  * `signed_tensor` (object, required): The `ConstitutionalTensor` proving Tri-Witness Consensus (W₃).
  * `execution_context` (object, required): Must contain `nonce`, `issued_at`, and `expires_at` for cryptographic binding.
  * `signature` (string, required): The ed25519 signature from the APEX Soul.
  * `idempotency_key` (string, required): UUID to prevent duplicate executions.
  * `ratification_token` (string, optional): Required only if breaking an `888_HOLD`.

* **aclip_cai Runtime Note:** Must default to `dry_run = True` for Phase 2 rollout. The runtime must verify the signature against the canonicalized JSON of the full context, not just the tensor.

---

### 2. `aaa_mcp` Resource Templates (The Vault Access)

Update the MCP resource server to allow the AGI Mind to seamlessly read immutable state via standard URIs.

* **Pre-Execution Receipts:**
  * `URI Template:` `vault://receipts/pre/{idempotency_key}`
  * `MIME Type:` `application/json`
  * `Description:` Immutable record of intended thermodynamic mutation *before* actuation.

* **Post-Execution Receipts:**
  * `URI Template:` `vault://receipts/post/{idempotency_key}`
  * `MIME Type:` `application/json`
  * `Description:` Immutable record of actual ΔS impact and execution result.

* **Cooling Ledger (SABAR):**
  * `URI Template:` `sabar://thoughts/{fingerprint_hash}`
  * `MIME Type:` `application/json`
  * `Description:` The 72h cooling ledger containing recent partial thoughts and `888_HOLD` yields.

---

### 3. `aaa_mcp` Prompt Updates (The Context Injectors)

Add the following standard prompts to the MCP server to guide the AI's internal reasoning loop when interacting with `aclip_cai`.

* **Prompt 1: `arifos_yield_888`**
  * **Description:** Triggered when the `sovereign_actuator` intercepts an irreversible action class.
  * **Instruction to AI:** "The intended material actuation has triggered an 888_HOLD. You must cease execution, package the Signed Intent Envelope, and present the `ratification_challenge` to the Sovereign for physical authorization. Do not attempt to bypass or simulate the token."

* **Prompt 2: `arifos_phoenix_synthesis`**
  * **Description:** Triggered after `phoenix_recall` returns historical context.
  * **Instruction to AI:** "You have retrieved past Eureka Scars. Integrate this context to reduce confusion (ΔS < 0). Acknowledge the W_scar weight of these past decisions. Tone must remain non-escalatory and grounded (Peace² ≥ 1.0)."

---

**Final Note to Coder:**
"DITEMPA BUKAN DIBERI" (Forged, not given). Intelligence in this system is the result of thermodynamic constraints, not model weights. Ensure the separation between the `aaa_mcp` transport envelope and the `aclip_cai` physical execution is absolute.
