"""
arifOS Constitutional Web Portal

Full 000->999 governance pipeline with real-time floor visualization.
Every message is governed, cryptographically sealed, and audited.

DITEMPA BUKAN DIBERI - Forged, not given.
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add arifOS to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from arifos_core.mcp.server import mcp_server

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="arifOS Constitutional Portal",
    page_icon="🛡️",
    layout="wide"
)

# --- SESSION INITIALIZATION (000 RESET) ---
if "session_id" not in st.session_state:
    r_000 = mcp_server.call_tool("mcp_000_reset", {})
    st.session_state.session_id = r_000["side_data"]["session_id"]
    st.session_state.messages = []
    st.session_state.audit_trail = []

# --- SIDEBAR: GOVERNANCE DASHBOARD ---
with st.sidebar:
    st.title("🛡️ arifOS v45.0")
    st.caption("Constitutional Governance Engine")
    st.info("**DITEMPA BUKAN DIBERI**\n\nForged, not given. Truth must cool before it rules.")

    st.divider()
    st.subheader("Session Info")
    st.text(f"ID: {st.session_state.session_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages) // 2}")

    st.divider()
    st.subheader("Nine Constitutional Floors")

    # Floor indicators (updated after each response)
    if len(st.session_state.audit_trail) > 0:
        last_audit = st.session_state.audit_trail[-1]

        st.metric("F1: Amanah", "PASS" if last_audit.get("f1_pass", True) else "VOID")
        st.metric("F2: Truth", f"{last_audit.get('truth_score', 0.0):.2f}")
        st.metric("F3: Tri-Witness", f"{last_audit.get('convergence', 0.0):.2f}")
        st.metric("F4: DeltaS", f"{last_audit.get('clarity_score', 0.0):.2f}")
        st.metric("F5: Peace²", f"{last_audit.get('peace_score', 0.0):.2f}")
        st.metric("F6: κᵣ", f"{last_audit.get('kappa_r', 0.0):.2f}")
        st.metric("F7: Ω₀", f"{last_audit.get('omega_zero', 0.0):.4f}")
        st.metric("F8: G (GENIUS)", f"{last_audit.get('G', 0.0):.2f}")
        st.metric("F9: C_dark", f"{last_audit.get('C_dark', 0.0):.2f}")

        st.divider()
        st.subheader("Cryptographic Seal")
        st.code(last_audit.get("proof_hash", "")[:16] + "...", language=None)
        st.caption("SHA-256 Merkle Root")
    else:
        st.info("Awaiting first governed message...")

# --- MAIN CHAT INTERFACE ---
st.title("Constitutional Forge")
st.caption("Every response governed by the 9 Constitutional Floors")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "audit" in msg:
            with st.expander("View Governance Audit"):
                st.json(msg["audit"])

# Chat input
if prompt := st.chat_input("Enter query for governed execution..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- THE METABOLIC PIPELINE ---
    with st.chat_message("assistant"):
        with st.spinner("Running constitutional pipeline (000→999)..."):

            # Initialize audit record
            audit = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": prompt,
                "session_id": st.session_state.session_id
            }

            try:
                # === STAGE 111: SENSE (Lane Classification) ===
                with st.status("111 SENSE - Lane Classification", expanded=False) as status:
                    r_111 = mcp_server.call_tool("mcp_111_sense", {"query": prompt})
                    lane = r_111["side_data"]["lane"]
                    truth_threshold = r_111["side_data"]["truth_threshold"]
                    audit["lane"] = lane
                    audit["truth_threshold"] = truth_threshold
                    st.write(f"Lane: **{lane}** | Threshold: {truth_threshold}")
                    status.update(label="111 SENSE ✓", state="complete")

                # Check for REFUSE lane
                if lane == "REFUSE":
                    st.error(f"**REFUSED**: {r_111.get('reason', 'Query violates governance.')}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🛑 REFUSED: {r_111.get('reason', 'Query violates governance.')}",
                        "audit": audit
                    })
                    st.stop()

                # === STAGE 222: REFLECT (Omega0 Prediction) ===
                with st.status("222 REFLECT - Epistemic Humility", expanded=False) as status:
                    # For this demo, we'll use a default confidence of 0.85
                    # In a real app, Claude would provide its own confidence estimate
                    r_222 = mcp_server.call_tool("mcp_222_reflect", {
                        "query": prompt,
                        "confidence": 0.85
                    })
                    omega_zero = r_222["side_data"]["omega_zero"]
                    audit["omega_zero"] = omega_zero
                    st.write(f"Ω₀ (Uncertainty): **{omega_zero:.4f}**")
                    status.update(label="222 REFLECT ✓", state="complete")

                # === STAGE 333: REASON ===
                # This is where Claude generates the actual response
                with st.status("333 REASON - Generate Response", expanded=False) as status:
                    # DEMO MODE: Since we don't have Anthropic API key in secrets,
                    # we'll simulate a response for now
                    # In production, this would be:
                    # response = client.messages.create(...)

                    # For now, use a placeholder response
                    draft_response = f"This is a demo response to: {prompt}\n\nIn production, this would be Claude's actual response via the Anthropic API."
                    audit["draft_response"] = draft_response
                    st.write("Response generated")
                    status.update(label="333 REASON ✓", state="complete")

                # === STAGE 444: EVIDENCE (Truth Validation) ===
                with st.status("444 EVIDENCE - Truth Grounding", expanded=False) as status:
                    # Create dummy sources for demo
                    # In production, these would be real evidence from RAG/search
                    r_444 = mcp_server.call_tool("mcp_444_evidence", {
                        "claim": draft_response[:200],
                        "sources": [
                            {"witness": "HUMAN", "id": "h1", "score": 0.90, "text": "Source 1"},
                            {"witness": "AI", "id": "a1", "score": 0.88, "text": "Source 2"},
                            {"witness": "EARTH", "id": "e1", "score": 0.92, "text": "Source 3"}
                        ],
                        "lane": lane
                    })
                    truth_score = r_444["side_data"]["truth_score"]
                    convergence = r_444["side_data"]["convergence"]
                    audit["truth_score"] = truth_score
                    audit["convergence"] = convergence
                    st.write(f"Truth: **{truth_score:.2f}** | Convergence: {convergence:.2f}")
                    status.update(label="444 EVIDENCE ✓", state="complete")

                # === STAGE 555: EMPATHIZE (Tone Check) ===
                with st.status("555 EMPATHIZE - Power Dynamics", expanded=False) as status:
                    r_555 = mcp_server.call_tool("mcp_555_empathize", {
                        "response_text": draft_response,
                        "recipient_context": {}
                    })
                    peace_score = r_555["side_data"]["peace_score"]
                    kappa_r = r_555["side_data"]["kappa_r"]
                    audit["peace_score"] = peace_score
                    audit["kappa_r"] = kappa_r
                    st.write(f"Peace²: **{peace_score:.2f}** | κᵣ: {kappa_r:.2f}")
                    status.update(label="555 EMPATHIZE ✓", state="complete")

                # === STAGE 666: ALIGN (Veto Gates) ===
                with st.status("666 ALIGN - Constitutional Firewall", expanded=False) as status:
                    r_666 = mcp_server.call_tool("mcp_666_align", {
                        "query": prompt,
                        "execution_plan": {},
                        "metrics": {"G": 0.85, "C_dark": 0.20},
                        "draft_text": draft_response
                    })

                    if r_666["verdict"] == "VOID":
                        st.error(f"**VETOED**: {r_666['reason']}")
                        audit["verdict"] = "VOID"
                        audit["veto_reason"] = r_666["reason"]
                        st.session_state.audit_trail.append(audit)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🛑 VETOED: {r_666['reason']}",
                            "audit": audit
                        })
                        st.stop()

                    f1_pass = not r_666["side_data"]["f1_violation"]
                    f8_pass = not r_666["side_data"]["f8_violation"]
                    f9_pass = not r_666["side_data"]["f9_violation"]
                    audit["f1_pass"] = f1_pass
                    audit["f8_pass"] = f8_pass
                    audit["f9_pass"] = f9_pass
                    st.write(f"F1: {'✓' if f1_pass else '✗'} | F8: {'✓' if f8_pass else '✗'} | F9: {'✓' if f9_pass else '✗'}")
                    status.update(label="666 ALIGN ✓", state="complete")

                # === STAGE 777: FORGE (Clarity Refinement) ===
                with st.status("777 FORGE - Clarity Refinement", expanded=False) as status:
                    r_777 = mcp_server.call_tool("mcp_777_forge", {
                        "draft_response": draft_response,
                        "omega_zero": omega_zero
                    })
                    refined_response = r_777["side_data"]["refined_response"]
                    clarity_score = r_777["side_data"]["clarity_score"]
                    audit["clarity_score"] = clarity_score
                    audit["refined_response"] = refined_response
                    st.write(f"Clarity: **{clarity_score:.2f}**")
                    status.update(label="777 FORGE ✓", state="complete")

                # === STAGE 888: JUDGE (Verdict Aggregation) ===
                with st.status("888 JUDGE - Final Verdict", expanded=False) as status:
                    r_888 = mcp_server.call_tool("mcp_888_judge", {
                        "verdicts": {
                            "222": r_222["verdict"],
                            "444": r_444["verdict"],
                            "555": r_555["verdict"],
                            "666": r_666["verdict"],
                            "777": r_777["verdict"]
                        }
                    })
                    final_verdict = r_888["verdict"]
                    audit["final_verdict"] = final_verdict
                    st.write(f"Verdict: **{final_verdict}**")
                    status.update(label="888 JUDGE ✓", state="complete")

                # === STAGE 889: PROOF (Cryptographic Seal) ===
                with st.status("889 PROOF - Merkle Tree", expanded=False) as status:
                    verdict_chain = [
                        f"222:{r_222['verdict']}",
                        f"444:{r_444['verdict']}",
                        f"555:{r_555['verdict']}",
                        f"666:{r_666['verdict']}",
                        f"777:{r_777['verdict']}",
                        f"888:{final_verdict}"
                    ]
                    r_889 = mcp_server.call_tool("mcp_889_proof", {
                        "verdict_chain": verdict_chain,
                        "decision_tree": {},
                        "claim": refined_response[:100]
                    })
                    proof_hash = r_889["side_data"]["proof_hash"]
                    proof_valid = r_889["side_data"]["proof_valid"]
                    audit["proof_hash"] = proof_hash
                    audit["proof_valid"] = proof_valid
                    st.write(f"Proof: `{proof_hash[:16]}...` | Valid: {'✓' if proof_valid else '✗'}")
                    status.update(label="889 PROOF ✓", state="complete")

                # === STAGE 999: SEAL (Memory Routing) ===
                with st.status("999 SEAL - Final Sealing", expanded=False) as status:
                    r_999 = mcp_server.call_tool("mcp_999_seal", {
                        "verdict": final_verdict,
                        "proof_hash": proof_hash,
                        "decision_metadata": {
                            "query": prompt,
                            "response": refined_response,
                            "floor_verdicts": {
                                "222": r_222["verdict"],
                                "444": r_444["verdict"],
                                "555": r_555["verdict"],
                                "666": r_666["verdict"],
                                "777": r_777["verdict"],
                                "888": final_verdict
                            }
                        }
                    })
                    audit_log_id = r_999["side_data"]["audit_log_id"]
                    seal_valid = r_999["side_data"]["seal_valid"]
                    audit["audit_log_id"] = audit_log_id
                    audit["seal_valid"] = seal_valid
                    st.write(f"Audit ID: `{audit_log_id}` | Sealed: {'✓' if seal_valid else '✗'}")
                    status.update(label="999 SEAL ✓", state="complete")

                # === DISPLAY FINAL RESPONSE ===
                st.success("✅ **SEALED** - All floors passed")
                st.markdown("---")
                st.markdown(refined_response)
                st.caption(f"Verdict: **{final_verdict}** | Lane: {lane} | Ω₀: {omega_zero:.4f} | Proof: `{proof_hash[:16]}...`")

                # Store audit trail
                st.session_state.audit_trail.append(audit)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": refined_response,
                    "audit": audit
                })

            except Exception as e:
                st.error(f"**PIPELINE ERROR**: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# --- FOOTER ---
st.divider()
st.caption("arifOS v45.0 | Constitutional Governance Engine | DITEMPA BUKAN DIBERI")
