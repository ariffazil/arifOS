"""
test_l7_memory.py - L7 Memory Layer Unit Tests for arifOS v38.2-alpha

30 unit tests covering:
- Mem0Client initialization and configuration
- EUREKA Sieve TTL policy
- Memory recall at 111_SENSE
- Memory store at 999_SEAL
- User isolation
- Fail-open behavior

Test Categories:
- test_mem0_client_* (10 tests): Client initialization, config, embed
- test_eureka_sieve_* (8 tests): TTL policy per verdict
- test_recall_* (6 tests): recall_at_stage_111
- test_store_* (6 tests): store_at_stage_999

Author: arifOS Project
Version: v38.2-alpha
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Import L7 Memory components
from arifos.core.memory.l7.mem0_client import (
    Mem0Client,
    Mem0Config,
    MemoryHit,
    EmbedResult,
    SearchResult,
    StoreResult,
    TTLPolicy,
    get_mem0_client,
    is_l7_enabled,
    is_l7_available,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K,
)

from arifos.core.memory.core.memory import (
    Memory,
    RecallResult,
    SieveResult,
    StoreAtSealResult,
    get_memory,
    recall_at_stage_111,
    store_at_stage_999,
    apply_eureka_sieve,
    RECALL_CONFIDENCE_CEILING,
    MAX_RECALL_ENTRIES,
    STORABLE_VERDICTS,
    DISCARD_VERDICTS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_mem0_client():
    """Create a mock Mem0 client for testing."""
    client = Mock(spec=Mem0Client)
    client.is_available = True
    client.initialization_error = None
    client.config = Mem0Config(enabled=True)
    return client


@pytest.fixture
def mock_config():
    """Create a test configuration."""
    return Mem0Config(
        api_key="test-api-key",
        qdrant_host="localhost",
        qdrant_port=6333,
        similarity_threshold=0.65,
        top_k=8,
        enabled=True,
    )


@pytest.fixture
def memory_instance(mock_mem0_client):
    """Create a Memory instance with mock client."""
    return Memory(client=mock_mem0_client)


# =============================================================================
# TEST: MEM0 CLIENT INITIALIZATION (10 tests)
# =============================================================================

class TestMem0ClientInit:
    """Tests for Mem0Client initialization."""

    def test_mem0_client_init_with_config(self, mock_config):
        """Test Mem0Client initialization with explicit config."""
        with patch.object(Mem0Client, '_initialize'):
            client = Mem0Client(config=mock_config)
            assert client.config == mock_config
            assert client.config.enabled is True

    def test_mem0_client_init_from_env(self):
        """Test Mem0Client initialization from environment variables."""
        with patch.dict(os.environ, {
            "ARIFOS_L7_ENABLED": "true",
            "MEM0_API_KEY": "env-api-key",
            "QDRANT_HOST": "env-host",
            "QDRANT_PORT": "7777",
            "ARIFOS_L7_SIMILARITY_THRESHOLD": "0.75",
            "ARIFOS_L7_TOP_K": "10",
        }):
            config = Mem0Config.from_env()
            assert config.enabled is True
            assert config.api_key == "env-api-key"
            assert config.qdrant_host == "env-host"
            assert config.qdrant_port == 7777
            assert config.similarity_threshold == 0.75
            assert config.top_k == 10

    def test_mem0_client_disabled_by_config(self):
        """Test Mem0Client when disabled by configuration."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)
        assert client.is_available is False
        assert client.initialization_error is not None

    def test_mem0_client_disabled_by_env(self):
        """Test Mem0Client when disabled by environment variable."""
        with patch.dict(os.environ, {"ARIFOS_L7_ENABLED": "false"}):
            config = Mem0Config.from_env()
            assert config.enabled is False

    def test_mem0_client_default_config_values(self):
        """Test default configuration values."""
        config = Mem0Config()
        assert config.similarity_threshold == DEFAULT_SIMILARITY_THRESHOLD
        assert config.top_k == DEFAULT_TOP_K
        assert config.qdrant_host == "localhost"
        assert config.qdrant_port == 6333

    def test_mem0_client_is_available_when_initialized(self):
        """Test is_available property when properly initialized."""
        with patch.object(Mem0Client, '_initialize') as mock_init:
            client = Mem0Client(config=Mem0Config(enabled=True))
            # Simulate successful initialization
            client._initialized = True
            client._client = Mock()
            assert client.is_available is True

    def test_mem0_client_not_available_when_not_initialized(self):
        """Test is_available property when not initialized."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)
        assert client.is_available is False

    def test_mem0_client_embed_returns_result(self, mock_config):
        """Test embed method returns EmbedResult with stub fallback."""
        with patch.object(Mem0Client, '_initialize'):
            client = Mem0Client(config=mock_config)
            client._initialized = False
            result = client.embed("test text")
            assert isinstance(result, EmbedResult)
            # Now uses stub fallback, so should succeed
            assert result.success is True
            assert result.model == "stub-hash-384"

    def test_mem0_client_singleton_pattern(self):
        """Test get_mem0_client returns singleton."""
        # Clear singleton
        import arifos.core.memory.mem0_client as m
        m._default_client = None

        with patch.object(Mem0Client, '_initialize'):
            client1 = get_mem0_client()
            client2 = get_mem0_client()
            assert client1 is client2

    def test_is_l7_enabled_function(self):
        """Test is_l7_enabled convenience function."""
        with patch.dict(os.environ, {"ARIFOS_L7_ENABLED": "true"}):
            assert is_l7_enabled() is True

        with patch.dict(os.environ, {"ARIFOS_L7_ENABLED": "false"}):
            assert is_l7_enabled() is False


# =============================================================================
# TEST: EUREKA SIEVE TTL POLICY (8 tests)
# =============================================================================

class TestEurekaSieve:
    """Tests for EUREKA Sieve TTL policy."""

    def test_sieve_seal_verdict_stores_forever(self):
        """Test SEAL verdict stores with TTL=None (forever)."""
        result = apply_eureka_sieve("SEAL")
        assert result.should_store is True
        assert result.ttl_days is None
        assert result.verdict == "SEAL"

    def test_sieve_partial_verdict_stores_730_days(self):
        """Test PARTIAL verdict stores with TTL=730."""
        result = apply_eureka_sieve("PARTIAL")
        assert result.should_store is True
        assert result.ttl_days == 730

    def test_sieve_888_hold_verdict_stores_730_days(self):
        """Test 888_HOLD verdict stores with TTL=730."""
        result = apply_eureka_sieve("888_HOLD")
        assert result.should_store is True
        assert result.ttl_days == 730

    def test_sieve_void_verdict_never_stores(self):
        """Test VOID verdict is never stored (TTL=0)."""
        result = apply_eureka_sieve("VOID")
        assert result.should_store is False
        assert result.ttl_days == 0

    def test_sieve_sabar_verdict_never_stores(self):
        """Test SABAR verdict is never stored (TTL=0)."""
        result = apply_eureka_sieve("SABAR")
        assert result.should_store is False
        assert result.ttl_days == 0

    def test_sieve_flag_verdict_stores_30_days(self):
        """Test FLAG verdict stores with TTL=30."""
        result = apply_eureka_sieve("FLAG")
        assert result.should_store is True
        assert result.ttl_days == 30

    def test_sieve_sunset_verdict_stores_30_days(self):
        """Test SUNSET verdict stores with TTL=30."""
        result = apply_eureka_sieve("SUNSET")
        assert result.should_store is True
        assert result.ttl_days == 30

    def test_sieve_case_insensitive(self):
        """Test sieve is case insensitive."""
        result_lower = apply_eureka_sieve("seal")
        result_upper = apply_eureka_sieve("SEAL")
        result_mixed = apply_eureka_sieve("SeAl")
        assert result_lower.should_store == result_upper.should_store == result_mixed.should_store
        assert result_lower.ttl_days == result_upper.ttl_days == result_mixed.ttl_days


# =============================================================================
# TEST: RECALL AT 111_SENSE (6 tests)
# =============================================================================

class TestRecallAtStage111:
    """Tests for recall_at_stage_111."""

    def test_recall_requires_user_id(self, memory_instance):
        """Test recall fails without user_id."""
        result = memory_instance.recall_at_stage_111(
            query="test query",
            user_id="",  # Empty user_id
        )
        assert result.has_memories is False
        assert result.error is not None
        assert "user_id" in result.error.lower()

    def test_recall_returns_recall_result(self, memory_instance, mock_mem0_client):
        """Test recall returns RecallResult object."""
        mock_mem0_client.search.return_value = SearchResult(hits=[], total_searched=0)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            assert isinstance(result, RecallResult)

    def test_recall_applies_confidence_ceiling(self, memory_instance, mock_mem0_client):
        """Test recall applies confidence ceiling to scores."""
        mock_hit = MemoryHit(
            memory_id="mem-1",
            content="test content",
            metadata={},
            score=0.95,  # Higher than ceiling
            user_id="user-123",
            timestamp="2025-01-01T00:00:00Z",
        )
        mock_mem0_client.search.return_value = SearchResult(hits=[mock_hit], total_searched=1)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            if result.has_memories:
                assert result.memories[0].score <= RECALL_CONFIDENCE_CEILING

    def test_recall_respects_max_entries(self, memory_instance, mock_mem0_client):
        """Test recall respects MAX_RECALL_ENTRIES limit."""
        # Create more hits than MAX_RECALL_ENTRIES
        hits = [
            MemoryHit(
                memory_id=f"mem-{i}",
                content=f"content {i}",
                metadata={},
                score=0.8,
                user_id="user-123",
                timestamp="2025-01-01T00:00:00Z",
            )
            for i in range(MAX_RECALL_ENTRIES + 5)
        ]
        mock_mem0_client.search.return_value = SearchResult(
            hits=hits,
            total_searched=len(hits),
        )

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            assert len(result.memories) <= MAX_RECALL_ENTRIES

    def test_recall_fail_open_when_l7_disabled(self, memory_instance):
        """Test recall returns empty result when L7 disabled (fail-open)."""
        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=False):
            result = memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            assert result.l7_available is False
            assert result.has_memories is False

    def test_recall_context_injection_format(self, memory_instance, mock_mem0_client):
        """Test recall result produces valid context injection."""
        mock_hit = MemoryHit(
            memory_id="mem-1",
            content="test content",
            metadata={},
            score=0.8,
            user_id="user-123",
            timestamp="2025-01-01T00:00:00Z",
        )
        mock_mem0_client.search.return_value = SearchResult(hits=[mock_hit], total_searched=1)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            injection = result.to_context_injection()
            assert "recalled_memories" in injection
            assert "confidence_ceiling" in injection
            assert "caveat" in injection


# =============================================================================
# TEST: STORE AT 999_SEAL (6 tests)
# =============================================================================

class TestStoreAtStage999:
    """Tests for store_at_stage_999."""

    def test_store_requires_user_id(self, memory_instance):
        """Test store fails without user_id."""
        result = memory_instance.store_at_stage_999(
            content="test content",
            user_id="",  # Empty user_id
            verdict="SEAL",
        )
        assert result.success is False
        assert result.error is not None

    def test_store_seal_verdict_succeeds(self, memory_instance, mock_mem0_client):
        """Test storing SEAL verdict succeeds."""
        mock_mem0_client.add.return_value = StoreResult(
            success=True,
            memory_id="new-mem-123",
        )

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.store_at_stage_999(
                content="test content",
                user_id="user-123",
                verdict="SEAL",
            )
            assert result.sieve_result.should_store is True
            assert result.sieve_result.ttl_days is None

    def test_store_void_verdict_blocked(self, memory_instance):
        """Test VOID verdict is blocked by EUREKA Sieve."""
        result = memory_instance.store_at_stage_999(
            content="test content",
            user_id="user-123",
            verdict="VOID",
        )
        assert result.success is False
        assert result.sieve_result.should_store is False
        assert "EUREKA Sieve" in result.error

    def test_store_sabar_verdict_blocked(self, memory_instance):
        """Test SABAR verdict is blocked by EUREKA Sieve."""
        result = memory_instance.store_at_stage_999(
            content="test content",
            user_id="user-123",
            verdict="SABAR",
        )
        assert result.success is False
        assert result.sieve_result.should_store is False

    def test_store_fail_open_when_l7_disabled(self, memory_instance):
        """Test store returns gracefully when L7 disabled (fail-open)."""
        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=False):
            result = memory_instance.store_at_stage_999(
                content="test content",
                user_id="user-123",
                verdict="SEAL",
            )
            assert result.success is False
            assert "disabled" in result.error.lower() or "fail-open" in result.error.lower()

    def test_store_includes_metadata(self, memory_instance, mock_mem0_client):
        """Test store includes provided metadata."""
        mock_mem0_client.add.return_value = StoreResult(
            success=True,
            memory_id="new-mem-123",
        )

        metadata = {"topic": "governance", "context": "test"}

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory_instance.store_at_stage_999(
                content="test content",
                user_id="user-123",
                verdict="SEAL",
                metadata=metadata,
            )
            # Verify add was called with metadata
            mock_mem0_client.add.assert_called_once()
            call_args = mock_mem0_client.add.call_args
            assert call_args[1]["metadata"] == metadata


# =============================================================================
# ADDITIONAL TESTS FOR COVERAGE
# =============================================================================

class TestMemoryHelpers:
    """Tests for Memory helper methods."""

    def test_get_ttl_for_verdict(self, memory_instance):
        """Test get_ttl_for_verdict helper."""
        assert memory_instance.get_ttl_for_verdict("SEAL") is None
        assert memory_instance.get_ttl_for_verdict("PARTIAL") == 730
        assert memory_instance.get_ttl_for_verdict("VOID") == 0

    def test_should_store_verdict(self, memory_instance):
        """Test should_store_verdict helper."""
        assert memory_instance.should_store_verdict("SEAL") is True
        assert memory_instance.should_store_verdict("VOID") is False
        assert memory_instance.should_store_verdict("SABAR") is False

    def test_memory_singleton_pattern(self):
        """Test get_memory returns singleton."""
        import arifos.core.memory.memory as m
        m._default_memory = None

        memory1 = get_memory()
        memory2 = get_memory()
        assert memory1 is memory2

    def test_convenience_functions_exist(self):
        """Test convenience functions are exported."""
        assert callable(recall_at_stage_111)
        assert callable(store_at_stage_999)
        assert callable(apply_eureka_sieve)


class TestTTLPolicyEnum:
    """Tests for TTLPolicy enum."""

    def test_ttl_policy_values(self):
        """Test TTLPolicy enum has correct values."""
        assert TTLPolicy.SEAL.value is None
        assert TTLPolicy.VETO.value == 730
        assert TTLPolicy.FLAG.value == 30
        assert TTLPolicy.VOID.value == 0
        assert TTLPolicy.SABAR.value == 0


class TestDataClasses:
    """Tests for data classes."""

    def test_memory_hit_to_dict(self):
        """Test MemoryHit.to_dict()."""
        hit = MemoryHit(
            memory_id="test-id",
            content="test content",
            metadata={"key": "value"},
            score=0.85,
            user_id="user-123",
            timestamp="2025-01-01T00:00:00Z",
        )
        d = hit.to_dict()
        assert d["memory_id"] == "test-id"
        assert d["content"] == "test content"
        assert d["score"] == 0.85

    def test_recall_result_has_memories(self):
        """Test RecallResult.has_memories property."""
        empty_result = RecallResult()
        assert empty_result.has_memories is False

        with_memory = RecallResult(memories=[
            MemoryHit(
                memory_id="test",
                content="test",
                metadata={},
                score=0.8,
                user_id="user",
                timestamp="2025-01-01T00:00:00Z",
            )
        ])
        assert with_memory.has_memories is True

    def test_sieve_result_from_verdict(self):
        """Test SieveResult.from_verdict class method."""
        result = SieveResult.from_verdict("SEAL")
        assert result.should_store is True
        assert result.verdict == "SEAL"
        assert result.ttl_days is None


# =============================================================================
# TEST: USER ISOLATION
# =============================================================================

class TestUserIsolation:
    """Tests for user isolation in memory operations."""

    def test_search_always_filters_by_user_id(self, memory_instance, mock_mem0_client):
        """Test search always includes user_id filter."""
        mock_mem0_client.search.return_value = SearchResult(hits=[], total_searched=0)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            memory_instance.recall_at_stage_111(
                query="test query",
                user_id="user-123",
            )
            mock_mem0_client.search.assert_called_once()
            call_args = mock_mem0_client.search.call_args
            assert call_args[1]["user_id"] == "user-123"

    def test_add_always_includes_user_id(self, memory_instance, mock_mem0_client):
        """Test add always includes user_id."""
        mock_mem0_client.add.return_value = StoreResult(success=True, memory_id="test")

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            memory_instance.store_at_stage_999(
                content="test content",
                user_id="user-456",
                verdict="SEAL",
            )
            mock_mem0_client.add.assert_called_once()
            call_args = mock_mem0_client.add.call_args
            assert call_args[1]["user_id"] == "user-456"


# =============================================================================
# TEST: EMBED FUNCTIONALITY
# =============================================================================

class TestEmbedFunctionality:
    """Tests for Mem0Client.embed() functionality."""

    def test_embed_returns_result_with_stub(self):
        """Test embed returns result using stub when Mem0 unavailable."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result = client.embed("test text")
        assert isinstance(result, EmbedResult)
        assert result.success is True
        assert result.embedding is not None
        assert len(result.embedding) == 384
        assert result.model == "stub-hash-384"

    def test_embed_empty_text_fails(self):
        """Test embed fails gracefully with empty text."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result = client.embed("")
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_embed_stub_is_deterministic(self):
        """Test stub embedding is deterministic (same text = same embedding)."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result1 = client.embed("test text")
        result2 = client.embed("test text")

        assert result1.embedding == result2.embedding

    def test_embed_stub_differs_for_different_text(self):
        """Test stub embedding differs for different text."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result1 = client.embed("text one")
        result2 = client.embed("text two")

        assert result1.embedding != result2.embedding

    def test_embed_without_stub_fallback(self):
        """Test embed fails when stub fallback disabled and Mem0 unavailable."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result = client.embed("test text", use_stub_fallback=False)
        assert result.success is False

    def test_embed_vector_is_normalized(self):
        """Test stub embedding vector is L2 normalized."""
        config = Mem0Config(enabled=False)
        client = Mem0Client(config=config)

        result = client.embed("test normalization")
        assert result.success is True

        # Check L2 norm is approximately 1.0
        norm = sum(x * x for x in result.embedding) ** 0.5
        assert abs(norm - 1.0) < 0.01


