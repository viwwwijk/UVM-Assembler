"""Запись машинного кода в файл и вывод его в виде байтов."""

from uvm.errors import AssemblerError


def format_bytes(code: bytes) -> str:
    """Записать байты в виде ``0xE7, 0x47, 0x00``."""
    return ", ".join(f"0x{byte:02X}" for byte in code)


def write_binary(path: str, code: bytes) -> None:
    """Записать машинный код в двоичный файл."""
    try:
        with open(path, "wb") as output:
            output.write(code)
    except OSError as error:
        raise AssemblerError(
            f"не удалось записать файл «{path}»: {error.strerror}"
        ) from error
