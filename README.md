# File Counter Agent

A minimal AI agent that answers questions about how many files are in a directory, powered by Google's Gemini API. Built as a learning project to understand how agent tool-calling loops work under the hood.

## What it does

You type a question in plain English — like *"how many PDFs are in my Downloads folder, including subfolders?"* — and the agent:

1. Sends your question to Gemini.
2. Gemini decides whether it needs to call the `count_files` tool to answer, and if so, figures out the right arguments (path, extension filter, recursive or not) from your wording.
3. The script actually runs `count_files` locally and sends the result back to Gemini.
4. Gemini reads the result and gives you a final plain-English answer.

This loop (ask → decide → act → observe → repeat) is the core pattern behind most AI agents.

## Setup

**1. Install dependencies**
```powershell
pip install google-genai python-dotenv
```

**2. Get a free Gemini API key**
Go to [aistudio.google.com](https://aistudio.google.com), sign in, and generate an API key. No credit card required.

**3. Add your key**
Create a file named `.env` in the same folder as `agent.py`, containing:
```
GEMINI_API_KEY=your_key_here
```

## Usage

Run the script:
```powershell
python agent.py
```

It'll prompt you:
```
Ask me something:
```

Type a question, for example:
```
How many pdf files are in C:/Users/HP/Downloads, including subfolders?
```

The agent will print which tool call it's making, then give you a final answer.

## How the tool works

`count_files(path, extension, recursive)` is the one tool the agent has access to:

| Argument | Type | Default | Description |
|---|---|---|---|
| `path` | string | `.` (current directory) | Which folder to look in |
| `extension` | string | none (counts all files) | Filter by file type, e.g. `pdf`, `py` |
| `recursive` | boolean | `False` | Whether to also search subfolders |

The model picks these arguments automatically based on how you phrase your question — you don't need to specify them in a special format.

## Project structure

```
agent.py     # the whole agent: client setup, tool schema, tool function, and the loop
.env         # your API key (never commit this to git)
```

## Known limitations

- Only one tool (`count_files`) — it can't do anything else yet.
- `max_steps=5` caps how many back-and-forth turns the agent can take per question, to avoid infinite loops.
- Runs once per execution — ask one question, get one answer, then the script exits. (A follow-up improvement would be wrapping the entry point in a loop to ask multiple questions in one session.)

## Notes on switching providers

This project originally used DeepSeek's OpenAI-compatible API, then moved to Gemini. If you ever want to swap providers again:
- OpenAI-compatible providers (DeepSeek, Groq, OpenRouter) share the same `tools` / `tool_calls` / `role: "tool"` shape — swapping between them is mostly just a `base_url` and API key change.
- Gemini uses its own SDK shape (`types.FunctionDeclaration`, `contents`, `function_calls`) — swapping to or from Gemini requires rewriting the client setup, tool schema, and loop, though the tool function itself (`count_files`) stays identical no matter which provider is used.
