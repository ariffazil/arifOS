from __future__ import annotations

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "deploy_production.py"

spec = importlib.util.spec_from_file_location("deploy_production_shared", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)

normalize_release_version = module.normalize_release_version
build_overlay_image_tag = module.build_overlay_image_tag
deployment_tool_contract = module.deployment_tool_contract
build_vps_overlay_script = module.build_vps_overlay_script
run_remote_bash = module.run_remote_bash
PUBLIC_DEPLOYMENT_TOOLS = module.PUBLIC_DEPLOYMENT_TOOLS
subprocess = module.subprocess
