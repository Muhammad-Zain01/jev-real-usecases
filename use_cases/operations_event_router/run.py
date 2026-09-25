"""Route a mixed operational event to the appropriate workflow."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="operations_event_router",
    title="Operations Event Router",
    description="Route an alert, ticket, or log event to an investigation workflow.",
    fields=(FieldSpec("event", "Event", "text", description="Paste the event payload or a concise structured summary."),),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    event = request.data.get("event")
    if not isinstance(event, str) or not event.strip():
        raise ValueError("operations_event_router requires non-empty 'event'")
    state = StateBuilder().add("event", event).build()
    questions = (
        QuestionBuilder()
        .choice("domain", "Which operational domain best fits this event?", {
            "security": "Possible attack, suspicious access, or security control alert.",
            "infrastructure": "Compute, network, storage, or deployment issue.",
            "application": "Application behavior, availability, or performance issue.",
            "data_pipeline": "Data freshness, transformation, or quality issue.",
            "customer_support": "A customer-facing request or service issue.",
            "other": "No domain clearly fits.",
        })
        .score("impact", "How severe is the apparent operational impact?", ["Informational", "Low", "Moderate", "High", "Critical"])
        .choice("next_workflow", "Which workflow should receive this event?", {
            "security_investigation": "Investigate security evidence and affected identities or assets.",
            "on_call_incident": "Page or queue the operational on-call workflow.",
            "application_support": "Investigate an application or customer-facing issue.",
            "data_quality_review": "Investigate data freshness or consistency.",
            "manual_triage": "A person should classify the event.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("operations_event_router", response, response.answers)
