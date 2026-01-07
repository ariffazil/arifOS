"""
test_sealion_api_key_detection.py - Regression test for SEALION_API_KEY support

Verifies that the SEA-LION evaluation harness correctly detects SEALION_API_KEY
without requiring duplication to ARIF_LLM_API_KEY.

Author: arifOS Project
Version: v45Ω Patch B.1
"""

import os
import pytest
from unittest.mock import patch

from arifos_core.integration.connectors.litellm_gateway import LiteLLMConfig


def test_sealion_api_key_detection_in_litellm_config():
    """
    Regression: SEALION_API_KEY must be detected as first-class API key.

    Before fix: Only ARIF_LLM_API_KEY, LLM_API_KEY, OPENAI_API_KEY were checked.
    After fix: SEALION_API_KEY is checked with priority after ARIF_LLM_API_KEY.
    """
    with patch.dict(os.environ, {
        "SEALION_API_KEY": "test-sealion-key-123",
        "ARIF_LLM_PROVIDER": "sealion",
    }, clear=True):
        config = LiteLLMConfig()

        # Should detect SEALION_API_KEY without requiring ARIF_LLM_API_KEY
        assert config.api_key == "test-sealion-key-123"
        assert config.provider == "sealion"


def test_api_key_priority_order():
    """
    Verify API key detection priority:
    1. ARIF_LLM_API_KEY (highest priority)
    2. SEALION_API_KEY
    3. LLM_API_KEY
    4. OPENAI_API_KEY (lowest priority)
    """
    # Test 1: ARIF_LLM_API_KEY takes priority over all others
    with patch.dict(os.environ, {
        "ARIF_LLM_API_KEY": "arif-key",
        "SEALION_API_KEY": "sealion-key",
        "LLM_API_KEY": "llm-key",
        "OPENAI_API_KEY": "openai-key",
    }, clear=True):
        config = LiteLLMConfig()
        assert config.api_key == "arif-key"

    # Test 2: SEALION_API_KEY used when ARIF_LLM_API_KEY not set
    with patch.dict(os.environ, {
        "SEALION_API_KEY": "sealion-key",
        "LLM_API_KEY": "llm-key",
        "OPENAI_API_KEY": "openai-key",
    }, clear=True):
        config = LiteLLMConfig()
        assert config.api_key == "sealion-key"

    # Test 3: LLM_API_KEY used when ARIF_LLM_API_KEY and SEALION_API_KEY not set
    with patch.dict(os.environ, {
        "LLM_API_KEY": "llm-key",
        "OPENAI_API_KEY": "openai-key",
    }, clear=True):
        config = LiteLLMConfig()
        assert config.api_key == "llm-key"

    # Test 4: OPENAI_API_KEY used as last resort
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "openai-key",
    }, clear=True):
        config = LiteLLMConfig()
        assert config.api_key == "openai-key"


def test_no_api_key_raises_error():
    """Verify that missing API key raises helpful error."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            LiteLLMConfig()

        # Error message should mention all accepted key names
        error_msg = str(exc_info.value)
        assert "SEALION_API_KEY" in error_msg
        assert "ARIF_LLM_API_KEY" in error_msg


def test_harness_validate_environment_detects_sealion_key():
    """
    Verify that harness validate_environment() function accepts SEALION_API_KEY.

    This is the main entry point for the SEA-LION full evaluation suite.
    """
    # Import here to avoid circular dependencies
    import sys
    from pathlib import Path

    # Add scripts directory to path
    scripts_dir = Path(__file__).parent.parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    try:
        from sealion_full_suite_v45 import validate_environment

        with patch.dict(os.environ, {
            "SEALION_API_KEY": "test-sealion-key-456",
            "ARIF_LLM_PROVIDER": "sealion",
            "ARIF_LLM_MODEL": "Qwen-SEA-LION-v4-32B-IT",
        }, clear=True):
            env_vars = validate_environment()

            # Should NOT raise ValueError
            assert env_vars is not None
            # Should track which key source was used
            assert env_vars["api_key_source"] == "SEALION_API_KEY"

    finally:
        sys.path.remove(str(scripts_dir))


def test_harness_api_key_source_tracking():
    """Verify that harness tracks which API key source was detected."""
    import sys
    from pathlib import Path

    scripts_dir = Path(__file__).parent.parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    try:
        from sealion_full_suite_v45 import validate_environment

        # Test ARIF_LLM_API_KEY source
        with patch.dict(os.environ, {
            "ARIF_LLM_API_KEY": "test-key",
        }, clear=True):
            env_vars = validate_environment()
            assert env_vars["api_key_source"] == "ARIF_LLM_API_KEY"

        # Test SEALION_API_KEY source
        with patch.dict(os.environ, {
            "SEALION_API_KEY": "test-key",
        }, clear=True):
            env_vars = validate_environment()
            assert env_vars["api_key_source"] == "SEALION_API_KEY"

        # Test OPENAI_API_KEY source
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
        }, clear=True):
            env_vars = validate_environment()
            assert env_vars["api_key_source"] == "OPENAI_API_KEY"

    finally:
        sys.path.remove(str(scripts_dir))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
