"""Тесты декодирования машинного кода в промежуточное представление."""

import unittest

from uvm.assembler import translate
from uvm.errors import InterpreterError
from uvm.machine import (
    decode_instruction,
    decode_program,
    encode_instruction,
    encode_program,
)


class DecodeSpecTest(unittest.TestCase):
    """Декодирование байтов из спецификации УВМ."""

    def assert_decoded(self, code, name, fields):
        """Проверить имя и поля декодированной команды."""
        instruction = decode_instruction(bytes(code))
        self.assertEqual(instruction.name, name)
        self.assertEqual(instruction.fields, fields)

    def test_load_const(self):
        """Байты загрузки константы: A=7, B=575, C=71."""
        self.assert_decoded(
            [0xE7, 0x47, 0x00, 0x00, 0xE0, 0x08],
            "load_const",
            (("A", 7), ("B", 575), ("C", 71)),
        )

    def test_read(self):
        """Байты чтения: A=13, B=41, C=726."""
        self.assert_decoded(
            [0x2D, 0x65, 0x2D, 0x00, 0x00, 0x00],
            "read",
            (("A", 13), ("B", 41), ("C", 726)),
        )

    def test_write(self):
        """Байты записи: A=22, B=36, C=85."""
        self.assert_decoded(
            [0x96, 0x54, 0x05, 0x00, 0x00, 0x00],
            "write",
            (("A", 22), ("B", 36), ("C", 85)),
        )

    def test_sqrt(self):
        """Байты sqrt(): A=23, B=48, C=8."""
        self.assert_decoded(
            [0x17, 0x86, 0x00, 0x00, 0x00, 0x00],
            "sqrt",
            (("A", 23), ("B", 48), ("C", 8)),
        )


class RoundTripTest(unittest.TestCase):
    """Кодирование и декодирование возвращают исходную программу."""

    def test_round_trip(self):
        """Программа с крайними значениями полей не меняется."""
        program = [
            {"load_const": {"value": 4294967295, "reg": 127}},
            {"load_const": {"value": 0, "reg": 0}},
            {"read": {"reg": 127, "addr": 1048575}},
            {"write": {"ptr": 127, "src": 127}},
            {"sqrt": {"ptr": 1, "src": 2}},
        ]
        instructions = translate(program)
        decoded = decode_program(encode_program(instructions))
        self.assertEqual(decoded, instructions)

    def test_single_instruction(self):
        """Одна команда восстанавливается из своих 6 байт."""
        instruction = translate([{"read": {"reg": 5, "addr": 99}}])[0]
        self.assertEqual(
            decode_instruction(encode_instruction(instruction)), instruction
        )


class DecodeErrorsTest(unittest.TestCase):
    """Ошибки в машинном коде."""

    def test_empty_program(self):
        """Пустой файл — программа без команд."""
        self.assertEqual(decode_program(b""), [])

    def test_size_is_not_multiple_of_command(self):
        """Размер файла должен быть кратен 6 байтам."""
        with self.assertRaises(InterpreterError) as context:
            decode_program(bytes(7))
        self.assertIn("не кратен", str(context.exception))

    def test_unknown_opcode(self):
        """Неизвестный код операции указывает номер команды."""
        code = bytes([0x17, 0x86, 0, 0, 0, 0, 0x1F, 0, 0, 0, 0, 0])
        with self.assertRaises(InterpreterError) as context:
            decode_program(code)
        message = str(context.exception)
        self.assertIn("команда 2", message)
        self.assertIn("A=31", message)


if __name__ == "__main__":
    unittest.main()
