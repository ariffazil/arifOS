"""
test_amanah_detector.py — Torture Test Suite for PHOENIX SOVEREIGNTY Phase 1

Tests the Python-sovereign Amanah detection (F1 floor).
Verifies that RED patterns are BLOCKED and ORANGE patterns are WARNED.

Axiom: "AI cannot self-legitimize."
Motto: "DITEMPA BUKAN DIBERI" — Measure, don't ask.

Test Categories:
    1. RED Patterns (BLOCKED → VOID)
        - SQL Destruction
        - Unix Destruction
        - Git Destruction
        - Python Destruction
        - Credential Leaks
        - Database Destruction

    2. ORANGE Patterns (WARNED → 888_HOLD)
        - Privilege Escalation
        - Code Execution
        - Network Risk
        - Git History Modification

    3. SAFE Patterns (PASSED → SEAL)
        - Normal code
        - Documentation
        - Comments mentioning dangerous commands

    4. Edge Cases
        - Mixed patterns
        - Disclosure keywords
        - Code blocks
"""

import pytest
from arifos_core.floor_detectors.amanah_risk_detectors import (
    AmanahDetector,
    AmanahResult,
    RiskLevel,
    AMANAH_DETECTOR,
    check_amanah,
    is_amanah_safe,
)


class TestAmanahDetectorSetup:
    """Test detector initialization and basic functionality."""

    def test_detector_initializes(self):
        """Detector should initialize without errors."""
        detector = AmanahDetector()
        assert detector is not None
        assert detector.strict_mode is True

    def test_singleton_available(self):
        """Global singleton should be available."""
        assert AMANAH_DETECTOR is not None
        assert isinstance(AMANAH_DETECTOR, AmanahDetector)

    def test_result_structure(self):
        """Result should have correct structure."""
        result = check_amanah("print('hello')")
        assert isinstance(result, AmanahResult)
        assert hasattr(result, 'is_safe')
        assert hasattr(result, 'risk_level')
        assert hasattr(result, 'violations')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'matches')

    def test_convenience_functions(self):
        """Convenience functions should work."""
        result = check_amanah("print('hello')")
        assert result.is_safe is True

        is_safe = is_amanah_safe("print('hello')")
        assert is_safe is True


# =============================================================================
# RED PATTERNS — SQL DESTRUCTION
# =============================================================================

class TestRedPatternsSQLDestruction:
    """Test SQL destruction patterns (RED → VOID)."""

    def test_delete_from_blocked(self):
        """DELETE FROM should be blocked."""
        result = check_amanah("DELETE FROM users")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert len(result.violations) > 0
        assert any("DELETE FROM" in v or "sql_delete" in v for v in result.violations)

    def test_delete_from_with_where_blocked(self):
        """DELETE FROM with WHERE should still be blocked."""
        result = check_amanah("DELETE FROM users WHERE id = 1")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_drop_table_blocked(self):
        """DROP TABLE should be blocked."""
        result = check_amanah("DROP TABLE users")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert any("DROP TABLE" in v or "sql_drop_table" in v for v in result.violations)

    def test_drop_table_if_exists_blocked(self):
        """DROP TABLE IF EXISTS should be blocked."""
        result = check_amanah("DROP TABLE IF EXISTS users")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_drop_database_blocked(self):
        """DROP DATABASE should be blocked."""
        result = check_amanah("DROP DATABASE production")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_truncate_blocked(self):
        """TRUNCATE should be blocked."""
        result = check_amanah("TRUNCATE TABLE users")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_truncate_without_table_blocked(self):
        """TRUNCATE without TABLE keyword should be blocked."""
        result = check_amanah("TRUNCATE users")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# RED PATTERNS — UNIX DESTRUCTION
# =============================================================================

class TestRedPatternsUnixDestruction:
    """Test Unix destruction patterns (RED → VOID)."""

    def test_rm_rf_blocked(self):
        """rm -rf should be blocked."""
        result = check_amanah("rm -rf /")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert any("rm" in v.lower() for v in result.violations)

    def test_rm_rf_home_blocked(self):
        """rm -rf ~ should be blocked."""
        result = check_amanah("rm -rf ~")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_rm_rf_path_blocked(self):
        """rm -rf /path/to/dir should be blocked."""
        result = check_amanah("rm -rf /var/log/important")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_rm_fr_blocked(self):
        """rm -fr should be blocked (flag order variant)."""
        result = check_amanah("rm -fr /tmp/test")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_rm_recursive_blocked(self):
        """rm -r should be blocked."""
        result = check_amanah("rm -r /some/directory")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_windows_rmdir_s_blocked(self):
        """rmdir /s should be blocked (Windows)."""
        result = check_amanah("rmdir /s /q C:\\Users\\test")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# RED PATTERNS — GIT DESTRUCTION
