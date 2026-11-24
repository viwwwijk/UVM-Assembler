"""Тесты дампа памяти в формате XML."""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree

from uvm.dump import check_range, dump_xml, write_dump
from uvm.errors import InterpreterError
from uvm.spec import DATA_MEMORY_SIZE


class DumpXmlTest(unittest.TestCase):
    """Содержимое XML-дампа."""

    def setUp(self):
        """Подготовить память с известными значениями."""
        self.data = [0] * DATA_MEMORY_SIZE
        self.data[3] = 30
        self.data[4] = 40

    def test_exact_text(self):
        """Дамп состоит из заголовка, корня и ячеек."""
        text = dump_xml(self.data, 3, 5)
        self.assertEqual(
            text,
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<memory first="3" last="5">\n'
            '  <cell address="3">30</cell>\n'
            '  <cell address="4">40</cell>\n'
            '  <cell address="5">0</cell>\n'
            "</memory>\n",
        )

    def test_xml_is_well_formed(self):
        """Дамп разбирается XML-парсером, значения совпадают."""
        root = ElementTree.fromstring(dump_xml(self.data, 3, 4))
        cells = {
            cell.get("address"): cell.text for cell in root.iter("cell")
        }
        self.assertEqual(root.tag, "memory")
        self.assertEqual(cells, {"3": "30", "4": "40"})

    def test_single_cell(self):
        """Диапазон из одного адреса даёт одну ячейку."""
        root = ElementTree.fromstring(dump_xml(self.data, 4, 4))
        self.assertEqual(len(list(root.iter("cell"))), 1)

    def test_last_address(self):
        """Последний адрес памяти можно выгрузить."""
        last = DATA_MEMORY_SIZE - 1
        root = ElementTree.fromstring(dump_xml(self.data, last, last))
        self.assertEqual(root.find("cell").get("address"), str(last))


class CheckRangeTest(unittest.TestCase):
    """Проверка диапазона адресов."""

    def assert_bad(self, first, last):
        """Проверить, что диапазон отвергается."""
        with self.assertRaises(InterpreterError) as context:
            check_range(first, last)
        self.assertIn("неверный диапазон", str(context.exception))

    def test_negative_first(self):
        """Отрицательный адрес не допускается."""
        self.assert_bad(-1, 5)

    def test_first_greater_than_last(self):
        """Первый адрес не может быть больше последнего."""
        self.assert_bad(6, 5)

    def test_last_out_of_memory(self):
        """Последний адрес должен лежать в памяти данных."""
        self.assert_bad(0, DATA_MEMORY_SIZE)


class WriteDumpTest(unittest.TestCase):
    """Запись дампа в файл."""

    def test_write_and_read_back(self):
        """Файл содержит записанный текст в UTF-8."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "dump.xml")
            write_dump(path, "<memory/>\n")
            with open(path, encoding="utf-8") as stream:
                self.assertEqual(stream.read(), "<memory/>\n")

    def test_unwritable_path(self):
        """Недоступный путь даёт понятную ошибку."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "no", "dump.xml")
            with self.assertRaises(InterpreterError) as context:
                write_dump(path, "text")
        self.assertIn("не удалось записать файл", str(context.exception))


if __name__ == "__main__":
    unittest.main()
