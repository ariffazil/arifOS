"""
tests/core/organs/test_vault_fixed.py — Fixed Vault Tests

Tests for unified_memory vault with CORRECT API
"""

import pytest
from unittest.mock import Mock, patch


class TestVaultFixed:
    """Test unified_memory vault with correct API."""

    @pytest.mark.asyncio
    async def test_vault_store_basic(self):
        """Test basic vault store operation."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="store", session_id="test-vault-001", content="Test content to store"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_search_basic(self):
        """Test basic vault search."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="search", session_id="test-vault-002", content="search query"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_recall_basic(self):
        """Test vault recall."""
        from core.organs.unified_memory import vault

        result = await vault(operation="recall", session_id="test-vault-003")

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_forget_basic(self):
        """Test vault forget."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="forget", session_id="test-vault-004", memory_ids=["memory-001", "memory-002"]
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_seal_basic(self):
        """Test vault seal."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="seal", session_id="test-vault-005", content="Sealing this content"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_default_operation(self):
        """Test vault with default operation (search)."""
        from core.organs.unified_memory import vault

        result = await vault(session_id="test-vault-default")

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_with_top_k(self):
        """Test vault search with top_k parameter."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="search", session_id="test-vault-topk", content="query", top_k=10
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_unicode_content(self):
        """Test vault with unicode content."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="store", session_id="test-vault-unicode", content="Unicode: 你好 🌍 ñ"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_long_content(self):
        """Test vault with long content."""
        from core.organs.unified_memory import vault

        long_content = "Test content " * 100

        result = await vault(operation="store", session_id="test-vault-long", content=long_content)

        assert result is not None

    @pytest.mark.asyncio
    async def test_vault_empty_content_store(self):
        """Test vault store with empty content (should raise error)."""
        from core.organs.unified_memory import vault

        with pytest.raises(ValueError):
            await vault(operation="store", session_id="test-vault-empty", content="")

    @pytest.mark.asyncio
    async def test_vault_with_auth_context(self):
        """Test vault with auth context."""
        from core.organs.unified_memory import vault

        result = await vault(
            operation="store",
            session_id="test-vault-auth",
            content="Authenticated content",
            auth_context={"actor_id": "arif", "authority": "sovereign"},
        )

        assert result is not None


class TestVaultOperations:
    """Test all vault operations."""

    @pytest.mark.asyncio
    async def test_all_operations_exist(self):
        """Verify all vault operations exist."""
        from core.organs.unified_memory import vault

        operations = ["store", "recall", "search", "forget", "seal"]

        for op in operations:
            result = await vault(operation=op, session_id=f"test-{op}", content=f"Test {op}")
            assert result is not None
