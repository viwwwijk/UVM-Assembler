"""Модель УВМ: память команд, память данных, регистры и цикл выполнения.

Память команд и память данных разделены: программа хранится в списке
команд и не доступна командам чтения и записи, а данные лежат в
отдельном массиве ``DATA_MEMORY_SIZE`` ячеек.
"""

from typing import List

from uvm.errors import InterpreterError
from uvm.intermediate import Instruction
from uvm.spec import DATA_MEMORY_SIZE, REGISTER_COUNT


class Machine:
    """Учебная виртуальная машина.

    Attributes:
        code: память команд.
        data: память данных.
        registers: регистры.
        counter: номер следующей команды в памяти команд.
    """

    def __init__(self, program: List[Instruction]) -> None:
        """Загрузить программу в память команд, обнулить данные."""
        self.code = list(program)
        self.data = [0] * DATA_MEMORY_SIZE
        self.registers = [0] * REGISTER_COUNT
        self.counter = 0

    def run(self) -> int:
        """Выполнить программу до конца, вернуть число команд."""
        while self.counter < len(self.code):
            self.step()
        return len(self.code)

    def step(self) -> None:
        """Выполнить одну команду из памяти команд."""
        instruction = self.code[self.counter]
        self.counter += 1
        handler = getattr(self, f"execute_{instruction.name}")
        handler(instruction)

    def execute_load_const(self, instruction: Instruction) -> None:
        """Загрузка константы: регистр C = константа B."""
        self.registers[instruction.value("C")] = instruction.value("B")

    def execute_read(self, instruction: Instruction) -> None:
        """Чтение из памяти: регистр B = память[C]."""
        address = instruction.value("C")
        self.registers[instruction.value("B")] = self.data[address]

    def execute_write(self, instruction: Instruction) -> None:
        """Запись в память: память[регистр B] = регистр C."""
        address = self.registers[instruction.value("B")]
        if address >= DATA_MEMORY_SIZE:
            raise InterpreterError(
                f"команда {self.counter}: адрес {address} вне памяти "
                f"данных (размер {DATA_MEMORY_SIZE} ячеек)"
            )
        self.data[address] = self.registers[instruction.value("C")]

    def execute_sqrt(self, instruction: Instruction) -> None:
        """Команда sqrt() будет реализована на этапе 4."""
        raise InterpreterError(
            f"команда {self.counter}: sqrt() пока не поддерживается"
        )
