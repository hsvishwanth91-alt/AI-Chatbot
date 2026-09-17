"""Convenience launcher for the nested AI-Chatbot project.

This lets you run the chatbot from the downloaded outer folder with:

    python main.py
"""

from pathlib import Path
import os
import runpy
import sys


PROJECT_DIR = Path(__file__).resolve().parent / "AI-Chatbot"


if __name__ == "__main__":
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, str(PROJECT_DIR))
    runpy.run_path(str(PROJECT_DIR / "main.py"), run_name="__main__")
