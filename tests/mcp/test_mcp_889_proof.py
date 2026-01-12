"""Tests for MCP Tool 889: PROOF - Cryptographic Proof Generation"""
import pytest
from arifos_core.mcp.tools.mcp_889_proof import (
    mcp_889_proof,
    mcp_889_proof_sync,
    generate_proof_hash,
    build_merkle_tree,
    generate_merkle_path,
    validate_merkle_proof
)


# =============================================================================
# BASIC FUNCTIONALITY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_proof_always_pass():
    """Test: Tool 889 verdict is always PASS."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS"],
        "decision_tree": {},
        "claim": "Test response"
    })

    assert result.verdict == "PASS"


@pytest.mark.asyncio
async def test_proof_deterministic():
    """Test: Same input produces same proof hash."""
    request = {
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS"],
        "decision_tree": {},
        "claim": "Test"
    }

    result1 = await mcp_889_proof(request)
    result2 = await mcp_889_proof(request)

    assert result1.side_data["proof_hash"] == result2.side_data["proof_hash"]


def test_proof_merkle_tree_build():
    """Test: Merkle tree construction is correct."""
    nodes = ["hash1", "hash2", "hash3", "hash4"]
    tree = build_merkle_tree(nodes)

    # Should have 3 levels: [4 nodes] -> [2 nodes] -> [1 root]
    assert len(tree) == 3
    assert len(tree[0]) == 4  # Leaf level
    assert len(tree[1]) == 2  # Middle level
    assert len(tree[2]) == 1  # Root level


def test_proof_merkle_tree_odd_nodes():
    """Test: Merkle tree handles odd number of nodes."""
    nodes = ["hash1", "hash2", "hash3"]
    tree = build_merkle_tree(nodes)

    # Should duplicate last node
    assert len(tree) == 3
    assert len(tree[0]) == 3  # Leaf level
    assert len(tree[1]) == 2  # Middle level (hash3 duplicated)
    assert len(tree[2]) == 1  # Root level


def test_proof_merkle_path_generation():
    """Test: Merkle path from leaf to root is correct."""
    nodes = ["hash1", "hash2", "hash3", "hash4"]
    tree = build_merkle_tree(nodes)

    path = generate_merkle_path(tree, leaf_index=0)

    # Path should have 2 elements (for tree depth 3)
    assert len(path) == 2


def test_proof_validation():
    """Test: Merkle proof validates correctly."""
    import hashlib

    # Create simple chain
    verdict_chain = ["222:PASS", "444:PASS"]
    hashed_nodes = [hashlib.sha256(v.encode('utf-8')).hexdigest() for v in verdict_chain]

    # Build tree
    tree = build_merkle_tree(hashed_nodes)
    root = tree[-1][0]

    # Generate path from first leaf
    path = generate_merkle_path(tree, leaf_index=0)

    # Validate
    is_valid = validate_merkle_proof(hashed_nodes[0], path, root)

    assert is_valid is True


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_proof_empty_verdict_chain():
    """Test: Handles empty verdict chain gracefully."""
    result = await mcp_889_proof({
        "verdict_chain": [],
        "decision_tree": {},
        "claim": ""
    })

    assert result.verdict == "PASS"
    assert result.side_data["nodes_verified"] == 0
    assert result.side_data["proof_valid"] is True


@pytest.mark.asyncio
async def test_proof_missing_decision_tree():
    """Test: Defaults to empty dict when decision_tree missing."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS"],
        "claim": "Test"
    })

    assert result.verdict == "PASS"
    assert "proof_hash" in result.side_data


@pytest.mark.asyncio
async def test_proof_invalid_verdict_chain():
    """Test: Converts non-list verdict_chain gracefully."""
    result = await mcp_889_proof({
        "verdict_chain": "not a list",
        "decision_tree": {},
        "claim": "Test"
    })

    assert result.verdict == "PASS"
    assert result.side_data["nodes_verified"] == 0


@pytest.mark.asyncio
async def test_proof_nodes_verified_count():
    """Test: Counts nodes verified correctly."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS", "666:PASS", "777:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    assert result.side_data["nodes_verified"] == 5


# =============================================================================
# CONSTITUTIONAL COMPLIANCE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_proof_includes_timestamp():
    """Test: Response includes valid ISO8601 timestamp (F4 ΔS)."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    assert result.timestamp is not None
    assert "T" in result.timestamp  # ISO format


def test_proof_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_889_proof_sync({
        "verdict_chain": ["222:PASS", "444:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    assert result.verdict == "PASS"


@pytest.mark.asyncio
async def test_proof_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict
    assert "proof_hash" in result_dict["side_data"]


# =============================================================================
# ADDITIONAL COMPREHENSIVE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_proof_hash_length():
    """Test: Proof hash is 64 characters (SHA-256 hex)."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    assert len(result.side_data["proof_hash"]) == 64


def test_proof_empty_tree():
    """Test: Empty tree handled gracefully."""
    tree = build_merkle_tree([])
    assert tree == []


def test_proof_single_node_tree():
    """Test: Single node tree (root only)."""
    tree = build_merkle_tree(["hash1"])

    # Should have 1 level (single root)
    assert len(tree) == 1
    assert len(tree[0]) == 1


@pytest.mark.asyncio
async def test_proof_merkle_path_included():
    """Test: Merkle path is included in response."""
    result = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    assert "merkle_path" in result.side_data
    assert isinstance(result.side_data["merkle_path"], list)


def test_validate_merkle_proof_empty_path():
    """Test: Validation with empty path (leaf == root)."""
    leaf = "hash1"
    path = []
    root = "hash1"

    is_valid = validate_merkle_proof(leaf, path, root)
    assert is_valid is True


def test_validate_merkle_proof_invalid():
    """Test: Validation fails with wrong root."""
    leaf = "hash1"
    path = ["hash2"]
    root = "wrong_root"

    is_valid = validate_merkle_proof(leaf, path, root)
    assert is_valid is False