# =============================================================================
# TEST: USER ISOLATION (CRITICAL SECURITY)
# =============================================================================

class TestUserIsolationSecurity:
    """Critical security tests: User A's memories MUST NOT leak to User B."""

    def test_user_a_cannot_see_user_b_memories(self, mock_mem0_client):
        """Test User A's recall cannot access User B's memories."""
        # Setup: User B has memories
        user_b_memories = [
            MemoryHit(
                memory_id="mem-b-1",
                content="User B secret information",
                metadata={"user": "user_b"},
                score=0.9,
                user_id="user_b",
                timestamp="2025-01-01T00:00:00Z",
            )
        ]

        def mock_search(query, user_id, **kwargs):
            # Only return memories for matching user_id
            if user_id == "user_b":
                return SearchResult(hits=user_b_memories, total_searched=1)
            else:
                return SearchResult(hits=[], total_searched=0)

        mock_mem0_client.search.side_effect = mock_search
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            # User A tries to recall
            result_a = memory.recall_at_stage_111(
                query="Show me secrets",
                user_id="user_a",
            )

            # User A should NOT see User B's memories
            assert result_a.has_memories is False

            # User B can see their own memories
            result_b = memory.recall_at_stage_111(
                query="Show me secrets",
                user_id="user_b",
            )
            assert result_b.has_memories is True

    def test_store_always_includes_user_id_metadata(self, mock_mem0_client):
        """Test store operation always includes user_id in metadata."""
        captured_calls = []

        def capture_add(content, user_id, metadata=None, **kwargs):
            captured_calls.append({
                "content": content,
                "user_id": user_id,
                "metadata": metadata,
            })
            return StoreResult(success=True, memory_id="test-id")

        mock_mem0_client.add.side_effect = capture_add
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            memory.store_at_stage_999(
                content="Test content",
                user_id="specific_user_123",
                verdict="SEAL",
            )

        assert len(captured_calls) == 1
        assert captured_calls[0]["user_id"] == "specific_user_123"

    def test_different_users_same_query_different_results(self, mock_mem0_client):
        """Test same query by different users returns different results."""
        user_memories = {
            "alice": [MemoryHit(
                memory_id="alice-1",
                content="Alice's favorite color is blue",
                metadata={}, score=0.8, user_id="alice",
                timestamp="2025-01-01T00:00:00Z",
            )],
            "bob": [MemoryHit(
                memory_id="bob-1",
                content="Bob's favorite color is red",
                metadata={}, score=0.8, user_id="bob",
                timestamp="2025-01-01T00:00:00Z",
            )],
        }

        def mock_search(query, user_id, **kwargs):
            return SearchResult(
                hits=user_memories.get(user_id, []),
                total_searched=len(user_memories.get(user_id, [])),
            )

        mock_mem0_client.search.side_effect = mock_search
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            alice_result = memory.recall_at_stage_111("favorite color", "alice")
            bob_result = memory.recall_at_stage_111("favorite color", "bob")

        assert alice_result.memories[0].content == "Alice's favorite color is blue"
        assert bob_result.memories[0].content == "Bob's favorite color is red"


