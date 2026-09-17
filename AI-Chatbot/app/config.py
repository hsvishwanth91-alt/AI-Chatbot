"""Application configuration.

Loads environment variables (via python-dotenv) and exposes a validated
`Config` object used throughout the application. This module is the single
source of truth for configuration values and never hardcodes secrets.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load variables from a local .env file into the process environment.
# This is a no-op (and safe) if no .env file is present.
load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Immutable container for application configuration.

    Attributes:
        openai_api_key: Secret API key used to authenticate with OpenAI.
        model: The chat completion model to use.
        temperature: Sampling temperature for response generation.
        max_tokens: Maximum number of tokens to generate per response.
    """

    openai_api_key: str
    model: str
    temperature: float
    max_tokens: int


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Returns:
        A populated, validated Config instance.

    Raises:
        ConfigError: If the OPENAI_API_KEY environment variable is missing
            or empty, or if numeric settings are invalid.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "Missing OPENAI_API_KEY. Create a .env file in the project root "
            "(see .env.example / README) and set OPENAI_API_KEY=your_key_here."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    try:
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    except ValueError as exc:
        raise ConfigError(
            "OPENAI_TEMPERATURE must be a valid number (e.g. 0.7)."
        ) from exc

    try:
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
    except ValueError as exc:
        raise ConfigError(
            "OPENAI_MAX_TOKENS must be a valid integer (e.g. 512)."
        ) from exc

    if not (0.0 <= temperature <= 2.0):
        raise ConfigError("OPENAI_TEMPERATURE must be between 0.0 and 2.0.")

    if max_tokens <= 0:
        raise ConfigError("OPENAI_MAX_TOKENS must be a positive integer.")

    return Config(
        openai_api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
