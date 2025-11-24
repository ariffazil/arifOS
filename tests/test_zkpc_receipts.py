
import tempfile, shutil
from pathlib import Path

from arifos_core.memory.zkpc import ZKPC

def test_zkpc_generation_and_persistence():
    tmp = tempfile.mkdtemp()
    try:
        const_path = Path(tmp) / "constitution.json"
        const_path.write_text('{}')
        zk = ZKPC(constitution_path=const_path)
        receipt = zk.make_receipt(
            request="Explain governance.",
            metrics={"truth": 0.995, "psi": 1.1, "tri_witness": 0.97},
            floor_pass={"floors_ok": True},
            verdict={"verdict": "SEAL"}
        )
        outpath = str(Path(tmp) / "zkpc.jsonl")
        zk.save_receipt(receipt, path=outpath)
        data = Path(outpath).read_text().strip()
        assert "request_hash" in data
        assert "constitution_hash" in data
    finally:
        shutil.rmtree(tmp)
