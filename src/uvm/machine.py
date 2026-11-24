"""Перевод между промежуточным представлением и машинным кодом УВМ.

Команда занимает 6 байт. Её поля A, B и C собираются в одно 48-битное
число (позиции и размеры полей берутся из ``uvm.spec``), которое
записывается в порядке от младшего байта к старшему.
"""

from typing import Iterable, List

from uvm.errors import InterpreterError
from uvm.intermediate import OPCODE_LABEL, Instruction
from uvm.spec import (
    COMMAND_SIZE_BYTES,
    COMMANDS,
    COMMANDS_BY_OPCODE,
    OPCODE_BITS,
    OPCODE_FIRST_BIT,
)

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


def decode_instruction(word: bytes) -> Instruction:
    """Перевести 6 байт машинного кода в промежуточное представление."""
    number = int.from_bytes(word, BYTE_ORDER)
    opcode = (number >> OPCODE_FIRST_BIT) & ((1 << OPCODE_BITS) - 1)
    if opcode not in COMMANDS_BY_OPCODE:
        raise InterpreterError(f"неизвестный код операции A={opcode}")
    spec = COMMANDS_BY_OPCODE[opcode]
    fields = [(OPCODE_LABEL, opcode)]
    for operand in spec.operands:
        value = (number >> operand.first_bit) & operand.max_value
        fields.append((operand.label, value))
    return Instruction(name=spec.name, fields=tuple(fields))


def decode_program(code: bytes) -> List[Instruction]:
    """Перевести машинный код программы в список команд."""
    if len(code) % COMMAND_SIZE_BYTES:
        raise InterpreterError(
            f"размер программы {len(code)} байт не кратен размеру "
            f"команды ({COMMAND_SIZE_BYTES} байт)"
        )
    instructions = []
    for start in range(0, len(code), COMMAND_SIZE_BYTES):
        word = code[start:start + COMMAND_SIZE_BYTES]
        try:
            instructions.append(decode_instruction(word))
        except InterpreterError as error:
            number = start // COMMAND_SIZE_BYTES + 1
            raise InterpreterError(f"команда {number}: {error}") from error
    return instructions
