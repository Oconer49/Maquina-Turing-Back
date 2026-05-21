from pydantic import BaseModel, Field


class MachineExample(BaseModel):
    input: str
    label: str


class Transition(BaseModel):
    from_state: str = Field(alias="from")
    read: str
    to: str
    write: str
    move: str

    model_config = {"populate_by_name": True, "ser_json_by_alias": True}


class TuringMachineConfig(BaseModel):
    id: str | None = None
    name: str
    description: str = ""
    states: list[str]
    input_alphabet: list[str]
    tape_alphabet: list[str]
    blank: str
    initial_state: str
    accept_states: list[str]
    reject_states: list[str] = []
    transitions: list[Transition]
    examples: list[MachineExample] = []

    model_config = {"populate_by_name": True, "ser_json_by_alias": True}
