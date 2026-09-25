"""Classify a failed workflow step and recommend a safe recovery path."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="workflow_failure_triage",
    title="Workflow Failure Triage",
    description="Classify a workflow failure and recommend retry, correction, or escalation.",
    fields=(
        FieldSpec("failed_step", "Failed step", "text", description="The step name and intended operation."),
        FieldSpec("error_details", "Error and execution details", "text", description="Error message, status code, attempts, and relevant logs."),
        FieldSpec("input_context", "Input context", "text", required=False, description="Relevant non-sensitive input or validation results."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    step, error = request.data.get("failed_step"), request.data.get("error_details")
    context = request.data.get("input_context", "")
    if not isinstance(step, str) or not step.strip() or not isinstance(error, str) or not error.strip():
        raise ValueError("workflow_failure_triage requires failed_step and error_details")
    if not isinstance(context, str):
        raise ValueError("'input_context' must be a string")
    state = StateBuilder().add("failed_step", step).add("error_details", error).add("input_context", context).build()
    questions = (
        QuestionBuilder()
        .choice("failure_type", "What is the most likely failure category from the supplied evidence?", {
            "transient_service": "A temporary network, rate-limit, or service availability failure.",
            "invalid_input": "The request or data failed validation or has an unsupported format.",
            "permission": "Credentials, access, or authorization appear insufficient.",
            "configuration": "A deployment, setting, or dependency appears misconfigured.",
            "application_bug": "The failure appears to come from application logic or an unexpected state.",
            "unknown": "The evidence is insufficient to identify the cause.",
        })
        .noul("retry_appears_safe", "Does the evidence suggest a bounded retry could be safe, without duplicating a non-idempotent action?")
        .choice("recovery", "What recovery path should the workflow recommend?", {
            "bounded_retry": "Retry within an existing retry limit and only if the operation is safe.",
            "correct_input": "Correct or request valid input before retrying.",
            "repair_configuration": "Review credentials, configuration, or dependencies.",
            "escalate_engineering": "Send the failure to engineering with diagnostic context.",
            "human_review": "A person should decide how to proceed.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("workflow_failure_triage", response, response.answers)
