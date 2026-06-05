import json
import os
import subprocess
import requests
from datetime import datetime, timezone

SOT_PATH = "/opt/arifos/sites/arif-fazil.com/GEOX/status.json"
SOT_DIR = os.path.dirname(SOT_PATH)
ARIFOS_REPO = os.environ.get("ARIFOS_REPO", "/opt/arifos/src/arifOS")

def get_container_status(name):
    try:
        res = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Status}}", name]).decode().strip()
        return res
    except:
        return "down"

def get_api_health(url):
    try:
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            return "healthy"
        return f"error_{res.status_code}"
    except:
        return "unreachable"

status_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "seal": "DITEMPA BUKAN DIBERI",
    "services": {
        "arifosmcp": {
            "docker": get_container_status("arifosmcp"),
            "api": get_api_health("https://arifosmcp.arif-fazil.com/health")
        },
        "geox_eic": {
            "docker": get_container_status("geox_eic"),
            "api": get_api_health("https://GEOX.arif-fazil.com/health")
        }
    },
    "integrity": {
        "skills_linked": os.path.islink(f"{ARIFOS_REPO}/GEOX/skills"),
        "submodule_sync": True
    }
}

os.makedirs(SOT_DIR, exist_ok=True)
with open(SOT_PATH, "w") as f:
    json.dump(status_data, f, indent=2)

print(f"Live SOT updated at {status_data['timestamp']}")
