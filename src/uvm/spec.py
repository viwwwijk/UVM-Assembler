"""Спецификация команд УВМ (вариант 12).

Таблица ``COMMANDS`` описывает все команды: код операции (поле A) и
операнды (поля B и C) с позицией и размером в битах. Размер команды
составляет 6 байт, биты нумеруются с нуля от младшего.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

COMMAND_SIZE_BYTES = 6
OPCODE_FIRST_BIT = 0
OPCODE_BITS = 5


@dataclass(frozen=True)
class Operand:
    """Операнд команды: поле B или C.

    Attributes:
        key: ключ операнда в тексте программы на языке ассемблера.
        label: имя поля в спецификации (``B`` или ``C``).
        first_bit: номер младшего бита поля в команде.
        bits: размер поля в битах.
    """

    key: str
    label: str
    first_bit: int
    bits: int

    @property
    def max_value(self) -> int:
        """Наибольшее значение, которое помещается в поле."""
        return (1 << self.bits) - 1


@dataclass(frozen=True)
class CommandSpec:
    """Описание команды: имя, код операции и операнды."""

    name: str
    opcode: int
    operands: Tuple[Operand, ...]


COMMANDS: Dict[str, CommandSpec] = {
    "load_const": CommandSpec(
        name="load_const",
        opcode=7,
        operands=(
            Operand("value", "B", 5, 32),
            Operand("reg", "C", 37, 7),
        ),
    ),
    "read": CommandSpec(
        name="read",
        opcode=13,
        operands=(
            Operand("reg", "B", 5, 7),
            Operand("addr", "C", 12, 20),
        ),
    ),
    "write": CommandSpec(
        name="write",
        opcode=22,
        operands=(
            Operand("ptr", "B", 5, 7),
            Operand("src", "C", 12, 7),
        ),
    ),
    "sqrt": CommandSpec(
        name="sqrt",
        opcode=23,
        operands=(
            Operand("ptr", "B", 5, 7),
            Operand("src", "C", 12, 7),
        ),
    ),
}

COMMANDS_BY_OPCODE: Dict[int, CommandSpec] = {
    spec.opcode: spec for spec in COMMANDS.values()
}

REGISTER_COUNT = 1 << 7
DATA_MEMORY_SIZE = 1 << 20
