"""Unit tests for app.utils."""

import unittest

from app.utils import (
    build_message,
    is_blank,
    is_exit_command,
    trim_history,
)


class TestIsExitCommand(unittest.TestCase):
    """Tests for is_exit_command()."""

    def test_recognizes_exit_variants(self) -> None:
        for word in ["exit", "EXIT", "  quit  ", "Bye", "q"]:
            with self.subTest(word=word):
                self.assertTrue(is_exit_command(word))

    def test_rejects_normal_message(self) -> None:
        self.assertFalse(is_exit_command("hello there"))


class TestIsBlank(unittest.TestCase):
    """Tests for is_blank()."""

    def test_empty_string_is_blank(self) -> None:
        self.assertTrue(is_blank(""))

    def test_whitespace_only_is_blank(self) -> None:
        self.assertTrue(is_blank("    \n\t"))

    def test_non_empty_is_not_blank(self) -> None:
        self.assertFalse(is_blank("hi"))


class TestBuildMessage(unittest.TestCase):
    """Tests for build_message()."""

    def test_builds_correct_dict(self) -> None:
        message = build_message("user", "hello")
        self.assertEqual(message, {"role": "user", "content": "hello"})


class TestTrimHistory(unittest.TestCase):
    """Tests for trim_history()."""

    def test_returns_same_list_when_under_limit(self) -> None:
        history = [build_message("user", "hi")]
        self.assertEqual(trim_history(history, 10), history)

    def test_trims_keeping_system_prompt(self) -> None:
        history = [build_message("system", "sys")] + [
            build_message("user", str(i)) for i in range(10)
        ]
        trimmed = trim_history(history, 5)
        self.assertEqual(trimmed[0]["role"], "system")
        self.assertEqual(len(trimmed), 5)
        # Should keep the most recent user messages.
        self.assertEqual(trimmed[-1]["content"], "9")

    def test_trims_without_system_prompt(self) -> None:
        history = [build_message("user", str(i)) for i in range(10)]
        trimmed = trim_history(history, 4)
        self.assertEqual(len(trimmed), 4)
        self.assertEqual(trimmed[-1]["content"], "9")


if __name__ == "__main__":
    unittest.main()
