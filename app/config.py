import os

MAX_STEPS_DEFAULT = 10_000
TAPE_WINDOW_RADIUS = 12
HISTORY_LIMIT = 500


def _parse_cors_origins() -> list[str]:
    """Lee orígenes permitidos desde CORS_ORIGINS (separados por coma) o usa localhost."""
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://maquina-turing-front.vercel.app",
    ]


CORS_ORIGINS = _parse_cors_origins()

CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")
