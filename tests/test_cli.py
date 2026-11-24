"""Тесты интерфейса командной строки."""

import io
import os
import tempfile
import unittest

from uvm.cli import EXIT_ASSEMBLER_ERROR, EXIT_OK, main

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
SPEC_PROGRAM = os.path.join(EXAMPLES_DIR, "spec_tests.yaml")
INVALID_PROGRAM = os.path.join(EXAMPLES_DIR, "invalid_range.yaml")

EXPECTED_LINES = [
    "0xE7, 0x47, 0x00, 0x00, 0xE0, 0x08",
    "0x2D, 0x65, 0x2D, 0x00, 0x00, 0x00",
    "0x96, 0x54, 0x05, 0x00, 0x00, 0x00",
    "0x17, 0x86, 0x00, 0x00, 0x00, 0x00",
]
SIZE_LINE = "Размер двоичного файла: 24 байт"


class CliTest(unittest.TestCase):
    """Запуск ассемблера через main()."""

    def setUp(self):
        """Создать временный каталог для двоичных файлов."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.output = os.path.join(folder.name, "result.bin")

    def run_main(self, argv):
        """Запустить main и вернуть код, stdout и stderr."""
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(argv, stdout, stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_test_mode_prints_bytes_and_size(self):
        """В режиме тестирования выводятся байты и размер файла."""
        code, out, err = self.run_main([SPEC_PROGRAM, self.output, "--test"])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(err, "")
        self.assertEqual(out.splitlines(), EXPECTED_LINES + [SIZE_LINE])

    def test_short_test_option(self):
        """Режим тестирования включается и короткой опцией -t."""
        code, out, _ = self.run_main([SPEC_PROGRAM, self.output, "-t"])
        self.assertEqual(code, EXIT_OK)
        self.assertTrue(out.startswith(EXPECTED_LINES[0]))

    def test_normal_mode_prints_only_size(self):
        """Без режима тестирования выводится только размер файла."""
        code, out, _ = self.run_main([SPEC_PROGRAM, self.output])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(out, SIZE_LINE + "\n")

    def test_binary_file_content(self):
        """В двоичный файл записаны байты всех тестовых команд."""
        self.run_main([SPEC_PROGRAM, self.output])
        with open(self.output, "rb") as stream:
            content = stream.read()
        self.assertEqual(
            content,
            bytes(
                [0xE7, 0x47, 0x00, 0x00, 0xE0, 0x08]
                + [0x2D, 0x65, 0x2D, 0x00, 0x00, 0x00]
                + [0x96, 0x54, 0x05, 0x00, 0x00, 0x00]
                + [0x17, 0x86, 0x00, 0x00, 0x00, 0x00]
            ),
        )

    def test_binary_file_size_matches_report(self):
        """Размер файла на диске равен выведенному размеру."""
        self.run_main([SPEC_PROGRAM, self.output])
        self.assertEqual(os.path.getsize(self.output), 24)

    def test_error_goes_to_stderr(self):
        """Ошибка выводится в stderr, файл не создаётся."""
        code, out, err = self.run_main(
            [INVALID_PROGRAM, self.output, "-t"]
        )
        self.assertEqual(code, EXIT_ASSEMBLER_ERROR)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("ошибка: команда 1"))
        self.assertFalse(os.path.exists(self.output))

    def test_missing_source_file(self):
        """Несуществующий исходный файл — ошибка, а не трассировка."""
        code, _, err = self.run_main(["nope.yaml", self.output])
        self.assertEqual(code, EXIT_ASSEMBLER_ERROR)
        self.assertIn("не удалось прочитать файл", err)

    def test_unwritable_output(self):
        """Недоступный путь результата даёт понятную ошибку."""
        bad_path = os.path.join(os.path.dirname(self.output), "no", "a.bin")
        code, _, err = self.run_main([SPEC_PROGRAM, bad_path])
        self.assertEqual(code, EXIT_ASSEMBLER_ERROR)
        self.assertIn("не удалось записать файл", err)


if __name__ == "__main__":
    unittest.main()
