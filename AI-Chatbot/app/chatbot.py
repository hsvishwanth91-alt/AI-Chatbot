"""Core chatbot logic.

Defines the `Chatbot` class, which wraps the OpenAI Chat Completions API,
maintains conversation history for a session, and exposes a simple
`get_response` method. Also provides `run_chat_loop`, the interactive
command-line loop used by `main.py`.
"""

from typing import List, Optional

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from app.config import Config
from app.utils import (
    Message,
    build_message,
    is_blank,
    is_exit_command,
    trim_history,
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, friendly, and concise AI assistant."
)
MAX_HISTORY_MESSAGES = 20
OPENAI_TIMEOUT_SECONDS = 45.0
OPENAI_MAX_RETRIES = 2


class ChatbotError(Exception):
    """Raised when the chatbot cannot produce a response."""


class Chatbot:
    """A conversational AI chatbot backed by the OpenAI Chat Completions API.

    The chatbot keeps track of the full conversation history for the
    lifetime of the session so that responses stay contextually aware.
    """

    def __init__(
        self,
        config: Config,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        client: Optional[OpenAI] = None,
    ) -> None:
        """Initialize the chatbot.

        Args:
            config: Validated application configuration containing the API
                key and model settings.
            system_prompt: Instruction that sets the assistant's behavior.
            client: Optional pre-built OpenAI client. Primarily used for
                dependency injection in tests; a real client is created
                from `config` if not provided.
        """
        self._config = config
        self._client = client or OpenAI(
            api_key=config.openai_api_key,
            timeout=OPENAI_TIMEOUT_SECONDS,
            max_retries=OPENAI_MAX_RETRIES,
        )
        self.history: List[Message] = [build_message("system", system_prompt)]

    def reset(self) -> None:
        """Clear the conversation history, keeping only the system prompt."""
        system_message = self.history[0]
        self.history = [system_message]

    def get_response(self, user_input: str) -> str:
        """Send a user message to the model and return its reply.

        The user message and the assistant's reply are both appended to
        the conversation history so that subsequent calls retain context.

        Args:
            user_input: The text typed by the user.

        Returns:
            The assistant's text response.

        Raises:
            ValueError: If `user_input` is empty or only whitespace.
            ChatbotError: If the OpenAI API call fails for any reason
                (authentication, rate limiting, connectivity, etc.).
        """
        if is_blank(user_input):
            raise ValueError("Message cannot be empty.")

        self.history.append(build_message("user", user_input))
        self.history = trim_history(self.history, MAX_HISTORY_MESSAGES)

        try:
            completion = self._client.chat.completions.create(
                model=self._config.model,
                messages=self.history,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
            )
        except AuthenticationError as exc:
            raise ChatbotError(
                "Authentication failed. Check that OPENAI_API_KEY in your "
                ".env file is valid."
            ) from exc
        except RateLimitError as exc:
            raise ChatbotError(
                "Rate limit or quota exceeded. Please wait and try again."
            ) from exc
        except APIConnectionError as exc:
            raise ChatbotError(
                "Could not connect to the OpenAI API from the server. Please "
                "try again in a moment. If this keeps happening on Render, "
                "check the service logs and Environment Variables."
            ) from exc
        except APIStatusError as exc:
            raise ChatbotError(
                f"OpenAI API returned an error (status {exc.status_code})."
            ) from exc
        except OpenAIError as exc:
            raise ChatbotError(f"OpenAI API error: {exc}") from exc

        reply = completion.choices[0].message.content
        if reply is None:
            raise ChatbotError("The model returned an empty response.")

        reply = reply.strip()
        self.history.append(build_message("assistant", reply))
        return reply


def run_chat_loop(chatbot: Chatbot) -> None:
    """Run the interactive command-line chat loop.

    Reads user input, prints assistant responses, and gracefully handles
    invalid input, API errors, and interruption (Ctrl+C / EOF) until the
    user issues an exit command.

    Args:
        chatbot: A ready-to-use Chatbot instance.
    """
    print("AI-Chatbot is ready. Type your message and press Enter.")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if is_exit_command(user_input):
            print("Goodbye!")
            break

        if is_blank(user_input):
            print("Bot: Please type a message, or 'exit' to quit.")
            continue

        try:
            reply = chatbot.get_response(user_input)
        except ValueError as exc:
            print(f"Bot: {exc}")
            continue
        except ChatbotError as exc:
            print(f"Bot: Sorry, something went wrong. {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - final safety net for CLI use
            print(f"Bot: An unexpected error occurred: {exc}")
            continue

        print(f"Bot: {reply}\n")
