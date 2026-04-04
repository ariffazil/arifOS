
import hashlib

# Read the file
with open(r'000_MANIFESTO.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Adjust to remove newlines if splitlines() was used in original thought context
# We want to hash lines 0 to 617 (line 618 in 1-based indexing)
# Checking alignment:
# Line 617: "**Witness:** Language ∩ Human (WHY meaning)"
# Line 618: \n
# Line 619: "**Content Integrity Seal (SHA-256):**  "

content_block = "".join(lines[:618])
seal_hash = hashlib.sha256(content_block.encode('utf-8')).hexdigest().upper()

print(f"SEAL HASH: {seal_hash}")
