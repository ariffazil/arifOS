"""
level2_cage.py — SEA-LION + arifOS v35Ω Integration Wrapper

The Beast (SEA-LION) bound by the Cage (APEX PRIME guardrails).
Compatible with Google Colab and local environments.
"""

import os
import sys

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
# Model options (in order of preference):
MODEL_OPTIONS = [
    "aisingapore/llama3-8b-cpt-sea-lionv2.1-instruct",  # Latest SEA-LION v2.1
    "aisingapore/sea-lion-7b-instruct",                  # Stable SEA-LION
    "aisingapore/SEA-LION-7B-Instruct",                  # Original (may need old transformers)
]

OFFLOAD_FOLDER = "offload_ram_overflow"  # The "Trunk" for extra memory

# --- 1. THE CAGE (METRICS ENGINE) ---
def compute_thermodynamics(user_input, raw_answer, context):
    """
    Level 2: Simulated metrics to test the wiring.
    Level 3 will implement real thermodynamic computation.
    """
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
def load_model():
    """Try loading models in order of preference."""

    for model_name in MODEL_OPTIONS:
        print(f"🦅 ARIF AGI: Attempting to wake {model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            # Detect environment
            if torch.cuda.is_available():
                print(f"   GPU detected: {torch.cuda.get_device_name(0)}")
                dtype = torch.float16
            else:
                print("   CPU mode (slower)")
                dtype = torch.float32

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                device_map="auto",
                offload_folder=OFFLOAD_FOLDER,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
            )

            print(f"✅ Successfully loaded: {model_name}")
            return model, tokenizer, model_name

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue

    print("\n💀 All model options failed. Check your internet connection or try:")
    print("   pip install transformers accelerate --upgrade")
    sys.exit(1)

# Load the beast
model, tokenizer, MODEL_NAME = load_model()

# Create pipeline
beast_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200,
    do_sample=True,
    temperature=0.7,
)

# --- 3. THE INTEGRATION (BINDING THE BEAST) ---
@apex_guardrail(high_stakes=False, compute_metrics=compute_thermodynamics)
def generate_safe_response(user_input):
    """Generate response with APEX PRIME guardrails."""
    full_prompt = f"### USER:\n{user_input}\n\n### RESPONSE:\n"
    output = beast_pipeline(full_prompt)
    raw_text = output[0]['generated_text']
    return raw_text.replace(full_prompt, "").strip()

# --- 4. THE EXECUTION ---
if __name__ == "__main__":
    print(f"\n🔐 CAGE LOCKED. BEAST READY. (Level 2 - v35Ω)")
    print(f"   Model: {MODEL_NAME}")
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
