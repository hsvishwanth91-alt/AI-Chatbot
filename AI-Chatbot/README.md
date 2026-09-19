# AI-Chatbot

A clean, modular command-line chatbot powered by the OpenAI API. Built with a
professional Python project structure, environment-based configuration, and
unit tests — ready to include in an internship portfolio.

## Description

AI-Chatbot is a terminal-based conversational assistant. It sends user
messages to an OpenAI chat model, keeps track of the conversation history for
the duration of the session so replies stay contextually aware, and handles
errors (bad API keys, rate limits, network issues, invalid input) gracefully
instead of crashing.

The codebase is organized so that configuration, chatbot logic, and helper
utilities each live in their own module, making the project easy to read,
test, and extend.

## Features

- 💬 Continuous, multi-turn conversation with session-level memory
- 🚪 Exit the chat anytime with `exit`, `quit`, `bye`, or `q`
- 🔐 API key loaded securely from environment variables (never hardcoded)
- ⚠️ Graceful handling of authentication errors, rate limits, connection
  issues, empty input, and unexpected exceptions
- 🧱 Clean, modular architecture (config / utils / chatbot / entry point)
- ✅ Type hints and docstrings throughout
- 🧪 Unit tests with mocked API calls (no network access needed to test)
- ⚙️ Configurable model, temperature, and max tokens via `.env`

## Tech Stack

- **Language:** Python 3.9+
- **AI Provider:** [OpenAI API](https://platform.openai.com/) (Chat
  Completions)
- **Config management:** [python-dotenv](https://pypi.org/project/python-dotenv/)
- **Testing:** `unittest` + `unittest.mock`

## Project Structure

```
AI-Chatbot/
├── app/
│   ├── __init__.py       # Package marker, exposes version info
│   ├── chatbot.py        # Chatbot class + interactive chat loop
│   ├── config.py         # Environment configuration & validation
│   └── utils.py          # Reusable helper functions
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py   # Chatbot tests (OpenAI API mocked)
│   ├── test_config.py    # Configuration loading/validation tests
│   └── test_utils.py     # Helper function tests
├── .env                  # Local environment variables (NOT committed)
├── .env.example           # Safe template for required env vars
├── .gitignore
├── requirements.txt
├── README.md
└── main.py                # Application entry point
```

## Installation

1. **Clone or download the project**, then move into the project folder:

   ```bash
   cd AI-Chatbot
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Environment Variable Setup

The chatbot reads its configuration from a `.env` file in the project root.

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your real OpenAI API key:

   ```env
   OPENAI_API_KEY=sk-your-real-key-here
   ```

3. (Optional) Adjust the other settings if you want a different model or
   generation behavior:

   | Variable              | Default       | Description                              |
   |------------------------|---------------|------------------------------------------|
   | `OPENAI_API_KEY`       | *(required)*  | Your secret OpenAI API key               |
   | `OPENAI_MODEL`         | `gpt-4o-mini` | Chat model to use                        |
   | `OPENAI_TEMPERATURE`   | `0.7`         | Response randomness (0.0–2.0)            |
   | `OPENAI_MAX_TOKENS`    | `512`         | Max tokens generated per response        |

`.env` is listed in `.gitignore` and will never be committed to source
control. Never share your API key or paste it into chat.

## How to Run the Chatbot

From the project root, with your virtual environment activated:

```bash
python main.py
```

You'll see a prompt where you can start chatting:

```
AI-Chatbot is ready. Type your message and press Enter.
Type 'exit', 'quit', or 'bye' to end the conversation.

You:
```

## How to Run Tests

Tests use mocked API calls, so they run instantly and require no API key or
network access.

```bash
python -m unittest discover -s tests -v
```

Or, if you have `pytest` installed:

```bash
pytest tests/
```

## Example Usage

```
AI-Chatbot is ready. Type your message and press Enter.
Type 'exit', 'quit', or 'bye' to end the conversation.

You: Hi! Can you explain what a REST API is?
Bot: A REST API is a way for two systems to communicate over HTTP using
standard methods like GET, POST, PUT, and DELETE...

You: Can you give me a simple example?
Bot: Sure! Imagine an endpoint /users — a GET request retrieves a list of
users, while a POST request creates a new one...

You: exit
Goodbye!
```

## Error Handling

The chatbot is designed to fail gracefully rather than crash:

- **Missing/invalid API key:** `config.py` validates configuration on
  startup and prints a clear error message before the app runs.
- **Authentication errors:** Caught and reported as a friendly message
  instructing the user to check their API key.
- **Rate limit / quota errors:** Caught and reported without exposing
  internal details.
- **Network/connection errors:** Caught and reported so the app doesn't
  crash if the internet drops.
- **Empty/whitespace input:** Detected and the user is re-prompted instead
  of sending a blank request to the API.
- **Unexpected errors:** A final catch-all in the chat loop reports the
  issue and lets the session continue instead of terminating abruptly.
- **The API key is never printed or logged** anywhere in the application.

## Future Improvements

- Add streaming responses for a more real-time chat experience
- Persist conversation history to a file or database between sessions
- Add streaming responses for the web UI
- Support multiple conversation "personas" via configurable system prompts
- Add retry-with-backoff for transient API errors
- Add structured logging instead of print statements
- Support swapping in other LLM providers behind the same interface

## License

This project is provided as-is for educational and portfolio purposes.

## Web Application

The project now includes a Flask web application with a responsive chat UI.
It keeps the OpenAI API key on the Python backend and never exposes secrets in
frontend JavaScript.

From the outer project folder:

```bash
cd "C:\Users\MANASA HV\Downloads\AI-Chatbot"
python index.py
```

Then open:

```text
http://127.0.0.1:5000
```

The original command-line chatbot still works:

```bash
python main.py
```

## Render Deployment

This project includes a root-level `render.yaml` that deploys the nested Flask
app from the `AI-Chatbot` folder.

1. Push this project to GitHub.
2. Create a Render Blueprint from the repository, or create a Python web
   service with `AI-Chatbot` as the root directory.
3. Add these Environment Variables in Render:

   ```env
   OPENAI_API_KEY=your_real_key
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=512
   FLASK_SECRET_KEY=use-a-long-random-secret
   ```

4. Deploy.

Do not commit `.env` to GitHub. Keep real secrets only in `.env` locally and
in Render Environment Variables for deployment.

If the deployed chatbot says it cannot connect to OpenAI, open this URL in
your deployed app:

```text
https://your-render-service.onrender.com/api/config-check
```

It should show `"configured": true`. If it does, check the Render service logs
for the exact backend error. The app logs the root cause without printing your
API key.
