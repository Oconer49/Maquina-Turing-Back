from app.core.result_explainer import explain_result


def test_anbn_ababa_pedagogical_not_technical():
    msg = explain_result(
        "REJECTED",
        "a_power_n_b_power_n",
        "ababa",
        "q3",
        "_",
        halt_cause="no_transition",
        symbol_at_halt="a",
    )
    assert msg is not None
    assert "Por qué no" in msg
    assert "ababa" in msg or "$ababa$" in msg
    assert "mezclar" in msg or "posición" in msg
    assert "No hay transición definida" not in msg


def test_unknown_machine_keeps_technical_no_transition():
    msg = explain_result(
        "REJECTED",
        "custom_machine",
        "x",
        "q0",
        "_",
        halt_cause="no_transition",
        symbol_at_halt="x",
    )
    assert msg is not None
    assert "No hay transición definida" in msg
