from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLCDNumber, QComboBox

from envs.gui_env.src.utils.utils import SignalHandler

POSSIBLE_OPERANDS_BASE_10 = [i for i in range(5)]
POSSIBLE_OPERANDS_BASE_2 = [bin(i) for i in range(5)]
POSSIBLE_OPERANDS_BASE_16 = [hex(i) for i in range(5)]

NUMERAL_SYSTEMS = ["Base 10", "Base 2", "Base 16"]


class Calculator:

    def __init__(self, calculator_output: QLCDNumber, first_operand_combobox: QComboBox,
                 second_operand_combobox: QComboBox, math_operator_combobox: QComboBox):
        self.calculator_output = calculator_output
        self.first_operand_combobox = first_operand_combobox
        self.second_operand_combobox = second_operand_combobox
        self.math_operator_combobox = math_operator_combobox
        self.numeral_system = "Base 10"

        self.addition_operator = True
        self.subtraction_operator = True
        self.multiplication_operator = False
        self.division_operator = False

        self._initialize()

        self.signal_handler = SignalHandler()

    def _initialize(self):
        self._initialize_operands()
        self._initialize_operators()

    def _initialize_operands(self):
        self.first_operand_combobox.clear()
        self.second_operand_combobox.clear()

        possible_operands = None
        if self.numeral_system == "Base 10":
            possible_operands = POSSIBLE_OPERANDS_BASE_10
        elif self.numeral_system == "Base 2":
            possible_operands = POSSIBLE_OPERANDS_BASE_2
        elif self.numeral_system == "Base 16":
            possible_operands = POSSIBLE_OPERANDS_BASE_16
        assert possible_operands

        self.first_operand_combobox.addItems(str(i) for i in possible_operands)
        self.second_operand_combobox.addItems(str(i) for i in possible_operands)

    def _initialize_operators(self):
        self.math_operator_combobox.clear()

        operators = []
        if self.addition_operator:
            operators.append("+")
        if self.subtraction_operator:
            operators.append("-")
        if self.multiplication_operator:
            operators.append("*")
        if self.division_operator:
            operators.append("/")

        if not operators:
            # TODO implement asking dialog for one operator that shall be activated
            self.signal_handler.all_operators_deselected.emit()

        self.math_operator_combobox.addItems(operators)

    @Slot(bool)
    def change_addition_operator(self, checked: bool):
        if checked:
            self.addition_operator = True
        else:
            self.addition_operator = False
        self._initialize_operators()

    @Slot(bool)
    def change_subtraction_operator(self, checked: bool):
        if checked:
            self.subtraction_operator = True
        else:
            self.subtraction_operator = False
        self._initialize_operators()

    @Slot(bool)
    def change_multiplication_operator(self, checked: bool):
        if checked:
            self.multiplication_operator = True
        else:
            self.multiplication_operator = False
        self._initialize_operators()

    @Slot(bool)
    def change_division_operator(self, checked: bool):
        if checked:
            self.division_operator = True
        else:
            self.division_operator = False
        self._initialize_operators()

    @Slot(str)
    def change_numeral_system(self, numeral_system: str):
        if numeral_system == "Base 10":
            self.numeral_system = "Base 10"
        elif numeral_system == "Base 2":
            self.numeral_system = "Base 2"
        elif numeral_system == "Base 16":
            self.numeral_system = "Base 16"

        assert self.numeral_system in NUMERAL_SYSTEMS

        self._initialize_operands()

    def calculate(self):
        first_operand_txt = self.first_operand_combobox.currentText()
        second_operand_txt = self.second_operand_combobox.currentText()

        first_operand, second_operand = None, None

        if first_operand_txt == "0":
            first_operand = "0"
        elif first_operand_txt == "1":
            first_operand = "1"
        elif first_operand_txt == "2":
            first_operand = "2"
        elif first_operand_txt == "3":
            first_operand = "3"
        elif first_operand_txt == "4":
            first_operand = "4"

        if second_operand_txt == "0":
            second_operand = "0"
        elif second_operand_txt == "1":
            second_operand = "1"
        elif second_operand_txt == "2":
            second_operand = "2"
        elif second_operand_txt == "3":
            second_operand = "3"
        elif second_operand_txt == "4":
            second_operand = "4"

        assert first_operand is not None
        assert second_operand is not None

        a, b = None, None
        if self.numeral_system == "Base 10":
            a = int(first_operand)
            b = int(second_operand)
        elif self.numeral_system == "Base 2":
            a = int(first_operand, 2)
            b = int(second_operand, 2)
        elif self.numeral_system == "Base 16":
            a = int(first_operand, 16)
            b = int(second_operand, 16)
        assert a is not None
        assert b is not None

        operator = self.math_operator_combobox.currentText()

        output = None
        if operator == "+":
            output = a + b
        elif operator == "-":
            output = a - b
        elif operator == "*":
            output = a * b
        elif operator == "/":
            try:
                output = a / b
            except ZeroDivisionError:
                # TODO implement warning dialog
                self.signal_handler.division_by_zero_occured.emit()
                return
        assert output is not None

        converted_output = None
        if self.numeral_system == "Base 10":
            converted_output = output
        elif self.numeral_system == "Base 2":
            converted_output = bin(int(output))
        elif self.numeral_system == "Base 16":
            converted_output = hex(int(output))
        assert converted_output is not None

        self.calculator_output.display(converted_output)
