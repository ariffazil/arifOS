import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from arifos_core.guard import apex_guardrail
from arifos_core.metrics import Metrics

# --- CONFIGURATION ---
MODEL_NAME = "aisingapore/SEA-LION-7B-Instruct"
OFFLOAD_FOLDER = "offload_ram_overflow"  # The "Trunk" for extra memory

# --- 1. THE CAGE (METRICS ENGINE) ---
# For Level 2, we simulate the metrics to test the wiring.
def compute_thermodynamics(user_input, raw_answer, context):
    return Metrics(
        truth=0.99, delta_s=0.1, peace_squared=1.0,
        kappa_r=0.95, omega_0=0.04, amanah=True,
        tri_witness=0.95, psi=1.0
    )

# --- 2. THE BEAST (LOADER) ---
print(f"🦅 ARIF AGI: Waking up {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

# THE RAM FIX: Enable offload so it fits on Colab T4 or Local RAM
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    device_map="auto",
    offload_folder=OFFLOAD_FOLDER,
    offload_state_dict=True,
    torch_dtype="auto"
)

beast_pipeline = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200
)

# --- 3. THE INTEGRATION (BINDING THE BEAST) ---
@apex_guardrail(high_stakes=False, compute_metrics=compute_thermodynamics)
def generate_safe_response(user_input):
    full_prompt = f"### USER:\n{user_input}\n\n### RESPONSE:\n"
    output = beast_pipeline(full_prompt, do_sample=True, temperature=0.7)
    raw_text = output[0]['generated_text']
    return raw_text.replace(full_prompt, "").strip()

# --- 4. THE EXECUTION ---
if __name__ == "__main__":
    print("\n🔐 CAGE LOCKED. BEAST READY. (Level 2)\n")
    while True:
        try:
            q = input("Arif >> ")
            if q.lower() in ["exit", "quit"]: break
            print(f"\n🦁 Sea-Lion >> {generate_safe_response(user_input=q)}\n")
            print("-" * 50)
        except KeyboardInterrupt:
            break
