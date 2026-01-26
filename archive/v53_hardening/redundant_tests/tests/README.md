# Body API Tests (v39/v51)

**Scope:** HTTP Interface
**Target:** `arifos.api`

This directory tests the **FastAPI** layer of arifOS.

**What is tested:**
1.  **Endpoints:** `/`, `/health`, `/v1/govern`.
2.  **Payloads:** JSON serialization/deserialization (Pydantic models).
3.  **Error Handling:** HTTP 500/400 mapping from Constitutional Exceptions.
4.  **Performance:** Latency of the HTTP wrapper (overhead).

**Key Command:**
```bash
pytest arifos/tests/test_api.py
# or
pytest -m api
```
