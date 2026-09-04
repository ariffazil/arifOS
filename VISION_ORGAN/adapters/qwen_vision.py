"""
Qwen Token Plan qwen3.8-max vision analysis adapter.
Verified endpoint: https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions
Vision confirmed: 256x256 shape test (5.7s), 512x512 scene (13.5s)
Cost: Qwen Token Plan credits (~258 image tokens per 512x512 image)
"""
import urllib.request
import urllib.error
import json
import base64
import time
import os


class QwenVisionAdapter:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("QWEN_INDIVIDUAL_API_KEY", "")
        self.base_url = "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen3.8-max"

    def analyze_image(self, image_path, prompt, max_tokens=500):
        """Analyze a local image file with vision model."""
        if not self.api_key:
            raise ValueError("QWEN_INDIVIDUAL_API_KEY not set")

        # Read image and convert to base64 data URI
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Detect MIME type
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            mime = "image/png"
        elif image_bytes[:3] == b'\xff\xd8\xff':
            mime = "image/jpeg"
        else:
            mime = "image/png"  # default
        
        data_uri = f"data:{mime};base64,{image_b64}"
        
        return self._call_vision(data_uri, prompt, max_tokens)

    def analyze_image_url(self, image_url, prompt, max_tokens=500):
        """Analyze a remote image URL with vision model."""
        if not self.api_key:
            raise ValueError("QWEN_INDIVIDUAL_API_KEY not set")
        
        # For MiniMax URLs - download and convert to base64 (more reliable than public URL)
        import urllib.request
        req = urllib.request.Request(image_url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            image_bytes = resp.read()
        
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            mime = "image/png"
        elif image_bytes[:3] == b'\xff\xd8\xff':
            mime = "image/jpeg"
        else:
            mime = "image/jpeg"
        
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime};base64,{image_b64}"
        
        return self._call_vision(data_uri, prompt, max_tokens)

    def _call_vision(self, data_uri, prompt, max_tokens):
        """Make the actual vision API call."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }],
            "max_tokens": max_tokens
        }

        start = time.time()
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - start
                
                choices = result.get("choices", [])
                if not choices:
                    raise RuntimeError("Qwen vision returned no choices")
                
                content = choices[0].get("message", {}).get("content", "")
                usage = result.get("usage", {})
                
                return {
                    "provider": "qwen_token_plan",
                    "model": self.model,
                    "content": content,
                    "elapsed_s": round(elapsed, 2),
                    "usage": usage,
                    "image_tokens": usage.get("prompt_tokens_details", {}).get("image_tokens", 0),
                }
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"Qwen vision HTTP {e.code}: {body[:500]}")

    def quality_gate(self, image_path, scene_contract):
        """Run atomic quality gate analysis against a scene contract."""
        sc = scene_contract.get("scene_contract", {})
        
        # Build atomic check prompt from scene contract
        checks_prompt = self._build_quality_prompt(sc)
        
        result = self.analyze_image(image_path, checks_prompt, max_tokens=600)
        
        # Parse JSON response
        try:
            content = result["content"]
            # Extract JSON from response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                checks = json.loads(json_str)
            else:
                checks = {"error": "Failed to parse JSON", "raw": content}
        except json.JSONDecodeError:
            checks = {"error": "Invalid JSON response", "raw": result["content"]}
        
        return {
            "provider": "qwen_token_plan",
            "model": self.model,
            "checks": checks,
            "elapsed_s": result["elapsed_s"],
            "image_tokens": result["image_tokens"],
        }

    def _build_quality_prompt(self, scene_contract):
        """Build atomic quality gate prompt from scene contract."""
        prompt = """You are an image-quality verifier. Inspect the supplied image strictly against the Scene Contract below.

Do not infer details that are not visibly supported.
For each check return PASS, FAIL, or UNCERTAIN.
Return JSON only. Do not explain in prose.

Scene Contract:
"""
        if scene_contract.get("subject"):
            prompt += f"- Subject: {scene_contract['subject']}\n"
        if scene_contract.get("required_objects"):
            prompt += f"- Required objects: {', '.join(scene_contract['required_objects'])}\n"
        if scene_contract.get("action"):
            action = scene_contract["action"]
            prompt += f"- Action: {action.get('verb', '')} using {action.get('tool', '')} on {action.get('target', '')}\n"
            if action.get("required_relation"):
                prompt += f"- Required relation: {action['required_relation']}\n"
        if scene_contract.get("setting"):
            prompt += f"- Setting: {scene_contract['setting']}\n"
        if scene_contract.get("camera"):
            prompt += f"- Camera: {scene_contract['camera']}\n"
        if scene_contract.get("negative_constraints"):
            prompt += f"- Must NOT have: {', '.join(scene_contract['negative_constraints'])}\n"
        
        prompt += """
Checks to perform (return PASS, FAIL, or UNCERTAIN for each):
1. Subject present and matches description
2. All required objects visible
3. Required action depicted
4. Required spatial relation satisfied
5. Setting matches contract
6. Camera framing correct
7. No negative constraint violations
8. No obvious anatomy errors (extra limbs, fingers)
9. No text overlay or watermark

Return JSON with keys matching each check, plus "overall" (PASS/REJECT/HUMAN_REVIEW), "confidence" (0.0-1.0), and "rejection_reasons" (list of strings)."""
        
        return prompt
