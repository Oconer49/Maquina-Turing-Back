from app.core.turing_engine import SimulationStatus
from app.services.preset_loader import PresetLoader


def test_even_zeros_accepts_empty(engine_factory):
    engine = engine_factory("even_zeros", "")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.ACCEPTED


def test_even_zeros_accepts_0000(engine_factory):
    engine = engine_factory("even_zeros", "0000")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.ACCEPTED


def test_even_zeros_rejects_0001(engine_factory):
    engine = engine_factory("even_zeros", "0001")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.REJECTED
    assert final.result_message is not None
    assert "impar" in final.result_message


def test_even_zeros_rejects_101010_message(engine_factory):
    engine = engine_factory("even_zeros", "101010")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.REJECTED
    assert "3" in final.result_message
    assert "impar" in final.result_message


def test_even_zeros_accepts_1010(engine_factory):
    engine = engine_factory("even_zeros", "1010")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.ACCEPTED


def test_palindrome_accepts_10101(engine_factory):
    engine = engine_factory("binary_palindrome", "10101")
    _, final = engine.run(5000)
    assert final.status == SimulationStatus.ACCEPTED


def test_palindrome_rejects_10100(engine_factory):
    engine = engine_factory("binary_palindrome", "10100")
    _, final = engine.run(5000)
    assert final.status == SimulationStatus.REJECTED


def test_palindrome_accepts_single_0(engine_factory):
    engine = engine_factory("binary_palindrome", "0")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.ACCEPTED


def test_palindrome_materializes_many_symbols_without_duplicate_q4(engine_factory):
    engine = engine_factory("binary_palindrome", "babahfwfdw")
    assert engine.config.initial_state == "q0"
    assert "q5" in engine.config.states
    keys = {(t.from_state, t.read) for t in engine.config.transitions}
    assert len(keys) == len(engine.config.transitions)


def test_anbn_accepts_ab(engine_factory):
    engine = engine_factory("a_power_n_b_power_n", "ab")
    _, final = engine.run(5000)
    assert final.status == SimulationStatus.ACCEPTED


def test_anbn_accepts_aabb(engine_factory):
    engine = engine_factory("a_power_n_b_power_n", "aabb")
    _, final = engine.run(5000)
    assert final.status == SimulationStatus.ACCEPTED


def test_anbn_rejects_abb(engine_factory):
    engine = engine_factory("a_power_n_b_power_n", "abb")
    _, final = engine.run(5000)
    assert final.status == SimulationStatus.REJECTED


def test_unary_increment_accepts_111(engine_factory):
    engine = engine_factory("unary_increment", "111")
    _, final = engine.run(500)
    assert final.status == SimulationStatus.ACCEPTED


def test_step_limit_infinite_loop(engine_factory):
    engine = engine_factory("infinite_loop", "a")
    _, final = engine.run(100)
    assert final.status == SimulationStatus.STEP_LIMIT
