from __future__ import annotations

from copy import deepcopy

from app.models.machine import Transition, TuringMachineConfig

RETURN_STATE = "q4"


def _scan_state_name(index: int) -> str:
    """q1, q2, q3, q5, q6… (q4 reservado solo para volver a la izquierda)."""
    n = index + 1
    if n < 4:
        return f"q{n}"
    return f"q{n + 1}"


def _match_state_name(index: int) -> str:
    return f"q3{chr(ord('a') + index)}"


def materialize_machine(config: TuringMachineConfig, machine_id: str, input_string: str) -> TuringMachineConfig:
    """
    Algunas MT se definen como "plantillas" y se materializan según la entrada.

    Caso actual:
    - binary_palindrome: se expande para aceptar palíndromos sobre cualquier Σ
      usando los símbolos presentes en `input_string`.
    """
    if machine_id != "binary_palindrome":
        return config

    sigma = sorted({c for c in input_string if c})
    # Permitir el caso ε (Σ vacía) manteniendo una Σ mínima para validación.
    if not sigma:
        sigma = ["0"]

    blank = config.blank
    marker = "X"
    scan_states = {s: _scan_state_name(i) for i, s in enumerate(sigma)}
    match_states = {s: _match_state_name(i) for i, s in enumerate(sigma)}
    states = (
        ["q0"]
        + [scan_states[s] for s in sigma]
        + [match_states[s] for s in sigma]
        + [RETURN_STATE, "q_accept", "q_reject"]
    )

    tape_alphabet = sorted(set(sigma + [marker, blank]))

    transitions: list[Transition] = []

    # q0: elegir el símbolo más a la izquierda no marcado.
    for s in sigma:
        transitions.append(Transition.model_validate({"from": "q0", "read": s, "to": scan_states[s], "write": marker, "move": "R"}))
    transitions.append(Transition.model_validate({"from": "q0", "read": marker, "to": "q0", "write": marker, "move": "R"}))
    transitions.append(Transition.model_validate({"from": "q0", "read": blank, "to": "q_accept", "write": blank, "move": "R"}))

    # q1, q2, …: ir hasta el blanco al final (un estado por símbolo de Σ).
    for s in sigma:
        scan = scan_states[s]
        for sym in sigma + [marker]:
            transitions.append(Transition.model_validate({"from": scan, "read": sym, "to": scan, "write": sym, "move": "R"}))
        transitions.append(Transition.model_validate({"from": scan, "read": blank, "to": match_states[s], "write": blank, "move": "L"}))

    # q3a, q3b, …: comparar el símbolo del extremo derecho.
    for s in sigma:
        match = match_states[s]
        transitions.append(Transition.model_validate({"from": match, "read": marker, "to": "q0", "write": marker, "move": "R"}))
        transitions.append(Transition.model_validate({"from": match, "read": blank, "to": "q_reject", "write": blank, "move": "R"}))
        for t in sigma:
            to_state = RETURN_STATE if t == s else "q_reject"
            transitions.append(Transition.model_validate({"from": match, "read": t, "to": to_state, "write": marker if t == s else t, "move": "L" if t == s else "R"}))

    # q4: volver hacia la izquierda hasta el siguiente marcador (único estado q4).
    for sym in sigma:
        transitions.append(Transition.model_validate({"from": RETURN_STATE, "read": sym, "to": RETURN_STATE, "write": sym, "move": "L"}))
    transitions.append(Transition.model_validate({"from": RETURN_STATE, "read": marker, "to": "q0", "write": marker, "move": "R"}))
    transitions.append(Transition.model_validate({"from": RETURN_STATE, "read": blank, "to": "q_reject", "write": blank, "move": "R"}))

    new_cfg = deepcopy(config)
    new_cfg.name = "Palíndromo (alfabeto libre)"
    new_cfg.description = "Acepta palíndromos sobre el alfabeto Σ definido por los símbolos de la entrada."
    new_cfg.states = states
    new_cfg.input_alphabet = sigma
    new_cfg.tape_alphabet = tape_alphabet
    new_cfg.transitions = transitions
    new_cfg.initial_state = "q0"
    new_cfg.accept_states = ["q_accept"]
    new_cfg.reject_states = ["q_reject"]
    return new_cfg

