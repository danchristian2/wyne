# File Assistant

An AI agent that answers questions about files on your computer — and can now create them too — powered by Google's Gemini API. Built as a learning project to understand how agent tool-calling loops work under the hood.

## What it does

You type a question or request in plain English, and the agent:

1. Sends your message to Gemini.
2. Gemini decides whether it needs to call one of its tools to help, and figures out the right arguments from your wording.
3. The script actually runs the tool locally and sends the result back to Gemini.
4. Gemini reads the result and gives you a final plain-English answer.
5. If the current model runs out of free-tier quota mid-conversation, the agent automatically switches to the next available model and keeps going.

This loop (ask → decide → act → observe → repeat) is the core pattern behind most AI agents.

## Project structure

```
wyne/
├── agent/
│   ├── __init__.py      # re-exports run_agent for easy importing
│   ├── client.py         # Gemini client setup + list of fallback models
│   ├── tools.py           # tool functions + their schemas
│   └── core.py             # the run_agent loop itself
├── main.py                 # terminal entry point
├── app.py                  # Flask web UI (not currently in use)
├── templates/
│   └── index.html
├── .env                     # your API key (never commit this)
└── .gitignore
```

## Setup

**1. Install dependencies**
```powershell
pip install google-genai python-dotenv
```

**2. Get a free Gemini API key**
Go to [aistudio.google.com](https://aistudio.google.com), sign in, and generate an API key. No credit card required.

**3. Add your key**
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```

## Usage

```powershell
python main.py
```

It'll prompt you:
```
Ask me anything:
```

Keep asking questions — type `quit` or `exit` to end the session. When you quit, it reports how many questions you asked.

## Available tools

| Tool | What it does |
|---|---|
| `count_files` | Counts files in a directory, optionally filtered by extension, optionally recursive |
| `get_file_size` | Reports a single file's size in a human-readable unit (KB, MB, GB, etc) |
| `create_file` | Creates a new file with optional text content. Refuses to overwrite an existing file |

Example prompts:
- *"How many PDFs are in my Downloads, including subfolders?"*
- *"How big is C:/Users/HP/Desktop/report.docx?"*
- *"Create a file called notes.txt on my Desktop with the text 'meeting at 3pm'"*

The model picks the right tool and arguments automatically based on how you phrase your request.

## Model fallback

The agent tries models in this order, automatically switching if one hits its free-tier quota:
```
gemini-3.1-flash-lite → gemini-3.5-flash-lite → gemini-3.6-flash → gemini-3.7-flash
```
You'll see a message in the terminal if a switch happens mid-conversation. If every model is exhausted, the agent reports that clearly instead of crashing.

To see which models your own API key currently has access to (model names change over time), run:
```powershell
python list_models.py
```

## Known limitations

- File-modifying tools (`create_file`) refuse to overwrite existing files as a safety guard — there's currently no "edit" or "delete" tool.
- `max_steps=5` caps how many back-and-forth turns the agent can take per question, to avoid runaway loops.
- The web UI (`app.py`) exists but isn't the current focus — the terminal (`main.py`) is the primary way to use this.
- Each question in a session is answered independently — the agent doesn't yet remember earlier questions in the same conversation.

## Development notes

This project is built one small feature per git branch, tested, then merged — a good habit for isolating changes and being able to safely experiment. See commit history for the order features were added in.

**Important lesson learned the hard way:** commit your work as soon as it's written, even before testing. Uncommitted files aren't protected if you switch or delete branches — several hours were lost re-adding a tool that existed only as an untracked file when a branch was deleted.