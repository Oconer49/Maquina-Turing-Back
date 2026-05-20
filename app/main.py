import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.simulation import router as simulation_router
from app.config import CORS_ORIGIN_REGEX, CORS_ORIGINS

app = FastAPI(
    title="Simulador de Máquinas de Turing",
    description="API REST para simulación educativa de máquinas de Turing deterministas",
    version="1.0.0",
)

_cors_allow_all = os.getenv("CORS_ALLOW_ALL", "1").lower() in ("1", "true", "yes")

if _cors_allow_all:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_origin_regex=CORS_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(simulation_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"message": "Simulador de Máquinas de Turing API", "docs": "/docs"}
