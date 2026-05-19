from app.config import TAPE_WINDOW_RADIUS
from app.core.result_explainer import explain_result
from app.core.tape import Tape
from app.models.machine import Transition, TuringMachineConfig
from app.models.simulation import AppliedTransition, SimulationSnapshot, TapeCell


class SimulationStatus:
    RUNNING = "RUNNING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    STEP_LIMIT = "STEP_LIMIT"


class TuringEngine:
    """Motor de simulación: aplica δ paso a paso sobre la cinta."""

    def __init__(self, config: TuringMachineConfig, input_string: str, machine_id: str | None = None):
        self.config = config
        self.machine_id = machine_id or config.id
        self.input_string = input_string
        self.tape = Tape(config.blank, input_string)
        self.current_state = config.initial_state
        self.step_count = 0
        self.status = SimulationStatus.RUNNING
        self.last_transition: Transition | None = None
        self.halt_cause: str | None = None
        self.symbol_at_halt: str | None = None
        self._transition_map: dict[tuple[str, str], Transition] = {}
        for t in config.transitions:
            self._transition_map[(t.from_state, t.read)] = t

    def _resolve_status(self) -> None:
        """Marca ACCEPTED o REJECTED si el estado actual es final."""
        if self.current_state in self.config.accept_states:
            self.status = SimulationStatus.ACCEPTED
            self.halt_cause = "accept_state"
        elif self.current_state in self.config.reject_states:
            self.status = SimulationStatus.REJECTED
            self.halt_cause = "reject_state"

    def snapshot(self, simulation_id: str | None = None) -> SimulationSnapshot:
        """Arma el JSON del paso actual (cinta, estado, mensaje)."""
        applied = None
        if self.last_transition:
            t = self.last_transition
            applied = AppliedTransition.model_validate(
                {
                    "from": t.from_state,
                    "read": t.read,
                    "to": t.to,
                    "write": t.write,
                    "move": t.move,
                }
            )
        result_message = explain_result(
            self.status,
            self.machine_id,
            self.input_string,
            self.current_state,
            self.config.blank,
            self.halt_cause,
            self.symbol_at_halt,
        )
        return SimulationSnapshot(
            simulation_id=simulation_id,
            step=self.step_count,
            current_state=self.current_state,
            head_index=self.tape.head,
            tape=[TapeCell(**c) for c in self.tape.window(TAPE_WINDOW_RADIUS)],
            status=self.status,
            machine_id=self.machine_id,
            applied_transition=applied,
            result_message=result_message,
        )

    def step(self) -> SimulationSnapshot:
        """Ejecuta un paso: lee, aplica δ, escribe y mueve la cabeza."""
        if self.status != SimulationStatus.RUNNING:
            return self.snapshot()

        symbol = self.tape.read()
        key = (self.current_state, symbol)
        transition = self._transition_map.get(key)

        if transition is None:
            self.status = SimulationStatus.REJECTED
            self.halt_cause = "no_transition"
            self.symbol_at_halt = symbol
            self.last_transition = None
            self.step_count += 1
            return self.snapshot()

        self.last_transition = transition
        self.tape.write(transition.write)
        self.current_state = transition.to
        self.tape.move(transition.move)
        self.step_count += 1
        self._resolve_status()

        return self.snapshot()

    def run(self, max_steps: int) -> tuple[list[SimulationSnapshot], SimulationSnapshot]:
        """Repite step hasta parar o alcanzar el límite de pasos."""
        history: list[SimulationSnapshot] = []
        while self.status == SimulationStatus.RUNNING and self.step_count < max_steps:
            snap = self.step()
            history.append(snap)
            if self.status != SimulationStatus.RUNNING:
                break

        if self.status == SimulationStatus.RUNNING and self.step_count >= max_steps:
            self.status = SimulationStatus.STEP_LIMIT
            self.halt_cause = "step_limit"

        final = self.snapshot()
        if not history or history[-1].step != final.step:
            history.append(final)

        return history, final

    def reset(self) -> SimulationSnapshot:
        """Restaura cinta, estado inicial y contador de pasos."""
        self.tape = Tape(self.config.blank, self.input_string)
        self.current_state = self.config.initial_state
        self.step_count = 0
        self.status = SimulationStatus.RUNNING
        self.last_transition = None
        self.halt_cause = None
        self.symbol_at_halt = None
        return self.snapshot()
