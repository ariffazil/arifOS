"""
Check VAULT999 final state
"""
import os

vault999_dir = "C:\\Users\\User\\arifOS\\VAULT999"

print("VAULT999 Operational Data - Final Structure:")
print("=" * 50)

for item in sorted(os.listdir(vault999_dir)):
    item_path = os.path.join(vault999_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
    else:
        print(f"  [FILE] {item}")

print("\nTotal items:", len(os.listdir(vault999_dir)))
print("\nOperational directories:")
for item in ["AAA_HUMAN", "BBB_LEDGER", "CCC_CANON", "SEALS", "operational"]:
    if os.path.exists(os.path.join(vault999_dir, item)):
        print(f"  - {item}/")

print("\nData directories:")
for item in ["entropy"]:
    if os.path.exists(os.path.join(vault999_dir, item)):
        count = len(os.listdir(os.path.join(vault999_dir, item)))
        print(f"  - {item}/ ({count} files)")

print("\nProof/status files:")
for item in os.listdir(vault999_dir):
    if item.endswith('.json'):
        print(f"  - {item}")
