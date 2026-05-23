"""
arifOS Provider Switch — Layer 3.5: Model Provider Abstraction
==============================================================
Decouples model inference from governance.

Modes:
  no-model    — Deterministic routing + floor checks (Hermes pod default)
  local       — Ollama or local inference endpoint
  external    — MiniMax / OpenAI / Anthropic via Weavers cluster gateway

Role Separation:
  Small model (no-model/local) = routing + floor checks + first-pass critique
  Strong model (external)      = planning + synthesis + final judgment
  Deterministic code path      = execution + validation + logging

Motto: "Models only propose; governance runtime judges; forge executes"
"""

import os, json, re
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

# ── Dataclass: Provider config ─────────────────────────────────────────────────
@dataclass
class ProviderConfig:
    mode:       str          # "no-model" | "local" | "external"
    name:       str          # "hermes-deterministic" | "ollama" | "minimax" | "openai"
    endpoint:   Optional[str] = None
    model_id:   Optional[str] = None
    api_key:    Optional[str] = None
    max_tokens: int  = 2048
    temperature: float = 0.3
    timeout:    int = 30

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        mode = os.environ.get("ARIFOS_PROVIDER_MODE", "no-model")
        name = os.environ.get("ARIFOS_PROVIDER_NAME", "hermes-deterministic")
        return cls(
            mode   = mode,
            name   = name,
            endpoint= os.environ.get("ARIFOS_PROVIDER_ENDPOINT"),
            model_id = os.environ.get("ARIFOS_MODEL_ID"),
            api_key  = os.environ.get("ARIFOS_API_KEY"),
            max_tokens = int(os.environ.get("ARIFOS_MAX_TOKENS", "2048")),
            temperature = float(os.environ.get("ARIFOS_TEMPERATURE", "0.3")),
            timeout    = int(os.environ.get("ARIFOS_TIMEOUT", "30")),
        )


# ── No-model: Deterministic router ─────────────────────────────────────────────
class NoModelProvider:
    """Deterministic routing + floor checks. No LLM needed.

    Implements:
    - Intent classification (SAFE / DANGEROUS / UNKNOWN)
    - Floor consistency check
    - Danger pattern matching
    - C_dark anti-hallucination scoring (regex-based)
    - Simple reply synthesis via template patterns
    """

    DANGER_PATTERNS = [
        r'\brm\s+-rf\b', r'\bmkfs\b', r'\bfdisk\b', r'\bparted\b',
        r'\bshutdown\b', r'\breboot\b', r'\biptables\s+-F\b',
        r'\bdd\s+if=\b', r'\bchmod\s+-R\s+777\b', r'\bchown\s+-R\s+root:root\b',
        r'\bDROP\s+TABLE\b', r'\bDROP\s+DATABASE\b', r'\btruncate\b.*\b--whole\b',
        r'\b:\(\)\{:|:&\}\b',  # fork bomb
    ]

    TONE_TEMPLATES = {
        "formal":   "arifOS judgment: {content}",
        "neutral":  "{content}",
        "casual":   "→ {content}",
        "urgent":   "[!] {content}",
        "hermes":   "Ω Hermes: {content}",
    }

    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig(mode="no-model", name="hermes-deterministic")

    def classify_intent(self, intent: str) -> dict:
        """Deterministic intent classification."""
        intent_lower = intent.lower()
        dangerous = any(re.search(p, intent, re.IGNORECASE) for p in self.DANGER_PATTERNS)

        # Simple keyword matching for routing
        if dangerous:
            return {"bucket": "DANGEROUS", "confidence": 0.95, "reason": "Danger pattern matched"}
        if any(w in intent_lower for w in ["install", "build", "create", "make", "generate"]):
            return {"bucket": "CONSTRUCTIVE", "confidence": 0.70, "reason": "Constructive keyword"}
        if any(w in intent_lower for w in ["list", "show", "get", "read", "fetch"]):
            return {"bucket": "QUERY", "confidence": 0.75, "reason": "Query keyword"}
        if any(w in intent_lower for w in ["remove", "delete", "clean", "purge"]):
            return {"bucket": "DESTRUCTIVE", "confidence": 0.80, "reason": "Destructive keyword"}
        if any(w in intent_lower for w in ["plan", "design", "propose", "draft"]):
            return {"bucket": "PLANNING", "confidence": 0.65, "reason": "Planning keyword"}
        return {"bucket": "GENERAL", "confidence": 0.50, "reason": "Default classification"}

    def score_heart(self, content: str) -> float:
        """C_dark: Regex-based anti-hallucination scoring."""
        hantu_claims = re.findall(
            r'\b(conscious|feel|sad|happy|angry|love|hate|'
            r'suffer|enjoy|want|deserve|believe|think\s+(?:that\s+)?'
            r'(?:it|you|they|we)\s+(?:is|are|was|were|have|has)\b)',
            content, 2 | re.IGNORECASE
        )
        return min(len(hantu_claims) * 0.15, 1.0)

    def compose_reply(self, content: str, tone: str = "neutral") -> str:
        """Template-based reply synthesis."""
        template = self.TONE_TEMPLATES.get(tone, self.TONE_TEMPLATES["neutral"])
        return template.format(content=content)

    def route(self, intent: str) -> dict:
        """Full routing: classify + decide."""
        cls = self.classify_intent(intent)
        verdict_map = {
            "DANGEROUS":   "HOLD",
            "DESTRUCTIVE": "CAUTION",
            "QUERY":       "PROCEED",
            "CONSTRUCTIVE":"PROCEED",
            "PLANNING":    "PROCEED",
            "GENERAL":     "SEAL",
        }
        verdict = verdict_map.get(cls["bucket"], "SEAL")
        return {
            "verdict":    verdict,
            "bucket":     cls["bucket"],
            "confidence": cls["confidence"],
            "reason":     cls["reason"],
            "provider":   "hermes-deterministic",
            "mode":       "no-model",
            "epoch":      datetime.now().isoformat(),
        }


