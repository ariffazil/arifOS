
try:
    import fastapi
    print("FastAPI: OK")
    import uvicorn
    print("Uvicorn: OK")
    import prometheus_client
    print("Prometheus: OK")
    from arifos.core.integration.api.app import app
    print("App Import: OK")
except Exception as e:
    print(f"DIAGNOSTIC FAILURE: {str(e)}")
    import traceback
    traceback.print_exc()
