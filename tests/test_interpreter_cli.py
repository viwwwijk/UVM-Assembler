"""Тесты интерфейса командной строки интерпретатора."""

import argparse
import io
import os
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree

from uvm.cli import main as assembler_main
from uvm.interpreter_cli import (
    EXIT_ERROR,
    EXIT_OK,
    main,
    parse_address,
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
COPY_PROGRAM = os.path.join(EXAMPLES_DIR, "copy_array.yaml")


class InterpreterCliTest(unittest.TestCase):
    """Запуск интерпретатора через main()."""

    def setUp(self):
        """Создать временный каталог и собрать программу копирования."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.binary = os.path.join(folder.name, "program.bin")
        self.dump = os.path.join(folder.name, "dump.xml")
        assembler_main(
            [COPY_PROGRAM, self.binary], io.StringIO(), io.StringIO()
        )

    def run_main(self, argv):
        """Запустить main и вернуть код, stdout и stderr."""
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(argv, stdout, stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def read_cells(self):
        """Прочитать ячейки дампа в словарь «адрес: значение»."""
        root = ElementTree.parse(self.dump).getroot()
        return {
            int(cell.get("address")): int(cell.text)
            for cell in root.iter("cell")
        }

    def test_copy_array_dump(self):
        """Дамп 10..24 содержит исходный массив и его копию."""
        code, out, err = self.run_main(
            [self.binary, self.dump, "--range", "10", "24"]
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(err, "")
        self.assertIn("Выполнено команд: 30", out)
        cells = self.read_cells()
        self.assertEqual(sorted(cells), list(range(10, 25)))
        for offset in range(5):
            self.assertEqual(cells[10 + offset], cells[20 + offset])
        self.assertEqual(cells[14], 55)

    def test_short_option_and_hex(self):
        """Диапазон можно задать короткой опцией и в шестнадцатеричном виде."""
        code, _, _ = self.run_main(
            [self.binary, self.dump, "-r", "0xA", "0xC"]
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(sorted(self.read_cells()), [10, 11, 12])

    def test_range_is_required(self):
        """Без диапазона адресов программа завершается с кодом 2."""
        with self.assertRaises(SystemExit) as context:
            self.run_main([self.binary, self.dump])
        self.assertEqual(context.exception.code, 2)

    def test_bad_range(self):
        """Неверный диапазон — ошибка до выполнения программы."""
        code, _, err = self.run_main(
            [self.binary, self.dump, "--range", "5", "1"]
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("неверный диапазон", err)
        self.assertFalse(os.path.exists(self.dump))

    def test_missing_binary(self):
        """Несуществующий двоичный файл — понятная ошибка."""
        code, _, err = self.run_main(
            ["nope.bin", self.dump, "--range", "0", "1"]
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не удалось прочитать файл", err)

    def test_broken_binary(self):
        """Файл неверного размера отвергается."""
        with open(self.binary, "wb") as stream:
            stream.write(bytes(5))
        code, _, err = self.run_main(
            [self.binary, self.dump, "--range", "0", "1"]
        )
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не кратен", err)

    def test_empty_binary(self):
        """Пустая программа даёт дамп из нулей."""
        with open(self.binary, "wb"):
            pass
        code, out, _ = self.run_main(
            [self.binary, self.dump, "--range", "0", "2"]
        )
        self.assertEqual(code, EXIT_OK)
        self.assertIn("Выполнено команд: 0", out)
        self.assertEqual(set(self.read_cells().values()), {0})


class ParseAddressTest(unittest.TestCase):
    """Разбор адреса из командной строки."""

    def test_decimal_and_hex(self):
        """Принимаются десятичные и шестнадцатеричные числа."""
        self.assertEqual(parse_address("26"), 26)
        self.assertEqual(parse_address("0x1A"), 26)

    def test_not_a_number(self):
        """Нечисловое значение отвергается."""
        with self.assertRaises(argparse.ArgumentTypeError) as context:
            parse_address("abc")
        self.assertIn("не является целым числом", str(context.exception))


if __name__ == "__main__":
    unittest.main()
