"""Тесты машинного кода: байты должны совпадать со спецификацией УВМ."""

import os
import unittest

from uvm.assembler import assemble_file, translate
from uvm.binary import format_bytes
from uvm.machine import encode_instruction, encode_program

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
SPEC_PROGRAM = os.path.join(EXAMPLES_DIR, "spec_tests.yaml")

LOAD_CONST_BYTES = bytes([0xE7, 0x47, 0x00, 0x00, 0xE0, 0x08])
READ_BYTES = bytes([0x2D, 0x65, 0x2D, 0x00, 0x00, 0x00])
WRITE_BYTES = bytes([0x96, 0x54, 0x05, 0x00, 0x00, 0x00])
SQRT_BYTES = bytes([0x17, 0x86, 0x00, 0x00, 0x00, 0x00])


class SpecBytesTest(unittest.TestCase):
    """Проверка байтов каждой команды из спецификации."""

    def assert_bytes(self, program, expected):
        """Проверить машинный код единственной команды программы."""
        instruction = translate(program)[0]
        self.assertEqual(encode_instruction(instruction), expected)

    def test_load_const(self):
        """Загрузка константы: A=7, B=575, C=71."""
        self.assert_bytes(
            [{"load_const": {"value": 575, "reg": 71}}], LOAD_CONST_BYTES
        )

    def test_read(self):
        """Чтение значения из памяти: A=13, B=41, C=726."""
        self.assert_bytes(
            [{"read": {"reg": 41, "addr": 726}}], READ_BYTES
        )

    def test_write(self):
        """Запись значения в память: A=22, B=36, C=85."""
        self.assert_bytes(
            [{"write": {"ptr": 36, "src": 85}}], WRITE_BYTES
        )

    def test_sqrt(self):
        """Унарная операция sqrt(): A=23, B=48, C=8."""
        self.assert_bytes(
            [{"sqrt": {"ptr": 48, "src": 8}}], SQRT_BYTES
        )


class ProgramBytesTest(unittest.TestCase):
    """Проверка машинного кода всей программы."""

    def test_spec_program(self):
        """Файл spec_tests.yaml даёт все тестовые последовательности."""
        code = encode_program(assemble_file(SPEC_PROGRAM))
        self.assertEqual(
            code,
            LOAD_CONST_BYTES + READ_BYTES + WRITE_BYTES + SQRT_BYTES,
        )

    def test_size_is_six_bytes_per_command(self):
        """Каждая команда занимает ровно 6 байт."""
        code = encode_program(assemble_file(SPEC_PROGRAM))
        self.assertEqual(len(code), 4 * len(LOAD_CONST_BYTES))

    def test_empty_program(self):
        """Пустой список команд даёт пустой машинный код."""
        self.assertEqual(encode_program([]), b"")

    def test_maximum_values(self):
        """Наибольшие значения занимают все биты своих полей."""
        program = [{"load_const": {"value": 4294967295, "reg": 127}}]
        code = encode_program(translate(program))
        self.assertEqual(code, bytes([0xE7, 0xFF, 0xFF, 0xFF, 0xFF, 0x0F]))

    def test_fields_do_not_overlap(self):
        """Поля не затирают друг друга: чтение с разными B и C."""
        program = [{"read": {"reg": 127, "addr": 1048575}}]
        code = encode_program(translate(program))
        self.assertEqual(code, bytes([0xED, 0xFF, 0xFF, 0xFF, 0x00, 0x00]))


class FormatBytesTest(unittest.TestCase):
    """Вывод байтов в формате из спецификации."""

    def test_format(self):
        """Байты выводятся как 0xE7, 0x47 с двумя цифрами и заглавными."""
        self.assertEqual(
            format_bytes(LOAD_CONST_BYTES),
            "0xE7, 0x47, 0x00, 0x00, 0xE0, 0x08",
        )

    def test_format_empty(self):
        """Для пустых данных выводится пустая строка."""
        self.assertEqual(format_bytes(b""), "")


if __name__ == "__main__":
    unittest.main()
