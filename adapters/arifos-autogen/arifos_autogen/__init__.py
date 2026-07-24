"""arifOS adapter for autogen — constitutional execution gate."""


class ArifOSGuard:
    def __init__(self, endpoint="https://mcp.arif-fazil.com/mcp"):
        self.endpoint = endpoint

    def protect(self, require_identity=True, reversibility="full"):
        def decorator(func):
            func._arifos_guard = {
                "require_identity": require_identity,
                "reversibility": reversibility,
            }
            return func

        return decorator
