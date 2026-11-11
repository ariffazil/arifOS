"""Canonical identity contract module forwarder.

Anti-split-brain invariant (Gap 14 closure, F13 2026-11-10):
sys.modules must share the exact same module instance so that:
  import contracts.identity as a
  import arifosmcp.contracts.identity as b
  assert a is b
"""
import sys
import contracts.identity as _identity

# Point sys.modules to the canonical module instance to prevent duplicate module objects
sys.modules[__name__] = _identity
