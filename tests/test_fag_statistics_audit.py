"""
Test FAG statistics and audit logging features.

Tests v41.0.0 enhancements:
- Access statistics tracking
- Audit file logging for denied access
"""

import json
import tempfile
from pathlib import Path

import pytest

from arifos_core.governance.fag import FAG


class TestFAGStatistics:
    """Test access statistics tracking."""
    
    def test_statistics_initialization(self, tmp_path):
        """Test that statistics are initialized correctly."""
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        stats = fag.get_access_statistics()
        assert stats["total_granted"] == 0
        assert stats["total_denied"] == 0
        assert stats["total_attempts"] == 0
        assert stats["success_rate"] == 0.0
    
    def test_statistics_track_granted_access(self, tmp_path):
        """Test that granted access is counted."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, arifOS!")
        
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Read file successfully
        result = fag.read("test.txt")
        assert result.verdict == "SEAL"
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_granted"] == 1
        assert stats["total_denied"] == 0
        assert stats["success_rate"] == 100.0
    
    def test_statistics_track_denied_f9_c_dark(self, tmp_path):
        """Test that F9 C_dark violations are counted."""
        # Create a forbidden file
        secret_file = tmp_path / ".env"
        secret_file.write_text("SECRET_KEY=12345")
        
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Try to read forbidden file
        result = fag.read(".env")
        assert result.verdict == "VOID"
        assert "F9 C_dark" in result.reason
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_denied"] == 1
        assert stats["f9_c_dark_fail"] == 1
        assert stats["success_rate"] == 0.0
    
    def test_statistics_track_denied_f2_truth(self, tmp_path):
        """Test that F2 Truth violations are counted."""
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Try to read non-existent file
        result = fag.read("nonexistent.txt")
        assert result.verdict == "VOID"
        assert "F2 Truth" in result.reason
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_denied"] == 1
        assert stats["f2_truth_fail"] == 1
    
    def test_statistics_track_denied_f4_delta_s(self, tmp_path):
        """Test that F4 DeltaS violations are counted."""
        # Create binary file
        binary_file = tmp_path / "test.exe"
        binary_file.write_bytes(b"\x00\x01\x02\x03")
        
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Try to read binary file
        result = fag.read("test.exe")
        assert result.verdict == "VOID"
        assert "F4 DeltaS" in result.reason
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_denied"] == 1
        assert stats["f4_delta_s_fail"] == 1
    
    def test_statistics_mixed_access(self, tmp_path):
        """Test statistics with mixed granted and denied access."""
        # Create test files
        (tmp_path / "good1.txt").write_text("OK")
        (tmp_path / "good2.txt").write_text("OK")
        (tmp_path / ".env").write_text("SECRET")
        (tmp_path / "test.exe").write_bytes(b"\x00")
        
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Mixed access patterns
        fag.read("good1.txt")  # SEAL
        fag.read("good2.txt")  # SEAL
        fag.read(".env")       # VOID (F9)
        fag.read("test.exe")   # VOID (F4)
        fag.read("missing.txt")  # VOID (F2)
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_granted"] == 2
        assert stats["total_denied"] == 3
        assert stats["total_attempts"] == 5
        assert stats["success_rate"] == 40.0
        assert stats["f9_c_dark_fail"] == 1
        assert stats["f4_delta_s_fail"] == 1
        assert stats["f2_truth_fail"] == 1


class TestFAGAuditFile:
    """Test audit file logging for denied access."""
    
    def test_audit_file_disabled_by_default(self, tmp_path):
        """Test that audit file is not created when disabled."""
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        # Try denied access
        fag.read("nonexistent.txt")
        
        # Audit file should not exist
        audit_file = tmp_path / "fag_audit.jsonl"
        assert not audit_file.exists()
    
    def test_audit_file_logs_denied_access(self, tmp_path):
        """Test that denied access is logged to audit file."""
        audit_path = tmp_path / "custom_audit.jsonl"
        
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            audit_file_path=str(audit_path),
        )
        
        # Denied access
        result = fag.read("nonexistent.txt")
        assert result.verdict == "VOID"
        
        # Check audit file
        assert audit_path.exists()
        
        # Parse JSONL
        with open(audit_path, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        entry = json.loads(lines[0])
        
        assert entry["verdict"] == "VOID"
        assert entry["path"] == "nonexistent.txt"
        assert "F2 Truth" in entry["reason"]
        assert "timestamp" in entry
        assert "floor_scores" in entry
    
    def test_audit_file_multiple_entries(self, tmp_path):
        """Test that multiple denied access attempts are logged."""
        audit_path = tmp_path / "audit.jsonl"
        
        # Create forbidden file
        (tmp_path / ".env").write_text("SECRET")
        
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            audit_file_path=str(audit_path),
        )
        
        # Multiple denied access
        fag.read("missing1.txt")  # F2 Truth
        fag.read(".env")          # F9 C_dark
        fag.read("missing2.txt")  # F2 Truth
        
        # Check audit file
        with open(audit_path, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        
        # Verify entries
        entry1 = json.loads(lines[0])
        assert "F2 Truth" in entry1["reason"]
        
        entry2 = json.loads(lines[1])
        assert "F9 C_dark" in entry2["reason"]
        
        entry3 = json.loads(lines[2])
        assert "F2 Truth" in entry3["reason"]
    
    def test_audit_file_only_logs_void_verdicts(self, tmp_path):
        """Test that SEAL verdicts are NOT logged to audit file."""
        audit_path = tmp_path / "audit.jsonl"
        
        # Create good file
        (tmp_path / "good.txt").write_text("OK")
        
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            audit_file_path=str(audit_path),
        )
        
        # Granted access
        result = fag.read("good.txt")
        assert result.verdict == "SEAL"
        
        # Audit file should not exist (no denied access)
        assert not audit_path.exists()
    
    def test_audit_file_default_location(self, tmp_path):
        """Test that default audit file location is <root>/fag_audit.jsonl."""
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
        )
        
        # Denied access
        fag.read("missing.txt")
        
        # Check default location
        default_audit = tmp_path / "fag_audit.jsonl"
        assert default_audit.exists()


class TestFAGIntegration:
    """Integration tests for statistics + audit file."""
    
    def test_combined_statistics_and_audit(self, tmp_path):
        """Test that statistics and audit file work together."""
        audit_path = tmp_path / "audit.jsonl"
        
        # Create test files
        (tmp_path / "good.txt").write_text("OK")
        (tmp_path / ".env").write_text("SECRET")
        
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            audit_file_path=str(audit_path),
        )
        
        # Mixed access
        fag.read("good.txt")      # SEAL
        fag.read(".env")          # VOID
        fag.read("missing.txt")   # VOID
        
        # Check statistics
        stats = fag.get_access_statistics()
        assert stats["total_granted"] == 1
        assert stats["total_denied"] == 2
        
        # Check audit file (only VOID entries)
        with open(audit_path, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 2  # Only 2 denied access
