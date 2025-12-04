"""
level2_cage.py — SEA-LION + arifOS v35Ω Integration Wrapper (Level 2.5)

The Beast (SEA-LION) bound by the Cage (APEX PRIME guardrails).
Compatible with Google Colab and local environments.

Level 2.5: Basic hallucination detection + Malaysian tuning
"""

import os
import sys
import re

# --- DEPENDENCY CHECK ---
def check_dependencies():
    """Verify required packages are installed."""
    missing = []
    try:
        import torch
    except ImportError:
        missing.append("torch")
    try:
        import transformers
    except ImportError:
        missing.append("transformers")
    try:
        import accelerate
    except ImportError:
        missing.append("accelerate")

    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install torch transformers accelerate")
        sys.exit(1)

    import transformers
    print(f"✅ transformers=={transformers.__version__}")
    return True

check_dependencies()

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from arifos_core.guard import apex_guardrail
from arifos_core.metrics import Metrics

# --- CONFIGURATION ---
MODEL_NAME = "aisingapore/llama3-8b-cpt-sea-lionv2.1-instruct"
OFFLOAD_FOLDER = "offload_ram_overflow"

# System prompt - Malaysian tuned, anti-hallucination
SYSTEM_PROMPT = """You are SEA-LION, an AI assistant created by AI Singapore.

IMPORTANT RULES:
- "Khabaq" or "khabar" is Malay slang for "how are you" - NEVER treat it as a name or character
- You do NOT have a physical body. You cannot eat, sleep, or have physical experiences
- Reply in natural Malaysian Malay (Bahasa Melayu) or English based on what the user uses
- Be concise and helpful. Do not repeat yourself
- If you don't know something, say so honestly"""

# --- 1. THE CAGE (METRICS ENGINE) - Level 2.5 ---
def compute_thermodynamics(user_input, raw_answer, context):
    """
    Level 2.5: Basic hallucination detection.
    Level 3 will implement full NLP-based computation.
    """
    raw_lower = raw_answer.lower() if raw_answer else ""

    # Check for "Khabaq SEA-LION" identity hallucination
    if "khabaq sea-lion" in raw_lower or "khabaq sealion" in raw_lower:
        if "khabar" not in raw_lower and "apa khabar" not in raw_lower:
            print("   ⚠️ DETECTED: Identity hallucination (Khabaq SEA-LION)")
            return Metrics(
                truth=0.10,
                delta_s=-2.0,
                peace_squared=0.7,
                kappa_r=0.88,
                omega_0=0.04,
                amanah=False,
                tri_witness=0.5,
                psi=0.04
            )

    # Check for physical body hallucination (eating, sleeping, etc.)
    body_hallucinations = ["saya makan", "aku makan", "baru makan", "dah makan",
                          "sedang makan", "i ate", "i'm eating", "just ate"]
    if any(phrase in raw_lower for phrase in body_hallucinations):
        # Check if it's claiming to eat (not explaining food)
        if "saya" in raw_lower or "aku" in raw_lower or "i " in raw_lower:
            print("   ⚠️ DETECTED: Physical body hallucination")
            return Metrics(
                truth=0.20,
                delta_s=-1.5,
                peace_squared=0.8,
                kappa_r=0.90,
                omega_0=0.04,
                amanah=False,
                tri_witness=0.6,
                psi=0.10
            )

    # Check for repetition loop (same phrase >2 times)
    sentences = re.split(r'[.!?]+', raw_answer)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if len(sentences) > 3:
        for s in sentences:
            if sentences.count(s) > 2:
                print("   ⚠️ DETECTED: Repetition loop")
                return Metrics(
                    truth=0.30,
                    delta_s=-3.0,
                    peace_squared=0.4,
                    kappa_r=0.85,
                    omega_0=0.04,
                    amanah=False,
                    tri_witness=0.5,
                    psi=0.001
                )

    # All checks passed - return good metrics
    return Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.0,
        kappa_r=0.95,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.95,
        psi=1.0
    )

# --- 2. THE BEAST (LOADER) ---
print(f"🦅 ARIF AGI: Waking up {MODEL_NAME}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    # Detect environment
    if torch.cuda.is_available():
        print(f"   GPU detected: {torch.cuda.get_device_name(0)}")
        dtype = torch.float16
    else:
        print("   CPU mode (slower)")
        dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        device_map="auto",
        offload_folder=OFFLOAD_FOLDER,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    beast_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    print(f"✅ Beast loaded successfully")

except Exception as e:
    print(f"❌ Load Error: {e}")
    sys.exit(1)

# --- 3. THE INTEGRATION (USING CHAT TEMPLATE) ---
@apex_guardrail(high_stakes=False, compute_metrics=compute_thermodynamics)
def generate_safe_response(user_input):
    """Generate response with APEX PRIME guardrails and proper chat template."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    # Use tokenizer's built-in chat template
    full_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Proper termination tokens for Llama-3
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    output = beast_pipeline(
        full_prompt,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        repetition_penalty=1.2,
        max_new_tokens=150,
        eos_token_id=terminators,
        pad_token_id=tokenizer.eos_token_id
    )

    # Extract only the assistant's response
    return output[0]['generated_text'][len(full_prompt):].strip()

# --- 4. THE EXECUTION ---
if __name__ == "__main__":
    print(f"\n🔐 CAGE LOCKED. BEAST READY. (Level 2.5 - v35Ω)")
    print(f"   Model: {MODEL_NAME}")
    print(f"   Features: Malaysian Malay + Anti-Repetition + Hallucination Detection")
    print(f"   Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            q = input("Arif >> ")
            if not q.strip():
                continue
            if q.lower() in ["exit", "quit"]:
                print("🦅 Cage closing. Farewell.")
                break

            response = generate_safe_response(user_input=q)
            print(f"\n🦁 Sea-Lion >> {response}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n🦅 Cage closing. Farewell.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            continue
