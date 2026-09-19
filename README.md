# Jev Real Use Cases

Small, practical experiments with TypeSafe AI's Jev decision model.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set the API key in `.env`, then load it into the current shell:

```bash
set -a
source .env
set +a
```

## Run the Gradio UI

```bash
python run_ui.py
```

The UI currently includes:

- Support ticket routing
- Resume parsing for TXT, PDF, and DOCX files

Uploaded files are converted to text before they are sent to Jev. Each use
case lives in its own folder with a common `run.py` file. Every `run.py`
exposes a `SPEC` for its form and the same `run(inference, request)` function
for execution.
