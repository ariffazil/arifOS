import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router

app = FastAPI(
    title="arifOS HTTPS MCP Gateway",
    description="Constitutional Gateway fronting Composio Tool Execution",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://mcp.arif-fazil.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint returning constitutional status."""
    return {
        "status": "SEAL",
        "service": "arifos-gateway",
        "version": "v50.0.0",
        "governance": os.getenv("GOVERNANCE_MODE", "HARD")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
