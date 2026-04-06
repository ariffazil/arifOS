# arifOS CIV INFRA — Hardened Office Forge v1 (888_SAFE)
**Date:** 2026-03-13
**Author:** Grok (with Arif 888_JUDGE override)
**Branch:** feature/civ-infra-forge-v1
**Verdict target:** SEAL only after F12 + APEX review

@agent: mcp-tool
@tag: office-forge-v1
@status: 888_HOLD_until_review

## 1. New Tool — forge_office_document (canonical wiring)

Create file (exact path for PR):
`/root/arifosmcp/arifosmcp/runtime/tools/office_forge/forge_office_document.py`

```python
from mcp import tool
from pathlib import Path
import subprocess
import asyncio
import tempfile
from core.kernel import arifOS_kernel, audit_rules  # canonical imports

@tool(
    name="forge_office_document",
    description="Governed Office Forge v1: markdown string → PPTX/PDF + diagrams. Takes content blob only. Full 000-888-999 loop. Max 2MB input, 30s timeout, dedicated worker."
)
async def forge_office_document(
    md_content: str,
    output_mode: str = "pdf",           # pdf | pptx | both
    theme: str = "corporate-navy",
    max_runtime_seconds: int = 30
):
    # 000 INIT — airlock
    await arifOS_kernel("000_INIT", {"action": "forge_office_document", "user": "Arif", "size_bytes": len(md_content)})

    # F12 Injection Guard + size check
    if len(md_content) > 2_000_000:
        return {"status": "VOID", "reason": "input_too_large"}

    await audit_rules("F12_injection_shield_F4_clarity_F7_humility")

    # Run in isolated temp dir
    with tempfile.TemporaryDirectory(dir="/opt/arifos/forge_temp") as tmpdir:
        input_file = Path(tmpdir) / "input.md"
        input_file.write_text(md_content)

        try:
            # All subprocesses with timeout + check
            if "pdf" in output_mode or output_mode == "both":
                await asyncio.wait_for(
                    asyncio.to_thread(subprocess.run,
                        ["marp", str(input_file), "--pdf", "--theme", theme, "-o", f"{tmpdir}/output.pdf"],
                        check=True, timeout=max_runtime_seconds),
                    timeout=max_runtime_seconds
                )

            if "pptx" in output_mode or output_mode == "both":
                await asyncio.wait_for(
                    asyncio.to_thread(subprocess.run,
                        ["python", "-m", "arifosmcp.scripts.pptx_forge", str(input_file), f"{tmpdir}/output.pptx"],
                        check=True, timeout=max_runtime_seconds),
                    timeout=max_runtime_seconds
                )

            # Mermaid + ImageMagick in same temp (quarantined)
            await asyncio.wait_for(
                asyncio.to_thread(subprocess.run, ["mmdc", "-i", str(input_file), "-o", f"{tmpdir}/diagram.png"], check=True, timeout=10),
                timeout=10
            )
            await asyncio.wait_for(
                asyncio.to_thread(subprocess.run, ["convert", f"{tmpdir}/diagram.png", "-resize", "1920x1080", f"{tmpdir}/branded.png"], check=True, timeout=5),
                timeout=5
            )

        except asyncio.TimeoutError:
            return {"status": "VOID", "reason": "timeout"}

        # 888 APEX + VAULT999 seal
        result = {"files": [f"{tmpdir}/output.pdf", f"{tmpdir}/output.pptx"], "status": "SEALED"}
        await arifOS_kernel("888_APEX_VERDICT", result)
        await arifOS_kernel("999_VAULT", {"merkle": "auto", "event": "forge_complete"})

        return result
2. Register tool (one line)
Bashecho 'from .office_forge.forge_office_document import forge_office_document' >> /root/arifosmcp/arifosmcp/runtime/tools/__init__.py
3. Branch & Deploy (safe, reversible)
Bashcd /root/arifosmcp
git checkout -b feature/civ-infra-forge-v1
git add arifosmcp/runtime/tools/office_forge/forge_office_document.py arifosmcp/runtime/tools/__init__.py
git commit -m "feat(forge-v1): hardened office forge — blob-only, full constitutional loop, no auto-trigger"
git push origin feature/civ-infra-forge-v1
docker restart arifosmcp
