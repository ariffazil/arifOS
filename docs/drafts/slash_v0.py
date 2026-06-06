"""
slash_v0.py — Sovereign Slash Gesture (operational draft v0)

Status: DRAFT. Not in live tree. Not promoted. Lives in docs/drafts/.

Purpose
-------
Specify the one-gesture seal flow:
  Arif types /999  →  bot reads prior observation  →  presents consequence
  card (display_hash)  →  Arif taps once  →  arif_vault_seal fires with full
  envelope (signature, nonce, session_id, judge_state_hash).

Design rules (Mode C, both tracks small):
  1. One gesture. /999 is short. /seal is also fine. Pick one.
  2. Zero cryptographic ceremony for the human. Agent handles the 7 primitives
     (signature, nonce, envelope, session_id, judge_state_hash, ack, payload).
  3. Kernel validates server-side via existing F1-F13 gates.
  4. Plain-text receipt back to Telegram — what was sealed, in English, nothing else.
  5. Display card must hash identically to the signed payload (UI deception guard).

Open questions
--------------
  - Slash name: /999 or /seal or /pin? (Arif decides)
  - Trigger: explicit only, or auto-prompt on irreversible observation?
  - If auto-prompt: what classifies as "irreversible"? (E.g. does the system
    auto-detect, or does the calling agent declare it?)

Architectural prerequisite
--------------------------
This draft assumes the arif_vault_seal schema fix (adding actor_signature +
nonce to its argument schema) is already live in the deployed runtime.
Without that fix, seal will HOLD with F11 floor breach. Status: pending
888_HOLD restart of arifos.service to pick up the schema change.

Constitutional floors invoked
-----------------------------
  L01 AMANAH  (reversible-first; seal is the exception)
  L11 AUDIT   (signature + nonce + session_id)
  L13 SOVEREIGN (Arif's tap is the final authority)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# This file is a draft spec. No executable code below.
# Promotion to live tree requires:
#   1. arif_vault_seal schema fix verified live
#   2. Slash name chosen by Arif
#   3. One real seal test, not a HOLD
#   4. Arif's explicit "promote v0 → v1" call

# ----------------------------------------------------------------------------
# CONCRETE PROPOSAL (illustrative — replace with chosen name)
# ----------------------------------------------------------------------------

PROPOSED_GESTURE = "/999"  # alt: "/seal", "/pin" — Arif decides
PROPOSED_FALLBACK = "/seal"

# What the bot does on receipt:
#
# 1. Read last fact-bearing exchange (last user message + assistant reply)
# 2. Generate fresh nonce (HMAC over ARIF_ROOTKEY, 5-min window)
# 3. Call arif_session_init with signature (refresh session envelope)
# 4. Build consequence card:
#    {
#       "what": "<1-line summary of what would be sealed>",
#       "object": "<file path / claim id / observation id>",
#       "blast_radius": "low | medium | high | critical",
#       "reversibility": "full | partial | none",
#    }
# 5. Compute display_hash = blake3(card_canonical_json)
# 6. Build IntentEnvelope dict (mirrors docs/drafts/intent_envelope_v0.py)
# 7. Telegram inline keyboard:
#       [  YES — seal  ]  [  NO — discard  ]
# 8. On YES: POST to arifOS /mcp arif_vault_seal with full envelope
# 9. On NO: discard. No state change.
# 10. On tap timeout (60s): discard silently. No nag.

DRAFT_STATUS = "v0 — pending Arif review"
PROMOTION_GATE = "Arif says 'promote v0 → v1' AND arif_vault_seal schema fix verified live"
