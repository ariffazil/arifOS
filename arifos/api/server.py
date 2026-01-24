import warnings
import uvicorn
from arifos.core.integration.api import app as core_app, create_app as core_create_app

warnings.warn(
    "arifos.api.server is deprecated. Use arifos.core.integration.api.app instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Backward-compatibility aliases to the canonical API app
app = core_app
create_app = core_create_app

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the Uvicorn server (deprecated path)."""
    uvicorn.run("arifos.core.integration.api.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    run_server()
