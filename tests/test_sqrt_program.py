"""Тест этапа 4: программа вычисляет sqrt() и сохраняет результат."""

import io
import os
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree

from uvm.assembler import assemble_file
from uvm.cli import main as assembler_main
from uvm.interpreter_cli import EXIT_OK, main as interpreter_main
from uvm.machine import decode_program, encode_program
from uvm.vm import Machine

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
SQRT_PROGRAM = os.path.join(EXAMPLES_DIR, "sqrt_test.yaml")

NUMBERS = [0, 1, 2, 4, 10, 16, 99, 144, 1000000, 4294967295]
ROOTS = [0, 1, 1, 2, 3, 4, 9, 12, 1000, 65535]
NUMBERS_FIRST = 0
ROOTS_FIRST = 10


class SqrtProgramTest(unittest.TestCase):
    """Программа examples/sqrt_test.yaml в интерпретаторе."""

    def setUp(self):
        """Выполнить программу через машинный код."""
        code = encode_program(assemble_file(SQRT_PROGRAM))
        self.machine = Machine(decode_program(code))
        self.machine.run()

    def test_numbers_are_stored(self):
        """Исходные числа записаны по адресам 0..9."""
        end = NUMBERS_FIRST + len(NUMBERS)
        self.assertEqual(self.machine.data[NUMBERS_FIRST:end], NUMBERS)

    def test_roots_are_stored(self):
        """Результаты sqrt() лежат по адресам 10..19."""
        end = ROOTS_FIRST + len(ROOTS)
        self.assertEqual(self.machine.data[ROOTS_FIRST:end], ROOTS)

    def test_roots_are_correct(self):
        """Для каждого числа r*r <= n < (r+1)*(r+1)."""
        for number, root in zip(NUMBERS, ROOTS):
            self.assertLessEqual(root * root, number)
            self.assertLess(number, (root + 1) * (root + 1))

    def test_all_commands_executed(self):
        """Выполнены все 50 команд программы."""
        self.assertEqual(self.machine.counter, len(self.machine.code))


class SqrtDumpTest(unittest.TestCase):
    """Полная цепочка: ассемблер, интерпретатор, XML-дамп."""

    def test_dump_contains_roots(self):
        """Дамп 0..19 содержит числа и их квадратные корни."""
        with tempfile.TemporaryDirectory() as folder:
            binary = os.path.join(folder, "program.bin")
            dump = os.path.join(folder, "dump.xml")
            assembler_main(
                [SQRT_PROGRAM, binary], io.StringIO(), io.StringIO()
            )
            code = interpreter_main(
                [binary, dump, "--range", "0", "19"],
                io.StringIO(),
                io.StringIO(),
            )
            root = ElementTree.parse(dump).getroot()
            cells = [int(cell.text) for cell in root.iter("cell")]
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(cells, NUMBERS + ROOTS)


if __name__ == "__main__":
    unittest.main()