# =============================================================================

class TestRedPatternsGitDestruction:
    """Test Git destruction patterns (RED → VOID)."""

    def test_git_push_force_blocked(self):
        """git push --force should be blocked."""
        result = check_amanah("git push --force origin main")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert any("force" in v.lower() or "git" in v.lower() for v in result.violations)

    def test_git_push_f_blocked(self):
        """git push -f should be blocked."""
        result = check_amanah("git push -f origin main")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_git_reset_hard_blocked(self):
        """git reset --hard should be blocked."""
        result = check_amanah("git reset --hard HEAD~3")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_git_reset_hard_origin_blocked(self):
        """git reset --hard origin/main should be blocked."""
        result = check_amanah("git reset --hard origin/main")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_git_clean_f_blocked(self):
        """git clean -f should be blocked."""
        result = check_amanah("git clean -fd")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# RED PATTERNS — PYTHON DESTRUCTION
# =============================================================================

class TestRedPatternsPythonDestruction:
    """Test Python destruction patterns (RED → VOID)."""

    def test_shutil_rmtree_blocked(self):
        """shutil.rmtree should be blocked."""
        result = check_amanah("shutil.rmtree('/var/data')")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert any("rmtree" in v.lower() for v in result.violations)

    def test_os_remove_blocked(self):
        """os.remove should be blocked."""
        result = check_amanah("os.remove('/etc/passwd')")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_os_unlink_blocked(self):
        """os.unlink should be blocked."""
        result = check_amanah("os.unlink(config_file)")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_os_rmdir_blocked(self):
        """os.rmdir should be blocked."""
        result = check_amanah("os.rmdir(temp_dir)")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_pathlib_unlink_blocked(self):
        """Path.unlink() should be blocked."""
        result = check_amanah("path.unlink()")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_pathlib_unlink_missing_ok_blocked(self):
        """Path.unlink(missing_ok=True) should be blocked."""
        result = check_amanah("config_path.unlink(missing_ok=True)")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# RED PATTERNS — CREDENTIAL LEAKS
# =============================================================================

