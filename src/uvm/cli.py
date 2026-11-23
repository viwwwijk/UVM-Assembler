"""Интерфейс командной строки ассемблера УВМ."""

import argparse
import sys
from typing import List, Optional, TextIO

from uvm.assembler import assemble_file
from uvm.binary import format_bytes, write_binary
from uvm.errors import AssemblerError
from uvm.intermediate import Instruction
from uvm.machine import encode_instruction, encode_program

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
        help="режим тестирования: вывести результат ассемблирования "
        "в байтовом формате",
    )
    return parser


def print_machine_code(
    instructions: List[Instruction], stdout: TextIO
) -> None:
    """Вывести машинный код в формате «0xE7, 0x47», по команде в строке."""
    for instruction in instructions:
        print(format_bytes(encode_instruction(instruction)), file=stdout)


def run(args: argparse.Namespace, stdout: TextIO) -> None:
    """Ассемблировать программу, записать файл и вывести результат."""
    instructions = assemble_file(args.source)
    code = encode_program(instructions)
    write_binary(args.output, code)
    if args.test:
        print_machine_code(instructions, stdout)
    print(f"Размер двоичного файла: {len(code)} байт", file=stdout)


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
        run(args, stdout)
    except AssemblerError as error:
        print(f"ошибка: {error}", file=stderr)
        return EXIT_ASSEMBLER_ERROR
    return EXIT_OK
