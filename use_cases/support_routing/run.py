"""Support-ticket routing use case."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="support_routing",
    title="Support Ticket Routing",
    description="Route a customer support ticket to the right team.",
    fields=(
        FieldSpec(
            name="ticket",
            label="Support ticket",
            kind="text",
            description="Paste the customer's support message.",
        ),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    """Route one support ticket to the most appropriate team."""
    ticket = request.data.get("ticket")
    if not isinstance(ticket, str) or not ticket.strip():
        raise ValueError("support_routing requires a non-empty 'ticket' string")

    state = StateBuilder().add("ticket", ticket).build()
    questions = (
        QuestionBuilder()
        .choice(
            name="category",
            instructions="Which team should handle this support ticket?",
            criteria={
                "billing": "Payment, invoice, refund, or subscription issue.",
                "technical": "Bug, error, integration, or product malfunction.",
                "account": "Login, account access, or profile issue.",
                "other": "None of the other categories clearly applies.",
            },
        )
        .build()
    )

    response = inference.infer(state=state, questions=questions)
    return UseCaseResult(
        name="support_routing",
        response=response,
        answers=response.answers,
    )
