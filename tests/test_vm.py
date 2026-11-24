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


class SqrtTest(unittest.TestCase):
    """Выполнение команды sqrt()."""

    def sqrt_of(self, value):
        """Выполнить sqrt() над value и вернуть результат из памяти."""
        program = [
            {"load_const": {"value": value, "reg": 1}},
            {"load_const": {"value": 500, "reg": 2}},
            {"sqrt": {"ptr": 2, "src": 1}},
        ]
        machine = make_machine(program)
        machine.run()
        return machine.data[500]

    def test_perfect_squares(self):
        """Для точных квадратов результат — точный корень."""
        for root in (0, 1, 2, 12, 1000, 65535):
            self.assertEqual(self.sqrt_of(root * root), root)

    def test_integer_part(self):
        """Для остальных чисел результат — целая часть корня."""
        self.assertEqual(self.sqrt_of(2), 1)
        self.assertEqual(self.sqrt_of(8), 2)
        self.assertEqual(self.sqrt_of(99), 9)
        self.assertEqual(self.sqrt_of(65535 * 65535 + 1), 65535)

    def test_maximum_constant(self):
        """Наибольшая константа 4294967295 даёт 65535."""
        self.assertEqual(self.sqrt_of(4294967295), 65535)

    def test_spec_command(self):
        """Команда из спецификации: ptr=48, src=8."""
        program = [
            {"load_const": {"value": 144, "reg": 8}},
            {"load_const": {"value": 77, "reg": 48}},
            {"sqrt": {"ptr": 48, "src": 8}},
        ]
        machine = make_machine(program)
        machine.run()
        self.assertEqual(machine.data[77], 12)

    def test_argument_register_is_not_changed(self):
        """sqrt() не меняет регистры, результат только в памяти."""
        program = [
            {"load_const": {"value": 81, "reg": 1}},
            {"load_const": {"value": 3, "reg": 2}},
            {"sqrt": {"ptr": 2, "src": 1}},
        ]
        machine = make_machine(program)
        machine.run()
        self.assertEqual(machine.registers[1], 81)
        self.assertEqual(machine.registers[2], 3)
        self.assertEqual(machine.data[3], 9)

    def test_sqrt_of_memory_value(self):
        """Корень можно взять от значения, прочитанного из памяти."""
        program = [
            {"read": {"reg": 1, "addr": 7}},
            {"load_const": {"value": 8, "reg": 2}},
            {"sqrt": {"ptr": 2, "src": 1}},
        ]
        machine = make_machine(program)
        machine.data[7] = 49
        machine.run()
        self.assertEqual(machine.data[8], 7)

    def test_address_out_of_memory(self):
        """Адрес результата за пределами памяти — ошибка выполнения."""
        program = [
            {"load_const": {"value": DATA_MEMORY_SIZE, "reg": 1}},
            {"sqrt": {"ptr": 1, "src": 2}},
        ]
        machine = make_machine(program)
        with self.assertRaises(InterpreterError) as context:
            machine.run()
        self.assertIn("команда 2", str(context.exception))


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
