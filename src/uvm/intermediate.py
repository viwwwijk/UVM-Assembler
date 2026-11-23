"""Промежуточное представление команды УВМ."""

from dataclasses import dataclass
from typing import Tuple

OPCODE_LABEL = "A"


@dataclass(frozen=True)
class Instruction:
    """Команда в промежуточном представлении.

    Attributes:
        name: имя команды в языке ассемблера.
        fields: пары «имя поля, значение» в порядке A, B, C.
    """

    name: str
    fields: Tuple[Tuple[str, int], ...]

    def value(self, label: str) -> int:
        """Вернуть значение поля по его имени (``A``, ``B`` или ``C``)."""
        return dict(self.fields)[label]

    def format(self) -> str:
        """Записать поля в виде ``A=7, B=575, C=71``."""
        return ", ".join(f"{label}={value}" for label, value in self.fields)
