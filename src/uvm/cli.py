"""Интерфейс командной строки ассемблера УВМ."""

import argparse
import sys
from typing import List, Optional, TextIO

from uvm.assembler import assemble_file
from uvm.errors import AssemblerError
from uvm.intermediate import Instruction

EXIT_OK = 0
EXIT_ASSEMBLER_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    """Создать разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Ассемблер учебной виртуальной машины (УВМ), вариант 12.",
    )
    parser.add_argument(
        "source", help="путь к исходному файлу с текстом программы (YAML)"
    )
    parser.add_argument("output", help="путь к двоичному файлу-результату")
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="режим тестирования: вывести внутреннее представление "
        "программы в формате полей и значений",
    )
    return parser


def print_instructions(
    instructions: List[Instruction], stdout: TextIO
) -> None:
    """Вывести команды в формате «A=7, B=575, C=71», по одной в строке."""
    for instruction in instructions:
        print(instruction.format(), file=stdout)


def main(
    argv: Optional[List[str]] = None,
    stdout: Optional[TextIO] = None,
    stderr: Optional[TextIO] = None,
) -> int:
    """Запустить ассемблер и вернуть код завершения."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    try:
        instructions = assemble_file(args.source)
    except AssemblerError as error:
        print(f"ошибка: {error}", file=stderr)
        return EXIT_ASSEMBLER_ERROR
    if args.test:
        print_instructions(instructions, stdout)
    else:
        print(f"Ассемблировано команд: {len(instructions)}", file=stdout)
    return EXIT_OK
