"""Тесты модели УВМ: память, регистры и выполнение команд."""

import unittest

from uvm.assembler import translate
from uvm.errors import InterpreterError
from uvm.spec import DATA_MEMORY_SIZE, REGISTER_COUNT
from uvm.vm import Machine


def make_machine(program):
    """Создать УВМ с программой из списка записей YAML."""
    return Machine(translate(program))


class MemoryModelTest(unittest.TestCase):
    """Устройство памяти УВМ."""

    def test_initial_state(self):
        """Память данных и регистры сначала нулевые."""
        machine = make_machine([{"read": {"reg": 0, "addr": 0}}])
        self.assertEqual(len(machine.data), DATA_MEMORY_SIZE)
        self.assertEqual(len(machine.registers), REGISTER_COUNT)
        self.assertEqual(set(machine.data), {0})
        self.assertEqual(set(machine.registers), {0})

    def test_code_and_data_are_separate(self):
        """Память команд не входит в память данных."""
        machine = make_machine([{"load_const": {"value": 7, "reg": 1}}])
        self.assertIsNot(machine.code, machine.data)
        self.assertEqual(len(machine.code), 1)
        self.assertEqual(len(machine.data), DATA_MEMORY_SIZE)

    def test_writing_data_does_not_change_code(self):
        """Запись в память данных не меняет память команд."""
        program = [
            {"load_const": {"value": 5, "reg": 1}},
            {"load_const": {"value": 0, "reg": 2}},
            {"write": {"ptr": 2, "src": 1}},
        ]
        machine = make_machine(program)
        code_before = list(machine.code)
        machine.run()
        self.assertEqual(machine.code, code_before)
        self.assertEqual(machine.data[0], 5)


class ExecuteTest(unittest.TestCase):
    """Выполнение отдельных команд."""

    def test_load_const(self):
        """Загрузка константы кладёт значение в регистр C."""
        machine = make_machine([{"load_const": {"value": 575, "reg": 71}}])
        machine.run()
        self.assertEqual(machine.registers[71], 575)

    def test_read(self):
        """Чтение кладёт значение из памяти по адресу C в регистр B."""
        machine = make_machine([{"read": {"reg": 41, "addr": 726}}])
        machine.data[726] = 99
        machine.run()
        self.assertEqual(machine.registers[41], 99)

    def test_write(self):
        """Запись кладёт регистр C в память по адресу из регистра B."""
        program = [
            {"load_const": {"value": 123, "reg": 36}},
            {"load_const": {"value": 85, "reg": 7}},
            {"write": {"ptr": 36, "src": 7}},
        ]
        machine = make_machine(program)
        machine.run()
        self.assertEqual(machine.data[123], 85)

    def test_write_to_last_address(self):
        """Запись по последнему адресу памяти данных допустима."""
        program = [
            {"load_const": {"value": DATA_MEMORY_SIZE - 1, "reg": 1}},
            {"load_const": {"value": 8, "reg": 2}},
            {"write": {"ptr": 1, "src": 2}},
        ]
        machine = make_machine(program)
        machine.run()
        self.assertEqual(machine.data[DATA_MEMORY_SIZE - 1], 8)

    def test_write_out_of_memory(self):
        """Адрес за пределами памяти данных — ошибка выполнения."""
        program = [
            {"load_const": {"value": DATA_MEMORY_SIZE, "reg": 1}},
            {"write": {"ptr": 1, "src": 2}},
        ]
        machine = make_machine(program)
        with self.assertRaises(InterpreterError) as context:
            machine.run()
        self.assertIn("команда 2", str(context.exception))

    def test_sqrt_is_not_supported_yet(self):
        """Команда sqrt() появится на этапе 4."""
        machine = make_machine([{"sqrt": {"ptr": 1, "src": 2}}])
        with self.assertRaises(InterpreterError) as context:
            machine.run()
        self.assertIn("sqrt()", str(context.exception))


class RunTest(unittest.TestCase):
    """Цикл выполнения."""

    def test_run_returns_number_of_commands(self):
        """run() возвращает число выполненных команд."""
        program = [
            {"load_const": {"value": 1, "reg": 1}},
            {"load_const": {"value": 2, "reg": 2}},
        ]
        machine = make_machine(program)
        self.assertEqual(machine.run(), len(program))
        self.assertEqual(machine.counter, len(program))

    def test_empty_program(self):
        """Пустая программа ничего не меняет."""
        machine = Machine([])
        self.assertEqual(machine.run(), 0)

    def test_step_executes_one_command(self):
        """step() выполняет ровно одну команду."""
        program = [
            {"load_const": {"value": 1, "reg": 1}},
            {"load_const": {"value": 2, "reg": 2}},
        ]
        machine = make_machine(program)
        machine.step()
        self.assertEqual(machine.registers[1], 1)
        self.assertEqual(machine.registers[2], 0)


if __name__ == "__main__":
    unittest.main()
