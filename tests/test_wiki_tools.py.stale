"""tests/test_wiki_tools.py — arifOS Wiki Tools forge smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).parents[1].resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "core") not in sys.path:
    sys.path.insert(0, str(root_dir / "core"))

import pytest

from arifos_wiki_tools.indexer import ingest_repo
from arifos_wiki_tools.search import search_index
from arifos_wiki_tools.synthesis import ask_repo, map_repo


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    """Create a minimal Python repo for testing."""
    repo = tmp_path / "mini_repo"
    repo.mkdir()

    # Python module with a function and class
    (repo / "gateway.py").write_text(
        "# AAA gateway entrypoint.\n"
        "\n"
        "\n"
        "class AuthGateway:\n"
        '    """Authenticate requests via token validation."""\n'
        "\n"
        "    def authenticate(self, token: str) -> bool:\n"
        '        """Return True if token is valid."""\n'
        '        return token == "ok"\n'
        "\n"
        "    def revoke(self, token: str) -> None:\n"
        '        """Revoke a token."""\n'
        "        pass\n"
        "\n"
        "\n"
        "def health_check() -> bool:\n"
        '    """Return True if gateway is healthy."""\n'
        "    return True\n",
        encoding="utf-8",
    )

    # Markdown README
    (repo / "README.md").write_text(
        "# Mini Repo\n"
        "\n"
        "Authentication is handled by `AuthGateway` in `gateway.py`.\n"
        "\n"
        "## Usage\n"
        "\n"
        "```python\n"
        "from gateway import AuthGateway\n"
        "\n"
        "gw = AuthGateway()\n"
        "assert gw.authenticate('ok') is True\n"
        "```\n",
        encoding="utf-8",
    )

    # YAML config
    (repo / "config.yaml").write_text(
        "gateway:\n  host: 0.0.0.0\n  port: 8080\n  auth:\n    token_ttl: 3600\n",
        encoding="utf-8",
    )

    return repo


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestIndexer:
    def test_ingest_mini_repo(self, mini_repo: Path):
        """ingest_repo produces manifest with expected keys."""
        manifest = ingest_repo(mini_repo, scope_name="TEST", write_wiki=True)

        assert manifest["scope_name"] == "TEST"
        assert manifest["files_indexed"] == 3
        assert manifest["chunks_indexed"] >= 3
        assert "python" in manifest["languages"]
        assert "markdown" in manifest["languages"]
        assert manifest["files_indexed"] >= 3

        # Artifacts written
        assert (mini_repo / ".arifos" / "wiki_index.jsonl").exists()
        assert (mini_repo / ".arifos" / "wiki_files.jsonl").exists()
        assert (mini_repo / ".arifos" / "wiki_manifest.json").exists()
        assert (mini_repo / "wiki" / "generated" / "index.md").exists()
        assert (mini_repo / "wiki" / "generated" / "overview.md").exists()

    def test_ingest_excludes_binary_and_large(self, tmp_path: Path):
        """Binary files and files >1MB are skipped."""
        repo = tmp_path / "filter_test"
        repo.mkdir()

        # Binary file (starts with null bytes)
        (repo / "binary.bin").write_bytes(b"\x00\x00\x00binary")
        # Large file (>1MB, should be skipped)
        large = repo / "large.py"
        large.write_text("x" * 1_001_000, encoding="utf-8")

        manifest = ingest_repo(repo, write_wiki=False)
        assert manifest["files_indexed"] == 0

    def test_ingest_no_write_wiki(self, mini_repo: Path):
        """write_wiki=False skips wiki generation."""
        manifest = ingest_repo(mini_repo, write_wiki=False)
        assert "generated_wiki_path" not in manifest
        assert not (mini_repo / "wiki" / "generated").exists()

    def test_ingest_respects_gitignore(self, tmp_path: Path):
        """Files matching .gitignore patterns are skipped."""
        repo = tmp_path / "gitignore_repo"
        repo.mkdir()

        # Write .gitignore
        (repo / ".gitignore").write_text("ignored.py\n*.tmp\n/anchored.py\n", encoding="utf-8")

        # Write some files
        (repo / "normal.py").write_text("print('normal')", encoding="utf-8")
        (repo / "ignored.py").write_text("print('ignored')", encoding="utf-8")
        (repo / "nested").mkdir()
        (repo / "nested" / "ignored.py").write_text("print('nested ignored')", encoding="utf-8")
        (repo / "test.tmp").write_text("temp", encoding="utf-8")
        (repo / "anchored.py").write_text("print('anchored')", encoding="utf-8")
        (repo / "nested" / "anchored.py").write_text(
            "print('not anchored at root')", encoding="utf-8"
        )

        manifest = ingest_repo(repo, write_wiki=False)

        # Files indexed should not include ignored files
        assert (
            manifest["files_indexed"] == 2
        )  # normal.py and nested/anchored.py (anchored.py is ignored only at root)

        # Check that normal.py and nested/anchored.py are indexed, others are not
        hits = search_index(repo, "print", top_k=10)
        indexed_files = {h["rel_path"] for h in hits}
        assert "normal.py" in indexed_files
        assert "nested/anchored.py" in indexed_files
        assert "ignored.py" not in indexed_files
        assert "nested/ignored.py" not in indexed_files
        assert "test.tmp" not in indexed_files
        assert "anchored.py" not in indexed_files


class TestSearch:
    def test_search_authenticate(self, mini_repo: Path):
        """Search for 'authenticate' returns relevant chunks."""
        ingest_repo(mini_repo, write_wiki=False)

        hits = search_index(mini_repo, "authenticate", top_k=5)
        assert len(hits) >= 1
        assert any("gateway.py" in h["rel_path"] for h in hits)

    def test_search_with_symbol_bonus(self, mini_repo: Path):
        """Path and symbol hits score higher than body-only hits."""
        ingest_repo(mini_repo, write_wiki=False)

        # Search by class name (should get symbol bonus)
        hits = search_index(mini_repo, "AuthGateway", top_k=5)
        assert len(hits) >= 1
        # The symbol-extracted chunks should score well
        scores = [h["score"] for h in hits if "gateway.py" in h["rel_path"]]
        assert max(scores) > 0

    def test_search_returns_excerpt(self, mini_repo: Path):
        """Each hit includes an excerpt string."""
        ingest_repo(mini_repo, write_wiki=False)
        hits = search_index(mini_repo, "authenticate", top_k=3)
        for h in hits:
            assert "excerpt" in h
            assert len(h["excerpt"]) > 0
            assert "chunk_id" in h
            assert "start_line" in h
            assert "end_line" in h

    def test_search_empty_query(self, mini_repo: Path):
        """Empty query returns empty list."""
        ingest_repo(mini_repo, write_wiki=False)
        hits = search_index(mini_repo, "", top_k=5)
        assert hits == []


class TestSynthesis:
    def test_map_repo_structure(self, mini_repo: Path):
        """map_repo returns tree, languages, and symbol_inventory."""
        ingest_repo(mini_repo, write_wiki=False)

        result = map_repo(mini_repo, max_depth=3)
        assert result["files_indexed"] == 3
        assert "python" in result["languages"]
        assert "markdown" in result["languages"]
        assert "tree" in result
        assert "symbol_inventory" in result
        # gateway.py has symbols
        symbol_files = [s["rel_path"] for s in result["symbol_inventory"]]
        assert any("gateway.py" in p for p in symbol_files)

    def test_ask_with_evidence(self, mini_repo: Path):
        """ask_repo returns evidence-grounded answer."""
        ingest_repo(mini_repo, write_wiki=False)

        answer = ask_repo(mini_repo, "Where is authentication handled?")
        assert answer["confidence"] in ("low", "medium")
        assert len(answer["evidence"]) >= 1
        assert any("gateway.py" in str(e) for e in answer["evidence"])
        assert "warnings" in answer
        # v0 warnings should mention lexical retrieval
        assert any("lexical" in w.lower() for w in answer["warnings"])

    def test_ask_no_evidence(self, tmp_path: Path):
        """ask_repo with no matches returns low-confidence failure message."""
        # Empty repo
        empty = tmp_path / "empty"
        empty.mkdir()
        (empty / "README.md").write_text("nothing useful here", encoding="utf-8")
        ingest_repo(empty, write_wiki=False)

        answer = ask_repo(empty, "zzzzz_not_found_zzzzz")
        assert answer["confidence"] == "low"
        assert answer["evidence"] == []
        assert "warnings" in answer


class TestCLIPipeline:
    def test_full_cli_pipeline(self, mini_repo: Path, tmp_path: Path):
        """Simulate the full ingest → search → ask pipeline."""
        # 1. Ingest
        manifest = ingest_repo(mini_repo, scope_name="CLI_TEST", write_wiki=True)
        assert manifest["files_indexed"] == 3

        # 2. Search
        hits = search_index(mini_repo, "revoke token", top_k=3)
        assert len(hits) >= 1

        # 3. Map
        result = map_repo(mini_repo)
        assert result["files_indexed"] == 3

        # 4. Ask
        answer = ask_repo(mini_repo, "what does health_check do?")
        assert "evidence" in answer
        assert answer["confidence"] in ("low", "medium")
