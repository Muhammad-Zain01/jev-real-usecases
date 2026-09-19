"""Gradio UI for trying the registered Jev use cases."""

import os
from pathlib import Path
from typing import Any

import gradio as gr

from inference import JevInference
from ingestion import extract_text
from use_cases import UseCaseInput
from use_cases.registry import get_use_case


def _serialize_result(result: Any) -> dict[str, Any]:
    """Convert the shared result object into JSON for the Gradio output."""
    answers = {
        name: answer.model_dump() if hasattr(answer, "model_dump") else answer
        for name, answer in result.answers.items()
    }
    usage = result.response.usage
    return {
        "use_case": result.name,
        "model": result.response.model,
        "answers": answers,
        "usage": usage.model_dump() if hasattr(usage, "model_dump") else usage,
    }


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

    use_case_selector = gr.Radio(
        choices=[("Support Ticket Routing", "support_routing"), ("Resume Parsing", "resume_parsing")],
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
