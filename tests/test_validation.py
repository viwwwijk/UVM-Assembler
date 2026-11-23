"""Тесты проверки программы: все ошибки должны быть понятными."""

import os
import tempfile
import unittest

from uvm.assembler import load_source, translate
from uvm.errors import AssemblerError
from uvm.spec import COMMANDS


class TranslateErrorsTest(unittest.TestCase):
    """Ошибки в структуре и значениях команд."""

    def assert_error(self, program, text):
        """Проверить, что трансляция падает с ожидаемым сообщением."""
        with self.assertRaises(AssemblerError) as context:
            translate(program)
        self.assertIn(text, str(context.exception))

    def test_program_is_not_a_list(self):
        """Программа должна быть списком."""
        self.assert_error({"sqrt": {}}, "непустым списком")

    def test_program_is_empty(self):
        """Пустая программа не допускается."""
        self.assert_error([], "непустым списком")

    def test_program_is_none(self):
        """Пустой файл YAML даёт None и тоже ошибку."""
        self.assert_error(None, "непустым списком")

    def test_command_is_not_a_mapping(self):
        """Команда должна быть записью «имя: операнды»."""
        self.assert_error(["sqrt"], "команда 1")

    def test_two_commands_in_one_item(self):
        """В одной записи не может быть двух команд."""
        item = {"sqrt": {"ptr": 1, "src": 2}, "read": {"reg": 1, "addr": 2}}
        self.assert_error([item], "ожидается запись")

    def test_operands_are_not_a_mapping(self):
        """Операнды должны быть заданы словарём."""
        self.assert_error([{"sqrt": 5}], "в виде «ключ: значение»")

    def test_unknown_command(self):
        """Неизвестная команда: в сообщении перечислены допустимые."""
        self.assert_error([{"jump": {}}], "неизвестная команда «jump»")
        self.assert_error([{"jump": {}}], ", ".join(COMMANDS))

    def test_missing_operand(self):
        """Не задан обязательный операнд."""
        self.assert_error([{"read": {"reg": 1}}], "не задан операнд «addr»")

    def test_extra_operand(self):
        """Лишний операнд."""
        program = [{"sqrt": {"ptr": 1, "src": 2, "dst": 3}}]
        self.assert_error(program, "неизвестный операнд «dst»")

    def test_value_is_not_integer(self):
        """Операнд должен быть целым числом."""
        program = [{"load_const": {"value": "много", "reg": 1}}]
        self.assert_error(program, "должен быть целым числом")

    def test_value_is_float(self):
        """Дробное число не допускается."""
        program = [{"load_const": {"value": 1.5, "reg": 1}}]
        self.assert_error(program, "должен быть целым числом")

    def test_value_is_boolean(self):
        """Логическое значение не считается числом."""
        program = [{"load_const": {"value": True, "reg": 1}}]
        self.assert_error(program, "должен быть целым числом")

    def test_value_is_negative(self):
        """Отрицательное значение не помещается в поле."""
        program = [{"load_const": {"value": -1, "reg": 1}}]
        self.assert_error(program, "допустимы значения от 0 до")

    def test_register_out_of_range(self):
        """Номер регистра ограничен семью битами."""
        program = [{"load_const": {"value": 1, "reg": 128}}]
        self.assert_error(program, "от 0 до 127")

    def test_address_out_of_range(self):
        """Адрес памяти ограничен двадцатью битами."""
        program = [{"read": {"reg": 1, "addr": 1048576}}]
        self.assert_error(program, "от 0 до 1048575")

    def test_error_names_the_command_number(self):
        """В сообщении указан номер команды с ошибкой."""
        program = [
            {"load_const": {"value": 1, "reg": 1}},
            {"read": {"reg": 1}},
        ]
        self.assert_error(program, "команда 2")


class BoundaryValuesTest(unittest.TestCase):
    """Крайние допустимые значения полей."""

    def test_maximum_values(self):
        """Наибольшие значения полей принимаются."""
        program = [
            {"load_const": {"value": 4294967295, "reg": 127}},
            {"read": {"reg": 127, "addr": 1048575}},
        ]
        instructions = translate(program)
        self.assertEqual(instructions[0].value("B"), 4294967295)
        self.assertEqual(instructions[1].value("C"), 1048575)

    def test_minimum_values(self):
        """Нулевые значения принимаются."""
        program = [{"sqrt": {"ptr": 0, "src": 0}}]
        self.assertEqual(translate(program)[0].format(), "A=23, B=0, C=0")


class LoadSourceTest(unittest.TestCase):
    """Чтение файла с программой."""

    def write_file(self, text):
        """Создать временный файл с текстом и вернуть его путь."""
        handle, path = tempfile.mkstemp(suffix=".yaml")
        self.addCleanup(os.remove, path)
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        return path

    def test_missing_file(self):
        """Несуществующий файл даёт понятную ошибку."""
        with self.assertRaises(AssemblerError) as context:
            load_source("no_such_file.yaml")
        self.assertIn("не удалось прочитать файл", str(context.exception))

    def test_broken_yaml(self):
        """Некорректный YAML даёт понятную ошибку."""
        path = self.write_file("- read: {reg: 1\n")
        with self.assertRaises(AssemblerError) as context:
            load_source(path)
        self.assertIn("ошибка YAML", str(context.exception))

    def test_comments_are_ignored(self):
        """Комментарии YAML допускаются в тексте программы."""
        path = self.write_file("\x23 комментарий\n- sqrt: {ptr: 1, src: 2}\n")
        self.assertEqual(
            load_source(path), [{"sqrt": {"ptr": 1, "src": 2}}]
        )


if __name__ == "__main__":
    unittest.main()
