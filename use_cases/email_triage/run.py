"""Classify inbound email and recommend a handling route."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="email_triage",
    title="Email Triage",
    description="Classify an inbound email and recommend its destination.",
    fields=(FieldSpec("email", "Email", "text", description="Paste the subject, sender context, and message body."),),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    email = request.data.get("email")
    if not isinstance(email, str) or not email.strip():
        raise ValueError("email_triage requires a non-empty 'email'")
    state = StateBuilder().add("email", email).build()
    questions = (
        QuestionBuilder()
        .choice("category", "What is the primary category of this email?", {
            "product_issue": "A product problem, bug, or error.",
            "how_to": "A request for instructions or information.",
            "account_request": "A request to update, access, or close an account.",
            "sales": "A sales inquiry or purchase interest.",
            "spam": "Unsolicited, irrelevant, or deceptive bulk email.",
            "other": "No category clearly fits.",
        })
        .score("urgency", "How urgent is a response based on the message?", ["Routine", "Soon", "Urgent", "Critical"])
        .choice("destination", "Which handling path is most appropriate?", {
            "support_queue": "A support specialist should handle the message.",
            "sales_queue": "A sales team should handle the message.",
            "account_workflow": "A verified account-maintenance workflow should handle it.",
            "spam_review": "Quarantine or review as possible spam.",
            "manual_review": "A person should determine the next step.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("email_triage", response, response.answers)