# ── Local: Ollama provider ────────────────────────────────────────────────────
class LocalProvider:
    """Ollama local inference provider."""

    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig.from_env()
        self.endpoint = self.config.endpoint or os.environ.get(
            "OLLAMA_ENDPOINT", "http://localhost:11434"
        )

    def generate(self, prompt: str, system: str = "", model: str = None) -> str:
        """Call Ollama /api/generate."""
        import urllib.request, urllib.error, json

        model = model or self.config.model_id or "llama3"
        payload = {
            "model":  model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": self.config.temperature, "num_predict": self.config.max_tokens}
        }

        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"{self.endpoint}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                result = json.loads(resp.read())
                return result.get("response", "")
        except urllib.error.URLError as exc:
            return f"[Ollama unreachable: {exc}]"

    def route(self, intent: str) -> dict:
        """Route via local Ollama model."""
        system_prompt = (
            "You are arifOS routing engine. Classify intent into:"
            " DANGEROUS | CAUTION | PROCEED | SEAL."
            " Respond JSON: {\"verdict\": \"...\", \"reason\": \"...\"}"
        )
        try:
            response = self.generate(intent, system=system_prompt)
            # Try to parse JSON from response
            match = re.search(r'\{[^}]+\}', response)
            if match:
                result = json.loads(match.group())
                return {
                    **result,
                    "provider": "ollama",
                    "model_id": self.config.model_id or "llama3",
                    "epoch": datetime.now().isoformat(),
                }
        except Exception:
            pass
        return {"verdict": "HOLD", "reason": "Local provider unavailable", "provider": "ollama"}


