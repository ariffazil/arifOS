# 🔱 The Metabolic Invariants
### *The 5 Laws of `wrap_call`*

The `wrap_call` function is the universal bridge of the arifOS Double Helix. It acts as the bloodstream connecting the FastMCP interface (The Skin) to the Inner Ring Organs (The Spine). To ensure the purity of this metabolism, all operations MUST adhere to these 5 Invariants.

---

### 1. The Law of the Universal Bridge
**No organ shall bypass the bloodstream.**
Every interaction between an Outer Ring stimulus (FastMCP tool call) and an Inner Ring organ must pass through `_wrap_call()`. Direct calls to `call_kernel()` or internal organs are strictly forbidden, as they bypass the telemetry and safety wrappers.

### 2. The Law of Identity Continuity
**A thought must know its origin.**
The session identity (`session_id`) must be normalized via `_normalize_session_id()` before any processing begins. If the session does not exist, a new cryptographic nonce is generated. This enforces **F11 (Authority)** by ensuring no actor can hijack an existing session without the proper token fingerprint.

### 3. The Law of Bounded User Modeling
**No psychological inference (Anti-Theory-of-Mind).**
The `_build_user_model()` function must decorate every envelope. It is strictly limited to capturing *explicit asks* and *observable constraints*. The system must NEVER infer hidden motives, emotional states, or psychological traits of the human operator.

### 4. The Law of Worldview Decoration
**Every envelope carries the Trinity.**
The `_select_philosophy_payload()` function must attach the appropriate ΔΩΨ (Clarity, Humility, Vitality) worldview to the response based on the organ's stage and the resulting `G★` score. This ensures the system communicates its boundaries to the client dynamically.

### 5. The Law of Absolute Error Containment
**Faults are metabolic, not mechanical.**
Raw stack traces must never leak to the FastMCP client. Any Python exception caught during organ execution must be translated into a `ConstitutionalViolation`, `InfrastructureFault`, or `EpistemicGap`. These are then cleanly packaged into a `RuntimeEnvelope` with the corresponding verdict (`VOID`, `888_HOLD`, or `SABAR`).

---
*DITEMPA BUKAN DIBERI — Forged, Not Given*