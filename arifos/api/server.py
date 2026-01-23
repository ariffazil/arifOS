import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from arifos.api.routes import router as api_router

def create_app() -> FastAPI:
    """
    Create the arifOS Body API application.
    """
    app = FastAPI(
        title="arifOS Body API",
        description="The Voice and Ears of the Constitutional AI System",
        version="v50.5.24",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routes
    app.include_router(api_router, prefix="/v1")

    @app.get("/")
    async def root():
        return {
            "system": "arifOS",
            "motto": "Ditempa Bukan Diberi",
            "status": "SOVEREIGN",
            "docs": "/docs"
        }

    return app

app = create_app()

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the Uvicorn server."""
    uvicorn.run("arifos.api.server:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    run_server()
