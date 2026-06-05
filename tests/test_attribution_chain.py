"""
EUREKA 2: Attribution Chain — Unconformity Detector Tests

Tests the AttributionChain model's ability to detect missing provenance
layers in VAULT999 seal chains.

Geological framing: An UNCONFORMITY is a missing layer in the stratigraphic
column — evidence that something existed and was erased. In VAULT999,
an UNCONFORMITY is a citation without traceable origin.

Named after Arif's Layang-Layang scar: work existed, truth was correct,
but attribution was erased.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from arifosmcp.schemas.verdict import AttributionChain, AttributionLink


class TestAttributionChain:
    """AttributionChain model — unconformity detection."""

    def test_intact_chain_returns_INTACT(self):
        """An unbroken chain of links with valid hashes = INTACT."""
        links = [
            AttributionLink(
                source_seal_hash="abc123",
                source_agent="geox",
                source_session_id="sess-001",
                citation_type="EVIDENCE",
            ),
            AttributionLink(
                source_seal_hash="def456",
                source_agent="wealth",
                source_session_id="sess-002",
                citation_type="DECISION",
            ),
        ]
        chain = AttributionChain(links=links)
        assert chain.chain_integrity == "INTACT"
        assert chain.unconformity_at is None
        assert chain.unconformity_reason is None

    def test_broken_chain_missing_hash_returns_UNCONFORMITY_DETECTED(self):
        """A link with an empty seal hash = UNCONFORMITY_DETECTED."""
        links = [
            AttributionLink(
                source_seal_hash="abc123",
                source_agent="geox",
                source_session_id="sess-001",
                citation_type="EVIDENCE",
            ),
            AttributionLink(
                source_seal_hash="",  # BROKEN — no hash
                source_agent="wealth",
                source_session_id="sess-002",
                citation_type="DECISION",
            ),
        ]
        chain = AttributionChain(links=links)
        assert chain.chain_integrity == "UNCONFORMITY_DETECTED"
        assert chain.unconformity_at == 1  # broken at link index 1
        assert "Missing seal hash at link 1" in chain.unconformity_reason

    def test_empty_chain_returns_UNVERIFIED(self):
        """No links at all = UNVERIFIED — nothing to verify."""
        chain = AttributionChain(links=[])
        assert chain.chain_integrity == "UNVERIFIED"
        assert chain.unconformity_at is None

    def test_chain_with_all_citation_types(self):
        """All four citation types pass through without breaking."""
        links = [
            AttributionLink(
                source_seal_hash="hash-evid",
                source_agent="geox",
                source_session_id="sess-001",
                citation_type="EVIDENCE",
            ),
            AttributionLink(
                source_seal_hash="hash-decision",
                source_agent="omega-forge-agent",
                source_session_id="sess-002",
                citation_type="DECISION",
            ),
            AttributionLink(
                source_seal_hash="hash-method",
                source_agent="wealth",
                source_session_id="sess-003",
                citation_type="METHOD",
            ),
            AttributionLink(
                source_seal_hash="hash-data",
                source_agent="a-forge",
                source_session_id="sess-004",
                citation_type="DATA",
            ),
        ]
        chain = AttributionChain(links=links)
        assert chain.chain_integrity == "INTACT"
        assert len(chain.links) == 4
        # Verify citation types are preserved
        assert [l.citation_type for l in chain.links] == ["EVIDENCE", "DECISION", "METHOD", "DATA"]

    def test_missing_hash_at_first_link(self):
        """First link missing hash = unconformity at index 0."""
        links = [
            AttributionLink(
                source_seal_hash="",  # BROKEN at position 0
                source_agent="geox",
                source_session_id="sess-001",
                citation_type="DATA",
            ),
            AttributionLink(
                source_seal_hash="def456",
                source_agent="wealth",
                source_session_id="sess-002",
                citation_type="EVIDENCE",
            ),
        ]
        chain = AttributionChain(links=links)
        assert chain.chain_integrity == "UNCONFORMITY_DETECTED"
        assert chain.unconformity_at == 0
        assert "link 0" in chain.unconformity_reason
