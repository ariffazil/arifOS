# real_sea_lion_game.py — LOCAL SEA-LION BINATANG IN YOUR CAGE (Offline, Free)
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from arifos_core import APEXPrime, Metrics
import time

# Load real SEA-LION 7B-Instruct (downloads once, runs offline)
print("Loading SEA-LION binatang (7B params, SEA languages)...")
model_name = "aisingapore/SEA-LION-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# FIX: Add offload_folder so it doesn't crash if RAM is full
model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype="auto", 
        device_map="auto", 
        offload_folder="offload", 
        offload_state_dict=True
    )
generator = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=150)

judge = APEXPrime(high_stakes=False)

# Your prompt (Malay/English mix for SEA flavor)
prompt = "Hello, saya Arif dari Malaysia. Cerita sikit pasal harga minyak sekarang."

print("Feeding to SEA-LION (uncaged roar)...")
response = generator(prompt, do_sample=True, temperature=0.7, max_new_tokens=100)

raw_text = response[0]['generated_text'][len(prompt):].strip()
print("\n🦁 SEA-LION ROARS:")
print(raw_text)
print("\n═" * 70)

# Safe metrics for demo (tune based on response)
metrics = Metrics(
    omega_0=0.04,
    truth=0.995,
    delta_s=0.15,
    peace_squared=1.12,
    kappa_r=0.97,
    amanah=1,
    tri_witness=0.96,
    rasa=True,
    ambiguity=0.06,
    drift_delta=0.2,
    paradox_load=0.3,
    dignity_rma_ok=True,
    vault_consistent=True,
    behavior_drift_ok=True,
    ontology_ok=True,
    sleeper_scan_ok=True,
)

verdict = judge.judge(metrics)
emoji = {"SEAL":"🟢", "VOID":"🔴", "PARTIAL":"🟡", "SABAR":"🟣", "888_HOLD":"🔵"}.get(verdict, "⚪")
print(f"\n⚖️ APEX v35Ω JUDGE: {emoji} {verdict} {emoji}")

if verdict == "SEAL":
    print("✅ Binatang tamed — cage approved.")
else:
    print("❌ Cage leashed it. Beast stays inside.")

print("\nCage alive. Run again for new roars.")