# =============================================================================
# TEST: ALL 8 VERDICT TYPES (EUREKA SIEVE)
# =============================================================================

class TestAllVerdictTypes:
    """Test EUREKA Sieve behavior for all 8 verdict types."""

    @pytest.mark.parametrize("verdict,expected_store,expected_ttl", [
        ("SEAL", True, None),       # Forever
        ("PARTIAL", True, 730),     # 2 years
        ("888_HOLD", True, 730),    # 2 years
        ("VETO", True, 730),        # 2 years
        ("FLAG", True, 30),         # 30 days
        ("SUNSET", True, 30),       # 30 days
        ("VOID", False, 0),         # Never store
        ("SABAR", False, 0),        # Never store
    ])
    def test_verdict_sieve_policy(self, verdict, expected_store, expected_ttl):
        """Test each verdict type follows EUREKA Sieve TTL policy."""
        result = apply_eureka_sieve(verdict)

        assert result.should_store == expected_store
        assert result.ttl_days == expected_ttl
        assert result.verdict == verdict.upper()

    @pytest.mark.parametrize("verdict", ["SEAL", "PARTIAL", "888_HOLD", "VETO", "FLAG", "SUNSET"])
    def test_storable_verdicts_attempt_storage(self, verdict, mock_mem0_client):
        """Test storable verdicts attempt to call storage."""
        mock_mem0_client.add.return_value = StoreResult(
            success=True,
            memory_id="test-id",
        )
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory.store_at_stage_999(
                content="Test",
                user_id="user",
                verdict=verdict,
            )

        # Should have attempted storage
        assert result.sieve_result.should_store is True
        mock_mem0_client.add.assert_called_once()

    @pytest.mark.parametrize("verdict", ["VOID", "SABAR"])
    def test_discard_verdicts_never_call_storage(self, verdict, mock_mem0_client):
        """Test VOID/SABAR verdicts never call storage backend."""
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory.store_at_stage_999(
                content="Test",
                user_id="user",
                verdict=verdict,
            )

        # Should NOT have called storage
        assert result.sieve_result.should_store is False
        mock_mem0_client.add.assert_not_called()


