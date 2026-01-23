# arifOS Constitutional Web Portal

**Full constitutional governance for web-based Claude interaction.**

Every message flows through the complete **000→999 metabolic pipeline** with real-time visualization of all 9 Constitutional Floors.

---

## 🚀 Quick Start

### Run the Portal

```bash
cd portal
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🛡️ What This Does

Unlike Claude Desktop (which runs MCP locally) or claude.ai (cloud-only), this portal:

1. **Runs locally** on your machine
2. **Governs every message** through the full 000→999 pipeline
3. **Displays all floor metrics** in real-time
4. **Generates cryptographic proofs** (SHA-256 Merkle tree) for every response
5. **Logs audit trail** for full accountability

---

## 📊 The Pipeline

Every query goes through 10 stages:

| Stage | Tool | Purpose | Output |
|-------|------|---------|--------|
| 000 | RESET | Session initialization | Session ID |
| 111 | SENSE | Lane classification (HARD/SOFT/PHATIC/REFUSE) | Lane, threshold |
| 222 | REFLECT | Omega0 prediction (epistemic humility) | Ω₀ uncertainty band |
| 333 | REASON | Generate Claude response | Draft response |
| 444 | EVIDENCE | Tri-witness truth validation | Truth score, convergence |
| 555 | EMPATHIZE | Power-aware tone check | Peace², κᵣ |
| 666 | ALIGN | Veto gates (F1/F8/F9) | PASS or VOID |
| 777 | FORGE | Clarity refinement + humility injection | Refined response |
| 888 | JUDGE | Verdict aggregation | SEAL/PARTIAL/VOID |
| 889 | PROOF | Cryptographic Merkle proof | SHA-256 hash |
| 999 | SEAL | Memory routing + audit log | Audit ID |

---

## 🔐 Adding Claude API Integration

Currently runs in **DEMO MODE** with placeholder responses.

To enable real Claude API calls:

1. Get API key from [console.anthropic.com](https://console.anthropic.com/)
2. Edit `.streamlit/secrets.toml`:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
3. Uncomment the Claude API code in `app.py` (Stage 333: REASON)

---

## 🌊 The Nine Floors

Displayed in real-time on the sidebar:

| Floor | Name | Threshold | Type |
|-------|------|-----------|------|
| F1 | Amanah | LOCK | Hard |
| F2 | Truth | ≥0.99 | Hard |
| F3 | Tri-Witness | ≥0.95 | Hard |
| F4 | DeltaS (Clarity) | ≥0 | Hard |
| F5 | Peace² | ≥1.0 | Soft |
| F6 | κᵣ (Empathy) | ≥0.95 | Soft |
| F7 | Ω₀ (Humility) | 0.03-0.05 | Hard |
| F8 | G (GENIUS) | ≥0.80 | Derived |
| F9 | C_dark | <0.30 | Derived |

Hard floor fail → **VOID**
Soft floor fail → **PARTIAL**

---

## 📝 Audit Trail

Every governed response is logged with:
- Full verdict chain (222→888)
- SHA-256 Merkle proof hash
- Floor scores (F1-F9)
- Session ID
- Timestamp
- Audit log ID

View audit for any message by clicking "View Governance Audit" below the response.

---

## 🔥 Why This Exists

**Problem:** claude.ai web doesn't support local MCP servers

**Solution:** Build your own web interface that:
- Calls Claude API directly
- Runs arifOS governance locally
- Gives you full control

You are the **Sovereign**. This is your **Forge**.

---

**DITEMPA BUKAN DIBERI** - Forged, not given.
