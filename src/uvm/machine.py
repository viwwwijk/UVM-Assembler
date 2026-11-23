"""Перевод промежуточного представления в машинный код УВМ.

Команда занимает 6 байт. Её поля A, B и C собираются в одно 48-битное
число (позиции и размеры полей берутся из ``uvm.spec``), которое
записывается в порядке от младшего байта к старшему.
"""

from typing import Iterable

from uvm.intermediate import OPCODE_LABEL, Instruction
from uvm.spec import COMMAND_SIZE_BYTES, COMMANDS, OPCODE_FIRST_BIT

BYTE_ORDER = "little"


def encode_instruction(instruction: Instruction) -> bytes:
    """Перевести одну команду в машинный код (6 байт)."""
    spec = COMMANDS[instruction.name]
    word = instruction.value(OPCODE_LABEL) << OPCODE_FIRST_BIT
    for operand in spec.operands:
        word |= instruction.value(operand.label) << operand.first_bit
    return word.to_bytes(COMMAND_SIZE_BYTES, BYTE_ORDER)


def encode_program(instructions: Iterable[Instruction]) -> bytes:
    """Перевести программу в машинный код: команды идут подряд."""
    return b"".join(encode_instruction(item) for item in instructions)
