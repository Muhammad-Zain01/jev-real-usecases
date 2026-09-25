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

The UI currently includes 24 example workflows:

- Support ticket routing
- Resume parsing for TXT, PDF, and DOCX files
- Query preprocessing and agent routing
- Tool policy checks and model-effort routing
- RAG retrieval reranking and prompt-safety screening
- Agent trace review and support next-action recommendations
- Invoice and security incident triage
- Email and product feedback triage
- Operations event and document intake routing
- Workflow failure triage and language routing
- SLA prioritization and complaint escalation
- Infrastructure change and data quality review
- Duplicate case and human reviewer assignment

Uploaded files are converted to text before they are sent to Jev. Each use
case lives in its own folder with a common `run.py` file. Every `run.py`
exposes a `SPEC` for its form and the same `run(inference, request)` function
for execution. These examples return decisions or recommendations; application
code is responsible for enforcing permissions, approval rules, and confidence
thresholds before taking consequential actions.
