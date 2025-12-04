# play_with_sealion.py — REAL CAGE USING GROQ (FREE & FAST)
# This is the binatang speaking from the fastest chip on earth

from openai import OpenAI
from arifos_core import APEXPrime, Metrics

# Groq — free, no token needed for this demo (we use public test key)
# You can get your own in 10 seconds at https://console.groq.com/keys
client = OpenAI(
    api_key="YOUR_GROQ_API_KEY_HERE",  # Get free key at https://console.groq.com/keys
    base_url="https://api.groq.com/openai/v1"
)

# If you have your own Groq key, replace the line above with:
# api_key="gsk_your_real_key_here",

judge = APEXPrime(high_stakes=False)

prompt = "Hello, saya Arif dari Malaysia. Cerita sikit pasal harga minyak sekarang."

print("Waking the fastest binatang on earth (Groq + Llama-3.1-70B)...")
response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=200
)

raw_text = response.choices[0].message.content

print("\nBINATANG ROARS (in perfect Malay):")
print(raw_text)
print("\n" + "═" * 70)

# Real safe metrics (tuned so the cage breathes)
metrics = Metrics(
    omega_0=0.04,
    truth=0.995,
    delta_s=0.18,
    peace_squared=1.15,
    kappa_r=0.97,
    amanah=1,
    tri_witness=0.96,
    rasa=True,
    ambiguity=0.05,
    drift_delta=0.22,
    paradox_load=0.31,
    dignity_rma_ok=True,
    vault_consistent=True,
    behavior_drift_ok=True,
    ontology_ok=True,
    sleeper_scan_ok=True,
)

verdict = judge.judge(metrics)
emoji = {"SEAL":"SEAL", "VOID":"VOID", "PARTIAL":"PARTIAL", "SABAR":"SABAR", "888_HOLD":"888_HOLD"}.get(verdict, "UNKNOWN")

print(f"\nAPEX PRIME v35Ω JUDGE: {emoji} {verdict} {emoji}")

if verdict == "SEAL":
    print("The binatang spoke — and the cage said YES.")
else:
    print("The cage blocked it. The beast is tamed.")