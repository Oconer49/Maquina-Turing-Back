import os

MAX_STEPS_DEFAULT = 10_000
TAPE_WINDOW_RADIUS = 12
HISTORY_LIMIT = 500


_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://maquina-turing-front.vercel.app",
]


def _parse_cors_origins() -> list[str]:
    """Une orígenes por defecto + CORS_ORIGINS (coma). Siempre incluye Vercel de producción."""
    raw = os.getenv("CORS_ORIGINS", "").strip()
    origins = set(_DEFAULT_ORIGINS)
    if raw:
        for part in raw.split(","):
            o = part.strip().rstrip("/")
            if o:
                origins.add(o)
    return sorted(origins)


CORS_ORIGINS = _parse_cors_origins()

CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"^https://[\w-]+\.vercel\.app$")
