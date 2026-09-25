"""Gradio UI for trying the registered Jev use cases."""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import gradio as gr

from inference import JevInference
from ingestion import extract_text
from use_cases import UseCaseInput
from use_cases.registry import get_use_case


def _json_safe(value: Any) -> Any:
    """Make nested Jev/Pydantic values safe for Gradio's JSON component."""
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if isinstance(value, Mapping):
        # Score probabilities can use integer labels; Gradio JSON requires strings.
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _serialize_result(result: Any) -> dict[str, Any]:
    """Convert the shared result object into JSON for the Gradio output."""
    usage = result.response.usage
    return _json_safe({
        "use_case": result.name,
        "model": result.response.model,
        "answers": result.answers,
        "usage": usage,
    })


def _run_use_case(use_case_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Run whichever use case the user selected on the main page."""
    if not os.getenv("TYPESAFE_API_KEY"):
        raise gr.Error("TYPESAFE_API_KEY is not loaded. Source your .env file first.")

    use_case = get_use_case(use_case_id)

    # One shared inference object is used for the selected use case.
    with JevInference() as inference:
        result = use_case.run(inference, UseCaseInput(data=data))

    return _serialize_result(result)


def _run_from_form(use_case_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Normalize form values before handing them to the selected use case."""
    if use_case_id == "resume_parsing":
        file_path = data.get("resume_file")
        if not file_path:
            raise gr.Error("Upload a TXT, PDF, or DOCX resume first.")

        path = Path(file_path)
        resume_text = extract_text(path)
        if not resume_text.strip():
            raise gr.Error("No readable text was found in the uploaded resume.")

        data = {"resume_text": resume_text, "filename": path.name}

    return _run_use_case(use_case_id, data)


with gr.Blocks(title="Jev Real Use Cases") as demo:
    gr.Markdown("# Jev Real Use Cases\nChoose a use case and test it with Jev.")

    use_case_selector = gr.Dropdown(
        choices=[
            ("Support Ticket Routing", "support_routing"),
            ("Resume Parsing", "resume_parsing"),
            ("Query Preprocessor", "query_preprocessor"),
            ("Agent Router", "agent_router"),
            ("Tool Selection and Policy Gate", "tool_policy_gate"),
            ("Model and Effort Router", "model_effort_router"),
            ("RAG Retrieval Reranker", "rag_reranker"),
            ("Agent Trace Reviewer", "agent_trace_reviewer"),
            ("Prompt Injection and Safety Gate", "prompt_safety_gate"),
            ("Support Next Action", "support_next_action"),
            ("Invoice Processing Triage", "invoice_triage"),
            ("Security Incident Triage", "security_incident_triage"),
            ("Email Triage", "email_triage"),
            ("Product Feedback Triage", "product_feedback_triage"),
            ("Operations Event Router", "operations_event_router"),
            ("Document Intake Router", "document_intake_router"),
            ("Workflow Failure Triage", "workflow_failure_triage"),
            ("Language and Locale Router", "language_locale_router"),
            ("SLA Breach Prioritizer", "sla_breach_prioritizer"),
            ("Complaint Escalation Review", "complaint_escalation"),
            ("Infrastructure Change Risk Review", "infrastructure_change_review"),
            ("Data Quality Issue Triage", "data_quality_triage"),
            ("Duplicate Case Review", "duplicate_case_review"),
            ("Human Review Queue Assignment", "reviewer_queue_assignment"),
        ],
        value="support_routing",
        label="Choose a use case",
    )

    @gr.render(inputs=use_case_selector)
    def render_form(use_case_id: str):
        use_case = get_use_case(use_case_id)
        spec = use_case.SPEC
        gr.Markdown(f"## {spec.title}\n{spec.description}")

        components = []
        field_names = []
        for field in spec.fields:
            field_names.append(field.name)
            if field.kind == "file":
                component = gr.File(
                    label=field.label,
                    file_types=[".txt", ".pdf", ".docx"],
                    type="filepath",
                )
            else:
                component = gr.Textbox(
                    label=field.label,
                    lines=8,
                    placeholder=field.description,
                )
            components.append(component)

        run_button = gr.Button(f"Run {spec.title}", variant="primary")
        output = gr.JSON(label="Jev result")

        def submit(*values: Any) -> dict[str, Any]:
            form_data = dict(zip(field_names, values, strict=True))
            return _run_from_form(use_case_id, form_data)

        run_button.click(submit, inputs=components, outputs=output)


if __name__ == "__main__":
    demo.launch()
