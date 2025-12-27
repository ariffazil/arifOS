#!/usr/bin/env python3
"""
Smoke tests for demo_sealion_raw_vs_governed.py

Tests that DO NOT call external APIs:
- CLI argument parsing
- Log directory creation
- Graceful handling when API key is missing
- Configuration validation

Tests that CALL external APIs are skipped by default.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCLIParsing:
    """Test command-line argument parsing"""

    def test_default_arguments(self):
        """Test default CLI arguments are set correctly"""
        from demo_sealion_raw_vs_governed import main
        import argparse

        # Mock sys.argv to simulate no CLI args
        with patch("sys.argv", ["demo_sealion_raw_vs_governed.py"]):
            # Mock argparse to capture parsed args
            original_parse_args = argparse.ArgumentParser.parse_args

            captured_args = None

            def capture_parse_args(self, args=None):
                nonlocal captured_args
                captured_args = original_parse_args(self, args)
                return captured_args

            with patch.object(argparse.ArgumentParser, "parse_args", capture_parse_args):
                # Mock RawVsGovernedDemo to prevent actual execution
                with patch("demo_sealion_raw_vs_governed.RawVsGovernedDemo") as mock_demo:
                    mock_instance = MagicMock()
                    mock_demo.return_value = mock_instance

                    try:
                        main()
                    except SystemExit:
                        pass

            # Verify defaults
            assert captured_args is not None
            assert captured_args.prompt == "Explain in 5 bullets how arifOS governs an LLM."
            assert captured_args.model == "Qwen-SEA-LION-v4-32B-IT"
            assert captured_args.max_tokens == 512
            assert captured_args.temperature == 0.2

    def test_custom_arguments(self):
        """Test custom CLI arguments are parsed correctly"""
        from demo_sealion_raw_vs_governed import main
        import argparse

        test_args = [
            "demo_sealion_raw_vs_governed.py",
            "--prompt", "Test prompt",
            "--model", "test-model",
            "--max_tokens", "256",
            "--temperature", "0.5",
        ]

        with patch("sys.argv", test_args):
            original_parse_args = argparse.ArgumentParser.parse_args

            captured_args = None

            def capture_parse_args(self, args=None):
                nonlocal captured_args
                captured_args = original_parse_args(self, args)
                return captured_args

            with patch.object(argparse.ArgumentParser, "parse_args", capture_parse_args):
                with patch("demo_sealion_raw_vs_governed.RawVsGovernedDemo") as mock_demo:
                    mock_instance = MagicMock()
                    mock_demo.return_value = mock_instance

                    try:
                        main()
                    except SystemExit:
                        pass

            assert captured_args is not None
            assert captured_args.prompt == "Test prompt"
            assert captured_args.model == "test-model"
            assert captured_args.max_tokens == 256
            assert captured_args.temperature == 0.5


class TestInitialization:
    """Test demo initialization and configuration"""

    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo

        # Clear all API key environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API Key not found"):
                RawVsGovernedDemo()

    def test_api_key_priority_arif_llm_api_key(self):
        """Test ARIF_LLM_API_KEY has highest priority"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo

        test_key = "test-arif-key"

        with patch.dict(
            os.environ,
            {
                "ARIF_LLM_API_KEY": test_key,
                "SEALION_API_KEY": "other-key",
                "LLM_API_KEY": "another-key",
                "OPENAI_API_KEY": "yet-another-key",
            },
        ):
            # Mock make_llm_generate to prevent actual LLM initialization
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()
                assert demo.api_key == test_key

    def test_api_key_fallback_chain(self):
        """Test API key fallback priority chain"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo

        # Test SEALION_API_KEY (second priority)
        with patch.dict(os.environ, {"SEALION_API_KEY": "sealion-key"}, clear=True):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()
                assert demo.api_key == "sealion-key"

        # Test LLM_API_KEY (third priority)
        with patch.dict(os.environ, {"LLM_API_KEY": "llm-key"}, clear=True):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()
                assert demo.api_key == "llm-key"

        # Test OPENAI_API_KEY (fourth priority)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-key"}, clear=True):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()
                assert demo.api_key == "openai-key"

    def test_log_directory_creation(self):
        """Test that log directory is created on initialization"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo

        with patch.dict(os.environ, {"ARIF_LLM_API_KEY": "test-key"}):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()

                # Check log directory exists
                expected_log_dir = Path(__file__).parent / "_runs"
                assert demo.log_dir == expected_log_dir
                assert demo.log_dir.exists()
                assert demo.log_dir.is_dir()

    def test_custom_model_configuration(self):
        """Test custom model parameters are set correctly"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo

        with patch.dict(os.environ, {"ARIF_LLM_API_KEY": "test-key"}):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo(
                    model="custom-model",
                    max_tokens=1024,
                    temperature=0.7,
                )

                assert demo.model == "custom-model"
                assert demo.max_tokens == 1024
                assert demo.temperature == 0.7


class TestLogSaving:
    """Test log saving functionality"""

    def test_log_file_created(self, tmp_path):
        """Test that log file is created with correct format"""
        from demo_sealion_raw_vs_governed import RawVsGovernedDemo
        import json

        with patch.dict(os.environ, {"ARIF_LLM_API_KEY": "test-key"}):
            with patch("demo_sealion_raw_vs_governed.make_llm_generate"):
                demo = RawVsGovernedDemo()

                # Override log directory to use tmp_path
                demo.log_dir = tmp_path

                # Create test results
                raw_result = {
                    "mode": "RAW",
                    "response": "test response",
                    "time_seconds": 1.5,
                    "error": None,
                }
                gov_result = {
                    "mode": "GOVERNED",
                    "verdict": "SEAL",
                    "time_seconds": 2.0,
                    "error": None,
                }

                # Save log
                demo.save_log("test prompt", raw_result, gov_result)

                # Verify log file was created
                log_files = list(tmp_path.glob("raw_vs_governed_*.jsonl"))
                assert len(log_files) == 1

                # Verify log content
                with open(log_files[0], "r", encoding="utf-8") as f:
                    log_entry = json.loads(f.read())

                assert log_entry["prompt"] == "test prompt"
                assert log_entry["raw"] == raw_result
                assert log_entry["governed"] == gov_result
                assert "timestamp" in log_entry


# =============================================================================
# EXTERNAL API TESTS (SKIPPED BY DEFAULT)
# =============================================================================

@pytest.mark.skip(reason="External API call - requires valid API key")
def test_raw_mode_actual_call():
    """Test RAW mode with actual API call (SKIPPED - requires API key)"""
    from demo_sealion_raw_vs_governed import RawVsGovernedDemo

    demo = RawVsGovernedDemo()
    result = demo.run_raw_mode("What is 2+2?")

    assert result["mode"] == "RAW"
    assert result["response"] is not None
    assert result["error"] is None
    assert result["time_seconds"] > 0


@pytest.mark.skip(reason="External API call - requires valid API key")
def test_governed_mode_actual_call():
    """Test GOVERNED mode with actual API call (SKIPPED - requires API key)"""
    from demo_sealion_raw_vs_governed import RawVsGovernedDemo

    demo = RawVsGovernedDemo()
    result = demo.run_governed_mode("What is 2+2?")

    assert result["mode"] == "GOVERNED"
    assert result["verdict"] is not None
    assert result["error"] is None
    assert result["time_seconds"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
