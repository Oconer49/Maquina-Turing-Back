from pydantic import BaseModel, Field

from app.models.machine import Transition, TuringMachineConfig


class TapeCell(BaseModel):
    index: int
    symbol: str


class AppliedTransition(BaseModel):
    from_state: str = Field(alias="from")
    read: str
    to: str
    write: str
    move: str

    model_config = {"populate_by_name": True, "ser_json_by_alias": True}


class SimulationSnapshot(BaseModel):
    simulation_id: str | None = None
    step: int
    current_state: str
    head_index: int
    tape: list[TapeCell]
    status: str
    machine_id: str | None = None
    applied_transition: AppliedTransition | None = None
    result_message: str | None = None


class CreateSimulationRequest(BaseModel):
    machine_id: str
    input: str = ""
    max_steps: int = 10_000


class RunRequest(BaseModel):
    max_steps: int | None = None


class RunResult(BaseModel):
    steps: list[SimulationSnapshot]
    final_status: str
    total_steps: int
    final_snapshot: SimulationSnapshot


class MachineSummary(BaseModel):
    id: str
    name: str
    description: str
