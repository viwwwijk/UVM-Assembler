"""Тесты команд из спецификации УВМ: поля и значения должны совпадать."""

import os
import unittest

from uvm.assembler import assemble_file, translate

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
SPEC_PROGRAM = os.path.join(EXAMPLES_DIR, "spec_tests.yaml")


class SpecCommandsTest(unittest.TestCase):
    """Проверка каждой команды из спецификации."""

    def assert_fields(self, program, expected):
        """Проверить поля единственной команды программы."""
        instructions = translate(program)
        self.assertEqual(len(instructions), len(program))
        self.assertEqual(instructions[0].fields, expected)

    def test_load_const(self):
        """Загрузка константы: A=7, B=575, C=71."""
        self.assert_fields(
            [{"load_const": {"value": 575, "reg": 71}}],
            (("A", 7), ("B", 575), ("C", 71)),
        )

    def test_read(self):
        """Чтение значения из памяти: A=13, B=41, C=726."""
        self.assert_fields(
            [{"read": {"reg": 41, "addr": 726}}],
            (("A", 13), ("B", 41), ("C", 726)),
        )

    def test_write(self):
        """Запись значения в память: A=22, B=36, C=85."""
        self.assert_fields(
            [{"write": {"ptr": 36, "src": 85}}],
            (("A", 22), ("B", 36), ("C", 85)),
        )

    def test_sqrt(self):
        """Унарная операция sqrt(): A=23, B=48, C=8."""
        self.assert_fields(
            [{"sqrt": {"ptr": 48, "src": 8}}],
            (("A", 23), ("B", 48), ("C", 8)),
        )


class SpecProgramTest(unittest.TestCase):
    """Проверка файла examples/spec_tests.yaml со всеми тестами."""

    def test_all_commands_in_order(self):
        """Файл содержит все четыре тестовые команды по порядку."""
        instructions = assemble_file(SPEC_PROGRAM)
        self.assertEqual(
            [instruction.format() for instruction in instructions],
            [
                "A=7, B=575, C=71",
                "A=13, B=41, C=726",
                "A=22, B=36, C=85",
                "A=23, B=48, C=8",
            ],
        )

    def test_value_by_label(self):
        """Значение поля можно получить по его имени."""
        instruction = assemble_file(SPEC_PROGRAM)[0]
        self.assertEqual(instruction.value("B"), 575)


if __name__ == "__main__":
    unittest.main()
