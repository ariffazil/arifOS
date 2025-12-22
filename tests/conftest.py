import os
import pytest

@pytest.fixture(scope="function", autouse=True)
def disable_physics_globally():
    """
    Globally disable TEARFRAME Physics logic for all tests by default.
    Tests that need physics (e.g. test_session_physics.py) must explicitly
    enable it by removing this env var in their setup.
    Function scope ensures it is reset even if a test misbehaves.
    """
    # Force disable
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    
    yield
    
    # Reset to disabled for safety
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
