"""Тесты интерфейса командной строки."""

import io
import os
import unittest

from uvm.cli import EXIT_ASSEMBLER_ERROR, EXIT_OK, main

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
SPEC_PROGRAM = os.path.join(EXAMPLES_DIR, "spec_tests.yaml")
INVALID_PROGRAM = os.path.join(EXAMPLES_DIR, "invalid_range.yaml")
OUTPUT_PATH = "result.bin"


class CliTest(unittest.TestCase):
    """Запуск ассемблера через main()."""

    def run_main(self, argv):
        """Запустить main и вернуть код, stdout и stderr."""
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(argv, stdout, stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_test_mode_prints_fields(self):
        """В режиме тестирования выводятся поля и значения команд."""
        code, out, err = self.run_main(
            [SPEC_PROGRAM, OUTPUT_PATH, "--test"]
        )
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(err, "")
        self.assertEqual(
            out.splitlines(),
            [
                "A=7, B=575, C=71",
                "A=13, B=41, C=726",
                "A=22, B=36, C=85",
                "A=23, B=48, C=8",
            ],
        )

    def test_short_test_option(self):
        """Режим тестирования включается и короткой опцией -t."""
        code, out, _ = self.run_main([SPEC_PROGRAM, OUTPUT_PATH, "-t"])
        self.assertEqual(code, EXIT_OK)
        self.assertTrue(out.startswith("A=7, B=575, C=71"))

    def test_normal_mode_reports_count(self):
        """Без режима тестирования выводится число команд."""
        code, out, _ = self.run_main([SPEC_PROGRAM, OUTPUT_PATH])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(out, "Ассемблировано команд: 4\n")

    def test_normal_mode_does_not_create_output(self):
        """На этапе 1 двоичный файл не создаётся."""
        self.run_main([SPEC_PROGRAM, OUTPUT_PATH])
        self.assertFalse(os.path.exists(OUTPUT_PATH))

    def test_error_goes_to_stderr(self):
        """Ошибка выводится в stderr, код завершения — 1."""
        code, out, err = self.run_main([INVALID_PROGRAM, OUTPUT_PATH, "-t"])
        self.assertEqual(code, EXIT_ASSEMBLER_ERROR)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("ошибка: команда 1"))

    def test_missing_source_file(self):
        """Несуществующий исходный файл — ошибка, а не трассировка."""
        code, _, err = self.run_main(["nope.yaml", OUTPUT_PATH])
        self.assertEqual(code, EXIT_ASSEMBLER_ERROR)
        self.assertIn("не удалось прочитать файл", err)


if __name__ == "__main__":
    unittest.main()
