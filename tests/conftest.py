
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def disable_physics_for_tests():
    """
    Globally disable TEARFRAME Physics during tests.
    
    This prevents 'SABAR' bursts/streaks from triggering during
    rapid-fire test execution, ensuring functional logic is tested
    without kinetic interference.
    """
    # Set the env var
    old_value = os.environ.get("ARIFOS_PHYSICS_DISABLED")
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    
    yield
    
    # Restore (optional, but good hygiene)
    if old_value is None:
        del os.environ["ARIFOS_PHYSICS_DISABLED"]
    else:
        os.environ["ARIFOS_PHYSICS_DISABLED"] = old_value
