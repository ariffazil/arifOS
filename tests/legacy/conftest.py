"""
tests/legacy/conftest.py — Skip all legacy tests

These tests reference deprecated APIs and are archived for reference only.
See tests/legacy/README.md for details.
"""


def pytest_ignore_collect(collection_path, config):
    """Skip all test collection in this directory."""
    return True
