"""Reusable helper functions for the AI-Chatbot application.

Keeping these helpers separate from `chatbot.py` keeps the chatbot module
focused purely on conversation logic.
"""

from datetime import datetime
from typing import Dict, List

Message = Dict[str, str]

EXIT_COMMANDS = {"exit", "quit", "bye", "q"}


def is_exit_command(user_input: str) -> bool:
    """Check whether the user input is a command to end the chat session.

    Args:
        user_input: The raw text entered by the user.

    Returns:
        True if the (trimmed, lowercased) input matches a known exit
        command, otherwise False.
    """
    return user_input.strip().lower() in EXIT_COMMANDS


def is_blank(user_input: str) -> bool:
    """Check whether the user input is empty or only whitespace.

    Args:
        user_input: The raw text entered by the user.

    Returns:
        True if the input contains no non-whitespace characters.
    """
    return len(user_input.strip()) == 0


def build_message(role: str, content: str) -> Message:
    """Build a single chat message dictionary in OpenAI's expected format.

    Args:
        role: The role of the message sender ("system", "user", or
            "assistant").
        content: The text content of the message.

    Returns:
        A dictionary with "role" and "content" keys.
    """
    return {"role": role, "content": content}


def trim_history(history: List[Message], max_messages: int) -> List[Message]:
    """Trim conversation history to a maximum number of messages.

    Always preserves the first message if it is a system prompt, and keeps
    the most recent messages up to `max_messages` total.

    Args:
        history: The full list of conversation messages, oldest first.
        max_messages: The maximum number of messages to retain.

    Returns:
        A trimmed list of messages.
    """
    if len(history) <= max_messages:
        return history

    if history and history[0]["role"] == "system":
        system_message = [history[0]]
        remainder = history[1:]
        keep = max_messages - 1
        return system_message + remainder[-keep:] if keep > 0 else system_message

    return history[-max_messages:]


def timestamp() -> str:
    """Return the current local time as a human-readable string.

    Returns:
        A formatted timestamp, e.g. "2026-09-18 10:15:00".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_error(prefix: str, error: Exception) -> str:
    """Format an exception into a user-friendly error message.

    Args:
        prefix: A short description of what operation failed.
        error: The exception that was raised.

    Returns:
        A single-line, human-readable error string. Never includes secrets.
    """
    return f"{prefix}: {error.__class__.__name__} - {error}"
