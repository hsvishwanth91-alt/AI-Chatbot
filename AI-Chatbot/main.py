"""Entry point for the AI-Chatbot application.

Run this file to start an interactive chat session:

    python main.py
"""

import sys

from app.chatbot import Chatbot, run_chat_loop
from app.config import ConfigError, load_config


def main() -> int:
    """Load configuration, initialize the chatbot, and start the chat loop.

    Returns:
        Process exit code (0 on success, 1 on configuration failure).
    """
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    chatbot = Chatbot(config=config)
    run_chat_loop(chatbot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
