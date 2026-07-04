# SPINE_CONFIG — Model Registry Configuration

> **arifOS 2026.6.5+** · Sovereign deployments must configure their spine location.

## What is the Spine?

The **arifOS Model Registry** ("spine") is a filesystem-based registry of AI model passports (`catalog.json` + per-model governance cards). It tells the arifOS kernel which models are authorized, what their risk leashes are, and what self-claim boundaries they operate under.

The spine is maintained as a separate git repository:
```bash
git clone https://github.com/ariffazil/arifos-model-registry.git
```

## Quick Start

```bash
# Clone the registry
git clone https://github.com/ariffazil/arifos-model-registry.git /opt/arifos-model-registry

# Point arifOS at it
export ARIFOS_REGISTRY_ROOT=/opt/arifos-model-registry

# Install and verify
pip install arifos==2026.6.5
python -c "from arifosmcp.runtime.registry_client import REGISTRY_ROOT; print(REGISTRY_ROOT)"
# Expected: /opt/arifos-model-registry
```

## Systemd Deployment

Add to your systemd unit:
```ini
[Service]
Environment=ARIFOS_REGISTRY_ROOT=/opt/arifos-model-registry
```

## Docker Deployment

```dockerfile
ENV ARIFOS_REGISTRY_ROOT=/app/arifos-model-registry
COPY arifos-model-registry/ /app/arifos-model-registry/
```

Or mount as a volume:
```bash
docker run -v /host/path/arifos-model-registry:/app/registry:ro ...
```

## Fallback Behavior (without ARIFOS_REGISTRY_ROOT)

If the env var is NOT set, the kernel attempts these locations in order:
1. `/root/arifos-model-registry` — af-forge VPS (production)
2. `/app/registry` — Docker container default
3. `./arifos-model-registry` — relative to arifOS repo
4. `./registry` — legacy relative

**These are best-effort fallbacks, not guaranteed.** A non-VPS install without the env var set will likely fail with a `FileNotFoundError` or operate with missing registry data.

## Registry Structure

```
arifos-model-registry/
├── catalog.json          # Master index of all models
├── models/               # Per-model governance cards (*.json)
├── provider_souls/       # Provider capability manifests
└── runtime_profiles/     # Per-model runtime configuration
```

## Verification

```bash
# Check registry is found
python -c "
from arifosmcp.runtime.registry_client import REGISTRY_ROOT, ModelRegistryClient
client = ModelRegistryClient()
print(f'Registry: {REGISTRY_ROOT}')
print(f'Models: {len(client.list_models())}')
print(f'Providers: {len(client.list_providers())}')
"
```

## Updating the Spine

```bash
cd /opt/arifos-model-registry
git pull origin main
systemctl restart arifos  # or your service name
```

---

**DITEMPA BUKAN DIBERI** — The spine is sovereign territory. Point it where you need it.
