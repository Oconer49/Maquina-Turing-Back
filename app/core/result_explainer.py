RUNNING = "RUNNING"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
STEP_LIMIT = "STEP_LIMIT"


def explain_result(
    status: str,
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
        if halt_cause == "no_transition" and symbol_at_halt is not None:
            sym = "$\\sqcup$ (blanco)" if symbol_at_halt == blank else f"${symbol_at_halt}$"
            return (
                f"No hay transición definida para el estado ${current_state}$ leyendo {sym}. "
                "La máquina no sabe cómo continuar."
            )
        return _reject_message(mid, input_string, current_state, halt_cause)

    return None


def _accept_message(machine_id: str, inp: str) -> str:
    """Elige el texto de aceptación según la máquina preset."""
    messages = {
        "even_zeros": _even_zeros_accept(inp),
        "binary_palindrome": (
            f"La cadena ${inp}$ es un palíndromo sobre $\\{{0,1\\}}$: se lee igual "
            "de izquierda a derecha que de derecha a izquierda."
        ),
        "a_power_n_b_power_n": _anbn_accept(inp),
        "unary_increment": (
            f"La cadena ${inp}$ tiene la forma $1^{{n}}$ con $n \\geq 1$. "
            "La máquina incrementó correctamente el valor unario en la cinta."
        ),
    }
    return messages.get(machine_id, "La cadena pertenece al lenguaje que reconoce esta máquina.")


def _reject_message(machine_id: str, inp: str, state: str, halt_cause: str | None) -> str:
    """Elige el texto de rechazo según la máquina y la cadena."""
    if machine_id == "even_zeros":
        return _even_zeros_reject(inp, state)
    if machine_id == "binary_palindrome":
        return _palindrome_reject(inp)
    if machine_id == "a_power_n_b_power_n":
        return _anbn_reject(inp)
    if machine_id == "unary_increment":
        return _unary_reject(inp)

    if halt_cause == "reject_state":
        return f"Se alcanzó el estado de rechazo ${state}$."
    return "La cadena no pertenece al lenguaje que reconoce esta máquina."


def _even_zeros_accept(inp: str) -> str:
    zero_count = inp.count("0")
    if zero_count == 0:
        return "La cadena no contiene ningún $0$ ($0$ ceros es cantidad par). Fue aceptada."
    return (
        f"La cadena contiene ${zero_count}$ símbolo(s) $0$ (cantidad par). "
        "Cumple la paridad pedida sobre $\\{0,1\\}$."
    )


def _even_zeros_reject(inp: str, state: str) -> str:
    zero_count = inp.count("0")
    if zero_count == 0:
        return "Rechazo inesperado: la cadena no tiene ceros."
    if zero_count % 2 == 1:
        return (
            f"La cadena contiene ${zero_count}$ símbolo(s) $0$ (cantidad impar). "
            "Esta máquina solo acepta cantidad par de ceros sobre $\\{0,1\\}$."
        )
    return (
        "La cadena terminó en estado de rechazo aunque el conteo de ceros parece par. "
        "Revise la ejecución paso a paso."
    )


def _palindrome_reject(inp: str) -> str:
    if not inp:
        return "La cadena vacía es palíndromo; si fue rechazada, revise la configuración de la máquina."
    if inp != inp[::-1]:
        return (
            f"La cadena ${inp}$ no es palíndromo: los extremos "
            f"${inp[0]}$ y ${inp[-1]}$ no coinciden o la estructura interna no es simétrica."
        )
    return (
        f"La cadena ${inp}$ fue rechazada durante el marcado de extremos; "
        "no se completó la verificación del palíndromo."
    )


def _anbn_accept(inp: str) -> str:
    n = len(inp) // 2 if inp else 0
    return (
        f"La cadena ${inp}$ tiene la forma $a^{{n}}b^{{n}}$ con $n={n}$: "
        f"${n}$ letras $a$ seguidas de ${n}$ letras $b$."
    )


def _anbn_reject(inp: str) -> str:
    if not inp:
        return "La cadena vacía no pertenece a $\\{ a^n b^n \\mid n \\geq 1 \\}$."

    a_count = inp.count("a")
    b_count = inp.count("b")

    for i, ch in enumerate(inp):
        if ch == "b" and "a" in inp[i + 1 :]:
            return (
                f"La cadena ${inp}$ no tiene la forma $a^{{n}}b^{{n}}$: hay una $b$ antes de "
                "terminar el bloque de $a$ (todas las $a$ deben ir al inicio)."
            )

    if a_count != b_count:
        return (
            f"La cadena ${inp}$ tiene ${a_count}$ letra(s) $a$ y ${b_count}$ letra(s) $b$. "
            "En $a^{{n}}b^{{n}}$ deben ser la misma cantidad."
        )

    if a_count == 0 or b_count == 0:
        return f"La cadena ${inp}$ no cumple $a^{{n}}b^{{n}}$ con $n \\geq 1$."

    if inp != "a" * a_count + "b" * b_count:
        return (
            f"La cadena ${inp}$ no es un bloque de $a$ seguido de un bloque de $b$."
        )

    return f"La cadena ${inp}$ no pertenece al lenguaje $a^{{n}}b^{{n}}$."



def _unary_reject(inp: str) -> str:
    if not inp:
        return "La cadena vacía no es válida: se espera $1^{{n}}$ con $n \\geq 1$."
    if any(c != "1" for c in inp):
        return "La cadena contiene símbolos distintos de $1$."
    return "La cadena fue rechazada antes de completar el incremento unario."
