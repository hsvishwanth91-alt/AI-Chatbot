"""Unit tests for app.chatbot.

All OpenAI API calls are mocked; no real network requests are made.
"""

import unittest
from unittest.mock import MagicMock

from openai import APIConnectionError, AuthenticationError, RateLimitError

from app.chatbot import Chatbot, ChatbotError
from app.config import Config


def make_config() -> Config:
    """Build a dummy Config for tests (never a real API key)."""
    return Config(
        openai_api_key="test-key",
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=100,
    )


def make_completion(content: str) -> MagicMock:
    """Build a mock object shaped like an OpenAI chat completion response."""
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestChatbotGetResponse(unittest.TestCase):
    """Tests for Chatbot.get_response()."""

    def setUp(self) -> None:
        self.mock_client = MagicMock()
        self.chatbot = Chatbot(config=make_config(), client=self.mock_client)

    def test_returns_model_reply(self) -> None:
        self.mock_client.chat.completions.create.return_value = make_completion(
            "Hello, human!"
        )
        reply = self.chatbot.get_response("Hi there")
        self.assertEqual(reply, "Hello, human!")

    def test_appends_to_history(self) -> None:
        self.mock_client.chat.completions.create.return_value = make_completion(
            "Reply"
        )
        self.chatbot.get_response("Hi there")
        roles = [m["role"] for m in self.chatbot.history]
        self.assertEqual(roles, ["system", "user", "assistant"])

    def test_empty_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.chatbot.get_response("   ")
        self.mock_client.chat.completions.create.assert_not_called()

    def test_authentication_error_wrapped_as_chatbot_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="bad key", response=MagicMock(status_code=401), body=None
        )
        with self.assertRaises(ChatbotError):
            self.chatbot.get_response("Hi")

    def test_rate_limit_error_wrapped_as_chatbot_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = RateLimitError(
            message="rate limited", response=MagicMock(status_code=429), body=None
        )
        with self.assertRaises(ChatbotError):
            self.chatbot.get_response("Hi")

    def test_connection_error_wrapped_as_chatbot_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = APIConnectionError(
            request=MagicMock()
        )
        with self.assertRaises(ChatbotError):
            self.chatbot.get_response("Hi")

    def test_none_content_raises_chatbot_error(self) -> None:
        self.mock_client.chat.completions.create.return_value = make_completion(None)
        with self.assertRaises(ChatbotError):
            self.chatbot.get_response("Hi")


class TestChatbotReset(unittest.TestCase):
    """Tests for Chatbot.reset()."""

    def test_reset_keeps_only_system_prompt(self) -> None:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = make_completion("Reply")
        chatbot = Chatbot(config=make_config(), client=mock_client)

        chatbot.get_response("Hi")
        self.assertGreater(len(chatbot.history), 1)

        chatbot.reset()
        self.assertEqual(len(chatbot.history), 1)
        self.assertEqual(chatbot.history[0]["role"], "system")


if __name__ == "__main__":
    unittest.main()
