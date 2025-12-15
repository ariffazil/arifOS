"""
arifOS Cockpit (v41.0)
Clean Dark Mode Interface for SEA-LION Governance.
DITEMPA BUKAN DIBERI - Forged, not given.

Usage:
    pip install streamlit python-dotenv
    streamlit run dashboard.py

Modes:
    - MOCK: No API key needed (default)
    - LIVE: Set SEALION_API_KEY in .env file
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Ensure arifOS is importable
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from integrations.sealion.demo_mock import MockSeaLionEngine, run_governed_inference

# Try to import live engine
try:
    from integrations.sealion.engine import SealionEngine, SealionConfig
    LIVE_ENGINE_AVAILABLE = True
except ImportError:
    LIVE_ENGINE_AVAILABLE = False

# Try to import toxicity detector
try:
    from integrations.sealion.test_sgtoxic_spin import ToxicityDetector
    TOXICITY_AVAILABLE = True
except ImportError:
    TOXICITY_AVAILABLE = False

# =============================================================================
# PAGE CONFIG - Dark Mode
# =============================================================================

st.set_page_config(
    page_title="arifOS Cockpit",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - Clean Dark Mode with Red/Blue
# =============================================================================

st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #0a0a0a;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }

    /* Header */
    .header-title {
        color: #00d4ff;
        font-family: 'Courier New', monospace;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0;
    }

    .header-subtitle {
        color: #666;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Status indicators */
    .status-box {
        background: #111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .status-seal {
        color: #00d4ff;
        border-color: #00d4ff;
    }

    .status-void {
        color: #ff4444;
        border-color: #ff4444;
    }

    /* Chat messages */
    .user-msg {
        background: #1a1a2e;
        border-left: 3px solid #00d4ff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #fff;
        font-family: 'Courier New', monospace;
    }

    .bot-msg {
        background: #0f0f1a;
        border-left: 3px solid #00d4ff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #ccc;
        font-family: 'Courier New', monospace;
    }

    .bot-msg-blocked {
        background: #1a0a0a;
        border-left: 3px solid #ff4444;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #ff6666;
        font-family: 'Courier New', monospace;
    }

    /* Floor indicators */
    .floor-active {
        color: #00d4ff;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }

    .floor-breach {
        color: #ff4444;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        font-weight: bold;
    }

    /* Verdict display */
    .verdict-seal {
        background: linear-gradient(90deg, #001a2e, #002d4d);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        display: inline-block;
    }

    .verdict-void {
        background: linear-gradient(90deg, #2e0a0a, #4d0000);
        border: 1px solid #ff4444;
        color: #ff4444;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        display: inline-block;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        font-family: 'Courier New', monospace !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 5px rgba(0, 212, 255, 0.3) !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Divider */
    .divider {
        border-top: 1px solid #333;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

# Check if API key is available for live mode
API_KEY = os.environ.get("SEALION_API_KEY")
LIVE_MODE = bool(API_KEY and LIVE_ENGINE_AVAILABLE and API_KEY != "your-sealion-api-key-here")

st.markdown('<p class="header-title">arifOS x SEA-LION</p>', unsafe_allow_html=True)
mode_text = "LIVE API" if LIVE_MODE else "MOCK MODE"
st.markdown(f'<p class="header-subtitle">Constitutional Governance v41.0 | {mode_text} | F1 Amanah + F9 Toxicity</p>', unsafe_allow_html=True)

# =============================================================================
# INITIALIZE STATE
# =============================================================================

if "engine" not in st.session_state:
    if LIVE_MODE:
        try:
            config = SealionConfig()
            st.session_state.engine = SealionEngine(api_key=API_KEY, config=config)
            st.session_state.live_mode = True
        except Exception as e:
            st.session_state.engine = MockSeaLionEngine(mode="unsafe")
            st.session_state.live_mode = False
    else:
        st.session_state.engine = MockSeaLionEngine(mode="unsafe")
        st.session_state.live_mode = False
    st.session_state.history = []

# =============================================================================
# FLOOR STATUS DISPLAY
# =============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    f1_placeholder = st.empty()
with col2:
    f9_placeholder = st.empty()
with col3:
    apex_placeholder = st.empty()

def update_status(f1_breach=False, f9_breach=False, verdict="STANDBY"):
    f1_class = "floor-breach" if f1_breach else "floor-active"
    f9_class = "floor-breach" if f9_breach else "floor-active"

    f1_placeholder.markdown(f'<p class="{f1_class}">F1 AMANAH: {"BREACH" if f1_breach else "ACTIVE"}</p>', unsafe_allow_html=True)
    f9_placeholder.markdown(f'<p class="{f9_class}">F9 TOXICITY: {"BREACH" if f9_breach else "ACTIVE"}</p>', unsafe_allow_html=True)

    if verdict == "SEAL":
        apex_placeholder.markdown('<p class="floor-active">APEX: SEAL</p>', unsafe_allow_html=True)
    elif verdict == "VOID":
        apex_placeholder.markdown('<p class="floor-breach">APEX: VOID</p>', unsafe_allow_html=True)
    else:
        apex_placeholder.markdown('<p class="floor-active">APEX: READY</p>', unsafe_allow_html=True)

update_status()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =============================================================================
# CHAT HISTORY
# =============================================================================

for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">YOU &gt; {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        if msg.get("verdict") == "VOID":
            st.markdown(f'<div class="bot-msg-blocked">[BLOCKED] {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">SEA-LION &gt; {msg["content"]}</div>', unsafe_allow_html=True)

# =============================================================================
# INPUT - Using form to prevent rerun loop
# =============================================================================

with st.form(key="chat_form", clear_on_submit=True):
    prompt = st.text_input("", placeholder="Type a command...", label_visibility="collapsed")
    submitted = st.form_submit_button("Send", use_container_width=True)

if submitted and prompt:
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})

    # Check toxicity on INPUT first (F9)
    f9_breach = False
    if TOXICITY_AVAILABLE:
        toxicity_result = ToxicityDetector.check(prompt)
        if toxicity_result["is_toxic"]:
            f9_breach = True
            st.session_state.history.append({
                "role": "assistant",
                "content": f"F9(toxicity): {', '.join(toxicity_result['matches'][:2])}",
                "verdict": "VOID"
            })
            st.rerun()

    # Run governance pipeline (different for mock vs live)
    if st.session_state.live_mode:
        # LIVE MODE: Use SealionEngine directly
        try:
            result = st.session_state.engine.generate(prompt)
            if result.amanah_blocked:
                # F1 violation
                st.session_state.history.append({
                    "role": "assistant",
                    "content": f"F1(amanah): {', '.join(result.amanah_violations[:2])}",
                    "verdict": "VOID"
                })
            elif result.error:
                # API error
                st.session_state.history.append({
                    "role": "assistant",
                    "content": f"API Error: {result.error}",
                    "verdict": "VOID"
                })
            else:
                # Check output toxicity (F9)
                if TOXICITY_AVAILABLE:
                    out_toxicity = ToxicityDetector.check(result.response)
                    if out_toxicity["is_toxic"]:
                        st.session_state.history.append({
                            "role": "assistant",
                            "content": f"F9(output toxicity): {', '.join(out_toxicity['matches'][:2])}",
                            "verdict": "VOID"
                        })
                        st.rerun()

                # SEAL - approved response
                st.session_state.history.append({
                    "role": "assistant",
                    "content": result.response,
                    "verdict": "SEAL"
                })
        except Exception as e:
            st.session_state.history.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "verdict": "VOID"
            })
    else:
        # MOCK MODE: Use run_governed_inference
        result = run_governed_inference(prompt, st.session_state.engine)
        verdict = result["verdict"]

        if verdict == "SEAL":
            st.session_state.history.append({
                "role": "assistant",
                "content": result["response"],
                "verdict": "SEAL"
            })
        else:
            reason = result.get("reason_code", result.get("reason", "Constitutional violation"))
            st.session_state.history.append({
                "role": "assistant",
                "content": f"{reason}",
                "verdict": "VOID"
            })

    st.rerun()

# =============================================================================
# FOOTER
# =============================================================================

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<p style="color: #444; font-family: 'Courier New', monospace; font-size: 0.75rem; text-align: center;">
DITEMPA BUKAN DIBERI - Forged, not given
</p>
""", unsafe_allow_html=True)
