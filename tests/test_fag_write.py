"""
tests/test_fag_write.py - FAG Write Governance Tests (v42.2)

Tests for FAG.write_validate() implementing FAG Write Contract.

Test Cases:
1. test_new_file_outside_sandbox - HOLD
2. test_new_file_in_sandbox - SEAL
3. test_canon_create_blocked - VOID
4. test_patch_no_read_proof - HOLD
5. test_patch_over_threshold - HOLD
6. test_patch_within_threshold - SEAL
7. test_delete_default - HOLD
"""

import hashlib
import pytest
from pathlib import Path

from arifos_core.governance.fag import FAG, FAGWritePlan, FAGWriteResult


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace with test files."""
    # Create sandbox directories
    (tmp_path / ".arifos_clip").mkdir()
    (tmp_path / "scratch").mkdir()
    
    # Create L1_THEORY (canon zone)
    (tmp_path / "L1_THEORY" / "canon").mkdir(parents=True)
    
    # Create a test file for patching
    test_file = tmp_path / "existing_file.py"
    test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5\n")
    
    return tmp_path


class TestFAGWriteValidateNewFiles:
    """Test Rule 1 & 2: No New Files + Canon Lock."""
    
    def test_new_file_outside_sandbox(self, temp_workspace: Path):
        """Creating new file outside sandbox without allowlist -> HOLD."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="new_file.py",
            operation="create",
            justification="Test new file creation",
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "HOLD"
        assert "No New Files" in result.reason
    
    def test_new_file_in_sandbox_arifos_clip(self, temp_workspace: Path):
        """Creating file in .arifos_clip/ sandbox -> SEAL."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path=".arifos_clip/session.json",
            operation="create",
            justification="Session artifact",
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "SEAL"
    
    def test_new_file_in_sandbox_scratch(self, temp_workspace: Path):
        """Creating file in scratch/ sandbox -> SEAL."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="scratch/temp.txt",
            operation="create",
            justification="Temporary work",
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "SEAL"
    
    def test_new_file_with_allowlist(self, temp_workspace: Path):
        """Creating file on session allowlist -> SEAL."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="docs/new_doc.md",
            operation="create",
            justification="Human approved",
        )
        
        result = fag.write_validate(plan, session_allowlist=["docs/new_doc.md"])
        
        assert result.verdict == "SEAL"
    
    def test_canon_create_blocked(self, temp_workspace: Path):
        """Creating new file in L1_THEORY/ -> VOID (absolute block)."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="L1_THEORY/canon/new_floor.md",
            operation="create",
            justification="Trying to create canon",
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "VOID"
        assert "L1_THEORY" in result.reason
        assert "amendment-only" in result.reason


class TestFAGWriteValidatePatch:
    """Test Rules 4-6: Read Before Write, Patch Only, Rewrite Threshold."""
    
    def test_patch_no_read_proof(self, temp_workspace: Path):
        """Patch without read_proof -> HOLD."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="patch",
            justification="Fix bug",
            diff="--- a/existing_file.py\n+++ b/existing_file.py\n- old\n+ new",
            # No read_sha256 or read_bytes provided
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "HOLD"
        assert "Read Before Write" in result.reason
    
    def test_patch_no_diff(self, temp_workspace: Path):
        """Patch without unified diff -> HOLD."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        # Get read proof for existing file
        test_file = temp_workspace / "existing_file.py"
        content = test_file.read_bytes()
        
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="patch",
            justification="Fix bug",
            # No diff provided
            read_sha256=hashlib.sha256(content).hexdigest(),
            read_bytes=len(content),
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "HOLD"
        assert "Patch Only" in result.reason
    
    def test_patch_over_threshold(self, temp_workspace: Path):
        """Patch with >30% deletion ratio -> HOLD."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        # Get read proof for existing file
        test_file = temp_workspace / "existing_file.py"
        content = test_file.read_bytes()
        
        # Diff that deletes 4 of 5 lines (80% deletion)
        big_diff = """--- a/existing_file.py
+++ b/existing_file.py
 line 1
-line 2
-line 3
-line 4
-line 5
+new line
"""
        
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="patch",
            justification="Major refactor",
            diff=big_diff,
            read_sha256=hashlib.sha256(content).hexdigest(),
            read_bytes=len(content),
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "HOLD"
        assert "Rewrite Threshold" in result.reason
        assert "30%" in result.reason
    
    def test_patch_within_threshold(self, temp_workspace: Path):
        """Patch with <30% deletion ratio -> SEAL."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        # Get read proof for existing file
        test_file = temp_workspace / "existing_file.py"
        content = test_file.read_bytes()
        
        # Diff that changes 1 of 5 lines (20% deletion)
        small_diff = """--- a/existing_file.py
+++ b/existing_file.py
 line 1
-line 2
+line 2 modified
 line 3
 line 4
 line 5
"""
        
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="patch",
            justification="Small fix",
            diff=small_diff,
            read_sha256=hashlib.sha256(content).hexdigest(),
            read_bytes=len(content),
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "SEAL"


class TestFAGWriteValidateDelete:
    """Test Rule 3: Delete Gate."""
    
    def test_delete_default_hold(self, temp_workspace: Path):
        """Delete operation -> HOLD (human gate)."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="delete",
            justification="Remove obsolete file",
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "HOLD"
        assert "Delete Gate" in result.reason


class TestFAGWriteValidateIntegration:
    """Integration tests for write_validate."""
    
    def test_full_valid_patch_flow(self, temp_workspace: Path):
        """Complete valid patch workflow: read -> compute proof -> validate."""
        fag = FAG(root=str(temp_workspace), enable_ledger=False)
        
        # Step 1: Read file (simulating FAG.read())
        test_file = temp_workspace / "existing_file.py"
        content = test_file.read_bytes()
        
        # Step 2: Compute read proof
        read_sha256 = hashlib.sha256(content).hexdigest()
        read_bytes = len(content)
        
        # Step 3: Prepare minimal patch
        patch_diff = """--- a/existing_file.py
+++ b/existing_file.py
 line 1
 line 2
 line 3
 line 4
-line 5
+line 5 updated
"""
        
        # Step 4: Validate
        plan = FAGWritePlan(
            target_path="existing_file.py",
            operation="patch",
            justification="Update last line",
            diff=patch_diff,
            read_sha256=read_sha256,
            read_bytes=read_bytes,
        )
        
        result = fag.write_validate(plan)
        
        assert result.verdict == "SEAL"
        assert "All FAG Write Contract rules passed" in result.reason
