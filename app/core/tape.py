from collections import defaultdict


class Tape:
    """Cinta infinita: diccionario index→símbolo y posición de la cabeza."""

    def __init__(self, blank: str, input_string: str):
        self.blank = blank
        self.cells: dict[int, str] = defaultdict(lambda: blank)
        for i, symbol in enumerate(input_string):
            self.cells[i] = symbol
        self.head = 0

    def read(self) -> str:
        """Lee el símbolo bajo la cabeza."""
        return self.cells[self.head]

    def write(self, symbol: str) -> None:
        """Escribe en la celda actual."""
        self.cells[self.head] = symbol

    def move(self, direction: str) -> None:
        """Mueve la cabeza L (izq) o R (der)."""
        if direction == "L":
            self.head -= 1
        elif direction == "R":
            self.head += 1
        else:
            raise ValueError(f"Dirección inválida: {direction}")

    def window(self, blank_pad: int = 2, view_radius: int = 14) -> list[dict]:
        """Ventana visible: contenido útil acotado alrededor del cabezal."""
        significant: set[int] = {self.head}
        for idx, sym in self.cells.items():
            if sym != self.blank:
                significant.add(idx)

        lo = min(significant) - blank_pad
        hi = max(significant) + blank_pad

        view_lo = self.head - view_radius
        view_hi = self.head + view_radius
        lo = max(lo, view_lo)
        hi = min(hi, view_hi)

        return [{"index": i, "symbol": self.cells[i]} for i in range(lo, hi + 1)]
