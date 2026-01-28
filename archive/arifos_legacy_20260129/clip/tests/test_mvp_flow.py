import os
import shutil
from arifos.clip.aclip.cli import _dispatcher000, _dispatcher777, _dispatcher888, _dispatcher999

def cleanup():
    # Remove any existing session artifacts for a clean start
    if os.path.isdir('.arifos_clip'):
        shutil.rmtree('.arifos_clip')

def test_pipeline_hold():
    cleanup()
    # Start a new session with 000 void
    code0 = _dispatcher000.main(["void", "Test", "task"])
    assert code0 == 40  # VOID exit code
    # Session file should be created
    assert os.path.isfile(".arifos_clip/session.json")
    # Forge stage (777)
    code777 = _dispatcher777.main(["forge"])
    assert code777 == 20  # PARTIAL exit code (forged but not sealed)
    assert os.path.isfile(".arifos_clip/forge/forge.json")
    # Apply a hold (888)
    code888 = _dispatcher888.main(["hold", "--reason", "Testing hold"])
    assert code888 == 88  # HOLD exit code
    assert os.path.isdir(".arifos_clip/holds")
    assert os.path.isfile(".arifos_clip/holds/hold.json")
    # Attempt seal without resolving hold (should block)
    code999 = _dispatcher999.main(["seal"])
    assert code999 == 88  # still in HOLD state, cannot seal

def test_seal_requires_authority():
    cleanup()
    _dispatcher000.main(["void", "Another", "task"])
    _dispatcher777.main(["forge"])
    # Try sealing without token
    code_no_token = _dispatcher999.main(["seal", "--apply"])
    assert code_no_token == 30  # SABAR: missing authority token
    # Try sealing with token (arifOS verdict likely HOLD due to no arifOS available)
    code_with_token = _dispatcher999.main(["seal", "--apply", "--authority-token", "TOKEN123"])
    # arifOS is not available in test, so this should result in a HOLD outcome
    assert code_with_token == 88

if __name__ == "__main__":
    test_pipeline_hold()
    test_seal_requires_authority()
    print("All MVP flow tests passed!")
