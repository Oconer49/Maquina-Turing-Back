import re

RUNNING = "RUNNING"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
STEP_LIMIT = "STEP_LIMIT"

MACHINES_WITH_PEDAGOGICAL_REJECT = frozenset(
    {"even_zeros", "binary_palindrome", "a_power_n_b_power_n", "unary_increment"}
)


def _state_latex(state: str) -> str:
    """Estado q3 → $q_{3}$ para que KaTeX no lo muestre partido."""
    if not state:
        return ""
    m = re.match(r"^q_?(.+)$", state, re.I)
    if not m:
        return f"\\text{{{state}}}"
    body = m.group(1)
    if body.isdigit():
        return f"q_{{{body}}}"
    return f"q_{{\\text{{{body}}}}}"


def explain_result(    status: str,
    machine_id: str | None,
    input_string: str,
    current_state: str,
    blank: str,
    halt_cause: str | None = None,
    symbol_at_halt: str | None = None,
) -> str | None:
    """Genera el mensaje pedagógico cuando la simulación termina."""
    if status == RUNNING:
        return None

    mid = machine_id or ""

    if status == ACCEPTED:
        return _accept_message(mid, input_string)

    if status == STEP_LIMIT:
        return (
            "La simulación alcanzó el límite máximo de pasos sin detenerse. "
            "Puede deberse a un bucle infinito en la máquina o a una cadena muy larga."
        )

    if status == REJECTED:
        if mid in MACHINES_WITH_PEDAGOGICAL_REJECT:
            return _reject_message(mid, input_string, current_state, halt_cause)

        if halt_cause == "no_transition" and symbol_at_halt is not None:
            sym = "$\\sqcup$ (blanco)" if symbol_at_halt == blank else f"${symbol_at_halt}$"
            q = _state_latex(current_state)
            return (
                f"No hay transición definida para el estado ${q}$ leyendo {sym}. "
                "La máquina no sabe cómo continuar con esta configuración."
            )
        return _reject_message(mid, input_string, current_state, halt_cause)
    return None


def _accept_message(machine_id: str, inp: str) -> str:
    """Texto de aceptación con el motivo según la máquina."""
    builders = {
        "even_zeros": _even_zeros_accept,
        "binary_palindrome": _palindrome_accept,
        "a_power_n_b_power_n": _anbn_accept,
        "unary_increment": _unary_accept,
    }
    builder = builders.get(machine_id)
    if builder:
        return builder(inp)
    return "La cadena pertenece al lenguaje que reconoce esta máquina."


def _reject_message(machine_id: str, inp: str, state: str, halt_cause: str | None) -> str:
    """Texto de rechazo con el motivo según la máquina."""
    builders = {
        "even_zeros": lambda: _even_zeros_reject(inp, state),
        "binary_palindrome": lambda: _palindrome_reject(inp),
        "a_power_n_b_power_n": lambda: _anbn_reject(inp),
        "unary_increment": lambda: _unary_reject(inp),
    }
    builder = builders.get(machine_id)
    if builder:
        return builder()

    if halt_cause == "reject_state":
        return f"Se alcanzó el estado de rechazo ${state}$."
    return "La cadena no pertenece al lenguaje que reconoce esta máquina."


def _first_palindrome_mismatch(inp: str) -> tuple[int, int, str, str] | None:
    """Primera pareja de posiciones simétricas que no coinciden."""
    for i in range(len(inp)):
        j = len(inp) - 1 - i
        if i >= j:
            return None
        if inp[i] != inp[j]:
            return i, j, inp[i], inp[j]
    return None


def _palindrome_accept(inp: str) -> str:
    if not inp:
        return (
            "Por qué sí: $\\varepsilon$ es palíndromo. "
            "No hay símbolos en extremos opuestos que deban coincidir."
        )
    mismatch = _first_palindrome_mismatch(inp)
    if mismatch:
        return (
            f"La cadena ${inp}$ fue aceptada por la máquina. "
            "Revise la ejecución si esperaba un rechazo."
        )
    return (
        f"Por qué sí: ${inp}$ es palíndromo sobre $\\Sigma^*$. "
        f"Al comparar posiciones simétricas (extremo izquierdo con derecho, luego hacia el centro), "
        f"todos los pares coinciden; por ejemplo ${inp[0]}$ con ${inp[-1]}$"
        f"{f' y ${inp[1]}$ con ${inp[-2]}$' if len(inp) > 3 else ''}. "
        f"La lectura al revés es ${inp[::-1]}$, igual que la original."
    )


def _palindrome_reject(inp: str) -> str:
    if not inp:
        return (
            "Por qué no: $\\varepsilon$ es palíndromo en $\\Sigma^*$; "
            "si fue rechazada, revise la configuración o la traza de la máquina."
        )

    mismatch = _first_palindrome_mismatch(inp)
    if mismatch:
        i, j, left_sym, right_sym = mismatch
        return (
            f"Por qué no: ${inp}$ no es palíndromo. "
            f"En la posición ${i}$ (desde la izquierda) está ${left_sym}$ y en la posición ${j}$ "
            f"(desde la derecha) está ${right_sym}$; deben ser iguales en un palíndromo. "
            f"Por eso la lectura al revés (${inp[::-1]}$) no coincide con ${inp}$."
        )

    return (
        f"Por qué no: ${inp}$ parece simétrica (${inp[::-1]}$), pero la máquina rechazó "
        "antes de terminar la verificación (marcado con $X$ en la cinta). "
        "Revise el historial de pasos."
    )


