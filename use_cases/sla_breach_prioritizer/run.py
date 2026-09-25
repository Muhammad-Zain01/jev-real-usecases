"""Prioritize a case based on impact, age, and service-level context."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="sla_breach_prioritizer",
    title="SLA Breach Prioritizer",
    description="Estimate urgency and breach risk for an operational or support case.",
    fields=(
        FieldSpec("case", "Case details", "text", description="The issue, customer impact, and current status."),
        FieldSpec("sla_context", "SLA and timing", "text", description="Priority policy, elapsed time, and response or resolution deadline."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    case, sla = request.data.get("case"), request.data.get("sla_context")
    if not isinstance(case, str) or not case.strip() or not isinstance(sla, str) or not sla.strip():
        raise ValueError("sla_breach_prioritizer requires case and sla_context")
    state = StateBuilder().add("case", case).add("sla_context", sla).build()
    questions = (
        QuestionBuilder()
        .score("customer_impact", "How broad and serious is the impact described?", ["Minimal", "Low", "Moderate", "High", "Critical"])
        .noul("likely_to_breach", "Given the supplied timing and SLA, is this case at risk of missing its next required response or resolution deadline?")
        .choice("priority", "What handling priority best fits the supplied evidence and SLA policy?", {
            "routine": "No immediate time pressure or material impact.",
            "normal": "Handle in the normal queue within the stated target.",
            "high": "Prioritize soon to avoid significant customer or service impact.",
            "urgent": "Immediate attention is warranted to address critical impact or an imminent breach.",
            "insufficient_data": "The SLA or timing context is not sufficient to set priority.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("sla_breach_prioritizer", response, response.answers)
