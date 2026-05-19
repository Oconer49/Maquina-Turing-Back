from app.models.machine import TuringMachineConfig


class ValidationError(Exception):
    pass


class MachineValidator:
    """Comprueba que la definición de la MT sea coherente."""

    @staticmethod
    def validate_machine(config: TuringMachineConfig) -> None:
        """Valida estados, alfabetos y que δ no tenga duplicados."""
        if not config.states:
            raise ValidationError("El conjunto de estados no puede estar vacío")
        if not config.input_alphabet:
            raise ValidationError("El alfabeto de entrada no puede estar vacío")
        if not config.tape_alphabet:
            raise ValidationError("El alfabeto de cinta no puede estar vacío")
        if config.blank not in config.tape_alphabet:
            raise ValidationError("El símbolo blanco debe pertenecer al alfabeto de cinta")
        if config.blank in config.input_alphabet:
            raise ValidationError("El símbolo blanco no puede estar en el alfabeto de entrada")

        input_set = set(config.input_alphabet)
        tape_set = set(config.tape_alphabet)
        if not input_set.issubset(tape_set):
            raise ValidationError("El alfabeto de entrada debe ser subconjunto del alfabeto de cinta")

        if config.initial_state not in config.states:
            raise ValidationError("El estado inicial no está definido en los estados")

        for state in config.accept_states:
            if state not in config.states:
                raise ValidationError(f"Estado de aceptación '{state}' no definido")

        for state in config.reject_states:
            if state not in config.states:
                raise ValidationError(f"Estado de rechazo '{state}' no definido")

        overlap = set(config.accept_states) & set(config.reject_states)
        if overlap:
            raise ValidationError("Los estados de aceptación y rechazo no pueden solaparse")

        seen: set[tuple[str, str]] = set()
        for t in config.transitions:
            if t.from_state not in config.states:
                raise ValidationError(f"Estado origen '{t.from_state}' no definido")
            if t.to not in config.states:
                raise ValidationError(f"Estado destino '{t.to}' no definido")
            if t.read not in tape_set:
                raise ValidationError(f"Símbolo leído '{t.read}' no está en el alfabeto de cinta")
            if t.write not in tape_set:
                raise ValidationError(f"Símbolo escrito '{t.write}' no está en el alfabeto de cinta")
            if t.move not in ("L", "R"):
                raise ValidationError(f"Movimiento '{t.move}' inválido; use L o R")

            key = (t.from_state, t.read)
            if key in seen:
                raise ValidationError(f"Transición duplicada para ({t.from_state}, {t.read})")
            seen.add(key)

    @staticmethod
    def validate_input(config: TuringMachineConfig, input_string: str) -> None:
        """Recorre la cadena y rechaza símbolos fuera de Σ."""
        input_set = set(config.input_alphabet)
        for i, char in enumerate(input_string):
            if char not in input_set:
                allowed = ", ".join(sorted(input_set))
                raise ValidationError(
                    f"El símbolo '{char}' en posición {i} no pertenece al alfabeto de entrada {{{allowed}}}"
                )
