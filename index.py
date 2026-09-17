"""Vercel and local web entry point for the AI-Chatbot app."""

from pathlib import Path
import os
import sys


PROJECT_DIR = Path(__file__).resolve().parent / "AI-Chatbot"
os.chdir(PROJECT_DIR)
sys.path.insert(0, str(PROJECT_DIR))

from web import app  # noqa: E402


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
