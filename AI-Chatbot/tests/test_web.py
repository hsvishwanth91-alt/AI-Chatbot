"""Unit tests for the Flask web API."""

import unittest
from unittest.mock import patch

from app.chatbot import ChatbotError
from app.config import Config, ConfigError
from web import app


def make_config() -> Config:
    """Build a dummy Config for tests."""
    return Config(
        openai_api_key="test-key",
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=100,
    )


class TestWebChatApi(unittest.TestCase):
    """Tests for /api/chat behavior."""

    def setUp(self) -> None:
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def test_chat_returns_reply(self) -> None:
        with patch("web.load_config", return_value=make_config()), patch(
            "web.Chatbot"
        ) as mock_chatbot_class:
            mock_chatbot = mock_chatbot_class.return_value
            mock_chatbot.history = [{"role": "system", "content": "sys"}]
            mock_chatbot.get_response.return_value = "Hello from the assistant"

            response = self.client.post(
                "/api/chat",
                json={"message": "Hi"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"reply": "Hello from the assistant"})
        mock_chatbot.get_response.assert_called_once_with("Hi")

    def test_chat_rejects_blank_message(self) -> None:
        response = self.client.post("/api/chat", json={"message": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_chat_reports_missing_render_config(self) -> None:
        with patch(
            "web.load_config",
            side_effect=ConfigError("Missing OPENAI_API_KEY"),
        ):
            response = self.client.post("/api/chat", json={"message": "Hi"})

        self.assertEqual(response.status_code, 500)
        self.assertIn("Render Environment Variables", response.get_json()["error"])

    def test_chat_reports_openai_error(self) -> None:
        with patch("web.load_config", return_value=make_config()), patch(
            "web.Chatbot"
        ) as mock_chatbot_class:
            mock_chatbot = mock_chatbot_class.return_value
            mock_chatbot.history = [{"role": "system", "content": "sys"}]
            mock_chatbot.get_response.side_effect = ChatbotError(
                "Could not connect to the OpenAI API from the server."
            )

            response = self.client.post("/api/chat", json={"message": "Hi"})

        self.assertEqual(response.status_code, 502)
        self.assertIn("OpenAI API", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
