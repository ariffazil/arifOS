"""
Tests for FAG (File Access Governance) - v41

Tests constitutional floor enforcement on file I/O operations.
"""

import pytest
import tempfile
from pathlib import Path

from arifos_core.governance.fag import FAG, FAGReadResult, fag_read


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Safe files
        (root / "safe.txt").write_text("Safe content")
        (root / "README.md").write_text("# Test README")
        
        # Forbidden files
        (root / ".env").write_text("SECRET_KEY=dangerous")
        (root / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
        
        # Binary file
        (root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        
        # Subdirectory
        subdir = root / "src"
        subdir.mkdir()
        (subdir / "main.py").write_text("print('hello')")
        
        yield root


class TestFAGBasicRead:
    """Test basic read operations."""
    
    def test_read_safe_file_seal(self, temp_workspace):
        """SEAL verdict for safe file."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("safe.txt")
        
        assert result.verdict == "SEAL"
        assert result.content == "Safe content"
        assert result.reason is None
        assert result.floor_scores["F1_amanah"] == 1.0
        assert result.floor_scores["F2_truth"] == 0.99
    
    def test_read_subdirectory_file_seal(self, temp_workspace):
        """SEAL verdict for file in subdirectory."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("src/main.py")
        
        assert result.verdict == "SEAL"
        assert result.content == "print('hello')"


class TestFAGF1Amanah:
    """Test F1 Amanah enforcement (root jail)."""
    
    def test_path_traversal_blocked(self, temp_workspace):
        """VOID verdict for path traversal attempt."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("../etc/passwd")
        
        assert result.verdict == "VOID"
        assert "F1 Amanah FAIL" in result.reason
        assert "outside root jail" in result.reason
    
    def test_absolute_path_outside_jail_blocked(self, temp_workspace):
        """VOID verdict for absolute path outside jail."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("/etc/passwd")
        
        assert result.verdict == "VOID"
        assert "F1 Amanah FAIL" in result.reason


class TestFAGF2Truth:
    """Test F2 Truth enforcement (file existence)."""
    
    def test_nonexistent_file_void(self, temp_workspace):
        """VOID verdict for nonexistent file."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("does_not_exist.txt")
        
        assert result.verdict == "VOID"
        assert "F2 Truth FAIL" in result.reason
        assert "does not exist" in result.reason
    
    def test_directory_not_file_void(self, temp_workspace):
        """VOID verdict for directory."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("src")
        
        assert result.verdict == "VOID"
        assert "F2 Truth FAIL" in result.reason
        assert "Not a regular file" in result.reason


class TestFAGF4DeltaS:
    """Test F4 DeltaS enforcement (binary rejection)."""
    
    def test_binary_file_rejected(self, temp_workspace):
        """VOID verdict for binary file."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("image.png")
        
        assert result.verdict == "VOID"
        assert "F4 DeltaS FAIL" in result.reason
        assert "Binary file rejected" in result.reason


class TestFAGF9CDark:
    """Test F9 C_dark enforcement (secret blocking)."""
    
    def test_dotenv_blocked(self, temp_workspace):
        """VOID verdict for .env file."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read(".env")
        
        assert result.verdict == "VOID"
        assert "F9 C_dark FAIL" in result.reason
        assert "Forbidden pattern" in result.reason
        assert result.floor_scores["F9_c_dark"] == 1.0  # Maximum dark cleverness
    
    def test_ssh_key_blocked(self, temp_workspace):
        """VOID verdict for SSH private key."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("id_rsa")
        
        assert result.verdict == "VOID"
        assert "F9 C_dark FAIL" in result.reason


class TestFAGConvenienceFunction:
    """Test convenience function."""
    
    def test_fag_read_function(self, temp_workspace):
        """Test fag_read() convenience function."""
        result = fag_read(
            path="safe.txt",
            root=str(temp_workspace),
            enable_ledger=False,
        )
        
        assert result.verdict == "SEAL"
        assert result.content == "Safe content"


class TestFAGLedgerIntegration:
    """Test Cooling Ledger integration."""
    
    def test_ledger_enabled_by_default(self, temp_workspace):
        """Ledger logging enabled by default."""
        fag = FAG(root=str(temp_workspace), enable_ledger=True)
        result = fag.read("safe.txt")
        
        assert result.verdict == "SEAL"
        assert result.ledger_entry_id is not None  # Timestamp from ledger
    
    def test_ledger_disabled_when_requested(self, temp_workspace):
        """Ledger logging can be disabled."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        result = fag.read("safe.txt")
        
        assert result.verdict == "SEAL"
        # ledger_entry_id will still be None when disabled


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
