"""Интерфейс командной строки интерпретатора УВМ."""

import argparse
import sys
from typing import List, Optional, TextIO

from uvm.binary import read_binary
from uvm.dump import check_range, dump_xml, write_dump
from uvm.errors import UvmError
from uvm.machine import decode_program
from uvm.vm import Machine

EXIT_OK = 0
EXIT_ERROR = 1
AUTO_BASE = 0


def parse_address(text: str) -> int:
    """Разобрать адрес: десятичное число или число с префиксом 0x."""
    try:
        return int(text, AUTO_BASE)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"«{text}» не является целым числом"
        ) from error


def build_parser() -> argparse.ArgumentParser:
    """Создать разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="interpreter.py",
        description="Интерпретатор учебной виртуальной машины (УВМ).",
    )
    parser.add_argument(
        "binary", help="путь к двоичному файлу с ассемблированной программой"
    )
    parser.add_argument(
        "dump", help="путь к XML-файлу для дампа памяти после выполнения"
    )
    parser.add_argument(
        "-r",
        "--range",
        nargs=2,
        type=parse_address,
        required=True,
        metavar=("FIRST", "LAST"),
        help="диапазон адресов памяти данных для дампа (границы включаются)",
    )
    return parser


def run(args: argparse.Namespace, stdout: TextIO) -> None:
    """Выполнить программу и записать дамп памяти."""
    first, last = args.range
    check_range(first, last)
    program = decode_program(read_binary(args.binary))
    machine = Machine(program)
    count = machine.run()
    write_dump(args.dump, dump_xml(machine.data, first, last))
    print(f"Выполнено команд: {count}", file=stdout)
    print(f"Дамп памяти {first}..{last} записан в {args.dump}", file=stdout)


def main(
    argv: Optional[List[str]] = None,
    stdout: Optional[TextIO] = None,
    stderr: Optional[TextIO] = None,
) -> int:
    """Запустить интерпретатор и вернуть код завершения."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    try:
        run(args, stdout)
    except UvmError as error:
        print(f"ошибка: {error}", file=stderr)
        return EXIT_ERROR
    return EXIT_OK
