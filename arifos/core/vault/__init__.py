"""
Shim for Vault -> arifos.core.memory.vault
"""
import sys
from arifos.core.memory import vault

# Re-export everything from the new location
sys.modules["arifos.core.vault"] = vault
from arifos.core.memory.vault import *
