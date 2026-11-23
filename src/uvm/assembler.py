"""Трансляция программы на языке ассемблера УВМ (YAML) в промежуточное
представление."""

from typing import Any, Dict, List, Tuple

import yaml

from uvm.errors import AssemblerError
from uvm.intermediate import OPCODE_LABEL, Instruction
from uvm.spec import COMMANDS, CommandSpec, Operand

SINGLE_ITEM = 1
MIN_VALUE = 0


def load_source(path: str) -> Any:
    """Прочитать файл с программой и разобрать его как YAML."""
    try:
        with open(path, encoding="utf-8") as source:
            return yaml.safe_load(source)
    except OSError as error:
        raise AssemblerError(
            f"не удалось прочитать файл «{path}»: {error.strerror}"
        ) from error
    except yaml.YAMLError as error:
        raise AssemblerError(
            f"ошибка YAML в файле «{path}»: {error}"
        ) from error


def split_command(item: Any, number: int) -> Tuple[str, Dict[Any, Any]]:
    """Разделить запись команды на имя и словарь операндов."""
    if not isinstance(item, dict) or len(item) != SINGLE_ITEM:
        raise AssemblerError(
            f"команда {number}: ожидается запись вида "
            "«имя: {операнд: значение, ...}»"
        )
    (name, params), = item.items()
    if not isinstance(params, dict):
        raise AssemblerError(
            f"команда {number} ({name}): операнды должны быть заданы "
            "в виде «ключ: значение»"
        )
    return str(name), params


def find_spec(name: str, number: int) -> CommandSpec:
    """Найти описание команды по имени."""
    if name not in COMMANDS:
        known = ", ".join(COMMANDS)
        raise AssemblerError(
            f"команда {number}: неизвестная команда «{name}», "
            f"допустимые команды: {known}"
        )
    return COMMANDS[name]


def check_keys(spec: CommandSpec, params: Dict[Any, Any], number: int) -> None:
    """Проверить, что заданы все операнды команды и нет лишних."""
    expected = [operand.key for operand in spec.operands]
    missing = [key for key in expected if key not in params]
    extra = [str(key) for key in params if key not in expected]
    if missing:
        raise AssemblerError(
            f"команда {number} ({spec.name}): не задан операнд "
            f"«{missing[0]}»"
        )
    if extra:
        raise AssemblerError(
            f"команда {number} ({spec.name}): неизвестный операнд "
            f"«{extra[0]}», допустимые операнды: {', '.join(expected)}"
        )


def check_value(
    spec: CommandSpec, operand: Operand, value: Any, number: int
) -> int:
    """Проверить значение операнда: целое число, помещающееся в поле."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise AssemblerError(
            f"команда {number} ({spec.name}): операнд «{operand.key}» "
            f"должен быть целым числом, получено «{value}»"
        )
    if not MIN_VALUE <= value <= operand.max_value:
        raise AssemblerError(
            f"команда {number} ({spec.name}): операнд «{operand.key}» "
            f"равен {value}, допустимы значения от {MIN_VALUE} "
            f"до {operand.max_value} (поле {operand.label}, "
            f"{operand.bits} бит)"
        )
    return value


def translate_command(item: Any, number: int) -> Instruction:
    """Преобразовать одну запись программы в команду."""
    name, params = split_command(item, number)
    spec = find_spec(name, number)
    check_keys(spec, params, number)
    fields = [(OPCODE_LABEL, spec.opcode)]
    for operand in spec.operands:
        value = check_value(spec, operand, params[operand.key], number)
        fields.append((operand.label, value))
    return Instruction(name=spec.name, fields=tuple(fields))


def translate(program: Any) -> List[Instruction]:
    """Преобразовать программу (список команд) в промежуточное
    представление."""
    if not isinstance(program, list) or not program:
        raise AssemblerError(
            "программа должна быть непустым списком команд "
            "(каждая команда начинается с «- »)"
        )
    return [
        translate_command(item, number)
        for number, item in enumerate(program, start=1)
    ]


def assemble_file(path: str) -> List[Instruction]:
    """Прочитать файл с программой и получить промежуточное
    представление."""
    return translate(load_source(path))