class TestRedPatternsCredentialLeaks:
    """Test credential leak patterns (RED → VOID)."""

    def test_openai_key_blocked(self):
        """OpenAI API key should be blocked."""
        result = check_amanah("api_key = 'sk-1234567890abcdefghijklmnopqrstuvwxyz'")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED
        assert any("openai" in v.lower() or "credential" in v.lower() for v in result.violations)

    def test_aws_secret_blocked(self):
        """AWS secret key should be blocked."""
        result = check_amanah("AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_aws_access_key_id_blocked(self):
        """AWS access key ID should be blocked."""
        result = check_amanah("AKIAIOSFODNN7EXAMPLE")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_github_token_blocked(self):
        """GitHub token should be blocked."""
        result = check_amanah("ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1234")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_private_key_blocked(self):
        """Private key header should be blocked."""
        result = check_amanah("-----BEGIN RSA PRIVATE KEY-----")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# RED PATTERNS — DATABASE DESTRUCTION
# =============================================================================

class TestRedPatternsDatabaseDestruction:
    """Test database destruction patterns (RED → VOID)."""

    def test_mongo_drop_blocked(self):
        """MongoDB drop should be blocked."""
        result = check_amanah("db.users.drop()")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_mongo_drop_database_blocked(self):
        """MongoDB dropDatabase should be blocked."""
        result = check_amanah("db.dropDatabase()")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_redis_flushall_blocked(self):
        """Redis FLUSHALL should be blocked."""
        result = check_amanah("redis.execute_command('FLUSHALL')")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_redis_flushdb_blocked(self):
        """Redis FLUSHDB should be blocked."""
        result = check_amanah("FLUSHDB")
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED


# =============================================================================
# ORANGE PATTERNS — WARNINGS
# =============================================================================

class TestOrangePatterns:
    """Test ORANGE patterns (WARNING → 888_HOLD)."""

    def test_sudo_warned(self):
        """sudo should be warned but not blocked."""
        result = check_amanah("sudo apt-get update")
        assert result.is_safe is True  # ORANGE doesn't block
        assert result.risk_level == RiskLevel.ORANGE
        assert len(result.warnings) > 0
        assert any("sudo" in w.lower() for w in result.warnings)

    def test_chmod_777_warned(self):
        """chmod 777 should be warned."""
        result = check_amanah("chmod 777 /var/www")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE
        assert len(result.warnings) > 0

    def test_eval_warned(self):
        """eval() should be warned."""
        result = check_amanah("result = eval(user_input)")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE
        assert any("eval" in w.lower() for w in result.warnings)

    def test_exec_warned(self):
        """exec() should be warned."""
        result = check_amanah("exec(code_string)")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE

    def test_subprocess_shell_warned(self):
        """subprocess with shell=True should be warned."""
        result = check_amanah("subprocess.run(cmd, shell=True)")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE

    def test_os_system_warned(self):
        """os.system should be warned."""
        result = check_amanah("os.system('ls -la')")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE

    def test_git_rebase_warned(self):
        """git rebase should be warned (but not blocked like --force)."""
        result = check_amanah("git rebase main")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE

    def test_git_amend_warned(self):
        """git commit --amend should be warned."""
        result = check_amanah("git commit --amend -m 'fix'")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.ORANGE


# =============================================================================
# SAFE PATTERNS — PASSED
# =============================================================================

class TestSafePatterns:
    """Test safe patterns that should pass."""

    def test_print_hello_passes(self):
        """Simple print should pass."""
        result = check_amanah("print('hello world')")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN
        assert len(result.violations) == 0
        assert len(result.warnings) == 0

    def test_normal_code_passes(self):
        """Normal Python code should pass."""
        code = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(1, 2)
print(result)
"""
        result = check_amanah(code)
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_select_query_passes(self):
        """SELECT query should pass."""
        result = check_amanah("SELECT * FROM users WHERE id = 1")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_insert_query_passes(self):
        """INSERT query should pass."""
        result = check_amanah("INSERT INTO users (name) VALUES ('test')")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_update_query_passes(self):
        """UPDATE query should pass."""
        result = check_amanah("UPDATE users SET name = 'test' WHERE id = 1")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_git_add_passes(self):
        """git add should pass."""
        result = check_amanah("git add .")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_git_commit_passes(self):
        """git commit should pass."""
        result = check_amanah("git commit -m 'feat: add feature'")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_git_push_passes(self):
        """git push (without force) should pass."""
        result = check_amanah("git push origin main")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_git_pull_passes(self):
        """git pull should pass."""
        result = check_amanah("git pull origin main")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_file_read_passes(self):
        """File read operations should pass."""
        result = check_amanah("with open('file.txt', 'r') as f: content = f.read()")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_file_write_passes(self):
        """File write operations should pass."""
        result = check_amanah("with open('file.txt', 'w') as f: f.write('content')")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_string_passes(self):
        """Empty string should pass."""
        result = check_amanah("")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_whitespace_only_passes(self):
        """Whitespace-only string should pass."""
        result = check_amanah("   \n\t   ")
        assert result.is_safe is True
        assert result.risk_level == RiskLevel.GREEN

    def test_mixed_red_and_orange_red_wins(self):
        """When both RED and ORANGE patterns, RED should determine safety."""
        result = check_amanah("sudo rm -rf /")
        assert result.is_safe is False  # RED overrides ORANGE
        assert result.risk_level == RiskLevel.RED
        assert len(result.violations) > 0
        assert len(result.warnings) > 0

    def test_disclosure_does_not_override_red(self):
        """Disclosure keywords should NOT override RED patterns in strict mode."""
        result = check_amanah("# This is a test: rm -rf /")
        # Even with "test" keyword, strict mode keeps RED as unsafe
        detector = AmanahDetector(strict_mode=True)
        result = detector.check("This is a dry-run test: rm -rf /var")
        assert result.is_safe is False  # Still unsafe in strict mode
        assert result.has_disclosure is True

    def test_case_insensitive_sql(self):
        """SQL patterns should be case-insensitive."""
        result = check_amanah("delete from users")
        assert result.is_safe is False

        result = check_amanah("DELETE FROM users")
        assert result.is_safe is False

        result = check_amanah("Delete From users")
        assert result.is_safe is False

    def test_multiline_detection(self):
        """Patterns should be detected across multiline text."""
        code = """
# Some comment
def dangerous_function():
    import shutil
    shutil.rmtree('/important/data')
"""
        result = check_amanah(code)
        assert result.is_safe is False
        assert result.risk_level == RiskLevel.RED

    def test_line_number_tracking(self):
        """Line numbers should be tracked in matches."""
        code = """line 1
line 2
rm -rf /tmp
line 4"""
        result = check_amanah(code)
        assert result.is_safe is False
        assert len(result.matches) > 0
        # rm -rf is on line 3
        match = result.matches[0]
        assert match.line_number == 3

    def test_multiple_violations_all_captured(self):
        """Multiple violations should all be captured."""
        code = """
DELETE FROM users;
DROP TABLE accounts;
rm -rf /var/log;
shutil.rmtree('/data');
"""
        result = check_amanah(code)
        assert result.is_safe is False
        assert len(result.violations) >= 4

    def test_to_dict_serialization(self):
        """Result should serialize to dict correctly."""
        result = check_amanah("rm -rf /")
        d = result.to_dict()
        assert "is_safe" in d
        assert "risk_level" in d
        assert "violations" in d
        assert "warnings" in d
        assert d["is_safe"] is False
        assert d["risk_level"] == "RED"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests with apex_measurements.py."""

    def test_detector_import_available(self):
        """Detector should be importable from apex_measurements."""
        try:
            from arifos_eval.apex.apex_measurements import AMANAH_DETECTOR_AVAILABLE
            # This test just checks the import works
            assert AMANAH_DETECTOR_AVAILABLE in [True, False]
        except ImportError:
            pytest.skip("apex_measurements not available")

    def test_check_with_context_interface(self):
        """check_with_context interface should work."""
        detector = AmanahDetector()
        is_safe, issues = detector.check_with_context("rm -rf /")
        assert is_safe is False
        assert len(issues) > 0

        is_safe, issues = detector.check_with_context("print('hello')")
        assert is_safe is True
        assert len(issues) == 0


# =============================================================================
# REGRESSION TESTS
# =============================================================================

class TestRegressions:
    """Regression tests for specific bugs or edge cases found."""

    def test_rm_without_rf_not_blocked(self):
        """rm without -r or -f should pass (single file removal is less dangerous)."""
        # Note: We're being strict here - rm with -r or -f is dangerous
        result = check_amanah("rm file.txt")
        # This should actually pass since it's not recursive/force
        # Let me check the pattern...
        # Actually our pattern catches rm -r or rm -f variants
        # Plain "rm file.txt" should pass
        assert result.is_safe is True

    def test_path_unlink_in_context(self):
        """Path.unlink in realistic context should be caught."""
        code = """
from pathlib import Path
config_file = Path('/etc/config.json')
config_file.unlink()
"""
        result = check_amanah(code)
        assert result.is_safe is False

    def test_false_positive_removal(self):
        """String 'remove' in normal context should not trigger."""
        result = check_amanah("Please remove the comment from line 5")
        assert result.is_safe is True

        result = check_amanah("list.remove(item)")
        assert result.is_safe is True

    def test_git_force_in_message(self):
        """'force' in commit message should not trigger."""
        result = check_amanah("git commit -m 'force users to re-login'")
        assert result.is_safe is True


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance tests for the detector."""

    def test_large_input_performance(self):
        """Detector should handle large inputs reasonably."""
        import time
        # Generate a large but safe input
        large_input = "print('hello')\n" * 10000

        start = time.time()
        result = check_amanah(large_input)
        elapsed = time.time() - start

        assert result.is_safe is True
        assert elapsed < 5.0  # Should complete in under 5 seconds

    def test_many_patterns_performance(self):
        """Detector should handle inputs with many pattern matches."""
        # Input with multiple dangerous commands
        dangerous_input = """
rm -rf /
DELETE FROM users;
DROP TABLE accounts;
git push --force
shutil.rmtree('/data')
os.remove('/etc/passwd')
""" * 100

        import time
        start = time.time()
        result = check_amanah(dangerous_input)
        elapsed = time.time() - start

        assert result.is_safe is False
        assert elapsed < 5.0  # Should complete in under 5 seconds
