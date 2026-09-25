"""Classify a complaint and recommend an escalation path."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="complaint_escalation",
    title="Complaint Escalation Review",
    description="Assess a complaint's issue and severity for appropriate human follow-up.",
    fields=(
        FieldSpec("complaint", "Complaint", "text", description="The complaint and conversation context."),
        FieldSpec("case_history", "Case history", "text", required=False, description="Prior attempts to resolve the matter or relevant case facts."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    complaint = request.data.get("complaint")
    history = request.data.get("case_history", "")
    if not isinstance(complaint, str) or not complaint.strip():
        raise ValueError("complaint_escalation requires non-empty 'complaint'")
    if not isinstance(history, str):
        raise ValueError("'case_history' must be a string")
    state = StateBuilder().add("complaint", complaint).add("case_history", history).build()
    questions = (
        QuestionBuilder()
        .choice("complaint_type", "What is the main issue in this complaint?", {
            "service_failure": "A product or service did not work as expected.",
            "billing_or_refund": "A charge, refund, or billing outcome is disputed.",
            "staff_or_process": "The complaint concerns staff conduct or a service process.",
            "safety_or_legal": "The complaint raises a safety, legal, or regulatory concern.",
            "other": "Another issue or insufficient evidence.",
        })
        .score("severity", "How serious is the complaint based on the stated impact and history?", ["Low", "Moderate", "High", "Severe"])
        .noul("repeat_unresolved_issue", "Does the supplied history suggest the same issue has repeatedly remained unresolved?")
        .choice("follow_up", "What follow-up path is appropriate?", {
            "normal_resolution": "Continue through the ordinary resolution process.",
            "specialist_review": "Route to a specialist for review.",
            "priority_human_handoff": "Promptly hand the case to a human lead.",
            "safety_or_compliance_escalation": "Route to the relevant safety, legal, or compliance team.",
            "request_more_details": "Ask for information needed to assess the complaint.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("complaint_escalation", response, response.answers)
