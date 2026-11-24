"""Дамп памяти данных в формате XML."""

from typing import List

from uvm.errors import InterpreterError
from uvm.spec import DATA_MEMORY_SIZE

MIN_ADDRESS = 0
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def check_range(first: int, last: int) -> None:
    """Проверить диапазон адресов: границы включаются в дамп."""
    last_address = DATA_MEMORY_SIZE - 1
    if not MIN_ADDRESS <= first <= last <= last_address:
        raise InterpreterError(
            f"неверный диапазон адресов {first}..{last}: нужно "
            f"{MIN_ADDRESS} <= первый <= последний <= {last_address}"
        )


def dump_xml(data: List[int], first: int, last: int) -> str:
    """Собрать XML-дамп ячеек памяти от first до last включительно."""
    check_range(first, last)
    lines = [XML_HEADER, f'<memory first="{first}" last="{last}">']
    for address in range(first, last + 1):
        lines.append(f'  <cell address="{address}">{data[address]}</cell>')
    lines.append("</memory>")
    return "\n".join(lines) + "\n"


def write_dump(path: str, text: str) -> None:
    """Записать XML-дамп в файл."""
    try:
        with open(path, "w", encoding="utf-8") as output:
            output.write(text)
    except OSError as error:
        raise InterpreterError(
            f"не удалось записать файл «{path}»: {error.strerror}"
        ) from error
