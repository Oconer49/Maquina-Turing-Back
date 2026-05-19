from fastapi import APIRouter, HTTPException

from app.config import HISTORY_LIMIT, MAX_STEPS_DEFAULT
from app.core.turing_engine import SimulationStatus, TuringEngine
from app.core.validator import MachineValidator, ValidationError
from app.models.machine import TuringMachineConfig
from app.models.simulation import (
    CreateSimulationRequest,
    MachineSummary,
    RunRequest,
    RunResult,
    SimulationSnapshot,
)
from app.services.preset_loader import PresetLoader
from app.services.simulation_store import simulation_store

router = APIRouter()


def _resolve_machine(body: CreateSimulationRequest) -> tuple[TuringMachineConfig, str]:
    """Busca la máquina preset por machine_id."""
    if not body.machine_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar machine_id")
    config = PresetLoader.get(body.machine_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return config, body.machine_id


def _get_engine_or_404(simulation_id: str) -> TuringEngine:
    """Recupera el motor de la sesión o responde 404."""
    engine = simulation_store.get(simulation_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return engine


def _ensure_running(engine: TuringEngine) -> None:
    """Impide step/run si la simulación ya terminó."""
    if engine.status != SimulationStatus.RUNNING:
        raise HTTPException(status_code=409, detail="La simulación ya finalizó")


@router.get("/health")
def health() -> dict:
    """Comprueba que la API está viva."""
    return {"status": "ok"}


@router.get("/machines", response_model=list[MachineSummary])
def list_machines() -> list[MachineSummary]:
    """GET /machines — listado de presets."""
    return [MachineSummary(**m) for m in PresetLoader.list_summaries()]


@router.get("/machines/{machine_id}", response_model=TuringMachineConfig)
def get_machine(machine_id: str) -> TuringMachineConfig:
    """GET /machines/{id} — definición completa con δ."""
    config = PresetLoader.get(machine_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return config


@router.post("/simulations", response_model=SimulationSnapshot, status_code=201)
def create_simulation(body: CreateSimulationRequest) -> SimulationSnapshot:
    """POST /simulations — crea sesión y devuelve snapshot inicial."""
    try:
        config, machine_id = _resolve_machine(body)
        MachineValidator.validate_machine(config)
        MachineValidator.validate_input(config, body.input)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    max_steps = body.max_steps or MAX_STEPS_DEFAULT
    engine = TuringEngine(config, body.input, machine_id=machine_id)
    simulation_id = simulation_store.create(engine)
    snap = engine.snapshot(simulation_id=simulation_id)
    snap.machine_id = machine_id
    return snap


@router.get("/simulations/{simulation_id}", response_model=SimulationSnapshot)
def get_simulation(simulation_id: str) -> SimulationSnapshot:
    engine = _get_engine_or_404(simulation_id)
    return engine.snapshot(simulation_id=simulation_id)


@router.post("/simulations/{simulation_id}/step", response_model=SimulationSnapshot)
def simulation_step(simulation_id: str) -> SimulationSnapshot:
    """POST .../step — avanza un paso."""
    engine = _get_engine_or_404(simulation_id)
    _ensure_running(engine)
    snap = engine.step()
    snap.simulation_id = simulation_id
    return snap


@router.post("/simulations/{simulation_id}/run", response_model=RunResult)
def simulation_run(simulation_id: str, body: RunRequest | None = None) -> RunResult:
    engine = _get_engine_or_404(simulation_id)
    _ensure_running(engine)
    max_steps = (body.max_steps if body and body.max_steps else MAX_STEPS_DEFAULT)
    history, final = engine.run(max_steps)
    if len(history) > HISTORY_LIMIT:
        history = history[-HISTORY_LIMIT:]
    for snap in history:
        snap.simulation_id = simulation_id
    final.simulation_id = simulation_id
    return RunResult(
        steps=history,
        final_status=final.status,
        total_steps=final.step,
        final_snapshot=final,
    )


@router.delete("/simulations/{simulation_id}", status_code=204)
def delete_simulation(simulation_id: str) -> None:
    if not simulation_store.delete(simulation_id):
        raise HTTPException(status_code=404, detail="Simulación no encontrada")


@router.post("/simulations/{simulation_id}/reset", response_model=SimulationSnapshot)
def reset_simulation(simulation_id: str) -> SimulationSnapshot:
    """POST .../reset — reinicia la misma sesión."""
    engine = _get_engine_or_404(simulation_id)
    snap = engine.reset()
    snap.simulation_id = simulation_id
    return snap

