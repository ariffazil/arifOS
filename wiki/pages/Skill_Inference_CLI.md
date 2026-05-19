---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- ai-ops
audience:
- engineers
- operators
- creators
difficulty: beginner
prerequisites:
- MCP_Tools
tags:
- inference.sh
- infsh
- cli
- image-generation
- video-generation
- llm
- search
- ai-apps
- flux
- veo
sources:
- Hermes official skill: official/devops/cli
- inference.sh docs: https://inference.sh/docs
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Inference.sh CLI

**Inference.sh CLI** (`infsh` / `belt`) is the unified gateway to 150+ cloud AI apps — image generation, video creation, LLMs, search, 3D, audio, and social automation. No GPU required.

## Purpose

To give federation agents access to frontier generative AI without managing individual provider APIs:
- Generate images (FLUX, Reve, Seedream, Grok, Gemini)
- Generate video (Veo, Wan, Seedance, OmniHuman)
- Run LLM inference
- AI-powered search (Tavily, Exa)
- Avatar / lip-sync generation
- 3D generation, TTS, Twitter/X automation

## Specifications

- **Stage**: 010 (Forge / Execution)
- **Layer**: MACHINE
- **Trinity**: Δ (Mind — execution against cloud substrate)
- **Floors touched most directly**: F1 (Amanah — API key spend), F4 (Guardrails — content policy), F8 (Audit — all generations logged)

## Installation

```bash
curl -fsSL https://cli.inference.sh | sh
infsh login        # interactive browser auth
# OR for CI/non-interactive:
belt login --key YOUR_API_KEY
```

**Installed on**: `/root` (VPS host)
**Binary**: `/usr/local/bin/infsh` (alias: `belt`)
**Docs**: https://inference.sh/docs

## Authentication

| Method | Command | Use Case |
| :--- | :--- | :--- |
| Browser | `infsh login` | Interactive / development |
| API Key | `belt login --key <key>` | CI/CD, agents, non-interactive |
| Guest | `belt app store` | Browse public catalog without auth |

Get API key: https://app.inference.sh/settings/keys

## Workflow

### 1. Search (never guess app IDs)
```bash
infsh app list --search flux
infsh app list --search video
infsh app list --search image
```

### 2. Run
```bash
infsh app run <app-id> --input '{"prompt": "your prompt"}' --json
```

### 3. Parse
JSON output contains media URLs. Present with `MEDIA:<url>` for inline display.

## Common Commands

### Image Generation
```bash
# FLUX Dev with LoRA
infsh app run falai/flux-dev-lora --input '{"prompt": "sunset over mountains", "num_images": 1}' --json

# Gemini image generation
infsh app run google/gemini-2-5-flash-image --input '{"prompt": "futuristic city", "num_images": 1}' --json

# Seedream (ByteDance)
infsh app run bytedance/seedream-5-lite --input '{"prompt": "nature scene"}' --json

# Grok Imagine (xAI)
infsh app run xai/grok-imagine-image --input '{"prompt": "abstract art"}' --json
```

### Video Generation
```bash
# Veo 3.1 (Google)
infsh app run google/veo-3-1-fast --input '{"prompt": "drone shot of coastline"}' --json

# Seedance (ByteDance)
infsh app run bytedance/seedance-1-5-pro --input '{"prompt": "dancing figure", "resolution": "1080p"}' --json

# Wan 2.5
infsh app run falai/wan-2-5 --input '{"prompt": "person walking through city"}' --json
```

### Local File Uploads
The CLI auto-uploads local files when a path is provided:
```bash
# Upscale a local image
infsh app run falai/topaz-image-upscaler --input '{"image": "/path/to/photo.jpg", "upscale_factor": 2}' --json

# Image-to-video from local file
infsh app run falai/wan-2-5-i2v --input '{"image": "/path/to/image.png", "prompt": "make it move"}' --json

# Avatar with audio
infsh app run bytedance/omnihuman-1-5 --input '{"audio": "/path/to/audio.mp3", "image": "/path/to/face.jpg"}' --json
```

### Search & Research
```bash
infsh app run tavily/tavily-search --input '{"query": "latest AI news"}' --json
infsh app run exa/exa-search --input '{"query": "machine learning papers"}' --json
```

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| "not logged in" | Run `infsh login` or `belt login --key <key>` |
| Wrong app ID | Always search first: `infsh app list --search <term>` |
| Raw output unreadable | Always use `--json` for structured output |
| Quotes break shell | Escape JSON properly or use single-quoted strings |
| Long video generation | Warn user: 30-120 seconds typical |

## Federation Context

- **Hermes**: Skill installed at `~/.hermes/skills/devops/cli/`
- **A-FORGE / arifOS**: Can invoke `infsh` via ShellTool or direct subprocess
- **Quota**: Per-inference pricing; monitor spend at https://app.inference.sh

## Related

- [[Skill_Docker_Management]] (Container ops for deploying generated assets)
- [[arifos_forge]] (Execution Bridge)
- [[MCP_Tools]] (Tool surface architecture)