def _even_zeros_accept(inp: str) -> str:
    zero_count = inp.count("0")
    if zero_count == 0:
        return (
            "Por qué sí: la cadena no tiene ningún $0$. "
            "Cero ceros es cantidad par; la máquina acepta cadenas con paridad par de símbolos $0$ en $\\{0,1\\}$."
        )
    return (
        f"Por qué sí: la cadena tiene ${zero_count}$ símbolo(s) $0$, cantidad par. "
        f"Esta máquina acepta exactamente las cadenas de $\\{{0,1\\}}^*$ con un número par de ceros "
        f"(los $1$ no alteran la paridad)."
    )


def _even_zeros_reject(inp: str, state: str) -> str:
    zero_count = inp.count("0")
    if zero_count == 0:
        return "Rechazo inesperado: no hay ceros y la paridad debería ser par."
    if zero_count % 2 == 1:
        return (
            f"Por qué no: hay ${zero_count}$ símbolo(s) $0$ (cantidad impar). "
            f"La máquina solo acepta un número par de ceros; con ${zero_count}$ ceros la paridad falla."
        )
    return (
        f"Por qué no: la cadena llegó a ${state}$ aunque el conteo de ceros (${zero_count}$) es par. "
        "Revise la traza: puede haber terminado en rechazo al leer el blanco en estado equivocado."
    )


def _anbn_accept(inp: str) -> str:
    a_count = inp.count("a")
    b_count = inp.count("b")
    n = a_count
    return (
        f"Por qué sí: ${inp}$ tiene la forma $a^{{n}}b^{{n}}$ con $n={n}$. "
        f"Hay ${a_count}$ letras $a$ seguidas de ${b_count}$ letras $b$ (misma cantidad), "
        "sin $b$ antes de terminar el bloque de $a$."
    )


def _first_a_after_b(inp: str) -> tuple[int, int] | None:
    """Primera $a$ que aparece después de alguna $b$: (índice de la a, índice de la primera b)."""
    first_b = None
    for i, ch in enumerate(inp):
        if ch == "b" and first_b is None:
            first_b = i
        elif ch == "a" and first_b is not None:
            return i, first_b
    return None


def _anbn_reject(inp: str) -> str:
    if not inp:
        return (
            "Por qué no: $\\varepsilon$ no pertenece a $\\{ a^n b^n \\mid n \\geq 1 \\}$; "
            "se necesita al menos una $a$ y una $b$."
        )

    a_count = inp.count("a")
    b_count = inp.count("b")

    mix = _first_a_after_b(inp)
    if mix is not None:
        i_a, i_b = mix
        return (
            f"Por qué no: ${inp}$ no pertenece a $a^{{n}}b^{{n}}$. "
            f"En la posición ${i_b}$ hay una $b$ y en la posición ${i_a}$ vuelve a aparecer una $a$. "
            f"En este lenguaje todas las $a$ deben ir juntas al inicio y luego todas las $b$, sin mezclar."
        )
    if a_count != b_count:
        return (
            f"Por qué no: hay ${a_count}$ letra(s) $a$ y ${b_count}$ letra(s) $b$. "
            f"En $a^{{n}}b^{{n}}$ deben ser la misma cantidad ($n$ iguales para $a$ y para $b$)."
        )

    if a_count == 0 or b_count == 0:
        return (
            f"Por qué no: ${inp}$ no cumple $a^{{n}}b^{{n}}$ con $n \\geq 1$ "
            "(hace falta al menos un $a$ y un $b$)."
        )

    if inp != "a" * a_count + "b" * b_count:
        return (
            f"Por qué no: ${inp}$ no es un bloque de solo $a$ seguido de un bloque de solo $b$."
        )

    return f"Por qué no: ${inp}$ no pertenece al lenguaje $a^{{n}}b^{{n}}$."


def _unary_accept(inp: str) -> str:
    n = len(inp)
    return (
        f"Por qué sí: ${inp}$ es $1^{{{n}}}$ ($n={n}$ símbolos $1$). "
        f"La máquina sumó $1$ en notación unaria (resultado $1^{{{n + 1}}}$ en la cinta al finalizar)."
    )


def _unary_reject(inp: str) -> str:
    if not inp:
        return (
            "Por qué no: $\\varepsilon$ no es válida para incremento unario; "
            "se espera $1^{{n}}$ con $n \\geq 1$."
        )
    bad = [c for c in inp if c != "1"]
    if bad:
        return (
            f"Por qué no: la cadena contiene símbolos distintos de $1$ "
            f"(por ejemplo ${bad[0]}$). Solo se aceptan cadenas unarias."
        )
    return (
        f"Por qué no: ${inp}$ tiene solo $1$, pero la máquina rechazó antes de completar el incremento. "
        "Revise la traza paso a paso."
    )
