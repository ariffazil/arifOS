"""
tests/test_vector_adapter.py — basic tests for L3 witness adapter.
"""

from arifos_core.memory.vector_adapter import VectorAdapter, WitnessHit


class DummyBackend:
    def search(self, query: str, top_k: int):
        return [
            ("Example witness", 0.75),
            ("Second item", 0.62),
        ][:top_k]


def test_vector_adapter_retrieves_witness_hits():
    adapter = VectorAdapter(DummyBackend())
    results = adapter.retrieve("test", top_k=1)

    assert len(results) == 1
    assert isinstance(results[0], WitnessHit)
    assert results[0].role == "witness"
    assert results[0].source == "vector_db"
    assert results[0].score == 0.75


def test_vector_adapter_dict_output():
    adapter = VectorAdapter(DummyBackend())
    dicts = adapter.as_dicts("test", top_k=2)

    assert len(dicts) == 2
    assert dicts[0]["role"] == "witness"
    assert "text" in dicts[0]
    assert "score" in dicts[0]