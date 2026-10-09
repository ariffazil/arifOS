"""
MiniMax image-01 generation adapter.
Verified endpoint: https://api.minimax.io/v1/image_generation
Response format: {"data": {"image_urls": ["..."]}, "base_resp": {"status_code": 0}}
URL expiry: 24 hours - must be downloaded immediately.
Cost: ~$0.0035 per image.
"""
import urllib.request
import urllib.error
import json
import time
import os
import base64


class MiniMaxImage01Adapter:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self.base_url = "https://api.minimax.io/v1"
        self.model = "image-01"

    def generate(self, prompt, aspect_ratio="1:1", n=1, response_format="url", prompt_optimizer=False):
        """Generate image(s) from prompt. Returns list of image URLs."""
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not set")

        url = f"{self.base_url}/image_generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n,
        }

        if prompt_optimizer is not None:
            payload["prompt_optimizer"] = prompt_optimizer

        start = time.time()
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - start

                base_resp = result.get("base_resp", {})
                if base_resp.get("status_code") != 0:
                    raise RuntimeError(
                        f"MiniMax generation failed: {base_resp.get('status_msg', 'unknown')}"
                    )

                image_data = result.get("data", {})
                image_urls = image_data.get("image_urls", [])
                if not image_urls:
                    raise RuntimeError("MiniMax returned no image URLs")

                return {
                    "provider": "minimax",
                    "model": self.model,
                    "image_urls": image_urls,
                    "elapsed_s": round(elapsed, 2),
                    "expires_in_hours": 24,
                    "prompt_fingerprint": hash(prompt),
                    "trace": {
                        "request_id": result.get("id", ""),
                        "metadata": result.get("metadata", {}),
                    },
                }
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"MiniMax HTTP {e.code}: {body[:500]}")

    def download_image(self, url, save_path):
        """Download image from MiniMax URL (expires in 24h)."""
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            image_bytes = resp.read()
            with open(save_path, "wb") as f:
                f.write(image_bytes)
            return {
                "path": save_path,
                "size_bytes": len(image_bytes),
                "hash": hash(image_bytes),
            }
