import pytest

from app.core.validator import MachineValidator, ValidationError
from app.models.machine import Transition, TuringMachineConfig


def _base_config(**overrides) -> TuringMachineConfig:
    data = {
        "name": "Test",
        "states": ["q0", "q_accept"],
        "input_alphabet": ["0"],
        "tape_alphabet": ["0", "_"],
        "blank": "_",
        "initial_state": "q0",
        "accept_states": ["q_accept"],
        "reject_states": [],
        "transitions": [
            Transition(**{"from": "q0", "read": "0", "to": "q_accept", "write": "0", "move": "R"}),
        ],
    }
    data.update(overrides)
    return TuringMachineConfig(**data)


def test_valid_machine():
    MachineValidator.validate_machine(_base_config())


def test_duplicate_transition():
    config = _base_config(
        transitions=[
            Transition(**{"from": "q0", "read": "0", "to": "q_accept", "write": "0", "move": "R"}),
            Transition(**{"from": "q0", "read": "0", "to": "q0", "write": "0", "move": "L"}),
        ]
    )
    with pytest.raises(ValidationError):
        MachineValidator.validate_machine(config)


def test_invalid_input_symbol():
    config = _base_config()
    with pytest.raises(ValidationError):
        MachineValidator.validate_input(config, "01")
