import json
from pathlib import Path

from app.models.machine import TuringMachineConfig

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"


class PresetLoader:
    """Lee las máquinas desde JSON en app/presets/."""

    _cache: dict[str, TuringMachineConfig] | None = None

    @classmethod
    def clear_cache(cls) -> None:
        """Vacía la caché (útil en tests)."""
        cls._cache = None

    @classmethod
    def _load_all(cls) -> dict[str, TuringMachineConfig]:
        """Carga todos los JSON de presets una sola vez."""
        if cls._cache is not None:
            return cls._cache
        machines: dict[str, TuringMachineConfig] = {}
        for path in sorted(PRESETS_DIR.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            config = TuringMachineConfig.model_validate(data)
            machine_id = config.id or path.stem
            config.id = machine_id
            machines[machine_id] = config
        cls._cache = machines
        return machines

    @classmethod
    def list_summaries(cls) -> list[dict]:
        """Lista id, nombre y descripción para el selector del frontend."""
        return [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "examples": [e.model_dump() for e in m.examples],
            }
            for m in cls._load_all().values()
        ]

    @classmethod
    def get(cls, machine_id: str) -> TuringMachineConfig | None:
        """Devuelve la definición completa de una máquina preset."""
        return cls._load_all().get(machine_id)
