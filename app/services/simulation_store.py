from uuid import UUID, uuid4

from app.core.turing_engine import TuringEngine


class SimulationStore:
    """Guarda motores de simulación en memoria (una sesión por UUID)."""

    def __init__(self) -> None:
        self._sessions: dict[str, TuringEngine] = {}

    def create(self, engine: TuringEngine) -> str:
        """Registra un motor nuevo y devuelve su simulation_id."""
        simulation_id = str(uuid4())
        self._sessions[simulation_id] = engine
        return simulation_id

    def get(self, simulation_id: str) -> TuringEngine | None:
        """Obtiene el motor de una sesión activa."""
        return self._sessions.get(simulation_id)

    def delete(self, simulation_id: str) -> bool:
        """Elimina una sesión de la memoria."""
        if simulation_id in self._sessions:
            del self._sessions[simulation_id]
            return True
        return False

    def exists(self, simulation_id: str) -> bool:
        return simulation_id in self._sessions


simulation_store = SimulationStore()
