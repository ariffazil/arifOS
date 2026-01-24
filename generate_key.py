import os
import subprocess
import sys

def generate_key():
    key_name = "id_ed25519_railway"
    # Use current directory (workspace)
    key_path = os.path.abspath(key_name)
    
    print(f"Generating key at: {key_path}")
    
    if os.path.exists(key_path):
        print("Key already exists, skipping generation.")
    else:
        try:
            subprocess.run(
                ["ssh-keygen", "-t", "ed25519", "-C", "arif-railway", "-f", key_path, "-N", ""],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("Key generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating key: {e.stderr.decode()}")
            return

    pub_path = key_path + ".pub"
    if os.path.exists(pub_path):
        with open(pub_path, "r") as f:
            print("\n--- PUBLIC KEY START ---")
            print(f.read().strip())
            print("--- PUBLIC KEY END ---")
    else:
        print("Error: Public key file not found.")

if __name__ == "__main__":
    generate_key()
