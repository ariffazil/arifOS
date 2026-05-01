import os

BASE = "/root/repos/arifOS/arifosmcp/tools"

TOOLS = [
    "arifos_000_init",
    "arifos_111_sense",
    "arifos_222_witness",
    "arifos_333_mind",
    "arifos_444_kernel",
    "arifos_555_memory",
    "arifos_666_heart",
    "arifos_777_ops",
    "arifos_888_judge",
    "arifos_999_vault",
    "arifos_forge",
    "arifos_gateway",
    "arifos_sabar",
]

PATHS = {
    "arifos_000_init": "_000_init.py",
    "arifos_111_sense": "_111_sense.py",
    "arifos_222_witness": "_222_witness.py",
    "arifos_333_mind": "_333_mind.py",
    "arifos_444_kernel": "_444_kernel.py",
    "arifos_555_memory": "_555_memory.py",
    "arifos_666_heart": "_666_heart.py",
    "arifos_777_ops": "_777_ops.py",
    "arifos_888_judge": "_888_judge.py",
    "arifos_999_vault": "_999_vault.py",
    "arifos_forge": "_forge.py",
    "arifos_gateway": "_gateway.py",
    "arifos_sabar": "_sabar.py",
}

def verify():
    print("--- arifOS Tool Verification Harness ---")
    print(f"Base Path: {BASE}\n")
    
    missing = []
    
    for tool in TOOLS:
        rel_path = PATHS.get(tool)
        full_path = os.path.join(BASE, rel_path)
        
        status = "✅ FOUND" if os.path.exists(full_path) else "❌ MISSING"
        print(f"{tool:<20} | {status} | {rel_path}")
        
        if status == "❌ MISSING":
            missing.append(tool)
            
    print("\n--- Summary ---")
    if not missing:
        print("All tools forged! Horizon is synchronized.")
    else:
        print(f"{len(TOOLS) - len(missing)}/{len(TOOLS)} tools forged.")
        print(f"Awaiting forges for: {', '.join(missing)}")

if __name__ == "__main__":
    verify()
