"""Vercel serverless entry point for the AI-Chatbot Flask app."""

from pathlib import Path
import os
import sys


PROJECT_DIR = Path(__file__).resolve().parent.parent / "AI-Chatbot"
os.chdir(PROJECT_DIR)
sys.path.insert(0, str(PROJECT_DIR))

from web import app  # noqa: E402
