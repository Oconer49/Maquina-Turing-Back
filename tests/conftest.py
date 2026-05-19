import pytest

from app.core.turing_engine import TuringEngine
from app.core.validator import MachineValidator
from app.models.machine import TuringMachineConfig
from app.services.preset_loader import PresetLoader


@pytest.fixture
def engine_factory():
    PresetLoader.clear_cache()

    def _factory(machine_id: str, input_string: str) -> TuringEngine:
        config = PresetLoader.get(machine_id)
        assert config is not None
        MachineValidator.validate_machine(config)
        MachineValidator.validate_input(config, input_string)
        return TuringEngine(config, input_string, machine_id=machine_id)

    return _factory
