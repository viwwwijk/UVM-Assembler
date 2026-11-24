"""Тесты этапа 5: sqrt() над вектором длины 10 и три примера программ."""

import io
import math
import os
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree

from uvm.cli import main as assembler_main
from uvm.interpreter_cli import EXIT_OK, main as interpreter_main

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
VECTOR_LENGTH = 10

TASK = (
    "task_sqrt_vector.yaml",
    50,
    60,
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
)
EXAMPLES = [
    (
        "example_small_numbers.yaml",
        0,
        10,
        [0, 1, 2, 3, 5, 7, 8, 10, 15, 20],
        [0, 1, 1, 1, 2, 2, 2, 3, 3, 4],
    ),
    (
        "example_large_numbers.yaml",
        0,
        10,
        [
            1000000, 123456789, 4294967295, 65536, 65535,
            999999, 2147483647, 3, 17, 1024,
        ],
        [1000, 11111, 65535, 256, 255, 999, 46340, 1, 4, 32],
    ),
    (
        "example_powers_of_two.yaml",
        0,
        10,
        [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
        [1, 1, 2, 2, 4, 5, 8, 11, 16, 22],
    ),
]


def run_program(name, first, last):
    """Ассемблировать и выполнить программу, вернуть ячейки дампа."""
    path = os.path.join(EXAMPLES_DIR, name)
    with tempfile.TemporaryDirectory() as folder:
        binary = os.path.join(folder, "program.bin")
        dump = os.path.join(folder, "dump.xml")
        assembler_main([path, binary], io.StringIO(), io.StringIO())
        code = interpreter_main(
            [binary, dump, "--range", str(first), str(last)],
            io.StringIO(),
            io.StringIO(),
        )
        root = ElementTree.parse(dump).getroot()
        cells = {
            int(cell.get("address")): int(cell.text)
            for cell in root.iter("cell")
        }
    return code, cells


class VectorProgramsTest(unittest.TestCase):
    """Проверка дампа памяти для всех программ этапа 5."""

    def assert_program(self, program):
        """Проверить исходный вектор, результат и отсутствие лишнего."""
        name, source, target, numbers, roots = program
        last = target + VECTOR_LENGTH - 1
        code, cells = run_program(name, source, last)
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(sorted(cells), list(range(source, last + 1)))
        source_vector = [cells[source + i] for i in range(VECTOR_LENGTH)]
        target_vector = [cells[target + i] for i in range(VECTOR_LENGTH)]
        self.assertEqual(source_vector, numbers)
        self.assertEqual(target_vector, roots)

    def test_task_vector(self):
        """Тестовая задача: sqrt() над вектором 1, 4, ..., 100."""
        self.assert_program(TASK)

    def test_examples(self):
        """Три примера с разными данными."""
        for program in EXAMPLES:
            with self.subTest(program=program[0]):
                self.assert_program(program)


class VectorDataTest(unittest.TestCase):
    """Проверка самих данных: ожидаемые корни посчитаны верно."""

    def test_expected_roots_are_integer_parts(self):
        """Для каждого числа r*r <= n < (r+1)*(r+1)."""
        for name, _, _, numbers, roots in [TASK] + EXAMPLES:
            with self.subTest(program=name):
                self.assertEqual(len(numbers), VECTOR_LENGTH)
                self.assertEqual(roots, [math.isqrt(n) for n in numbers])

    def test_examples_use_different_data(self):
        """Векторы всех программ различаются."""
        vectors = [tuple(item[3]) for item in [TASK] + EXAMPLES]
        self.assertEqual(len(set(vectors)), len(vectors))


if __name__ == "__main__":
    unittest.main()
