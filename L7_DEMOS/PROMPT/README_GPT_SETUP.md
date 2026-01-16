# 🛠️ arifOS GPT Setup Guide (2-File System)

You do NOT need a `config.json` for the **Prompt Generator** or **Voice** mode.
The logic is "Simulated" via the System Prompt and Knowledge Base.

## 📦 The 2 Essential Files

### 1️⃣ Instructions (The Brain)
*   **Source File:** [`SYSTEM_PROMPT.md`](./SYSTEM_PROMPT.md)
*   **Where to put it:** Copy and paste the *entire text* into the **"Instructions"** box in the GPT Builder.
*   **What it does:** Defines the 10-Stage Metabolic Loop, 12 Floors, and Voice Protocol.

### 2️⃣ Knowledge (The Memory)
*   **Source File:** [`AGI_KNOWLEDGE_v46.md`](./AGI_KNOWLEDGE_v46.md)
*   **Where to put it:** Upload this file to the **"Knowledge"** section.
*   **What it does:** Teaches the GPT *how* to generate Golden Prompts (UPP) and understand Agent Zero profiling.

---

## ❓ FAQ

### "Do I need Actions / config.json?"
**No.**
*   **Voice/Prompt Mode:** Runs fully on the 2 files above.
*   **Governance Mode:** Logic is simulated via `AGI_KNOWLEDGE`.
*   *(Optional)* Only if you want the GPT to *physically* control your PC do you need Actions (connecting to the MCP Server), which is a separate advanced step.

### "How do I test it?"
1.  **Voice:** Open ChatGPT App -> Headphone Icon -> Speak.
2.  **Prompt Gen:** Type "Generate a prompt for [X]".

**Status:** Ready to Deploy.
