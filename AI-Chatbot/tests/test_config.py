"""Unit tests for app.config."""

import os
import unittest
from unittest.mock import patch

from app.config import ConfigError, load_config


class TestLoadConfig(unittest.TestCase):
    """Tests for the load_config() function."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}, clear=True)
    def test_loads_defaults_when_only_api_key_set(self) -> None:
        config = load_config()
        self.assertEqual(config.openai_api_key, "test-key-123")
        self.assertEqual(config.model, "gpt-4o-mini")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 512)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "   "}, clear=True)
    def test_blank_api_key_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "key", "OPENAI_TEMPERATURE": "not-a-number"},
        clear=True,
    )
    def test_invalid_temperature_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "key", "OPENAI_MAX_TOKENS": "not-an-int"},
        clear=True,
    )
    def test_invalid_max_tokens_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "key", "OPENAI_TEMPERATURE": "5"},
        clear=True,
    )
    def test_out_of_range_temperature_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "key", "OPENAI_MAX_TOKENS": "0"},
        clear=True,
    )
    def test_non_positive_max_tokens_raises_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config()

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "key",
            "OPENAI_MODEL": "gpt-test",
            "OPENAI_TEMPERATURE": "0.2",
            "OPENAI_MAX_TOKENS": "100",
        },
        clear=True,
    )
    def test_custom_values_are_respected(self) -> None:
        config = load_config()
        self.assertEqual(config.model, "gpt-test")
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.max_tokens, 100)


if __name__ == "__main__":
    unittest.main()