# =============================================================================
# TEST: EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_query_truncation(self, mock_mem0_client):
        """Test very long queries are handled gracefully."""
        mock_mem0_client.search.return_value = SearchResult(hits=[], total_searched=0)
        memory = Memory(client=mock_mem0_client)

        # 10,000 character query
        long_query = "x" * 10000

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory.recall_at_stage_111(
                query=long_query,
                user_id="user",
            )

        # Should not crash
        assert result is not None

    def test_unicode_content_handling(self, mock_mem0_client):
        """Test unicode content is handled correctly."""
        mock_mem0_client.add.return_value = StoreResult(
            success=True,
            memory_id="unicode-id",
        )
        memory = Memory(client=mock_mem0_client)

        unicode_content = "日本語テスト 🎉 émojis работает"

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory.store_at_stage_999(
                content=unicode_content,
                user_id="user",
                verdict="SEAL",
            )

        assert result.success is True

    def test_special_characters_in_user_id(self, mock_mem0_client):
        """Test special characters in user_id are handled."""
        mock_mem0_client.search.return_value = SearchResult(hits=[], total_searched=0)
        memory = Memory(client=mock_mem0_client)

        special_user_id = "user@domain.com/path#fragment"

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            result = memory.recall_at_stage_111(
                query="test",
                user_id=special_user_id,
            )

        # Should handle special characters
        assert result is not None
        mock_mem0_client.search.assert_called_once()

    def test_empty_metadata_handling(self, mock_mem0_client):
        """Test empty/None metadata is handled."""
        mock_mem0_client.add.return_value = StoreResult(
            success=True,
            memory_id="test-id",
        )
        memory = Memory(client=mock_mem0_client)

        with patch('arifos_core.memory.memory.is_l7_enabled', return_value=True):
            # Test with None metadata
            result = memory.store_at_stage_999(
                content="Test",
                user_id="user",
                verdict="SEAL",
                metadata=None,
            )

        assert result.success is True

    def test_case_insensitive_verdict_handling(self):
        """Test verdicts are case-insensitive."""
        variants = ["seal", "SEAL", "SeAl", "sEaL"]

        for variant in variants:
            result = apply_eureka_sieve(variant)
            assert result.should_store is True
            assert result.verdict == "SEAL"
            assert result.ttl_days is None


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