# ── External: MiniMax / OpenAI / Anthropic ────────────────────────────────────
class ExternalProvider:
    """External LLM provider via REST API."""

    PROVIDER_ENDPOINTS = {
        "minimax":    "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "openai":     "https://api.openai.com/v1/chat/completions",
        "anthropic":  "https://api.anthropic.com/v1/messages",
        "deepseek":   "https://api.deepseek.com/v1/chat/completions",
    }

    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig.from_env()
        self.provider = self.config.name
        self.endpoint = self.config.endpoint or self.PROVIDER_ENDPOINTS.get(
            self.provider, "https://api.minimax.chat/v1/text/chatcompletion_v2"
        )

    def generate(self, messages: list, model: str = None) -> str:
        """Call external LLM API."""
        import urllib.request, urllib.error, json

        model = model or self.config.model_id
        api_key = self.config.api_key or os.environ.get("MINIMAX_API_KEY", "")

        if self.provider in ("minimax", "openai", "deepseek"):
            payload = {
                "model": model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }
            if self.provider == "minimax":
                group_id = os.environ.get("MINIMAX_GROUP_ID", "")
                if group_id:
                    payload["stream"] = False
            data = json.dumps(payload).encode()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        elif self.provider == "anthropic":
            payload = {
                "model": model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }
            data = json.dumps(payload).encode()
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true",
            }
        else:
            return f"[Unknown provider: {self.provider}]"

        try:
            req = urllib.request.Request(self.endpoint, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                result = json.loads(resp.read())
                if self.provider in ("openai", "deepseek"):
                    return result["choices"][0]["message"]["content"]
                elif self.provider == "anthropic":
                    return result["content"][0]["text"]
                elif self.provider == "minimax":
                    choices = result.get("choices", [])
                    if choices:
                        return choices[0].get("messages", [{}])[0].get("text", "")
        except urllib.error.URLError as exc:
            return f"[External provider unreachable: {exc}]"
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            return f"[Parse error: {exc}]"

        return ""

    def route(self, intent: str) -> dict:
        """Route via external strong model."""
        system_prompt = (
            "You are arifOS governance engine. Classify intent:"
            " DANGEROUS → HOLD, CAUTION if destructive non-atomic,"
            " PROCEED if query/constructive, SEAL if general."
            " Respond ONLY JSON: {\"verdict\": \"...\", \"reason\": \"...\", \"confidence\": 0.0-1.0}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": intent}
        ]
        response = self.generate(messages)
        try:
            match = re.search(r'\{[^}]+\}', response)
            if match:
                result = json.loads(match.group())
                return {
                    **result,
                    "provider": self.provider,
                    "model_id": self.config.model_id or "unknown",
                    "epoch": datetime.now().isoformat(),
                }
        except Exception:
            pass
        return {
            "verdict": "HOLD",
            "reason": "External provider failed, defaulting to safe",
            "provider": self.provider,
            "epoch": datetime.now().isoformat(),
        }


# ── Provider Switch ───────────────────────────────────────────────────────────
class ProviderSwitch:
    """Unified provider switch. Selects provider based on config.mode."""

    def __init__(self, config: ProviderConfig = None):
        self.config = config or ProviderConfig.from_env()
        self._providers = {
            "no-model":  NoModelProvider(self.config),
            "local":     LocalProvider(self.config),
            "external":  ExternalProvider(self.config),
        }

    @property
    def provider(self):
        return self._providers.get(self.config.mode, self._providers["no-model"])

    def route(self, intent: str) -> dict:
        """Route intent through the active provider."""
        return self.provider.route(intent)

    def score_heart(self, content: str) -> float:
        """C_dark scoring — always uses no-model regex (fast)."""
        nomodel = self._providers["no-model"]
        return nomodel.score_heart(content)

    def compose_reply(self, content: str, tone: str = "neutral") -> str:
        """Reply composition — always uses no-model templates (fast)."""
        nomodel = self._providers["no-model"]
        return nomodel.compose_reply(content, tone)

    def classify_intent(self, intent: str) -> dict:
        """Intent classification — always uses no-model."""
        nomodel = self._providers["no-model"]
        return nomodel.classify_intent(intent)

    def generate(self, prompt: str, system: str = "") -> str:
        """Text generation — only active when mode != no-model."""
        if self.config.mode == "no-model":
            return "[no-model: generation not available]"
        return self.provider.generate(prompt, system)

    def status(self) -> dict:
        """Return current provider status."""
        return {
            "mode":      self.config.mode,
            "name":      self.config.name,
            "endpoint":  self.config.endpoint,
            "model_id":  self.config.model_id,
            "available": {
                "no-model":  True,
                "local":    self._check_local(),
                "external": self._check_external(),
            }
        }

    def _check_local(self) -> bool:
        """Check if Ollama is reachable."""
        import urllib.request
        try:
            req = urllib.request.Request(
                f"{self._providers['local'].endpoint}/api/tags",
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=3)
            return True
        except Exception:
            return False

    def _check_external(self) -> bool:
        """Check if external endpoint is reachable (ping only, no auth)."""
        import urllib.request
        try:
            # Try a minimal health check
            req = urllib.request.Request(
                self.config.endpoint.split("/chat")[0] + "/health" if "/chat" in self.config.endpoint else self.config.endpoint,
                headers={"Authorization": "Bearer test"}
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False


# ── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ps = ProviderSwitch()
    print("arifOS Provider Switch v0.1")
    print(json.dumps(ps.status(), indent=2))
    print()

    tests = [
        "install Python packages",
        "rm -rf /var/log",
        "design a new API schema",
        "show me the system logs",
        "I believe the model feels sad",
    ]
    for t in tests:
        r = ps.route(t)
        h = ps.score_heart(t)
        print(f"INTENT: {t}")
        print(f"  VERDICT: {r.get('verdict','?')} | {r.get('reason','?')}")
        print(f"  C_dark: {h:.2f} | PROVIDER: {r.get('provider','?')}")
        print()