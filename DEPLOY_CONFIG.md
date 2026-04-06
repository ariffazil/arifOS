# arifOS MCP GUI Mode - Deploy Config
# Add mode="gui" support to existing tools for ChatGPT Apps SDK

# ═══════════════════════════════════════════════════════════════════════
# DEPLOY: Copy these files to arifOS MCP server (VPS)
# ═══════════════════════════════════════════════════════════════════════

# Files to add (new):
# - core/gui/__init__.py
# - core/gui/widgets.py
# - core/gui/dashboard_builder.py

# Files to modify:
# - runtime/megaTools/tool_03_apex_soul.py (add mode param + GUI branch)
# - runtime/megaTools/tool_01_init_anchor.py (add mode param + GUI branch)

# ═══════════════════════════════════════════════════════════════════════
# Quick Deploy (VPS):
# ═══════════════════════════════════════════════════════════════════════
# cd /root/arifOS
# git pull origin main
# docker compose restart