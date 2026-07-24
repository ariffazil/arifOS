# Federation Canonical JSON — FCJ-v1

**Status:** HARDENED DRAFT (not F13-ratified)
**Owner:** arifOS
**Purpose:** Deterministic `payload_hash` across languages.

## Algorithm (payload only)

1. Serialize payload with FCJ-v1:
   - UTF-8
   - Object keys sorted by Unicode code point
   - Separators `","` and `":"` (no whitespace)
   - `ensure_ascii=False`
   - Arrays preserve order
   - Numbers use host JSON number form (no JCS number rewrite)
2. SHA-256 over those UTF-8 bytes
3. Emit `sha256:` + lowercase hex (64 chars)

## Python reference

```python
import hashlib, json
def payload_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

## RFC 8785 / JCS

FCJ-v1 is a federation-owned profile **inspired by** JCS key-sorting and compact form.
It is **not** full RFC 8785. Full JCS adoption would be a later minor revision.
