"""Flask web application for the AI-Chatbot project."""

from __future__ import annotations

import os
import traceback
from typing import Any

from flask import Flask, jsonify, render_template, request, session

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.chatbot import Chatbot, ChatbotError, DEFAULT_SYSTEM_PROMPT
from app.config import ConfigError, load_config
from app.utils import build_message, is_blank, trim_history


MAX_WEB_HISTORY_MESSAGES = 20

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-dev-secret-change-me")


def _initial_history() -> list[dict[str, str]]:
    return [build_message("system", DEFAULT_SYSTEM_PROMPT)]


def _get_history() -> list[dict[str, str]]:
    history = session.get("chat_history")
    if not isinstance(history, list) or not history:
        return _initial_history()
    return history


def _json_error(message: str, status_code: int = 400) -> tuple[Any, int]:
    return jsonify({"error": message}), status_code


@app.get("/")
def index() -> str:
    """Render the chat interface."""
    return render_template("index.html")


@app.post("/api/chat")
def chat() -> tuple[Any, int] | Any:
    """Accept a user message and return the assistant response."""
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if is_blank(message):
        return _json_error("Please type a message before sending.")

    try:
        config = load_config()
    except ConfigError as exc:
        app.logger.error("Configuration error: %s", exc)
        return _json_error(
            "The chatbot is not configured yet. Add OPENAI_API_KEY to .env "
            "locally or to your Vercel Environment Variables.",
            500,
        )

    try:
        chatbot = Chatbot(config=config)
        chatbot.history = trim_history(_get_history(), MAX_WEB_HISTORY_MESSAGES)
        reply = chatbot.get_response(message)
    except ValueError:
        return _json_error("Please type a message before sending.")
    except ChatbotError as exc:
        app.logger.error("Chatbot error: %s", exc)
        if exc.__cause__ is not None:
            app.logger.error("Root cause: %r", exc.__cause__)
        return _json_error(str(exc), 502)
    except Exception as exc:
        app.logger.error("Unexpected chat error: %s", exc)
        app.logger.error(traceback.format_exc())
        return _json_error(
            "Something went wrong while contacting the assistant. Please try again.",
            500,
        )

    session["chat_history"] = trim_history(
        chatbot.history,
        MAX_WEB_HISTORY_MESSAGES,
    )
    session.modified = True

    return jsonify({"reply": reply})


@app.post("/api/clear")
def clear_chat() -> Any:
    """Clear the browser session's chat history."""
    session["chat_history"] = _initial_history()
    session.modified = True
    return jsonify({"ok": True})


@app.get("/api/health")
def health() -> Any:
    """Small health endpoint for local and deployment checks."""
    return jsonify({"status": "ok"})


@app.get("/api/config-check")
def config_check() -> Any:
    """Report deployment config status without exposing secret values."""
    try:
        config = load_config()
    except ConfigError as exc:
        return jsonify({"configured": False, "error": str(exc)}), 500

    return jsonify(
        {
            "configured": True,
            "model": config.model,
            "has_openai_key": bool(config.openai_api_key),
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
    )


@app.get("/api/openai-check")
def openai_check() -> Any:
    """Test OpenAI connectivity without exposing the API key."""
    try:
        config = load_config()
    except ConfigError as exc:
        return jsonify({"ok": False, "step": "config", "error": str(exc)}), 500

    client = OpenAI(api_key=config.openai_api_key, timeout=20.0, max_retries=0)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "Reply with exactly: ok"},
                {"role": "user", "content": "connection test"},
            ],
            max_tokens=5,
            temperature=0,
        )
    except AuthenticationError as exc:
        app.logger.error("OpenAI auth check failed: %r", exc)
        return jsonify(
            {
                "ok": False,
                "step": "openai_auth",
                "error_type": exc.__class__.__name__,
                "message": "The OpenAI API key is missing, invalid, or revoked.",
            }
        ), 401
    except RateLimitError as exc:
        app.logger.error("OpenAI quota/rate check failed: %r", exc)
        return jsonify(
            {
                "ok": False,
                "step": "openai_quota",
                "error_type": exc.__class__.__name__,
                "message": "The OpenAI account is rate-limited or out of quota.",
            }
        ), 429
    except APIConnectionError as exc:
        app.logger.error("OpenAI connection check failed: %r", exc)
        cause = repr(exc.__cause__) if exc.__cause__ else repr(exc)
        return jsonify(
            {
                "ok": False,
                "step": "openai_connection",
                "error_type": exc.__class__.__name__,
                "cause": cause[:500],
                "message": "The server could not reach api.openai.com.",
            }
        ), 502
    except APIStatusError as exc:
        app.logger.error("OpenAI status check failed: %r", exc)
        return jsonify(
            {
                "ok": False,
                "step": "openai_status",
                "error_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "message": "OpenAI returned an API error.",
            }
        ), exc.status_code
    except Exception as exc:
        app.logger.error("OpenAI unknown check failed: %r", exc)
        return jsonify(
            {
                "ok": False,
                "step": "unknown",
                "error_type": exc.__class__.__name__,
                "message": "Unexpected error while testing OpenAI.",
            }
        ), 500

    content = response.choices[0].message.content if response.choices else ""
    return jsonify(
        {
            "ok": True,
            "model": config.model,
            "reply": content,
        }
    )
