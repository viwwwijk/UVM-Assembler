"""Тест этапа 3: тестовая программа копирует массив между адресами."""

import os
import unittest

from uvm.assembler import assemble_file
from uvm.machine import decode_program, encode_program
from uvm.vm import Machine

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
COPY_PROGRAM = os.path.join(EXAMPLES_DIR, "copy_array.yaml")

ARRAY = [11, 22, 33, 44, 55]
SOURCE_FIRST = 10
TARGET_FIRST = 20


def run_copy_program():
    """Ассемблировать программу, декодировать и выполнить её."""
    code = encode_program(assemble_file(COPY_PROGRAM))
    machine = Machine(decode_program(code))
    machine.run()
    return machine


class CopyArrayTest(unittest.TestCase):
    """Копирование массива с адреса 10 на адрес 20."""

    def setUp(self):
        """Выполнить программу копирования."""
        self.machine = run_copy_program()

    def test_source_array_is_written(self):
        """Исходный массив записан по адресам 10..14."""
        end = SOURCE_FIRST + len(ARRAY)
        self.assertEqual(self.machine.data[SOURCE_FIRST:end], ARRAY)

    def test_target_array_equals_source(self):
        """По адресам 20..24 лежит копия массива."""
        end = TARGET_FIRST + len(ARRAY)
        self.assertEqual(self.machine.data[TARGET_FIRST:end], ARRAY)

    def test_gap_between_arrays_is_empty(self):
        """Между массивами память не тронута."""
        gap = self.machine.data[SOURCE_FIRST + len(ARRAY):TARGET_FIRST]
        self.assertEqual(set(gap), {0})

    def test_all_commands_executed(self):
        """Выполнены все 30 команд программы."""
        self.assertEqual(self.machine.counter, len(self.machine.code))


if __name__ == "__main__":
    unittest.main()
